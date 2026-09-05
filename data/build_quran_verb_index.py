# -*- coding: utf-8 -*-
"""Build the **complete Quranic verb index** from tagged corpus morphology.

This is what makes search work across the whole Quran instead of across a
handful of hand-entered verbs.

Grouping: by (ROOT, باب), not by lemma
--------------------------------------
The corpus tags each verb token with ``ROOT``, ``VF`` (the verb form, i.e. the
باب), tense, voice and person/gender/number.  Its ``LEM`` tag is *not* reliable
— in 13% of verb tokens the lemma is simply the surface form again
(``LEM:كُوِّرَتْ``, ``LEM:يَشْعُرُ``), which would split one verb across several
bogus head-words.  ``ROOT`` and ``VF`` are dependable, and together they are
exactly how this application models a verb, so entries are keyed on the pair.

The head-word shown to the student is chosen from **attested** forms, in the
order a dictionary would: the ماضی معروف 3rd-m-sg if the Quran contains it,
otherwise the مضارع, otherwise the commonest form — never a manufactured one.

Whole words as well as segments
-------------------------------
The corpus splits a word into morphemes: ``أَنزَلْنَٰهُ`` is stored as
``أَنزَلْ`` + ``نَٰ`` + ``هُ``.  A student types the whole word, so every token
is also reassembled from its segments and indexed under that spelling.

Accuracy policy
---------------
Nothing is generated.  An entry exists only because the verb occurs in the
Quran; its باب is the corpus's own tag; a principal part is recorded only when
that exact form is attested.  A theoretically possible form, a real lexical
verb and a real Quranic occurrence are three different things, and this file
contains only the third.

Sources: morphology — Quranic Arabic Corpus tagged data; ayah text — Tanzil
uthmani.  Neither is Islam360; see ``services/quran_source.py``.

Usage::

    python data/build_quran_verb_index.py --download
"""

import argparse
import json
import re
import sys
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from core.arabic_utils import normalise_letters, strip_marks   # noqa: E402

CACHE = ROOT_DIR / 'data' / 'quran_cache'
MORPHOLOGY = CACHE / 'quran-morphology.txt'
UTHMANI = CACHE / 'quran-uthmani.txt'
MORPHOLOGY_URL = ('https://raw.githubusercontent.com/mustafa0x/'
                  'quran-morphology/master/quran-morphology.txt')

MAX_OCCURRENCES = 8


def download():
    CACHE.mkdir(parents=True, exist_ok=True)
    if MORPHOLOGY.exists() and MORPHOLOGY.stat().st_size > 100000:
        print('  cached   quran-morphology.txt')
        return
    print('  fetching quran-morphology.txt ...')
    req = urllib.request.Request(MORPHOLOGY_URL,
                                 headers={'User-Agent': 'Mozilla/5.0'})
    MORPHOLOGY.write_bytes(urllib.request.urlopen(req, timeout=300).read())


def parse_features(feats: str) -> dict:
    out = {'tense': None, 'voice': 'ACT', 'pgn': None, 'mood': None,
           'baab': None, 'lemma': None}
    for tag in ('PERF', 'IMPF', 'IMPV'):
        if tag in feats:
            out['tense'] = tag
            break
    if 'PASS' in feats:
        out['voice'] = 'PASS'
    m = re.search(r'VF:(\d+)', feats)
    if m:
        out['baab'] = int(m.group(1))
    m = re.search(r'MOOD:(\w+)', feats)
    if m:
        out['mood'] = m.group(1)
    m = re.search(r'(?:^|\|)([123])(M|F)?(S|D|P)(?:\||$)', feats)
    if m:
        out['pgn'] = ''.join(g for g in m.groups() if g)
    m = re.search(r'LEM:([^|]+)', feats)
    if m:
        out['lemma'] = m.group(1)
    return out


def load_ayat() -> dict:
    if not UTHMANI.exists():
        return {}
    out = {}
    for line in UTHMANI.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        parts = line.split('|', 2)
        if len(parts) == 3:
            out[(int(parts[0]), int(parts[1]))] = parts[2].strip()
    return out


# ---------------------------------------------------------------------------
def build():
    if not MORPHOLOGY.exists():
        raise SystemExit('morphology file missing — run with --download')

    ayat = load_ayat()

    # ---- pass 1: read every segment, grouped by the word it belongs to ---
    words = defaultdict(list)          # (s,a,w) -> [(seg, form, pos, feats)]
    for line in MORPHOLOGY.read_text(encoding='utf-8').split('\n'):
        if not line.strip():
            continue
        parts = line.split('\t')
        if len(parts) < 3:
            continue
        loc = parts[0].split(':')
        if len(loc) != 4:
            continue
        key = (int(loc[0]), int(loc[1]), int(loc[2]))
        words[key].append((int(loc[3]), parts[1], parts[2],
                           parts[3] if len(parts) > 3 else ''))

    # ---- pass 2: group verb tokens by (root, باب) ------------------------
    groups = {}
    tokens = 0
    for (surah, ayah, wordno), segs in words.items():
        segs.sort()
        whole = ''.join(s[1] for s in segs)
        for _segno, form, pos, feats in segs:
            if pos != 'V':
                continue
            info = parse_features(feats)
            root = ''
            m = re.search(r'ROOT:([^|]+)', feats)
            if m:
                root = m.group(1)
            if not root or not info['baab']:
                continue
            tokens += 1
            gkey = (root, info['baab'])
            g = groups.setdefault(gkey, {
                'root': root, 'baab': info['baab'], 'count': 0,
                'segments': {}, 'words': {}, 'occurrences': [],
                'lemma_tags': Counter(),
            })
            g['count'] += 1
            if info['lemma']:
                g['lemma_tags'][info['lemma']] += 1

            # One spelling can be more than one thing.  يَعْلَمُ is the 3MS
            # «اللَّهُ يَعْلَمُ» and also the stem the corpus splits out of the
            # 3MP يَعْلَمُونَ.  Keeping only the reading that happened to come
            # first loses the other one for good — which is how the مضارع of
            # عَلِمَ came to be reported as unattested.  Every distinct
            # analysis is counted; the commonest becomes the primary one.
            analysis = (info['tense'], info['voice'], info['pgn'],
                        info['mood'])
            g['segments'].setdefault(form, Counter())[analysis] += 1

            # the word as the student would type it, pronouns and all
            g['words'].setdefault(whole, Counter())[analysis] += 1

            if len(g['occurrences']) < MAX_OCCURRENCES:
                g['occurrences'].append({
                    's': surah, 'a': ayah, 'w': whole, 'seg': form,
                    'tense': info['tense'], 'voice': info['voice'],
                    'pgn': info['pgn'], 'mood': info['mood'],
                    'text': ayat.get((surah, ayah), ''),
                })

    # ---- pass 3: head-word and principal parts, attested only -----------
    def resolve(counter):
        """Commonest analysis first, every other one kept beside it."""
        ranked = counter.most_common()
        (tense, voice, pgn, mood), _n = ranked[0]
        rec = {'tense': tense, 'voice': voice, 'pgn': pgn, 'mood': mood,
               'count': sum(counter.values())}
        if len(ranked) > 1:
            rec['alts'] = [list(a) for a, _ in ranked[1:]]
        return rec

    verbs = []
    for (root, baab), g in groups.items():
        g['segments'] = {f: resolve(c) for f, c in g['segments'].items()}
        g['words'] = {w: resolve(c) for w, c in g['words'].items()}

        principal = {}
        for form, s in g['segments'].items():
            # every reading this spelling has, not just the commonest
            readings = [(s['tense'], s['voice'], s['pgn'], s['mood'])]
            readings += [tuple(a) for a in s.get('alts', [])]
            for tense, voice, pgn, mood in readings:
                if mood not in (None, 'IND'):
                    continue
                key = None
                if tense == 'PERF' and pgn == '3MS':
                    key = 'past_passive' if voice == 'PASS' else 'past_active'
                elif tense == 'IMPF' and pgn == '3MS':
                    key = ('present_passive' if voice == 'PASS'
                           else 'present_active')
                if key and key not in principal:
                    principal[key] = form

        headword = (principal.get('past_active')
                    or principal.get('present_active')
                    or principal.get('past_passive')
                    or principal.get('present_passive'))
        headword_attested = bool(headword)
        if not headword:
            # fall back to the corpus lemma tag, then the commonest form
            if g['lemma_tags']:
                headword = g['lemma_tags'].most_common(1)[0][0]
            else:
                headword = max(g['segments'].items(),
                               key=lambda kv: kv[1]['count'])[0]

        g.pop('lemma_tags', None)
        g['headword'] = headword
        g['headword_attested'] = headword_attested
        g['principal'] = principal
        g['root_spaced'] = ' '.join(root)
        g['surface_count'] = len(g['segments'])
        verbs.append(g)

    verbs.sort(key=lambda v: -v['count'])

    meta = {
        'source_morphology': 'Quranic Arabic Corpus tagged morphology',
        'source_ayah_text': 'Tanzil uthmani',
        'grouping': 'root + verb form (باب)',
        'islam360_verified': False,
        'islam360_note': ('Islam360 verification NOT performed — no authorized '
                          'Islam360 data or API access is available in this '
                          'environment.'),
        'verb_tokens': tokens,
        'entries': len(verbs),
        'roots': len({v['root'] for v in verbs}),
    }

    out = ROOT_DIR / 'data' / 'quran_verbs.json'
    out.write_text(json.dumps({'meta': meta, 'verbs': verbs},
                              ensure_ascii=False), encoding='utf-8')

    print('Quranic verb index -> %s' % out.name)
    print('  entries (root+باب)  : %d' % meta['entries'])
    print('  distinct roots      : %d' % meta['roots'])
    print('  verb tokens         : %d' % tokens)
    print('  segment spellings   : %d' % sum(v['surface_count'] for v in verbs))
    print('  whole-word spellings: %d' % sum(len(v['words']) for v in verbs))
    print('  head-word attested  : %d / %d'
          % (sum(1 for v in verbs if v['headword_attested']), len(verbs)))
    print('  >=2 principal parts : %d'
          % sum(1 for v in verbs if len(v['principal']) >= 2))
    print('  baab spread         : %s'
          % dict(sorted(Counter(v['baab'] for v in verbs).items())))
    print('  file size           : %.1f MB' % (out.stat().st_size / 1e6))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--download', action='store_true')
    args = ap.parse_args()
    if args.download:
        print('Downloading sources:')
        download()
    return build()


if __name__ == '__main__':
    raise SystemExit(main())
