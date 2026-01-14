from .views import ingest_view,extract_details
from django.urls import path


urlpatterns = [
    path("ingest/", ingest_view),
    path("extract/<int:pk>", extract_details),
]
