from django.urls import path
from django.shortcuts import redirect
from django.contrib.auth.views import LogoutView
from . import views

def redirect_to_login(request):
    return redirect('login')

urlpatterns = [
    path('', redirect_to_login, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.face_login, name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('delete-account/', views.delete_account, name='delete_account'),
] 