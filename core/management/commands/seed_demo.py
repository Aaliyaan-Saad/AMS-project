"""Seed the database with demo data so the system is usable immediately.

Usage:
    python manage.py seed_demo
"""
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from events.models import Announcement, EmailLog, Event, EventRegistration
from members.models import Member, MembershipPlan
from payments.models import Donation, Payment


class Command(BaseCommand):
    help = 'Seed the database with demo users, members, plans, payments, events and donations.'

    def handle(self, *args, **options):
        User = get_user_model()
        today = timezone.localdate()

        admin, _ = User.objects.get_or_create(
            email='admin@ams.com',
            defaults={'name': 'System Admin', 'role': 'ADMIN', 'is_staff': True, 'is_superuser': True},
        )
        admin.set_password('Admin@123')
        admin.save()

        staff, _ = User.objects.get_or_create(
            email='staff@ams.com',
            defaults={'name': 'Staff Member', 'role': 'STAFF'},
        )
        staff.set_password('Staff@123')
        staff.save()

        plans = {
            'Student': MembershipPlan.objects.get_or_create(name='Student', defaults={
                'price': 100, 'duration_months': 12, 'description': 'For full-time students.', 'active': True,
            })[0],
            'Professional': MembershipPlan.objects.get_or_create(name='Professional', defaults={
                'price': 250, 'duration_months': 12, 'description': 'For working professionals.', 'active': True,
            })[0],
            'Corporate': MembershipPlan.objects.get_or_create(name='Corporate', defaults={
                'price': 500, 'duration_months': 12, 'description': 'For organisations and companies.', 'active': True,
            })[0],
        }

        sample_members = [
            ('James', 'Miller', 'james.miller@example.com', 'Professional', 320, True),
            ('Sofia', 'Carter', 'sofia.carter@example.com', 'Student', 210, True),
            ('Liam', 'Johnson', 'liam.johnson@example.com', 'Corporate', 90, True),
            ('Emma', 'Williams', 'emma.williams@example.com', 'Student', 300, True),
            ('Noah', 'Brown', 'noah.brown@example.com', 'Professional', 140, True),
            ('Olivia', 'Davis', 'olivia.davis@example.com', 'Professional', 75, True),
            ('Ethan', 'Garcia', 'ethan.garcia@example.com', 'Corporate', 55, True),
            ('Ava', 'Rodriguez', 'ava.rodriguez@example.com', 'Student', 180, True),
            ('Mason', 'Wilson', 'mason.wilson@example.com', 'Professional', 25, True),
            ('Isabella', 'Martinez', 'isabella.martinez@example.com', 'Corporate', 45, True),
            ('Logan', 'Anderson', 'logan.anderson@example.com', 'Professional', 15, False),
            ('Mia', 'Thomas', 'mia.thomas@example.com', 'Student', 210, False),
            ('Lucas', 'Taylor', 'lucas.taylor@example.com', 'Corporate', 60, False),
        ]

        members = []
        for first, last, email, plan_name, months_ago, active in sample_members:
            join = today - timedelta(days=months_ago * 30)
            expiry = join + timedelta(days=plan_days(plans[plan_name])) if active else today - timedelta(days=40)
            member, created = Member.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': first,
                    'last_name': last,
                    'phone': f'+1 555 {100 + len(members)}0 0000',
                    'city': ['London', 'Manchester', 'Leeds', 'Bristol'][len(members) % 4],
                    'plan': plans[plan_name],
                    'join_date': join,
                    'expiry_date': expiry,
                    'last_renewed_date': join,
                },
            )
            members.append(member)

        # Payments
        payment_counter = 1
        for i, member in enumerate(members[:12]):
            Payment.objects.get_or_create(
                payment_code=f'PAY-{payment_counter:04d}',
                defaults={
                    'member': member,
                    'payment_type': 'MEMBERSHIP',
                    'amount': member.plan.price,
                    'payment_method': 'CASH',
                    'payment_date': member.join_date,
                    'status': 'PAID',
                },
            )
            payment_counter += 1
            Payment.objects.get_or_create(
                payment_code=f'PAY-{payment_counter:04d}',
                defaults={
                    'member': member,
                    'payment_type': 'RENEWAL',
                    'amount': member.plan.price,
                    'payment_method': 'BANK_TRANSFER',
                    'payment_date': today - timedelta(days=(i * 5) % 30),
                    'status': 'PENDING' if i % 3 == 0 else 'PAID',
                },
            )
            payment_counter += 1

        # Events
        event_data = [
            ('Annual General Meeting', 40, today + timedelta(days=14), 'Main Hall'),
            ('Networking Night', 60, today + timedelta(days=30), 'Riverside Lounge'),
            ('Workshop: Personal Finance', 30, today + timedelta(days=45), 'Room B2'),
            ('Summer Picnic', 100, today - timedelta(days=20), 'City Park'),
        ]
        events = []
        for name, capacity, event_date, venue in event_data:
            event, _ = Event.objects.get_or_create(
                name=name,
                defaults={
                    'description': f'Members event: {name}.',
                    'event_date': event_date,
                    'event_time': '18:00',
                    'venue': venue,
                    'capacity': capacity,
                    'member_price': 0 if 'Picnic' in name else 15,
                    'status': 'COMPLETED' if event_date < today else 'UPCOMING',
                },
            )
            events.append(event)

        for i, member in enumerate(members[:8]):
            event = events[i % 2]
            EventRegistration.objects.get_or_create(
                event=event,
                member=member,
                defaults={
                    'registration_date': today - timedelta(days=2),
                    'attendance_status': 'REGISTERED',
                },
            )

        # Announcements
        Announcement.objects.get_or_create(
            title='Welcome to the new AMS portal',
            defaults={
                'message': 'The association now has an online member portal. Log in to manage your membership.',
                'audience': 'ALL',
                'publish_date': today,
                'expiry_date': today + timedelta(days=30),
                'priority': 'IMPORTANT',
                'created_by': admin,
            },
        )
        Announcement.objects.get_or_create(
            title='Annual General Meeting',
            defaults={
                'message': 'Join us for the AGM. Registration is required.',
                'audience': 'ALL',
                'publish_date': today - timedelta(days=1),
                'expiry_date': today + timedelta(days=13),
                'priority': 'NORMAL',
                'created_by': admin,
            },
        )
        Announcement.objects.get_or_create(
            title='Student fee deadline',
            defaults={
                'message': 'Student membership renewals are due this month.',
                'audience': 'STUDENT',
                'publish_date': today - timedelta(days=10),
                'expiry_date': today - timedelta(days=2),
                'priority': 'NORMAL',
                'created_by': staff,
            },
        )

        # Donations
        Donation.objects.get_or_create(
            donation_code='DON-9001',
            defaults={
                'member': members[0],
                'amount': 50,
                'donation_date': today - timedelta(days=5),
                'payment_method': 'CARD',
                'message': 'Keep up the great work!',
                'status': 'RECEIVED',
            },
        )
        Donation.objects.get_or_create(
            donation_code='DON-9002',
            defaults={
                'member': members[1],
                'amount': 25,
                'donation_date': today,
                'payment_method': 'CASH',
                'message': '',
                'status': 'PENDING',
            },
        )

        # Email log
        EmailLog.objects.get_or_create(
            subject='Welcome to the association',
            defaults={
                'audience': 'All Members',
                'recipient_count': len(members),
                'sent_by': admin,
                'sent_at': today - timedelta(days=3),
            },
        )

        self.stdout.write(self.style.SUCCESS(
            f'Seed complete: {len(members)} members, {len(events)} events, '
            f'{len(plans)} plans, admin/staff users created.'
        ))


def plan_days(plan):
    return plan.duration_months * 30
