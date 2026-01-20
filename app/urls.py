from django.urls import path
from .views import ingest_view,extract_details, ask_question, audit, ask_stream, get_metrics



urlpatterns = [
    path("ingest/", ingest_view),
    path("extract/<int:pk>", extract_details),
    path("ask/", ask_question),
    path("audit/", audit),
    path("que/stream/", ask_stream),
    path("metrics/", get_metrics),
]
