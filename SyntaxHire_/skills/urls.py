from django.urls import path
from .views import SkillListView


app_name = 'skills'

urlpatterns = [
    path('skills/', SkillListView.as_view(), name='skills'),

]