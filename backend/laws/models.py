# laws/models.py
from django.db import models
import uuid

class Catalog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    law_reference = models.CharField(max_length=255, unique=True)
    law_name = models.CharField(max_length=500)
    hierarchy_level = models.IntegerField()
    source_url = models.CharField(max_length=500, blank=True)
    
    class Meta:
        db_table = 'catalog'
        managed = False

class Article(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    law = models.ForeignKey(Catalog, on_delete=models.CASCADE, db_column='law_id')
    article_number = models.CharField(max_length=50)
    article_title = models.CharField(max_length=500, blank=True, null=True)
    content = models.TextField()
    
    class Meta:
        db_table = 'articles'
        managed = False
        unique_together = ['law', 'article_number']

class Chunk(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, db_column='article_id')
    chunk_text = models.TextField()
    original_reference = models.CharField(max_length=255)
    
    class Meta:
        db_table = 'chunks'
        managed = False

class Embedding(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chunk = models.ForeignKey(Chunk, on_delete=models.CASCADE, db_column='chunk_id')
    # Для vector-поля нужно будет использовать RawSQL или кастомное поле
    embedding = models.BinaryField()  # временно, пока не настроишь pgvector
    model_name = models.CharField(max_length=100, default='multilingual-e5-large')
    
    class Meta:
        db_table = 'embeddings'
        managed = False