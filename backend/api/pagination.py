from rest_framework.pagination import PageNumberPagination


class LimitPageNumberPagination(PageNumberPagination):
    """Limit on displaying posts per page."""
    page_size = 6
    page_size_query_param = 'limit'
