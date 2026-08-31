# -*- coding: utf-8 -*-
"""🧠 کیوں؟ — a plain-language explanation of every صیغہ.

For each form: what it is, who it refers to, how many, which gender, and why
the ending looks the way it does.
"""

import streamlit as st

from core.conjugation import TENSE_ORDER
from core.morphology import ArabicMorphology
from . import theme
from .theme import t

_TENSE_WHY = {
    'past_active': ('ماضی — گزرا ہوا وقت۔ کام ہو چکا۔',
                    'The past tense: the action has already happened.'),
    'present_active': ('مضارع — حال یا مستقبل۔ کام ہو رہا ہے یا ہو گا۔',
                       'The present/future tense: the action is happening or will happen.'),
    'past_passive': ('ماضی مجہول — کام کرنے والا معلوم نہیں، کام ہو چکا۔',
                     'The past passive: the doer is not named; the action was done.'),
    'present_passive': ('مضارع مجہول — کام کرنے والا معلوم نہیں، کام ہو رہا ہے۔',
                        'The present passive: the doer is not named; the action is being done.'),
    'imperative': ('امر — حکم دینا۔ صرف حاضر (تو، تم) کے صیغے آتے ہیں۔',
                   'The imperative: a command, so only the six second-person forms exist.'),
    'prohibition': ('نہی — منع کرنا۔ «لَا» کے ساتھ مضارع مجزوم آتا ہے۔',
                    'The prohibition: «لَا» plus the jussive of the present tense.'),
}

_PERSON_UR = {1: 'متکلم (بولنے والا)', 2: 'حاضر (جس سے بات ہو رہی ہے)',
              3: 'غائب (جس کے بارے میں بات ہو رہی ہے)'}
_PERSON_EN = {1: '1st person (the speaker)', 2: '2nd person (the one addressed)',
              3: '3rd person (the one spoken about)'}
_NUMBER_UR = {'singular': 'واحد (ایک)', 'dual': 'تثنیہ (دو)', 'plural': 'جمع (دو سے زیادہ)'}
_NUMBER_EN = {'singular': 'singular (one)', 'dual': 'dual (two)',
              'plural': 'plural (more than two)'}
_GENDER_UR = {'masculine': 'مذکر', 'feminine': 'مؤنث', 'common': 'مذکر و مؤنث'}
_GENDER_EN = {'masculine': 'masculine', 'feminine': 'feminine',
              'common': 'common (m/f)'}


def render_learning_view(verb_data: dict, conjugations: dict, lang: str = 'ur',
                         translations: dict = None, font_scale: float = 1.0):
    st.markdown(f'### {t("nav_learn", lang)}')

    vtype = ArabicMorphology.get_verb_type_info(verb_data.get('verb_type', 'sound'))
    theme.card(
        'بنیادی ساخت (Basic structure)',
        theme.fact_grid([
            (t('root', lang), verb_data.get('root', '')),
            (t('baab', lang), verb_data.get('baab_name_arabic', '')),
            (t('wazn', lang), verb_data.get('wazn', '')),
            (t('verb_type', lang), vtype.get('title_ur', '')),
        ]) +
        f'<div class="qa-info" style="margin-top:12px">{theme.esc(vtype.get("desc_ur",""))}</div>'
        f'<div class="qa-card" dir="ltr" style="text-align:left;margin-top:8px">'
        f'{theme.esc(vtype.get("desc_en",""))}</div>',
        lang)

    for key in TENSE_ORDER:
        rows = conjugations.get(key) or []
        if not rows:
            continue
        why_ur, why_en = _TENSE_WHY.get(key, ('', ''))
        with st.expander('📖 %s (%d %s)' % (t(key, lang), len(rows),
                                            t('sigha_count', lang))):
            st.markdown(f'<div class="qa-info">{theme.esc(why_ur)}</div>',
                        unsafe_allow_html=True)
            st.markdown(f'<div class="qa-card" dir="ltr" style="text-align:left">'
                        f'{theme.esc(why_en)}</div>', unsafe_allow_html=True)

            headers = [t('th_arabic', lang), t('th_pronoun', lang),
                       t('person', lang), t('number', lang), t('gender', lang),
                       t('th_urdu', lang)]
            classes = ['qa-ar', 'qa-pron', 'qa-ur', 'qa-ur', 'qa-ur', 'qa-ur']
            table_rows = [[
                r.get('arabic', ''), r.get('pronoun_arabic', ''),
                _PERSON_UR.get(r.get('person'), ''),
                _NUMBER_UR.get(r.get('number'), ''),
                _GENDER_UR.get(r.get('gender'), ''),
                r.get('meaning_urdu', ''),
            ] for r in rows]
            st.markdown(theme.simple_table(headers, table_rows, lang, classes),
                        unsafe_allow_html=True)

            headers_en = ['Arabic', 'Pronoun', 'Person', 'Number', 'Gender',
                          'English meaning']
            table_en = [[
                r.get('arabic', ''), r.get('pronoun_arabic', ''),
                _PERSON_EN.get(r.get('person'), ''),
                _NUMBER_EN.get(r.get('number'), ''),
                _GENDER_EN.get(r.get('gender'), ''),
                r.get('meaning_english', ''),
            ] for r in rows]
            st.markdown(theme.simple_table(headers_en, table_en, 'en',
                                           ['qa-ar', 'qa-pron', 'qa-en',
                                            'qa-en', 'qa-en', 'qa-en']),
                        unsafe_allow_html=True)
