from django.conf import settings
from django.db import models
from django.utils import timezone


class Event(models.Model):
    """An association event."""

    STATUS_CHOICES = [
        ('UPCOMING', 'Upcoming'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    name = models.CharField(max_length=200, verbose_name='Event name')
    description = models.TextField(blank=True, verbose_name='Description')
    event_date = models.DateField(verbose_name='Date')
    event_time = models.TimeField(null=True, blank=True, verbose_name='Time')
    venue = models.CharField(max_length=200, blank=True, verbose_name='Venue')
    capacity = models.PositiveIntegerField(default=0, verbose_name='Capacity')  # 0 = unlimited
    member_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Member price')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='UPCOMING', verbose_name='Status')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['event_date']

    def __str__(self):
        return self.name

    @property
    def registration_count(self):
        return self.registrations.count()

    @property
    def remaining_capacity(self):
        if self.capacity == 0:
            return None  # unlimited
        return self.capacity - self.registration_count


class EventRegistration(models.Model):
    """A member registered for an event. Duplicate (event, member) is blocked."""

    ATTENDANCE_CHOICES = [
        ('REGISTERED', 'Registered'),
        ('ATTENDED', 'Attended'),
        ('ABSENT', 'Absent'),
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations', verbose_name='Event')
    member = models.ForeignKey('members.Member', on_delete=models.CASCADE, related_name='event_registrations', verbose_name='Member')
    registration_date = models.DateField(default=timezone.localdate, verbose_name='Registration date')
    attendance_status = models.CharField(max_length=10, choices=ATTENDANCE_CHOICES, default='REGISTERED', verbose_name='Attendance')

    class Meta:
        unique_together = ('event', 'member')
        ordering = ['registration_date']

    def __str__(self):
        return f'{self.member.full_name} -> {self.event.name}'


class Announcement(models.Model):
    """An announcement shown to members. Auto-inactive after expiry."""

    AUDIENCE_CHOICES = [
        ('ALL', 'All Members'),
        ('STUDENT', 'Student Members'),
        ('PROFESSIONAL', 'Professional Members'),
        ('CORPORATE', 'Corporate Members'),
    ]

    PRIORITY_CHOICES = [
        ('NORMAL', 'Normal'),
        ('IMPORTANT', 'Important'),
    ]

    title = models.CharField(max_length=200, verbose_name='Title')
    message = models.TextField(verbose_name='Message')
    audience = models.CharField(max_length=20, choices=AUDIENCE_CHOICES, default='ALL', verbose_name='Audience')
    publish_date = models.DateField(default=timezone.localdate, verbose_name='Publish date')
    expiry_date = models.DateField(null=True, blank=True, verbose_name='Expiry date')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='NORMAL', verbose_name='Priority')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='announcements', verbose_name='Created by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-publish_date']

    def __str__(self):
        return self.title

    @property
    def is_active(self):
        today = timezone.localdate()
        if self.publish_date > today:
            return False
        if self.expiry_date and self.expiry_date < today:
            return False
        return True


class EmailLog(models.Model):
    """History of admin-to-member emails."""

    subject = models.CharField(max_length=255, verbose_name='Subject')
    audience = models.CharField(max_length=255, verbose_name='Recipients / audience')
    recipient_count = models.PositiveIntegerField(default=0, verbose_name='Recipients')
    sent_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='emails_sent', verbose_name='Sent by')
    sent_at = models.DateTimeField(auto_now_add=True, verbose_name='Sent at')

    class Meta:
        ordering = ['-sent_at']

    def __str__(self):
        return self.subject
