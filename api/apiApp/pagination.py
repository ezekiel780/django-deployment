from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from collections import OrderedDict


class CustomPagination(PageNumberPagination):
    """
    Custom pagination class with enhanced metadata and flexible page sizing.
    
    Features:
    - Customizable page size via query parameter
    - Rich metadata including page info and numbered links
    - Support for page number navigation
    
    Query Parameters:
    - page: Page number (default: 1)
    - page_size: Number of items per page (default: 10, max: 100)
    
    Example:
    - /api/products/?page=2
    - /api/products/?page=1&page_size=20
    """
    
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_query_param = 'page'
    
    def get_paginated_response(self, data):
        """
        Returns enhanced paginated response with comprehensive metadata.
        
        Args:
            data (list): Serialized data for the current page
            
        Returns:
            Response: Paginated response with links, count, and page info
        """
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('page_size', self.get_page_size(self.request)),
            ('current_page', self.page.number),
            ('total_pages', self.page.paginator.num_pages),
            ('links', OrderedDict([
                ('next', self.get_next_link()),
                ('previous', self.get_previous_link()),
                ('first', self.get_first_link()),
                ('last', self.get_last_link()),
                ('numbered', list(self.get_numbered_links())),
            ])),
            ('results', data),
        ]))
    
    def get_numbered_links(self):
        """
        Returns a range of page numbers for pagination navigation.
        Shows up to 9 pages centered around the current page.
        
        Returns:
            range: Page numbers for navigation (e.g., [1, 2, 3, 4, 5])
        """
        if not self.page.paginator.num_pages:
            return []
        
        current_page = self.page.number
        total_pages = self.page.paginator.num_pages
        
        # Show max 9 pages (4 before + current + 4 after)
        start_page = max(current_page - 4, 1)
        end_page = min(current_page + 4, total_pages)
        
        # Adjust if we're near the beginning or end
        if current_page <= 5:
            end_page = min(9, total_pages)
        elif current_page >= total_pages - 4:
            start_page = max(total_pages - 8, 1)
        
        return range(start_page, end_page + 1)
    
    def get_first_link(self):
        """Returns the URL for the first page."""
        if not self.page.has_previous():
            return None
        url = self.request.build_absolute_uri()
        return self.replace_query_param(url, self.page_query_param, 1)
    
    def get_last_link(self):
        """Returns the URL for the last page."""
        if not self.page.has_next():
            return None
        url = self.request.build_absolute_uri()
        last_page = self.page.paginator.num_pages
        return self.replace_query_param(url, self.page_query_param, last_page)
    
    def replace_query_param(self, url, key, val):
        """Helper method to replace query parameters in URL."""
        from rest_framework.utils.urls import replace_query_param
        return replace_query_param(url, key, val)


class SmallResultsSetPagination(PageNumberPagination):
    """
    Pagination for smaller datasets (5 items per page).
    Useful for featured products, recent items, etc.
    """
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 20


class LargeResultsSetPagination(PageNumberPagination):
    """
    Pagination for larger datasets (50 items per page).
    Useful for admin views, bulk operations, etc.
    """
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200


class NoPagination(PageNumberPagination):
    """
    Pagination class that returns all results.
    Use sparingly - only for small datasets!
    """
    page_size = None
    
    def paginate_queryset(self, queryset, request, view=None):
        """Returns None to disable pagination."""
        return None

        