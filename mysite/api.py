from wagtail.api.v2.views import PagesAPIViewSet  # Import PagesAPIViewSet
from wagtail.api.v2.router import WagtailAPIRouter
from wagtail.images.api.v2.views import ImagesAPIViewSet  # Correct import for ImagesAPIViewSet
from wagtail.documents.api.v2.views import DocumentsAPIViewSet  # Correct import for DocumentsAPIViewSet

api_router = WagtailAPIRouter('wagtailapi')

api_router.register_endpoint('pages', PagesAPIViewSet)
api_router.register_endpoint('images', ImagesAPIViewSet)
api_router.register_endpoint('documents', DocumentsAPIViewSet)
