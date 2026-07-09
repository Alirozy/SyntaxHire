import uuid
from django.db import models
from django.conf import settings
from core.models import TimeStampedModel
from skills.models import Skill



class DeveloperProfile(TimeStampedModel):
    """Profile model specific to software developers, created during the onboarding completion phase."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='developer_profile'
    )
    
    # Temel Bilgiler (Arama sorguları için title indekslendi)
    title = models.CharField(max_length=255, blank=True, null=True, db_index=True, verbose_name="Professional Title")
    bio = models.TextField(blank=True, null=True, verbose_name="Biography")
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, db_index=True, verbose_name="Hourly Rate ($)")
    
    # Durum ve İletişim Tercihleri (Filtrelemeler için durum alanı indekslendi)
    class AvailabilityChoices(models.TextChoices):
        AVAILABLE = 'AVAILABLE', 'Available'
        PART_TIME = 'PART_TIME', 'Part-time Available'

        BUSY = 'BUSY', 'Busy'
    availability_status = models.CharField(
        max_length=20, 
        choices=AvailabilityChoices.choices, 
        default=AvailabilityChoices.AVAILABLE,
        db_index=True
    )
    
    job_success_score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name="Job Success Score (%)")
    total_earnings = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name="Total Earnings ($)")
    total_hours_worked = models.PositiveIntegerField(default=0, verbose_name="Total Hours Worked")
    # Platform İstatistikleri (Yalnızca onaylı yazılımcıları listelemek için is_verified indekslendi)
    is_verified = models.BooleanField(default=False, db_index=True, verbose_name="Identity/Skill Verified")

    # Linkler
    github_url = models.URLField(blank=True, null=True, verbose_name="GitHub URL")
    linkedin_url = models.URLField(blank=True, null=True, verbose_name="LinkedIn URL")
    website_url = models.URLField(blank=True, null=True, verbose_name="Personal Website URL")

    class EnglishLevelChoices(models.TextChoices):
        A1 = 'A1', 'A1 - Beginner'
        A2 = 'A2', 'A2 - Elementary'
        B1 = 'B1', 'B1 - Intermediate'
        B2 = 'B2', 'B2 - Upper Intermediate'
        C1 = 'C1', 'C1 - Advanced'
        C2 = 'C2', 'C2 - Proficient'
        NATIVE = 'NATIVE', 'Native / Bilingual'
    english_level = models.CharField(max_length=10, choices=EnglishLevelChoices.choices, blank=True, null=True)

    

    def __str__(self):
        # title alanı boşsa hata vermemesi için fallback eklendi
        return f"Developer: {self.user.email} - {self.title or 'Profile Incomplete'}"




class DeveloperSkill(TimeStampedModel):
    """
    Geliştiricinin yeteneklerini ve o yetenekteki seviyesini tutan ara (Through) tablo.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    developer = models.ForeignKey(DeveloperProfile, on_delete=models.CASCADE, related_name='developer_skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='skill_developers')
    
    class LevelChoices(models.TextChoices):
        JUNIOR = 'JUNIOR', 'Junior'
        MID = 'MID', 'Mid-Level'
        SENIOR = 'SENIOR', 'Senior'
        EXPERT = 'EXPERT', 'Expert'
        
    level = models.CharField(max_length=20, choices=LevelChoices.choices, default=LevelChoices.MID, db_index=True)

    class Meta:
        # DÜZELTME: unique_together yerine modern Meta Constraints yapısı
        constraints = [
            models.UniqueConstraint(fields=['developer', 'skill'], name='unique_developer_skill')
        ]

    def __str__(self):
        return f"{self.developer.user.email} - {self.skill.name} ({self.level})"




class PortfolioProject(TimeStampedModel):
    """Geliştiricinin vitrininde sergileyeceği projeler."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    developer = models.ForeignKey(DeveloperProfile, on_delete=models.CASCADE, related_name='portfolio_projects')
    
    title = models.CharField(max_length=255, verbose_name="Project Title")
    description = models.TextField(verbose_name="Project Description")
    
    project_url = models.URLField(blank=True, null=True, verbose_name="Live Project URL")
    repository_url = models.URLField(blank=True, null=True, verbose_name="Repository (GitHub/GitLab) URL")
    
    # Projeye özel dinamik etiketler için JSONField mantıklı bir tercih, aynen korundu.
    technologies_used = models.JSONField(default=list, blank=True, verbose_name="Technologies Used (Array)") 
    completion_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} by {self.developer.user.email}"




class DeveloperEducation(TimeStampedModel):
    """Geliştiricinin eğitim geçmişini tutan model."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    developer = models.ForeignKey(DeveloperProfile, on_delete=models.CASCADE, related_name='educations')

    university_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="University / Institution Name")
    degree = models.CharField(max_length=255, blank=True, null=True, verbose_name="Degree (e.g., B.Sc., M.Sc.)")
    field_of_study = models.CharField(max_length=255, blank=True, null=True, verbose_name="Field of Study")
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    is_current = models.BooleanField(default=False, verbose_name="Currently Studying")
    description = models.TextField(blank=True, null=True, verbose_name="Description / Achievements")

    def __str__(self):
        return f"{self.university_name or 'No University Specified'} - {self.degree or 'No Degree Specified'}"




class DeveloperCertification(TimeStampedModel):
    """Geliştiricinin sahip olduğu sertifikaları tutan model."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    developer = models.ForeignKey(DeveloperProfile, on_delete=models.CASCADE, related_name='certifications')

    name = models.CharField(max_length=255, verbose_name="Certification Name")
    issuing_organization = models.CharField(max_length=255, blank=True, null=True, verbose_name="Issuing Organization")
    issue_date = models.DateField(blank=True, null=True)
    expiration_date = models.DateField(blank=True, null=True)
    credential_id = models.CharField(max_length=100, blank=True, null=True, verbose_name="Credential ID")
    credential_url = models.URLField(blank=True, null=True, verbose_name="Credential URL")
    verification_url = models.URLField(blank=True, null=True, verbose_name="Verification URL")
    path_to_certificate_file = models.FileField(upload_to='certificates/', blank=True, null=True, verbose_name="Certificate File")

    def __str__(self):
        return f"{self.name} - {self.issuing_organization or 'No Organization Specified'}"
    


    
class ClientProfile(TimeStampedModel):
    """Profile model specific to individual clients/freelance employers, created during the onboarding completion phase."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='client_profile'
    )
    company_name = models.CharField(max_length=150, blank=True, null=True, verbose_name="Company Name (if applicable)")
    industry = models.CharField(max_length=100, blank=True, null=True, verbose_name="Industry Sector (if applicable)")
    payment_verification_status = models.BooleanField(default=False, verbose_name="Payment Verification Status")

    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Phone Number")
    total_spent = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Total Spent ($)")

    def __str__(self):
        return f"Client: {self.user.email}"



