from django.contrib import admin
from .models import DeveloperProfile, ClientProfile, Skill, DeveloperSkill, PortfolioProject, DeveloperEducation, DeveloperCertification

# Register your models here.

admin.site.register(Skill)
admin.site.register(DeveloperSkill)
admin.site.register(PortfolioProject)
admin.site.register(DeveloperProfile)
admin.site.register(ClientProfile)
admin.site.register(DeveloperEducation)
admin.site.register(DeveloperCertification)
