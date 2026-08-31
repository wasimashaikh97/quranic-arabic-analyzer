"""Lookup over the verified verb lexicon.

Matching is layered so that precision comes first:

    1. fully diacritised match          أَنْزَلَ  ==  أَنْزَلَ
    2. shadda-aware, vowel-free match   انزل    ==  أَنْزَلَ
       (shadda is *kept*, so عَلَّمَ never collapses into عَلِمَ)
    3. loose match, hamza/alef/ya folded   انزل  ==  أَنْزَلَ
    4. substring match, as a last resort
"""

from .arabic_utils import key_exact, key_strict, key_loose, key_bare
from .morphology import ArabicMorphology
from .validation import InputValidator


class VerbSearch:
    def __init__(self, verbs: list, roots: list):
        self.verbs = verbs or []
        self.roots = roots or []
        self._reindex()

    def _reindex(self):
        self._exact = {}
        self._strict = {}
        self._loose = {}
        self._bare = {}
        for verb in self.verbs:
            ar = verb.get('arabic', '')
            self._exact.setdefault(key_exact(ar), []).append(verb)
            self._strict.setdefault(key_strict(ar), []).append(verb)
            self._loose.setdefault(key_loose(ar), []).append(verb)
            self._bare.setdefault(key_bare(ar), []).append(verb)

    # ------------------------------------------------------------------
    def search(self, query: str, search_type: str = 'auto') -> list:
        query = (query or '').strip()
        if not query:
            return []
        if search_type == 'auto':
            search_type = self.detect_search_type(query)
        return {
            'arabic': self.search_arabic,
            'root': self.search_root,
            'urdu': self.search_urdu,
            'english': self.search_english,
        }.get(search_type, self.search_arabic)(query)

    def detect_search_type(self, query: str) -> str:
        if InputValidator.is_english(query):
            return 'english'
        if InputValidator.is_root_format(query):
            return 'root'
        if InputValidator.is_urdu(query):
            return 'urdu'
        if InputValidator.is_arabic(query):
            return 'arabic'
        return 'english'

    # ------------------------------------------------------------------
    def search_exact(self, query: str) -> list:
        """Fully-diacritised match (insensitive only to mark ordering)."""
        return list(self._exact.get(key_exact(query), []))

    def search_arabic(self, query: str) -> list:
        """Ranked Arabic lookup; the first hit is the best hit."""
        query = query.strip()
        for table, key in ((self._exact, key_exact),
                           (self._strict, key_strict),
                           (self._loose, key_loose),
                           (self._bare, key_bare)):
            hits = table.get(key(query))
            if hits:
                return list(hits)

        # last resort: substring, shortest (most specific) candidate first
        needle = key_loose(query)
        if len(needle) >= 3:
            partial = [v for v in self.verbs
                       if needle in key_loose(v.get('arabic', ''))]
            partial.sort(key=lambda v: len(key_loose(v.get('arabic', ''))))
            return partial
        return []

    def match_quality(self, query: str, verb: dict) -> str:
        """'exact' | 'vowelless' | 'loose' | 'partial' — shown to the user."""
        ar = verb.get('arabic', '')
        q = query.strip()
        if key_exact(q) == key_exact(ar):
            return 'exact'
        if key_strict(q) == key_strict(ar):
            return 'vowelless'
        if key_loose(q) == key_loose(ar) or key_bare(q) == key_bare(ar):
            return 'loose'
        return 'partial'

    # ------------------------------------------------------------------
    def search_root(self, query: str) -> list:
        target = key_loose(query)
        return [v for v in self.verbs
                if key_loose(v.get('root', '')) == target]

    def search_urdu(self, query: str) -> list:
        q = query.strip()
        return [v for v in self.verbs
                if q in (v.get('meaning_urdu', '') or '')
                or q in (v.get('ur_stem', '') or '')]

    def search_english(self, query: str) -> list:
        q = query.strip().lower()
        if not q:
            return []
        starts, contains = [], []
        for v in self.verbs:
            en = (v.get('meaning_english', '') or '').lower()
            base = (v.get('en_base', '') or '').lower()
            if base == q or en == 'to ' + q:
                starts.insert(0, v)
            elif base.startswith(q) or en.startswith('to ' + q):
                starts.append(v)
            elif q in en or q in base:
                contains.append(v)
        return starts + contains

    # ------------------------------------------------------------------
    def search_conjugated_form(self, word: str, conjugation_engine) -> list:
        """Reverse-parse a conjugated word against every verified form."""
        return conjugation_engine.identify_form_from_conjugated(word, self.verbs)

    def guess_root(self, word: str) -> str:
        return ' '.join(ArabicMorphology.extract_root_letters(word))
