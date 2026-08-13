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
        'members_by_plan': [(plan.name, plan.member_count) for plan in
                            MembershipPlan.objects.annotate(member_count=Count('members')).order_by('name')],
        'members_by_status': [('Active', active_members), ('Expired', expired_members)],
        'active_announcements': Announcement.objects.filter(publish_date__lte=today).filter(
            models_expiry_lte_or_null(today)
        ).order_by('-priority', '-publish_date')[:5],
        # Analytics
        'revenue_by_type': _revenue_by_type(),
        'payments_by_status': [(label, Payment.objects.filter(status=value).count())
                               for value, label in Payment.STATUS_CHOICES],
        'donations_by_status': [(label, Donation.objects.filter(status=value).count())
                                for value, label in Donation.STATUS_CHOICES],
        'revenue_by_month': _sum_by_month(
            Payment.objects.filter(status='PAID').values('payment_date__year', 'payment_date__month')
            .annotate(total=Sum('amount')), 'payment_date', 6),
        'donations_by_month': _sum_by_month(
            Donation.objects.filter(status='RECEIVED').values('donation_date__year', 'donation_date__month')
            .annotate(total=Sum('amount')), 'donation_date', 6),
    }
    return render(request, 'dashboard.html', context)


def _revenue_by_type():
    result = []
    for value, label in Payment.TYPE_CHOICES:
        total = Payment.objects.filter(status='PAID', payment_type=value).aggregate(s=Sum('amount'))['s'] or 0
        result.append((label, float(total)))
    return result


def _last_months(n):
    """Return the last n (year, month) tuples in ascending order, ending this month."""
    year, month = timezone.localdate().year, timezone.localdate().month
    months = []
    for _ in range(n):
        months.append((year, month))
        month -= 1
        if month == 0:
            month = 12
            year -= 1
    return list(reversed(months))


def _sum_by_month(rows, date_field, months):
    """rows: queryset of values('..._year', '..._month') already filtered; sums per month."""
    by_month = {}
    for row in rows:
        key = (row[f'{date_field}__year'], row[f'{date_field}__month'])
        by_month[key] = by_month.get(key, 0) + row['total']

    output = []
    for year, month in _last_months(months):
        output.append((f'{month:02d}', float(by_month.get((year, month), 0))))
    return output


@login_required
def settings_view(request):
    return render(request, 'settings.html')


def models_expiry_lte_or_null(today):
    from django.db.models import Q
    return Q(expiry_date__gte=today) | Q(expiry_date__isnull=True)
