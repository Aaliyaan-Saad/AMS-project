from django import forms

from members.models import Member

from .models import Announcement, Event, EventRegistration


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            "name",
            "description",
            "event_date",
            "event_time",
            "venue",
            "capacity",
            "member_price",
            "status",
        ]
        widgets = {
            "event_date": forms.DateInput(attrs={"type": "date"}),
            "event_time": forms.TimeInput(attrs={"type": "time"}),
        }


class EventRegistrationForm(forms.ModelForm):
    class Meta:
        model = EventRegistration
        fields = ["member"]
        widgets = {
            "member": forms.Select(attrs={"class": "form-select"}),
        }


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = [
            "title",
            "message",
            "audience",
            "publish_date",
            "expiry_date",
            "priority",
        ]
        widgets = {
            "publish_date": forms.DateInput(attrs={"type": "date"}),
            "expiry_date": forms.DateInput(attrs={"type": "date"}),
        }


class EmailComposeForm(forms.Form):
    RECIPIENT_CHOICES = [
        ("single", "Single member"),
        ("selected", "Selected members"),
        ("all", "All members"),
    ]

    recipient_type = forms.ChoiceField(
        choices=RECIPIENT_CHOICES,
        label="Recipients",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    members = forms.ModelMultipleChoiceField(
        queryset=Member.objects.all(),
        required=False,
        label="Members",
        widget=forms.SelectMultiple(attrs={"class": "form-select"}),
    )
    subject = forms.CharField(
        max_length=255,
        label="Subject",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    body = forms.CharField(
        label="Message",
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 6}),
    )

    def clean(self):
        cleaned = super().clean()
        recipient_type = cleaned.get("recipient_type")
        members = cleaned.get("members") or []

        if recipient_type == "single" and len(members) != 1:
            raise forms.ValidationError(
                "Select exactly one member when sending to a single member."
            )
        if recipient_type == "selected" and not members:
            raise forms.ValidationError(
                "Select at least one member when sending to selected members."
            )

        return cleaned
