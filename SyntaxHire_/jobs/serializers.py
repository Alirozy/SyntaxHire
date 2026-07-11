from rest_framework import serializers
from .models import JobPosting, JobSkill, Proposal, Contract, WorkSubmission, Dispute
from skills.models import Skill # skill modelinizi import edin

class JobSkillSerializer(serializers.ModelSerializer):
    skill_id = serializers.UUIDField(source='skill.id', read_only=True)
    name = serializers.CharField(source='skill.name', read_only=True)
    category = serializers.CharField(source='skill.category', read_only=True)

    class Meta:
        model = JobSkill
        fields = ['id', 'skill_id', 'name', 'category']

class JobPostingReadSerializer(serializers.ModelSerializer):
    required_skills = JobSkillSerializer(many=True, read_only=True)
    client_name = serializers.CharField(source='client.company_name', read_only=True)

    class Meta:
        model = JobPosting
        fields = '__all__'

class JobPostingWriteSerializer(serializers.ModelSerializer):
    skill_ids = serializers.ListField(
        child=serializers.UUIDField(), write_only=True, required=False
    )

    class Meta:
        model = JobPosting
        fields = [
            'title', 'description', 'project_type', 'budget_min', 
            'budget_max', 'required_experience', 'estimated_duration', 
            'status', 'skill_ids'
        ]

    def create(self, validated_data):
        skill_ids = validated_data.pop('skill_ids', [])
        job = super().create(validated_data)
        
        # Müşterinin seçtiği yetenekleri ara tabloya (JobSkill) kaydet
        if skill_ids:
            job_skills = [JobSkill(job=job, skill_id=s_id) for s_id in skill_ids]
            JobSkill.objects.bulk_create(job_skills, ignore_conflicts=True)
            
        return job

class ProposalSerializer(serializers.ModelSerializer):
    developer_email = serializers.CharField(source='developer.user.email', read_only=True)

    class Meta:
        model = Proposal
        fields = '__all__'
        read_only_fields = ['job', 'developer', 'status']

class ContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        fields = '__all__'
        read_only_fields = ['proposal']


class WorkSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkSubmission
        fields = ['id', 'contract', 'message', 'attachment_url', 'status', 'created_at']
        read_only_fields = ['id', 'contract', 'status', 'created_at']