import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from core.models import TimeStampedModel
from django.conf import settings

class JobPosting(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey('profiles.ClientProfile', on_delete=models.CASCADE, related_name='job_postings')
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    
    class ProjectType(models.TextChoices):
        HOURLY = 'HOURLY', _('Hourly')
        FIXED = 'FIXED', _('Fixed Price')
        
    project_type = models.CharField(max_length=20, choices=ProjectType.choices, db_index=True)
    budget_min = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.00)])
    budget_max = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.00)])
    
    class ExperienceLevel(models.TextChoices):
        JUNIOR = 'JUNIOR', _('Junior')
        MID = 'MID', _('Mid-Level')
        SENIOR = 'SENIOR', _('Senior')
        EXPERT = 'EXPERT', _('Expert')
        
    required_experience = models.CharField(max_length=20, choices=ExperienceLevel.choices)
    estimated_duration = models.CharField(max_length=100)
    
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', _('Draft')
        OPEN = 'OPEN', _('Open')
        IN_PROGRESS = 'IN_PROGRESS', _('In Progress')
        COMPLETED = 'COMPLETED', _('Completed')
        CANCELLED = 'CANCELLED', _('Cancelled')
        
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN, db_index=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class JobSkill(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name='required_skills')
    skill = models.ForeignKey('skills.Skill', on_delete=models.CASCADE, related_name='job_postings')
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['job', 'skill'], name='unique_job_skill')
        ]

class Proposal(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name='proposals')
    developer = models.ForeignKey('profiles.DeveloperProfile', on_delete=models.CASCADE, related_name='proposals')
    
    cover_letter = models.TextField()
    proposed_rate = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.00)])
    estimated_duration = models.CharField(max_length=100)
    
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        SHORTLISTED = 'SHORTLISTED', _('Shortlisted')
        ACCEPTED = 'ACCEPTED', _('Accepted')
        REJECTED = 'REJECTED', _('Rejected')
        WITHDRAWN = 'WITHDRAWN', _('Withdrawn')
        
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['job', 'developer'], name='unique_job_proposal')
        ]
        ordering = ['-created_at']

class Contract(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    proposal = models.OneToOneField(Proposal, on_delete=models.CASCADE, related_name='contract')
    
    agreed_rate = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.00)])
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(null=True, blank=True)
    
    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', _('Active')
        IN_REVIEW = 'IN_REVIEW', _('In Review') # YENİ: Geliştirici işi teslim etti, onay bekliyor
        DISPUTE = 'DISPUTE', _('Dispute')       # YENİ: Sorun çıktı, admin müdahalesi gerekiyor
        COMPLETED = 'COMPLETED', _('Completed')
        CANCELLED = 'CANCELLED', _('Cancelled')
        
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    client_rating = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)])
    developer_rating = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)])



class WorkSubmission(TimeStampedModel):
    """Geliştiricinin sözleşme kapsamında teslim ettiği iş paketleri/revizyonlar."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='submissions')
    
    message = models.TextField(help_text="Geliştiricinin teslimat notu (Örn: Proje yayında, test edebilirsiniz.)")
    attachment_url = models.URLField(blank=True, null=True, help_text="Github linki, Drive linki veya ZIP dosyası adresi")
    
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending Approval')
        APPROVED = 'APPROVED', _('Approved')
        REJECTED = 'REJECTED', _('Changes Requested')
        
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    class Meta:
        ordering = ['-created_at']

class Dispute(TimeStampedModel):
    """Sözleşme sürecinde yaşanan anlaşmazlıkların tutulduğu tablo."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contract = models.OneToOneField(Contract, on_delete=models.CASCADE, related_name='dispute')
    
    # Şikayeti başlatan tarafın kim olduğunu (Client veya Developer) bilmemiz lazım
    initiated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='initiated_disputes')    
    reason = models.TextField(help_text="Anlaşmazlığın / Şikayetin sebebi")
    
    class Status(models.TextChoices):
        OPEN = 'OPEN', _('Open')
        UNDER_INVESTIGATION = 'UNDER_INVESTIGATION', _('Under Investigation')
        RESOLVED = 'RESOLVED', _('Resolved')
        
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    resolution_notes = models.TextField(blank=True, null=True, help_text="Adminlerin verdiği karar ve çözüm detayları")