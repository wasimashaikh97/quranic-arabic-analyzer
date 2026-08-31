"""ابواب — the Arabic verb families as they are taught in Sarf textbooks.

Each باب carries its **Arabic name** (إفعال، تفعیل، مفاعلة …) together with the
four principal وزن of the pattern, its مصدر / اسم فاعل / اسم مفعول patterns and
an Urdu + English explanation of what the باب *does* to the meaning.

The eight ثلاثی مزید فیہ ابواب of the reference book are, in its order:

    ۱ إفعال      ۲ تفعیل     ۳ مفاعلة    ۴ تفعّل
    ۵ تفاعل      ۶ انفعال    ۷ افتعال    ۸ استفعال
"""

# ---------------------------------------------------------------------------
BAAB_INFO = {
    1: {
        'form': 1,
        'name_ar': 'ثلاثی مجرد',
        'name_ur': 'ثلاثی مجرد',
        'name_en': 'Form I — the bare triliteral',
        'category_ar': 'ثلاثی مجرد',
        'category_ur': 'ثلاثی مجرد',
        'is_mazeed': False,
        'wazn_past': 'فَعَلَ',
        'wazn_present': 'يَفْعُلُ / يَفْعِلُ / يَفْعَلُ',
        'wazn_past_passive': 'فُعِلَ',
        'wazn_present_passive': 'يُفْعَلُ',
        'masdar_pattern': 'فَعْل / فِعَالَة / فُعُول (سماعی)',
        'ism_fail_pattern': 'فَاعِل',
        'ism_mafool_pattern': 'مَفْعُول',
        'principal_parts': ('فَعَلَ', 'يَفْعُلُ', 'فُعِلَ', 'يُفْعَلُ'),
        'meaning_ur': 'یہ فعل کی اصل اور بنیادی صورت ہے۔ اس میں مادہ کے تین حروف کے علاوہ '
                      'کوئی زائد حرف نہیں ہوتا۔ اس کا مصدر سماعی ہوتا ہے یعنی لغت سے لیا جاتا ہے۔',
        'meaning_en': 'The bare three-letter verb with no added letters. Its مصدر is not '
                      'predictable from a pattern — it must be learnt from the dictionary.',
        'examples': ['كَتَبَ', 'نَصَرَ', 'ضَرَبَ', 'فَتَحَ', 'عَلِمَ', 'كَرُمَ'],
    },
    4: {
        'form': 4,
        'name_ar': 'إفعال',
        'name_ur': 'إفعال',
        'name_en': 'Form IV — إفعال',
        'category_ar': 'ثلاثی مزید فیہ',
        'category_ur': 'ثلاثی مزید فیہ',
        'is_mazeed': True,
        'order': 1,
        'wazn_past': 'أَفْعَلَ',
        'wazn_present': 'يُفْعِلُ',
        'wazn_past_passive': 'أُفْعِلَ',
        'wazn_present_passive': 'يُفْعَلُ',
        'masdar_pattern': 'إِفْعَال',
        'ism_fail_pattern': 'مُفْعِل',
        'ism_mafool_pattern': 'مُفْعَل',
        'principal_parts': ('أَفْعَلَ', 'يُفْعِلُ', 'أُفْعِلَ', 'يُفْعَلُ'),
        'meaning_ur': 'اس باب میں مادہ کے شروع میں ہمزہ بڑھایا جاتا ہے۔ عام طور پر یہ باب '
                      'فعل کو متعدی بنا دیتا ہے یعنی کام کرانے یا سبب بننے کا معنی دیتا ہے۔ '
                      'مثلاً «نَزَلَ» (اُترنا) سے «أَنْزَلَ» (اُتارنا، نازل کرنا)۔',
        'meaning_en': 'A hamza is added at the front. It normally makes the verb transitive '
                      '(causative): نَزَلَ “to come down” → أَنْزَلَ “to send down”.',
        'examples': ['أَنْزَلَ', 'أَخْرَجَ', 'أَرْسَلَ', 'أَدْخَلَ'],
    },
    2: {
        'form': 2,
        'name_ar': 'تفعیل',
        'name_ur': 'تفعیل',
        'name_en': 'Form II — تفعیل',
        'category_ar': 'ثلاثی مزید فیہ',
        'category_ur': 'ثلاثی مزید فیہ',
        'is_mazeed': True,
        'order': 2,
        'wazn_past': 'فَعَّلَ',
        'wazn_present': 'يُفَعِّلُ',
        'wazn_past_passive': 'فُعِّلَ',
        'wazn_present_passive': 'يُفَعَّلُ',
        'masdar_pattern': 'تَفْعِيل',
        'ism_fail_pattern': 'مُفَعِّل',
        'ism_mafool_pattern': 'مُفَعَّل',
        'principal_parts': ('فَعَّلَ', 'يُفَعِّلُ', 'فُعِّلَ', 'يُفَعَّلُ'),
        'meaning_ur': 'اس باب میں مادہ کا دوسرا حرف مشدد (دوہرا) کر دیا جاتا ہے۔ یہ باب '
                      'شدت، کثرت یا کام کرانے کا معنی دیتا ہے۔ مثلاً «عَلِمَ» (جاننا) سے '
                      '«عَلَّمَ» (سکھانا)۔',
        'meaning_en': 'The middle radical is doubled (shadda). It conveys intensity, '
                      'repetition, or causation: عَلِمَ “to know” → عَلَّمَ “to teach”.',
        'examples': ['عَلَّمَ', 'نَزَّلَ', 'كَوَّرَ', 'خَفَّفَ'],
    },
    3: {
        'form': 3,
        'name_ar': 'مفاعلة',
        'name_ur': 'مفاعلة',
        'name_en': 'Form III — مفاعلة',
        'category_ar': 'ثلاثی مزید فیہ',
        'category_ur': 'ثلاثی مزید فیہ',
        'is_mazeed': True,
        'order': 3,
        'wazn_past': 'فَاعَلَ',
        'wazn_present': 'يُفَاعِلُ',
        'wazn_past_passive': 'فُوعِلَ',
        'wazn_present_passive': 'يُفَاعَلُ',
        'masdar_pattern': 'مُفَاعَلَة / فِعَال',
        'ism_fail_pattern': 'مُفَاعِل',
        'ism_mafool_pattern': 'مُفَاعَل',
        'principal_parts': ('فَاعَلَ', 'يُفَاعِلُ', 'فُوعِلَ', 'يُفَاعَلُ'),
        'meaning_ur': 'اس باب میں مادہ کے پہلے حرف کے بعد الف بڑھایا جاتا ہے۔ یہ باب '
                      'باہمی عمل یعنی دو فریقوں کے درمیان کام کا معنی دیتا ہے۔ مثلاً '
                      '«قَتَلَ» (قتل کرنا) سے «قَاتَلَ» (ایک دوسرے سے لڑنا)۔',
        'meaning_en': 'An alif is inserted after the first radical. It expresses a mutual '
                      'or reciprocal action: قَتَلَ “to kill” → قَاتَلَ “to fight (each other)”.',
        'examples': ['قَاتَلَ', 'حَاسَبَ', 'نَادَى', 'نَاصَرَ'],
    },
    5: {
        'form': 5,
        'name_ar': "تفعّل",
        'name_ur': "تفعّل",
        'name_en': 'Form V — تفعّل',
        'category_ar': 'ثلاثی مزید فیہ',
        'category_ur': 'ثلاثی مزید فیہ',
        'is_mazeed': True,
        'order': 4,
        'wazn_past': 'تَفَعَّلَ',
        'wazn_present': 'يَتَفَعَّلُ',
        'wazn_past_passive': 'تُفُعِّلَ',
        'wazn_present_passive': 'يُتَفَعَّلُ',
        'masdar_pattern': 'تَفَعُّل',
        'ism_fail_pattern': 'مُتَفَعِّل',
        'ism_mafool_pattern': 'مُتَفَعَّل',
        'principal_parts': ('تَفَعَّلَ', 'يَتَفَعَّلُ', 'تُفُعِّلَ', 'يُتَفَعَّلُ'),
        'meaning_ur': 'یہ باب تفعیل کا مطاوع ہے۔ شروع میں «ت» بڑھتی ہے اور دوسرا حرف مشدد '
                      'رہتا ہے۔ معنی میں اثر قبول کرنا، تکلف یا بتدریج کرنا پایا جاتا ہے۔ '
                      'مثلاً «عَلَّمَ» (سکھانا) سے «تَعَلَّمَ» (سیکھنا)۔',
        'meaning_en': 'The reflexive of Form II — a ت is prefixed. It expresses accepting '
                      'the action upon oneself: عَلَّمَ “to teach” → تَعَلَّمَ “to learn”.',
        'examples': ['تَعَلَّمَ', 'تَقَبَّلَ', 'تَخَطَّفَ', 'تَنَزَّلَ'],
    },
    6: {
        'form': 6,
        'name_ar': 'تفاعل',
        'name_ur': 'تفاعل',
        'name_en': 'Form VI — تفاعل',
        'category_ar': 'ثلاثی مزید فیہ',
        'category_ur': 'ثلاثی مزید فیہ',
        'is_mazeed': True,
        'order': 5,
        'wazn_past': 'تَفَاعَلَ',
        'wazn_present': 'يَتَفَاعَلُ',
        'wazn_past_passive': 'تُفُوعِلَ',
        'wazn_present_passive': 'يُتَفَاعَلُ',
        'masdar_pattern': 'تَفَاعُل',
        'ism_fail_pattern': 'مُتَفَاعِل',
        'ism_mafool_pattern': 'مُتَفَاعَل',
        'principal_parts': ('تَفَاعَلَ', 'يَتَفَاعَلُ', 'تُفُوعِلَ', 'يُتَفَاعَلُ'),
        'meaning_ur': 'یہ باب مفاعلة کا مطاوع ہے۔ شروع میں «ت» اور پہلے حرف کے بعد الف '
                      'بڑھتا ہے۔ معنی باہمی شراکت یا ظاہر کرنے کا ہوتا ہے۔ مثلاً '
                      '«عَاوَنَ» سے «تَعَاوَنَ» (ایک دوسرے کی مدد کرنا)۔',
        'meaning_en': 'The reflexive of Form III: ت prefixed plus the inserted alif. It '
                      'expresses shared or pretended action: تَعَاوَنَ “to help one another”.',
        'examples': ['تَعَاوَنَ', 'تَنَافَسَ', 'تَدَاخَلَ'],
    },
    7: {
        'form': 7,
        'name_ar': 'انفعال',
        'name_ur': 'انفعال',
        'name_en': 'Form VII — انفعال',
        'category_ar': 'ثلاثی مزید فیہ',
        'category_ur': 'ثلاثی مزید فیہ',
        'is_mazeed': True,
        'order': 6,
        'wazn_past': 'اِنْفَعَلَ',
        'wazn_present': 'يَنْفَعِلُ',
        'wazn_past_passive': '—',
        'wazn_present_passive': '—',
        'masdar_pattern': 'اِنْفِعَال',
        'ism_fail_pattern': 'مُنْفَعِل',
        'ism_mafool_pattern': '—',
        'principal_parts': ('اِنْفَعَلَ', 'يَنْفَعِلُ', None, None),
        'meaning_ur': 'اس باب میں شروع میں «اِنْ» بڑھایا جاتا ہے۔ یہ ثلاثی مجرد کا مطاوع ہے '
                      'یعنی کام کا اثر قبول کرنا۔ چونکہ اس کا معنی خود ہی مجہول جیسا ہے، '
                      'اس لیے اس باب کا مجہول اور اسم مفعول استعمال نہیں ہوتا۔ مثلاً '
                      '«كَسَرَ» (توڑنا) سے «اِنْكَسَرَ» (ٹوٹ جانا)۔',
        'meaning_en': 'اِنْ is prefixed. It is the passive-reflexive of Form I — the subject '
                      'undergoes the action: كَسَرَ “to break” → اِنْكَسَرَ “to be broken”. '
                      'Because its meaning is already passive, this باب is intransitive and '
                      'has no passive voice and no اسم مفعول.',
        'examples': ['اِنْكَسَرَ', 'اِنْفَطَرَ', 'اِنْكَتَبَ'],
    },
    8: {
        'form': 8,
        'name_ar': 'افتعال',
        'name_ur': 'افتعال',
        'name_en': 'Form VIII — افتعال',
        'category_ar': 'ثلاثی مزید فیہ',
        'category_ur': 'ثلاثی مزید فیہ',
        'is_mazeed': True,
        'order': 7,
        'wazn_past': 'اِفْتَعَلَ',
        'wazn_present': 'يَفْتَعِلُ',
        'wazn_past_passive': 'اُفْتُعِلَ',
        'wazn_present_passive': 'يُفْتَعَلُ',
        'masdar_pattern': 'اِفْتِعَال',
        'ism_fail_pattern': 'مُفْتَعِل',
        'ism_mafool_pattern': 'مُفْتَعَل',
        'principal_parts': ('اِفْتَعَلَ', 'يَفْتَعِلُ', 'اُفْتُعِلَ', 'يُفْتَعَلُ'),
        'meaning_ur': 'اس باب میں شروع میں الف اور پہلے حرف کے بعد «ت» بڑھائی جاتی ہے۔ '
                      'معنی میں کوشش کرنا، اپنے لیے حاصل کرنا یا مطاوعت پائی جاتی ہے۔ '
                      'مثلاً «جَمَعَ» (جمع کرنا) سے «اِجْتَمَعَ» (جمع ہو جانا)۔',
        'meaning_en': 'An alif is prefixed and a ت inserted after the first radical. It '
                      'conveys doing something for oneself or with effort: جَمَعَ “to gather” '
                      '→ اِجْتَمَعَ “to gather together”.',
        'examples': ['اِجْتَمَعَ', 'اِخْتَلَفَ', 'اِرْتَفَعَ', 'اِنْتَفَعَ'],
    },
    10: {
        'form': 10,
        'name_ar': 'استفعال',
        'name_ur': 'استفعال',
        'name_en': 'Form X — استفعال',
        'category_ar': 'ثلاثی مزید فیہ',
        'category_ur': 'ثلاثی مزید فیہ',
        'is_mazeed': True,
        'order': 8,
        'wazn_past': 'اِسْتَفْعَلَ',
        'wazn_present': 'يَسْتَفْعِلُ',
        'wazn_past_passive': 'اُسْتُفْعِلَ',
        'wazn_present_passive': 'يُسْتَفْعَلُ',
        'masdar_pattern': 'اِسْتِفْعَال',
        'ism_fail_pattern': 'مُسْتَفْعِل',
        'ism_mafool_pattern': 'مُسْتَفْعَل',
        'principal_parts': ('اِسْتَفْعَلَ', 'يَسْتَفْعِلُ', 'اُسْتُفْعِلَ', 'يُسْتَفْعَلُ'),
        'meaning_ur': 'اس باب میں شروع میں «اِسْتَ» بڑھایا جاتا ہے۔ معنی میں طلب کرنا، '
                      'چاہنا یا کسی چیز کو اپنے لیے مانگنا پایا جاتا ہے۔ مثلاً «غَفَرَ» '
                      '(بخشنا) سے «اِسْتَغْفَرَ» (بخشش مانگنا)۔',
        'meaning_en': 'اِسْتَ is prefixed. It expresses seeking or requesting the meaning of '
                      'the root: غَفَرَ “to forgive” → اِسْتَغْفَرَ “to seek forgiveness”.',
        'examples': ['اِسْتَغْفَرَ', 'اِسْتَهْزَأَ', 'اِسْتَعْتَبَ', 'اِسْتَخْرَجَ'],
    },
    9: {
        'form': 9,
        'name_ar': 'افعلال',
        'name_ur': 'افعلال',
        'name_en': 'Form IX — افعلال',
        'category_ar': 'ثلاثی مزید فیہ',
        'category_ur': 'ثلاثی مزید فیہ',
        'is_mazeed': True,
        'order': 9,
        'listed_in_book': False,
        'wazn_past': 'اِفْعَلَّ',
        'wazn_present': 'يَفْعَلُّ',
        'wazn_past_passive': '—',
        'wazn_present_passive': '—',
        'masdar_pattern': 'اِفْعِلَال',
        'ism_fail_pattern': 'مُفْعَلّ',
        'ism_mafool_pattern': '—',
        'principal_parts': ('اِفْعَلَّ', 'يَفْعَلُّ', None, None),
        'meaning_ur': 'یہ باب رنگوں اور جسمانی عیوب کے لیے آتا ہے، جیسے «اِحْمَرَّ» '
                      '(سرخ ہو جانا)۔ یہ لازم ہوتا ہے، اس لیے مجہول نہیں آتا۔',
        'meaning_en': 'Used for colours and bodily defects, e.g. اِحْمَرَّ “to turn red”. '
                      'It is intransitive, so it has no passive.',
        'examples': ['اِحْمَرَّ'],
    },
}

#: the eight ثلاثی مزید فیہ ابواب, in the order used by the reference book
MAZEED_ORDER = [4, 2, 3, 5, 6, 7, 8, 10]

#: every باب the application knows about, مجرد first
ALL_BAAB_ORDER = [1] + MAZEED_ORDER + [9]


def get_baab(form) -> dict:
    """Look a باب up by its form number (1–10)."""
    try:
        form = int(form)
    except (TypeError, ValueError):
        form = 1
    return BAAB_INFO.get(form, BAAB_INFO[1])


def baab_name(form, lang: str = 'ur') -> str:
    info = get_baab(form)
    if lang == 'en':
        return info['name_en']
    return info['name_ar']


def baab_label(form, lang: str = 'ur') -> str:
    """A short human label, e.g. «إفعال (باب ۴)»."""
    info = get_baab(form)
    if lang == 'en':
        return '%s (Form %s)' % (info['name_ar'], info['form'])
    return '%s (باب %s)' % (info['name_ar'], _arabic_numeral(info['form']))


_AR_DIGITS = '٠١٢٣٤٥٦٧٨٩'


def _arabic_numeral(n) -> str:
    return ''.join(_AR_DIGITS[int(d)] for d in str(n))


def mazeed_abwaab() -> list:
    """The eight ابواب ثلاثی مزید فیہ in book order."""
    return [BAAB_INFO[f] for f in MAZEED_ORDER]


def all_abwaab() -> list:
    return [BAAB_INFO[f] for f in ALL_BAAB_ORDER]


def detect_baab(past_3ms: str, root_letters=None) -> int:
    """Best-effort باب detection from a diacritised ماضی form.

    Used only as a *hint* when the verb is not in the lexicon — never to
    fabricate a conjugation.
    """
    from .arabic_utils import strip_marks, split_units, SHADDA

    bare = strip_marks(past_3ms or '')
    units = split_units(past_3ms or '')
    n_letters = len(bare)

    if bare.startswith('است') and n_letters >= 6:
        return 10
    if bare.startswith('ان') and n_letters >= 5:
        return 7
    if bare.startswith('ت') and n_letters >= 5 and bare[2:3] == 'ا':
        return 6
    if bare.startswith('ت') and n_letters >= 4 and _has_shadda(units, SHADDA):
        return 5
    if bare.startswith('ت') and n_letters >= 4:
        return 5
    if bare.startswith('ا') and n_letters >= 5 and bare[2:3] == 'ت':
        return 8
    if bare[:1] in ('أ', 'ا') and n_letters == 4:
        return 4
    if n_letters >= 4 and bare[1:2] == 'ا':
        return 3
    if _has_shadda(units, SHADDA) and n_letters == 3:
        return 2
    return 1


def _has_shadda(units, shadda) -> bool:
    return any(shadda in marks for _letter, marks in units)
