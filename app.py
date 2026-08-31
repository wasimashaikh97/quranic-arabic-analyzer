# -*- coding: utf-8 -*-
"""📖 عربی فعل اور گردان — a digital Sarf textbook.

Run with:  streamlit run app.py
"""

import os
import sys

import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.analyzer import VerbAnalyzer                       # noqa: E402
from core.conjugation import TENSE_ORDER                     # noqa: E402
from core.morphology import ArabicMorphology                 # noqa: E402
from services.pdf_generator import PDFGenerator              # noqa: E402

from ui import theme                                         # noqa: E402
from ui.theme import t                                       # noqa: E402
from ui.table_view import render_table_view                  # noqa: E402
from ui.tree_view import render_tree_view                    # noqa: E402
from ui.sarf_view import render_sarf_view, render_quranic     # noqa: E402
from ui.gardaan_view import render_gardaan_view              # noqa: E402
from ui.afaal_view import render_afaal_view                  # noqa: E402
from ui.abwaab_view import render_abwaab_view                # noqa: E402
from ui.learning_view import render_learning_view            # noqa: E402
from ui.compare_view import render_compare_view              # noqa: E402
from ui.dashboard import render_dashboard                    # noqa: E402
from ui.practice import render_practice_mode, render_flashcard_mode  # noqa: E402

EXAMPLES = ['كَتَبَ', 'أَنْزَلَ', 'عَلَّمَ', 'قَالَ', 'دَعَا', 'رَمَى',
            'رَدَّ', 'أَكَلَ', 'اِسْتَغْفَرَ', 'تَعَلَّمَ']

RESULT_VIEWS = [
    ('table', 'nav_table'),
    ('tree', 'nav_tree'),
    ('sarf', 'nav_sarf'),
    ('afaal', 'nav_afaal'),
    ('gardaan', 'nav_gardaan'),
    ('learn', 'nav_learn'),
    ('quran', 'nav_quran'),
]


# ---------------------------------------------------------------------------
@st.cache_resource
def get_analyzer():
    return VerbAnalyzer()


@st.cache_resource
def get_pdf_generator():
    return PDFGenerator()


def _init_state():
    defaults = {
        'lang': 'ur',
        'font_scale': 1.15,
        'page': 'home',
        'result_view': 'table',
        'query': '',
        'result': None,
        'gardaan_tense': None,
        'pending_query': None,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def set_page(name: str):
    st.session_state.page = name


def run_analysis(word: str):
    """Analyse a word and store the result in session state."""
    analyzer = get_analyzer()
    lang = st.session_state.lang
    st.session_state.query = word
    result = analyzer.analyze_verb(word, lang)
    st.session_state.result = result
    st.session_state.gardaan_tense = None
    st.session_state.result_view = 'table'
    if result.get('found'):
        analyzer.record_study(result.get('verb', {}).get('id', ''))
    set_page('home')


def select_verb(verb: dict):
    """Open another verb (used by every clickable row / node / card)."""
    run_analysis(verb.get('arabic', ''))
    st.rerun()


# ---------------------------------------------------------------------------
def main():
    st.set_page_config(page_title='عربی فعل اور گردان — Arabic Verb Sarf',
                       page_icon='📖', layout='wide',
                       initial_sidebar_state='collapsed')
    _init_state()
    lang = st.session_state.lang
    theme.inject_css(st.session_state.font_scale, lang)

    analyzer = get_analyzer()
    pdf_gen = get_pdf_generator()

    render_top_bar(lang)
    render_sidebar(analyzer, lang)

    page = st.session_state.page
    if page == 'home':
        render_home(analyzer, pdf_gen, lang)
    elif page == 'abwaab':
        theme.header(lang)
        _home_button(lang)
        render_abwaab_view(analyzer, lang, st.session_state.font_scale,
                           on_select=select_verb)
    elif page == 'compare':
        theme.header(lang)
        _home_button(lang)
        render_compare_view(analyzer, lang, {}, st.session_state.font_scale)
    elif page == 'practice':
        theme.header(lang)
        _home_button(lang)
        render_practice_mode(analyzer, lang, {})
    elif page == 'flashcards':
        theme.header(lang)
        _home_button(lang)
        render_flashcard_mode(analyzer, lang, {})
    elif page == 'dashboard':
        theme.header(lang)
        _home_button(lang)
        render_dashboard(analyzer, lang, {})
    elif page == 'bookmarks':
        theme.header(lang)
        _home_button(lang)
        render_bookmarks(analyzer, lang)


def _home_button(lang: str):
    if st.button(t('home', lang), key='btn_home_%s' % st.session_state.page):
        set_page('home')
        st.rerun()


# ---------------------------------------------------------------------------
def render_top_bar(lang: str):
    """Language and text-size controls — nothing else, to keep it simple."""
    col_lang, col_size = st.columns([1, 2])

    with col_lang:
        codes = list(theme.LANGS.keys())
        chosen = st.radio(
            t('language', lang), codes, index=codes.index(lang),
            horizontal=True, key='lang_radio',
            format_func=lambda c: theme.LANGS[c])
        if chosen != lang:
            st.session_state.lang = chosen
            st.rerun()

    with col_size:
        st.markdown(f'**{t("text_size", lang)}**')
        c1, c2, c3, _ = st.columns([1, 1, 1, 3])
        if c1.button('A−', key='font_down', help=t('text_size', lang)):
            st.session_state.font_scale = max(0.9,
                                              st.session_state.font_scale - 0.15)
            st.rerun()
        if c2.button('A', key='font_reset', help=t('reset_size', lang)):
            st.session_state.font_scale = 1.15
            st.rerun()
        if c3.button('A+', key='font_up', help=t('text_size', lang)):
            st.session_state.font_scale = min(2.2,
                                              st.session_state.font_scale + 0.15)
            st.rerun()


def render_sidebar(analyzer, lang: str):
    with st.sidebar:
        st.markdown('## 📖')
        for page, key in (('home', 'home'), ('abwaab', 'nav_abwaab'),
                          ('bookmarks', 'bookmarks'), ('compare', 'compare'),
                          ('practice', 'practice'), ('flashcards', 'flashcards'),
                          ('dashboard', 'dashboard')):
            if st.button(t(key, lang), key='side_%s' % page,
                         use_container_width=True):
                set_page(page)
                st.rerun()

        st.markdown('---')
        st.markdown('### %s' % t('recent', lang))
        for verb_id in analyzer.get_recent_verbs(limit=6):
            verb = analyzer.get_verb_by_id(verb_id)
            if not verb:
                continue
            if st.button(verb.get('arabic', verb_id), key='recent_%s' % verb_id,
                         use_container_width=True):
                select_verb(verb)

        st.markdown('---')
        stats = analyzer.get_statistics()
        st.caption('%d افعال · %d مادے · %d ابواب · %d صیغے'
                   % (stats['verbs'], stats['roots'], stats['abwaab'],
                      stats['total_forms']))


# ---------------------------------------------------------------------------
def render_home(analyzer, pdf_gen, lang: str):
    theme.header(lang)

    # ---- the single search box ------------------------------------------
    left, middle, right = st.columns([1, 3, 1])
    with middle:
        with st.form('search_form', clear_on_submit=False):
            word = st.text_input(t('enter_verb', lang),
                                 value=st.session_state.query,
                                 placeholder='أَنْزَلَ',
                                 key='search_box')
            submitted = st.form_submit_button(t('analyze', lang),
                                              use_container_width=True,
                                              type='primary')
        if submitted:
            run_analysis(word)
            st.rerun()

        st.markdown(f'<div style="text-align:center;color:#4b5563;'
                    f'margin:10px 0 6px">{theme.esc(t("examples", lang))}</div>',
                    unsafe_allow_html=True)
        for start in range(0, len(EXAMPLES), 5):
            cols = st.columns(5)
            for i, example in enumerate(EXAMPLES[start:start + 5]):
                if cols[i].button(example, key='ex_%s' % example,
                                  use_container_width=True):
                    run_analysis(example)
                    st.rerun()

    result = st.session_state.result
    if not result:
        render_welcome(analyzer, lang)
        return
    if not result.get('found'):
        render_not_found(analyzer, result, lang)
        return

    render_result(analyzer, pdf_gen, result, lang)


def render_welcome(analyzer, lang: str):
    st.markdown('---')
    theme.notice('اوپر خانے میں کوئی عربی فعل لکھیں اور «تجزیہ کریں» دبائیں۔ '
                 'یا نیچے دی گئی مثالوں میں سے کسی پر دبائیں۔', 'info')
    if st.button(t('nav_abwaab', lang), key='welcome_abwaab',
                 use_container_width=True):
        set_page('abwaab')
        st.rerun()


def render_not_found(analyzer, result: dict, lang: str):
    st.markdown('---')
    theme.notice(result.get('message', t('no_data', lang)))

    suggestions = result.get('root_suggestions') or []
    if suggestions:
        st.markdown('#### %s %s' % (t('try_these', lang),
                                    result.get('guessed_root', '')))
        cols = st.columns(min(len(suggestions), 4))
        for i, verb in enumerate(suggestions):
            with cols[i % len(cols)]:
                if st.button('%s — %s' % (verb.get('arabic'),
                                          verb.get('meaning_urdu')),
                             key='sugg_%s' % verb.get('id'),
                             use_container_width=True):
                    select_verb(verb)


# ---------------------------------------------------------------------------
def render_result(analyzer, pdf_gen, result: dict, lang: str):
    verb = result['verb']
    conjugations = result['conjugations']
    na = t('not_applicable', lang)

    st.markdown('---')

    # ---- was the input an inflected form? -------------------------------
    parsed = result.get('conjugated_info')
    if parsed:
        render_parse_banner(parsed, result.get('all_parses') or [], lang)

    # ---- 📖 فعل کی معلومات ----------------------------------------------
    st.markdown(
        f"""<div class="qa-verb-banner">
            <div class="qa-verb">{theme.esc(verb.get('arabic',''))}</div>
            <div class="qa-verb-meaning">{theme.esc(verb.get('meaning_urdu',''))}</div>
            <div class="qa-verb-meaning-en">{theme.esc(verb.get('meaning_english',''))}</div>
        </div>""", unsafe_allow_html=True)

    vtype = ArabicMorphology.get_verb_type_info(verb.get('verb_type', 'sound'))
    theme.card(
        t('verb_info', lang),
        theme.fact_grid([
            (t('verb', lang), verb.get('arabic', '')),
            (t('root', lang), verb.get('root', '')),
            (t('baab', lang), verb.get('baab_name_arabic', '')),
            (t('wazn', lang), verb.get('wazn', '')),
            (t('past_active', lang), verb.get('past_3ms') or '—'),
            (t('present_active', lang), verb.get('present_3ms') or '—'),
            (t('past_passive', lang), verb.get('past_passive_3ms') or na),
            (t('present_passive', lang), verb.get('present_passive_3ms') or na),
            (t('masdar', lang), verb.get('masdar') or '—'),
            (t('ism_fail', lang), verb.get('ism_fail') or '—'),
            (t('ism_mafool', lang), verb.get('ism_mafool') or na),
            (t('verb_type', lang), vtype.get('title_ur', '')),
            (t('transitivity', lang), verb.get('transitivity', '')),
            (t('meaning_ur', lang), verb.get('meaning_urdu', '')),
            (t('meaning_en', lang), verb.get('meaning_english', '')),
        ], small_keys=(t('verb_type', lang), t('transitivity', lang),
                       t('meaning_ur', lang), t('meaning_en', lang),
                       t('masdar', lang), t('ism_fail', lang),
                       t('ism_mafool', lang))),
        lang)

    if verb.get('unavailable_note'):
        theme.notice(verb['unavailable_note'])

    # ---- actions: save / listen / PDF -----------------------------------
    render_actions(analyzer, pdf_gen, result, lang)

    # ---- the four big navigation buttons --------------------------------
    st.markdown('---')
    cols = st.columns(4)
    for i, (view, key) in enumerate(RESULT_VIEWS[:4]):
        if cols[i].button(t(key, lang), key='nav_%s' % view,
                          use_container_width=True,
                          type=('primary' if st.session_state.result_view == view
                                else 'secondary')):
            st.session_state.result_view = view
            st.rerun()
    cols2 = st.columns(4)
    for i, (view, key) in enumerate(RESULT_VIEWS[4:]):
        if cols2[i].button(t(key, lang), key='nav_%s' % view,
                           use_container_width=True,
                           type=('primary' if st.session_state.result_view == view
                                 else 'secondary')):
            st.session_state.result_view = view
            st.rerun()
    if cols2[3].button(t('nav_abwaab', lang), key='nav_abwaab_btn',
                       use_container_width=True):
        set_page('abwaab')
        st.rerun()

    st.markdown('---')

    # ---- the selected view ----------------------------------------------
    view = st.session_state.result_view
    scale = st.session_state.font_scale

    if view == 'table':
        render_table_view(verb, conjugations, lang, {}, scale,
                          analyzer=analyzer, on_select=select_verb)
    elif view == 'tree':
        render_tree_view(verb, conjugations, lang, {}, scale,
                         analyzer=analyzer, on_select=select_verb,
                         on_tense=_open_tense)
    elif view == 'sarf':
        render_sarf_view(verb, conjugations, analyzer, lang, {}, scale,
                         on_select=select_verb)
    elif view == 'afaal':
        render_afaal_view(verb, analyzer, lang, {}, scale,
                          on_select=select_verb)
    elif view == 'gardaan':
        render_gardaan_view(verb, conjugations, lang, {}, scale,
                            only_tense=st.session_state.gardaan_tense)
    elif view == 'learn':
        render_learning_view(verb, conjugations, lang, {}, scale)
    elif view == 'quran':
        st.markdown('### %s' % t('nav_quran', lang))
        render_quranic(analyzer, verb.get('id'), lang)


def _open_tense(tense_key: str):
    st.session_state.gardaan_tense = tense_key
    st.session_state.result_view = 'gardaan'
    st.rerun()


def render_parse_banner(parsed: dict, all_parses: list, lang: str):
    body = theme.fact_grid([
        ('آپ کا لفظ', parsed.get('input_word', '')),
        (t('base_verb', lang), parsed.get('base_verb', '')),
        (t('root', lang), parsed.get('root', '')),
        (t('baab', lang), parsed.get('baab_name', '')),
        (t('tense', lang), parsed.get('tense_urdu', '')),
        (t('th_pronoun', lang), parsed.get('pronoun', '')),
        (t('th_sigha', lang), parsed.get('sigha_urdu', '')),
        (t('meaning_ur', lang), parsed.get('meaning_urdu', '')),
    ], small_keys=(t('tense', lang), t('th_sigha', lang), t('meaning_ur', lang)))
    theme.card('%s: «%s»' % (t('parsed_as', lang), parsed.get('input_word', '')),
               body, lang)

    if len(all_parses) > 1:
        with st.expander('%s (%d)' % (t('ambiguous', lang), len(all_parses))):
            headers = [t('th_arabic', lang), t('base_verb', lang),
                       t('tense', lang), t('th_pronoun', lang),
                       t('th_sigha', lang)]
            classes = ['qa-ar', 'qa-ar', 'qa-ur', 'qa-pron', 'qa-ur']
            rows = [[p.get('form', ''), p.get('base_verb', ''),
                     p.get('tense_urdu', ''), p.get('pronoun', ''),
                     p.get('sigha_urdu', '')] for p in all_parses]
            st.markdown(theme.simple_table(headers, rows, lang, classes),
                        unsafe_allow_html=True)


def render_actions(analyzer, pdf_gen, result: dict, lang: str):
    verb = result['verb']
    conjugations = result['conjugations']
    verb_id = verb.get('id', '')

    c1, c2, c3 = st.columns([1, 1, 2])

    with c1:
        if st.button(t('listen', lang), key='listen_btn',
                     use_container_width=True):
            speak(verb.get('arabic', ''))

    with c2:
        saved = analyzer.is_bookmarked(verb_id)
        if st.button(t('saved', lang) if saved else t('save', lang),
                     key='save_btn', use_container_width=True):
            if saved:
                analyzer.remove_bookmark(verb_id)
            else:
                analyzer.add_bookmark(verb_id)
            st.rerun()

    with c3:
        with st.expander(t('download_pdf', lang), expanded=False):
            st.markdown('**%s**' % t('pdf_one_page', lang))
            one_page = pdf_gen.generate_one_page_sheet(
                verb, conjugations, result.get('baab'), result.get('root_info'))
            st.download_button(
                '⬇ %s' % t('pdf_one_page', lang), data=one_page,
                file_name='%s_one_page.pdf' % _safe_name(verb),
                mime='application/pdf', key='dl_one', use_container_width=True)

            st.markdown('---')
            st.markdown('**%s**' % t('pdf_detailed', lang))
            inc_ur = st.checkbox('اردو ترجمہ', value=True, key='pdf_ur')
            inc_en = st.checkbox('English translation', value=True, key='pdf_en')
            inc_qu = st.checkbox('قرآنی مثالیں', value=True, key='pdf_qu')
            detailed = pdf_gen.generate_study_sheet(
                verb_data=verb, conjugations=conjugations,
                quranic_data=result.get('quranic_usage'),
                root_info=result.get('root_info'), baab=result.get('baab'),
                afaal=result.get('afaal'),
                include_quranic=inc_qu, include_english=inc_en,
                include_urdu=inc_ur)
            st.download_button(
                '⬇ %s' % t('pdf_detailed', lang), data=detailed,
                file_name='%s_detailed.pdf' % _safe_name(verb),
                mime='application/pdf', key='dl_full', use_container_width=True)


def _safe_name(verb: dict) -> str:
    """A filename browsers on every platform will accept."""
    root = (verb.get('root') or '').replace(' ', '')
    return '%s_%s' % (verb.get('id', 'verb'), root or 'sarf')


def speak(text: str):
    """Pronounce the verb with the browser's own speech synthesis."""
    safe = (text or '').replace('\\', '').replace("'", '')
    st.components.v1.html(f"""
        <script>
        try {{
            var u = new SpeechSynthesisUtterance('{safe}');
            u.lang = 'ar-SA'; u.rate = 0.75;
            window.speechSynthesis.speak(u);
        }} catch (e) {{}}
        </script>""", height=0)


# ---------------------------------------------------------------------------
def render_bookmarks(analyzer, lang: str):
    st.markdown('### %s' % t('bookmarks', lang))
    ids = analyzer.get_bookmarks()
    verbs = [analyzer.get_verb_by_id(i) for i in ids]
    verbs = [v for v in verbs if v]
    if not verbs:
        theme.notice('آپ نے ابھی کوئی فعل محفوظ نہیں کیا۔', 'info')
        return
    cols = st.columns(3)
    for i, verb in enumerate(verbs):
        with cols[i % 3]:
            st.markdown(
                f"""<div class="qa-node">
                    <div class="qa-node-value">{theme.esc(verb.get('arabic',''))}</div>
                    <div class="qa-node-label">{theme.esc(verb.get('meaning_urdu',''))}</div>
                    <div class="qa-node-label">{theme.esc(verb.get('baab_name_arabic',''))}
                        · {theme.esc(verb.get('root',''))}</div>
                </div>""", unsafe_allow_html=True)
            if st.button(t('open', lang), key='bm_%s' % verb.get('id'),
                         use_container_width=True):
                select_verb(verb)


if __name__ == '__main__':
    main()
