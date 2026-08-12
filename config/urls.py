"""
Root URL configuration.

Each module has its own URL file. The members and events apps are
pre-wired here as placeholders; Developer 1 and Developer 2 fill in
their own urlpatterns inside their app's urls.py - they do NOT need
to touch this file.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('members/', include('members.urls')),  # Developer 1 - Members & Memberships
    path('events/', include('events.urls')),    # Developer 2 - Events & Announcements
    path('', include('payments.urls')),         # Developer 3 - Payments & Donations
]
