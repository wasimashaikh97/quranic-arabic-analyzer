# -*- coding: utf-8 -*-
"""Build the Islam360 index from the locally installed Islam360 app.

The specification requires Quranic references, verses, meanings and grammar to
come from **Islam360 only**.  Islam360 has no public API, but the Windows app
installed on this machine ships its data as XML, and reading it locally is a
legitimate way to satisfy that requirement.

Source (read-only, never modified)::

    C:\\Program Files\\WindowsApps\\48071ZahidHussainChihpa.Islam360Universal_…
        XmlFiles\\RootWords.xml       77,877 words: root, word, surah, ayah, لغات
        XmlFiles\\QuranComplete.xml    6,236 ayaat: Arabic, Urdu, English, names

Output — ``data/islam360_index.json``::

    {
      "meta":  {...source, version, counts...},
      "ayat":  {"2:255": {"ar": …, "ur": …, "en": …, "surah_ur": …}},
      "roots": {"ن ز ل": {"words": {"أَنْزَلَ": [[2,4], …]}, "lughaat": "…"}},
      "words": {"انزل": ["ن ز ل"]}
    }

**Licensing.** This is Islam360's copyrighted content.  The index is written
for local use and is **git-ignored on purpose** — publishing it would be
redistribution.  The application degrades gracefully when it is absent: it
falls back to its own corpus data and says so, rather than pretending to have
Islam360 verification it does not have.

Usage::

    python data/build_islam360_index.py
"""

import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from core.arabic_utils import normalise_letters, strip_marks    # noqa: E402

PACKAGE = ('48071ZahidHussainChihpa.Islam360Universal'
           '_1.1.0.23_x64__8x13y3kbk4qr2')
DEFAULT_XML = Path('C:/Program Files/WindowsApps') / PACKAGE / 'XmlFiles'

OUT = ROOT_DIR / 'data' / 'islam360_index.json'

#: لغات entries are long Urdu lexicon articles; keep them readable
MAX_LUGHAAT = 1800


def find_xml_dir() -> Path:
    """Locate the installed app, allowing for a different version number."""
    if DEFAULT_XML.exists():
        return DEFAULT_XML
    base = Path('C:/Program Files/WindowsApps')
    if base.exists():
        for child in base.glob('*Islam360Universal*'):
            candidate = child / 'XmlFiles'
            if candidate.exists():
                return candidate
    raise SystemExit(
        'Islam360 XML data not found. Install the Islam360 Universal app, or '
        'pass the XmlFiles folder path as the first argument.')


def key_word(text: str) -> str:
    return normalise_letters(strip_marks(text or '')).replace(' ', '').strip()


def clean(text: str) -> str:
    return re.sub(r'\s+', ' ', (text or '').strip())


# ---------------------------------------------------------------------------
def read_ayat(xml_dir: Path) -> dict:
    """(surah:ayah) -> Islam360's Arabic text and its own translations."""
    out = {}
    path = xml_dir / 'QuranComplete.xml'
    for _ev, el in ET.iterparse(str(path), events=('end',)):
        if el.tag != 'Quran':
            continue
        get = lambda t: clean(el.findtext(t) or '')      # noqa: E731
        surah, ayah = get('surat_id'), get('ayat_number')
        if surah and ayah:
            out['%s:%s' % (surah, ayah)] = {
                'ar': get('arabic'),
                'ur': get('translation_urdu'),
                'en': get('translation_english'),
                'surah_ur': get('surat_name_urdu'),
                'surah_en': get('surat_name_english'),
            }
        el.clear()
    return out


def read_roots(xml_dir: Path):
    """Islam360's own root for every Quranic word, plus its لغات notes."""
    roots = defaultdict(lambda: {'words': defaultdict(list), 'lughaat': ''})
    words = defaultdict(set)
    total = 0
    path = xml_dir / 'RootWords.xml'
    for _ev, el in ET.iterparse(str(path), events=('end',)):
        if el.tag != 'RootWord':
            continue
        total += 1
        root = clean(el.findtext('Root') or '')
        word = clean(el.findtext('Arabic_Word') or '')
        surah = clean(el.findtext('Surat_ID') or '')
        ayah = clean(el.findtext('Aayat') or '')
        lughaat = clean(el.findtext('Lughaat') or '')
        el.clear()

        if not root or not word:
            continue
        entry = roots[root]
        if surah and ayah:
            occ = [int(surah), int(ayah)]
            bucket = entry['words'][word]
            if len(bucket) < 12 and occ not in bucket:
                bucket.append(occ)
        else:
            entry['words'].setdefault(word, [])
        # the لغات article is attached to a root's first occurrence
        if lughaat and not entry['lughaat']:
            entry['lughaat'] = lughaat[:MAX_LUGHAAT]
        words[key_word(word)].add(root)
    return roots, words, total


# ---------------------------------------------------------------------------
def main() -> int:
    xml_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else find_xml_dir()
    print('Islam360 data: %s' % xml_dir)

    print('  reading QuranComplete.xml ...')
    ayat = read_ayat(xml_dir)
    print('    %d ayaat' % len(ayat))

    print('  reading RootWords.xml ...')
    roots, words, total = read_roots(xml_dir)
    print('    %d word entries, %d distinct roots' % (total, len(roots)))

    payload = {
        'meta': {
            'source': 'Islam360 Universal (locally installed app)',
            'package': PACKAGE,
            'xml_dir': str(xml_dir),
            'islam360_verified': True,
            'ayat': len(ayat),
            'roots': len(roots),
            'word_entries': total,
            'note': ('Islam360 copyrighted content, indexed locally for this '
                     'installation. Not redistributed.'),
        },
        'ayat': ayat,
        'roots': {r: {'words': dict(v['words']), 'lughaat': v['lughaat']}
                  for r, v in roots.items()},
        'words': {k: sorted(v) for k, v in words.items()},
    }

    OUT.write_text(json.dumps(payload, ensure_ascii=False), encoding='utf-8')
    with_lughaat = sum(1 for v in roots.values() if v['lughaat'])
    print()
    print('wrote %s' % OUT.name)
    print('  ayaat            : %d' % len(ayat))
    print('  roots            : %d  (%d with لغات)' % (len(roots), with_lughaat))
    print('  distinct words   : %d' % len(words))
    print('  size             : %.1f MB' % (OUT.stat().st_size / 1e6))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
