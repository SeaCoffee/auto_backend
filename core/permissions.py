from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAuthenticatedOrReadOnly(BasePermission):
    """
    Доступ только для аутентифицированных пользователей или разрешение на чтение для всех.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True  # Разрешен доступ только для чтения.
        return bool(request.user and request.user.is_authenticated)  # Доступ для аутентифицированных пользователей.


class IsSeller(BasePermission):
    """
    Разрешение для пользователей с ролью продавца (seller).
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role.name == 'seller')  # Проверка роли пользователя.


class IsBuyer(BasePermission):
    """
    Разрешение для пользователей с ролью покупателя (buyer).
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role.name == 'buyer')  # Проверка роли пользователя.


class IsPremiumAccount(BasePermission):
    """
    Разрешение для пользователей с премиум аккаунтом.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.account_type == 'premium'  # Проверка типа аккаунта.
        )


class IsPremiumSeller(BasePermission):
    """
    Разрешение для пользователей с ролью продавца и премиум аккаунтом.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role.name == 'seller' and
            request.user.account_type == 'premium'  # Проверка роли и типа аккаунта.
        )


class IsManager(BasePermission):
    """
    Разрешение для пользователей с ролью менеджера.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.is_staff and  # Проверка, является ли пользователь сотрудником.
            request.user.role.name == 'manager'  # Проверка роли пользователя.
        )


class IsAdmin(BasePermission):
    """
    Разрешение для пользователей с ролью администратора (superuser).
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.is_staff and
            request.user.is_superuser  # Проверка, является ли пользователь суперпользователем.
        )


class IsSellerOrManagerAndOwner(BasePermission):
    """
    Разрешение для пользователей с ролью продавца, если они являются владельцами объекта, или для менеджеров.
    """
    def has_object_permission(self, request, view, obj):
        is_seller_and_owner = request.user and request.user.role.name == 'seller' and obj.seller == request.user  # Проверка, является ли пользователь продавцом и владельцем объекта.
        is_manager = request.user and request.user.role.name == 'manager'  # Проверка, является ли пользователь менеджером.
        return is_seller_and_owner or is_manager  # Доступ разрешен, если пользователь - продавец и владелец или менеджер.