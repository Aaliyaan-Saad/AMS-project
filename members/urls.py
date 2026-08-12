"""
DEVELOPER 1 - Members & Memberships (YOUR module).

This app is included in the project at the 'members/' prefix
(see config/urls.py). Add YOUR urlpatterns below.

Suggested routes (names are up to you, but the sidebar links to these paths):
    ''                          -> members list            (/members/)
    'add/'                      -> add member
    '<int:pk>/'                 -> member profile
    '<int:pk>/edit/'            -> edit member
    '<int:pk>/delete/'          -> delete member
    '<int:pk>/renew/'           -> renew membership
    'plans/'                    -> membership plans        (/members/plans/)
    'plans/add/'                -> create plan
    'plans/<int:pk>/edit/'      -> edit plan
    'plans/<int:pk>/disable/'   -> disable plan

IMPORTANT
- The models Member and MembershipPlan are ALREADY defined for you in
  models.py (they are the shared contract). Do NOT change field names.
- Work only inside this folder. Never edit config/, core/, payments/,
  or static/.
- Use the shared layout: extend 'base.html', set page_title, and reuse
  partials (pagination, confirm modal, badges).
- Deleting a plan is not allowed; implement 'disable' instead.
"""
from django.urls import path

from . import views

urlpatterns = [
    path("", views.member_list, name="member_list"),
    path("add/", views.member_add, name="member_add"),
    path("<int:pk>/", views.member_detail, name="member_detail"),
    path("<int:pk>/edit/", views.member_edit, name="member_edit"),
    path("<int:pk>/delete/", views.member_delete, name="member_delete"),
    path("<int:pk>/renew/", views.member_renew, name="member_renew"),

    path("plans/", views.plan_list, name="plan_list"),
    path("plans/add/", views.plan_add, name="plan_add"),
    path("plans/<int:pk>/edit/", views.plan_edit, name="plan_edit"),
    path("plans/<int:pk>/disable/", views.plan_disable, name="plan_disable"),
]
