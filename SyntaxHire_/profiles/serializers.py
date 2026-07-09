from rest_framework import serializers
from django.contrib.auth import get_user_model
from skills.models import Skill
from .models import (
    DeveloperProfile, DeveloperSkill, PortfolioProject, 
    ClientProfile, DeveloperEducation, DeveloperCertification
)

User = get_user_model()

class RoleSelectionSerializer(serializers.Serializer):
    """Serializer to handle user role assignment during onboarding."""
    
    ROLE_CHOICES = (
        ('DEVELOPER', 'Developer'),
        ('COMPANY', 'Company/Client'),
    )
    
    role = serializers.ChoiceField(choices=ROLE_CHOICES, required=True)

    def save(self, user):
        """Updates user role and initialises the specific profile structure using UUIDs."""
        role = self.validated_data['role']
        
        user.user_type = role
        user.save()
        
        if role == 'DEVELOPER':
            DeveloperProfile.objects.get_or_create(user=user)
        elif role == 'COMPANY':
            ClientProfile.objects.get_or_create(user=user)
            
        return user


class DeveloperSkillReadSerializer(serializers.ModelSerializer):
    """Profil okunurken (GET) yetenekleri tüm detaylarıyla getiren yardımcı serializer."""
    # DÜZELTME: Tablonun kendi 'id'si yerine Skill id'sini 'skill_id' olarak ayrı sunuyoruz.
    skill_id = serializers.UUIDField(source='skill.id', read_only=True)
    name = serializers.CharField(source='skill.name', read_only=True)
    category = serializers.CharField(source='skill.category', read_only=True)
    level_display = serializers.CharField(source='get_level_display', read_only=True)

    class Meta:
        model = DeveloperSkill
        # 'id' alanı DeveloperSkill tablosunun kendi UUID'sidir ve CRUD için zorunludur.
        fields = ['id', 'skill_id', 'name', 'category', 'level', 'level_display']


class DeveloperSkillWriteSerializer(serializers.ModelSerializer):
    """Profil güncellenirken (POST/PUT/PATCH) yetenek kaydeden serializer."""
    skill_id = serializers.PrimaryKeyRelatedField(
        # NOT: Eğer Skill modelini ayrı bir app'e taşıdıysan buradaki queryset
        # içe aktardığın (import) yeni Skill modelinden gelmelidir.
        queryset=Skill.objects.all(), 
        source='skill'
    )

    class Meta:
        model = DeveloperSkill
        fields = ['skill_id', 'level']

# =====================================================================
# --- NEW: EĞİTİM VE SERTİFİKA SERIALIZERS (CRUD İÇİN) ---
# =====================================================================

class DeveloperEducationSerializer(serializers.ModelSerializer):
    """Geliştiricinin eğitim geçmişi CRUD işlemleri için."""
    class Meta:
        model = DeveloperEducation
        fields = [
            'id', 'university_name', 'degree', 'field_of_study', 
            'start_date', 'end_date', 'is_current', 'description'
        ]
        read_only_fields = ['id']


class DeveloperCertificationSerializer(serializers.ModelSerializer):
    """Geliştiricinin sertifikaları için CRUD işlemleri."""
    class Meta:
        model = DeveloperCertification
        fields = [
            'id', 'name', 'issuing_organization', 'issue_date', 
            'expiration_date', 'credential_id', 'credential_url', 
            'verification_url', 'path_to_certificate_file'
        ]
        read_only_fields = ['id']


class PortfolioProjectSerializer(serializers.ModelSerializer):
    """Geliştiricinin portfolyosuna ekleyeceği projelerin CRUD işlemleri için."""
    class Meta:
        model = PortfolioProject
        fields = [
            'id', 'title', 'description', 'project_url', 
            'repository_url', 'technologies_used', 'completion_date'
        ]
        read_only_fields = ['id']


# =====================================================================
# --- ANA PROFİL SERIALIZERS ---
# =====================================================================

class DeveloperProfileSerializer(serializers.ModelSerializer):
    """
    Detailed profile data for Developer role updates.
    Yetenek, Portfolyo, Eğitim ve Sertifikaları iç içe (nested) sunar.
    """
    email = serializers.EmailField(source='user.email', read_only=True)
    
    # Okuma (Read) İlişkileri - İlgili verileri profil detayında listeler
    portfolio_projects = PortfolioProjectSerializer(many=True, read_only=True)
    skills = DeveloperSkillReadSerializer(many=True, source='developer_skills', read_only=True)
    educations = DeveloperEducationSerializer(many=True, read_only=True)  # YENİ EKLENDİ
    certifications = DeveloperCertificationSerializer(many=True, read_only=True)  # YENİ EKLENDİ
    
    # Okunaklı Enum Çıktıları
    availability_display = serializers.CharField(source='get_availability_status_display', read_only=True)
    english_level_display = serializers.CharField(source='get_english_level_display', read_only=True)

    # Yazma (Write) İlişkisi
    skills_input = DeveloperSkillWriteSerializer(many=True, write_only=True, required=False, source='developer_skills')

    class Meta:
        model = DeveloperProfile
        fields = [
            'id', 'email', 'title', 'bio', 'hourly_rate', 
            'availability_status', 'availability_display',
            'english_level', 'english_level_display',
            'github_url', 'linkedin_url', 'website_url',
            'is_verified', 'job_success_score', 'total_earnings', 'total_hours_worked',
            'skills', 'skills_input', 'portfolio_projects', 'educations', 'certifications', 
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'is_verified', 'job_success_score', 'total_earnings',
            'total_hours_worked', 'created_at', 'updated_at'
        ]

    def update(self, instance, validated_data):
        """İç içe gelen yetenek verilerini veritabanına işler."""
        skills_data = validated_data.pop('developer_skills', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if skills_data is not None:
            instance.developer_skills.all().delete()
            
            developer_skills_to_create = [
                DeveloperSkill(
                    developer=instance,
                    skill=skill_item['skill'],
                    level=skill_item.get('level', DeveloperSkill.LevelChoices.MID)
                )
                for skill_item in skills_data
            ]
            DeveloperSkill.objects.bulk_create(developer_skills_to_create)

        return instance
    

class ClientProfileSerializer(serializers.ModelSerializer):
    """Detailed profile data for Client role updates."""
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = ClientProfile
        fields = [
            'id', 'email', 'company_name', 'industry', 
            'payment_verification_status', 'phone_number', 'total_spent', 
            'created_at', 'updated_at'
        ]        
        read_only_fields = [
            'id', 'payment_verification_status', 'total_spent', 
            'created_at', 'updated_at'
        ]