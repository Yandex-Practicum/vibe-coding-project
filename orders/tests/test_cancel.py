from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from orders.models import Order


class OrderCancelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="owner@example.com",
            password="safe-pass-123",
        )
        self.other_user = User.objects.create_user(
            username="other@example.com",
            password="safe-pass-123",
        )
        self.order = Order.objects.create(
            owner=self.user,
            title="Заказ",
            status=Order.Status.PAID,
            total=Decimal("100.00"),
        )
        self.client.force_login(self.user)

    def test_owner_can_cancel_order(self):
        response = self.client.post(
            reverse("orders:cancel", args=[self.order.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], Order.Status.CANCELLED)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.Status.CANCELLED)

    def test_other_users_order_returns_403(self):
        other_order = Order.objects.create(
            owner=self.other_user,
            title="Чужой заказ",
            total=Decimal("50.00"),
        )

        response = self.client.post(
            reverse("orders:cancel", args=[other_order.id])
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json(), {"error": "forbidden"})

    def test_missing_order_returns_404(self):
        response = self.client.post(reverse("orders:cancel", args=[999999]))

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"error": "not_found"})

    def test_repeated_cancel_returns_400(self):
        url = reverse("orders:cancel", args=[self.order.id])
        self.client.post(url)

        response = self.client.post(url)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "cannot_cancel"})
