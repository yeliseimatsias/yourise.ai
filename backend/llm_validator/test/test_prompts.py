"""
Тесты для промптов.
"""

import pytest
from llm_validator.prompts.base_prompt import BasePrompt
from llm_validator.prompts.modified_prompt import ModifiedPrompt
from llm_validator.prompts.added_prompt import AddedPrompt
from llm_validator.prompts.deleted_prompt import DeletedPrompt


class TestBasePrompt:
    """Тесты базового промпта."""
    
    def test_system_message_exists(self):
        """Тест наличия системного сообщения."""
        assert BasePrompt.SYSTEM_MESSAGE
        assert "JSON" in BasePrompt.SYSTEM_MESSAGE
    
    def test_few_shot_examples(self):
        """Тест получения few-shot примеров."""
        examples = BasePrompt.get_few_shot_examples()
        
        assert "Пример" in examples
        assert "direct" in examples
        assert "indirect" in examples
        assert "none" in examples
    
    def test_format_change_type(self):
        """Тест форматирования типов изменений."""
        assert BasePrompt.format_change_type('added') == 'ДОБАВЛЕНИЕ НОВОГО ТЕКСТА'
        assert BasePrompt.format_change_type('deleted') == 'УДАЛЕНИЕ ТЕКСТА'
        assert BasePrompt.format_change_type('modified') == 'ИЗМЕНЕНИЕ ТЕКСТА'
        assert BasePrompt.format_change_type('unknown') == 'UNKNOWN'


class TestModifiedPrompt:
    """Тесты промпта для изменений."""
    
    @pytest.fixture
    def change_data(self):
        return {
            'change_id': 'test-123',
            'type': 'modified',
            'element_number': '5.3',
            'old_text': 'Старый текст',
            'new_text': 'Новый текст',
            'full_chunk': 'Полный контекст',
            'document_type': 'local_act',
            'document_level': 7
        }
    
    @pytest.fixture
    def law_data(self):
        return {
            'law_reference': 'ТК РБ, ст.155',
            'chunk_text': 'Текст закона',
            'similarity': 0.89,
            'hierarchy_level': 2
        }
    
    def test_build_prompt(self, change_data, law_data):
        """Тест построения промпта."""
        prompt = ModifiedPrompt.build(change_data, law_data)
        
        assert 'ИЗМЕНЕНИЕ ТЕКСТА' in prompt
        assert 'Старый текст' in prompt
        assert 'Новый текст' in prompt
        assert 'ТК РБ, ст.155' in prompt
        assert 'Текст закона' in prompt
        assert 'НОВАЯ редакция' in prompt
    
    def test_prompt_contains_system_message(self, change_data, law_data):
        """Тест наличия системного сообщения в промпте."""
        prompt = ModifiedPrompt.build(change_data, law_data)
        
        assert BasePrompt.SYSTEM_MESSAGE in prompt
    
    def test_prompt_contains_examples(self, change_data, law_data):
        """Тест наличия примеров в промпте."""
        prompt = ModifiedPrompt.build(change_data, law_data)
        
        assert 'Пример' in prompt


class TestAddedPrompt:
    """Тесты промпта для добавлений."""
    
    @pytest.fixture
    def change_data(self):
        return {
            'change_id': 'test-123',
            'type': 'added',
            'element_number': '5.4',
            'new_text': 'Добавленный текст',
            'full_chunk': 'Контекст с добавлением',
            'document_type': 'local_act'
        }
    
    @pytest.fixture
    def law_data(self):
        return {
            'law_reference': 'ТК РБ, ст.160',
            'chunk_text': 'Текст статьи',
            'similarity': 0.75,
            'hierarchy_level': 2
        }
    
    def test_build_prompt(self, change_data, law_data):
        """Тест построения промпта для добавления."""
        prompt = AddedPrompt.build(change_data, law_data)
        
        assert 'ДОБАВЛЕНИЕ НОВОГО ТЕКСТА' in prompt
        assert 'Добавленный текст' in prompt
        assert 'ДОБАВЛЕННЫЙ текст' in prompt
    
    def test_prompt_contains_criteria(self, change_data, law_data):
        """Тест наличия критериев проверки."""
        prompt = AddedPrompt.build(change_data, law_data)
        
        assert 'КРИТЕРИИ ПРОВЕРКИ' in prompt


class TestDeletedPrompt:
    """Тесты промпта для удалений."""
    
    @pytest.fixture
    def change_data(self):
        return {
            'change_id': 'test-123',
            'type': 'deleted',
            'element_number': '5.2',
            'old_text': 'Удаляемый текст',
            'full_chunk': 'Контекст удаления',
            'document_type': 'local_act'
        }
    
    @pytest.fixture
    def law_data(self):
        return {
            'law_reference': 'ТК РБ, ст.150',
            'chunk_text': 'Текст статьи',
            'similarity': 0.80,
            'hierarchy_level': 2
        }
    
    def test_build_prompt(self, change_data, law_data):
        """Тест построения промпта для удаления."""
        prompt = DeletedPrompt.build(change_data, law_data)
        
        assert 'УДАЛЕНИЕ ТЕКСТА' in prompt
        assert 'Удаляемый текст' in prompt
        assert 'УДАЛЕНИЕ этого текста' in prompt
    
    def test_prompt_contains_deletion_criteria(self, change_data, law_data):
        """Тест наличия критериев для проверки удаления."""
        prompt = DeletedPrompt.build(change_data, law_data)
        
        assert 'ОБЯЗАТЕЛЬНОГО наличия' in prompt
        assert 'пробел в правовом регулировании' in prompt


class TestPromptIntegration:
    """Интеграционные тесты промптов."""
    
    def test_all_prompts_have_same_structure(self):
        """Тест что все промпты имеют схожую структуру."""
        change_data = {
            'change_id': 'test',
            'type': 'modified',
            'old_text': 'old',
            'new_text': 'new',
            'full_chunk': 'chunk'
        }
        law_data = {
            'law_reference': 'Закон',
            'chunk_text': 'Текст'
        }
        
        modified = ModifiedPrompt.build(change_data, law_data)
        added = AddedPrompt.build(change_data, law_data)
        deleted = DeletedPrompt.build(change_data, law_data)
        
        # Все должны содержать системное сообщение
        assert BasePrompt.SYSTEM_MESSAGE in modified
        assert BasePrompt.SYSTEM_MESSAGE in added
        assert BasePrompt.SYSTEM_MESSAGE in deleted
        
        # Все должны содержать примеры
        assert 'Пример' in modified
        assert 'Пример' in added
        assert 'Пример' in deleted
        
        # Все должны требовать JSON
        assert 'JSON' in modified
        assert 'JSON' in added
        assert 'JSON' in deleted