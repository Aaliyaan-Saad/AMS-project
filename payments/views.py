from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from core.decorators import admin_required
from members.models import Member

from .forms import DonationStatusForm, PaymentForm, PublicDonateForm
from .models import Donation, Payment


# ---------------------------------------------------------------------------
# Payments
# ---------------------------------------------------------------------------

@login_required
def payment_list(request):
    payments = Payment.objects.select_related('member')

    search = request.GET.get('q', '').strip()
    payment_type = request.GET.get('type', '')
    status = request.GET.get('status', '')

    if search:
        payments = payments.filter(
            Q(member__first_name__icontains=search)
            | Q(member__last_name__icontains=search)
            | Q(member__member_code__icontains=search)
            | Q(payment_code__icontains=search)
        )
    if payment_type:
        payments = payments.filter(payment_type=payment_type)
    if status:
        payments = payments.filter(status=status)

    paginator = Paginator(payments, 15)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'page_obj': page_obj,
        'types': Payment.TYPE_CHOICES,
        'statuses': Payment.STATUS_CHOICES,
        'search': search,
        'selected_type': payment_type,
        'selected_status': status,
    }
    return render(request, 'payments/payment_list.html', context)


@login_required
def payment_create(request):
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save()
            messages.success(request, f'Payment {payment.payment_code} recorded.')
            return redirect('payment_list')
    else:
        initial = {}
        member_id = request.GET.get('member')
        if member_id:
            initial['member'] = member_id
        form = PaymentForm(initial=initial)
    return render(request, 'payments/payment_form.html', {'form': form})


@login_required
def payment_receipt(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    if payment.status != 'PAID':
        messages.info(request, 'Receipts are available for paid payments only.')
        return redirect('payment_list')
    return render(request, 'payments/receipt.html', {'payment': payment})


# ---------------------------------------------------------------------------
# Donations
# ---------------------------------------------------------------------------

@login_required
def donation_list(request):
    donations = Donation.objects.select_related('member')

    search = request.GET.get('q', '').strip()
    status = request.GET.get('status', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    if search:
        donations = donations.filter(
            Q(member__first_name__icontains=search)
            | Q(member__last_name__icontains=search)
            | Q(member__member_code__icontains=search)
            | Q(donation_code__icontains=search)
        )
    if status:
        donations = donations.filter(status=status)
    if date_from:
        donations = donations.filter(donation_date__gte=date_from)
    if date_to:
        donations = donations.filter(donation_date__lte=date_to)

    today = timezone.localdate()
    total_received = Donation.objects.filter(status='RECEIVED').aggregate(total=Sum('amount'))['total'] or 0
    month_received = Donation.objects.filter(
        status='RECEIVED', donation_date__year=today.year, donation_date__month=today.month
    ).aggregate(total=Sum('amount'))['total'] or 0

    paginator = Paginator(donations, 15)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'page_obj': page_obj,
        'statuses': Donation.STATUS_CHOICES,
        'search': search,
        'selected_status': status,
        'date_from': date_from,
        'date_to': date_to,
        'total_received': total_received,
        'month_received': month_received,
    }
    return render(request, 'payments/donation_list.html', context)


@admin_required
@require_POST
def donation_update_status(request, pk):
    donation = get_object_or_404(Donation, pk=pk)
    form = DonationStatusForm(request.POST, instance=donation)
    if form.is_valid():
        form.save()
        messages.success(request, f'Donation {donation.donation_code} updated to "{donation.get_status_display()}".')
    else:
        messages.error(request, 'Could not update the donation status.')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/donations/'))


def public_donate(request):
    """Public page: a member enters their Member ID to submit a donation."""
    if request.method == 'POST':
        form = PublicDonateForm(request.POST)
        if form.is_valid():
            member = Member.objects.get(member_code=form.cleaned_data['member_code'])
            Donation.objects.create(
                member=member,
                amount=form.cleaned_data['amount'],
                payment_method=form.cleaned_data['payment_method'],
                message=form.cleaned_data.get('message', ''),
            )
            return render(request, 'payments/donate_success.html', {'member': member})
    else:
        form = PublicDonateForm()
    return render(request, 'payments/public_donate.html', {'form': form})
