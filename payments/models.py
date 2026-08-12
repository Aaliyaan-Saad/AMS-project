from django.db import models
from django.utils import timezone


class Payment(models.Model):
    """A payment record. No online payment gateway - records only."""

    TYPE_CHOICES = [
        ('MEMBERSHIP', 'Membership Fee'),
        ('RENEWAL', 'Renewal Fee'),
        ('EVENT', 'Event Fee'),
    ]

    METHOD_CHOICES = [
        ('CASH', 'Cash'),
        ('BANK_TRANSFER', 'Bank Transfer'),
        ('CARD', 'Card'),
    ]

    STATUS_CHOICES = [
        ('PAID', 'Paid'),
        ('PENDING', 'Pending'),
    ]

    payment_code = models.CharField(max_length=20, unique=True, blank=True, editable=False, verbose_name='Payment ID')
    member = models.ForeignKey('members.Member', on_delete=models.PROTECT, related_name='payments', verbose_name='Member')
    payment_type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name='Payment type')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Amount')
    payment_method = models.CharField(max_length=20, choices=METHOD_CHOICES, verbose_name='Payment method')
    payment_date = models.DateField(default=timezone.localdate, verbose_name='Date')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING', verbose_name='Status')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-payment_date', '-created_at']

    def __str__(self):
        return f'{self.payment_code} - {self.member.full_name} - {self.amount}'

    def save(self, *args, **kwargs):
        if not self.payment_code:
            next_number = Payment.objects.count() + 1
            self.payment_code = f'PAY-{next_number:04d}'
        super().save(*args, **kwargs)


class Donation(models.Model):
    """A donation made by a member through the public donate page."""

    METHOD_CHOICES = Payment.METHOD_CHOICES

    STATUS_CHOICES = [
        ('RECEIVED', 'Received'),
        ('PENDING', 'Pending'),
    ]

    donation_code = models.CharField(max_length=20, unique=True, blank=True, editable=False, verbose_name='Donation ID')
    member = models.ForeignKey('members.Member', on_delete=models.PROTECT, related_name='donations', verbose_name='Member')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Amount')
    donation_date = models.DateField(default=timezone.localdate, verbose_name='Donation date')
    payment_method = models.CharField(max_length=20, choices=METHOD_CHOICES, verbose_name='Payment method')
    message = models.TextField(blank=True, verbose_name='Note / message')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING', verbose_name='Status')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-donation_date', '-created_at']

    def __str__(self):
        return f'{self.donation_code} - {self.member.full_name} - {self.amount}'

    def save(self, *args, **kwargs):
        if not self.donation_code:
            next_number = Donation.objects.count() + 1
            self.donation_code = f'DON-{next_number:04d}'
        super().save(*args, **kwargs)
