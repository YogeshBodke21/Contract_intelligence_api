from django.db import models

# Create your models here.

class Document(models.Model):
    file = models.FileField(upload_to="documents/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    text_content = models.TextField(blank=True, null=True)

class Contract_fields(models.Model):
    document = models.OneToOneField(Document, on_delete=models.CASCADE, related_name="fields")
    parties = models.JSONField(default=list)
    effective_date = models.DateField(null=True, blank=True)
    term = models.CharField(max_length=255, blank=True)
    governing_law = models.CharField(max_length=255, blank=True)
    payment_terms = models.TextField(blank=True)
    termination = models.TextField(blank=True)
    auto_renewal = models.BooleanField(default=False)
    confidentiality = models.TextField(blank=True)
    indemnity = models.TextField(blank=True)
    liability_cap = models.JSONField(default=dict)  # {"amount": 1000, "currency": "USD"}
    signatories = models.JSONField(default=list)  # [{"name": "", "title": ""}]
