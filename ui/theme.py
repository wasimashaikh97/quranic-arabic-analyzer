# -*- coding: utf-8 -*-
"""Shared look-and-feel, translations and HTML builders for every view.

The design target is an **older Quran student**: a light, high-contrast,
print-like page with very large Arabic, generous spacing, RTL throughout, and
no developer vocabulary anywhere on screen.
"""

import streamlit as st

# ---------------------------------------------------------------------------
# palette — light, high contrast, matching the printed sheet
# ---------------------------------------------------------------------------
C = {
    'page': '#fbfaf6',
    'card': '#ffffff',
    'ink': '#1f2937',
    'ink_soft': '#4b5563',
    'ink_faint': '#6b7280',
    'brand': '#14532d',
    'brand_mid': '#166534',
    'brand_soft': '#dcfce7',
    'brand_edge': '#86efac',
    'accent': '#92400e',
    'accent_soft': '#fef3c7',
    'line': '#d1d5db',
    'row_alt': '#f6f6f2',
    'warn_bg': '#fffbeb',
    'warn_edge': '#f59e0b',
}

ARABIC_STACK = ("'Amiri', 'Noto Naskh Arabic', 'Scheherazade New', "
                "'Traditional Arabic', serif")
URDU_STACK = ("'Noto Nastaliq Urdu', 'Jameel Noori Nastaleeq', 'Amiri', serif")

LANGS = {'ur': 'اردو', 'ar': 'العربية', 'en': 'English'}
RTL_LANGS = ('ur', 'ar')

# ---------------------------------------------------------------------------
# translations
# ---------------------------------------------------------------------------
_T = {
    # --- chrome -----------------------------------------------------------
    'app_title': {'ur': '📖 عربی فعل اور گردان',
                  'ar': '📖 الأفعال العربية وتصريفها',
                  'en': '📖 Arabic Verbs & Conjugation'},
    'app_subtitle': {
        'ur': 'قرآنی عربی کے افعال، ابواب اور مکمل گردان — آسان اور مستند',
        'ar': 'أفعال العربية القرآنية وأبوابها وتصريفها الكامل',
        'en': 'Quranic Arabic verbs, their Baab, and the complete conjugation'},
    'enter_verb': {'ur': 'عربی لفظ لکھیں:',
                   'ar': 'اكتب الكلمة العربية:',
                   'en': 'Enter an Arabic word:'},
    'analyze': {'ur': '🔍 تجزیہ کریں', 'ar': '🔍 حلّل', 'en': '🔍 Analyse'},
    'examples': {'ur': 'مثالیں — کسی پر دبائیں:',
                 'ar': 'أمثلة — اضغط على أي منها:',
                 'en': 'Examples — tap any one:'},
    'language': {'ur': 'زبان', 'ar': 'اللغة', 'en': 'Language'},
    'text_size': {'ur': '👓 بڑا متن', 'ar': '👓 حجم الخط', 'en': '👓 Text size'},
    'reset_size': {'ur': 'اصل سائز', 'ar': 'الحجم الأصلي', 'en': 'Normal size'},
    'home': {'ur': '🏠 پہلا صفحہ', 'ar': '🏠 الصفحة الأولى', 'en': '🏠 Home'},
    'back': {'ur': '↩ واپس', 'ar': '↩ رجوع', 'en': '↩ Back'},

    # --- result header ----------------------------------------------------
    'verb_info': {'ur': '📖 فعل کی معلومات',
                  'ar': '📖 معلومات الفعل',
                  'en': '📖 Verb information'},
    'verb': {'ur': 'فعل', 'ar': 'الفعل', 'en': 'Verb'},
    'root': {'ur': 'مادہ', 'ar': 'المادة', 'en': 'Root'},
    'baab': {'ur': 'باب', 'ar': 'الباب', 'en': 'Baab (family)'},
    'wazn': {'ur': 'وزن', 'ar': 'الوزن', 'en': 'Pattern (Wazn)'},
    'meaning_ur': {'ur': 'اردو معنی', 'ar': 'المعنى بالأردية', 'en': 'Urdu meaning'},
    'meaning_en': {'ur': 'English Meaning', 'ar': 'المعنى بالإنجليزية',
                   'en': 'English meaning'},
    'verb_type': {'ur': 'فعل کی قسم', 'ar': 'نوع الفعل', 'en': 'Verb type'},
    'transitivity': {'ur': 'متعدی / لازم', 'ar': 'متعدٍّ / لازم',
                     'en': 'Transitive / Intransitive'},
    'masdar': {'ur': 'مصدر', 'ar': 'المصدر', 'en': 'Masdar'},
    'ism_fail': {'ur': 'اسم فاعل', 'ar': 'اسم الفاعل', 'en': "Ism Fa'il"},
    'ism_mafool': {'ur': 'اسم مفعول', 'ar': 'اسم المفعول', 'en': "Ism Maf'ool"},

    # --- navigation -------------------------------------------------------
    'nav_table': {'ur': '📊 جدول', 'ar': '📊 جدول', 'en': '📊 Table'},
    'nav_tree': {'ur': '🌳 درخت', 'ar': '🌳 شجرة', 'en': '🌳 Tree'},
    'nav_sarf': {'ur': '📚 مکمل صرف', 'ar': '📚 الصرف الكامل',
                 'en': '📚 Complete Sarf'},
    'nav_afaal': {'ur': '📚 تمام افعال', 'ar': '📚 جميع الأفعال',
                  'en': '📚 All verbs of this root'},
    'nav_abwaab': {'ur': '📚 آٹھ ابواب', 'ar': '📚 الأبواب الثمانية',
                   'en': '📚 The eight Abwaab'},
    'nav_gardaan': {'ur': '📖 مکمل گردان', 'ar': '📖 التصريف الكامل',
                    'en': '📖 Complete Gardaan'},
    'nav_quran': {'ur': '📖 قرآن میں استعمال', 'ar': '📖 في القرآن',
                  'en': '📖 In the Quran'},
    'nav_learn': {'ur': '🧠 کیوں؟', 'ar': '🧠 لماذا؟', 'en': '🧠 Why?'},

    # --- tenses -----------------------------------------------------------
    'past_active': {'ur': 'ماضی معروف', 'ar': 'الماضي المعروف',
                    'en': 'Past Active'},
    'present_active': {'ur': 'مضارع معروف', 'ar': 'المضارع المعروف',
                       'en': 'Present Active'},
    'past_passive': {'ur': 'ماضی مجہول', 'ar': 'الماضي المجهول',
                     'en': 'Past Passive'},
    'present_passive': {'ur': 'مضارع مجہول', 'ar': 'المضارع المجهول',
                        'en': 'Present Passive'},
    'imperative': {'ur': 'امر', 'ar': 'الأمر', 'en': 'Imperative'},
    'prohibition': {'ur': 'نہی', 'ar': 'النهي', 'en': 'Prohibition'},

    # --- table headings ---------------------------------------------------
    'th_pronoun': {'ur': 'ضمیر', 'ar': 'الضمير', 'en': 'Pronoun'},
    'th_sigha': {'ur': 'صیغہ', 'ar': 'الصيغة', 'en': 'Form (Sigha)'},
    'th_arabic': {'ur': 'عربی', 'ar': 'العربية', 'en': 'Arabic'},
    'th_urdu': {'ur': 'اردو', 'ar': 'الأردية', 'en': 'Urdu'},
    'th_english': {'ur': 'English', 'ar': 'الإنجليزية', 'en': 'English'},

    # --- messages ---------------------------------------------------------
    'not_applicable': {'ur': 'قابلِ اطلاق نہیں', 'ar': 'غير منطبق',
                       'en': 'Not applicable'},
    'no_data': {'ur': 'اس لفظ کی مستند صرفی معلومات دستیاب نہیں۔',
                'ar': 'لا تتوفر معلومات صرفية موثوقة لهذه الكلمة.',
                'en': 'No verified morphological data is available for this word.'},
    'not_verified': {
        'ur': 'اس باب میں اس مادہ کا مستند فعل دستیاب نہیں — اس لیے یہاں کوئی '
              'فعل نہیں بنایا گیا۔',
        'ar': 'لا يوجد فعل موثوق لهذه المادة في هذا الباب.',
        'en': 'No attested verb exists for this root in this Baab, so none has '
              'been invented here.'},
    'try_these': {'ur': 'اسی مادہ کے دستیاب افعال:',
                  'ar': 'الأفعال المتوفرة من هذه المادة:',
                  'en': 'Verified verbs from this root:'},
    'ambiguous': {'ur': 'یہ لفظ ایک سے زیادہ صیغوں کے ساتھ ملتا ہے:',
                  'ar': 'تنطبق هذه الكلمة على أكثر من صيغة:',
                  'en': 'This word matches more than one form:'},

    # --- conjugated input -------------------------------------------------
    'parsed_as': {'ur': '⚡ آپ کا لکھا ہوا لفظ',
                  'ar': '⚡ الكلمة التي كتبتها',
                  'en': '⚡ The word you typed'},
    'base_verb': {'ur': 'اصل فعل', 'ar': 'الفعل الأصلي', 'en': 'Dictionary form'},
    'tense': {'ur': 'زمانہ / صورت', 'ar': 'الزمن', 'en': 'Tense'},
    'person': {'ur': 'شخص', 'ar': 'الشخص', 'en': 'Person'},
    'number': {'ur': 'تعداد', 'ar': 'العدد', 'en': 'Number'},
    'gender': {'ur': 'جنس', 'ar': 'الجنس', 'en': 'Gender'},

    # --- pdf --------------------------------------------------------------
    'download_pdf': {'ur': '📥 PDF ڈاؤن لوڈ کریں', 'ar': '📥 تحميل PDF',
                     'en': '📥 Download PDF'},
    'pdf_one_page': {'ur': '📄 ایک صفحے کا مکمل چارٹ (پرنٹ کے لیے)',
                     'ar': '📄 صفحة واحدة كاملة (للطباعة)',
                     'en': '📄 Complete one-page chart (for printing)'},
    'pdf_detailed': {'ur': '📚 تفصیلی کتابچہ (ہر صیغے کا ترجمہ)',
                     'ar': '📚 كتيّب مفصّل', 'en': '📚 Detailed booklet'},
    'pdf_prepare': {'ur': 'PDF تیار کریں', 'ar': 'إنشاء PDF', 'en': 'Create PDF'},
    'pdf_click': {'ur': '⬇ فائل محفوظ کریں', 'ar': '⬇ حفظ الملف',
                  'en': '⬇ Save the file'},

    # --- misc -------------------------------------------------------------
    'save': {'ur': '⭐ محفوظ کریں', 'ar': '⭐ احفظ', 'en': '⭐ Save'},
    'saved': {'ur': '★ محفوظ شدہ', 'ar': '★ محفوظ', 'en': '★ Saved'},
    'listen': {'ur': '🔊 تلفظ سنیں', 'ar': '🔊 استمع', 'en': '🔊 Listen'},
    'compare': {'ur': '⚖ تقابل', 'ar': '⚖ مقارنة', 'en': '⚖ Compare'},
    'practice': {'ur': '✍ مشق', 'ar': '✍ تمرين', 'en': '✍ Practice'},
    'flashcards': {'ur': '🗂 فلیش کارڈ', 'ar': '🗂 بطاقات', 'en': '🗂 Flashcards'},
    'dashboard': {'ur': '📊 میری پیش رفت', 'ar': '📊 تقدمي', 'en': '📊 My progress'},
    'bookmarks': {'ur': '⭐ محفوظ افعال', 'ar': '⭐ المحفوظات',
                  'en': '⭐ Saved verbs'},
    'recent': {'ur': '🕘 حالیہ', 'ar': '🕘 الأخيرة', 'en': '🕘 Recent'},
    'open': {'ur': 'کھولیں', 'ar': 'افتح', 'en': 'Open'},
    'view_gardaan': {'ur': '📖 گردان دیکھیں', 'ar': '📖 شاهد التصريف',
                     'en': '📖 View conjugation'},
    'derived': {'ur': 'مشتقات', 'ar': 'المشتقات', 'en': 'Derived words'},
    'related_afaal': {'ur': 'اسی مادہ کے دیگر افعال',
                      'ar': 'أفعال أخرى من المادة',
                      'en': 'Other verbs from this root'},
    'hierarchy': {'ur': 'شجری خاکہ', 'ar': 'المخطط الشجري', 'en': 'Hierarchy'},
    'available': {'ur': 'دستیاب', 'ar': 'متوفر', 'en': 'Available'},
    'unavailable': {'ur': 'دستیاب نہیں', 'ar': 'غير متوفر', 'en': 'Not available'},
    'sigha_count': {'ur': 'صیغے', 'ar': 'صيغة', 'en': 'forms'},
}


def t(key: str, lang: str = 'ur') -> str:
    entry = _T.get(key)
    if not entry:
        return key
    return entry.get(lang) or entry.get('ur') or key


def is_rtl(lang: str) -> bool:
    return lang in RTL_LANGS


def direction(lang: str) -> str:
    return 'rtl' if is_rtl(lang) else 'ltr'


def align(lang: str) -> str:
    return 'right' if is_rtl(lang) else 'left'


# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------
def inject_css(font_scale: float = 1.0, lang: str = 'ur'):
    base = round(17 * font_scale, 1)
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Noto+Naskh+Arabic:wght@400;500;600;700&family=Noto+Nastaliq+Urdu:wght@400;600&display=swap');

    /* ---------- page ---------- */
    .stApp {{ background: {C['page']}; }}
    html, body, [class*="css"], .stMarkdown, .stButton button {{
        font-family: {ARABIC_STACK};
        font-size: {base}px;
        color: {C['ink']};
    }}
    .block-container {{
        padding-top: 1.1rem; padding-bottom: 3rem;
        max-width: 1250px;
    }}
    #MainMenu, footer {{ visibility: hidden; }}

    /* ---------- header ---------- */
    .qa-header {{
        background: linear-gradient(135deg, {C['brand']} 0%, {C['brand_mid']} 100%);
        border-radius: 18px; padding: 26px 20px; text-align: center;
        margin-bottom: 18px; box-shadow: 0 6px 18px rgba(20,83,45,.18);
    }}
    .qa-title {{
        font-size: {2.5 * font_scale:.2f}em; font-weight: 700;
        color: #fef3c7; margin: 0 0 6px 0; line-height: 1.35;
    }}
    .qa-subtitle {{
        font-size: {1.15 * font_scale:.2f}em; color: #dcfce7; margin: 0;
        line-height: 1.7;
    }}

    /* ---------- cards ---------- */
    .qa-card {{
        background: {C['card']}; border: 2px solid {C['line']};
        border-radius: 16px; padding: 20px 22px; margin-bottom: 16px;
    }}
    .qa-card-title {{
        font-size: {1.5 * font_scale:.2f}em; font-weight: 700;
        color: {C['brand']}; margin: 0 0 14px 0;
        border-bottom: 3px solid {C['brand_soft']}; padding-bottom: 8px;
    }}

    /* ---------- the verb banner ---------- */
    .qa-verb-banner {{
        background: {C['card']}; border: 3px solid {C['brand_edge']};
        border-radius: 18px; padding: 22px; text-align: center;
        margin-bottom: 16px;
    }}
    .qa-verb {{
        font-size: {3.6 * font_scale:.2f}em; font-weight: 700;
        color: {C['accent']}; line-height: 1.5; margin: 0;
        font-family: {ARABIC_STACK};
    }}
    .qa-verb-meaning {{
        font-size: {1.35 * font_scale:.2f}em; color: {C['brand']};
        margin-top: 6px; line-height: 1.8;
    }}
    .qa-verb-meaning-en {{
        font-size: {1.05 * font_scale:.2f}em; color: {C['ink_soft']};
        direction: ltr;
    }}

    /* ---------- fact grid ---------- */
    .qa-grid {{
        display: grid; gap: 12px;
        grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
    }}
    .qa-fact {{
        background: {C['brand_soft']}; border-radius: 12px;
        padding: 12px 14px; border-right: 6px solid {C['brand']};
        text-align: right; direction: rtl;
    }}
    .qa-fact-label {{
        font-size: {0.95 * font_scale:.2f}em; color: {C['ink_faint']};
        margin-bottom: 3px;
    }}
    .qa-fact-value {{
        font-size: {1.6 * font_scale:.2f}em; font-weight: 700;
        color: {C['accent']}; line-height: 1.6; word-break: break-word;
    }}
    .qa-fact-value-sm {{
        font-size: {1.15 * font_scale:.2f}em; font-weight: 600;
        color: {C['brand']}; line-height: 1.8;
    }}

    /* ---------- tables ---------- */
    .qa-table-wrap {{ overflow-x: auto; -webkit-overflow-scrolling: touch; }}
    table.qa-table {{
        width: 100%; border-collapse: collapse; background: {C['card']};
        border: 2px solid {C['brand']}; border-radius: 12px; overflow: hidden;
        min-width: 520px;
    }}
    table.qa-table thead tr {{ background: {C['brand']}; }}
    table.qa-table th {{
        color: #ffffff; padding: 12px 10px; font-weight: 700;
        font-size: {1.05 * font_scale:.2f}em; text-align: center;
        white-space: nowrap;
    }}
    table.qa-table td {{
        padding: 11px 10px; border-bottom: 1px solid {C['line']};
        text-align: center; vertical-align: middle;
        font-size: {1.0 * font_scale:.2f}em; line-height: 1.9;
    }}
    table.qa-table tbody tr:nth-child(even) {{ background: {C['row_alt']}; }}
    table.qa-table tbody tr:hover {{ background: {C['brand_soft']}; }}
    td.qa-ar {{
        font-family: {ARABIC_STACK}; color: {C['accent']};
        font-weight: 700; font-size: {1.6 * font_scale:.2f}em;
        direction: rtl; white-space: nowrap;
    }}
    td.qa-pron {{
        font-family: {ARABIC_STACK}; color: {C['ink']};
        font-size: {1.2 * font_scale:.2f}em; direction: rtl; white-space: nowrap;
    }}
    td.qa-ur {{ direction: rtl; text-align: right; color: {C['ink']}; }}
    td.qa-en {{ direction: ltr; text-align: left; color: {C['ink_soft']}; }}
    td.qa-na {{ color: {C['ink_faint']}; font-style: normal; }}
    .qa-num {{ color: {C['ink_faint']}; font-size: .9em; }}

    /* ---------- notices ---------- */
    .qa-note {{
        background: {C['warn_bg']}; border: 2px solid {C['warn_edge']};
        border-radius: 12px; padding: 14px 16px; margin: 12px 0;
        direction: rtl; text-align: right;
        font-size: {1.1 * font_scale:.2f}em; line-height: 1.9;
        color: {C['accent']};
    }}
    .qa-info {{
        background: {C['brand_soft']}; border: 2px solid {C['brand_edge']};
        border-radius: 12px; padding: 14px 16px; margin: 12px 0;
        direction: rtl; text-align: right;
        font-size: {1.1 * font_scale:.2f}em; line-height: 1.9;
        color: {C['brand']};
    }}

    /* ---------- tree ---------- */
    .qa-node {{
        background: {C['card']}; border: 2px solid {C['brand_edge']};
        border-radius: 14px; padding: 12px 16px; text-align: center;
        direction: rtl;
    }}
    .qa-node-label {{ font-size: {0.95 * font_scale:.2f}em; color: {C['ink_faint']}; }}
    .qa-node-value {{
        font-size: {1.8 * font_scale:.2f}em; font-weight: 700;
        color: {C['accent']}; line-height: 1.6;
    }}
    .qa-connector {{
        width: 4px; height: 20px; background: {C['brand_edge']};
        margin: 0 auto;
    }}

    /* ---------- buttons ---------- */
    .stButton > button {{
        font-family: {ARABIC_STACK};
        font-size: {1.2 * font_scale:.2f}em !important;
        font-weight: 700 !important;
        border-radius: 14px !important;
        padding: 0.7em 1.1em !important;
        border: 2px solid {C['brand']} !important;
        background: {C['card']} !important;
        color: {C['brand']} !important;
        line-height: 1.6 !important;
        min-height: 3em;
    }}
    .stButton > button:hover {{
        background: {C['brand_soft']} !important;
        border-color: {C['brand_mid']} !important;
    }}
    .stButton > button[kind="primary"] {{
        background: {C['brand']} !important; color: #ffffff !important;
        font-size: {1.45 * font_scale:.2f}em !important;
    }}
    .stButton > button[kind="primary"]:hover {{
        background: {C['brand_mid']} !important;
    }}
    .stDownloadButton > button {{
        font-size: {1.2 * font_scale:.2f}em !important;
        font-weight: 700 !important; border-radius: 14px !important;
        background: {C['accent']} !important; color: #fff !important;
        border: none !important; padding: 0.7em 1.1em !important;
    }}

    /* ---------- inputs ---------- */
    .stTextInput > div > div > input {{
        font-family: {ARABIC_STACK};
        font-size: {2.0 * font_scale:.2f}em !important;
        text-align: center; direction: rtl;
        padding: 0.55em !important; height: auto !important;
        border: 3px solid {C['brand']} !important;
        border-radius: 14px !important;
        background: {C['card']} !important;
        color: {C['ink']} !important;
    }}
    .stTextInput label, .stSelectbox label, .stRadio label {{
        font-size: {1.2 * font_scale:.2f}em !important;
        font-weight: 700 !important; color: {C['brand']} !important;
    }}

    /* ---------- expanders & tabs ---------- */
    .streamlit-expanderHeader, details summary {{
        font-size: {1.2 * font_scale:.2f}em !important; font-weight: 700 !important;
        color: {C['brand']} !important;
    }}
    .stTabs [data-baseweb="tab"] {{
        font-size: {1.1 * font_scale:.2f}em; font-weight: 700;
        padding: 10px 16px;
    }}

    /* ---------- mobile ---------- */
    @media (max-width: 720px) {{
        .block-container {{ padding-left: .6rem; padding-right: .6rem; }}
        .qa-title {{ font-size: {1.7 * font_scale:.2f}em; }}
        .qa-verb {{ font-size: {2.5 * font_scale:.2f}em; }}
        .qa-grid {{ grid-template-columns: 1fr 1fr; }}
        table.qa-table {{ min-width: 460px; }}
        .stButton > button {{ font-size: {1.05 * font_scale:.2f}em !important; }}
    }}
    @media (max-width: 460px) {{
        .qa-grid {{ grid-template-columns: 1fr; }}
    }}

    /* ---------- print ---------- */
    @media print {{
        .stButton, .stDownloadButton, header, .qa-noprint {{ display: none !important; }}
        .stApp {{ background: #fff; }}
    }}
    </style>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# HTML builders
# ---------------------------------------------------------------------------
def esc(text) -> str:
    """Minimal escaping — the data is ours, but keep the markup valid."""
    if text is None:
        return ''
    return (str(text).replace('&', '&amp;').replace('<', '&lt;')
            .replace('>', '&gt;'))


def header(lang: str = 'ur'):
    st.markdown(
        f"""<div class="qa-header">
            <div class="qa-title">{esc(t('app_title', lang))}</div>
            <div class="qa-subtitle">{esc(t('app_subtitle', lang))}</div>
        </div>""", unsafe_allow_html=True)


def card(title: str, body_html: str, lang: str = 'ur'):
    st.markdown(
        f"""<div class="qa-card" dir="{direction(lang)}">
            <div class="qa-card-title">{esc(title)}</div>
            {body_html}
        </div>""", unsafe_allow_html=True)


def fact_grid(facts, small_keys=()) -> str:
    """``facts`` is a list of ``(label, value)`` pairs."""
    cells = []
    for label, value in facts:
        klass = ('qa-fact-value-sm' if label in small_keys
                 else 'qa-fact-value')
        cells.append(
            f'<div class="qa-fact">'
            f'<div class="qa-fact-label">{esc(label)}</div>'
            f'<div class="{klass}">{esc(value) if value not in (None, "") else "—"}</div>'
            f'</div>')
    return '<div class="qa-grid">%s</div>' % ''.join(cells)


def notice(text: str, kind: str = 'note'):
    klass = 'qa-note' if kind == 'note' else 'qa-info'
    st.markdown(f'<div class="{klass}">{esc(text)}</div>', unsafe_allow_html=True)


def gardaan_table(rows, lang: str = 'ur', show_meanings: bool = True,
                  na_text: str = None) -> str:
    """Build one gardaan table: # | ضمیر | صیغہ | عربی | اردو | English."""
    if not rows:
        return (f'<div class="qa-note">{esc(na_text or t("not_applicable", lang))}'
                f'</div>')

    heads = ['#', t('th_pronoun', lang), t('th_sigha', lang), t('th_arabic', lang)]
    if show_meanings:
        heads += [t('th_urdu', lang), t('th_english', lang)]
    if is_rtl(lang):
        heads = list(reversed(heads))

    body = []
    for i, row in enumerate(rows, start=1):
        cells = [
            f'<td class="qa-num">{i}</td>',
            f'<td class="qa-pron">{esc(row.get("pronoun_arabic"))}</td>',
            f'<td class="qa-ur">{esc(row.get("sigha_urdu"))}</td>',
            f'<td class="qa-ar">{esc(row.get("arabic"))}</td>',
        ]
        if show_meanings:
            cells += [
                f'<td class="qa-ur">{esc(row.get("meaning_urdu"))}</td>',
                f'<td class="qa-en">{esc(row.get("meaning_english"))}</td>',
            ]
        if is_rtl(lang):
            cells = list(reversed(cells))
        body.append('<tr>%s</tr>' % ''.join(cells))

    return (
        '<div class="qa-table-wrap"><table class="qa-table">'
        '<thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>'
        % (''.join('<th>%s</th>' % esc(h) for h in heads), ''.join(body)))


def simple_table(headers, rows, lang: str = 'ur', cell_classes=None) -> str:
    """Generic table; ``rows`` is a list of lists of already-stringified cells."""
    cell_classes = cell_classes or [''] * len(headers)
    heads = list(headers)
    if is_rtl(lang):
        heads = list(reversed(heads))

    body = []
    for row in rows:
        cells = ['<td class="%s">%s</td>' % (cell_classes[i] if i < len(cell_classes)
                                             else '', esc(v))
                 for i, v in enumerate(row)]
        if is_rtl(lang):
            cells = list(reversed(cells))
        body.append('<tr>%s</tr>' % ''.join(cells))

    return (
        '<div class="qa-table-wrap"><table class="qa-table">'
        '<thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>'
        % (''.join('<th>%s</th>' % esc(h) for h in heads), ''.join(body)))
