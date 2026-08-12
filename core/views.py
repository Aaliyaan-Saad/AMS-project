from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.db.models import Count, Sum
from django.shortcuts import redirect, render
from django.utils import timezone

from events.models import Announcement, Event
from members.models import Member, MembershipPlan
from payments.models import Donation, Payment

from .forms import EmailLoginForm


class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    authentication_form = EmailLoginForm


def logout_view(request):
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'You have been logged out.')
        return redirect('login')
    return redirect('dashboard')


@login_required
def dashboard(request):
    today = timezone.localdate()

    total_members = Member.objects.count()
    active_members = Member.objects.filter(expiry_date__gte=today).count()
    expired_members = total_members - active_members

    total_revenue = Payment.objects.filter(status='PAID').aggregate(total=Sum('amount'))['total'] or 0
    total_donations = Donation.objects.filter(status='RECEIVED').aggregate(total=Sum('amount'))['total'] or 0

    context = {
        'total_members': total_members,
        'active_members': active_members,
        'expired_members': expired_members,
        'total_revenue': total_revenue,
        'total_donations': total_donations,
        'upcoming_events': Event.objects.filter(status='UPCOMING', event_date__gte=today).order_by('event_date')[:5],
        'recent_members': Member.objects.order_by('-created_at')[:5],
        'recent_payments': Payment.objects.order_by('-created_at')[:5],
        'recent_donations': Donation.objects.order_by('-created_at')[:5],
        'members_by_plan': MembershipPlan.objects.annotate(member_count=Count('members')).order_by('name'),
        'active_announcements': Announcement.objects.filter(publish_date__lte=today).filter(
            models_expiry_lte_or_null(today)
        ).order_by('-priority', '-publish_date')[:5],
    }
    return render(request, 'dashboard.html', context)


@login_required
def settings_view(request):
    return render(request, 'settings.html')


def models_expiry_lte_or_null(today):
    from django.db.models import Q
    return Q(expiry_date__gte=today) | Q(expiry_date__isnull=True)
