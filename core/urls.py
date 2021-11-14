from django.urls import path
from core import views

urlpatterns = [
    path('compilecode/', views.CompileCode.as_view()),
    path('runcode/', views.RunCode.as_view()),
]