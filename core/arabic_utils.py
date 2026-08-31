"""Low-level Arabic text helpers shared by the morphology engine.

Everything here is pure text manipulation — no lexical guessing.
"""

# --- Diacritics (harakat) -------------------------------------------------
FATHA = 'َ'      # َ
DAMMA = 'ُ'      # ُ
KASRA = 'ِ'      # ِ
SHADDA = 'ّ'     # ّ
SUKUN = 'ْ'      # ْ
FATHATAN = 'ً'   # ً
DAMMATAN = 'ٌ'   # ٌ
KASRATAN = 'ٍ'   # ٍ
MADDA_ABOVE = 'ٓ'
HAMZA_ABOVE = 'ٔ'
HAMZA_BELOW = 'ٕ'
SUPERSCRIPT_ALEF = 'ٰ'

SHORT_VOWELS = (FATHA, DAMMA, KASRA)
ALL_MARKS = frozenset([
    FATHA, DAMMA, KASRA, SHADDA, SUKUN,
    FATHATAN, DAMMATAN, KASRATAN,
    MADDA_ABOVE, HAMZA_ABOVE, HAMZA_BELOW, SUPERSCRIPT_ALEF,
])

# Letters
ALEF = 'ا'            # ا
ALEF_MAQSURA = 'ى'    # ى
WAW = 'و'             # و
YA = 'ي'              # ي
TA = 'ت'              # ت
NOON = 'ن'            # ن
HAMZA_ON_ALEF = 'أ'   # أ
ALEF_MADDA = 'آ'      # آ
ALEF_HAMZA_BELOW = 'إ'  # إ
WAW_HAMZA = 'ؤ'       # ؤ
YA_HAMZA = 'ئ'        # ئ
HAMZA = 'ء'           # ء
TA_MARBUTA = 'ة'      # ة
HA = 'ه'              # ه

WEAK_LETTERS = frozenset([ALEF, ALEF_MAQSURA, WAW, YA])
HAMZA_FORMS = frozenset([HAMZA, HAMZA_ON_ALEF, ALEF_HAMZA_BELOW,
                         ALEF_MADDA, WAW_HAMZA, YA_HAMZA])

ARABIC_LETTERS = frozenset(
    'ابتثجحخدذرز'
    'سشصضطظعغفقك'
    'لمنهويىة'
) | HAMZA_FORMS


def is_mark(ch: str) -> bool:
    return ch in ALL_MARKS


def split_units(text: str) -> list:
    """Split diacritised Arabic into ``[[letter, marks], ...]`` units."""
    units = []
    for ch in text:
        if is_mark(ch) and units:
            units[-1][1] += ch
        else:
            units.append([ch, ''])
    return units


def join_units(units) -> str:
    return ''.join(letter + marks for letter, marks in units)


#: order marks are written in within one letter: shadda, then the vowel,
#: then anything else.  Both orders occur in real text and in what users type,
#: so everything is canonicalised before it is compared or displayed.
_MARK_RANK = {SHADDA: 0, FATHA: 1, DAMMA: 1, KASRA: 1,
              FATHATAN: 1, DAMMATAN: 1, KASRATAN: 1, SUKUN: 1}


def canonical_marks(text: str) -> str:
    """Put the diacritics of every letter into canonical order."""
    if not text:
        return ''
    out = []
    for letter, marks in split_units(text):
        if len(marks) > 1:
            marks = ''.join(sorted(marks, key=lambda m: _MARK_RANK.get(m, 2)))
        out.append(letter + marks)
    return ''.join(out)


def strip_marks(text: str) -> str:
    """Remove *all* diacritics, shadda included (display/loose compare)."""
    if not text:
        return ''
    return ''.join(ch for ch in text if not is_mark(ch))


def strip_vowels(text: str) -> str:
    """Remove short vowels & sukun but KEEP shadda.

    Keeping shadda is what allows كَتَبَ and كَتَّبَ (or عَلِمَ and عَلَّمَ)
    to stay distinguishable when the user omits the harakat.
    """
    if not text:
        return ''
    drop = ALL_MARKS - {SHADDA}
    return ''.join(ch for ch in text if ch not in drop)


def normalise_letters(text: str) -> str:
    """Fold orthographic variants so a user's loose spelling still matches."""
    if not text:
        return ''
    out = []
    for ch in text:
        if ch in (HAMZA_ON_ALEF, ALEF_HAMZA_BELOW, ALEF_MADDA, HAMZA):
            out.append(ALEF)
        elif ch == ALEF_MAQSURA:
            out.append(YA)
        elif ch == WAW_HAMZA:
            out.append(WAW)
        elif ch == YA_HAMZA:
            out.append(YA)
        elif ch == TA_MARBUTA:
            out.append(HA)
        else:
            out.append(ch)
    return ''.join(out)


def key_exact(text: str) -> str:
    """Full-diacritic key, insensitive only to how marks were ordered."""
    return canonical_marks((text or '').strip())


def key_strict(text: str) -> str:
    """Comparison key that keeps hamza and shadda (highest precision)."""
    return strip_vowels(text).replace(' ', '')


def key_loose(text: str) -> str:
    """Comparison key that also folds hamza/alef/ya variants."""
    return normalise_letters(strip_vowels(text)).replace(' ', '')


def key_bare(text: str) -> str:
    """Loosest key: no shadda, no hamza distinction."""
    return normalise_letters(strip_marks(text)).replace(' ', '')


# --- Phonological tidy-ups ----------------------------------------------
_HAMZA_FIXES = (
    # أَ + أْ  ->  آ      (أَأْكُلُ  ->  آكُلُ)
    (HAMZA_ON_ALEF + FATHA + HAMZA_ON_ALEF + SUKUN, ALEF_MADDA),
    (HAMZA_ON_ALEF + FATHA + ALEF + SUKUN, ALEF_MADDA),
    # أُ + ؤْ  ->  أُو     (أُؤْكَلُ  ->  أُوكَلُ)
    (HAMZA_ON_ALEF + DAMMA + WAW_HAMZA + SUKUN, HAMZA_ON_ALEF + DAMMA + WAW),
    (HAMZA_ON_ALEF + DAMMA + HAMZA_ON_ALEF + SUKUN, HAMZA_ON_ALEF + DAMMA + WAW),
    # يُ + أْ  ->  يُؤْ     (يُأْكَلُ  ->  يُؤْكَلُ)
    (YA + DAMMA + HAMZA_ON_ALEF + SUKUN, YA + DAMMA + WAW_HAMZA + SUKUN),
    (TA + DAMMA + HAMZA_ON_ALEF + SUKUN, TA + DAMMA + WAW_HAMZA + SUKUN),
    (NOON + DAMMA + HAMZA_ON_ALEF + SUKUN, NOON + DAMMA + WAW_HAMZA + SUKUN),
)

# Hamza seat changes for a *non-initial* أ, driven by the adjacent long vowel.
#   قَرَأَا     -> قَرَآ
#   قَرَأُوا    -> قَرَؤُوا
#   تَقْرَأِينَ -> تَقْرَئِينَ
_HAMZA_SEAT_FIXES = (
    (HAMZA_ON_ALEF + FATHA + ALEF, ALEF_MADDA),
    (HAMZA_ON_ALEF + DAMMA + WAW, WAW_HAMZA + DAMMA + WAW),
    (HAMZA_ON_ALEF + KASRA + YA, YA_HAMZA + KASRA + YA),
)

# A final ن of the root merges with the ـنَ / ـنَا endings:
#   تَعَاوَنْنَ  -> تَعَاوَنَّ      كُنْنَا -> كُنَّا
_NOON_ASSIM = (
    (NOON + SUKUN + NOON + FATHA, NOON + SHADDA + FATHA),
)


def tidy(form: str) -> str:
    """Apply the obligatory orthographic / phonological adjustments."""
    if not form:
        return form

    for src, dst in _HAMZA_FIXES:
        if src in form:
            form = form.replace(src, dst)

    # seat changes only apply away from the start of the word, so that the
    # word-initial أُو of أُوكَلُ is not turned back into a hamza-on-waw.
    for src, dst in _HAMZA_SEAT_FIXES:
        idx = form.find(src, 1)
        while idx > 0:
            form = form[:idx] + dst + form[idx + len(src):]
            idx = form.find(src, idx + 1)

    for src, dst in _NOON_ASSIM:
        form = form.replace(src, dst)

    # never leave a doubled short vowel or sukun behind
    for v in SHORT_VOWELS:
        form = form.replace(v + v, v)
    form = form.replace(SUKUN + SUKUN, SUKUN)
    return canonical_marks(form)
