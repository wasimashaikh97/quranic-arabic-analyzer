# -*- coding: utf-8 -*-
"""Where Quranic information comes from — and whether it is Islam360-verified.

The specification requires that Quranic references, meanings and grammar be
taken from **Islam360 only**, and that if authorized Islam360 access is not
available the application must say so rather than quietly substitute another
source or invent data.

Current status: **NOT CONNECTED.**

What was actually checked, on this machine, at build time:

===========================  =========================================
``islam360.com``             responds, but serves a domain-parking page
                             ("ISLAM360.COM MAY BE AVAILABLE!") — it is
                             not the app's site and carries no data
``islam360.pk``              connection times out from this network
``api.islam360.pk``          DNS does not resolve
``quran.islam360.pk``        DNS does not resolve
===========================  =========================================

There is no public, documented Islam360 data API, and no authorized dataset
or credentials were supplied.  So :class:`Islam360Provider` is present and
wired, but deliberately unimplemented: asking it for data raises
:class:`Islam360NotConfigured` instead of returning something invented.

Meanwhile the Quranic material the application does show is labelled with its
real provenance, never as Islam360:

* **grammar** (root, باب, tense, voice, person/gender/number, and which forms
  actually occur) — Quranic Arabic Corpus tagged morphology;
* **ayah text** — Tanzil uthmani;
* **translations** — Jalandhry (Urdu), Sahih International (English).

To connect Islam360 later, implement the three methods of
:class:`Islam360Provider` and set ``ACTIVE = Islam360Provider(...)``.  Nothing
else in the application needs to change: it asks this module for the source
label and the verification status, and renders whatever it is told.
"""


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

    def grammar(self, surah: int, ayah: int, word: int) -> dict:
        raise NotImplementedError

    def status(self) -> dict:
        return {'name': self.name, 'islam360_verified': self.islam360_verified}


class Islam360Provider(QuranSource):
    """Islam360 — required by the specification, not reachable here.

    Left deliberately unimplemented.  Returning data from anywhere else while
    calling it Islam360 would be exactly the mislabelling the specification
    forbids, so every method raises instead.
    """

    name = 'Islam360'
    islam360_verified = True

    #: what was probed, so the claim in the interface is checkable
    PROBED = {
        'islam360.com': 'domain-parking page, no data',
        'islam360.pk': 'connection timed out',
        'api.islam360.pk': 'DNS does not resolve',
        'quran.islam360.pk': 'DNS does not resolve',
    }

    def __init__(self, api_key: str = None, base_url: str = None,
                 dataset_path: str = None):
        self.api_key = api_key
        self.base_url = base_url
        self.dataset_path = dataset_path

    @property
    def configured(self) -> bool:
        return bool(self.api_key or self.dataset_path)

    def _require(self):
        raise Islam360NotConfigured(
            'Islam360 verification is blocked because authorized Islam360 '
            'data/API access is not available in the current environment.')

    def ayah(self, surah, ayah):
        self._require()

    def occurrences(self, root, baab=None):
        self._require()

    def grammar(self, surah, ayah, word):
        self._require()


class LocalCorpusProvider(QuranSource):
    """What the application actually ships with, labelled truthfully."""

    name = 'Quranic Arabic Corpus (grammar) + Tanzil (text)'
    islam360_verified = False

    SOURCES = {
        'grammar': 'Quranic Arabic Corpus — tagged morphology',
        'text': 'Tanzil uthmani',
        'translation_urdu': 'Fateh Muhammad Jalandhry',
        'translation_english': 'Sahih International',
    }

    def status(self) -> dict:
        return {
            'name': self.name,
            'islam360_verified': False,
            'sources': self.SOURCES,
        }


#: the provider in use.  Swap in a configured Islam360Provider to switch.
ACTIVE = LocalCorpusProvider()

ISLAM360_BLOCKED_MESSAGE = {
    'ur': ('اسلام۳۶۰ سے تصدیق نہیں کی جا سکی — اس ماحول میں اسلام۳۶۰ کے مستند '
           'ڈیٹا یا API تک رسائی دستیاب نہیں۔ ذیل کی قرآنی معلومات کے اصل '
           'مآخذ نیچے درج ہیں۔'),
    'en': ('Islam360 verification is blocked because authorized Islam360 '
           'data/API access is not available in the current environment. '
           'The actual source of the Quranic material shown is listed below.'),
    'ar': ('تعذّر التحقق من إسلام360 لعدم توفر وصول مصرّح به إلى بياناته في '
           'هذه البيئة. المصادر الفعلية مذكورة أدناه.'),
}


def verification_status(lang: str = 'ur') -> dict:
    """What the interface should display about Quranic provenance."""
    active = ACTIVE
    islam360 = Islam360Provider()
    return {
        'islam360_verified': bool(getattr(active, 'islam360_verified', False)
                                  and getattr(active, 'configured', False)),
        'islam360_configured': islam360.configured,
        'blocked_message': ISLAM360_BLOCKED_MESSAGE.get(
            lang, ISLAM360_BLOCKED_MESSAGE['ur']),
        'active_source': active.name,
        'sources': getattr(active, 'SOURCES', {}),
        'probed': Islam360Provider.PROBED,
    }
