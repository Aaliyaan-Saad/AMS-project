# TEAM WORKFLOW — how the three developers collaborate

This file is the ground rule for the whole project. **Read it before writing any code.**

## One repo, one project, separate folders

Everyone works inside the **same Django project** (same repo, same database). Nobody builds a separate
project. Each developer only edits files **inside their own app folder**.

```
/ams_project
├── config/     ← ONLY Developer 3 (leader) edits
├── core/       ← ONLY Developer 3
├── static/     ← ONLY Developer 3
├── members/    ← ONLY Developer 1
├── events/     ← ONLY Developer 2
└── payments/   ← ONLY Developer 3
```

| Folder | Owner | What you build here |
|---|---|---|
| `members/` | Developer 1 | views, forms, templates, URL routes for members & plans |
| `events/` | Developer 2 | views, forms, templates, URL routes for events, announcements, email |
| `payments/`, `core/`, `config/`, `static/` | Developer 3 | already implemented — do not edit |

> If you need something changed in a shared file (a sidebar link, a new badge colour, a field),
> **ask Developer 3** to do it. Do not edit shared files yourself.

## What is already done for you

- **All database models** (`Member`, `MembershipPlan`, `Event`, `EventRegistration`, `Announcement`,
  `EmailLog`, `Payment`, `Donation`, `User`) — the shared contract. **Do not change model fields.**
- Migrations, shared layout, dashboard, payments, donations, auth, seed data.
- Your app's `urls.py` already exists with instructions (see the comments inside it).

Your job is to add the **functional layer**: views, forms, URLs, and templates.

## Getting started (first time)

```bash
git clone https://github.com/YOUR-ORG/ams_project.git
cd ams_project
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Check it works: open http://127.0.0.1:8000/ and log in (`admin@ams.com` / `Admin@123`).

## Daily workflow

```bash
git checkout main
git pull origin main          # 1. always get the latest merged work first
git checkout -b dev1-members  # 2. your OWN branch (Dev 2 uses dev2-events)
# ... write code ONLY inside your folder ...
git status                    # 3. check: it should only show YOUR folder
git add members/              # 4. stage only your files
git commit -m "members: list and add pages"
git push -u origin dev1-members
```

Then open a **Pull Request** on GitHub from your branch to `main` and ask the leader to review and merge.
The leader merges; **you never merge your own PR.**

After the leader merges (or when they say so), everyone:

```bash
git checkout main
git pull origin main
python manage.py makemigrations --check   # nothing should be pending
python manage.py migrate                  # apply any new tables from the merge
```

## The rules (non-negotiable)

1. **Only the leader edits** `config/`, `core/`, `payments/`, `static/`.
2. **Never touch files outside your own folder.** Check `git status` before every commit.
3. **Never change model field names.** Models are the shared contract (everything references them).
4. **Never delete your database file to "fix" things.** Use `python manage.py migrate` and `seed_demo`.
5. Pull before you start, commit small and often, always use a PR.
6. If git says you have a **conflict**, stop and ask the leader — do not force-push or overwrite others' work.
7. Use the shared layout: extend `base.html`, set `page_title`, reuse existing partials, badges and CSS classes.

## Your URL space (owned by you)

**Developer 1** — your routes live under `/members/` (registered in `config/urls.py`). The sidebar already
links to `/members/` and `/members/plans/` — make sure those pages exist.

**Developer 2** — your routes live under `/events/`. The sidebar already links to `/events/`,
`/events/announcements/` and `/events/email/` (email history) — make sure those pages exist.

Suggested routes are listed in the comments at the top of your `urls.py`.

## Shared UI cheat sheet

- Templates: start with `{% extends 'base.html' %}` and a `{% block content %}`.
- Page heading: set `{% block page_title %}My Page{% endblock %}` (shows in the top bar).
- Status pills: `{% load ams_tags %}` then `{% status_badge value %}` (green/yellow/red/gray automatically).
- Tables: wrap in `<div class="table-wrap">`.
- Delete confirm: `<form method="post" data-confirm="Delete this?">` (modal appears automatically).
- Toasts/messages: `messages.success(request, '...')` (shown automatically).
- Loading state: add class `js-loading` to your form.
- Pagination: include `{% include 'partials/pagination.html' %}` and paginate with `Paginator`.
- Empty states: copy the pattern from `payments/templates/payments/payment_list.html`.

## Scope — what NOT to build

Do not add: SMS, committees, chapters, groups, tickets, complaints, resource library, certificates,
QR/RFID/barcodes, public member directory, complex RBAC, recurring payments, accounting, voting, AI,
mobile app, email marketing/tracking, donation campaigns/goals. These are future work — stay in scope.

## Definition of done for a feature

- Page uses the shared layout, badges, tables and forms.
- Confirmation on deletes, success/error messages on actions.
- Empty states and search/filter bars where the module spec says so.
- `python manage.py check` passes and nothing outside your folder was changed.
- A PR is open for review.
