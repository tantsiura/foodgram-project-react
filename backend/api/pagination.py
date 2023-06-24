from django.conf import settings
from django.core import paginator
from rest_framework.pagination import PageNumberPagination


class UserPagination(PageNumberPagination):
    """Class for displaying pagination."""
    django_paginator_class = paginator.Paginator
    page_size_query_param = 'limit'
    page_size = settings.PAGE_SIZE
