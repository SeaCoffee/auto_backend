import os.path
import uuid

def upload_avatar(instance, filename):
    """
    Функция для генерации пути для загрузки аватара пользователя.
    Используется UUID для генерации уникального имени файла, что предотвращает конфликты имен.
    :param instance: Экземпляр модели, для которой загружается файл
    :param filename: Оригинальное имя загружаемого файла
    :return: Сгенерированный путь для сохранения файла
    """
    extension = filename.split('.')[-1]  # Получаем расширение файла
    filename = f"{uuid.uuid4()}.{extension}"  # Генерируем уникальное имя файла
    return os.path.join('avatars', instance.user.username, filename)  # Возвращаем путь для сохранения файла


def upload_photo_listing(instance, filename):
    """
    Функция для генерации пути для загрузки фотографий объявлений.
    Используется UUID для генерации уникального имени файла.
    :param instance: Экземпляр модели, для которой загружается файл
    :param filename: Оригинальное имя загружаемого файла
    :return: Сгенерированный путь для сохранения файла
    """
    extension = filename.split('.')[-1]  # Получаем расширение файла
    filename = f"{uuid.uuid4()}.{extension}"  # Генерируем уникальное имя файла
    return os.path.join('upload_photo_listing', filename)  # Возвращаем путь для сохранения файла