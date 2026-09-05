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


def _configured_path() -> Path:
    """The index location: the operator's if they named one, else the default."""
    override = (os.environ.get(ENV_VAR) or '').strip()
    if not override:
        try:                                    # Streamlit secrets, if present
            import streamlit as st
            override = str(st.secrets.get(ENV_VAR, '') or '').strip()
        except Exception:
            override = ''
    return Path(override) if override else DEFAULT_INDEX_PATH


#: kept for callers that import it by name
INDEX_PATH = DEFAULT_INDEX_PATH


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

    def ayah(self, surah, ayah) -> dict:
        """Islam360's own text and translations for one ayah."""
        record = self.data.get('ayat', {}).get('%s:%s' % (surah, ayah))
        if not record:
            return {}
        return {
            'arabic_text': self._RUKU_MARKER.sub('', record.get('ar', '')),
            'translation_urdu': record.get('ur', ''),
            'translation_english': record.get('en', ''),
            'surah_name_arabic': self._SURAH_PREFIX.sub(
                '', record.get('surah_ur', '')),
            'surah_name_english': record.get('surah_en', ''),
            'surah_number': surah,
            'ayah_number': ayah,
            'source': 'Islam360',
        }

    def root_entry(self, root: str) -> dict:
        """Islam360's record for a root: its Quranic words and its لغات."""
        roots = self.data.get('roots', {})
        if root in roots:
            return roots[root]
        # tolerate spacing differences between «ن ز ل» and «نزل»
        squashed = (root or '').replace(' ', '')
        for key, value in roots.items():
            if key.replace(' ', '') == squashed:
                return value
        return {}

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
        return self.data.get('words', {}).get(word_key, [])

    def status(self) -> dict:
        if not self.configured:
            return {'name': self.name, 'islam360_verified': False}
        meta = self.data.get('meta', {})
        return {
            'name': self.name,
            'islam360_verified': True,
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
        'sources': getattr(active, 'SOURCES', {}),
        'blocked_message': ISLAM360_BLOCKED_MESSAGE.get(
            lang, ISLAM360_BLOCKED_MESSAGE['ur']),
        'ok_message': ISLAM360_OK_MESSAGE.get(lang, ISLAM360_OK_MESSAGE['ur']),
    }
    if verified:
        status.update(active.status())
    return status
