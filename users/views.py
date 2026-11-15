import json

from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST


@csrf_exempt
@require_POST
def register(request):
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"error": "invalid_json"}, status=400)

    if not isinstance(data, dict):
        return JsonResponse({"error": "invalid_json"}, status=400)

    email = data.get("email")
    password = data.get("password")
    if not isinstance(email, str) or not isinstance(password, str):
        return JsonResponse({"error": "email_and_password_required"}, status=400)

    email = email.strip().lower()
    if not email or not password:
        return JsonResponse({"error": "email_and_password_required"}, status=400)
    if len(password) < 8:
        return JsonResponse({"error": "password_too_short"}, status=400)
    if User.objects.filter(Q(username=email) | Q(email=email)).exists():
        return JsonResponse({"error": "email_taken"}, status=400)

    try:
        with transaction.atomic():
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
            )
    except IntegrityError:
        if User.objects.filter(Q(username=email) | Q(email=email)).exists():
            return JsonResponse({"error": "email_taken"}, status=400)
        raise

    return JsonResponse({"id": user.id, "email": user.email}, status=201)
