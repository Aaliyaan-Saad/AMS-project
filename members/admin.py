from django.contrib import admin

from .models import Member, MembershipPlan


@admin.register(MembershipPlan)
class MembershipPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'duration_months', 'active')
    list_filter = ('active',)
    search_fields = ('name',)


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('member_code', 'full_name', 'email', 'phone', 'plan', 'expiry_date', 'status')
    list_filter = ('plan',)
    search_fields = ('member_code', 'first_name', 'last_name', 'email')
    readonly_fields = ('member_code', 'created_at')
