# AMS — Association Management System

A small, fully working association management system built with **Django + SQLite** for a 3-person university/group project.

## Modules

| Module | Description |
|---|---|
| Authentication | Login/logout with hashed passwords, roles: **Admin** / **Staff**, protected routes |
| Dashboard | Real database stats: total/active/expired members, total revenue, total donations, upcoming events, recent members/payments/donations, members-by-plan chart, active announcements |
| Members | Auto Member IDs (`MEM-0001`), search + filters, add/edit/delete, profile page, renewal |
| Memberships | Plans: Student / Professional / Corporate (price, duration, description). Create / edit / disable (never delete plans in use) |
| Payments | Records only (no gateway). Types: Membership / Renewal / Event fee. Methods: Cash / Bank Transfer / Card. Status: Paid / Pending. Printable receipt for paid payments |
| Events | Events with capacity + member price, registrations (duplicates blocked), manual attendance |
| Email | Admin-to-member email (one / selected / all), email history. Console backend in dev, real SMTP switchable |
| Announcements | Audience + priority + publish/expiry dates, auto-inactive after expiry |
| Donations | Public donate page (member enters Member ID → Pending), admin list with filters + totals, admin confirmation |

## Tech Stack

- Python 3.12, Django 6.x, SQLite (single file — zero config)
- Custom `User` model: login by **email**, `role` field (`ADMIN` / `STAFF`)
- Custom CSS/JS only (no external CDNs)

## Quick Start

```bash
cd ams_project
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

python manage.py migrate
python manage.py seed_demo   # demo data (members, plans, payments, events, ...)
python manage.py runserver
```

Open http://127.0.0.1:8000/ and sign in.

### Demo accounts

| Email | Password | Role |
|---|---|---|
| `admin@ams.com` | `Admin@123` | Admin (full access) |
| `staff@ams.com` | `Staff@123` | Staff (operational pages) |

### Public pages

- `http://127.0.0.1:8000/donate/` — member donation page (no login needed)

## Email Configuration

By default emails are **printed to the console** (nothing is sent). To send real
emails, edit `config/settings.py` and enable the SMTP block (see the `Email`
section in the file).

## Team Division (3 developers)

| Developer | Owns | Main tables |
|---|---|---|
| **Developer 3** (Team leader) | Auth, main layout, dashboard, payments, receipts, donations, integration | `users`, `payments`, `donations` |
| **Developer 1** | Members, member profiles, membership plans, renewal | `members`, `membership_plans` |
| **Developer 2** | Events, event registration, attendance, announcements, email | `events`, `event_registrations`, `announcements`, `email_logs` |

> **Important:** All database models are already defined (the "shared contract").
> Developers build the *functional layer* on top: views, forms, URLs, templates.
> Do not change model field names. See `TEAM_WORKFLOW.md` for the exact rules.

## URL Map

| Path | Owner | Status |
|---|---|---|
| `/` (dashboard), `/login/`, `/settings/` | Developer 3 | Done |
| `/payments/`, `/payments/add/`, `/payments/<id>/receipt/` | Developer 3 | Done |
| `/donations/`, `/donations/<id>/status/` | Developer 3 | Done |
| `/donate/` (public) | Developer 3 | Done |
| `/members/` and `/members/plans/` (…) | Developer 1 | Placeholder |
| `/events/`, `/events/announcements/`, `/events/email/` (…) | Developer 2 | Placeholder |

## Tests

```bash
python manage.py test
```

## Repository layout

```
config/     project settings & URL routing (leader only)
core/       auth, dashboard, layout, seed command (leader)
members/    Member + MembershipPlan models (contract) — Dev 1 builds here
events/     Event, EventRegistration, Announcement, EmailLog models (contract) — Dev 2 builds here
payments/   Payment + Donation models, views, templates (leader)
static/     shared CSS/JS (leader only)
```
