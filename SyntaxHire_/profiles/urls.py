from django.urls import path
from .views import (
    ChooseRoleView, 
    DeveloperProfileDetailView, 
    ClientProfileDetailView,
    PortfolioProjectListCreateView,
    PortfolioProjectDetailView,
    DeveloperEducationListCreateView,
    DeveloperEducationDetailView,
    DeveloperCertificationListCreateView,
    DeveloperCertificationDetailView,
    DeveloperSkillListCreateView,
    DeveloperSkillDetailView
)
app_name = 'profiles'

urlpatterns = [
    path('choose-role/', ChooseRoleView.as_view(), name='choose-role'),

    # Profile CRUD (Self Management)
    path('developer/me/', DeveloperProfileDetailView.as_view(), name='developer-me'),
    path('client/me/', ClientProfileDetailView.as_view(), name='client-me'),


    # Portfolyo Projeleri CRUD
    path('portfolio-projects/', PortfolioProjectListCreateView.as_view(), name='portfolio-project-list-create'),
    path('portfolio-projects/<uuid:pk>/', PortfolioProjectDetailView.as_view(), name='portfolio-project-detail'),

    # Eğitim Geçmişi CRUD
    path('educations/', DeveloperEducationListCreateView.as_view(), name='education-list-create'),
    path('educations/<uuid:pk>/', DeveloperEducationDetailView.as_view(), name='education-detail'),

    # Sertifikalar CRUD
    path('certifications/', DeveloperCertificationListCreateView.as_view(), name='certification-list-create'),
    path('certifications/<uuid:pk>/', DeveloperCertificationDetailView.as_view(), name='certification-detail'),

    # 
    path('developer/skills/', DeveloperSkillListCreateView.as_view(), name='developer-skill-list-create'),
    path('developer/skills/<uuid:pk>/', DeveloperSkillDetailView.as_view(), name='developer-skill-detail'),
]