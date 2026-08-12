from django.contrib import admin

from .models import Donation, Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_code', 'member', 'payment_type', 'amount', 'payment_method', 'payment_date', 'status')
    list_filter = ('payment_type', 'payment_method', 'status')
    search_fields = ('payment_code', 'member__first_name', 'member__last_name')


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ('donation_code', 'member', 'amount', 'donation_date', 'payment_method', 'status')
    list_filter = ('status', 'payment_method')
    search_fields = ('donation_code', 'member__first_name', 'member__last_name')
