"""
URLs para la API de usuarios.
"""
from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # Autenticación
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Perfil
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/update/', views.ProfileUpdateView.as_view(), name='profile-update'),
    path('change-password/', views.change_password_view, name='change-password'),
]