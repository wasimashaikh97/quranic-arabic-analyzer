# -*- coding: utf-8 -*-
"""📖 مکمل گردان — the traditional conjugation tables, one after another."""

import streamlit as st

from core.conjugation import TENSE_ORDER
from . import theme
from .theme import t


def render_gardaan_view(verb_data: dict, conjugations: dict, lang: str = 'ur',
                        translations: dict = None, font_scale: float = 1.0,
                        only_tense: str = None):
    na = t('not_applicable', lang)

    st.markdown(
        f"""<div class="qa-verb-banner">
            <div class="qa-verb">{theme.esc(verb_data.get('arabic',''))}</div>
            <div class="qa-verb-meaning">
                {theme.esc(verb_data.get('meaning_urdu',''))}
                &nbsp;·&nbsp; {theme.esc(verb_data.get('root',''))}
                &nbsp;·&nbsp; {theme.esc(verb_data.get('baab_name_arabic',''))}
                &nbsp;·&nbsp; {theme.esc(verb_data.get('wazn',''))}
            </div>
            <div class="qa-verb-meaning-en">
                {theme.esc(verb_data.get('meaning_english',''))}</div>
        </div>""", unsafe_allow_html=True)

    keys = [only_tense] if only_tense else TENSE_ORDER
    for key in keys:
        rows = conjugations.get(key) or []
        st.markdown(
            f'<div class="qa-card-title" dir="rtl">{theme.esc(t(key, lang))}'
            f'{" — %d %s" % (len(rows), t("sigha_count", lang)) if rows else ""}'
            f'</div>', unsafe_allow_html=True)
        if rows:
            st.markdown(theme.gardaan_table(rows, lang), unsafe_allow_html=True)
        else:
            theme.notice('%s — %s' % (na, verb_data.get('unavailable_note') or ''))
        st.markdown('<br>', unsafe_allow_html=True)
