"""Input validation with friendly, non-technical messages."""

import re

from .arabic_utils import (
    ARABIC_LETTERS, ALL_MARKS, normalise_letters, strip_marks,
)

#: every message the user can be shown, in all three interface languages
MESSAGES = {
    'empty': {
        'ur': 'براہ کرم عربی لفظ درج کریں۔',
        'en': 'Please enter an Arabic word.',
        'ar': 'الرجاء إدخال كلمة عربية.',
    },
    'not_arabic': {
        'ur': 'براہ کرم عربی حروف میں لفظ لکھیں۔',
        'en': 'Please enter an Arabic word.',
        'ar': 'الرجاء الكتابة بالحروف العربية.',
    },
    'too_short': {
        'ur': 'براہ کرم مکمل عربی فعل لکھیں (کم از کم تین حروف)۔',
        'en': 'Please enter a complete Arabic verb (at least three letters).',
        'ar': 'الرجاء إدخال فعل عربي كامل (ثلاثة أحرف على الأقل).',
    },
    'not_found': {
        'ur': 'اس لفظ کی مستند صرفی معلومات دستیاب نہیں۔',
        'en': 'No verified morphological data is available for this word.',
        'ar': 'لا تتوفر معلومات صرفية موثوقة لهذه الكلمة.',
    },
    'not_applicable': {
        'ur': 'قابلِ اطلاق نہیں',
        'en': 'Not applicable',
        'ar': 'غير منطبق',
    },
}


def message(key: str, lang: str = 'ur') -> str:
    entry = MESSAGES.get(key, MESSAGES['not_found'])
    return entry.get(lang, entry['ur'])


class InputValidator:
    """Validate what the student typed into the single search box."""

    ARABIC_PATTERN = re.compile(r'[؀-ۿݐ-ݿﭐ-﷿ﹰ-﻿]')
    #: letters that occur in Urdu but not in Arabic
    URDU_SPECIFIC = set('ٹڈڑژںھےۓپچگکہ')
    LATIN = re.compile(r'[A-Za-z]')

    @staticmethod
    def is_arabic(text: str) -> bool:
        return bool(InputValidator.ARABIC_PATTERN.search(text or ''))

    @staticmethod
    def is_urdu(text: str) -> bool:
        return any(c in InputValidator.URDU_SPECIFIC for c in (text or ''))

    @staticmethod
    def is_english(text: str) -> bool:
        text = text or ''
        return bool(InputValidator.LATIN.search(text)) and not \
            InputValidator.is_arabic(text)

    @staticmethod
    def is_root_format(text: str) -> bool:
        """True for input like «ن ز ل» — three single letters, space separated."""
        parts = (text or '').split()
        return (len(parts) == 3
                and all(len(strip_marks(p)) == 1 and InputValidator.is_arabic(p)
                        for p in parts))

    @staticmethod
    def validate_input(text: str) -> dict:
        """Return ``{valid, input_type, cleaned, error_key}``."""
        if not text or not text.strip():
            return {'valid': False, 'input_type': 'empty', 'cleaned': '',
                    'error_key': 'empty', 'error': message('empty', 'en')}

        cleaned = InputValidator.clean(text)

        if InputValidator.is_english(cleaned):
            # An English word is still a legitimate search key for the meaning
            # index, so it is accepted — the analyzer decides what to do.
            return {'valid': True, 'input_type': 'english', 'cleaned': cleaned,
                    'error_key': None, 'error': ''}

        if not InputValidator.is_arabic(cleaned):
            return {'valid': False, 'input_type': 'unknown', 'cleaned': cleaned,
                    'error_key': 'not_arabic',
                    'error': message('not_arabic', 'en')}

        if InputValidator.is_root_format(cleaned):
            return {'valid': True, 'input_type': 'root', 'cleaned': cleaned,
                    'error_key': None, 'error': ''}

        if InputValidator.is_urdu(cleaned):
            return {'valid': True, 'input_type': 'urdu', 'cleaned': cleaned,
                    'error_key': None, 'error': ''}

        # No length floor beyond "at least one letter": many correct answers
        # are very short — رَدَّ (shadda = a doubled letter), كُلْ، قُلْ، عِدْ،
        # and the امر of وَفَى is the single letter فِ.
        letters = [c for c in strip_marks(cleaned) if c in ARABIC_LETTERS]
        if not letters:
            return {'valid': False, 'input_type': 'arabic', 'cleaned': cleaned,
                    'error_key': 'too_short',
                    'error': message('too_short', 'en')}

        return {'valid': True, 'input_type': 'arabic', 'cleaned': cleaned,
                'error_key': None, 'error': ''}

    # ------------------------------------------------------------------
    @staticmethod
    def clean(text: str) -> str:
        """Trim and drop invisible characters — diacritics are preserved.

        Nothing is folded here: أَكَلَ must stay distinguishable from اكل and
        عَلَّمَ from عَلِمَ.  Folding happens only inside the search keys.
        """
        text = (text or '').strip()
        # tatweel and the zero-width joiners users often paste in
        for ch in ('ـ', '​', '‌', '‍', '‎', '‏'):
            text = text.replace(ch, '')
        return re.sub(r'\s+', ' ', text)

    # kept so older call-sites keep working
    @staticmethod
    def clean_arabic(text: str) -> str:
        return InputValidator.clean(text)

    @staticmethod
    def normalize_arabic(text: str) -> str:
        return normalise_letters(text)
