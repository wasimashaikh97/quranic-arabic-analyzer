# -*- coding: utf-8 -*-
"""📚 مکمل صرف — everything about the selected verb, in the taught order.

    ۱ فعل   ۲ مادہ   ۳ باب   ۴ وزن   ۵ اردو معنی   ۶ English meaning
    ۷ ماضی معروف   ۸ مضارع معروف   ۹ ماضی مجہول   ۱۰ مضارع مجہول
    ۱۱ امر   ۱۲ نہی   ۱۳ مصدر   ۱۴ اسم فاعل   ۱۵ اسم مفعول
    ۱۶ دیگر مشتقات   ۱۷ متعلقہ افعال   ۱۸ متعلقہ باب   ۱۹ قرآنی استعمال
"""

import streamlit as st

from core.abwaab import get_baab
from core.conjugation import TENSE_ORDER
from core.morphology import ArabicMorphology
from . import theme
from .theme import t


def render_sarf_view(verb_data: dict, conjugations: dict, analyzer=None,
                     lang: str = 'ur', translations: dict = None,
                     font_scale: float = 1.0, on_select=None):
    st.markdown(f'### {t("nav_sarf", lang)}')

    na = t('not_applicable', lang)
    vtype = ArabicMorphology.get_verb_type_info(verb_data.get('verb_type', 'sound'))
    baab = get_baab(verb_data.get('baab', 1))

    # ---- 1–6: identity ---------------------------------------------------
    theme.card(
        t('verb_info', lang),
        theme.fact_grid([
            (t('verb', lang), verb_data.get('arabic', '')),
            (t('root', lang), verb_data.get('root', '')),
            (t('baab', lang), verb_data.get('baab_name_arabic', '')),
            (t('wazn', lang), verb_data.get('wazn', '')),
            (t('verb_type', lang), vtype.get('title_ur', '')),
            (t('transitivity', lang), verb_data.get('transitivity', '')),
            (t('meaning_ur', lang), verb_data.get('meaning_urdu', '')),
            (t('meaning_en', lang), verb_data.get('meaning_english', '')),
        ], small_keys=(t('verb_type', lang), t('transitivity', lang),
                       t('meaning_ur', lang), t('meaning_en', lang))),
        lang)

    if verb_data.get('unavailable_note'):
        theme.notice(verb_data['unavailable_note'])

    # ---- 7–12: the four mandatory gardaans, then امر and نہی ------------
    for key in TENSE_ORDER:
        rows = conjugations.get(key) or []
        count = ' (%d %s)' % (len(rows), t('sigha_count', lang)) if rows else ''
        with st.expander('📖 %s%s' % (t(key, lang), count),
                         expanded=(key == 'past_active')):
            if rows:
                st.markdown(theme.gardaan_table(rows, lang),
                            unsafe_allow_html=True)
            else:
                theme.notice('%s — %s' % (na, verb_data.get('unavailable_note') or ''))

    # ---- 13–16: مصدر، اسم فاعل، اسم مفعول، دیگر مشتقات -------------------
    with st.expander('📖 %s' % t('derived', lang), expanded=True):
        derived = verb_data.get('derived_nouns') or {}
        if derived:
            headers = [t('th_sigha', lang), t('th_arabic', lang),
                       t('wazn', lang), t('th_urdu', lang), t('th_english', lang)]
            classes = ['qa-ur', 'qa-ar', 'qa-pron', 'qa-ur', 'qa-en']
            rows = [[info.get('label_ur', ''), info.get('arabic', ''),
                     info.get('pattern', ''), info.get('meaning_urdu', ''),
                     info.get('meaning_english', '')]
                    for info in derived.values() if isinstance(info, dict)]
            st.markdown(theme.simple_table(headers, rows, lang, classes),
                        unsafe_allow_html=True)
        else:
            theme.notice(na)
        if not verb_data.get('ism_mafool'):
            theme.notice('%s: %s — %s' % (t('ism_mafool', lang), na,
                                          verb_data.get('unavailable_note') or ''))

    # ---- 17: related verified verbs of the same root --------------------
    with st.expander('📖 %s' % t('related_afaal', lang), expanded=True):
        others = []
        if analyzer:
            others = [v for v in analyzer.get_verb_forms_for_root(
                verb_data.get('root', '')) if v.get('id') != verb_data.get('id')]
        if others:
            headers = [t('baab', lang), t('th_arabic', lang),
                       t('present_active', lang), t('masdar', lang),
                       t('th_urdu', lang)]
            classes = ['qa-ur', 'qa-ar', 'qa-ar', 'qa-ar', 'qa-ur']
            rows = [[v.get('baab_name_arabic', ''), v.get('arabic', ''),
                     v.get('present_3ms', ''), v.get('masdar', ''),
                     v.get('meaning_urdu', '')] for v in others]
            st.markdown(theme.simple_table(headers, rows, lang, classes),
                        unsafe_allow_html=True)
            if on_select:
                cols = st.columns(min(len(others), 4))
                for i, v in enumerate(others):
                    with cols[i % len(cols)]:
                        if st.button('%s %s' % (t('open', lang), v.get('arabic')),
                                     key='sarf_rel_%s' % v.get('id'),
                                     use_container_width=True):
                            on_select(v)
        else:
            theme.notice(t('not_verified', lang))

    # ---- 18: the باب this verb belongs to -------------------------------
    with st.expander('📖 %s — %s' % (t('baab', lang), baab['name_ar']),
                     expanded=True):
        st.markdown(theme.fact_grid([
            (t('baab', lang), baab['name_ar']),
            (t('past_active', lang), baab['wazn_past']),
            (t('present_active', lang), baab['wazn_present']),
            (t('past_passive', lang), baab['wazn_past_passive']),
            (t('present_passive', lang), baab['wazn_present_passive']),
            (t('masdar', lang), baab['masdar_pattern']),
            (t('ism_fail', lang), baab['ism_fail_pattern']),
            (t('ism_mafool', lang), baab['ism_mafool_pattern']),
        ]), unsafe_allow_html=True)
        st.markdown(
            f'<div class="qa-info">{theme.esc(baab["meaning_ur"])}</div>',
            unsafe_allow_html=True)
        st.markdown(
            f'<div class="qa-card" dir="ltr" style="text-align:left">'
            f'{theme.esc(baab["meaning_en"])}</div>', unsafe_allow_html=True)

    # ---- 19: verified Quranic usage -------------------------------------
    with st.expander('📖 %s' % t('nav_quran', lang), expanded=False):
        render_quranic(analyzer, verb_data.get('id'), lang)


def render_quranic(analyzer, verb_id: str, lang: str = 'ur'):
    usage = analyzer.get_quranic_usage(verb_id) if analyzer else []
    if not usage:
        theme.notice(t('no_data', lang))
        return
    for ex in usage:
        st.markdown(
            f"""<div class="qa-card" dir="rtl">
                <div class="qa-fact-label">سورۃ {theme.esc(ex.get('surah_name_arabic',''))}
                    ({theme.esc(ex.get('surah_number',''))}:{theme.esc(ex.get('ayah_number',''))})
                    — {theme.esc(ex.get('highlighted_word',''))}</div>
                <div class="qa-verb" style="font-size:1.9em; text-align:right;">
                    {theme.esc(ex.get('arabic_text',''))}</div>
                <div class="qa-fact-value-sm">{theme.esc(ex.get('translation_urdu',''))}</div>
                <div dir="ltr" style="text-align:left; color:#4b5563; margin-top:8px;">
                    {theme.esc(ex.get('translation_english',''))}</div>
                <div dir="ltr" style="text-align:left; color:#6b7280; font-size:.9em; margin-top:6px;">
                    {theme.esc(ex.get('grammatical_note',''))}</div>
            </div>""", unsafe_allow_html=True)
