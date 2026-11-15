from orders.models import Order


class OrderCannotBeCancelled(Exception):
    """Raised when an order is already cancelled."""


def cancel_order(order):
    if order.status not in {Order.Status.NEW, Order.Status.PAID}:
        raise OrderCannotBeCancelled

    order.status = Order.Status.CANCELLED
    order.save(update_fields=["status"])
    return order
