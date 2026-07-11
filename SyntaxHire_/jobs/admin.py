from django.contrib import admin
from .models import JobPosting, JobSkill, Proposal, Contract, WorkSubmission, Dispute

# Register your models here.
admin.site.register(JobPosting)
admin.site.register(JobSkill)
admin.site.register(Proposal)
admin.site.register(Contract)
admin.site.register(WorkSubmission)
admin.site.register(Dispute)

