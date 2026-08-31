# -*- coding: utf-8 -*-
"""📚 تمام افعال — every verified verb of one root, grouped by باب.

A باب with no attested verb for this root is shown as an explicit gap.  The
application never manufactures a verb just because the pattern would allow it.
"""

import streamlit as st

from . import theme
from .theme import t


def render_afaal_view(verb_data: dict, analyzer, lang: str = 'ur',
                      translations: dict = None, font_scale: float = 1.0,
                      on_select=None):
    root = verb_data.get('root', '')
    st.markdown(f'### {t("nav_afaal", lang)} — {theme.esc(root)}')

    root_info = analyzer.get_root_info(root)
    if root_info.get('basic_meaning_urdu'):
        st.markdown(theme.fact_grid([
            (t('root', lang), root),
            ('بنیادی معنی', root_info.get('basic_meaning_urdu', '')),
            ('Basic sense', root_info.get('basic_meaning_english', '')),
        ], small_keys=('بنیادی معنی', 'Basic sense')), unsafe_allow_html=True)

    afaal = analyzer.get_afaal_for_root(root)
    available = [e for e in afaal if e['available']]
    missing = [e for e in afaal if not e['available']]

    # ---- one summary table over every باب --------------------------------
    na = t('not_applicable', lang)
    headers = [t('baab', lang), t('wazn', lang), t('verb', lang),
               t('present_active', lang), t('past_passive', lang),
               t('masdar', lang), t('th_urdu', lang)]
    classes = ['qa-ur', 'qa-pron', 'qa-ar', 'qa-ar', 'qa-ar', 'qa-ar', 'qa-ur']

    rows = []
    for entry in afaal:
        info = entry['baab_info']
        if entry['available']:
            for v in entry['verbs']:
                rows.append([
                    info['name_ar'], info['wazn_past'], v.get('arabic', ''),
                    v.get('present_3ms', ''),
                    v.get('past_passive_3ms') or na,
                    v.get('masdar', ''), v.get('meaning_urdu', ''),
                ])
        else:
            rows.append([info['name_ar'], info['wazn_past'], '—', '—', '—', '—',
                         t('unavailable', lang)])

    st.markdown(theme.simple_table(headers, rows, lang, classes),
                unsafe_allow_html=True)

    # ---- open any verified verb ------------------------------------------
    if on_select and available:
        st.markdown('---')
        st.markdown(f'**{t("view_gardaan", lang)}**')
        flat = [v for e in available for v in e['verbs']]
        cols = st.columns(min(len(flat), 4))
        for i, v in enumerate(flat):
            with cols[i % len(cols)]:
                if st.button('%s\n%s' % (v.get('arabic', ''),
                                         v.get('baab_name_arabic', '')),
                             key='afaal_%s' % v.get('id'),
                             use_container_width=True,
                             disabled=(v.get('id') == verb_data.get('id'))):
                    on_select(v)

    # ---- be explicit about the gaps -------------------------------------
    if missing:
        names = '، '.join(e['baab_info']['name_ar'] for e in missing)
        theme.notice('%s\n\n%s' % (t('not_verified', lang), names))

    # ---- non-verbal derivatives of the root ------------------------------
    words = root_info.get('derived_words') or []
    if words:
        st.markdown('---')
        st.markdown(f'#### {t("derived", lang)} — {theme.esc(root)}')
        headers = [t('th_arabic', lang), t('th_sigha', lang),
                   t('th_urdu', lang), t('th_english', lang)]
        classes = ['qa-ar', 'qa-ur', 'qa-ur', 'qa-en']
        rows = [[w.get('arabic', ''), w.get('type', ''),
                 w.get('meaning_urdu', ''), w.get('meaning_english', '')]
                for w in words]
        st.markdown(theme.simple_table(headers, rows, lang, classes),
                    unsafe_allow_html=True)
