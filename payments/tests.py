from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from members.models import Member, MembershipPlan
from payments.models import Donation, Payment


class PaymentTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.admin = User.objects.create_user(
            email='admin@test.com', name='Test Admin', role='ADMIN', password='Passw0rd!'
        )
        self.staff = User.objects.create_user(
            email='staff@test.com', name='Test Staff', role='STAFF', password='Passw0rd!'
        )
        self.plan = MembershipPlan.objects.create(name='Test Plan', price=100, duration_months=12)
        self.member = Member.objects.create(
            first_name='John', last_name='Doe', email='john@test.com', plan=self.plan,
            join_date=timezone.localdate(), expiry_date=timezone.localdate() + timedelta(days=365),
        )
        self.client.login(email='admin@test.com', password='Passw0rd!')

    def test_payment_list_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('payment_list'))
        self.assertEqual(response.status_code, 302)

    def test_create_payment(self):
        response = self.client.post(reverse('payment_add'), {
            'member': self.member.pk,
            'payment_type': 'MEMBERSHIP',
            'amount': '100.00',
            'payment_method': 'CASH',
            'payment_date': timezone.localdate(),
            'status': 'PAID',
        })
        self.assertRedirects(response, reverse('payment_list'))
        self.assertEqual(Payment.objects.count(), 1)
        self.assertTrue(Payment.objects.first().payment_code.startswith('PAY-'))

    def test_receipt_only_for_paid(self):
        payment = Payment.objects.create(
            member=self.member, payment_type='MEMBERSHIP', amount=100,
            payment_method='CASH', payment_date=timezone.localdate(), status='PENDING',
        )
        response = self.client.get(reverse('payment_receipt', args=[payment.pk]))
        self.assertRedirects(response, reverse('payment_list'))
        payment.status = 'PAID'
        payment.save()
        response = self.client.get(reverse('payment_receipt', args=[payment.pk]))
        self.assertEqual(response.status_code, 200)

    def test_public_donate_page(self):
        response = self.client.get(reverse('public_donate'))
        self.assertEqual(response.status_code, 200)

    def test_public_donate_valid_member(self):
        response = self.client.post(reverse('public_donate'), {
            'member_code': self.member.member_code,
            'amount': '50.00',
            'payment_method': 'CARD',
            'message': 'Thank you',
        })
        self.assertEqual(response.status_code, 200)
        donation = Donation.objects.first()
        self.assertEqual(donation.amount, 50)
        self.assertEqual(donation.status, 'PENDING')

    def test_public_donate_unknown_member_rejected(self):
        response = self.client.post(reverse('public_donate'), {
            'member_code': 'MEM-9999',
            'amount': '50.00',
            'payment_method': 'CARD',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Donation.objects.count(), 0)

    def test_donation_status_update_admin_only(self):
        donation = Donation.objects.create(member=self.member, amount=50, payment_method='CARD')
        self.client.logout()
        self.client.login(email='staff@test.com', password='Passw0rd!')
        response = self.client.post(reverse('donation_status', args=[donation.pk]), {'status': 'RECEIVED'})
        self.assertNotEqual(response.status_code, 200)
        donation.refresh_from_db()
        self.assertEqual(donation.status, 'PENDING')
