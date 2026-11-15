from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST

from orders.models import Order
from orders.services import OrderCannotBeCancelled, cancel_order


@require_GET
@login_required
def order_list(request):
    status = request.GET.get("status")
    valid_statuses = set(Order.Status.values)
    if status is not None and status not in valid_statuses:
        return JsonResponse({"error": "invalid_status"}, status=400)

    orders = Order.objects.filter(owner=request.user)
    if status is not None:
        orders = orders.filter(status=status)
    orders = orders.order_by("-created_at", "-id")

    data = [
        {
            "id": order.id,
            "title": order.title,
            "status": order.status,
            "total": str(order.total),
            "created_at": order.created_at.isoformat(),
        }
        for order in orders
    ]
    return JsonResponse({"orders": data})


@require_POST
@login_required
def cancel(request, order_id):
    try:
        order = Order.objects.get(pk=order_id)
    except Order.DoesNotExist:
        return JsonResponse({"error": "not_found"}, status=404)

    if order.owner_id != request.user.id:
        return JsonResponse({"error": "forbidden"}, status=403)

    try:
        cancel_order(order)
    except OrderCannotBeCancelled:
        return JsonResponse({"error": "cannot_cancel"}, status=400)

    return JsonResponse({"id": order.id, "status": order.status})
