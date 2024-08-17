from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAuthenticatedOrReadOnly(BasePermission):
    """
    Разрешает чтение для всех, изменение только аутентифицированным пользователям.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated)

class IsSeller(BasePermission):
    """
    Позволяет доступ только зарегистрированным продавцам.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role.name == 'seller')

class IsBuyer(BasePermission):
    """
    Позволяет доступ только покупателям.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role.name == 'buyer')


class IsPremiumAccount(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.account_type == 'premium'
        )


class IsPremiumSeller(BasePermission):
    """
    Позволяет доступ только продавцам с премиум-аккаунтом.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role.name == 'seller' and
            request.user.account_type == 'premium'
        )

class IsManager(BasePermission):
    """
    Позволяет доступ только менеджерам.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff and request.user.role.name == 'manager')



class IsAdmin(BasePermission):
    """
    Позволяет доступ только super user
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff and request.user.is_superuser)

class IsSellerOrManagerAndOwner(BasePermission):
    """
    Позволяет доступ либо продавцу-создателю объявления, либо менеджеру.
    """
    def has_object_permission(self, request, view, obj):
        # Проверка, что пользователь либо владелец объявления (продавец), либо менеджер
        is_seller_and_owner = request.user and request.user.role.name == 'seller' and obj.seller == request.user
        is_manager = request.user and request.user.role.name == 'manager'
        return is_seller_and_owner or is_manager