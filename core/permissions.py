from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAuthenticatedOrReadOnly(BasePermission):

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated)

class IsSeller(BasePermission):

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role.name == 'seller')

class IsBuyer(BasePermission):

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

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role.name == 'seller' and
            request.user.account_type == 'premium'
        )

class IsManager(BasePermission):

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff and request.user.role.name == 'manager')



class IsAdmin(BasePermission):

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff and request.user.is_superuser)

class IsSellerOrManagerAndOwner(BasePermission):

    def has_object_permission(self, request, view, obj):
        is_seller_and_owner = request.user and request.user.role.name == 'seller' and obj.seller == request.user
        is_manager = request.user and request.user.role.name == 'manager'
        return is_seller_and_owner or is_manager