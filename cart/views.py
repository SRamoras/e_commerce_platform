import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.models import Profile
from .services import (
    get_cart_contents,
    add_to_cart,
    remove_from_cart,
    update_cart_item,
    clear_cart,
)


def is_buyer(user):
    return Profile.objects.filter(user=user, role=Profile.Role.BUYER).exists()


@login_required
def cart_page_view(request):
    if not is_buyer(request.user):
        return render(
            request,
            "cart/cart.html",
            {"error": "Apenas buyers podem acessar o carrinho.", "cart": None},
        )

    cart_data = get_cart_contents(request.user)
    return render(request, "cart/cart.html", {"cart": cart_data})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def cart_view(request):
    if not is_buyer(request.user):
        return Response(
            {"detail": "Apenas buyers podem acessar o carrinho."},
            status=status.HTTP_403_FORBIDDEN,
        )

    cart_data = get_cart_contents(request.user)
    return Response(cart_data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def cart_add_view(request):
    if not is_buyer(request.user):
        return Response(
            {"detail": "Apenas buyers podem adicionar itens ao carrinho."},
            status=status.HTTP_403_FORBIDDEN,
        )

    try:
        data = request.data
        variant_id = data.get("variant_id")
        quantity = int(data.get("quantity", 1))

        if not variant_id:
            return Response(
                {"variant_id": ["This field is required."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if quantity <= 0:
            return Response(
                {"quantity": ["Quantity must be greater than 0."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        item = add_to_cart(request.user, variant_id, quantity)
        return Response(
            {
                "id": item.id,
                "variant_id": item.variant_id,
                "quantity": item.quantity,
                "subtotal": str(item.subtotal),
            },
            status=status.HTTP_201_CREATED,
        )
    except ValueError as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def cart_remove_view(request, item_id):
    if not is_buyer(request.user):
        return Response(
            {"detail": "Apenas buyers podem remover itens do carrinho."},
            status=status.HTTP_403_FORBIDDEN,
        )

    try:
        remove_from_cart(request.user, item_id)
        return Response({"detail": "Item removed from cart."})
    except ValueError as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def cart_update_view(request, item_id):
    if not is_buyer(request.user):
        return Response(
            {"detail": "Apenas buyers podem atualizar itens do carrinho."},
            status=status.HTTP_403_FORBIDDEN,
        )

    try:
        quantity = int(request.data.get("quantity", 1))

        if quantity <= 0:
            remove_from_cart(request.user, item_id)
            return Response({"detail": "Item removed from cart."})

        item = update_cart_item(request.user, item_id, quantity)

        if item is None:
            return Response({"detail": "Item removed from cart."})

        return Response(
            {
                "id": item.id,
                "variant_id": item.variant_id,
                "quantity": item.quantity,
                "subtotal": str(item.subtotal),
            }
        )
    except ValueError as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def cart_clear_view(request):
    if not is_buyer(request.user):
        return Response(
            {"detail": "Apenas buyers podem limpar o carrinho."},
            status=status.HTTP_403_FORBIDDEN,
        )

    clear_cart(request.user)
    return Response({"detail": "Cart cleared successfully."})
