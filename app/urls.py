from .views import ingest_view,extract_details, ask_question
from django.urls import path


urlpatterns = [
    path("ingest/", ingest_view),
    path("extract/<int:pk>", extract_details),
    path("ask/", ask_question),
]
