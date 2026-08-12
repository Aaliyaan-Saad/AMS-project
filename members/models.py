from datetime import date

from django.db import models
from django.utils import timezone


class MembershipPlan(models.Model):
    """A membership plan (Student / Professional / Corporate).

    Plans in use are never deleted; they are disabled instead.
    """

    name = models.CharField(max_length=100, unique=True, verbose_name='Plan name')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Price')
    duration_months = models.PositiveIntegerField(verbose_name='Duration (months)')
    description = models.TextField(blank=True, verbose_name='Description')
    active = models.BooleanField(default=True, verbose_name='Active')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def expiry_date_from(self, start_date):
        """Return the expiry date for a membership starting on start_date."""
        year = start_date.year + (start_date.month + self.duration_months - 1) // 12
        month = (start_date.month + self.duration_months - 1) % 12 + 1
        day = min(start_date.day, _days_in_month(year, month))
        return date(year, month, day)


def _days_in_month(year, month):
    import calendar
    return calendar.monthrange(year, month)[1]


class Member(models.Model):
    """A member of the association.

    This model is the shared contract: payments, event registrations and
    donations all reference it. Field names must not change without
    telling the team.
    """

    member_code = models.CharField(max_length=20, unique=True, blank=True, editable=False, verbose_name='Member ID')
    first_name = models.CharField(max_length=50, verbose_name='First name')
    last_name = models.CharField(max_length=50, verbose_name='Last name')
    email = models.EmailField(unique=True, verbose_name='Email')
    phone = models.CharField(max_length=30, blank=True, verbose_name='Phone')
    city = models.CharField(max_length=100, blank=True, verbose_name='City')
    plan = models.ForeignKey(MembershipPlan, on_delete=models.PROTECT, related_name='members', verbose_name='Membership plan')
    join_date = models.DateField(default=timezone.localdate, verbose_name='Join date')
    expiry_date = models.DateField(null=True, blank=True, verbose_name='Expiry date')
    last_renewed_date = models.DateField(null=True, blank=True, verbose_name='Last renewed')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['first_name', 'last_name']

    def __str__(self):
        return f'{self.full_name} ({self.member_code})'

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'.strip()

    @property
    def status(self):
        """Active while the expiry date is today or in the future."""
        if self.expiry_date and self.expiry_date >= timezone.localdate():
            return 'Active'
        return 'Expired'

    def save(self, *args, **kwargs):
        if not self.member_code:
            next_number = Member.objects.count() + 1
            self.member_code = f'MEM-{next_number:04d}'
        super().save(*args, **kwargs)
