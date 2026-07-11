from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404
from .models import JobPosting, Proposal, Contract, WorkSubmission, Dispute
from .serializers import (
    JobPostingReadSerializer, JobPostingWriteSerializer, 
    ProposalSerializer, ContractSerializer, WorkSubmissionSerializer
)
from profiles.models import ClientProfile, DeveloperProfile
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone




# ================= JOB POSTINGS (İş İlanları) =================

class ClientJobPostingListCreateView(generics.ListCreateAPIView):
    """Müşterinin kendi açtığı ilanları görmesi ve yeni ilan açması için."""
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return JobPostingWriteSerializer
        return JobPostingReadSerializer

    def get_queryset(self):
        if self.request.user.user_type not in ['COMPANY', 'CLIENT']:
            raise PermissionDenied("Only clients can manage job postings.")
        return JobPosting.objects.filter(client__user=self.request.user).prefetch_related('required_skills__skill')

    def perform_create(self, serializer):
        client_profile = get_object_or_404(ClientProfile, user=self.request.user)
        serializer.save(client=client_profile)


class PublicJobPostingListView(generics.ListAPIView):
    """Geliştiricilerin (veya herkesin) yayındaki (OPEN) ilanları görebileceği endpoint."""
    permission_classes = [permissions.AllowAny]
    serializer_class = JobPostingReadSerializer
    
    def get_queryset(self):
        return JobPosting.objects.filter(status='OPEN').select_related('client').prefetch_related('required_skills__skill')


# ================= PROPOSALS (Teklifler / Başvurular) =================

class DeveloperProposalListCreateView(generics.ListCreateAPIView):
    """Geliştiricinin yaptığı başvuruları listelemesi ve yeni başvuru yapması için."""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProposalSerializer

    def get_queryset(self):
        if self.request.user.user_type != 'DEVELOPER':
            raise PermissionDenied("Only developers can submit proposals.")
        return Proposal.objects.filter(developer__user=self.request.user)

    def perform_create(self, serializer):
        developer_profile = get_object_or_404(DeveloperProfile, user=self.request.user)
        job_id = self.kwargs.get('job_pk')
        job = get_object_or_404(JobPosting, id=job_id, status='OPEN')
        
        try:
            serializer.save(developer=developer_profile, job=job)
        except IntegrityError:
            raise ValidationError({"error": "You have already submitted a proposal for this job."})


class ClientProposalListView(generics.ListAPIView):
    """Müşterinin belirli bir iş ilanına gelen başvuruları incelemesi için."""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProposalSerializer

    def get_queryset(self):
        if self.request.user.user_type not in ['COMPANY', 'CLIENT']:
            raise PermissionDenied("Only clients can view received proposals.")
            
        job_id = self.kwargs.get('job_pk')
        # Sadece bu müşteriye ait ilanların teklifleri görülebilir (Güvenlik)
        job = get_object_or_404(JobPosting, id=job_id, client__user=self.request.user)
        return Proposal.objects.filter(job=job)
    
class AcceptProposalView(APIView):
    """
    Müşterinin gelen bir teklifi kabul edip, resmi sözleşmeyi (Contract) başlattığı endpoint.
    POST /api/jobs/proposals/{proposal_id}/accept/
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk, *args, **kwargs):
        # Sadece Client/Company rolündekiler onaylama yapabilir
        if request.user.user_type not in ['COMPANY', 'CLIENT']:
            raise PermissionDenied("Only clients can accept proposals.")

        # 1. İlgili teklifi (Proposal) ve bağlı olduğu iş ilanını (Job) bul
        proposal = get_object_or_404(Proposal, id=pk)
        job = proposal.job

        # 2. GÜVENLİK: Bu ilanın sahibi, isteği atan müşteri mi?
        if job.client.user != request.user:
            raise PermissionDenied("You do not have permission to accept proposals for this job.")

        # 3. KONTROL: İş ilanı hala açık mı? Ve teklif hala beklemede mi?
        if job.status != JobPosting.Status.OPEN:
            return Response({"error": "This job is no longer open."}, status=status.HTTP_400_BAD_REQUEST)
        
        if proposal.status != Proposal.Status.PENDING and proposal.status != Proposal.Status.SHORTLISTED:
            return Response({"error": "This proposal cannot be accepted in its current state."}, status=status.HTTP_400_BAD_REQUEST)

        # =========================================================
        # PRO SEVİYE VERİTABANI İŞLEMİ (TRANSACTION)
        # Hata olursa hiçbir değişiklik veritabanına yazılmaz (Rollback)
        # =========================================================
        try:
            with transaction.atomic():
                # A. Teklifin durumunu "Kabul Edildi" yap
                proposal.status = Proposal.Status.ACCEPTED
                proposal.save()

                # B. İş ilanını artık "Devam Ediyor" (In Progress) yap
                job.status = JobPosting.Status.IN_PROGRESS
                job.save()

                # C. Diğer bekleyen tüm teklifleri "Reddedildi" olarak işaretle (İsteğe bağlı)
                # Eğer aynı işe birden fazla kişi alınmayacaksa bu şarttır.
                Proposal.objects.filter(job=job, status=Proposal.Status.PENDING).exclude(id=proposal.id).update(status=Proposal.Status.REJECTED)

                # D. RESMİ SÖZLEŞMEYİ (CONTRACT) OLUŞTUR!
                # Burada anlaşılan fiyat, geliştiricinin teklif ettiği fiyattır.
                contract = Contract.objects.create(
                    proposal=proposal,
                    agreed_rate=proposal.proposed_rate,
                    status=Contract.Status.ACTIVE,
                    start_date=timezone.now().date()
                )
                
                # Gelecekte eklenecek: Escrow Akıllı Kontrat tetiklemesi veya Stripe API ödeme alma kodu buraya yazılır.

            # Transaction başarıyla bitti, müşteriye veriyi dön.
            serializer = ContractSerializer(contract)
            return Response({
                "message": "Proposal accepted successfully! Contract created and job is now in progress.",
                "contract": serializer.data
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            # Beklenmeyen bir hata olursa (Örn: Veritabanı çökmesi), 
            # yukarıdaki A, B, C, D adımlarının hiçbiri kaydedilmez!
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class SubmitWorkView(APIView):
    """
    Geliştiricinin bitirdiği işi müşteriye teslim ettiği endpoint.
    POST /api/jobs/contracts/{contract_id}/submit/
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, contract_id):
        # 1. Sözleşmeyi bul ve güvenlik kontrolü yap (Sadece bu sözleşmenin geliştiricisi iş teslim edebilir)
        contract = get_object_or_404(Contract, id=contract_id)
        
        if contract.proposal.developer.user != request.user:
            raise PermissionDenied("You are not the developer of this contract.")

        # 2. Sözleşme durumu aktif mi? (Örn: Tamamlanmış veya iptal edilmiş bir işe teslimat yapılamaz)
        if contract.status not in [Contract.Status.ACTIVE, Contract.Status.IN_REVIEW]:
            return Response({"error": "Work can only be submitted for active contracts."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = WorkSubmissionSerializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                # Teslimat kaydını oluştur
                submission = serializer.save(contract=contract)
                
                # Sözleşmeyi "İncelemede" durumuna çek ki müşteri bildirim alsın
                contract.status = Contract.Status.IN_REVIEW
                contract.save()

            return Response({
                "message": "Work submitted successfully. Awaiting client approval.",
                "submission": WorkSubmissionSerializer(submission).data
            }, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReviewWorkSubmissionView(APIView):
    """
    Müşterinin teslim edilen işi inceleyip ONAYLADIĞI veya REVİZYON istediği endpoint.
    POST /api/jobs/submissions/{submission_id}/review/
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, submission_id):
        submission = get_object_or_404(WorkSubmission, id=submission_id)
        contract = submission.contract

        # 1. Güvenlik: Sadece bu sözleşmenin müşterisi onay verebilir
        if contract.proposal.job.client.user != request.user:
            raise PermissionDenied("You are not the client for this contract.")

        # İşlem türü: 'approve' veya 'reject' (revizyon)
        action = request.data.get('action')

        if action == 'approve':
            with transaction.atomic():
                submission.status = WorkSubmission.Status.APPROVED
                submission.save()

                # Sözleşme başarıyla bitti!
                contract.status = Contract.Status.COMPLETED
                contract.end_date = timezone.now().date()
                contract.save()

                # İleride eklenecek: STRIPE veya SMART CONTRACT ile parayı (Escrow)
                # platformdan alıp doğrudan geliştiricinin cüzdanına aktaran kod bloğu BURAYA YAZILACAK.
                
            return Response({"message": "Work approved! Contract is now completed and funds are released."})

        elif action == 'reject':
            with transaction.atomic():
                submission.status = WorkSubmission.Status.REJECTED
                submission.save()
                
                # Sözleşme tekrar aktif duruma döner, geliştirici işe devam eder
                contract.status = Contract.Status.ACTIVE
                contract.save()
            return Response({"message": "Changes requested. Developer has been notified."})

        return Response({"error": "Invalid action. Use 'approve' or 'reject'."}, status=status.HTTP_400_BAD_REQUEST)