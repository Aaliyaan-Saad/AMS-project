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

# Color palette used by the chart tags (kept in sync with style.css).
CHART_PALETTE = ['#2563eb', '#16a34a', '#d97706', '#7c3aed', '#0891b2', '#dc2626', '#0ea5e9', '#84cc16']


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


def _normalize_rows(rows):
    """Return a list of (label, value, color) tuples with colors auto-assigned."""
    out = []
    for i, row in enumerate(rows):
        label, value = row[0], row[1]
        color = row[2] if len(row) > 2 else CHART_PALETTE[i % len(CHART_PALETTE)]
        out.append((label, value, color))
    return out


@register.simple_tag
def chart_bars(rows, value_format='plain'):
    """Horizontal bar chart. rows = [(label, value), ...] or [(label, value, color), ...].

    value_format: 'plain' shows raw numbers, 'money' shows $x.xx.
    """
    items = _normalize_rows(rows)
    if not items:
        return mark_safe('<div class="chart-empty">No data yet.</div>')

    max_value = max(value for _, value, _ in items) or 1
    parts = ['<div class="chart">']
    for label, value, color in items:
        if value_format == 'money':
            shown = f'${value:,.2f}' if value else '$0'
        else:
            shown = f'{value:g}'
        pct = round(value / max_value * 100)
        empty_class = ' empty' if value == 0 else ''
        parts.append(
            f'<div class="chart-row">'
            f'<div class="chart-label">{label}</div>'
            f'<div class="chart-track">'
            f'<div class="chart-bar{empty_class}" style="width:{pct}%;background:{color};">{shown}</div>'
            f'</div>'
            f'</div>'
        )
    parts.append('</div>')
    return mark_safe(''.join(parts))


@register.simple_tag
def donut_chart(rows, center_label='Total'):
    """Donut chart (pure CSS conic-gradient) with a legend.

    rows = [(label, value), ...] or [(label, value, color), ...].
    """
    items = _normalize_rows(rows)
    total = sum(value for _, value, _ in items)
    if total == 0:
        return mark_safe('<div class="chart-empty">No data yet.</div>')

    angle = 0.0
    stops = []
    for _, value, color in items:
        span = value / total * 360
        stops.append(f'{color} {angle:.2f}deg {angle + span:.2f}deg')
        angle += span

    gradient = 'conic-gradient(' + ', '.join(stops) + ')'
    legend = []
    for label, value, color in items:
        legend.append(
            f'<div class="legend-item">'
            f'<span class="legend-dot" style="background:{color};"></span>'
            f'<span class="legend-name">{label}</span>'
            f'<span class="legend-val">{value}</span>'
            f'</div>'
        )

    return mark_safe(
        '<div class="chart-flex">'
        f'<div class="donut-wrap"><div class="donut" style="background:{gradient};"></div>'
        f'<div class="donut-hole"><div class="donut-total">{total}</div><div class="donut-label">{center_label}</div></div></div>'
        f'<div class="legend">{"".join(legend)}</div>'
        '</div>'
    )
