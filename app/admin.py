from django.contrib import admin
from .models import Document, DocumentChunk, Contract_fields

admin.site.register(Document)
admin.site.register(DocumentChunk)
admin.site.register(Contract_fields)

