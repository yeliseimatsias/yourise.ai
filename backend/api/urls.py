from django.urls import path
from . import views

urlpatterns = [
    path('compare/', views.compare_documents, name='api_compare'),
    path('download/<str:filename>/', views.download_report, name='api_download_report'),
]