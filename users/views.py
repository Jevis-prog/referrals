import time
from typing import Any

import requests
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .auth_codes import send_code, verify_code
from .forms import CodeForm, InviteForm, PhoneForm
from .models import User
from .serializers import (
    ActivateInviteCodeSerializer,
    ProfileSerializer,
    RequestCodeSerializer,
    VerifyCodeSerializer,
)
from .utils import generate_invite_code, get_tokens_for_user

UserModel = get_user_model()


class RequestCodeView(APIView):
    def post(self, request: Request) -> Response:
        serializer = RequestCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone: int = serializer.validated_data["phone_number"]
        send_code(phone)
        return Response({"detail": "Код отправлен"}, status=status.HTTP_200_OK)


class VerifyCodeView(APIView):
    def post(self, request: Request) -> Response:
        serializer = VerifyCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone: int = serializer.validated_data["phone_number"]
        code: int = serializer.validated_data["code"]

        if not verify_code(phone, code):
            return Response({"detail": "Неверный код"}, status=status.HTTP_400_BAD_REQUEST)

        user, created = UserModel.objects.get_or_create(
            phone_number=phone, defaults={"invite_code": generate_invite_code()}
        )

        tokens: dict[str, str] = get_tokens_for_user(user)

        return Response(
            {
                "phone_number": user.phone_number,
                "invite_code": user.invite_code,
                "access": tokens["access"],
                "refresh": tokens["refresh"],
                "detail": "Авторизация успешна",
            },
            status=status.HTTP_200_OK,
        )


class ProfileView(generics.RetrieveAPIView):
    permission_classes: list[type[IsAuthenticated]] = [IsAuthenticated]
    serializer_class: type[ProfileSerializer] = ProfileSerializer

    def get_object(self) -> UserModel:
        return self.request.user


class ActivateInviteCodeView(APIView):
    permission_classes: list[type[IsAuthenticated]] = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        serializer = ActivateInviteCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code: str = serializer.validated_data["invite_code"]
        user: User = request.user

        if user.invited_by:
            return Response(
                {"detail": "Инвайт-код уже был активирован"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            invited_by_user: UserModel = UserModel.objects.get(invite_code=code)
        except UserModel.DoesNotExist:
            return Response({"detail": "Инвайт-код не найден"}, status=status.HTTP_404_NOT_FOUND)

        if invited_by_user == user:
            return Response(
                {"detail": "Нельзя ввести свой собственный код"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.invited_by = invited_by_user
        user.save()

        return Response({"detail": "Инвайт-код успешно активирован"})


API_BASE: str = "http://127.0.0.1:8000/api"


def phone_view(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = PhoneForm(request.POST)
        if form.is_valid():
            phone: int = form.cleaned_data["phone_number"]
            response: requests.Response = requests.post(f"{API_BASE}/auth/request_code/", json={"phone_number": phone})
            if response.status_code == 200:
                request.session["phone_number"] = phone
                messages.success(request, "Код отправлен на номер")
                return redirect("code")
            messages.error(request, "Ошибка при отправке кода")
    else:
        form = PhoneForm()
    return render(request, "users/phone.html", {"form": form})


def code_view(request: HttpRequest) -> HttpResponse:
    phone: int | None = request.session.get("phone_number")
    if not phone:
        return redirect("phone")

    if request.method == "POST":
        form = CodeForm(request.POST)
        if form.is_valid():
            code: str = form.cleaned_data["code"]
            response: requests.Response = requests.post(
                f"{API_BASE}/auth/verify_code/",
                json={"phone_number": phone, "code": code},
            )
            if response.status_code == 200:
                data: dict[str, Any] = response.json()
                request.session["access"] = data.get("access")
                request.session["refresh"] = data.get("refresh")
                messages.success(request, "Авторизация успешна")
                return redirect("profile")
            messages.error(request, "Неверный код")
    else:
        form = CodeForm()
    return render(request, "users/code.html", {"form": form})


def profile_view(request: HttpRequest) -> HttpResponse:
    token: str | None = request.session.get("access")
    if not token:
        messages.error(request, "Токен отсутствует, пожалуйста, войдите заново")
        return redirect("phone")

    headers: dict[str, str] = {"Authorization": f"Bearer {token}"}
    response: requests.Response = requests.get(f"{API_BASE}/profile_back/", headers=headers)

    if response.status_code != 200:
        messages.error(request, "Ошибка получения профиля")
        return redirect("phone")

    profile_data: dict[str, Any] = response.json()

    if request.method == "POST":
        form = InviteForm(request.POST)
        if form.is_valid():
            invite_code: int = form.cleaned_data["invite_code"]
            resp: requests.Response = requests.post(
                f"{API_BASE}/profile/activate_invite/",
                json={"invite_code": invite_code},
                headers=headers,
            )
            if resp.status_code == 200:
                messages.success(request, "Инвайт-код активирован")
                return redirect("profile")
            messages.error(request, "Ошибка активации инвайт-кода")
    else:
        form = InviteForm()

    return render(
        request,
        "users/profile.html",
        {
            "profile": profile_data,
            "form": form,
            "invited_users": profile_data.get("invited_users", []),
        },
    )
