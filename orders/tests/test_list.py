from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from orders.models import Order


class OrderListTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="owner@example.com",
            password="safe-pass-123",
        )
        other_user = User.objects.create_user(
            username="other@example.com",
            password="safe-pass-123",
        )
        self.new_order = Order.objects.create(
            owner=self.user,
            title="Новый заказ",
            status=Order.Status.NEW,
            total=Decimal("100.00"),
        )
        self.paid_order = Order.objects.create(
            owner=self.user,
            title="Оплаченный заказ",
            status=Order.Status.PAID,
            total=Decimal("250.50"),
        )
        Order.objects.create(
            owner=other_user,
            title="Чужой заказ",
            status=Order.Status.NEW,
            total=Decimal("999.00"),
        )
        self.client.force_login(self.user)
        self.url = reverse("orders:list")

    def test_list_contains_only_own_orders(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        order_ids = [item["id"] for item in response.json()["orders"]]
        self.assertEqual(order_ids, [self.paid_order.id, self.new_order.id])

    def test_list_filters_by_status(self):
        response = self.client.get(self.url, {"status": Order.Status.PAID})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [item["id"] for item in response.json()["orders"]],
            [self.paid_order.id],
        )

    def test_invalid_status_returns_400(self):
        response = self.client.get(self.url, {"status": "unknown"})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "invalid_status"})
