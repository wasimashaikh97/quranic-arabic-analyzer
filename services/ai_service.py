import os
import requests
from typing import Optional

class AIService:
    """Optional AI integration for enhanced explanations.
    
    Supports: OpenAI, Claude, Gemini (via environment variables).
    If no API key is configured, provides offline fallback explanations.
    """
    
    def __init__(self):
        self.api_key = os.environ.get('OPENAI_API_KEY', '')
        self.provider = self._detect_provider()
        self.available = bool(self.api_key or os.environ.get('ANTHROPIC_API_KEY') or os.environ.get('GOOGLE_API_KEY'))
    
    def _detect_provider(self) -> str:
        """Detect which AI provider is configured."""
        if os.environ.get('OPENAI_API_KEY'):
            return 'openai'
        if os.environ.get('ANTHROPIC_API_KEY'):
            return 'anthropic'
        if os.environ.get('GOOGLE_API_KEY'):
            return 'google'
        return 'offline'
    
    def get_explanation(self, verb_data: dict, language: str = 'en') -> str:
        """Get AI-generated explanation of a verb. Falls back to template if no AI."""
        if not self.available:
            return self._offline_explanation(verb_data, language)
            
        # Simplified simulation of AI requests for illustration.
        if self.provider == 'openai':
            # Would call OpenAI API via requests here
            pass
            
        return self._offline_explanation(verb_data, language)
    
    def get_grammar_tip(self, verb_data: dict, conjugation_info: dict, language: str = 'en') -> str:
        """Get a grammar tip. Falls back to template."""
        if not self.available:
            return self._offline_grammar_tip(verb_data, conjugation_info, language)
        return self._offline_grammar_tip(verb_data, conjugation_info, language)
    
    def generate_practice_question(self, verb_data: dict, question_type: str) -> dict:
        """Generate a practice question. Falls back to template-based generation."""
        if not self.available:
            return {
                "question": f"What is the past tense of {verb_data.get('arabic', 'the verb')}?",
                "options": ["Option A", "Option B", "Option C"],
                "answer": "Option A"
            }
        return {
                "question": f"What is the past tense of {verb_data.get('arabic', 'the verb')}?",
                "options": ["Option A", "Option B", "Option C"],
                "answer": "Option A"
        }
    
    def _offline_explanation(self, verb_data: dict, language: str) -> str:
        """Generate explanation without AI."""
        verb = verb_data.get('arabic', '')
        meaning = verb_data.get('meaning_en', '') if language == 'en' else verb_data.get('meaning_ur', '')
        
        if language == 'ur':
            return f"یہ فعل '{verb}' ہے، جس کا معنی '{meaning}' ہے۔"
        return f"The verb '{verb}' means '{meaning}'."
    
    def _offline_grammar_tip(self, verb_data: dict, conjugation_info: dict, language: str) -> str:
        """Generate grammar tip without AI."""
        if language == 'ur':
            return "گرامر کا مشورہ: فعل کے باب اور وزن پر توجہ دیں۔"
        return "Grammar tip: Pay attention to the form and pattern of the verb."
    
    def is_available(self) -> bool:
        """Check if AI service is available."""
        return self.available
