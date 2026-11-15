from django.urls import path

from orders.views import cancel, order_list


app_name = "orders"

urlpatterns = [
    path("", order_list, name="list"),
    path("<int:order_id>/cancel/", cancel, name="cancel"),
]
