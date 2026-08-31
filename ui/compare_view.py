# -*- coding: utf-8 -*-
"""⚖ تقابل — compare two verbs side by side.

Differences between the two are highlighted so a student can see what the باب
actually changes.
"""

import streamlit as st

from core.conjugation import TENSE_ORDER
from core.morphology import ArabicMorphology
from . import theme
from .theme import t


def render_compare_view(analyzer, lang: str = 'ur', translations: dict = None,
                        font_scale: float = 1.0):
    st.markdown('### %s' % t('compare', lang))

    verbs = getattr(analyzer, 'verbs', [])
    if not verbs:
        theme.notice(t('no_data', lang))
        return

    labels = {i: '%s — %s (%s)' % (v.get('arabic', ''),
                                   v.get('meaning_urdu', ''),
                                   v.get('baab_name_arabic', ''))
              for i, v in enumerate(verbs)}

    # default to two verbs of the same root, which is the instructive case
    default_a = 0
    default_b = next((i for i, v in enumerate(verbs)
                      if v.get('root') == verbs[0].get('root')
                      and v.get('id') != verbs[0].get('id')), min(1, len(verbs) - 1))

    col_a, col_b = st.columns(2)
    with col_a:
        idx_a = st.selectbox('پہلا فعل', list(labels), index=default_a,
                             format_func=lambda i: labels[i], key='cmp_a')
    with col_b:
        idx_b = st.selectbox('دوسرا فعل', list(labels), index=default_b,
                             format_func=lambda i: labels[i], key='cmp_b')

    v_a, v_b = verbs[idx_a], verbs[idx_b]
    conj_a = analyzer.conjugate(v_a)
    conj_b = analyzer.conjugate(v_b)
    na = t('not_applicable', lang)

    # ---- side-by-side facts, differences marked ------------------------
    type_a = ArabicMorphology.get_verb_type_info(v_a.get('verb_type', 'sound'))
    type_b = ArabicMorphology.get_verb_type_info(v_b.get('verb_type', 'sound'))

    fields = [
        (t('root', lang), v_a.get('root', ''), v_b.get('root', '')),
        (t('baab', lang), v_a.get('baab_name_arabic', ''),
         v_b.get('baab_name_arabic', '')),
        (t('wazn', lang), v_a.get('wazn', ''), v_b.get('wazn', '')),
        (t('past_active', lang), v_a.get('past_3ms') or '—',
         v_b.get('past_3ms') or '—'),
        (t('present_active', lang), v_a.get('present_3ms') or '—',
         v_b.get('present_3ms') or '—'),
        (t('past_passive', lang), v_a.get('past_passive_3ms') or na,
         v_b.get('past_passive_3ms') or na),
        (t('present_passive', lang), v_a.get('present_passive_3ms') or na,
         v_b.get('present_passive_3ms') or na),
        (t('masdar', lang), v_a.get('masdar') or '—', v_b.get('masdar') or '—'),
        (t('ism_fail', lang), v_a.get('ism_fail') or '—',
         v_b.get('ism_fail') or '—'),
        (t('ism_mafool', lang), v_a.get('ism_mafool') or na,
         v_b.get('ism_mafool') or na),
        (t('verb_type', lang), type_a.get('title_ur', ''),
         type_b.get('title_ur', '')),
        (t('transitivity', lang), v_a.get('transitivity', ''),
         v_b.get('transitivity', '')),
        (t('meaning_ur', lang), v_a.get('meaning_urdu', ''),
         v_b.get('meaning_urdu', '')),
        (t('meaning_en', lang), v_a.get('meaning_english', ''),
         v_b.get('meaning_english', '')),
    ]

    rows = []
    for label, val_a, val_b in fields:
        differs = (val_a != val_b)
        mark = ' ✱' if differs else ''
        rows.append([label, str(val_a) + mark, str(val_b) + mark])

    st.markdown(theme.simple_table(
        [t('th_sigha', lang), v_a.get('arabic', ''), v_b.get('arabic', '')],
        rows, lang, ['qa-ur', 'qa-ar', 'qa-ar']), unsafe_allow_html=True)
    theme.notice('✱ کے نشان والی سطریں دونوں افعال میں مختلف ہیں۔', 'info')

    # ---- gardaan side by side -------------------------------------------
    for key in TENSE_ORDER:
        rows_a = conj_a.get(key) or []
        rows_b = conj_b.get(key) or []
        if not rows_a and not rows_b:
            continue
        with st.expander('📖 %s' % t(key, lang), expanded=(key == 'past_active')):
            length = max(len(rows_a), len(rows_b))
            table_rows = []
            for i in range(length):
                a = rows_a[i] if i < len(rows_a) else {}
                b = rows_b[i] if i < len(rows_b) else {}
                pronoun = a.get('pronoun_arabic') or b.get('pronoun_arabic', '')
                table_rows.append([
                    pronoun,
                    a.get('arabic', na if not rows_a else '—'),
                    b.get('arabic', na if not rows_b else '—'),
                    a.get('meaning_urdu') or b.get('meaning_urdu', ''),
                ])
            st.markdown(theme.simple_table(
                [t('th_pronoun', lang), v_a.get('arabic', ''),
                 v_b.get('arabic', ''), t('th_urdu', lang)],
                table_rows, lang,
                ['qa-pron', 'qa-ar', 'qa-ar', 'qa-ur']),
                unsafe_allow_html=True)
