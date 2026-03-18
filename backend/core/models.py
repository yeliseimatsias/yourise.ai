# core/models.py
from django.db import models
import uuid

class Session(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default='pending')
    progress = models.IntegerField(default=0)
    changes_total = models.IntegerField(default=0)
    changes_processed = models.IntegerField(default=0)
    error_message = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'sessions'
        managed = False
    
    def __str__(self):
        return f"Session {self.id} ({self.status})"


class Document(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(Session, on_delete=models.CASCADE, db_column='session_id')
    filename = models.CharField(max_length=512)
    file_path = models.CharField(max_length=1024)
    document_type = models.CharField(max_length=10)  # 'old' или 'new'
    parsed_json = models.JSONField(null=True, blank=True)
    page_count = models.IntegerField(null=True, blank=True)
    word_count = models.IntegerField(null=True, blank=True)
    
    class Meta:
        db_table = 'documents'
        managed = False
    
    def __str__(self):
        return f"{self.filename} ({self.document_type})"


class Change(models.Model):  # ← ЭТОГО КЛАССА НЕ ХВАТАЕТ!
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(Session, on_delete=models.CASCADE, db_column='session_id')
    element_number = models.CharField(max_length=100)
    change_type = models.CharField(max_length=20)  # 'added', 'deleted', 'modified'
    old_text = models.TextField(blank=True, null=True)
    new_text = models.TextField(blank=True, null=True)
    semantic_type = models.CharField(max_length=50, blank=True, null=True)
    risk_level = models.CharField(max_length=10, default='green')  # 'red', 'yellow', 'green'
    diff_json = models.JSONField(null=True, blank=True)
    processing_status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'changes'
        managed = False
    
    def __str__(self):
        return f"Change {self.element_number} ({self.risk_level})"


class ValidationResult(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    change = models.ForeignKey(Change, on_delete=models.CASCADE, db_column='change_id')
    law_reference = models.CharField(max_length=255)
    law_text = models.TextField()
    explanation = models.TextField()
    confidence = models.FloatField(default=0.95)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'validation_results'
        managed = False
    
    def __str__(self):
        return f"Validation for {self.change_id}"


class Report(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(Session, on_delete=models.CASCADE, db_column='session_id')
    report_format = models.CharField(max_length=10)  # 'json', 'docx'
    report_path = models.CharField(max_length=1024, blank=True, null=True)
    summary = models.JSONField(null=True, blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'reports'
        managed = False
    
    def __str__(self):
        return f"Report for session {self.session_id} ({self.report_format})"