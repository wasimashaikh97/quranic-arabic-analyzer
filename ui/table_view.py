# -*- coding: utf-8 -*-
"""📊 جدول — the summary table plus the complete گردان of each tense.

The summary table is the one the specification asks for:

    | باب | مادہ | ماضی معروف | مضارع معروف | ماضی مجہول | مضارع مجہول |

Every row is clickable and opens that verb's complete گردان.
"""

import streamlit as st

from core.conjugation import TENSE_ORDER
from . import theme
from .theme import t


def render_table_view(verb_data: dict, conjugations: dict, lang: str = 'ur',
                      translations: dict = None, font_scale: float = 1.0,
                      analyzer=None, on_select=None):
    """Summary row for this verb + the six full gardaan tables."""
    st.markdown(f'### {t("nav_table", lang)}')

    # ---- the summary table, including every verb of the same root --------
    verbs = [verb_data]
    if analyzer:
        siblings = analyzer.get_verb_forms_for_root(verb_data.get('root', ''))
        if siblings:
            verbs = siblings

    render_summary_table(verbs, lang, analyzer=analyzer,
                         current_id=verb_data.get('id'), on_select=on_select)

    st.markdown('---')

    # ---- the complete gardaan, one tab per tense ------------------------
    labels = [t(key, lang) for key in TENSE_ORDER]
    tabs = st.tabs(labels)
    for tab, key in zip(tabs, TENSE_ORDER):
        with tab:
            rows = conjugations.get(key) or []
            if rows:
                st.markdown(theme.gardaan_table(rows, lang),
                            unsafe_allow_html=True)
            else:
                _unavailable(verb_data, key, lang)


def render_summary_table(verbs: list, lang: str = 'ur', analyzer=None,
                         current_id: str = None, on_select=None):
    """The باب | مادہ | four-principal-parts table, with clickable rows."""
    na = t('not_applicable', lang)

    headers = [t('baab', lang), t('root', lang), t('past_active', lang),
               t('present_active', lang), t('past_passive', lang),
               t('present_passive', lang)]
    classes = ['qa-ur', 'qa-pron', 'qa-ar', 'qa-ar', 'qa-ar', 'qa-ar']

    rows = []
    for v in verbs:
        rows.append([
            v.get('baab_name_arabic', ''),
            v.get('root', ''),
            v.get('past_3ms') or '—',
            v.get('present_3ms') or '—',
            v.get('past_passive_3ms') or na,
            v.get('present_passive_3ms') or na,
        ])

    st.markdown(theme.simple_table(headers, rows, lang, classes),
                unsafe_allow_html=True)

    # Streamlit cannot make an HTML row itself clickable, so every row gets a
    # large, clearly-labelled button underneath — easier to hit than a row.
    if on_select and len(verbs) > 0:
        st.markdown(f'**{t("view_gardaan", lang)}**')
        cols = st.columns(min(len(verbs), 4))
        for i, v in enumerate(verbs):
            with cols[i % len(cols)]:
                label = '%s — %s' % (v.get('arabic', ''),
                                     v.get('baab_name_arabic', ''))
                if st.button(label, key='tbl_row_%s' % v.get('id'),
                             use_container_width=True,
                             disabled=(v.get('id') == current_id)):
                    on_select(v)


def _unavailable(verb_data: dict, tense_key: str, lang: str):
    reason = verb_data.get('unavailable_note')
    text = '%s — %s' % (t('not_applicable', lang), t(tense_key, lang))
    theme.notice(text if not reason else '%s\n\n%s' % (text, reason))
