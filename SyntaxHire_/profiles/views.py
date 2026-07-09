from django.db import IntegrityError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, generics
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied, ValidationError

from .models import (
    DeveloperProfile, ClientProfile, 
    PortfolioProject, DeveloperEducation, DeveloperCertification, DeveloperSkill
)
from .permissions import IsOwnerOfProfile
from .serializers import (
    RoleSelectionSerializer, 
    DeveloperProfileSerializer, 
    ClientProfileSerializer,
    DeveloperSkillReadSerializer,
    DeveloperSkillWriteSerializer,
    DeveloperEducationSerializer,
    DeveloperCertificationSerializer,
    PortfolioProjectSerializer
)

class ChooseRoleView(APIView):
    """
    Endpoint for newly registered users with PENDING state to choose their ecosystem role.
    POST /api/profiles/choose-role/
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        
        # Safety guard: Rolü zaten seçilmiş kullanıcıların tekrar işlem yapmasını engelle
        if user.user_type != 'PENDING':
            return Response(
                {"error": "Role has already been assigned for this account."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        serializer = RoleSelectionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user)
            return Response(
                {
                    "message": "Role successfully assigned and profile structure initialised.",
                    "current_role": user.user_type
                },
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# --- PRO Developer Profile Detail View ---
class DeveloperProfileDetailView(generics.RetrieveUpdateAPIView):
    """
    Retrieve or update the authenticated developer's profile.
    GET/PUT/PATCH /api/profiles/developer/me/
    """
    serializer_class = DeveloperProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOfProfile]

    def get_object(self):
        """
        PRO OPTIMIZATION: Fetches the developer profile with all nested relations
        (skills, projects, educations, certifications) in a single, optimized query.
        """
        # Güvenlik duvarı: Kullanıcının rolü DEVELOPER değilse erişimi engelle
        if self.request.user.user_type != 'DEVELOPER':
            raise PermissionDenied("You do not have a developer profile.")

        # DÜZELTME: Yeni eklenen 'educations' ve 'certifications' ilişkileri prefetch listesine eklendi.
        # Bu ekleme yapılmasaydı her eğitim ve sertifika satırı için veritabanına yüzlerce gereksiz sorgu (N+1) atılacaktı.
        queryset = DeveloperProfile.objects.select_related('user').prefetch_related(
            'developer_skills__skill',  # Ara tablo üzerinden yetenekleri getirir
            'portfolio_projects',       # Portfolyo projelerini getirir
            'educations',               # YENİ: Eğitim geçmişini tek seferde getirir
            'certifications'            # YENİ: Sertifikaları tek seferde getirir
        )
        
        obj = get_object_or_404(queryset, user=self.request.user)
        self.check_object_permissions(self.request, obj)
        return obj


# --- Client Profile Detail View ---
class ClientProfileDetailView(generics.RetrieveUpdateAPIView):
    """
    Retrieve or update the authenticated client's profile.
    GET/PUT/PATCH /api/profiles/client/me/
    """
    serializer_class = ClientProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOfProfile]

    def get_object(self):
        """
        Fetches the client profile and ensures the role strictly matches.
        """
        # Güvenlik duvarı: Kullanıcının rolü COMPANY/CLIENT değilse erişimi engelle
        if self.request.user.user_type not in ['COMPANY', 'CLIENT']:
            raise PermissionDenied("You do not have a client profile.")

        queryset = ClientProfile.objects.select_related('user')
        obj = get_object_or_404(queryset, user=self.request.user)
        
        self.check_object_permissions(self.request, obj)
        return obj
    
# =====================================================================
# --- NEW: Kalan Serializer'lar İçin Bağımsız CRUD Endpoints ---
# =====================================================================

class PortfolioProjectListCreateView(generics.ListCreateAPIView):
    """Geliştiricinin kendi projelerini listelemesi ve yeni proje eklemesi için."""
    serializer_class = PortfolioProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.user_type != 'DEVELOPER':
            raise PermissionDenied("Only developers have portfolio projects.")
        return PortfolioProject.objects.filter(developer__user=self.request.user)

    def perform_create(self, serializer):
        developer_profile = get_object_or_404(DeveloperProfile, user=self.request.user)
        serializer.save(developer=developer_profile)


class PortfolioProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Belirli bir portfolyo projesini okuma, güncelleme ve silme."""
    serializer_class = PortfolioProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PortfolioProject.objects.filter(developer__user=self.request.user)


class DeveloperEducationListCreateView(generics.ListCreateAPIView):
    """Geliştiricinin eğitim geçmişini listelemesi ve eğitim eklemesi için."""
    serializer_class = DeveloperEducationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.user_type != 'DEVELOPER':
            raise PermissionDenied("Only developers have education records.")
        return DeveloperEducation.objects.filter(developer__user=self.request.user)

    def perform_create(self, serializer):
        developer_profile = get_object_or_404(DeveloperProfile, user=self.request.user)
        serializer.save(developer=developer_profile)


class DeveloperEducationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Belirli bir eğitim kaydını okuma, güncelleme ve silme."""
    serializer_class = DeveloperEducationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return DeveloperEducation.objects.filter(developer__user=self.request.user)


class DeveloperCertificationListCreateView(generics.ListCreateAPIView):
    """Geliştiricinin sertifikalarını listelemesi ve yeni sertifika eklemesi için."""
    serializer_class = DeveloperCertificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.user_type != 'DEVELOPER':
            raise PermissionDenied("Only developers have certification records.")
        return DeveloperCertification.objects.filter(developer__user=self.request.user)

    def perform_create(self, serializer):
        developer_profile = get_object_or_404(DeveloperProfile, user=self.request.user)
        serializer.save(developer=developer_profile)


class DeveloperCertificationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Belirli bir sertifikayı okuma, güncelleme ve silme."""
    serializer_class = DeveloperCertificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return DeveloperCertification.objects.filter(developer__user=self.request.user)
    



class DeveloperSkillListCreateView(generics.ListCreateAPIView):
    """Geliştiricinin yeteneklerini listeler ve yeni yetenek eklemesini sağlar."""
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        # İstek tipi POST (Yaratma) ise Write, GET (Okuma) ise Read serializer kullan.
        if self.request.method == 'POST':
            return DeveloperSkillWriteSerializer
        return DeveloperSkillReadSerializer

    def get_queryset(self):
        # Sadece DEVELOPER rolündekiler işlem yapabilir
        if self.request.user.user_type != 'DEVELOPER':
            raise PermissionDenied("Only developers can manage skills.")
            
        # N+1 performans optimizasyonu için select_related kullanıldı
        return DeveloperSkill.objects.filter(developer__user=self.request.user).select_related('skill')

    def perform_create(self, serializer):
        developer_profile = get_object_or_404(DeveloperProfile, user=self.request.user)
        
        # Mükerrer yetenek (UniqueConstraint) engellemesi
        try:
            serializer.save(developer=developer_profile)
        except IntegrityError:
            raise ValidationError({"skill_id": "You have already added this skill to your profile."})


class DeveloperSkillDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Belirli bir yetenek kaydını okuma, seviyesini güncelleme veya silme."""
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        # İstek tipi PUT/PATCH (Güncelleme) ise Write, GET (Okuma) ise Read serializer kullan.
        if self.request.method in ['PUT', 'PATCH']:
            return DeveloperSkillWriteSerializer
        return DeveloperSkillReadSerializer

    def get_queryset(self):
        return DeveloperSkill.objects.filter(developer__user=self.request.user).select_related('skill')
