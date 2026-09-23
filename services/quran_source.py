# -*- coding: utf-8 -*-
"""Where Quranic information comes from — and whether it is Islam360-verified.

The specification requires Quranic references, verses, meanings and grammar to
be taken from **Islam360 only**, and requires the application to say so plainly
rather than substitute another source if Islam360 is unavailable.

Islam360 publishes no API.  What it does have is a Windows app, and where that
app is installed on the machine its data ships as XML, which
``data/build_islam360_index.py`` reads locally into
``data/islam360_index.json``:

* ``QuranComplete.xml``  — 6,349 ayaat: Islam360's Arabic text and its own Urdu
  and English translations, with its surah names
* ``RootWords.xml``      — 77,877 Quranic words tagged with Islam360's own root,
  and 2,284 لغات (lexicon) articles

So verification has two possible states, and the interface reports whichever is
true rather than assuming:

``CONNECTED``
    ``data/islam360_index.json`` is present.  Ayah text, translations, surah
    names, roots and لغات all come from Islam360.
``NOT CONNECTED``
    The index is absent — the app is not installed here, or the data was not
    built.  The application then falls back to its own corpus data **and says
    so**, labelled with its real provenance.  Nothing is ever presented as
    Islam360-verified when it is not.

**Licensing.** The index holds Islam360's copyrighted content.  It is built
locally and git-ignored on purpose: publishing it would be redistribution.  A
public deployment therefore runs in the NOT CONNECTED state unless the operator
has the right to ship that data.
"""

import json
import os
import re
from pathlib import Path

from core.quran_index import key_bare

#: Where the index lives by default — built locally, never committed.
DEFAULT_INDEX_PATH = (Path(__file__).parent.parent / 'data'
                      / 'islam360_index.json')

#: A deployment cannot use the committed file, because the file is
#: deliberately not committed.  An operator who holds the right to use
#: Islam360's data on their own server points at it with this, and the app
#: runs CONNECTED there without the data ever entering the repository::
#:
#:     ISLAM360_INDEX_PATH=/srv/private/islam360_index.json
#:
#: On Streamlit Cloud the same value can be set as a secret; anything absent
#: or unreadable simply leaves the app in its honest NOT CONNECTED state.
ENV_VAR = 'ISLAM360_INDEX_PATH'


#: A deployment that may not carry the file in git can fetch it at start-up
#: from a private location the operator controls — a private GitHub repo's
#: raw URL, a private Hugging Face dataset, a bucket — and cache it on disk::
#:
#:     ISLAM360_INDEX_URL=https://raw.githubusercontent.com/<you>/<private>/main/islam360_index.json
#:     ISLAM360_INDEX_TOKEN=<token that may read it>
#:
#: A ``.gz`` URL is decompressed.  Any failure — no network, wrong token,
#: bad JSON — leaves the app NOT CONNECTED and saying so; it never raises.
ENV_URL = 'ISLAM360_INDEX_URL'
ENV_TOKEN = 'ISLAM360_INDEX_TOKEN'

#: where a downloaded index is cached; the data folder if writable
_CACHE_CANDIDATES = (DEFAULT_INDEX_PATH,
                     Path(os.environ.get('TMPDIR') or os.environ.get('TEMP')
                          or '/tmp') / 'islam360_index.json')


def _setting(name: str) -> str:
    """An environment variable, or the same key in Streamlit secrets."""
    value = (os.environ.get(name) or '').strip()
    if not value:
        try:                                    # Streamlit secrets, if present
            import streamlit as st
            value = str(st.secrets.get(name, '') or '').strip()
        except Exception:
            value = ''
    return value


def _download_index(url: str, token: str = '') -> Path:
    """Fetch the index once into a cache file; return its path, or None."""
    for target in _CACHE_CANDIDATES:
        if target.exists() and target.stat().st_size > 0:
            return target
    import gzip
    import tempfile
    import urllib.request
    request = urllib.request.Request(url, headers={
        'User-Agent': 'quranic-arabic-analyzer',
        **({'Authorization': ('Bearer %s' % token)
            if 'huggingface' in url else ('token %s' % token)}
           if token else {}),
    })
    try:
        with urllib.request.urlopen(request, timeout=120) as resp:
            raw = resp.read()
            gz = (url.lower().endswith('.gz')
                  or 'gzip' in (resp.headers.get('Content-Encoding') or '')
                  or raw[:2] == b'\x1f\x8b')
        if gz:
            raw = gzip.decompress(raw)
        json.loads(raw.decode('utf-8'))            # must be the real thing
    except Exception:
        return None
    for target in _CACHE_CANDIDATES:
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            fd, tmp = tempfile.mkstemp(dir=str(target.parent), suffix='.part')
            with os.fdopen(fd, 'wb') as fh:
                fh.write(raw)
            os.replace(tmp, target)                # atomic: never a half file
            return target
        except OSError:
            continue
    return None


def _configured_path() -> Path:
    """The index location, in order of preference: a path the operator
    named, a URL the operator named (downloaded and cached), the default."""
    override = _setting(ENV_VAR)
    if override:
        return Path(override)
    if not DEFAULT_INDEX_PATH.exists():
        url = _setting(ENV_URL)
        if url:
            fetched = _download_index(url, _setting(ENV_TOKEN))
            if fetched:
                return fetched
    return DEFAULT_INDEX_PATH


#: kept for callers that import it by name
INDEX_PATH = DEFAULT_INDEX_PATH


def _weak_final_variant(root_key: str):
    """The other analysis of a defective root, or None.

    Lexicographers legitimately disagree on the final radical of a ناقص root:
    the corpus has ندي where Islam360 has ن د و, رضو against ر ض ي.  Only the
    *final* radical is folded — the middle one distinguishes real roots
    (قول/قيل, دون/دين, طور/طير) and is never touched.
    """
    if len(root_key) == 3 and root_key[-1] in 'وي':
        return root_key[:-1] + ('ي' if root_key[-1] == 'و' else 'و')
    return None


class Islam360NotConfigured(RuntimeError):
    """Raised when Islam360 data is requested but no access is configured."""


class QuranSource:
    """The interface every Quran data provider implements."""

    name = 'unknown'
    islam360_verified = False

    def ayah(self, surah: int, ayah: int) -> dict:
        raise NotImplementedError

    def occurrences(self, root: str, baab=None) -> list:
        raise NotImplementedError

    def grammar(self, root: str) -> dict:
        raise NotImplementedError

    def status(self) -> dict:
        return {'name': self.name, 'islam360_verified': self.islam360_verified}


class Islam360Provider(QuranSource):
    """Islam360, read from the locally installed app's own data."""

    name = 'Islam360'
    islam360_verified = True

    def __init__(self, index_path: Path = None):
        self.index_path = Path(index_path) if index_path else _configured_path()
        self._data = None
        self._roots_by_key = None

    # -- loading --------------------------------------------------------
    @property
    def configured(self) -> bool:
        return self.index_path.exists()

    @property
    def data(self) -> dict:
        if self._data is None:
            if not self.configured:
                raise Islam360NotConfigured(BLOCKED_REASON)
            try:
                self._data = json.loads(
                    self.index_path.read_text(encoding='utf-8'))
            except (json.JSONDecodeError, OSError) as exc:
                raise Islam360NotConfigured(
                    'Islam360 index could not be read: %s' % exc)
        return self._data

    # -- queries --------------------------------------------------------
    #: Islam360's mushaf text carries the printed رکوع marker — a lone
    #: trailing digit (Arabic-Indic or Latin) that is typography, not part of
    #: the ayah.  It is dropped for display; nothing else in the text is
    #: touched.
    _RUKU_MARKER = re.compile(r'[\s۝]*[0-9٠-٩۰-۹]+\s*$')

    #: Islam360 names a surah «سورة الحجر»; the corpus names it «الحجر», and
    #: every renderer already writes the word «سورۃ» itself.  Strip the
    #: prefix so both sources hand back the same bare name and no caller
    #: prints it twice.
    _SURAH_PREFIX = re.compile(r'^\s*سور[ةهۃ]\s+')

    #: Islam360's English names are «Surat-ul-Baqara», «Surat-ut-Toor»; the
    #: renderer writes the word «Surah» itself, so only the name is kept.
    _SURAH_PREFIX_EN = re.compile(
        r'^\s*Surat?[-\s]+(?:u[ltnsrzd]{1,2}|a[ltnsrzd]{1,2})?[-\s]*',
        re.IGNORECASE)

    @staticmethod
    def _keys(surah, ayah) -> list:
        """Islam360's record key(s) for a standard (Kufi) surah:ayah.

        Islam360 keeps بسم الله as record ``n:0`` of every surah, and divides
        Al-Fatiha differently from the standard count: its 1:1 is الحمد, so
        standard 1:2‥1:6 are its 1:1‥1:5, standard 1:1 is its 1:0, and the
        standard 1:7 «صراط الذين … ولا الضالين» is split across its 1:6 and
        1:7.  Every other surah is numbered identically (checked: 2:286 and
        114:6 exist, 2:287 and 114:7 do not).
        """
        surah, ayah = int(surah), int(ayah)
        if surah != 1:
            return ['%s:%s' % (surah, ayah)]
        if ayah == 1:
            return ['1:0']
        if ayah == 7:
            return ['1:6', '1:7']
        return ['1:%s' % (ayah - 1)]

    def ayah(self, surah, ayah) -> dict:
        """Islam360's own text and translations for one (standard) ayah."""
        ayat = self.data.get('ayat', {})
        records = [ayat[k] for k in self._keys(surah, ayah) if k in ayat]
        if not records:
            return {}
        joined = lambda field: ' '.join(                          # noqa: E731
            r.get(field, '') for r in records if r.get(field))
        first = records[0]
        return {
            'arabic_text': ' '.join(self._RUKU_MARKER.sub('', r.get('ar', ''))
                                    for r in records),
            'translation_urdu': joined('ur'),
            'translation_english': joined('en'),
            'surah_name_arabic': self._SURAH_PREFIX.sub(
                '', first.get('surah_ur', '')),
            'surah_name_english': self._SURAH_PREFIX_EN.sub(
                '', first.get('surah_en', '')),
            'surah_number': surah,
            'ayah_number': ayah,
            'source': 'Islam360',
        }

    @property
    def _root_lookup(self) -> dict:
        """Folded comparison key -> Islam360's own spelling of the root.

        Islam360 writes «ھ د ي» where the corpus writes «هدي», and keeps a
        particle like لَــــیْسَ as its own root, harakat and tatweel and
        all.  Comparing folded keys makes those one root, as they are.
        """
        if self._roots_by_key is None:
            lookup = {}
            for root in self.data.get('roots', {}):
                lookup.setdefault(key_bare(root), root)
            self._roots_by_key = lookup
        return self._roots_by_key

    def root_entry(self, root: str) -> dict:
        """Islam360's record for a root: its Quranic words and its لغات."""
        roots = self.data.get('roots', {})
        if root in roots:
            return roots[root]
        key = key_bare(root or '')
        real = self._root_lookup.get(key)
        if real is None:
            variant = _weak_final_variant(key)
            real = self._root_lookup.get(variant) if variant else None
        return roots.get(real, {}) if real else {}

    def confirm(self, surah, ayah, word: str, root: str) -> dict:
        """Does Islam360 list this word, at this ayah, under this root?

        The exact check the specification asks for, made against Islam360's
        own per-ayah tagging rather than a sampled list.  Three answers, each
        true only when Islam360 actually says so:

        ``ayah``  Islam360 has the ayah at all
        ``root``  Islam360 assigns this root to some word of that ayah
        ``word``  Islam360 assigns this root to *this* word there
        ``word_other_root``  the word is there, under a different root
        """
        table = self.data.get('ayah_words', {})
        aw = {}
        for key in self._keys(surah, ayah):
            aw.update(table.get(key, {}))
        if not aw:
            return {'ayah': False, 'root': False, 'word': False}
        rk, wk = key_bare(root or ''), key_bare(word or '')
        alt = _weak_final_variant(rk)
        root_hit = word_hit = word_seen = False
        for w, roots in aw.items():
            # Islam360 writes a clitic-bearing word's root segmented,
            # «صفو|ک» for ٱصْطَفَىٰكِ — each segment is a candidate root
            keys = [key_bare(part) for r in roots for part in r.split('|')]
            same_word = key_bare(w) == wk
            word_seen = word_seen or same_word
            if rk in keys:
                root_hit = True
                if same_word:
                    word_hit = True
            elif alt and alt in keys and same_word:
                # the same word, at the same place, under the other analysis
                # of a defective root — that is one root, not two
                root_hit = word_hit = True
        return {'ayah': True, 'root': root_hit, 'word': word_hit,
                # Islam360 has the word at this ayah but analyses its root
                # differently (a quadriliteral like طمأن read as ط م ن);
                # the reference is confirmed, the root analysis is not
                'word_other_root': word_seen and not word_hit}

    def occurrences(self, root: str, baab=None, limit: int = 8) -> list:
        """Where the words of this root occur, with Islam360's ayah text."""
        entry = self.root_entry(root)
        if not entry:
            return []
        out = []
        for word, places in entry.get('words', {}).items():
            for surah, ayah in places:
                record = self.ayah(surah, ayah)
                if not record:
                    continue
                record['highlighted_word'] = word
                out.append(record)
                if len(out) >= limit:
                    return out
        return out

    def grammar(self, root: str) -> dict:
        """Islam360's لغات article for a root."""
        entry = self.root_entry(root)
        return {'lughaat': entry.get('lughaat', ''),
                'word_count': len(entry.get('words', {})),
                'source': 'Islam360'} if entry else {}

    def roots_for_word(self, word_key: str) -> list:
        return self.data.get('words', {}).get(key_bare(word_key or ''), [])

    def status(self) -> dict:
        if not self.configured:
            return {'name': self.name, 'islam360_verified': False}
        meta = self.data.get('meta', {})
        return {
            'name': self.name,
            'islam360_verified': True,
            'origin': ('downloaded' if self.index_path != DEFAULT_INDEX_PATH
                       or _setting(ENV_URL) else 'local'),
            'ayat': meta.get('ayat'),
            'roots': meta.get('roots'),
            'word_entries': meta.get('word_entries'),
            'package': meta.get('package', ''),
        }


class LocalCorpusProvider(QuranSource):
    """The fallback, labelled truthfully — used only when Islam360 is absent."""

    name = 'Quranic Arabic Corpus (grammar) + Tanzil (text)'
    islam360_verified = False

    SOURCES = {
        'grammar': 'Quranic Arabic Corpus — tagged morphology',
        'text': 'Tanzil uthmani',
        'translation_urdu': 'Fateh Muhammad Jalandhry',
        'translation_english': 'Sahih International',
    }

    #: the same list in the reader's language — a source named in a
    #: script they cannot read tells them nothing
    SOURCES_BY_LANG = {
        'en': {'Grammar': 'Quranic Arabic Corpus (tagged morphology)',
               'Verse text': 'Tanzil (Uthmani)',
               'Urdu translation': 'Fateh Muhammad Jalandhry',
               'English translation': 'Sahih International'},
        'ur': {'صرفی تجزیہ': 'قرآنی عربی کارپس',
               'آیات کا متن': 'تنزیل (عثمانی رسم)',
               'اردو ترجمہ': 'فتح محمد جالندھری',
               'انگریزی ترجمہ': 'صحیح انٹرنیشنل'},
        'ar': {'التحليل الصرفي': 'مدوّنة القرآن العربية',
               'نص الآيات': 'تنزيل (الرسم العثماني)',
               'الترجمة الأردية': 'فتح محمد جالندهري',
               'الترجمة الإنجليزية': 'صحيح إنترناشيونال'},
    }

    def sources(self, lang: str = 'ur') -> dict:
        return self.SOURCES_BY_LANG.get(lang) or self.SOURCES_BY_LANG['ur']

    def status(self) -> dict:
        return {'name': self.name, 'islam360_verified': False,
                'sources': self.SOURCES}


BLOCKED_REASON = (
    'Islam360 verification is blocked because authorized Islam360 data/API '
    'access is not available in the current environment.')

ISLAM360_BLOCKED_MESSAGE = {
    'ur': ('اسلام۳۶۰ سے تصدیق نہیں کی جا سکی — اس ماحول میں اسلام۳۶۰ کے مستند '
           'ڈیٹا تک رسائی دستیاب نہیں۔ ذیل کی قرآنی معلومات کے اصل مآخذ نیچے '
           'درج ہیں۔'),
    'en': (BLOCKED_REASON + ' The actual source of the Quranic material shown '
           'is listed below.'),
    'ar': ('تعذّر التحقق من إسلام360 لعدم توفر وصول مصرّح به إلى بياناته في '
           'هذه البيئة. المصادر الفعلية مذكورة أدناه.'),
}

ISLAM360_OK_MESSAGE = {
    'ur': 'قرآنی معلومات اسلام۳۶۰ سے لی گئی ہیں (اسی کمپیوٹر پر نصب ایپ سے)۔',
    'en': 'Quranic material verified against Islam360 (the app installed on '
          'this computer).',
    'ar': 'المعلومات القرآنية مأخوذة من إسلام360 المثبّت على هذا الجهاز.',
}


def _pick_active():
    provider = Islam360Provider()
    return provider if provider.configured else LocalCorpusProvider()


#: the provider in use — Islam360 when its data is present, else the fallback
ACTIVE = _pick_active()


def refresh():
    """Re-check for the Islam360 index (used after building it)."""
    global ACTIVE
    ACTIVE = _pick_active()
    return ACTIVE


def get_islam360():
    """The Islam360 provider, whether or not it is currently configured."""
    return ACTIVE if isinstance(ACTIVE, Islam360Provider) else Islam360Provider()


def verification_status(lang: str = 'ur') -> dict:
    """What the interface should display about Quranic provenance."""
    active = ACTIVE
    verified = bool(getattr(active, 'islam360_verified', False)
                    and getattr(active, 'configured', False))
    status = {
        'islam360_verified': verified,
        'islam360_configured': verified,
        'active_source': active.name,
        'sources': (active.sources(lang) if hasattr(active, 'sources')
                    else getattr(active, 'SOURCES', {})),
        'blocked_message': ISLAM360_BLOCKED_MESSAGE.get(
            lang, ISLAM360_BLOCKED_MESSAGE['ur']),
        'ok_message': ISLAM360_OK_MESSAGE.get(lang, ISLAM360_OK_MESSAGE['ur']),
    }
    if verified:
        status.update(active.status())
    return status
