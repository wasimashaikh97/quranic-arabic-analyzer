"""Analysis orchestrator — the single entry point the interface talks to."""

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

from .arabic_utils import key_exact, key_strict, key_loose
from .abwaab import get_baab, mazeed_abwaab, ALL_BAAB_ORDER, BAAB_INFO
from .morphology import ArabicMorphology
from .conjugation import (
    ConjugationEngine, ConjugationError, TENSE_ORDER, TENSE_LABELS,
    MANDATORY_TENSES,
)
from .search import VerbSearch

from .validation import InputValidator, message

#: surah names, read once from the cached list if it is present
def _load_surah_names():
    import json as _json
    from pathlib import Path as _Path
    p = _Path(__file__).parent.parent / 'data' / 'surah_names.json'
    if p.exists():
        try:
            return {int(k): v for k, v in
                    _json.loads(p.read_text(encoding='utf-8')).items()}
        except Exception:
            return {}
    return {}

SURAH_NAMES = _load_surah_names()


class VerbAnalyzer:
    """Loads the verified lexicon and answers every question the UI asks."""

    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / 'data'
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.verbs = (self._load_json('verbs.json') or {}).get('verbs', [])
        self.roots = (self._load_json('roots.json') or {}).get('roots', [])
        self.quranic = (self._load_json('quranic_occurrences.json')
                        or {}).get('occurrences', [])

        self.morphology = ArabicMorphology()
        self.conjugation_engine = ConjugationEngine()
        self.search_engine = VerbSearch(self.verbs, self.roots)

        self._verbs_by_id = {v.get('id'): v for v in self.verbs}
        self._quran_index = None      # loaded on first use
        self._conjugation_cache = {}
        self._form_index_exact = {}
        self._form_index_strict = {}
        self._form_index_loose = {}
        self._build_form_index()

        self.db_path = self.data_dir / 'user_data.db'
        self._init_db()

    # ------------------------------------------------------------------
    def _load_json(self, filename: str):
        path = self.data_dir / filename
        if not path.exists():
            return {}
        try:
            with open(path, 'r', encoding='utf-8') as fh:
                return json.load(fh)
        except (json.JSONDecodeError, OSError):
            return {}

    # ------------------------------------------------------------------
    def conjugate(self, verb: dict) -> dict:
        """Cached full گردان of one verb."""
        vid = verb.get('id') or verb.get('arabic')
        if vid in self._conjugation_cache:
            return self._conjugation_cache[vid]
        try:
            conj = self.conjugation_engine.conjugate_verb(verb)
        except ConjugationError:
            conj = {k: [] for k in TENSE_ORDER}
        self._conjugation_cache[vid] = conj
        return conj

    def _build_form_index(self):
        """Index all 68 inflected forms of every verb for reverse lookup."""
        for verb in self.verbs:
            conj = self.conjugate(verb)
            for tense, rows in conj.items():
                for row in rows:
                    form = row.get('arabic', '')
                    if not form:
                        continue
                    hit = (verb.get('id'), tense, row)
                    self._form_index_exact.setdefault(
                        key_exact(form), []).append(hit)
                    self._form_index_strict.setdefault(
                        key_strict(form), []).append(hit)
                    self._form_index_loose.setdefault(
                        key_loose(form), []).append(hit)

    # ==================================================================
    # main analysis
    # ==================================================================
    def analyze_verb(self, input_text: str, lang: str = 'ur') -> dict:
        """Identify a verb — dictionary form, conjugated form, or root."""
        valid = InputValidator.validate_input(input_text)
        if not valid['valid']:
            return {'found': False, 'reason': valid['error_key'],
                    'message': message(valid['error_key'], lang),
                    'input': input_text}

        cleaned = valid['cleaned']
        input_type = valid['input_type']

        # ---- 1. exact, fully-diacritised dictionary head-word ----------
        if input_type in ('arabic', 'urdu'):
            hits = self.search_engine.search_exact(cleaned)
            if hits:
                verb = self._best_hit(hits)
                return self._result(
                    verb, cleaned, analysis_type='dictionary_form',
                    quality='exact',
                    alternatives=[v for v in hits if v is not verb][:8])

        # ---- 2. exact, fully-diacritised inflected form ----------------
        #  أُنْزِلَ is the ماضی مجہول of أَنْزَلَ, not a head-word of its own,
        #  so an exact inflected match must beat a vowel-blind head-word match.
        if input_type in ('arabic', 'urdu'):
            parsed = self.parse_conjugated(cleaned, exact_only=True)
            if parsed.get('found'):
                return self._conjugated_result(parsed, cleaned)

        # ---- 3. root entered as «ن ز ل» --------------------------------
        if input_type == 'root':
            hits = self.search_engine.search_root(cleaned)
            if hits:
                verb = self._best_hit(hits)
                return self._result(
                    verb, cleaned, analysis_type='root_lookup',
                    quality='exact',
                    alternatives=[v for v in hits if v is not verb][:12])

        # ---- 4. head-word without (or with partial) harakat ------------
        if input_type in ('arabic', 'urdu'):
            hits = self.search_engine.search_arabic(cleaned)
            if hits:
                verb = self._best_hit(hits)
                return self._result(
                    verb, cleaned, analysis_type='dictionary_form',
                    quality=self.search_engine.match_quality(cleaned, verb),
                    alternatives=[v for v in hits if v is not verb][:8])

        # ---- 5. inflected form without harakat -------------------------
        parsed = self.parse_conjugated(cleaned)
        if parsed.get('found'):
            return self._conjugated_result(parsed, cleaned)

        # ---- 6. meaning search (Urdu / English) ------------------------
        if input_type in ('english', 'urdu'):
            hits = (self.search_engine.search_english(cleaned)
                    if input_type == 'english'
                    else self.search_engine.search_urdu(cleaned))
            if hits:
                verb = hits[0]
                return self._result(verb, cleaned, analysis_type='meaning_search',
                                    quality='meaning',
                                    alternatives=hits[1:9])

        # ---- 7. the complete Quranic verb index -------------------------
        #  1,473 verbs that actually occur in the Quran, searchable by lemma,
        #  by root, and by any inflected form the text contains.  Reached only
        #  after the curated lexicon, which carries the fuller Sarf data.
        if input_type in ('arabic', 'urdu', 'root'):
            quranic = self.lookup_quranic(cleaned)
            if quranic:
                return self._quranic_result(quranic, cleaned, lang)

        guessed = self.search_engine.guess_root(cleaned)
        siblings = self.search_engine.search_root(guessed)
        if siblings:
            return {
                'found': False,
                'reason': 'root_only',
                'message': message('not_found', lang),
                'input': cleaned,
                'guessed_root': guessed,
                'root_suggestions': siblings[:12],
                # near misses too, so the student always has somewhere to go
                'did_you_mean': self.suggest(cleaned, 4),
            }

        # ---- 8. nothing matched — offer «کیا آپ کا مطلب یہ تھا؟» --------
        if input_type in ('arabic', 'urdu', 'root'):
            did_you_mean = self.suggest(cleaned)
            if did_you_mean:
                return {
                    'found': False,
                    'reason': 'did_you_mean',
                    'message': message('not_found', lang),
                    'input': cleaned,
                    'guessed_root': self.search_engine.guess_root(cleaned),
                    'root_suggestions': [],
                    'did_you_mean': did_you_mean,
                }

        # Latin input that matched no meaning is almost always someone typing
        # in the wrong script — say so plainly instead of "no data".
        reason = 'not_arabic' if input_type == 'english' else 'not_found'
        return {'found': False, 'reason': reason,
                'message': message(reason, lang),
                'input': cleaned, 'guessed_root': guessed,
                'root_suggestions': []}

    # ==================================================================
    # the complete Quranic verb index
    # ==================================================================
    @property
    def quran_index(self):
        """Lazily loaded, so start-up stays fast when it is not needed."""
        if self._quran_index is None:
            from .quran_index import QuranVerbIndex
            self._quran_index = QuranVerbIndex()
        return self._quran_index

    def lookup_quranic(self, word: str) -> list:
        try:
            return self.quran_index.lookup(word)
        except Exception:
            return []

    def suggest(self, word: str, limit: int = 6) -> list:
        """«کیا آپ کا مطلب یہ تھا؟» over real Quranic verbs."""
        try:
            return self.quran_index.suggest(word, limit)
        except Exception:
            return []

    def quranic_to_record(self, entry: dict) -> dict:
        """Shape a Quranic index entry like a curated verb record.

        The interface already knows how to render a verb, so a Quranic verb is
        adapted into the same shape rather than given a second layout.  Fields
        the Quran does not attest are left empty on purpose — the page then
        shows «قابلِ اطلاق نہیں» instead of a manufactured form.
        """
        from .quran_index import PGN_UR, PGN_EN, describe_parse

        baab = entry.get('baab') or 1
        baab_info = get_baab(baab)
        principal = entry.get('principal') or {}
        root_spaced = entry.get('root_spaced') or ' '.join(entry.get('root', ''))

        record = {
            'id': 'q_%s_%s' % (entry.get('root', ''), baab),
            'arabic': entry.get('headword', ''),
            'root': root_spaced,
            'root_letters': list(entry.get('root', '')),
            'baab': baab,
            'form': baab,
            'baab_name_arabic': baab_info['name_ar'],
            'baab_name_urdu': baab_info['name_ur'],
            'baab_name_english': baab_info['name_en'],
            'baab_category_urdu': baab_info['category_ur'],
            'is_mazeed': baab_info['is_mazeed'],
            'wazn': baab_info['wazn_past'],
            'pattern': baab_info['wazn_past'],
            'form_name_arabic': baab_info['wazn_past'],
            'wazn_present': baab_info['wazn_present'],
            'wazn_past_passive': baab_info['wazn_past_passive'],
            'wazn_present_passive': baab_info['wazn_present_passive'],

            # principal parts, ONLY where the Quran attests them
            'past_3ms': principal.get('past_active'),
            'present_3ms': principal.get('present_active'),
            'past_passive_3ms': principal.get('past_passive'),
            'present_passive_3ms': principal.get('present_passive'),
            'has_passive': bool(principal.get('past_passive')),

            'verb_type': ArabicMorphology.identify_verb_type(
                list(entry.get('root', ''))),
            'transitivity': '',
            'masdar': None,
            'masdar_pattern': baab_info['masdar_pattern'],
            'ism_fail': None,
            'ism_mafool': None,
            'derived_nouns': {},
            'meaning_urdu': '',
            'meaning_english': '',

            # provenance — this is a Quranic-corpus verb, not a curated one
            'source': 'quran_index',
            'quran_count': entry.get('count', 0),
            'quran_forms': entry.get('surface_count', 0),
            'headword_attested': entry.get('headword_attested', False),
            'unavailable_note': self._quranic_note(entry),
        }
        return record

    @staticmethod
    def _quranic_note(entry: dict) -> str:
        missing = [k for k in ('past_active', 'present_active')
                   if k not in (entry.get('principal') or {})]
        bits = ['یہ فعل قرآن مجید میں %d مرتبہ آیا ہے۔' % entry.get('count', 0)]
        if not entry.get('headword_attested'):
            bits.append('اس کی لغوی (ڈکشنری) صورت قرآن میں نہیں آئی، اس لیے '
                        'یہاں قرآن میں موجود صورت دکھائی گئی ہے۔')
        if missing:
            bits.append('صرف وہی صیغے دکھائے گئے ہیں جو قرآن میں موجود ہیں؛ '
                        'باقی صورتیں خود سے نہیں بنائی گئیں۔')
        return ' '.join(bits)

    def islam360_enrich(self, occurrences: list, root: str = '') -> list:
        """Put Islam360's own ayah text and translations onto occurrences.

        The specification asks for Quranic references, verses and meanings to
        come from Islam360.  Islam360's data is indexed by root, not parsed
        morphologically, so it cannot say which صیغہ a word is — and asking it
        for «every word of the root» returns the wrong words entirely
        (تَقَبَّلَ would come back showing the preposition قَبْلِكَ).

        So which words belong to the searched verb stays a morphology question,
        answered by the tagged corpus, and Islam360 answers the questions it
        actually holds the answers to: the verse text, the surah name, the Urdu
        and English meanings, and whether it lists that word under this root.
        Each occurrence records which parts came from where.  When Islam360 is
        not connected the occurrences pass through untouched.
        """
        if not occurrences:
            return occurrences
        try:
            from services import quran_source
            from .quran_index import key_bare
            provider = quran_source.get_islam360()
            if not provider.configured:
                return occurrences
        except Exception:
            return occurrences

        target = key_bare(root)
        for occ in occurrences:
            try:
                record = provider.ayah(occ.get('surah_number'),
                                       occ.get('ayah_number'))
            except Exception:
                record = None
            if not record:
                continue
            occ['arabic_text'] = record.get('arabic_text') or occ.get('arabic_text', '')
            occ['surah_name_arabic'] = (record.get('surah_name_arabic')
                                        or occ.get('surah_name_arabic', ''))
            occ['surah_name_english'] = (record.get('surah_name_english')
                                         or occ.get('surah_name_english', ''))
            occ['translation_urdu'] = record.get('translation_urdu', '')
            occ['translation_english'] = record.get('translation_english', '')
            occ['text_source'] = 'Islam360'
            occ['source'] = 'Islam360'
            try:
                roots = provider.roots_for_word(
                    key_bare(occ.get('highlighted_word', '')))
                occ['islam360_root_match'] = any(
                    key_bare(r) == target for r in roots) if target else False
            except Exception:
                occ['islam360_root_match'] = False
        return occurrences

    def islam360_occurrences(self, root: str, limit: int = 6) -> list:
        """Every Quranic word of a root, straight from Islam360.

        Islam360 groups by root, so this is a root-level listing — it is *not*
        صیغہ-analysed and may include nouns and other abwaab of the same root.
        Used only as a labelled last resort when the tagged corpus has no
        occurrence for the verb itself, never as a substitute for it.
        """
        try:
            from services import quran_source
            provider = quran_source.get_islam360()
            if not provider.configured:
                return []
            out = []
            for record in provider.occurrences(root, limit=limit):
                out.append({
                    'verb_id': '',
                    'root': root,
                    'surah_number': record.get('surah_number'),
                    'ayah_number': record.get('ayah_number'),
                    'surah_name_arabic': record.get('surah_name_arabic', ''),
                    'surah_name_english': record.get('surah_name_english', ''),
                    'arabic_text': record.get('arabic_text', ''),
                    'highlighted_word': record.get('highlighted_word', ''),
                    'word_form': '',
                    'sigha_urdu': '',
                    'sigha_english': '',
                    'pronoun_arabic': '',
                    'form_certain': False,
                    'root_level': True,
                    'translation_urdu': record.get('translation_urdu', ''),
                    'translation_english': record.get('translation_english', ''),
                    'text_source': 'Islam360',
                    'source': 'Islam360',
                })
            return out
        except Exception:
            return []

    def quranic_usage_for(self, verb: dict) -> list:
        """This verb's own Quranic occurrences, with Islam360 text on top.

        Order of preference, most precise first: the curated occurrence data,
        then the tagged corpus entry for this exact (root, باب).  Both know the
        صیغہ.  Islam360's root-level listing is the labelled last resort.
        """
        root = verb.get('root', '')
        usage = self.get_quranic_usage(verb.get('id')) or []
        if not usage:
            entry = None
            try:
                entry = self.quran_index.get_by_root_baab(root,
                                                          verb.get('baab'))
            except Exception:
                entry = None
            if entry:
                usage = self.quranic_occurrences(entry)
        if usage:
            return self.islam360_enrich(usage, root)
        return self.islam360_occurrences(root)

    def islam360_lughaat(self, root: str) -> dict:
        """Islam360's own لغات (lexicon) article for a root."""
        try:
            from services import quran_source
            provider = quran_source.get_islam360()
            if not provider.configured:
                return {}
            return provider.grammar(root) or {}
        except Exception:
            return {}

    def quranic_occurrences(self, entry: dict) -> list:
        """Occurrences shaped like the existing Quranic section expects."""
        from .quran_index import describe_parse, PGN_UR, PGN_EN
        out = []
        for occ in entry.get('occurrences', []):
            out.append({
                'verb_id': 'q_%s_%s' % (entry.get('root', ''),
                                        entry.get('baab')),
                'root': entry.get('root_spaced', ''),
                'surah_number': occ.get('s'),
                'ayah_number': occ.get('a'),
                'surah_name_arabic': SURAH_NAMES.get(occ.get('s'), ''),
                'surah_name_english': '',
                'arabic_text': occ.get('text', ''),
                'highlighted_word': occ.get('w', ''),
                'word_form': occ.get('tense', ''),
                'sigha_urdu': describe_parse(occ, 'ur'),
                'sigha_english': describe_parse(occ, 'en'),
                'pronoun_arabic': '',
                'form_certain': True,
                'translation_urdu': '',
                'translation_english': '',
            })
        return out

    def _quranic_result(self, hits: list, cleaned: str, lang: str) -> dict:
        best = hits[0]
        entry = best['entry']
        record = self.quranic_to_record(entry)
        conj = self.conjugate(record) if record.get('present_3ms') \
            or record.get('past_3ms') else {k: [] for k in TENSE_ORDER}

        alternatives = []
        for h in hits[1:8]:
            alternatives.append(self.quranic_to_record(h['entry']))

        result = {
            'found': True,
            'verb': record,
            'query': cleaned,
            'conjugations': conj,
            'available_tenses': [t for t in TENSE_ORDER if conj.get(t)],
            'missing_tenses': [t for t in MANDATORY_TENSES if not conj.get(t)],
            'baab': self.get_baab_info(record['baab']),
            'root_info': self.get_root_info(record['root']),
            'afaal': self.get_afaal_for_root(record['root']),
            'quranic_usage': self.islam360_enrich(
                self.quranic_occurrences(entry), record['root']),
            'islam360_lughaat': self.islam360_lughaat(record['root']),
            'analysis_type': 'quran_index',
            'match_quality': best['match'],
            'confidence': 'high' if best['match'].endswith('exact') else 'medium',
            'is_conjugated_form': best['match'].startswith('surface'),
            'alternatives': alternatives,
            'source': 'quran_index',
            'quran_entry': entry,
        }
        if best.get('surface') and best.get('parse'):
            from .quran_index import describe_parse
            result['conjugated_info'] = {
                'input_word': cleaned,
                'base_verb': record['arabic'],
                'root': record['root'],
                'baab_name': record['baab_name_arabic'],
                'tense_urdu': describe_parse(best['parse'], 'ur'),
                'tense_english': describe_parse(best['parse'], 'en'),
                'sigha_urdu': describe_parse(best['parse'], 'ur'),
                'pronoun': '',
                'form': best['surface'],
            }
        return result

    def quranic_afaal_for_root(self, root: str) -> list:
        """Every Quranic verb of a root, grouped by باب."""
        bare = (root or '').replace(' ', '')
        try:
            return self.quran_index.by_root(bare)
        except Exception:
            return []

    def _conjugated_result(self, parsed: dict, cleaned: str) -> dict:
        verb = self._verbs_by_id.get(parsed['verb_id'], {})
        res = self._result(verb, cleaned, analysis_type='conjugated_form',
                           quality='exact')
        res['is_conjugated_form'] = True
        res['conjugated_info'] = parsed
        res['all_parses'] = parsed.get('all_parses', [])
        return res

    @staticmethod
    def _best_hit(hits: list) -> dict:
        """Prefer the bare Form I verb when several share a spelling."""
        return sorted(hits, key=lambda v: (v.get('baab', 1) != 1,
                                           v.get('baab', 1)))[0]

    def _result(self, verb: dict, query: str, analysis_type: str,
                quality: str = 'exact', alternatives=None) -> dict:
        conj = self.conjugate(verb)
        root = verb.get('root', '')
        return {
            'found': True,
            'verb': verb,
            'query': query,
            'conjugations': conj,
            'available_tenses': [t for t in TENSE_ORDER if conj.get(t)],
            'missing_tenses': [t for t in MANDATORY_TENSES if not conj.get(t)],
            'baab': self.get_baab_info(verb.get('baab', 1)),
            'root_info': self.get_root_info(root),
            'afaal': self.get_afaal_for_root(root),
            'quranic_usage': self.quranic_usage_for(verb),
            'islam360_lughaat': self.islam360_lughaat(root),
            'analysis_type': analysis_type,
            'match_quality': quality,
            'confidence': 'high' if quality in ('exact', 'vowelless') else 'medium',
            'is_conjugated_form': False,
            'alternatives': alternatives or [],
        }

    # ==================================================================
    # reverse parsing of an inflected word
    # ==================================================================
    def parse_conjugated(self, word: str, exact_only: bool = False) -> dict:
        """Identify tense / person / gender / number of an inflected form."""
        word = (word or '').strip()
        hits = self._form_index_exact.get(key_exact(word))
        if not hits and not exact_only:
            hits = (self._form_index_strict.get(key_strict(word))
                    or self._form_index_loose.get(key_loose(word)))
        if not hits:
            return {'found': False}

        parses = []
        for verb_id, tense, row in hits:
            verb = self._verbs_by_id.get(verb_id, {})
            parses.append({
                'verb_id': verb_id,
                'base_verb': verb.get('arabic', ''),
                'root': verb.get('root', ''),
                'baab': verb.get('baab'),
                'baab_name': verb.get('baab_name_arabic', ''),
                'wazn': verb.get('wazn', ''),
                'tense': tense,
                'tense_urdu': TENSE_LABELS[tense]['ur'],
                'tense_english': TENSE_LABELS[tense]['en'],
                'tense_arabic': TENSE_LABELS[tense]['ar'],
                'form': row.get('arabic'),
                'pronoun': row.get('pronoun_arabic'),
                'pronoun_urdu': row.get('pronoun_urdu'),
                'pronoun_english': row.get('pronoun_english'),
                'sigha_urdu': row.get('sigha_urdu'),
                'sigha_english': row.get('sigha_english'),
                'sigha_number': row.get('sigha_number'),
                'person': row.get('person'),
                'gender': row.get('gender'),
                'number': row.get('number'),
                'meaning_urdu': row.get('meaning_urdu'),
                'meaning_english': row.get('meaning_english'),
            })

        # most-canonical reading first: مندرجہ ذیل ترتیب — tense order, then صیغہ
        parses.sort(key=lambda p: (TENSE_ORDER.index(p['tense'])
                                   if p['tense'] in TENSE_ORDER else 99,
                                   p['sigha_number'] or 99))
        primary = dict(parses[0])
        primary['found'] = True
        primary['input_word'] = word
        primary['all_parses'] = parses
        primary['ambiguous'] = len(parses) > 1
        return primary

    def quick_analyze(self, word: str) -> dict:
        """Backward-compatible wrapper used by the quick-analysis banner."""
        parsed = self.parse_conjugated(word)
        if not parsed.get('found'):
            return {'found': False}
        person_ur = {1: 'متکلم (First person)', 2: 'حاضر (Second person)',
                     3: 'غائب (Third person)'}
        number_ur = {'singular': 'واحد (Singular)', 'dual': 'تثنیہ (Dual)',
                     'plural': 'جمع (Plural)'}
        gender_ur = {'masculine': 'مذکر (Masculine)',
                     'feminine': 'مؤنث (Feminine)',
                     'common': 'مذکر / مؤنث (Common)'}
        out = dict(parsed)
        out.update({
            'tense': parsed['tense_urdu'] + ' (%s)' % parsed['tense_english'],
            'tense_raw': parsed['tense'],
            'person': person_ur.get(parsed['person'], parsed['person']),
            'number': number_ur.get(parsed['number'], parsed['number']),
            'gender': gender_ur.get(parsed['gender'], parsed['gender']),
            'verb': self._verbs_by_id.get(parsed['verb_id'], {}),
        })
        return out

    # ==================================================================
    # lookups
    # ==================================================================
    def get_verb_by_id(self, verb_id: str) -> dict:
        return self._verbs_by_id.get(verb_id, {})

    def get_verb_by_arabic(self, arabic: str) -> dict:
        hits = self.search_engine.search_arabic(arabic)
        return self._best_hit(hits) if hits else {}

    def search_verbs(self, query: str, search_type: str = 'auto') -> list:
        return self.search_engine.search(query, search_type)

    def get_all_verbs(self) -> list:
        return self.verbs

    def get_quranic_usage(self, verb_id: str) -> list:
        return [q for q in self.quranic if q.get('verb_id') == verb_id]

    def get_root_info(self, root: str) -> dict:
        for r in self.roots:
            if r.get('root') == root:
                return r
        return {'root': root, 'root_letters': root.split(),
                'derived_words': [], 'related_verbs': []}

    def get_verb_forms_for_root(self, root: str) -> list:
        verbs = [v for v in self.verbs if v.get('root') == root]
        verbs.sort(key=lambda v: v.get('baab', 1))
        return verbs

    def get_afaal_for_root(self, root: str) -> list:
        """Every باب for this root: the verified verb, or an explicit gap.

        A باب with no attested verb for the root is reported as *absent* —
        the application never manufactures one.
        """
        present = {}
        for verb in self.get_verb_forms_for_root(root):
            present.setdefault(verb.get('baab', 1), []).append(verb)

        rows = []
        for form in ALL_BAAB_ORDER:
            baab = BAAB_INFO[form]
            if form == 9 and form not in present:
                continue                      # باب افعلال is only shown when used
            rows.append({
                'baab': form,
                'baab_info': baab,
                'verbs': present.get(form, []),
                'available': form in present,
            })
        return rows

    def get_baab_info(self, form) -> dict:
        return get_baab(form)

    def get_all_abwaab(self) -> list:
        return mazeed_abwaab()

    def get_verbs_by_baab(self, form) -> list:
        try:
            form = int(form)
        except (TypeError, ValueError):
            return []
        return [v for v in self.verbs if v.get('baab') == form]

    def get_baab_example_conjugation(self, form) -> dict:
        """Conjugate the وزن itself (فَعَلَ / فَعَّلَ …) for the ابواب page."""
        baab = get_baab(form)
        past, pres, pass_past, pass_pres = baab['principal_parts']
        pattern_verb = {
            'id': 'pattern_%s' % form,
            'arabic': past, 'past_3ms': past, 'present_3ms': pres,
            'past_passive_3ms': pass_past, 'present_passive_3ms': pass_pres,
            'baab': form, 'root': 'ف ع ل', 'root_letters': ['ف', 'ع', 'ل'],
            'meaning_urdu': 'وزن کی مثال', 'meaning_english': 'to do',
            'ur_stem': 'کر', 'ur_past': 'کیا',
            'en_base': 'do', 'en_past': 'did', 'en_pp': 'done',
        }
        if form == 1:
            pattern_verb['present_3ms'] = 'يَفْعُلُ'
        try:
            return self.conjugation_engine.conjugate_verb(pattern_verb)
        except ConjugationError:
            return {}

    def get_summary_rows(self, verbs: list) -> list:
        """Rows for the جدول view: باب | مادہ | the four principal parts."""
        rows = []
        na = message('not_applicable', 'ur')
        for verb in verbs:
            rows.append({
                'id': verb.get('id'),
                'arabic': verb.get('arabic'),
                'baab': verb.get('baab'),
                'baab_name': verb.get('baab_name_arabic'),
                'wazn': verb.get('wazn'),
                'root': verb.get('root'),
                'past_active': verb.get('past_3ms') or '—',
                'present_active': verb.get('present_3ms') or '—',
                'past_passive': verb.get('past_passive_3ms') or na,
                'present_passive': verb.get('present_passive_3ms') or na,
                'masdar': verb.get('masdar') or '—',
                'meaning_urdu': verb.get('meaning_urdu', ''),
                'meaning_english': verb.get('meaning_english', ''),
                'has_passive': verb.get('has_passive', False),
            })
        return rows

    def get_statistics(self) -> dict:
        return {
            'verbs': len(self.verbs),
            'roots': len(self.roots),
            'abwaab': len(sorted({v.get('baab') for v in self.verbs})),
            'quranic_occurrences': len(self.quranic),
            'total_forms': sum(len(rows)
                               for v in self.verbs
                               for rows in self.conjugate(v).values()),
        }

    # ==================================================================
    # user data (bookmarks, progress, flashcards)
    # ==================================================================
    def _init_db(self):
        with sqlite3.connect(self.db_path, check_same_thread=False) as conn:
            cur = conn.cursor()
            cur.execute('''CREATE TABLE IF NOT EXISTS bookmarks (
                    verb_id TEXT PRIMARY KEY,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
            cur.execute('''CREATE TABLE IF NOT EXISTS practice_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    verb_id TEXT, correct BOOLEAN, question_type TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
            cur.execute('''CREATE TABLE IF NOT EXISTS study_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, verb_id TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
            cur.execute('''CREATE TABLE IF NOT EXISTS flashcard_sm2 (
                    card_id TEXT PRIMARY KEY, verb_id TEXT NOT NULL,
                    card_type TEXT NOT NULL, easiness_factor REAL DEFAULT 2.5,
                    interval INTEGER DEFAULT 0, repetitions INTEGER DEFAULT 0,
                    next_review TEXT, last_review TEXT)''')
            conn.commit()

    def add_bookmark(self, verb_id: str) -> bool:
        if not verb_id:
            return False
        try:
            with sqlite3.connect(self.db_path, check_same_thread=False) as conn:
                conn.execute(
                    'INSERT OR IGNORE INTO bookmarks (verb_id) VALUES (?)',
                    (verb_id,))
                conn.commit()
            return True
        except sqlite3.Error:
            return False

    def remove_bookmark(self, verb_id: str) -> bool:
        try:
            with sqlite3.connect(self.db_path, check_same_thread=False) as conn:
                conn.execute('DELETE FROM bookmarks WHERE verb_id = ?',
                             (verb_id,))
                conn.commit()
            return True
        except sqlite3.Error:
            return False

    def get_bookmarks(self) -> list:
        try:
            with sqlite3.connect(self.db_path, check_same_thread=False) as conn:
                cur = conn.cursor()
                cur.execute(
                    'SELECT verb_id FROM bookmarks ORDER BY added_at DESC')
                return [row[0] for row in cur.fetchall()]
        except sqlite3.Error:
            return []

    def is_bookmarked(self, verb_id: str) -> bool:
        if not verb_id:
            return False
        try:
            with sqlite3.connect(self.db_path, check_same_thread=False) as conn:
                cur = conn.cursor()
                cur.execute('SELECT 1 FROM bookmarks WHERE verb_id = ?',
                            (verb_id,))
                return cur.fetchone() is not None
        except sqlite3.Error:
            return False

    def record_practice(self, verb_id: str, correct: bool, question_type: str):
        with sqlite3.connect(self.db_path, check_same_thread=False) as conn:
            conn.execute('INSERT INTO practice_history '
                         '(verb_id, correct, question_type) VALUES (?, ?, ?)',
                         (verb_id, correct, question_type))
            conn.commit()

    def get_progress(self) -> dict:
        with sqlite3.connect(self.db_path, check_same_thread=False) as conn:
            cur = conn.cursor()
            cur.execute('SELECT count(*) FROM practice_history')
            total = cur.fetchone()[0]
            cur.execute('SELECT count(*) FROM practice_history WHERE correct = 1')
            correct = cur.fetchone()[0]
        return {'total_attempts': total, 'correct_attempts': correct,
                'accuracy': (correct / total * 100) if total else 0}

    def get_practice_history(self, verb_id: str = None) -> list:
        with sqlite3.connect(self.db_path, check_same_thread=False) as conn:
            cur = conn.cursor()
            if verb_id:
                cur.execute('SELECT correct, question_type, timestamp '
                            'FROM practice_history WHERE verb_id = ?', (verb_id,))
            else:
                cur.execute('SELECT verb_id, correct, question_type, timestamp '
                            'FROM practice_history')
            return cur.fetchall()

    def get_study_stats(self) -> dict:
        with sqlite3.connect(self.db_path, check_same_thread=False) as conn:
            cur = conn.cursor()
            cur.execute('SELECT count(DISTINCT verb_id) FROM study_sessions')
            return {'unique_verbs_studied': cur.fetchone()[0]}

    def record_study(self, verb_id: str):
        if not verb_id:
            return
        with sqlite3.connect(self.db_path, check_same_thread=False) as conn:
            conn.execute('INSERT INTO study_sessions (verb_id) VALUES (?)',
                         (verb_id,))
            conn.commit()

    def get_recent_verbs(self, limit: int = 10) -> list:
        with sqlite3.connect(self.db_path, check_same_thread=False) as conn:
            cur = conn.cursor()
            cur.execute('SELECT verb_id, MAX(timestamp) AS t FROM study_sessions '
                        'GROUP BY verb_id ORDER BY t DESC LIMIT ?', (limit,))
            return [row[0] for row in cur.fetchall()]

    # -- SM-2 spaced repetition ----------------------------------------
    def get_sm2_card(self, card_id: str) -> dict:
        with sqlite3.connect(self.db_path, check_same_thread=False) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute('SELECT * FROM flashcard_sm2 WHERE card_id = ?',
                        (card_id,))
            row = cur.fetchone()
            return dict(row) if row else {}

    def update_sm2_card(self, card_id: str, verb_id: str, card_type: str,
                        quality: int) -> dict:
        card = self.get_sm2_card(card_id) or {
            'easiness_factor': 2.5, 'interval': 0, 'repetitions': 0}
        ef = card.get('easiness_factor', 2.5)
        interval = card.get('interval', 0)
        reps = card.get('repetitions', 0)

        if quality >= 3:
            interval = 1 if reps == 0 else (6 if reps == 1 else round(interval * ef))
            ef = max(1.3, ef + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))
            reps += 1
        else:
            reps, interval = 0, 1

        now = datetime.now()
        with sqlite3.connect(self.db_path, check_same_thread=False) as conn:
            conn.execute('''INSERT OR REPLACE INTO flashcard_sm2
                (card_id, verb_id, card_type, easiness_factor, interval,
                 repetitions, next_review, last_review)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                         (card_id, verb_id, card_type, ef, interval, reps,
                          (now + timedelta(days=interval)).isoformat(),
                          now.isoformat()))
            conn.commit()
        return self.get_sm2_card(card_id)

    def get_due_cards(self, limit: int = 20) -> list:
        now = datetime.now().isoformat()
        with sqlite3.connect(self.db_path, check_same_thread=False) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute('SELECT * FROM flashcard_sm2 WHERE next_review <= ? '
                        'ORDER BY next_review ASC LIMIT ?', (now, limit))
            cards = [dict(row) for row in cur.fetchall()]
        for card in cards:
            card['verb'] = self.get_verb_by_id(card['verb_id'])
        return cards

    def get_sm2_stats(self) -> dict:
        now = datetime.now().isoformat()
        with sqlite3.connect(self.db_path, check_same_thread=False) as conn:
            cur = conn.cursor()
            cur.execute('SELECT COUNT(*) FROM flashcard_sm2')
            total = cur.fetchone()[0]
            cur.execute('SELECT COUNT(*) FROM flashcard_sm2 WHERE next_review <= ?',
                        (now,))
            due = cur.fetchone()[0]
            cur.execute('SELECT AVG(easiness_factor) FROM flashcard_sm2')
            avg_ef = cur.fetchone()[0] or 2.5
        return {'total_cards': total, 'due_today': due,
                'average_ef': round(avg_ef, 2)}
