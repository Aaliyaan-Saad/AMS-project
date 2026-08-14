from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from members.models import Member

from .forms import AnnouncementForm, EmailComposeForm, EventForm, EventRegistrationForm
from .models import Announcement, EmailLog, Event, EventRegistration


def event_list(request):
    events = Event.objects.all()

    search = request.GET.get("q", "").strip()
    if search:
        events = events.filter(name__icontains=search)

    paginator = Paginator(events, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "events/event_list.html", {
        "page_obj": page_obj,
        "search": search,
    })


def event_add(request):
    if request.method == "POST":
        form = EventForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Event created successfully.")
            return redirect("event_list")
    else:
        form = EventForm()

    return render(request, "events/event_form.html", {
        "form": form,
        "title": "Add Event",
    })


def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)

    registrations = event.registrations.select_related("member").order_by("registration_date")

    if request.method == "POST":
        registration_id = request.POST.get("registration_id")
        attendance_status = request.POST.get("attendance_status")

        if registration_id and attendance_status in dict(EventRegistration.ATTENDANCE_CHOICES):
            registration = get_object_or_404(EventRegistration, pk=registration_id, event=event)
            registration.attendance_status = attendance_status
            registration.save(update_fields=["attendance_status"])
            messages.success(request, "Attendance updated.")
            return redirect("event_detail", pk=event.pk)

    return render(request, "events/event_detail.html", {
        "event": event,
        "registrations": registrations,
        "register_form": EventRegistrationForm(),
        "attendance_choices": EventRegistration.ATTENDANCE_CHOICES,
    })


def event_edit(request, pk):
    event = get_object_or_404(Event, pk=pk)

    if request.method == "POST":
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, "Event updated successfully.")
            return redirect("event_detail", pk=event.pk)
    else:
        form = EventForm(instance=event)

    return render(request, "events/event_form.html", {
        "form": form,
        "title": "Edit Event",
        "event": event,
    })


def event_cancel(request, pk):
    event = get_object_or_404(Event, pk=pk)

    if request.method == "POST":
        if event.status == "CANCELLED":
            messages.info(request, "This event is already cancelled.")
        else:
            event.status = "CANCELLED"
            event.save(update_fields=["status"])
            messages.success(request, "Event cancelled successfully.")
        return redirect("event_detail", pk=event.pk)

    return render(request, "events/event_confirm_cancel.html", {
        "event": event,
    })


def event_register(request, pk):
    event = get_object_or_404(Event, pk=pk)

    if event.status == "CANCELLED":
        messages.error(request, "A cancelled event cannot accept registrations.")
        return redirect("event_detail", pk=event.pk)

    if request.method == "POST":
        form = EventRegistrationForm(request.POST)
        if form.is_valid():
            member = form.cleaned_data["member"]

            if EventRegistration.objects.filter(event=event, member=member).exists():
                messages.error(request, f"{member.full_name} is already registered for this event.")
                return redirect("event_detail", pk=event.pk)

            if event.capacity > 0 and event.registration_count >= event.capacity:
                messages.error(request, "This event is full. No more registrations can be accepted.")
                return redirect("event_detail", pk=event.pk)

            try:
                EventRegistration.objects.create(event=event, member=member)
            except IntegrityError:
                messages.error(request, f"{member.full_name} is already registered for this event.")
                return redirect("event_detail", pk=event.pk)

            messages.success(request, f"{member.full_name} registered successfully.")
            return redirect("event_detail", pk=event.pk)

        messages.error(request, "Please select a valid member.")
        return redirect("event_detail", pk=event.pk)

    return redirect("event_detail", pk=event.pk)


def announcement_list(request):
    announcements = Announcement.objects.select_related("created_by").all()

    search = request.GET.get("q", "").strip()
    audience = request.GET.get("audience", "").strip()

    if search:
        announcements = announcements.filter(
            Q(title__icontains=search) | Q(message__icontains=search)
        )
    if audience:
        announcements = announcements.filter(audience=audience)

    paginator = Paginator(announcements, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "events/announcement_list.html", {
        "page_obj": page_obj,
        "search": search,
        "audience": audience,
        "audience_choices": Announcement.AUDIENCE_CHOICES,
    })


def announcement_add(request):
    if request.method == "POST":
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.created_by = request.user
            announcement.save()
            messages.success(request, "Announcement created successfully.")
            return redirect("announcement_list")
    else:
        form = AnnouncementForm()

    return render(request, "events/announcement_form.html", {
        "form": form,
        "title": "Add Announcement",
    })


def announcement_detail(request, pk):
    announcement = get_object_or_404(
        Announcement.objects.select_related("created_by"),
        pk=pk,
    )

    return render(request, "events/announcement_detail.html", {
        "announcement": announcement,
    })


def announcement_edit(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk)

    if request.method == "POST":
        form = AnnouncementForm(request.POST, instance=announcement)
        if form.is_valid():
            form.save()
            messages.success(request, "Announcement updated successfully.")
            return redirect("announcement_detail", pk=announcement.pk)
    else:
        form = AnnouncementForm(instance=announcement)

    return render(request, "events/announcement_form.html", {
        "form": form,
        "title": "Edit Announcement",
        "announcement": announcement,
    })


def announcement_delete(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk)

    if request.method == "POST":
        announcement.delete()
        messages.success(request, "Announcement deleted successfully.")
        return redirect("announcement_list")

    return render(request, "events/announcement_confirm_delete.html", {
        "announcement": announcement,
    })


def email_list(request):
    logs = EmailLog.objects.select_related("sent_by").all()

    paginator = Paginator(logs, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "events/email_list.html", {
        "page_obj": page_obj,
    })


def email_compose(request):
    if request.method == "POST":
        form = EmailComposeForm(request.POST)
        if form.is_valid():
            recipient_type = form.cleaned_data["recipient_type"]
            subject = form.cleaned_data["subject"]
            body = form.cleaned_data["body"]

            if recipient_type == "all":
                members = list(Member.objects.all())
            else:
                members = list(form.cleaned_data["members"])

            recipient_list = [member.email for member in members]

            if not recipient_list:
                messages.error(request, "No recipients found to email.")
                return render(request, "events/email_compose.html", {"form": form})

            try:
                send_mail(
                    subject,
                    body,
                    settings.DEFAULT_FROM_EMAIL,
                    recipient_list,
                    fail_silently=False,
                )
            except Exception:
                messages.error(request, "Failed to send email. Please try again.")
                return render(request, "events/email_compose.html", {"form": form})

            if recipient_type == "all":
                audience = f"All members ({len(recipient_list)})"
            elif recipient_type == "single":
                member = members[0]
                audience = f"{member.full_name} ({member.member_code})"
            else:
                audience = f"{len(recipient_list)} selected members"

            EmailLog.objects.create(
                subject=subject,
                audience=audience,
                recipient_count=len(recipient_list),
                sent_by=request.user,
            )

            messages.success(
                request,
                f"Email sent to {len(recipient_list)} recipient(s) and logged.",
            )
            return redirect("email_list")
    else:
        form = EmailComposeForm()

    return render(request, "events/email_compose.html", {
        "form": form,
    })
