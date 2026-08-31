# -*- coding: utf-8 -*-
"""🌳 درخت — the hierarchical view.

    مادہ ↓ ن ز ل ↓ فعل ↓ أَنْزَلَ ↓ باب ↓ إفعال ↓ وزن ↓ أَفْعَلَ
         ↓ ماضی معروف ↓ مضارع معروف ↓ ماضی مجہول ↓ مضارع مجہول ↓ مکمل گردان

Every node that leads somewhere is a real button, so a student can walk the
tree by tapping rather than scrolling.
"""

import streamlit as st

from core.conjugation import MANDATORY_TENSES
from core.morphology import ArabicMorphology
from . import theme
from .theme import t


def render_tree_view(verb_data: dict, conjugations: dict, lang: str = 'ur',
                     translations: dict = None, font_scale: float = 1.0,
                     analyzer=None, on_select=None, on_tense=None):
    st.markdown(f'### {t("nav_tree", lang)}')

    na = t('not_applicable', lang)
    vtype = ArabicMorphology.get_verb_type_info(verb_data.get('verb_type', 'sound'))

    chain = [
        (t('root', lang), verb_data.get('root', ''), None),
        (t('verb', lang), verb_data.get('arabic', ''), None),
        (t('baab', lang), verb_data.get('baab_name_arabic', ''), None),
        (t('wazn', lang), verb_data.get('wazn', ''), None),
        (t('verb_type', lang), vtype.get('title_ur', ''), None),
    ]
    for key in MANDATORY_TENSES:
        value = verb_data.get({
            'past_active': 'past_3ms',
            'present_active': 'present_3ms',
            'past_passive': 'past_passive_3ms',
            'present_passive': 'present_passive_3ms',
        }[key]) or na
        chain.append((t(key, lang), value, key))

    # ---- draw the spine -------------------------------------------------
    for i, (label, value, tense_key) in enumerate(chain):
        if i:
            st.markdown('<div class="qa-connector"></div>', unsafe_allow_html=True)
        st.markdown(
            f"""<div class="qa-node">
                <div class="qa-node-label">{theme.esc(label)}</div>
                <div class="qa-node-value">{theme.esc(value)}</div>
            </div>""", unsafe_allow_html=True)
        if tense_key and conjugations.get(tense_key) and on_tense:
            if st.button('%s — %s (%d %s)' % (t('nav_gardaan', lang),
                                              t(tense_key, lang),
                                              len(conjugations[tense_key]),
                                              t('sigha_count', lang)),
                         key='tree_tense_%s' % tense_key,
                         use_container_width=True):
                on_tense(tense_key)

    # ---- the complete gardaan node --------------------------------------
    total = sum(len(rows) for rows in conjugations.values())
    st.markdown('<div class="qa-connector"></div>', unsafe_allow_html=True)
    st.markdown(
        f"""<div class="qa-node" style="border-color:#14532d;">
            <div class="qa-node-label">{theme.esc(t('nav_gardaan', lang))}</div>
            <div class="qa-node-value">{total} {theme.esc(t('sigha_count', lang))}</div>
        </div>""", unsafe_allow_html=True)

    # ---- derivatives branch ---------------------------------------------
    derived = verb_data.get('derived_nouns') or {}
    if derived:
        st.markdown('---')
        st.markdown(f'#### {t("derived", lang)}')
        cols = st.columns(min(len(derived), 4))
        for i, info in enumerate(derived.values()):
            if not isinstance(info, dict):
                continue
            with cols[i % len(cols)]:
                st.markdown(
                    f"""<div class="qa-node">
                        <div class="qa-node-label">{theme.esc(info.get('label_ur',''))}</div>
                        <div class="qa-node-value">{theme.esc(info.get('arabic',''))}</div>
                        <div class="qa-node-label">{theme.esc(info.get('pattern',''))}</div>
                    </div>""", unsafe_allow_html=True)

    # ---- related verified verbs of the same root ------------------------
    if analyzer:
        root = verb_data.get('root', '')
        others = [v for v in analyzer.get_verb_forms_for_root(root)
                  if v.get('id') != verb_data.get('id')]
        if others:
            st.markdown('---')
            st.markdown(f'#### {t("related_afaal", lang)} — {theme.esc(root)}')
            cols = st.columns(min(len(others), 4))
            for i, v in enumerate(others):
                with cols[i % len(cols)]:
                    st.markdown(
                        f"""<div class="qa-node">
                            <div class="qa-node-label">{theme.esc(v.get('baab_name_arabic',''))}</div>
                            <div class="qa-node-value">{theme.esc(v.get('arabic',''))}</div>
                            <div class="qa-node-label">{theme.esc(v.get('meaning_urdu',''))}</div>
                        </div>""", unsafe_allow_html=True)
                    if on_select and st.button(t('open', lang),
                                              key='tree_rel_%s' % v.get('id'),
                                              use_container_width=True):
                        on_select(v)
