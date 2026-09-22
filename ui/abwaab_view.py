# -*- coding: utf-8 -*-
"""📚 ابواب ثلاثی مزید فیہ — the eight Baab of the reference book.

For each باب: its Arabic name, the four وزن, the مصدر / اسم فاعل / اسم مفعول
patterns, an Urdu and an English explanation, verified example verbs, and the
complete conjugation of the pattern itself (فَعَّلَ / يُفَعِّلُ …).
"""

import streamlit as st

from core.abwaab import BAAB_INFO, MAZEED_ORDER
from . import theme
from .theme import t


def render_abwaab_view(analyzer, lang: str = 'ur', font_scale: float = 1.0,
                       on_select=None, verb_data: dict = None):
    st.markdown('### %s' % t('abwaab_title', lang))
    st.markdown(f'<div class="qa-info">{theme.esc(t("abwaab_intro", lang))}</div>',
                unsafe_allow_html=True)

    # ---- overview table over all eight ----------------------------------
    headers = ['#', t('baab', lang), t('past_active', lang),
               t('present_active', lang), t('past_passive', lang),
               t('present_passive', lang), t('masdar', lang)]
    classes = ['qa-num', 'qa-ur', 'qa-ar', 'qa-ar', 'qa-ar', 'qa-ar', 'qa-pron']
    rows = []
    for i, form in enumerate(MAZEED_ORDER, start=1):
        b = BAAB_INFO[form]
        rows.append([i, theme.baab_name(b, lang), b['wazn_past'], b['wazn_present'],
                     b['wazn_past_passive'], b['wazn_present_passive'],
                     b['masdar_pattern']])
    st.markdown(theme.simple_table(headers, rows, lang, classes),
                unsafe_allow_html=True)

    # ---- Form I for reference --------------------------------------------
    with st.expander('📖 %s — %s' % (theme.baab_name(BAAB_INFO[1], lang),
                                     BAAB_INFO[1]['wazn_past']), expanded=False):
        _render_one(BAAB_INFO[1], analyzer, lang, on_select)

    st.markdown('---')

    # ---- one section per باب ---------------------------------------------
    for i, form in enumerate(MAZEED_ORDER, start=1):
        b = BAAB_INFO[form]
        with st.expander('📖 %d. %s — %s' % (i, theme.baab_name(b, lang),
                                             b['wazn_past']),
                         expanded=(i == 1)):
            _render_one(b, analyzer, lang, on_select)


def _render_one(baab: dict, analyzer, lang: str, on_select=None):
    st.markdown(theme.fact_grid([
        (t('baab', lang), theme.baab_name(baab, lang)),
        (t('past_active', lang), baab['wazn_past']),
        (t('present_active', lang), baab['wazn_present']),
        (t('past_passive', lang), baab['wazn_past_passive']),
        (t('present_passive', lang), baab['wazn_present_passive']),
        (t('masdar', lang), baab['masdar_pattern']),
        (t('ism_fail', lang), baab['ism_fail_pattern']),
        (t('ism_mafool', lang), baab['ism_mafool_pattern']),
    ]), unsafe_allow_html=True)

    if lang != 'en':
        st.markdown(f'<div class="qa-info">{theme.esc(baab["meaning_ur"])}</div>',
                    unsafe_allow_html=True)
    if lang != 'ur':
        st.markdown(
            f'<div class="qa-card" dir="ltr" style="text-align:left">'
            f'{theme.esc(baab["meaning_en"])}</div>', unsafe_allow_html=True)

    # ---- verified verbs of this باب in the lexicon -----------------------
    verbs = analyzer.get_verbs_by_baab(baab['form']) if analyzer else []
    if verbs:
        st.markdown(f'**{t("examples", lang)}**')
        headers = [t('verb', lang), t('root', lang), t('present_active', lang),
                   t('masdar', lang), t('meaning', lang)]
        classes = ['qa-ar', 'qa-pron', 'qa-ar', 'qa-ar',
                   'qa-en' if lang == 'en' else 'qa-ur']
        rows = [[v.get('arabic', ''), v.get('root', ''),
                 v.get('present_3ms', ''), v.get('masdar', ''),
                 theme.gloss(v, lang)] for v in verbs]
        st.markdown(theme.simple_table(headers, rows, lang, classes),
                    unsafe_allow_html=True)

        if on_select:
            cols = st.columns(min(len(verbs), 5))
            for i, v in enumerate(verbs[:10]):
                with cols[i % len(cols)]:
                    if st.button(v.get('arabic', ''),
                                 key='abwaab_%s_%s' % (baab['form'], v.get('id')),
                                 use_container_width=True):
                        on_select(v)

    # ---- the pattern itself, fully conjugated ---------------------------
    if analyzer:
        conj = analyzer.get_baab_example_conjugation(baab['form'])
        if conj:
            with st.expander('📖 %s — %s' % (t('nav_gardaan', lang),
                                             baab['wazn_past'])):
                st.markdown(
                    f'<div class="qa-info">'
                    f'{theme.esc(t("pattern_note", lang))}'
                    f'</div>', unsafe_allow_html=True)
                for key in ('past_active', 'present_active', 'past_passive',
                            'present_passive', 'imperative', 'prohibition'):
                    rows = conj.get(key) or []
                    st.markdown(f'**{t(key, lang)}**')
                    if rows:
                        st.markdown(theme.gardaan_grid(rows, lang),
                                    unsafe_allow_html=True)
                    else:
                        theme.notice(t('not_applicable', lang))


# Backwards-compatible signature used by earlier call-sites
def render_abwaab_view_for_verb(verb_data: dict, analyzer, lang: str = 'ur',
                                translations: dict = None,
                                font_scale: float = 1.0):
    render_abwaab_view(analyzer, lang, font_scale, verb_data=verb_data)
