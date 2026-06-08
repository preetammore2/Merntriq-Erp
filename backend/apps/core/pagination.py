from django.conf import settings
from rest_framework.pagination import PageNumberPagination


class OptionalPageNumberPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = "page_size"
    max_page_size = 200

    def paginate_queryset(self, queryset, request, view=None):
        self.page_size = getattr(settings, "REST_FRAMEWORK", {}).get("PAGE_SIZE", self.page_size)
        self.max_page_size = getattr(settings, "MAX_PAGE_SIZE", self.max_page_size)
        if not (
            request.query_params.get(self.page_query_param)
            or request.query_params.get(self.page_size_query_param)
            or request.query_params.get("paginate") == "true"
        ):
            return None
        return super().paginate_queryset(queryset, request, view)
