# -*- coding: utf-8 -*-
"""📖 عربی فعل اور گردان — a digital Sarf textbook.

One page per verb.  A student types the word they met in the Quran and reads
straight down: what it is, its مادہ / باب / وزن, the complete گردان, its
مشتقات, the other verbs of its root, and the ayaat it occurs in — then prints
it.  Nothing is hidden behind navigation, because for an older reader anything
behind a button is effectively not there.

Run with:  streamlit run app.py
"""

import os
import sys

import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.analyzer import VerbAnalyzer                       # noqa: E402
from core.conjugation import MANDATORY_TENSES                # noqa: E402
from core.morphology import ArabicMorphology                 # noqa: E402
from services.pdf_generator import PDFGenerator              # noqa: E402
from services import quran_source                            # noqa: E402

from ui import theme                                         # noqa: E402
from ui.theme import t                                       # noqa: E402
from ui.abwaab_view import render_abwaab_view                # noqa: E402
from ui import keyboard                                      # noqa: E402

EXAMPLES = ['أَنْزَلَ', 'كَتَبَ', 'قَالَ', 'دَعَا', 'عَلَّمَ', 'اِسْتَغْفَرَ']

#: the reading order of a verb page
FOUR = ['past_active', 'present_active', 'past_passive', 'present_passive']


@st.cache_resource
def get_analyzer():
    return VerbAnalyzer()


@st.cache_resource
def get_pdf_generator():
    return PDFGenerator()


def _init_state():
    for key, value in {'lang': 'ur', 'font_scale': 1.15, 'page': 'home',
                       'query': '', 'result': None}.items():
        st.session_state.setdefault(key, value)


def run_analysis(word: str):
    analyzer = get_analyzer()
    st.session_state.query = word
    result = analyzer.analyze_verb(word, st.session_state.lang)
    st.session_state.result = result
    st.session_state.page = 'home'
    if result.get('found'):
        analyzer.record_study(result.get('verb', {}).get('id', ''))


def queue_input(word: str):
    """Put text in the search box and analyse it on the next run."""
    st.session_state.pending_input = word
    run_analysis(word)


def open_verb(verb: dict):
    queue_input(verb.get('arabic', ''))
    st.rerun()


# ===========================================================================
def main():
    st.set_page_config(page_title='عربی فعل اور گردان', page_icon='📖',
                       layout='wide', initial_sidebar_state='collapsed')
    _init_state()
    lang = st.session_state.lang
    theme.inject_css(st.session_state.font_scale, lang)
    keyboard.inject_keyboard_css(st.session_state.font_scale)

    render_controls(lang)

    if st.session_state.page == 'abwaab':
        render_abwaab_view(get_analyzer(), lang, st.session_state.font_scale,
                           on_select=open_verb)
        return

    render_home(get_analyzer(), get_pdf_generator(), lang)


def render_controls(lang: str):
    """One slim strip: two destinations, the language, and the text size.

    Deliberately compact — every pixel here pushes the search box further down
    the page, and the search box has to be the first thing an older reader
    sees without scrolling.
    """
    home, abwaab, langs, sizes = st.columns([2, 2, 3, 2])

    with home:
        if st.button(t('home', lang), key='go_home', use_container_width=True):
            st.session_state.page = 'home'
            st.rerun()
    with abwaab:
        if st.button(t('nav_abwaab', lang), key='go_abwaab',
                     use_container_width=True):
            st.session_state.page = 'abwaab'
            st.rerun()

    with langs:
        codes = list(theme.LANGS)
        chosen = st.radio(t('language', lang), codes, index=codes.index(lang),
                          horizontal=True, key='lang_radio',
                          label_visibility='collapsed',
                          format_func=lambda c: theme.LANGS[c])
        if chosen != lang:
            st.session_state.lang = chosen
            st.rerun()

    with sizes:
        # three equal columns, so «A−» and «A+» always have room on one line
        a, b, c = st.columns(3)
        if a.button('A −', key='font_down', use_container_width=True,
                    help=t('text_size', lang)):
            st.session_state.font_scale = max(0.9,
                                              st.session_state.font_scale - 0.15)
            st.rerun()
        if b.button('A', key='font_reset', use_container_width=True,
                    help=t('reset_size', lang)):
            st.session_state.font_scale = 1.15
            st.rerun()
        if c.button('A +', key='font_up', use_container_width=True,
                    help=t('text_size', lang)):
            st.session_state.font_scale = min(2.2,
                                              st.session_state.font_scale + 0.15)
            st.rerun()


# ===========================================================================
def render_home(analyzer, pdf_gen, lang: str):
    theme.header(lang)

    # A widget's value cannot be assigned after the widget exists in the same
    # run, so anything that wants to fill the box (an example chip, the
    # on-screen keyboard) parks the text here and it is applied on the next
    # run, before the box is drawn.
    if st.session_state.get('pending_input') is not None:
        st.session_state[keyboard.FIELD] = st.session_state.pop('pending_input')
    st.session_state.setdefault(keyboard.FIELD, '')

    _, middle, _ = st.columns([1, 3, 1])
    with middle:
        with st.form('search_form'):
            st.text_input(t('enter_verb', lang), placeholder='أَنْزَلَ',
                          key=keyboard.FIELD)
            submitted = st.form_submit_button(t('analyze', lang),
                                              use_container_width=True,
                                              type='primary')
        if submitted:
            run_analysis(st.session_state.get(keyboard.FIELD, ''))
            st.rerun()

        # the on-screen Arabic keyboard, directly under the existing box
        keyboard.render_keyboard(lang, on_search=queue_input)

        st.markdown(
            f'<div style="text-align:center;color:#4b5563;margin:10px 0 6px">'
            f'{theme.esc(t("examples", lang))}</div>', unsafe_allow_html=True)
        cols = st.columns(len(EXAMPLES))
        for i, example in enumerate(EXAMPLES):
            if cols[i].button(example, key='ex_%s' % example,
                              use_container_width=True):
                queue_input(example)
                st.rerun()

    result = st.session_state.result
    if not result:
        theme.notice('اوپر خانے میں کوئی عربی فعل لکھیں اور «تجزیہ کریں» دبائیں۔',
                     'info')
        return
    if not result.get('found'):
        render_not_found(result, lang)
        return
    render_verb_page(analyzer, pdf_gen, result, lang)


def render_not_found(result: dict, lang: str):
    st.markdown('---')
    theme.notice(result.get('message', t('no_data', lang)))

    # «کیا آپ کا مطلب یہ تھا؟» — near misses drawn from verbs that really
    # occur in the Quran, so a misspelling leads somewhere instead of a
    # dead end.
    did_you_mean = result.get('did_you_mean') or []
    if did_you_mean:
        st.markdown('#### %s' % {'en': 'Did you mean?',
                                 'ar': 'هل تقصد؟'}.get(
            lang, 'کیا آپ کا مطلب یہ تھا؟'))
        cols = st.columns(min(len(did_you_mean), 3))
        for i, entry in enumerate(did_you_mean):
            with cols[i % len(cols)]:
                label = '%s — %s' % (entry.get('headword', ''),
                                     entry.get('root_spaced', ''))
                if st.button(label, key='dym_%d' % i,
                             use_container_width=True):
                    queue_input(entry.get('headword', ''))
                    st.rerun()

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
                    open_verb(verb)


# ===========================================================================
def render_verb_page(analyzer, pdf_gen, result: dict, lang: str):
    """The whole verb, top to bottom, in the order a teacher teaches it."""
    verb = result['verb']
    conj = result['conjugations']
    na = t('not_applicable', lang)

    st.markdown('---')

    parsed = result.get('conjugated_info')
    if parsed:
        with _section('⚡', t('parsed_as', lang), lang, expanded=True):
            st.markdown(theme.fact_grid([
                ('آپ کا لفظ', parsed.get('input_word', '')),
                (t('base_verb', lang), parsed.get('base_verb', '')),
                (t('tense', lang), parsed.get('tense_urdu', '')),
                (t('th_sigha', lang), parsed.get('sigha_urdu', '')),
            ], small_keys=(t('tense', lang), t('th_sigha', lang))),
                unsafe_allow_html=True)

    # ---- the verb itself ------------------------------------------------
    st.markdown(
        f"""<div class="qa-verb-banner">
            <div class="qa-verb">{theme.esc(verb.get('arabic',''))}</div>
            <div class="qa-verb-meaning">{theme.esc(verb.get('meaning_urdu',''))}</div>
            <div class="qa-verb-meaning-en">{theme.esc(verb.get('meaning_english',''))}</div>
        </div>""", unsafe_allow_html=True)

    # ---- ① فعل کی معلومات — the one section open by default -------------
    vtype = ArabicMorphology.get_verb_type_info(verb.get('verb_type', 'sound'))
    with _section('①', t('verb_info', lang), lang, expanded=True):
        st.markdown(theme.fact_grid([
            (t('root', lang), verb.get('root', '')),
            (t('baab', lang), verb.get('baab_name_arabic', '')),
            (t('wazn', lang), verb.get('wazn', '')),
            (t('verb_type', lang), vtype.get('title_ur', '')),
            (t('masdar', lang), verb.get('masdar') or '—'),
            (t('ism_fail', lang), verb.get('ism_fail') or '—'),
            (t('ism_mafool', lang), verb.get('ism_mafool') or na),
            (t('transitivity', lang), verb.get('transitivity', '')),
        ], small_keys=(t('verb_type', lang), t('transitivity', lang))),
            unsafe_allow_html=True)
        if verb.get('unavailable_note'):
            theme.notice(verb['unavailable_note'])

    # ---- ② چار بنیادی صورتیں --------------------------------------------
    with _section('②', 'چار بنیادی صورتیں', lang):
        st.markdown(theme.fact_grid([
            (t('past_active', lang), verb.get('past_3ms') or '—'),
            (t('present_active', lang), verb.get('present_3ms') or '—'),
            (t('past_passive', lang), verb.get('past_passive_3ms') or na),
            (t('present_passive', lang), verb.get('present_passive_3ms') or na),
        ]), unsafe_allow_html=True)

    # ---- ③ مکمل گردان ---------------------------------------------------
    with _section('③', t('nav_gardaan', lang), lang):
        for key in FOUR:
            rows = conj.get(key) or []
            st.markdown(
                f'<div class="qa-tense-head">{theme.esc(t(key, lang))}</div>',
                unsafe_allow_html=True)
            st.markdown(theme.gardaan_grid(rows, lang), unsafe_allow_html=True)
            if rows:
                with st.expander('%s — %s' % (t('th_urdu', lang),
                                              t(key, lang))):
                    st.markdown(theme.gardaan_meaning_list(rows, lang),
                                unsafe_allow_html=True)

    # ---- ④ امر و نہی ----------------------------------------------------
    with _section('④', '%s · %s' % (t('imperative', lang),
                                    t('prohibition', lang)), lang):
        left, right = st.columns(2)
        with left:
            st.markdown(
                f'<div class="qa-tense-head">'
                f'{theme.esc(t("imperative", lang))}</div>',
                unsafe_allow_html=True)
            st.markdown(theme.gardaan_grid(conj.get('imperative') or [], lang),
                        unsafe_allow_html=True)
        with right:
            st.markdown(
                f'<div class="qa-tense-head">'
                f'{theme.esc(t("prohibition", lang))}</div>',
                unsafe_allow_html=True)
            st.markdown(theme.gardaan_grid(conj.get('prohibition') or [], lang),
                        unsafe_allow_html=True)

    # ---- ⑤ مشتقات -------------------------------------------------------
    with _section('⑤', t('derived', lang), lang):
        derived = verb.get('derived_nouns') or {}
        if derived:
            st.markdown(theme.simple_table(
                [t('th_sigha', lang), t('th_arabic', lang), t('wazn', lang),
                 t('th_urdu', lang)],
                [[d.get('label_ur', ''), d.get('arabic', ''),
                  d.get('pattern', ''), d.get('meaning_urdu', '')]
                 for d in derived.values() if isinstance(d, dict)],
                lang, ['qa-ur', 'qa-ar', 'qa-pron', 'qa-ur']),
                unsafe_allow_html=True)
        else:
            theme.notice(na)

    # ---- ⑥ اسی مادہ کے دیگر افعال ---------------------------------------
    with _section('⑥', '%s — %s' % (t('nav_afaal', lang),
                                    verb.get('root', '')), lang):
        render_afaal(analyzer, verb, lang)

    # ---- ⑦ اس باب کی وضاحت ----------------------------------------------
    baab = result.get('baab') or {}
    with _section('⑦', '%s — %s' % (t('baab', lang),
                                    baab.get('name_ar', '')), lang):
        st.markdown(
            f'<div class="qa-info">{theme.esc(baab.get("meaning_ur",""))}</div>',
            unsafe_allow_html=True)
        st.markdown(f'<div class="qa-card" dir="ltr" style="text-align:left">'
                    f'{theme.esc(baab.get("meaning_en",""))}</div>',
                    unsafe_allow_html=True)

    # ---- ⑧ قرآن مجید میں استعمال ----------------------------------------
    ayaat = result.get('quranic_usage') or []
    with _section('⑧', '%s (%d)' % (t('nav_quran', lang), len(ayaat)), lang):
        render_quranic(ayaat, lang)

    # ---- PDF ------------------------------------------------------------
    st.markdown('---')
    render_pdf(pdf_gen, result, lang)


def _section(number: str, title: str, lang: str, expanded: bool = False):
    """A numbered, click-to-open section of the verb page.

    Returns the expander, so callers use it as a context manager.  Only the
    first section opens by default: the page then fits on one screen and the
    student chooses what to look at, instead of scrolling past everything.
    """
    return st.expander('%s  %s' % (number, title), expanded=expanded)


def render_afaal(analyzer, verb: dict, lang: str):
    na = t('not_applicable', lang)
    afaal = analyzer.get_afaal_for_root(verb.get('root', ''))
    rows, present = [], []
    for entry in afaal:
        info = entry['baab_info']
        if entry['available']:
            for v in entry['verbs']:
                here = ' ◀' if v.get('id') == verb.get('id') else ''
                rows.append([info['name_ar'] + here, v.get('arabic', ''),
                             v.get('present_3ms', ''),
                             v.get('past_passive_3ms') or na,
                             v.get('masdar', ''), v.get('meaning_urdu', '')])
                present.append(v)
        else:
            rows.append([info['name_ar'], '×', '×', '×', '×',
                         t('unavailable', lang)])

    st.markdown(theme.simple_table(
        [t('baab', lang), t('past_active', lang), t('present_active', lang),
         t('past_passive', lang), t('masdar', lang), t('th_urdu', lang)],
        rows, lang, ['qa-ur', 'qa-ar', 'qa-ar', 'qa-ar', 'qa-ar', 'qa-ur']),
        unsafe_allow_html=True)

    others = [v for v in present if v.get('id') != verb.get('id')]
    if others:
        cols = st.columns(min(len(others), 4))
        for i, v in enumerate(others):
            with cols[i % len(cols)]:
                if st.button('%s — %s' % (v.get('arabic'),
                                          v.get('baab_name_arabic')),
                             key='afaal_%s' % v.get('id'),
                             use_container_width=True):
                    open_verb(v)


def render_quranic(usage: list, lang: str):
    # Provenance first, and truthfully.  The specification asks for Islam360
    # only; Islam360 is not reachable here, so the panel says so and names the
    # sources actually used rather than implying a verification never done.
    status = quran_source.verification_status(lang)
    if not status['islam360_verified']:
        srcs = ' · '.join('%s: %s' % (k, v)
                          for k, v in (status.get('sources') or {}).items())
        theme.notice('%s\n\n%s' % (status['blocked_message'], srcs))

    if not usage:
        theme.notice('اس فعل کا قرآن مجید میں کوئی مستند استعمال ہمارے ریکارڈ '
                     'میں نہیں ملا۔', 'info')
        return
    for ex in usage:
        sigha = ex.get('sigha_urdu', '')
        if not ex.get('form_certain', True):
            sigha += ' (احتمالاً)'
        st.markdown(
            f"""<div class="qa-card" dir="rtl">
              <div class="qa-ayah-ref">سورۃ {theme.esc(ex.get('surah_name_arabic',''))}
                  ({theme.esc(ex.get('surah_number',''))}:{theme.esc(ex.get('ayah_number',''))})
                  &nbsp;·&nbsp; <b>{theme.esc(ex.get('highlighted_word',''))}</b>
                  &nbsp;·&nbsp; {theme.esc(sigha)}</div>
              <div class="qa-ayah">{theme.esc(ex.get('arabic_text',''))}</div>
              <div class="qa-ayah-ur">{theme.esc(ex.get('translation_urdu',''))}</div>
              <div class="qa-ayah-en">{theme.esc(ex.get('translation_english',''))}</div>
            </div>""", unsafe_allow_html=True)


def render_pdf(pdf_gen, result: dict, lang: str):
    verb = result['verb']
    conj = result['conjugations']
    name = '%s_%s' % (verb.get('id', 'verb'),
                      (verb.get('root') or '').replace(' ', ''))

    st.markdown(f'#### {t("download_pdf", lang)}')
    left, right = st.columns(2)
    with left:
        st.download_button(
            '📄 %s' % t('pdf_one_page', lang),
            data=pdf_gen.generate_one_page_sheet(
                verb, conj, result.get('baab'), result.get('root_info')),
            file_name='%s_one_page.pdf' % name, mime='application/pdf',
            key='dl_one', use_container_width=True)
    with right:
        st.download_button(
            '📚 %s' % t('pdf_detailed', lang),
            data=pdf_gen.generate_study_sheet(
                verb_data=verb, conjugations=conj,
                quranic_data=result.get('quranic_usage'),
                root_info=result.get('root_info'), baab=result.get('baab'),
                afaal=result.get('afaal')),
            file_name='%s_detailed.pdf' % name, mime='application/pdf',
            key='dl_full', use_container_width=True)


if __name__ == '__main__':
    main()
