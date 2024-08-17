import os.path
import uuid


def upload_avatar(instance, filename):
    extension = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{extension}"
    return os.path.join('avatars', instance.user.username, filename)
def upload_photo_listing(instance, filename):
    extension = filename.split('.')[-1]
    seller_name = instance.seller.username
    return os.path.join('photo_listings', seller_name, f'{uuid.uuid4()}.{extension}')