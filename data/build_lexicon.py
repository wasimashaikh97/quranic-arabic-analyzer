# -*- coding: utf-8 -*-
"""Build ``data/verbs.json`` and ``data/roots.json`` from ``data/lexicon.py``.

Run it after editing the lexicon::

    python data/build_lexicon.py

The generated data model is hierarchical, exactly as the application needs it:

    ROOT → VERBS → BAAB → WAZN → 4 principal parts → GARDAAN → DERIVATIVES
                                                   → MEANINGS → QURANIC REFS

The 68 inflected forms of each verb are *not* stored; they are produced on
demand by ``core.conjugation`` from the verified principal parts, so there is
exactly one place where a form can be right or wrong.
"""

import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from core.abwaab import get_baab                                # noqa: E402
from core.morphology import ArabicMorphology                    # noqa: E402
from data.lexicon import LEXICON, ROOT_INFO, LAZIM              # noqa: E402


def build_verb(entry: dict) -> dict:
    root_letters = entry['root'].split()
    baab = get_baab(entry['baab'])
    vtype = entry.get('vtype') or ArabicMorphology.identify_verb_type(root_letters)

    derived = {}
    if entry.get('masdar'):
        derived['masdar'] = {
            'arabic': entry['masdar'],
            'pattern': baab['masdar_pattern'],
            'label_ur': 'مصدر', 'label_en': 'Verbal noun (Masdar)',
            'meaning_urdu': entry['ur'],
            'meaning_english': 'to ' + entry['en'],
        }
    if entry.get('masdar2'):
        derived['masdar_thani'] = {
            'arabic': entry['masdar2'],
            'pattern': baab['masdar_pattern'],
            'label_ur': 'مصدر (دوسرا)', 'label_en': 'Second Masdar',
            'meaning_urdu': entry['ur'],
            'meaning_english': 'to ' + entry['en'],
        }
    if entry.get('fail'):
        derived['ism_fail'] = {
            'arabic': entry['fail'],
            'pattern': baab['ism_fail_pattern'],
            'label_ur': 'اسم فاعل', 'label_en': "Active participle (Ism Fa'il)",
            'meaning_urdu': entry['ur_stem'] + 'نے والا',
            'meaning_english': 'the one who %ss' % entry['en']
                               if not entry['en'].endswith('s') else
                               'the one who %s' % entry['en'],
        }
    if entry.get('mafool'):
        derived['ism_mafool'] = {
            'arabic': entry['mafool'],
            'pattern': baab['ism_mafool_pattern'],
            'label_ur': 'اسم مفعول', 'label_en': "Passive participle (Ism Maf'ool)",
            'meaning_urdu': entry['ur_past'] + ' ہوا',
            'meaning_english': entry['en_pp'],
        }

    has_passive = bool(entry.get('pass_past'))

    return {
        'id': entry['id'],
        'arabic': entry['ar'],
        'root': entry['root'],
        'root_letters': root_letters,

        # --- باب / وزن ----------------------------------------------------
        'baab': entry['baab'],
        'form': entry['baab'],                      # legacy alias
        'baab_name_arabic': baab['name_ar'],
        'baab_name_urdu': baab['name_ur'],
        'baab_name_english': baab['name_en'],
        'baab_category_urdu': baab['category_ur'],
        'is_mazeed': baab['is_mazeed'],
        'wazn': baab['wazn_past'],
        'pattern': baab['wazn_past'],               # legacy alias
        'form_name_arabic': baab['wazn_past'],      # legacy alias
        'wazn_present': baab['wazn_present'],
        'wazn_past_passive': baab['wazn_past_passive'],
        'wazn_present_passive': baab['wazn_present_passive'],

        # --- the four verified principal parts ---------------------------
        'past_3ms': entry['ar'],
        'present_3ms': entry['pres'],
        'past_passive_3ms': entry.get('pass_past'),
        'present_passive_3ms': entry.get('pass_pres'),
        'past_short_stem': entry.get('past_short'),
        'past_passive_short_stem': entry.get('pass_past_short'),
        'imperative_forms': entry.get('imp'),
        'has_passive': has_passive,
        'unavailable_note': entry.get('note'),

        # --- classification ---------------------------------------------
        'verb_type': vtype,
        'transitivity': entry.get('trans'),
        'is_transitive': entry.get('trans') != LAZIM,

        # --- meanings ----------------------------------------------------
        'meaning_urdu': entry['ur'],
        'meaning_english': 'to ' + entry['en'],
        'ur_stem': entry['ur_stem'],
        'ur_past': entry['ur_past'],
        'en_base': entry['en'],
        'en_past': entry['en_past'],
        'en_pp': entry['en_pp'],

        # --- derivatives -------------------------------------------------
        'masdar': entry['masdar'],
        'masdar_pattern': baab['masdar_pattern'],
        'ism_fail': entry.get('fail'),
        'ism_mafool': entry.get('mafool'),
        'derived_nouns': derived,
    }


def build_roots(verbs: list) -> list:
    by_root = {}
    for v in verbs:
        by_root.setdefault(v['root'], []).append(v)

    roots = []
    for root, group in by_root.items():
        group.sort(key=lambda v: v['baab'])
        info = ROOT_INFO.get(root, {})
        words = [
            {'arabic': w[0], 'meaning_urdu': w[1], 'meaning_english': w[2],
             'type': w[3]}
            for w in info.get('words', [])
        ]
        roots.append({
            'root': root,
            'root_letters': root.split(),
            'basic_meaning_arabic': info.get('ar', ''),
            'basic_meaning_urdu': info.get('ur', group[0]['meaning_urdu']),
            'basic_meaning_english': info.get('en',
                                              group[0]['meaning_english']),
            'root_type': group[0]['verb_type'],
            'related_verbs': [v['id'] for v in group],
            'abwaab_present': sorted({v['baab'] for v in group}),
            'derived_words': words,
        })
    roots.sort(key=lambda r: r['root'])
    return roots


def main() -> int:
    data_dir = Path(__file__).resolve().parent
    verbs = [build_verb(e) for e in LEXICON]

    ids = [v['id'] for v in verbs]
    duplicates = {i for i in ids if ids.count(i) > 1}
    if duplicates:
        print('ERROR: duplicate verb ids: %s' % sorted(duplicates))
        return 1

    roots = build_roots(verbs)

    (data_dir / 'verbs.json').write_text(
        json.dumps({'verbs': verbs}, ensure_ascii=False, indent=1),
        encoding='utf-8')
    (data_dir / 'roots.json').write_text(
        json.dumps({'roots': roots}, ensure_ascii=False, indent=1),
        encoding='utf-8')

    print('wrote %d verbs across %d roots' % (len(verbs), len(roots)))
    print('  abwaab covered: %s'
          % sorted({v['baab'] for v in verbs}))
    print('  verbs without passive: %d'
          % sum(1 for v in verbs if not v['has_passive']))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
