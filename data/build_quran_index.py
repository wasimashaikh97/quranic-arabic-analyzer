# -*- coding: utf-8 -*-
"""Build ``data/quranic_occurrences.json`` from the verified Quran text.

Nothing here is written from memory.  The pipeline is:

  1. read the Tanzil **uthmani** text (the standard reference edition) that
     ``download`` cached under ``data/quran_cache/``;
  2. for every verb in the lexicon, take the 68 forms ``core.conjugation``
     generates and look for them as **whole words** in that text;
  3. record the surah, the ayah, the exact ayah text, the matched word, and —
     when the vowels identify it unambiguously — which صیغہ it is.

A match must agree on the shadda-aware consonantal skeleton *and* contain the
verb's root letters in order, which is what keeps كَتَّبَ out of كَتَبَ's results.

Usage::

    python data/build_quran_index.py            # rebuild the index
    python data/build_quran_index.py --download # fetch the sources first
"""

import argparse
import json
import os
import sys
import urllib.request
from collections import defaultdict
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from core.arabic_utils import (                                    # noqa: E402
    ALL_MARKS, SHADDA, FATHA, DAMMA, KASRA, SUKUN,
    normalise_letters, split_units, strip_marks,
)
from core.analyzer import VerbAnalyzer                             # noqa: E402
from core.conjugation import (                                     # noqa: E402
    ConjugationEngine, TENSE_LABELS, present_forms,
)

CACHE = ROOT_DIR / 'data' / 'quran_cache'

SOURCES = {
    'quran-uthmani.txt':
        'https://tanzil.net/pub/download/index.php'
        '?quranType=uthmani&outType=txt-2&agree=true',
    'ur.jalandhry.json': 'https://api.alquran.cloud/v1/quran/ur.jalandhry',
    'en.sahih.json': 'https://api.alquran.cloud/v1/quran/en.sahih',
    'surahs.json': 'https://api.alquran.cloud/v1/surah',
}

#: at most this many ayaat per verb, so the page stays readable
MAX_PER_VERB = 6
#: uthmani text uses characters that never appear in a dictionary head-word
UTHMANI_EXTRAS = (
    'ٱ'   # ٱ  alef wasla
    'ٰ'   # ٰ  superscript alef
    'ۣۡۢۤۥۦ۪ۭۧۨ۫۬'
    'ۖۗۘۙۚۛۜ۝۞۟۠'
    'ٕٖ۟ٓٔٗ٘'
)


# ---------------------------------------------------------------------------
def download():
    CACHE.mkdir(parents=True, exist_ok=True)
    for name, url in SOURCES.items():
        path = CACHE / name
        if path.exists() and path.stat().st_size > 1000:
            print('  cached  %s' % name)
            continue
        print('  fetching %s ...' % name)
        data = urllib.request.urlopen(url, timeout=180).read()
        path.write_bytes(data)


# ---------------------------------------------------------------------------
HAMZA_CHARS = 'ءأإآؤئ'

#: single-letter proclitics that attach to a verb in the Quran
#:   فَلْيَتَنَافَسِ  =  فَ + لْ + يَتَنَافَسِ
PROCLITICS = ('فَ', 'وَ', 'لَ', 'لِ', 'لْ', 'سَ', 'أَ', 'فَلْ', 'وَلْ',
              'فَسَ', 'وَسَ', 'أَفَ', 'أَوَ', 'فَ', 'وَ')

#: attached object pronouns that follow a verb
#:   أَنزَلْنَاهُ  =  أَنزَلْنَا + هُ
ENCLITICS = ('هُمَا', 'هِمَا', 'كُمَا', 'هُمْ', 'هِمْ', 'كُمْ', 'هُنَّ', 'هِنَّ',
             'كُنَّ', 'نِي', 'نَا', 'هَا', 'هُ', 'هِ', 'كَ', 'كِ', 'ي')


def word_key(word: str) -> str:
    """Shadda-aware consonantal skeleton, with uthmani spelling folded in."""
    out = []
    for ch in word:
        if ch in UTHMANI_EXTRAS:
            # ٱ is a plain alef; ٰ stands for a long a; marks carry no letter
            if ch in ('ٱ', 'ٰ'):
                out.append('ا')
            continue
        if ch in ALL_MARKS and ch != SHADDA:
            continue
        out.append(ch)
    return normalise_letters(''.join(out))


def word_key_variants(word: str) -> set:
    """Every skeleton this word could plausibly be written as.

    The uthmani text seats hamza differently from a dictionary head-word
    (يَسْتَهْزِءُونَ vs يَسْتَهْزِئُونَ), so each spelling of the hamza gets its
    own key and a match on any one of them counts.
    """
    base = word_key(word)
    variants = {base}
    # every hamza carrier folded to a single marker, and dropped entirely
    folded = ''.join('ء' if ch in HAMZA_CHARS else ch for ch in base)
    variants.add(folded)
    variants.add(folded.replace('ء', ''))
    variants.add(''.join(ch for ch in base if ch not in HAMZA_CHARS))
    # ٰ sometimes stands in for an alef that is already written (وَقَىٰ),
    # so a variant without the extra alef is needed too
    for v in list(variants):
        if 'ا' in v:
            variants.add(v.replace('اا', 'ا'))
    return {v for v in variants if len(v) >= 3}


def strip_affixes(word: str):
    """Yield ``(stem, n_stripped)`` for the word and its clitic-stripped forms.

    The unstripped word is yielded first so that an exact match always wins
    over one that needed a pronoun removed.
    """
    yield word, 0
    seen = {word}

    def add(candidate, depth):
        if candidate and candidate not in seen and len(strip_marks(candidate)) >= 3:
            seen.add(candidate)
            return [(candidate, depth)]
        return []

    stage = []
    for enc in ENCLITICS:
        if word.endswith(enc):
            stage += add(word[:-len(enc)], 1)
    for pro in PROCLITICS:
        if word.startswith(pro):
            stage += add(word[len(pro):], 1)
    for candidate, _d in list(stage):
        for enc in ENCLITICS:
            if candidate.endswith(enc):
                stage += add(candidate[:-len(enc)], 2)
    for item in stage:
        yield item


def vowel_signature(word: str) -> str:
    """The short vowels written on a word, in order.

    Two conventions are normalised away, symmetrically on both sides:

    * **Sukun** — the uthmani text routinely omits it where a dictionary form
      writes it, so requiring it to agree would discard correct matches.
    * **The vowel on a word-initial alef** — همزۃ الوصل is written bare in the
      Quran (ٱنفَطَرَتْ) but voweled in a dictionary head-word (اِنْفَطَرَتْ),
      which would otherwise lose every باب انفعال / افتعال / استفعال match.
    """
    units = split_units(word)
    if units and units[0][0] in 'اٱأإآ':
        units = units[1:]                 # drop that first letter's vowel
    marks = ''.join(m for _letter, m in units)
    return ''.join(ch for ch in marks if ch in (FATHA, DAMMA, KASRA))


def bare_letters(word: str) -> str:
    return normalise_letters(strip_marks(
        ''.join(c for c in word if c not in UTHMANI_EXTRAS or c == 'ٱ')
    ).replace('ٱ', 'ا'))


#: a weak or hamza radical surfaces as any of these, or vanishes altogether
_WEAK_EQUIV = set('اوىيءأإآؤئ')


def contains_root(word: str, root_letters) -> bool:
    """Are the root letters present, in order, in this word?

    A weak radical is matched loosely, because it frequently does **not**
    survive on the surface: خ‑و‑ف gives خَافَ (the و became an alef) and
    يَخَافُ, so demanding a literal و would reject every hollow verb.  Weak
    radicals may therefore also be absent; the strong radicals must be there.
    """
    letters = bare_letters(word)
    pos = 0
    for radical in root_letters:
        radical = normalise_letters(radical)
        if radical in _WEAK_EQUIV:
            # accept any weak letter here, or none at all
            for candidate in 'اويى':
                found = letters.find(candidate, pos)
                if found >= 0:
                    pos = found + 1
                    break
            continue
        found = letters.find(radical, pos)
        if found < 0:
            return False
        pos = found + 1
    return True


def letters_variants(word: str) -> set:
    """Letter sequences this word could be, ignoring all vowels.

    Folded, because these are the same letter written differently:
      ٱ → ا          (alef wasla)
      أ إ آ ؤ ئ ء → ء (the hamza, wherever it is seated)
    Kept apart, because these are genuinely different letters:
      ى vs ي,  و vs ا
    ٰ stands either for an alef that is written elsewhere or for one that is
    not, so both readings are offered.
    """
    keep_alef, drop_alef = [], []
    for ch in word:
        if ch in ALL_MARKS:
            continue
        if ch == 'ٱ':
            keep_alef.append('ا'); drop_alef.append('ا'); continue
        if ch == 'ٰ':
            keep_alef.append('ا'); continue          # drop_alef omits it
        if ch in UTHMANI_EXTRAS:
            continue
        if ch in HAMZA_CHARS:
            keep_alef.append('ء'); drop_alef.append('ء'); continue
        keep_alef.append(ch); drop_alef.append(ch)
    return {''.join(keep_alef), ''.join(drop_alef)}


def _mark_of(marks: str):
    """The single vowel or sukun written on a letter, if any."""
    for ch in marks:
        if ch in (FATHA, DAMMA, KASRA, SUKUN):
            return ch
    return None


def compatible(quranic_stem: str, candidate: str) -> bool:
    """Could the Quran's spelling and this generated form be the same word?

    Two conditions, both necessary:

    1. the **letters** agree (see :func:`letters_variants`), which rejects
       أَفِى (the preposition, with ى) as a form of وَفَى (whose أَفِي has ي);
    2. no letter carries **contradicting** marks.  The uthmani text often
       omits a sukun the dictionary writes, which is fine, but it never writes
       فتحہ where the form has سکون — that is what separates أَعْنَتَ
       (from ع‑ن‑ت) from أَعَنْتَ (from ع‑و‑ن).
    """
    if not letters_variants(quranic_stem) & letters_variants(candidate):
        return False

    q_units = [u for u in split_units(quranic_stem)
               if u[0] not in UTHMANI_EXTRAS or u[0] in 'ٱٰ']
    c_units = split_units(candidate)
    if len(q_units) != len(c_units):
        return True          # the ٰ reading differed; the letters already agreed

    for (_ql, q_marks), (_cl, c_marks) in zip(q_units, c_units):
        q_mark, c_mark = _mark_of(q_marks), _mark_of(c_marks)
        if q_mark and c_mark and q_mark != c_mark:
            return False
        if (SHADDA in q_marks) != (SHADDA in c_marks):
            return False

    # The Quran vowels its text fully, so a form ending in a bare weak letter
    # (يَدْعُو، نَادِي) must correspond to a bare one there too.  This is what
    # separates the noun نَادِيَ (96:17) from the verb form نَادِي.
    q_last, c_last = _mark_of(q_units[-1][1]), _mark_of(c_units[-1][1])
    if c_last is None and q_last in (FATHA, DAMMA, KASRA):
        return False
    return True


# ---------------------------------------------------------------------------
def load_corpus():
    text_path = CACHE / 'quran-uthmani.txt'
    if not text_path.exists():
        raise SystemExit('Quran text missing — run with --download first.')

    ayaat = {}
    for line in text_path.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        parts = line.split('|', 2)
        if len(parts) != 3:
            continue
        surah, ayah, body = int(parts[0]), int(parts[1]), parts[2].strip()
        ayaat[(surah, ayah)] = body

    def load_translation(name):
        raw = json.loads((CACHE / name).read_text(encoding='utf-8'))
        out = {}
        for surah in raw['data']['surahs']:
            for ayah in surah['ayahs']:
                out[(surah['number'], ayah['numberInSurah'])] = ayah['text']
        return out

    urdu = load_translation('ur.jalandhry.json')
    english = load_translation('en.sahih.json')

    surahs = {}
    for s in json.loads((CACHE / 'surahs.json').read_text(encoding='utf-8'))['data']:
        surahs[s['number']] = {
            'name_arabic': s['name'].replace('سُورَةُ ', '').strip(),
            'name_english': s['englishName'],
        }

    return ayaat, urdu, english, surahs


def build_word_index(ayaat):
    """key -> list of (surah, ayah, word as written, stem matched, n_stripped).

    Each Quranic word is indexed under the skeletons of the word itself *and*
    of its clitic-stripped stems, so أَنزَلْنَاهُ is found for أَنْزَلَ and
    فَلْيَتَنَافَسِ for تَنَافَسَ.
    """
    index = defaultdict(list)
    # NB: ٱ and ٰ are *letters*, so they must never be stripped —
    # doing so turned ٱنفَطَرَتْ (82:1) into نفَطَرَتْ and lost the match.
    strip_chars = ''.join(c for c in UTHMANI_EXTRAS if c not in 'ٱٰ')         + '.,;:!?؛؟‌‍‎‏'
    for (surah, ayah), body in ayaat.items():
        for raw in body.split():
            cleaned = raw.strip(strip_chars)
            if not cleaned:
                continue
            for stem, depth in strip_affixes(cleaned):
                for key in word_key_variants(stem):
                    index[key].append((surah, ayah, cleaned, stem, depth))
    return index


# ---------------------------------------------------------------------------
def identify_sigha(quranic_word: str, candidates: list):
    """Pick the صیغہ whose vowels agree with the word as the Quran writes it.

    ``candidates`` is a list of ``(tense, row)``.  Returns
    ``(tense, row, certain)`` or ``None`` when nothing agrees.
    """
    if not candidates:
        return None

    # A skeleton match alone is not enough: نَادِيَهُ (96:17) is the noun
    # «نادی» + هُ, not a form of نَادَى.  Compare letter by letter.
    agreeing = [(tense, row) for tense, row in candidates
                if compatible(quranic_word, row['arabic'])]
    if not agreeing:
        return None

    # A form can be reached by more than one route — يَكْتُبُوا is both منصوب
    # and مجزوم — which is one word, not an ambiguity.  Collapse those, and
    # prefer the plain tense a student looks up over the derived moods.
    MAIN = ('past_active', 'present_active', 'past_passive',
            'present_passive', 'imperative', 'prohibition')
    agreeing.sort(key=lambda tr: (tr[0] not in MAIN, tr[0]))

    distinct = []
    seen = set()
    for tense, row in agreeing:
        signature = (row['arabic'], row.get('sigha_urdu'))
        if signature in seen:
            continue
        seen.add(signature)
        distinct.append((tense, row))

    tense, row = distinct[0]
    # genuinely different صیغے sharing one spelling (أَنْتُمَا masculine and
    # feminine) stay flagged as ambiguous
    return tense, row, len(distinct) == 1


# ---------------------------------------------------------------------------
def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--download', action='store_true',
                        help='fetch the Quran text and translations first')
    args = parser.parse_args()

    if args.download:
        print('Downloading sources:')
        download()

    print('Loading the verified corpus ...')
    ayaat, urdu, english, surahs = load_corpus()
    print('  %d ayaat, %d Urdu, %d English, %d surahs'
          % (len(ayaat), len(urdu), len(english), len(surahs)))

    print('Indexing every word of the Quran ...')
    word_index = build_word_index(ayaat)
    print('  %d distinct word skeletons' % len(word_index))

    analyzer = VerbAnalyzer()
    occurrences = []
    covered = 0
    uncertain = 0

    print('Matching %d verbs ...' % len(analyzer.verbs))
    for verb in analyzer.verbs:
        root_letters = verb.get('root_letters') or []
        conj = analyzer.conjugate(verb)

        # every generated form of this verb, grouped by its skeleton variants.
        # The مضارع منصوب / مجزوم are included because Quranic Arabic uses them
        # constantly (أَنْ تَصُومُوا، فَلْيَتَنَافَسِ، لَمْ يَلِدْ).
        extra = {}
        for mood, label in (('subjunctive', 'present_subjunctive'),
                            ('jussive', 'present_jussive')):
            for base, voice in (('present_3ms', 'active'),
                                ('present_passive_3ms', 'passive')):
                stem = verb.get(base)
                if not stem:
                    continue
                key_name = '%s_%s' % (label, voice)
                try:
                    forms = present_forms(stem, mood)
                except Exception:
                    continue
                extra[key_name] = ConjugationEngine._rows(
                    forms, 'present_active' if voice == 'active'
                    else 'present_passive',
                    verb.get('ur_stem', ''), verb.get('ur_past', ''),
                    verb.get('en_base', ''), verb.get('en_past', ''),
                    verb.get('en_pp', ''))

        by_key = defaultdict(list)
        for tense, rows in list(conj.items()) + list(extra.items()):
            for row in rows:
                form = row.get('arabic', '')
                if not form or ' ' in form:          # skip «لَا تَكْتُبْ»
                    continue
                if len(strip_marks(form)) < 3:       # too short to be safe
                    continue
                for key in word_key_variants(form):
                    by_key[key].append((tense, row))

        # collect candidate matches, then keep the best one per ayah
        found = {}
        for key, candidates in by_key.items():
            for surah, ayah, quranic_word, stem, depth in word_index.get(key, []):
                if not contains_root(stem, root_letters):
                    continue
                previous = found.get((surah, ayah))
                if previous and previous[0] <= depth:
                    continue                          # keep the cleaner match
                found[(surah, ayah)] = (depth, quranic_word, stem, candidates)

        hits = []
        for (surah, ayah), (depth, quranic_word, stem, candidates) in found.items():
                identified = identify_sigha(stem, candidates)
                if not identified:
                    continue
                tense, row, certain = identified
                if not certain:
                    uncertain += 1
                body = ayaat[(surah, ayah)]
                hits.append({
                    'affixed': depth > 0,
                    'verb_id': verb['id'],
                    'root': verb['root'],
                    'surah_number': surah,
                    'surah_name_arabic': surahs.get(surah, {}).get('name_arabic', ''),
                    'surah_name_english': surahs.get(surah, {}).get('name_english', ''),
                    'ayah_number': ayah,
                    'arabic_text': body,
                    'highlighted_word': quranic_word,
                    'word_form': tense,
                    'sigha_urdu': row.get('sigha_urdu', ''),
                    'sigha_english': row.get('sigha_english', ''),
                    'pronoun_arabic': row.get('pronoun_arabic', ''),
                    'form_certain': certain,
                    'translation_urdu': urdu.get((surah, ayah), ''),
                    'translation_english': english.get((surah, ayah), ''),
                    'ayah_length': len(body),
                })

        # prefer short ayaat (easier to read) and a certain identification
        hits.sort(key=lambda h: (not h['form_certain'], h['ayah_length']))
        chosen = hits[:MAX_PER_VERB]
        for hit in chosen:
            hit.pop('ayah_length', None)
        occurrences.extend(chosen)
        if chosen:
            covered += 1
        print('  %-16s %-9s %d ayaat' % (verb['arabic'], verb['root'],
                                         len(chosen)))

    out = ROOT_DIR / 'data' / 'quranic_occurrences.json'
    out.write_text(json.dumps({'occurrences': occurrences},
                              ensure_ascii=False, indent=1),
                   encoding='utf-8')

    print()
    print('Wrote %d occurrences for %d/%d verbs (%.0f%% coverage)'
          % (len(occurrences), covered, len(analyzer.verbs),
             100.0 * covered / max(1, len(analyzer.verbs))))
    print('  صیغہ uncertain in %d matches (labelled as such)' % uncertain)
    print('  source: Tanzil uthmani · Urdu: Jalandhry · English: Sahih Intl')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
