import math

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class PagePagination(PageNumberPagination):
    """
    Кастомная пагинация для API. Управляет размером страниц и количеством элементов на странице.
    """
    page_size = 25  # Размер страницы по умолчанию.
    max_page_size = 10  # Максимальный размер страницы.
    page_size_query_param = 'size'  # Параметр запроса для управления размером страницы.

    def get_paginated_response(self, data):
        """
        Возвращает кастомный ответ с метаданными о пагинации.
        :param data: Данные для текущей страницы.
        :return: Ответ с информацией о пагинации и данных.
        """
        count = self.page.paginator.count  # Общее количество элементов.
        total_pages = math.ceil(count / self.get_page_size(self.request))  # Общее количество страниц.
        return Response({
            'total_items': count,
            'total_pages': total_pages,
            'prev': bool(self.get_previous_link()),  # Есть ли предыдущая страница.
            'next': bool(self.get_next_link()),  # Есть ли следующая страница.
            'data': data  # Данные для текущей страницы.
        })
