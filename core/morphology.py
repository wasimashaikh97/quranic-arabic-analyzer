"""Morphological classification of Arabic roots and verbs.

Classification only — no form is generated here.  ``core.conjugation`` does the
inflecting and ``core.abwaab`` holds the باب definitions.
"""

import re

from .arabic_utils import (
    strip_marks, strip_vowels, normalise_letters,
    split_units, SHADDA,
    ARABIC_LETTERS, HAMZA_FORMS, WEAK_LETTERS,
)
from . import abwaab


class ArabicMorphology:
    """فعل اور مادہ کی اقسام کی شناخت — verb & root type identification."""

    ARABIC_LETTERS = ARABIC_LETTERS
    HAMZA_FORMS = HAMZA_FORMS
    WEAK_LETTERS = WEAK_LETTERS
    DIACRITICS = set('ًٌٍَُِّْٰٓ')

    # Kept for backward compatibility; the authoritative باب data now lives
    # in core.abwaab.BAAB_INFO.
    VERB_FORMS = {
        f: {
            'past': info['wazn_past'],
            'present': info['wazn_present'],
            'past_passive': info['wazn_past_passive'],
            'present_passive': info['wazn_present_passive'],
            'masdar_patterns': [info['masdar_pattern']],
            'name_arabic': info['name_ar'],
            'meaning_en': info['name_en'],
            'meaning_ur': info['name_ur'],
        }
        for f, info in abwaab.BAAB_INFO.items()
    }

    VERB_TYPES = {
        'sound': {
            'title_ar': 'صحيح سالم',
            'title_ur': 'صحیح سالم',
            'title_en': 'Sound Verb',
            'desc_ur': 'اس فعل کے مادہ میں کوئی حرفِ علت (ا، و، ی) نہیں، کوئی ہمزہ نہیں، '
                       'اور کوئی حرف دو بار نہیں آیا۔ اس لیے اس کی گردان بالکل سیدھی ہے۔',
            'desc_en': 'A regular verb: no weak letter, no hamza, no doubled radical, so '
                       'its conjugation follows the plain pattern.',
            'example': 'كَتَبَ',
        },
        'hollow': {
            'title_ar': 'أجوف',
            'title_ur': 'اجوف (درمیان میں حرفِ علت)',
            'title_en': 'Hollow Verb',
            'desc_ur': 'مادہ کا درمیانی حرف حرفِ علت (و یا ی) ہے۔ ماضی میں جب ضمیر کا حرف '
                       'ساکن ہو تو یہ حرف گر جاتا ہے: قَالَ ← قُلْتُ۔',
            'desc_en': 'The middle radical is weak (و or ی). It drops before a consonantal '
                       'ending: قَالَ → قُلْتُ.',
            'example': 'قَالَ',
        },
        'defective': {
            'title_ar': 'ناقص',
            'title_ur': 'ناقص (آخر میں حرفِ علت)',
            'title_en': 'Defective Verb',
            'desc_ur': 'مادہ کا آخری حرف حرفِ علت (و یا ی) ہے، اس لیے آخر میں تبدیلی آتی ہے: '
                       'دَعَا ← دَعَوْتُ، رَمَى ← رَمَيْتُ۔',
            'desc_en': 'The final radical is weak (و or ی), so the ending shifts: '
                       'دَعَا → دَعَوْتُ, رَمَى → رَمَيْتُ.',
            'example': 'دَعَا',
        },
        'doubled': {
            'title_ar': 'مضاعف',
            'title_ur': 'مضاعف (ایک حرف دو بار)',
            'title_en': 'Doubled Verb',
            'desc_ur': 'مادہ کا دوسرا اور تیسرا حرف ایک ہی ہے، اس لیے تشدید آ جاتی ہے: '
                       'رَدَّ ← رَدَدْتُ۔',
            'desc_en': 'The second and third radicals are identical, producing a shadda: '
                       'رَدَّ → رَدَدْتُ.',
            'example': 'رَدَّ',
        },
        'hamzated': {
            'title_ar': 'مهموز',
            'title_ur': 'مہموز (ہمزہ والا)',
            'title_en': 'Hamzated Verb',
            'desc_ur': 'مادہ کے حروف میں ہمزہ (أ، ؤ، ئ) شامل ہے، جیسے أَكَلَ، سَأَلَ، قَرَأَ۔ '
                       'ہمزہ کی نشست (کرسی) حرکت کے مطابق بدلتی ہے۔',
            'desc_en': 'The root contains a hamza (أ، ؤ، ئ) — أَكَلَ، سَأَلَ، قَرَأَ. The seat '
                       'of the hamza changes with the surrounding vowels.',
            'example': 'أَكَلَ',
        },
        'assimilated': {
            'title_ar': 'مثال',
            'title_ur': 'مثال (شروع میں حرفِ علت)',
            'title_en': 'Assimilated Verb',
            'desc_ur': 'مادہ کا پہلا حرف حرفِ علت (عموماً و) ہے، جو مضارع میں گر جاتا ہے: '
                       'وَعَدَ ← يَعِدُ۔',
            'desc_en': 'The first radical is weak (usually و) and drops in the مضارع: '
                       'وَعَدَ → يَعِدُ.',
            'example': 'وَعَدَ',
        },
        'lafeef': {
            'title_ar': 'لفيف',
            'title_ur': 'لفیف (دو حروفِ علت)',
            'title_en': 'Doubly-Weak Verb',
            'desc_ur': 'مادہ میں دو حروفِ علت ہیں، جیسے وَفَى، وَقَى، رَوَى۔ اس میں مثال اور '
                       'ناقص دونوں کے قاعدے جمع ہو جاتے ہیں۔',
            'desc_en': 'The root has two weak letters — وَفَى، وَقَى، رَوَى — so the rules of '
                       'both the assimilated and the defective verb apply together.',
            'example': 'وَقَى',
        },
    }

    # ------------------------------------------------------------------
    @staticmethod
    def strip_diacritics(text: str) -> str:
        """Remove every diacritic (kept for backward compatibility)."""
        return strip_marks(text)

    @staticmethod
    def strip_harakat_keep_shadda(text: str) -> str:
        return strip_vowels(text)

    # ------------------------------------------------------------------
    @staticmethod
    def identify_verb_type(root_letters) -> str:
        """Classify a *root* (list of three letters)."""
        if not root_letters or len(root_letters) < 3:
            return 'sound'

        r1, r2, r3 = root_letters[0], root_letters[1], root_letters[2]
        weak_count = sum(1 for l in root_letters if l in WEAK_LETTERS)

        if weak_count >= 2:
            return 'lafeef'
        if r2 == r3 and r2 not in WEAK_LETTERS:
            return 'doubled'
        if r1 in WEAK_LETTERS:
            return 'assimilated'
        if r2 in WEAK_LETTERS:
            return 'hollow'
        if r3 in WEAK_LETTERS:
            return 'defective'
        if any(l in HAMZA_FORMS for l in root_letters):
            return 'hamzated'
        return 'sound'

    @staticmethod
    def lafeef_subtype(root_letters) -> str:
        """مفروق (weak letters apart) vs مقرون (weak letters adjacent)."""
        if not root_letters or len(root_letters) < 3:
            return ''
        r1, r2, r3 = root_letters[0], root_letters[1], root_letters[2]
        if r1 in WEAK_LETTERS and r3 in WEAK_LETTERS:
            return 'مفروق'
        if r2 in WEAK_LETTERS and r3 in WEAK_LETTERS:
            return 'مقرون'
        return ''

    @staticmethod
    def get_verb_type_info(verb_type: str) -> dict:
        return ArabicMorphology.VERB_TYPES.get(
            verb_type, ArabicMorphology.VERB_TYPES['sound'])

    @staticmethod
    def get_form_info(form_number) -> dict:
        return ArabicMorphology.VERB_FORMS.get(
            int(form_number) if str(form_number).isdigit() else 1,
            ArabicMorphology.VERB_FORMS[1])

    @staticmethod
    def get_baab_info(form_number) -> dict:
        return abwaab.get_baab(form_number)

    # ------------------------------------------------------------------
    #: affixes stripped when guessing a root from an unknown word
    _PREFIXES = ['است', 'انت', 'ان', 'افت', 'مست', 'مت', 'يست', 'تست',
                 'يت', 'تت', 'نت', 'أت', 'ي', 'ت', 'ن', 'أ', 'ا', 'م', 'س']
    _SUFFIXES = ['تموا', 'تمو', 'تما', 'تمن', 'ونا', 'ينا', 'تنّ', 'ون', 'ين',
                 'ان', 'وا', 'تم', 'تن', 'نا', 'ات', 'ة', 'ت', 'ا', 'ن',
                 'و', 'ي', 'ى']

    @staticmethod
    def extract_root_letters(word: str) -> list:
        """Best-effort root guess from an arbitrary word.

        Only ever used as a *search hint*: a guessed root is looked up in the
        verified lexicon, and if nothing matches the application says so
        instead of conjugating the guess.
        """
        bare = normalise_letters(strip_marks(word or ''))
        letters = [c for c in bare if c in ARABIC_LETTERS]
        if len(letters) == 3:
            return letters

        stem = ''.join(letters)
        changed = True
        while changed and len(stem) > 3:
            changed = False
            for p in ArabicMorphology._PREFIXES:
                if stem.startswith(p) and len(stem) - len(p) >= 3:
                    stem = stem[len(p):]
                    changed = True
                    break
            if len(stem) <= 3:
                break
            for s in ArabicMorphology._SUFFIXES:
                if stem.endswith(s) and len(stem) - len(s) >= 3:
                    stem = stem[:-len(s)]
                    changed = True
                    break
        return list(stem[:3]) if len(stem) >= 3 else list(stem)

    @staticmethod
    def has_shadda(text: str) -> bool:
        return any(SHADDA in marks for _l, marks in split_units(text or ''))

    @staticmethod
    def detect_baab(past_3ms: str, root_letters=None) -> int:
        return abwaab.detect_baab(past_3ms, root_letters)
