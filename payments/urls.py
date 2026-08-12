from django.urls import path

from . import views

urlpatterns = [
    path('payments/', views.payment_list, name='payment_list'),
    path('payments/add/', views.payment_create, name='payment_add'),
    path('payments/<int:pk>/receipt/', views.payment_receipt, name='payment_receipt'),
    path('donations/', views.donation_list, name='donation_list'),
    path('donations/<int:pk>/status/', views.donation_update_status, name='donation_status'),
    path('donate/', views.public_donate, name='public_donate'),
]
