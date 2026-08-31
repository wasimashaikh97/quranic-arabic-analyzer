"""Deterministic Arabic verb inflection engine (گردان).

Accuracy policy
---------------
The **four principal parts** of every verb —

    ماضی معروف   (past active,     e.g. أَنْزَلَ)
    مضارع معروف  (present active,  e.g. يُنْزِلُ)
    ماضی مجہول   (past passive,    e.g. أُنْزِلَ)
    مضارع مجہول  (present passive, e.g. يُنْزَلُ)

— are *verified lexical data* held in ``data/verbs.json``.  This module never
guesses them.  What it does is perform the **regular** inflection of those
verified stems across the 14 صیغے, and the regular derivation of the
مجزوم (jussive) from which امر and نہی follow.

If a principal part is absent from the lexicon (e.g. an intransitive verb has
no passive) the corresponding table comes back empty and the interface shows
«قابلِ اطلاق نہیں» instead of a fabricated form.
"""

from .arabic_utils import (
    FATHA, DAMMA, KASRA, SHADDA, SUKUN,
    ALEF, ALEF_MAQSURA, WAW, YA, TA, NOON, HAMZA_ON_ALEF,
    WEAK_LETTERS, SHORT_VOWELS,
    split_units, join_units, strip_marks, tidy, key_strict, key_loose,
)


# ---------------------------------------------------------------------------
# Pronoun (صیغہ) metadata — the traditional 14-form order
# ---------------------------------------------------------------------------
PRONOUN_META = [
    {"pronoun_ar": "هُوَ", "pronoun_en": "He", "pronoun_ur": "وہ (ایک مرد)",
     "person": 3, "gender": "masculine", "number": "singular",
     "sigha_ur": "واحد مذکر غائب", "sigha_en": "3rd person masculine singular"},
    {"pronoun_ar": "هُمَا", "pronoun_en": "They two (m)", "pronoun_ur": "وہ دونوں (مرد)",
     "person": 3, "gender": "masculine", "number": "dual",
     "sigha_ur": "تثنیہ مذکر غائب", "sigha_en": "3rd person masculine dual"},
    {"pronoun_ar": "هُمْ", "pronoun_en": "They (m)", "pronoun_ur": "وہ سب (مرد)",
     "person": 3, "gender": "masculine", "number": "plural",
     "sigha_ur": "جمع مذکر غائب", "sigha_en": "3rd person masculine plural"},
    {"pronoun_ar": "هِيَ", "pronoun_en": "She", "pronoun_ur": "وہ (ایک عورت)",
     "person": 3, "gender": "feminine", "number": "singular",
     "sigha_ur": "واحد مؤنث غائب", "sigha_en": "3rd person feminine singular"},
    {"pronoun_ar": "هُمَا", "pronoun_en": "They two (f)", "pronoun_ur": "وہ دونوں (عورتیں)",
     "person": 3, "gender": "feminine", "number": "dual",
     "sigha_ur": "تثنیہ مؤنث غائب", "sigha_en": "3rd person feminine dual"},
    {"pronoun_ar": "هُنَّ", "pronoun_en": "They (f)", "pronoun_ur": "وہ سب (عورتیں)",
     "person": 3, "gender": "feminine", "number": "plural",
     "sigha_ur": "جمع مؤنث غائب", "sigha_en": "3rd person feminine plural"},
    {"pronoun_ar": "أَنْتَ", "pronoun_en": "You (m)", "pronoun_ur": "تو (ایک مرد)",
     "person": 2, "gender": "masculine", "number": "singular",
     "sigha_ur": "واحد مذکر حاضر", "sigha_en": "2nd person masculine singular"},
    {"pronoun_ar": "أَنْتُمَا", "pronoun_en": "You two (m)", "pronoun_ur": "تم دونوں (مرد)",
     "person": 2, "gender": "masculine", "number": "dual",
     "sigha_ur": "تثنیہ مذکر حاضر", "sigha_en": "2nd person masculine dual"},
    {"pronoun_ar": "أَنْتُمْ", "pronoun_en": "You all (m)", "pronoun_ur": "تم سب (مرد)",
     "person": 2, "gender": "masculine", "number": "plural",
     "sigha_ur": "جمع مذکر حاضر", "sigha_en": "2nd person masculine plural"},
    {"pronoun_ar": "أَنْتِ", "pronoun_en": "You (f)", "pronoun_ur": "تو (ایک عورت)",
     "person": 2, "gender": "feminine", "number": "singular",
     "sigha_ur": "واحد مؤنث حاضر", "sigha_en": "2nd person feminine singular"},
    {"pronoun_ar": "أَنْتُمَا", "pronoun_en": "You two (f)", "pronoun_ur": "تم دونوں (عورتیں)",
     "person": 2, "gender": "feminine", "number": "dual",
     "sigha_ur": "تثنیہ مؤنث حاضر", "sigha_en": "2nd person feminine dual"},
    {"pronoun_ar": "أَنْتُنَّ", "pronoun_en": "You all (f)", "pronoun_ur": "تم سب (عورتیں)",
     "person": 2, "gender": "feminine", "number": "plural",
     "sigha_ur": "جمع مؤنث حاضر", "sigha_en": "2nd person feminine plural"},
    {"pronoun_ar": "أَنَا", "pronoun_en": "I", "pronoun_ur": "میں",
     "person": 1, "gender": "common", "number": "singular",
     "sigha_ur": "واحد متکلم", "sigha_en": "1st person singular"},
    {"pronoun_ar": "نَحْنُ", "pronoun_en": "We", "pronoun_ur": "ہم",
     "person": 1, "gender": "common", "number": "plural",
     "sigha_ur": "جمع متکلم", "sigha_en": "1st person plural"},
]

# indices whose past-tense suffix begins with a vowel
_PAST_VOWEL_INITIAL = (0, 1, 2, 3, 4)
# past suffixes for the consonant-initial group (indices 5..13), sukun added by caller
_PAST_CONS_SUFFIX = {
    5: NOON + FATHA,                          # هُنَّ    ـنَ
    6: TA + FATHA,                            # أَنْتَ    ـتَ
    7: TA + DAMMA + 'مَا',                    # أَنْتُمَا  ـتُمَا
    8: TA + DAMMA + 'مْ',                     # أَنْتُمْ   ـتُمْ
    9: TA + KASRA,                            # أَنْتِ    ـتِ
    10: TA + DAMMA + 'مَا',                   # أَنْتُمَا  ـتُمَا
    11: TA + DAMMA + NOON + SHADDA + FATHA,   # أَنْتُنَّ  ـتُنَّ
    12: TA + DAMMA,                           # أَنَا     ـتُ
    13: NOON + FATHA + ALEF,                  # نَحْنُ    ـنَا
}
# vowel-initial past suffixes
_PAST_VOWEL_SUFFIX = {
    0: FATHA,
    1: FATHA + ALEF,
    2: DAMMA + WAW + ALEF,
    3: FATHA + TA + SUKUN,
    4: FATHA + TA + FATHA + ALEF,
}

# present prefix letters, indexed like PRONOUN_META
_PRESENT_PREFIX_LETTERS = [YA, YA, YA, TA, TA, YA, TA, TA, TA, TA, TA, TA,
                           HAMZA_ON_ALEF, NOON]

_SINGULAR_IDX = (0, 3, 6, 12, 13)   # take the plain mood ending
_DUAL_IDX = (1, 4, 7, 10)           # ـَانِ / ـَا
_MASC_PLURAL_IDX = (2, 8)           # ـُونَ / ـُوا
_FEM_SG2_IDX = (9,)                 # ـِينَ / ـِي
_FEM_PLURAL_IDX = (5, 11)           # ـْنَ (invariable)

SECOND_PERSON_IDX = (6, 7, 8, 9, 10, 11)


class ConjugationError(ValueError):
    """Raised when lexical data is insufficient to inflect accurately."""


# ---------------------------------------------------------------------------
# Stem analysis
# ---------------------------------------------------------------------------
def _is_bare_weak(unit) -> bool:
    return unit[0] in WEAK_LETTERS and unit[1] == ''


def _first_short_vowel(units) -> str:
    for _letter, marks in units:
        for v in SHORT_VOWELS:
            if v in marks:
                return v
    return FATHA


def _shorten_long_vowel(units):
    """Drop a bare weak letter sitting in the penultimate slot (قُول → قُل)."""
    if len(units) >= 2 and _is_bare_weak(units[-2]):
        return units[:-2] + [units[-1]]
    return list(units)


def _stem_vowel(units) -> str:
    """The characteristic vowel of a stem — that of its last voweled letter."""
    for _letter, marks in reversed(units):
        for v in SHORT_VOWELS:
            if v in marks:
                return v
    return FATHA


def _expand_doubled_past(units):
    """رَدَّ → رَدَد (active) / رُدَّ → رُدِد (passive).

    The first radical keeps its own vowel; the linking vowel is فتحہ in the
    active and کسرہ in the passive (رَدَدْتُ / رُدِدْتُ).
    """
    last_letter, last_marks = units[-1]
    if SHADDA not in last_marks:
        return list(units)
    head = [list(u) for u in units[:-1]]
    link = KASRA if _first_short_vowel(units) == DAMMA else FATHA
    return head + [[last_letter, link], [last_letter, last_marks.replace(SHADDA, '')]]


def _expand_doubled_present(units):
    """رُدّ → رْدُد  (يَرُدُّ → يَرْدُدْنَ)  /  رَدّ → رْدَد  (يُرَدُّ → يُرْدَدْنَ).

    In the مضارع the first radical takes سکون and the linking vowel is the
    stem vowel itself.
    """
    last_letter, last_marks = units[-1]
    if SHADDA not in last_marks:
        return list(units)
    head = [list(u) for u in units[:-1]]
    link = _first_short_vowel(units)
    if head:
        marks = head[-1][1]
        for v in SHORT_VOWELS:
            marks = marks.replace(v, '')
        head[-1][1] = marks + SUKUN
    return head + [[last_letter, link], [last_letter, last_marks.replace(SHADDA, '')]]


def analyse_past(past_3ms: str, short_stem: str = None) -> dict:
    """Classify a verified ماضی 3ms form and return its inflection stems."""
    units = split_units(past_3ms)
    if len(units) < 2:
        raise ConjugationError('past form too short: %r' % past_3ms)

    last_letter, last_marks = units[-1]

    # ---- defective (ناقص):  دَعَا / رَمَى / نَادَى -------------------------
    if last_letter in (ALEF, ALEF_MAQSURA) and last_marks == '':
        base = join_units(units[:-1])
        kind = 'def_waw' if last_letter == ALEF else 'def_ya'
        return {'kind': kind, 'given': past_3ms, 'base': base}

    # ---- passive/فَعِلَ defective:  دُعِيَ / لَقِيَ -------------------------
    if last_letter == YA and FATHA in last_marks and len(units) >= 2 \
            and KASRA in units[-2][1]:
        base_i = join_units(units[:-1])                       # دُعِ
        cons = join_units(units[:-2] + [[units[-2][0], '']])   # دُع
        return {'kind': 'def_i', 'given': past_3ms,
                'base': base_i, 'cons_base': cons}

    # ---- doubled (مضاعف):  رَدَّ / رُدَّ -----------------------------------
    if SHADDA in last_marks:
        long_units = units[:-1] + [[last_letter, SHADDA]]
        short = short_stem or join_units(_expand_doubled_past(long_units))
        return {'kind': 'doubled', 'long': join_units(long_units), 'short': short}

    # ---- hollow (اجوف):  قَالَ / قِيلَ ------------------------------------
    if len(units) >= 3 and _is_bare_weak(units[-2]):
        long_units = units[:-1] + [[last_letter, '']]
        if short_stem:
            short = short_stem
        else:
            short = join_units(_shorten_long_vowel(long_units))
        return {'kind': 'hollow', 'long': join_units(long_units), 'short': short}

    # ---- regular (صحیح / مہموز / مثال / all derived sound forms) ----------
    stem_units = units[:-1] + [[last_letter, last_marks.replace(FATHA, '')]]
    return {'kind': 'regular', 'long': join_units(stem_units)}


def analyse_present(present_3ms: str) -> dict:
    """Classify a verified مضارع 3ms form and return its inflection stems."""
    units = split_units(present_3ms)
    if len(units) < 3:
        raise ConjugationError('present form too short: %r' % present_3ms)

    prefix_vowel = units[0][1] or FATHA
    body = [list(u) for u in units[1:]]
    last_letter, last_marks = body[-1]

    # ---- defective: يَدْعُو / يَرْمِي / يَسْعَى ---------------------------
    if last_letter in (WAW, YA, ALEF_MAQSURA) and last_marks == '':
        base = body[:-1]
        kind = {WAW: 'def_u', YA: 'def_i', ALEF_MAQSURA: 'def_a'}[last_letter]
        return {'kind': kind, 'prefix_vowel': prefix_vowel,
                'base': join_units(base), 'base_units': base,
                'stem_vowel': _stem_vowel(base)}

    if DAMMA not in last_marks:
        raise ConjugationError('present must end in ـُ or a weak letter: %r'
                               % present_3ms)

    stem = body[:-1] + [[last_letter, last_marks.replace(DAMMA, '')]]

    # ---- doubled: يَرُدُّ -------------------------------------------------
    if SHADDA in stem[-1][1]:
        return {'kind': 'doubled', 'prefix_vowel': prefix_vowel,
                'stem': join_units(stem),
                'expanded': join_units(_expand_doubled_present(stem)),
                'stem_vowel': _stem_vowel(stem)}

    # ---- hollow: يَقُولُ / يُقِيمُ / يَخَافُ ------------------------------
    if len(stem) >= 2 and _is_bare_weak(stem[-2]):
        return {'kind': 'hollow', 'prefix_vowel': prefix_vowel,
                'stem': join_units(stem),
                'short': join_units(_shorten_long_vowel(stem)),
                'stem_vowel': _stem_vowel(stem)}

    return {'kind': 'regular', 'prefix_vowel': prefix_vowel,
            'stem': join_units(stem), 'stem_vowel': _stem_vowel(stem)}


# ---------------------------------------------------------------------------
# Past paradigm
# ---------------------------------------------------------------------------
def past_forms(past_3ms: str, short_stem: str = None) -> list:
    """Return the 14 ماضی forms of a verified 3ms past."""
    info = analyse_past(past_3ms, short_stem)
    kind = info['kind']
    out = []

    if kind in ('regular', 'hollow', 'doubled'):
        long_stem = info['long']
        short = info.get('short', long_stem)
        for i in range(14):
            if i in _PAST_VOWEL_INITIAL:
                out.append(long_stem + _PAST_VOWEL_SUFFIX[i])
            else:
                out.append(short + SUKUN + _PAST_CONS_SUFFIX[i])

    elif kind in ('def_waw', 'def_ya'):
        base = info['base']
        weak = WAW if kind == 'def_waw' else YA
        for i in range(14):
            if i == 0:
                out.append(info['given'])
            elif i == 1:
                out.append(base + weak + FATHA + ALEF)
            elif i == 2:
                out.append(base + WAW + SUKUN + ALEF)
            elif i == 3:
                out.append(base + TA + SUKUN)
            elif i == 4:
                out.append(base + TA + FATHA + ALEF)
            else:
                out.append(base + weak + SUKUN + _PAST_CONS_SUFFIX[i])

    elif kind == 'def_i':
        base = info['base']          # دُعِ
        cons = info['cons_base']     # دُع
        for i in range(14):
            if i == 0:
                out.append(info['given'])
            elif i == 1:
                out.append(base + YA + FATHA + ALEF)
            elif i == 2:
                out.append(cons + DAMMA + WAW + ALEF)
            elif i == 3:
                out.append(base + YA + FATHA + TA + SUKUN)
            elif i == 4:
                out.append(base + YA + FATHA + TA + FATHA + ALEF)
            else:
                out.append(base + YA + _PAST_CONS_SUFFIX[i])
    else:  # pragma: no cover - defensive
        raise ConjugationError('unknown past kind %r' % kind)

    return [tidy(f) for f in out]


# ---------------------------------------------------------------------------
# Present paradigm (indicative مرفوع and jussive مجزوم)
# ---------------------------------------------------------------------------
def present_forms(present_3ms: str, mood: str = 'indicative') -> list:
    """Return the 14 مضارع forms; ``mood`` is 'indicative' or 'jussive'."""
    info = analyse_present(present_3ms)
    kind = info['kind']
    pv = info['prefix_vowel']
    jussive = (mood == 'jussive')
    out = []

    for i in range(14):
        prefix = _PRESENT_PREFIX_LETTERS[i] + pv

        if kind == 'regular':
            stem = info['stem']
            if i in _SINGULAR_IDX:
                body = stem + (SUKUN if jussive else DAMMA)
            elif i in _DUAL_IDX:
                body = stem + FATHA + ALEF + ('' if jussive else NOON + KASRA)
            elif i in _MASC_PLURAL_IDX:
                body = stem + DAMMA + WAW + (ALEF if jussive else NOON + FATHA)
            elif i in _FEM_SG2_IDX:
                body = stem + KASRA + YA + ('' if jussive else NOON + FATHA)
            else:  # feminine plural — invariable
                body = stem + SUKUN + NOON + FATHA

        elif kind == 'hollow':
            stem, short = info['stem'], info['short']
            if i in _SINGULAR_IDX:
                body = (short + SUKUN) if jussive else (stem + DAMMA)
            elif i in _DUAL_IDX:
                body = stem + FATHA + ALEF + ('' if jussive else NOON + KASRA)
            elif i in _MASC_PLURAL_IDX:
                body = stem + DAMMA + WAW + (ALEF if jussive else NOON + FATHA)
            elif i in _FEM_SG2_IDX:
                body = stem + KASRA + YA + ('' if jussive else NOON + FATHA)
            else:
                body = short + SUKUN + NOON + FATHA

        elif kind == 'doubled':
            stem, expanded = info['stem'], info['expanded']
            if i in _SINGULAR_IDX:
                body = stem + (FATHA if jussive else DAMMA)
            elif i in _DUAL_IDX:
                body = stem + FATHA + ALEF + ('' if jussive else NOON + KASRA)
            elif i in _MASC_PLURAL_IDX:
                body = stem + DAMMA + WAW + (ALEF if jussive else NOON + FATHA)
            elif i in _FEM_SG2_IDX:
                body = stem + KASRA + YA + ('' if jussive else NOON + FATHA)
            else:
                body = expanded + SUKUN + NOON + FATHA

        elif kind == 'def_u':                      # يَدْعُو
            base = info['base']                    # ...دْعُ
            base_k = _reset_final_vowel(info['base_units'], KASRA)
            if i in _SINGULAR_IDX:
                body = base if jussive else base + WAW
            elif i in _DUAL_IDX:
                body = base + WAW + FATHA + ALEF + ('' if jussive else NOON + KASRA)
            elif i in _MASC_PLURAL_IDX:
                body = base + WAW + (ALEF if jussive else NOON + FATHA)
            elif i in _FEM_SG2_IDX:
                body = base_k + YA + ('' if jussive else NOON + FATHA)
            else:
                body = base + WAW + NOON + FATHA

        elif kind == 'def_i':                      # يَرْمِي
            base = info['base']                    # ...رْمِ
            base_d = _reset_final_vowel(info['base_units'], DAMMA)
            if i in _SINGULAR_IDX:
                body = base if jussive else base + YA
            elif i in _DUAL_IDX:
                body = base + YA + FATHA + ALEF + ('' if jussive else NOON + KASRA)
            elif i in _MASC_PLURAL_IDX:
                body = base_d + WAW + (ALEF if jussive else NOON + FATHA)
            elif i in _FEM_SG2_IDX:
                body = base + YA + ('' if jussive else NOON + FATHA)
            else:
                body = base + YA + NOON + FATHA

        elif kind == 'def_a':                      # يَسْعَى / يُدْعَى
            base = info['base']                    # ...سْعَ
            if i in _SINGULAR_IDX:
                body = base if jussive else base + ALEF_MAQSURA
            elif i in _DUAL_IDX:
                body = base + YA + FATHA + ALEF + ('' if jussive else NOON + KASRA)
            elif i in _MASC_PLURAL_IDX:
                body = base + WAW + SUKUN + (ALEF if jussive else NOON + FATHA)
            elif i in _FEM_SG2_IDX:
                body = base + YA + SUKUN + ('' if jussive else NOON + FATHA)
            else:
                body = base + YA + SUKUN + NOON + FATHA
        else:  # pragma: no cover
            raise ConjugationError('unknown present kind %r' % kind)

        out.append(tidy(prefix + body))

    return out


def _reset_final_vowel(base_units, vowel: str) -> str:
    """Swap the short vowel of the last unit (دْعُ → دْعِ)."""
    units = [list(u) for u in base_units]
    if units:
        marks = units[-1][1]
        for v in SHORT_VOWELS:
            marks = marks.replace(v, '')
        units[-1][1] = marks + vowel
    return join_units(units)


# ---------------------------------------------------------------------------
# امر (imperative) and نہی (prohibition) — derived from the jussive
# ---------------------------------------------------------------------------
def imperative_forms(present_3ms: str, baab: int = 1, override: list = None) -> list:
    """Return the 6 امر forms.

    ``override`` lets the lexicon supply the genuinely irregular imperatives
    (أَكَلَ → كُلْ، أَمَرَ → مُرْ، أَخَذَ → خُذْ).
    """
    if override:
        return [tidy(f) for f in override]

    juss = present_forms(present_3ms, mood='jussive')
    # همزۃ الوصل takes ضمہ only when the stem vowel of the مضارع is ضمہ
    # (اُكْتُبْ، اُدْعُ، اُرْدُدْنَ) and کسرہ otherwise (اِعْلَمْ، اِرْمِ، اِنْتَصِرْ).
    stem_vowel = analyse_present(present_3ms).get('stem_vowel', FATHA)
    wasl_vowel = DAMMA if stem_vowel == DAMMA else KASRA

    out = []
    for i in SECOND_PERSON_IDX:
        units = split_units(juss[i])
        remainder = join_units(units[1:])      # drop the تَ / تُ prefix
        out.append(tidy(_add_imperative_prefix(remainder, baab, wasl_vowel)))
    return out


def _add_imperative_prefix(remainder: str, baab: int, wasl_vowel: str) -> str:
    units = split_units(remainder)
    if not units:
        return remainder
    if baab == 4:
        # باب إفعال always restores همزۂ قطع:  أَنْزِلْ، أَخْرِجْ
        return HAMZA_ON_ALEF + FATHA + remainder
    first_marks = units[0][1]
    if SUKUN in first_marks or first_marks == '':
        # the stem opens with a consonant cluster → prefix همزۃ الوصل
        return ALEF + wasl_vowel + remainder
    return remainder


def prohibition_forms(present_3ms: str) -> list:
    """Return the 6 نہی forms:  لَا + مضارع مجزوم (2nd person)."""
    juss = present_forms(present_3ms, mood='jussive')
    return ['لَا ' + juss[i] for i in SECOND_PERSON_IDX]


# ---------------------------------------------------------------------------
# Urdu / English gloss builders
# ---------------------------------------------------------------------------
_UR_PAST_SUBJ = [
    'اُس (ایک مرد) نے', 'اُن دونوں (مردوں) نے', 'اُن سب (مردوں) نے',
    'اُس (ایک عورت) نے', 'اُن دونوں (عورتوں) نے', 'اُن سب (عورتوں) نے',
    'تو (ایک مرد) نے', 'تم دونوں (مردوں) نے', 'تم سب (مردوں) نے',
    'تو (ایک عورت) نے', 'تم دونوں (عورتوں) نے', 'تم سب (عورتوں) نے',
    'میں نے', 'ہم نے',
]
_UR_NOM_SUBJ = [
    'وہ (ایک مرد)', 'وہ دونوں (مرد)', 'وہ سب (مرد)',
    'وہ (ایک عورت)', 'وہ دونوں (عورتیں)', 'وہ سب (عورتیں)',
    'تو (ایک مرد)', 'تم دونوں (مرد)', 'تم سب (مرد)',
    'تو (ایک عورت)', 'تم دونوں (عورتیں)', 'تم سب (عورتیں)',
    'میں', 'ہم',
]
# imperfective participle ending + auxiliary, per صیغہ
_UR_PRESENT_TAIL = [
    ('تا', 'ہے'), ('تے', 'ہیں'), ('تے', 'ہیں'),
    ('تی', 'ہے'), ('تی', 'ہیں'), ('تی', 'ہیں'),
    ('تا', 'ہے'), ('تے', 'ہو'), ('تے', 'ہو'),
    ('تی', 'ہے'), ('تی', 'ہو'), ('تی', 'ہو'),
    ('تا', 'ہوں'), ('تے', 'ہیں'),
]
# gender/number of the grammatical subject, used for passive agreement
_UR_AGREEMENT = ['ms', 'mp', 'mp', 'fs', 'fp', 'fp',
                 'ms', 'mp', 'mp', 'fs', 'fp', 'fp', 'ms', 'mp']
_UR_JANA = {'ms': 'گیا', 'mp': 'گئے', 'fs': 'گئی', 'fp': 'گئیں'}
_UR_JATA = {'ms': 'جاتا ہے', 'mp': 'جاتے ہیں', 'fs': 'جاتی ہے', 'fp': 'جاتی ہیں'}

_EN_SUBJ = ['He', 'They two (m)', 'They (m)', 'She', 'They two (f)', 'They (f)',
            'You (m.s)', 'You two (m)', 'You all (m)', 'You (f.s)',
            'You two (f)', 'You all (f)', 'I', 'We']
_EN_WAS = {0: 'was', 3: 'was', 12: 'was'}
_EN_IS = {0: 'is', 3: 'is', 12: 'am'}


def _ur_agree(ur_past: str, agreement: str) -> str:
    """Inflect an Urdu past participle for gender/number (لکھا → لکھے/لکھی)."""
    if not ur_past:
        return ur_past
    if agreement == 'ms':
        return ur_past
    stem, last = ur_past[:-1], ur_past[-1]
    if last != 'ا':
        return ur_past
    if stem.endswith('ی'):          # کھایا، دیا، لایا
        stem = stem[:-1] + 'ئ' if len(stem) > 1 else stem
        return stem + {'mp': 'ے', 'fs': 'ی', 'fp': 'یں'}[agreement]
    return stem + {'mp': 'ے', 'fs': 'ی', 'fp': 'یں'}[agreement]


def _en_third_person(base: str) -> str:
    if not base:
        return base
    if base.endswith(('s', 'x', 'z', 'ch', 'sh', 'o')):
        return base + 'es'
    if base.endswith('y') and len(base) > 1 and base[-2] not in 'aeiou':
        return base[:-1] + 'ies'
    return base + 's'


def build_gloss(index: int, tense: str, ur_stem: str, ur_past: str,
                en_base: str, en_past: str, en_pp: str) -> tuple:
    """Return ``(urdu, english)`` gloss for one صیغہ of one tense."""
    meta = PRONOUN_META[index]
    agree = _UR_AGREEMENT[index]

    if tense == 'past_active':
        ur = '%s %s' % (_UR_PAST_SUBJ[index], ur_past)
        en = '%s %s' % (_EN_SUBJ[index], en_past)

    elif tense == 'present_active':
        tail, aux = _UR_PRESENT_TAIL[index]
        ur = '%s %s%s %s' % (_UR_NOM_SUBJ[index], ur_stem, tail, aux)
        if index in (0, 3):
            en = '%s %s' % (_EN_SUBJ[index], _en_third_person(en_base))
        else:
            en = '%s %s' % (_EN_SUBJ[index], en_base)

    elif tense == 'past_passive':
        ur = '%s %s %s' % (_UR_NOM_SUBJ[index],
                           _ur_agree(ur_past, agree), _UR_JANA[agree])
        en = '%s %s %s' % (_EN_SUBJ[index], _EN_WAS.get(index, 'were'), en_pp)

    elif tense == 'present_passive':
        ur = '%s %s %s' % (_UR_NOM_SUBJ[index],
                           _ur_agree(ur_past, agree), _UR_JATA[agree])
        en = '%s %s %s' % (_EN_SUBJ[index], _EN_IS.get(index, 'are'), en_pp)

    elif tense == 'imperative':
        ur_tail = {'ms': '', 'mp': 'و', 'fs': '', 'fp': 'و'}[agree]
        ur = '%s %s%s' % (_UR_NOM_SUBJ[index], ur_stem, ur_tail)
        en = '%s! (%s)' % (en_base.capitalize(), meta['pronoun_en'])

    elif tense == 'prohibition':
        ur_tail = {'ms': '', 'mp': 'و', 'fs': '', 'fp': 'و'}[agree]
        ur = '%s مت %s%s' % (_UR_NOM_SUBJ[index], ur_stem, ur_tail)
        en = "Don't %s! (%s)" % (en_base, meta['pronoun_en'])

    else:
        ur, en = '', ''

    return ur, en


# ---------------------------------------------------------------------------
# Public engine
# ---------------------------------------------------------------------------
TENSE_LABELS = {
    'past_active':     {'ar': 'الماضي المعروف', 'ur': 'ماضی معروف', 'en': 'Past Active'},
    'present_active':  {'ar': 'المضارع المعروف', 'ur': 'مضارع معروف', 'en': 'Present Active'},
    'past_passive':    {'ar': 'الماضي المجهول', 'ur': 'ماضی مجہول', 'en': 'Past Passive'},
    'present_passive': {'ar': 'المضارع المجهول', 'ur': 'مضارع مجہول', 'en': 'Present Passive'},
    'imperative':      {'ar': 'فعل الأمر', 'ur': 'امر', 'en': 'Imperative'},
    'prohibition':     {'ar': 'فعل النهي', 'ur': 'نہی', 'en': 'Prohibition'},
}
TENSE_ORDER = ['past_active', 'present_active', 'past_passive',
               'present_passive', 'imperative', 'prohibition']
MANDATORY_TENSES = ['past_active', 'present_active',
                    'past_passive', 'present_passive']


class ConjugationEngine:
    """Inflects verified lexical stems into the complete گردان."""

    PRONOUN_META = PRONOUN_META            # kept for backward compatibility

    def conjugate_verb(self, verb_data: dict, tense: str = None) -> dict:
        """Return ``{tense: [row, ...]}`` for one lexicon entry.

        A tense whose principal part is not attested comes back as ``[]``.
        """
        if not verb_data:
            return {}

        ur_stem = verb_data.get('ur_stem') or _fallback_ur_stem(verb_data)
        ur_past = verb_data.get('ur_past') or (ur_stem + 'ا')
        en_base = (verb_data.get('en_base')
                   or verb_data.get('meaning_english', '').replace('to ', '').strip())
        en_past = verb_data.get('en_past') or _fallback_en_past(en_base)
        en_pp = verb_data.get('en_pp') or _fallback_en_past(en_base)

        baab = int(verb_data.get('baab') or verb_data.get('form') or 1)

        past_3ms = verb_data.get('past_3ms') or verb_data.get('arabic')
        present_3ms = verb_data.get('present_3ms')
        past_pass = verb_data.get('past_passive_3ms')
        pres_pass = verb_data.get('present_passive_3ms')

        result = {k: [] for k in TENSE_ORDER}

        if past_3ms:
            forms = past_forms(past_3ms, verb_data.get('past_short_stem'))
            result['past_active'] = self._rows(forms, 'past_active', ur_stem,
                                               ur_past, en_base, en_past, en_pp)
        if present_3ms:
            forms = present_forms(present_3ms)
            result['present_active'] = self._rows(forms, 'present_active', ur_stem,
                                                  ur_past, en_base, en_past, en_pp)
            imp = imperative_forms(present_3ms, baab,
                                   verb_data.get('imperative_forms'))
            result['imperative'] = self._rows(imp, 'imperative', ur_stem, ur_past,
                                              en_base, en_past, en_pp,
                                              indices=SECOND_PERSON_IDX)
            pro = prohibition_forms(present_3ms)
            result['prohibition'] = self._rows(pro, 'prohibition', ur_stem, ur_past,
                                               en_base, en_past, en_pp,
                                               indices=SECOND_PERSON_IDX)
        if past_pass:
            forms = past_forms(past_pass, verb_data.get('past_passive_short_stem'))
            result['past_passive'] = self._rows(forms, 'past_passive', ur_stem,
                                                ur_past, en_base, en_past, en_pp)
        if pres_pass:
            forms = present_forms(pres_pass)
            result['present_passive'] = self._rows(forms, 'present_passive', ur_stem,
                                                   ur_past, en_base, en_past, en_pp)

        if tense:
            return {tense: result.get(tense, [])}
        return result

    @staticmethod
    def _rows(forms, tense, ur_stem, ur_past, en_base, en_past, en_pp,
              indices=None):
        indices = list(indices) if indices else list(range(14))
        rows = []
        for slot, idx in enumerate(indices):
            if slot >= len(forms):
                break
            meta = PRONOUN_META[idx]
            ur, en = build_gloss(idx, tense, ur_stem, ur_past,
                                 en_base, en_past, en_pp)
            rows.append({
                'index': slot + 1,
                'sigha_number': idx + 1,
                'pronoun_arabic': meta['pronoun_ar'],
                'pronoun_english': meta['pronoun_en'],
                'pronoun_urdu': meta['pronoun_ur'],
                'sigha_urdu': meta['sigha_ur'],
                'sigha_english': meta['sigha_en'],
                'person': meta['person'],
                'gender': meta['gender'],
                'number': meta['number'],
                'arabic': forms[slot],
                'meaning_urdu': ur,
                'meaning_english': en,
                'tense': tense,
            })
        return rows

    # -- reverse analysis ---------------------------------------------------
    def identify_form_from_conjugated(self, word: str, verb_data_list: list) -> list:
        """Find every verified form matching a conjugated word the user typed."""
        target_strict = key_strict(word.strip())
        target_loose = key_loose(word.strip())
        exact, loose = [], []

        for verb in verb_data_list:
            try:
                conjugations = self.conjugate_verb(verb)
            except ConjugationError:
                continue
            for tense, rows in conjugations.items():
                for row in rows:
                    form = row.get('arabic', '')
                    hit = {
                        'verb_id': verb.get('id'),
                        'verb_arabic': verb.get('arabic'),
                        'root': verb.get('root'),
                        'baab': verb.get('baab', verb.get('form')),
                        'baab_name': verb.get('baab_name_arabic', ''),
                        'tense': tense,
                        'form': form,
                        'person': row.get('person'),
                        'gender': row.get('gender'),
                        'number': row.get('number'),
                        'pronoun': row.get('pronoun_arabic'),
                        'sigha_urdu': row.get('sigha_urdu'),
                        'sigha_english': row.get('sigha_english'),
                        'meaning_urdu': row.get('meaning_urdu'),
                        'meaning_english': row.get('meaning_english'),
                    }
                    if key_strict(form) == target_strict:
                        exact.append(hit)
                    elif key_loose(form) == target_loose:
                        loose.append(hit)
        return exact if exact else loose


def _fallback_ur_stem(verb_data: dict) -> str:
    ur = verb_data.get('meaning_urdu', '') or ''
    return ur[:-2] if ur.endswith('نا') else ur


def _fallback_en_past(base: str) -> str:
    if not base:
        return base
    if base.endswith('e'):
        return base + 'd'
    if base.endswith('y') and len(base) > 1 and base[-2] not in 'aeiou':
        return base[:-1] + 'ied'
    return base + 'ed'
