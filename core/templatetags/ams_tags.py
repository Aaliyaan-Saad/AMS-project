from django import template
from django.utils.safestring import mark_safe

register = template.Library()

STATUS_COLORS = {
    'Active': 'success',
    'Paid': 'success',
    'Received': 'success',
    'Attended': 'success',
    'Upcoming': 'info',
    'Registered': 'info',
    'Pending': 'warning',
    'Expired': 'danger',
    'Absent': 'danger',
    'Cancelled': 'danger',
    'Completed': 'gray',
    'Normal': 'gray',
    'Important': 'danger',
}


@register.simple_tag
def status_badge(status):
    """Render a colored status pill, e.g. {% status_badge member.status %}."""
    key = str(status).strip()
    color = STATUS_COLORS.get(key, 'gray')
    return mark_safe(f'<span class="badge badge-{color}">{key}</span>')


@register.filter
def divide(value, arg):
    """Division with safe fallback, used by the dashboard chart."""
    try:
        return float(value) / float(arg)
    except (TypeError, ValueError, ZeroDivisionError):
        return 0
