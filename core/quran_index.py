# -*- coding: utf-8 -*-
"""Search over the **complete Quranic verb index**.

``data/quran_verbs.json`` holds every verb that actually occurs in the Quran —
1,473 lemmas over 941 roots — each with its root, its باب, every written form
it takes in the text, and the grammatical parse of each of those forms.

This module makes that index searchable by:

* the lemma, with or without harakat            أَنزَلَ  /  انزل
* **any inflected form that occurs in the Quran**   أَنزَلْنَا، يُنزِلُ، أُنزِلَ
* the root                                       ن ز ل  /  نزل
* a near miss, via «کیا آپ کا مطلب یہ تھا؟»

Accuracy policy
---------------
Every entry here is an *attested Quranic verb*; none is generated.  A principal
part is present only when that exact form occurs in the Quran, so a گردان built
from this index rests on Quranic evidence rather than on pattern-filling.  The
three things the brief separates — a theoretically possible form, a real
lexical verb, and a real Quranic occurrence — are kept distinct: this index
contains only the third.
"""

import difflib
import json
import re
from collections import defaultdict
from pathlib import Path

from .arabic_utils import normalise_letters, strip_marks, strip_vowels

DATA = Path(__file__).parent.parent / 'data' / 'quran_verbs.json'

#: tense/voice tags as the corpus writes them
TENSE_UR = {'PERF': 'ماضی', 'IMPF': 'مضارع', 'IMPV': 'امر'}
TENSE_EN = {'PERF': 'Past', 'IMPF': 'Present', 'IMPV': 'Imperative'}
VOICE_UR = {'ACT': 'معروف', 'PASS': 'مجہول'}
VOICE_EN = {'ACT': 'Active', 'PASS': 'Passive'}
MOOD_UR = {'IND': 'مرفوع', 'SUBJ': 'منصوب', 'JUS': 'مجزوم'}

PGN_UR = {
    '3MS': 'واحد مذکر غائب', '3MD': 'تثنیہ مذکر غائب', '3MP': 'جمع مذکر غائب',
    '3FS': 'واحد مؤنث غائب', '3FD': 'تثنیہ مؤنث غائب', '3FP': 'جمع مؤنث غائب',
    '2MS': 'واحد مذکر حاضر', '2MD': 'تثنیہ مذکر حاضر', '2MP': 'جمع مذکر حاضر',
    '2FS': 'واحد مؤنث حاضر', '2FD': 'تثنیہ مؤنث حاضر', '2FP': 'جمع مؤنث حاضر',
    '1S': 'واحد متکلم', '1P': 'جمع متکلم',
}
PGN_EN = {
    '3MS': '3rd m. sing.', '3MD': '3rd m. dual', '3MP': '3rd m. plural',
    '3FS': '3rd f. sing.', '3FD': '3rd f. dual', '3FP': '3rd f. plural',
    '2MS': '2nd m. sing.', '2MD': '2nd m. dual', '2MP': '2nd m. plural',
    '2FS': '2nd f. sing.', '2FD': '2nd f. dual', '2FP': '2nd f. plural',
    '1S': '1st sing.', '1P': '1st plural',
}
PGN_PRONOUN = {
    '3MS': 'هُوَ', '3MD': 'هُمَا', '3MP': 'هُمْ',
    '3FS': 'هِيَ', '3FD': 'هُمَا', '3FP': 'هُنَّ',
    '2MS': 'أَنْتَ', '2MD': 'أَنْتُمَا', '2MP': 'أَنْتُمْ',
    '2FS': 'أَنْتِ', '2FD': 'أَنْتُمَا', '2FP': 'أَنْتُنَّ',
    '1S': 'أَنَا', '1P': 'نَحْنُ',
}


#: Quranic recitation marks — small high seen, rounded zero, waqf signs and
#: friends.  They are not harakat, so ``strip_marks`` leaves them alone, but
#: they must go before comparing: the Quran writes قَالُوا۟, a student types
#: قالوا, and those are the same word.
_QURANIC_MARKS = ''.join(chr(c) for c in
                         list(range(0x0610, 0x061B)) +      # ؐ .. ؚ
                         list(range(0x0653, 0x0660)) +      # ٓ .. ٟ  (ٖ ٗ ٘ …)
                         list(range(0x06D6, 0x06EE)) +      # ۖ .. ۭ
                         [0x0640])                          # ـ tatweel
_QURANIC_TABLE = {ord(c): None for c in _QURANIC_MARKS}

#: the dagger alef — handled before the other marks go, because it is not a
#: vowel sign but a whole letter written small
_DAGGER = 'ٰ'
_ALEF_MAQSURA = 'ى'


def _strip_quranic(text: str) -> str:
    return (text or '').translate(_QURANIC_TABLE)


def _bare_letters(text: str, keep_shadda: bool = False) -> str:
    """Letters only — every mark removed except the dagger alef (and, when
    asked, the shadda), which still have to be interpreted."""
    from .arabic_utils import is_mark, SHADDA
    out = []
    for ch in _strip_quranic(text):
        if ch == _DAGGER or (keep_shadda and ch == SHADDA) or not is_mark(ch):
            out.append(ch)
    return ''.join(out)


def _fold_dagger(bare: str) -> str:
    """Read the Uthmani dagger alef as the long alef it stands for.

    The corpus writes أَنزَلْنَٰهُ, كِتَٰب, هَدَىٰكُمْ; a student types
    انزلناه, كتاب, هداكم, and Islam360 prints اَنْزَلْنٰهُ, كِتَاب, هَدٰكُمْ.
    Dropping the dagger — what a plain mark-stripper does — turned those into
    انزلنه, كتب, هدكم and matched none of them.

    ىٰ is the alef-maqsura ending, which both a student and Islam360 write
    with a ya whether or not a pronoun follows (تَرْضَىٰ → ترضي,
    ٱصْطَفَىٰكِ → اصطفيك as Islam360 has it); a dagger directly before a ya
    is redundant with it; anywhere else it is an alef.
    """
    bare = re.sub(_ALEF_MAQSURA + _DAGGER, 'ي', bare)
    bare = re.sub(_DAGGER + '(?=[يىی])', '', bare)
    return bare.replace(_DAGGER, 'ا')


def _finish(letters: str) -> str:
    # ءَا (the corpus's آ) folds to two alefs; Islam360's اٰ folds to one.
    return re.sub('ا{2,}', 'ا', normalise_letters(letters)).replace(' ', '')


def key_bare(text: str) -> str:
    """Vowel-free, orthography-folded — the main lookup key."""
    return _finish(_fold_dagger(_bare_letters(text)))


def key_shadda(text: str) -> str:
    """Vowel-free but keeps shadda, so عَلَّمَ never collapses into عَلِمَ."""
    return _finish(_fold_dagger(_bare_letters(text, keep_shadda=True)))


class QuranVerbIndex:
    """Loads the index once and answers lookups against it."""

    def __init__(self, path: Path = None):
        self.path = Path(path or DATA)
        self.meta = {}
        self.verbs = []
        self._by_lemma_exact = {}
        self._by_lemma_bare = defaultdict(list)
        self._by_lemma_shadda = defaultdict(list)
        self._by_surface_exact = defaultdict(list)
        self._by_surface_bare = defaultdict(list)
        self._by_root = defaultdict(list)
        self._suggest_pool = {}
        self._load()

    # ------------------------------------------------------------------
    def _load(self):
        if not self.path.exists():
            return
        try:
            raw = json.loads(self.path.read_text(encoding='utf-8'))
        except (json.JSONDecodeError, OSError):
            return
        self.meta = raw.get('meta', {})
        self.verbs = raw.get('verbs', [])

        self._by_surface_shadda = defaultdict(list)
        for i, v in enumerate(self.verbs):
            head = v.get('headword', '')
            self._by_lemma_exact.setdefault(head, i)
            self._by_lemma_bare[key_bare(head)].append(i)
            self._by_lemma_shadda[key_shadda(head)].append(i)
            root = v.get('root', '')
            if root:
                self._by_root[key_bare(root)].append(i)
            # both the morpheme spellings and the whole words a student types
            for surface in list(v.get('segments', {})) + list(v.get('words', {})):
                self._by_surface_exact[surface].append(i)
                self._by_surface_bare[key_bare(surface)].append(i)
                self._by_surface_shadda[key_shadda(surface)].append(i)
            self._suggest_pool.setdefault(key_bare(head), i)

    @property
    def available(self) -> bool:
        return bool(self.verbs)

    def stats(self) -> dict:
        return {
            'lemmas': len(self.verbs),
            'roots': len(self._by_root),
            'surfaces': len(self._by_surface_bare),
            'tokens': self.meta.get('verb_tokens', 0),
        }

    # ------------------------------------------------------------------
    def lookup(self, word: str) -> list:
        """Find Quranic verbs matching ``word``, best match first.

        Returns dicts of ``{entry, match, surface, parse}`` where ``match`` is
        one of ``lemma_exact``, ``surface_exact``, ``lemma``, ``surface``.
        """
        word = (word or '').strip()
        if not word:
            return []

        results, seen = [], set()

        def parse_of(entry, surface):
            if not surface:
                return None
            return (entry.get('words', {}).get(surface)
                    or entry.get('segments', {}).get(surface))

        def add(idx, match, surface=None):
            # one row per verb: the first (best) match type wins, so a verb
            # never appears three times merely because several keys reached it
            if idx in seen:
                return
            seen.add(idx)
            entry = self.verbs[idx]
            results.append({'entry': entry, 'match': match,
                            'surface': surface,
                            'parse': parse_of(entry, surface)})

        # 1. the word IS a lemma, exactly as written
        if word in self._by_lemma_exact:
            add(self._by_lemma_exact[word], 'lemma_exact')

        # 2. the word is an inflected form, exactly as the Quran writes it
        for idx in self._by_surface_exact.get(word, []):
            add(idx, 'surface_exact', word)

        # 3. shadda-preserving match — must outrank the vowel-blind one, or
        #    عَلَّمَ (باب تفعیل) would lose to the commoner عَلِمَ (باب اوّل)
        bare = key_bare(word)
        shadda = key_shadda(word)
        for idx in self._by_lemma_shadda.get(shadda, []):
            add(idx, 'lemma_shadda')
        for idx in self._by_surface_shadda.get(shadda, []):
            add(idx, 'surface_shadda',
                self._pick_surface(idx, key_shadda, shadda))

        # 4. finally, ignoring shadda too
        for idx in self._by_lemma_bare.get(bare, []):
            add(idx, 'lemma')
        for idx in self._by_surface_bare.get(bare, []):
            add(idx, 'surface', self._pick_surface(idx, key_bare, bare))

        # 5. the word may be a bare root — ن ز ل or نزل
        if not results and 2 <= len(bare) <= 4:
            for entry in self.by_root(bare):
                idx = self._by_lemma_exact.get(entry.get('headword'))
                if idx is not None:
                    add(idx, 'root')

        order = {'lemma_exact': 0, 'surface_exact': 1,
                 'lemma_shadda': 2, 'surface_shadda': 3,
                 'lemma': 4, 'surface': 5, 'root': 6}
        results.sort(key=lambda r: (order[r['match']],
                                    -r['entry'].get('count', 0)))
        return results

    def _pick_surface(self, idx: int, keyfn, target: str):
        entry = self.verbs[idx]
        for pool in ('words', 'segments'):
            for surface in entry.get(pool, {}):
                if keyfn(surface) == target:
                    return surface
        return None

    def by_root(self, root: str) -> list:
        """Every Quranic verb sharing a root, ordered by frequency."""
        idxs = self._by_root.get(key_bare(root), [])
        return sorted((self.verbs[i] for i in idxs),
                      key=lambda v: (v.get('baab') or 99, -v.get('count', 0)))

    def get(self, headword: str):
        idx = self._by_lemma_exact.get(headword)
        return self.verbs[idx] if idx is not None else None

    def get_by_root_baab(self, root: str, baab):
        target = key_bare(root)
        for i in self._by_root.get(target, []):
            if self.verbs[i].get('baab') == baab:
                return self.verbs[i]
        return None

    # ------------------------------------------------------------------
    def suggest(self, word: str, limit: int = 6) -> list:
        """«کیا آپ کا مطلب یہ تھا؟» — near misses from real Quranic verbs.

        Matches on the vowel-free skeleton, then keeps only candidates that
        are genuinely close, so an unrelated verb is never offered merely
        because it happens to share a couple of letters.
        """
        bare = key_bare(word)
        if len(bare) < 2:
            return []

        pool = list(self._suggest_pool)
        close = difflib.get_close_matches(bare, pool, n=limit * 4, cutoff=0.6)

        scored = []
        for cand in close:
            idx = self._suggest_pool[cand]
            entry = self.verbs[idx]
            ratio = difflib.SequenceMatcher(None, bare, cand).ratio()
            # a shared root is strong evidence the suggestion is relevant
            shares_root = bool(entry.get('root')) and (
                key_bare(entry['root'])[:2] in bare[:3])
            _ = shares_root
            scored.append((ratio + (0.15 if shares_root else 0), entry))

        scored.sort(key=lambda x: (-x[0], -x[1].get('count', 0)))
        out, seen = [], set()
        for score, entry in scored:
            if entry['headword'] in seen:
                continue
            seen.add(entry['headword'])
            out.append(entry)
            if len(out) >= limit:
                break
        return out


# ---------------------------------------------------------------------------
def describe_parse(parse: dict, lang: str = 'ur') -> str:
    """A readable description of one Quranic form's grammar."""
    if not parse:
        return ''
    tense, voice = parse.get('tense'), parse.get('voice', 'ACT')
    pgn, mood = parse.get('pgn'), parse.get('mood')
    if lang == 'en':
        bits = [TENSE_EN.get(tense, ''), VOICE_EN.get(voice, ''),
                PGN_EN.get(pgn, '')]
    else:
        bits = [TENSE_UR.get(tense, ''), VOICE_UR.get(voice, ''),
                PGN_UR.get(pgn, '')]
        if mood and mood != 'IND':
            bits.append(MOOD_UR.get(mood, ''))
    return ' · '.join(b for b in bits if b)
