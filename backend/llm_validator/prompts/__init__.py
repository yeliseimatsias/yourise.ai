"""Промпты для различных типов проверок."""

from .base_prompt import BasePrompt
from .modified_prompt import ModifiedPrompt
from .added_prompt import AddedPrompt
from .deleted_prompt import DeletedPrompt

__all__ = ["BasePrompt", "ModifiedPrompt", "AddedPrompt", "DeletedPrompt"]
