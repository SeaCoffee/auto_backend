import os.path
import uuid


def upload_avatar(instance, filename):
    extension = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{extension}"
    return os.path.join('storage', 'media', 'avatars', instance.user.username, filename)

def upload_photo_listing(instance, filename):
    extension = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{extension}"
    return os.path.join('storage', 'media', 'upload_photo_listing', filename)

