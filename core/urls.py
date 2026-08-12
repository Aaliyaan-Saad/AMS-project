from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView
from django.urls import path, reverse_lazy

from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('settings/', views.settings_view, name='settings'),
    path('settings/password/', login_required(PasswordChangeView.as_view(
        template_name='change_password.html',
        success_url=reverse_lazy('settings'),
    )), name='change_password'),
]
