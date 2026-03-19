# core/views.py
import os
import json
import uuid
import logging
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

# Импорты без префикса backend.
from parsers.factory import ParserFactory
from semantic_differ.analyzer import DocumentDiffer
from llm_validator.core import LLMValidatorPipeline
from llm_validator.config import Config
from llm_validator.report import ReportGenerator

logger = logging.getLogger(__name__)


@api_view(['POST'])
def compare_documents_alt(request):
    """
    Альтернативная версия (если хотите использовать её вместо api/views.py)
    """
    # Здесь можно разместить аналогичный код, но импорты уже правильные.
    # Однако, если вы используете api/views.py, этот файл не нужен.
    pass