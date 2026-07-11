from django.urls import path
from .views import (
    ClientJobPostingListCreateView,
    PublicJobPostingListView,
    DeveloperProposalListCreateView,
    ClientProposalListView,
    AcceptProposalView,
    SubmitWorkView, 
    ReviewWorkSubmissionView
)

app_name = 'jobs'

urlpatterns = [
    # Müşteri (Client) İlan Rotaları
    path('client/jobs/', ClientJobPostingListCreateView.as_view(), name='client-job-list-create'),
    
    # Geliştirici / Genel İlan Arama
    path('explore/jobs/', PublicJobPostingListView.as_view(), name='public-job-list'),
    
    # Teklif (Proposal) Rotaları
    # Müşteri ilana gelen teklifleri okur: GET /api/jobs/{job_id}/proposals/
    path('<uuid:job_pk>/proposals/', ClientProposalListView.as_view(), name='client-proposal-list'),
    
    # Geliştirici ilana teklif atar: POST /api/jobs/{job_id}/apply/
    path('<uuid:job_pk>/apply/', DeveloperProposalListCreateView.as_view(), name='developer-apply'),
    
    # Teklifi Kabul Et ve Sözleşme Başlat
    path('proposals/<uuid:pk>/accept/', AcceptProposalView.as_view(), name='accept-proposal'),
   
    # Geliştirici sözleşmeye ait işi teslim eder
    path('contracts/<uuid:contract_id>/submit/', SubmitWorkView.as_view(), name='contract-submit-work'),
    
    # Müşteri teslim edilen spesifik bir işi inceler/onaylar
    path('submissions/<uuid:submission_id>/review/', ReviewWorkSubmissionView.as_view(), name='submission-review'),
]