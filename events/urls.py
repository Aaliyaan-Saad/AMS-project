"""
DEVELOPER 2 - Events, Announcements & Email (YOUR module).

This app is included in the project at the 'events/' prefix
(see config/urls.py). Add YOUR urlpatterns below.

Suggested routes (names are up to you, but the sidebar links to these paths):
    ''                          -> events list             (/events/)
    'add/'                      -> create event
    '<int:pk>/'                 -> event detail (registrations + attendance)
    '<int:pk>/edit/'            -> edit event
    '<int:pk>/cancel/'          -> cancel event
    '<int:pk>/register/'        -> register a member for the event
    'announcements/'            -> announcements list       (/events/announcements/)
    'announcements/add/'        -> create announcement
    'announcements/<int:pk>/'   -> view announcement
    'announcements/<int:pk>/edit/'   -> edit announcement
    'announcements/<int:pk>/delete/' -> delete announcement
    'email/'                    -> email history list       (/events/email/)
    'email/compose/'            -> compose & send email     (/events/email/compose/)

IMPORTANT
- The models Event, EventRegistration, Announcement and EmailLog are
  ALREADY defined for you in models.py (shared contract). Do NOT change
  field names.
- Work only inside this folder. Never edit config/, core/, payments/,
  or static/.
- Use the shared layout: extend 'base.html', set page_title, and reuse
  partials (pagination, confirm modal, badges).
- For sending email use Django's send_mail() (see settings.py EMAIL_*).
  Log every sent email as an EmailLog row.
"""
from django.urls import path

from . import views

urlpatterns = [
    # Add your routes here, e.g.:
    # path('', views.event_list, name='event_list'),
    # path('announcements/', views.announcement_list, name='announcement_list'),
    # path('email/compose/', views.email_compose, name='email_compose'),
]
