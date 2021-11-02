from django.urls import path
from problems import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('getTagList/', views.getTagList.as_view()),
    path('getProblemsList/', views.getProblemsList.as_view()),
    path('getTagListCreateProblem/', views.getTagListCreateProblem.as_view()),
    path('addProblem/', views.AddProblem.as_view()),
    path('getProblem/', views.GetProblem.as_view()),
    path('uploadTC/', views.UploadTestCases.as_view()),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
