from django.contrib import admin

from .models import Announcement, EmailLog, Event, EventRegistration


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'event_date', 'event_time', 'venue', 'capacity', 'registration_count', 'status')
    list_filter = ('status',)
    search_fields = ('name', 'venue')


@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ('event', 'member', 'registration_date', 'attendance_status')
    list_filter = ('attendance_status', 'event')
    search_fields = ('member__first_name', 'member__last_name', 'event__name')


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'audience', 'priority', 'publish_date', 'expiry_date', 'is_active')
    list_filter = ('audience', 'priority')
    search_fields = ('title', 'message')


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ('subject', 'audience', 'recipient_count', 'sent_by', 'sent_at')
    search_fields = ('subject',)
