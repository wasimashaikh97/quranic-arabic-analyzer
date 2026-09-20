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

    # A root the Quran uses, but never as a verb.  نَامَ is a real Arabic verb
    # and ن و م is a Quranic root, yet the Quran has only نَوْم، مَنَام،
    # نَاۗىِٕمُوْنَ.  Saying precisely that beats a bare «not found».
    no_verb = result.get('root_no_verb')
    if no_verb:
        theme.notice(
            {'en': 'The root %s does occur in the Quran, but never as a verb. '
                   'Its Quranic words, from Islam360, are below — no verb was '
                   'constructed for it.',
             'ar': 'المادة %s واردة في القرآن لكن لا كفعل.'}.get(
                lang,
                'یہ مادہ (%s) قرآن مجید میں آیا ہے، مگر فعل کے طور پر نہیں۔ '
                'اسلام۳۶۰ کے مطابق اس کے قرآنی الفاظ نیچے ہیں — اس کا کوئی '
                'فعل خود سے نہیں بنایا گیا۔') % no_verb['root'], 'info')
        st.markdown(
            '<div class="qa-card" dir="rtl" style="text-align:center;'
            'line-height:2.4">%s</div>'
            % ' &nbsp;·&nbsp; '.join(theme.esc(w) for w in no_verb['words']),
            unsafe_allow_html=True)
        if no_verb.get('lughaat'):
            with st.expander('📗 %s' % {
                    'en': 'Islam360 lexicon (لغات) for this root',
                    'ar': 'لغات إسلام360'}.get(
                    lang, 'اسلام۳۶۰ کی لغات — اس مادہ کی تشریح')):
                st.markdown(
                    '<div class="qa-card" dir="rtl" style="line-height:2.1">'
                    '%s</div>' % theme.esc(no_verb['lughaat']),
                    unsafe_allow_html=True)

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
        render_quranic(ayaat, lang, result.get('islam360_lughaat'))

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


def render_quranic(usage: list, lang: str, lughaat: dict = None):
    # Provenance first, and truthfully: whichever of the two states is actually
    # true.  Islam360 when its data is present, otherwise the fallback named
    # openly — never a verification that was not performed.
    status = quran_source.verification_status(lang)
    if status['islam360_verified']:
        counts = {'en': '%s ayaat · %s roots',
                  'ar': '%s آية · %s مادة'}.get(lang, '%s آیات · %s مادے')
        theme.notice('%s  —  %s' % (status['ok_message'],
                                    counts % (status.get('ayat', ''),
                                              status.get('roots', ''))),
                     'info')
        # Islam360 indexes by root; it does not tag صیغہ.  Say which part of
        # what follows is its and which is the tagged morphology's.
        theme.notice(
            {'en': 'Verse text, surah names and both translations are '
                   'Islam360’s. The صیغہ label under each verse is from '
                   'the tagged morphology — Islam360 does not tag صیغہ.',
             'ar': 'نصّ الآية والترجمتان من إسلام360؛ وسم الصيغة من التحليل '
                   'الصرفي.'}.get(
                lang,
                'آیت کا متن، سورۃ کے نام اور دونوں ترجمے اسلام۳۶۰ کے ہیں۔ '
                'ہر آیت کے نیچے صیغے کی شناخت صرفی تجزیے سے ہے — اسلام۳۶۰ '
                'صیغہ متعین نہیں کرتا۔'), 'info')
    else:
        srcs = ' · '.join('%s: %s' % (k, v)
                          for k, v in (status.get('sources') or {}).items())
        theme.notice('%s\n\n%s' % (status['blocked_message'], srcs))

    # Islam360's own لغات article for the root, when it has one
    if lughaat and lughaat.get('lughaat'):
        with st.expander('📗 %s' % {'en': 'Islam360 lexicon (لغات) for this root',
                                    'ar': 'لغات إسلام360'}.get(
                lang, 'اسلام۳۶۰ کی لغات — اس مادہ کی تشریح')):
            st.markdown(
                '<div class="qa-card" dir="rtl" style="line-height:2.1">%s</div>'
                % theme.esc(lughaat['lughaat']), unsafe_allow_html=True)

    if not usage:
        theme.notice({
            'en': 'No attested occurrence of this verb in the Quran is in '
                  'our records.',
            'ar': 'لم نجد لهذا الفعل استعمالاً موثّقاً في القرآن الكريم.'}.get(
            lang, 'اس فعل کا قرآن مجید میں کوئی مستند استعمال ہمارے ریکارڈ '
                  'میں نہیں ملا۔'), 'info')
        return

    # Two different claims, kept apart on purpose.  «This verb occurs here» is
    # only said of occurrences the tagged morphology attests.  A root-level
    # listing is Islam360's own but is not صیغہ-analysed and holds other words
    # of the same root, so it never stands in for the verb: the honest answer
    # («this verb is not attested») comes first, and the root listing is
    # offered separately, folded away, for whoever wants it.
    root_level = [ex for ex in usage if ex.get('root_level')]
    attested = [ex for ex in usage if not ex.get('root_level')]

    if attested:
        _render_ayaat(attested, lang)

    if root_level:
        if not attested:
            theme.notice({
                'en': 'This verb, in this باب, has no attested occurrence in '
                      'the Quran.',
                'ar': 'لا يوجد لهذا الفعل في هذا الباب استعمال موثّق في '
                      'القرآن.'}.get(
                lang, 'اس فعل (اسی باب میں) کا قرآن مجید میں کوئی مستند '
                      'استعمال نہیں ملا۔'), 'info')
        with st.expander('📖 %s' % {
                'en': 'Other words of this root in the Quran (Islam360) — '
                      'not صیغہ-analysed',
                'ar': 'كلمات أخرى من هذه المادة (إسلام360)'}.get(
                lang, 'اسی مادہ کے دوسرے قرآنی الفاظ (اسلام۳۶۰) — '
                      'ان کا صیغہ متعین نہیں کیا گیا')):
            _render_ayaat(root_level, lang)


def _render_ayaat(usage: list, lang: str = 'ur'):
    """One ayah card per occurrence, in the section's existing card style.

    Every card exists in three languages: the reference line, the صیغہ and
    the confirmation label follow the interface language, and the reader's
    own translation comes first.  The Arabic of the verse is the Arabic.
    """
    surah_word = {'en': 'Surah', 'ar': 'سورة'}.get(lang, 'سورۃ')
    verified = {'en': '✓ Islam360', 'ar': '✓ إسلام360'}.get(lang, '✓ اسلام۳۶۰')
    uncertain = {'en': ' (probable)', 'ar': ' (على الأرجح)'}.get(lang, ' (احتمالاً)')
    direction = 'ltr' if lang == 'en' else 'rtl'

    for ex in usage:
        if lang == 'en':
            sigha = ex.get('sigha_english') or ex.get('sigha_urdu', '')
            surah = ex.get('surah_name_english') or ex.get('surah_name_arabic', '')
        else:
            sigha = ex.get('sigha_urdu', '')
            surah = ex.get('surah_name_arabic', '')
        if sigha and not ex.get('form_certain', True):
            sigha += uncertain
        sigha_html = ('&nbsp;·&nbsp; %s' % theme.esc(sigha)) if sigha else ''
        # said only when Islam360 itself lists this word at this ayah under
        # this root — a claim checked per ayah, never assumed from the panel
        verified_html = ''
        if ex.get('islam360_confirmed'):
            verified_html = ('&nbsp;·&nbsp; <span style="color:#166534;'
                             'font-size:.85em" title="Islam360">%s</span>'
                             % theme.esc(verified))
        ur = ('<div class="qa-ayah-ur">%s</div>'
              % theme.esc(ex.get('translation_urdu', '')))
        en = ('<div class="qa-ayah-en">%s</div>'
              % theme.esc(ex.get('translation_english', '')))
        translations = en + ur if lang == 'en' else ur + en
        st.markdown(
            f"""<div class="qa-card" dir="{direction}">
              <div class="qa-ayah-ref">{theme.esc(surah_word)} {theme.esc(surah)}
                  ({theme.esc(ex.get('surah_number',''))}:{theme.esc(ex.get('ayah_number',''))})
                  &nbsp;·&nbsp; <b dir="rtl">{theme.esc(ex.get('highlighted_word',''))}</b>
                  {sigha_html}{verified_html}</div>
              <div class="qa-ayah" dir="rtl">{theme.esc(ex.get('arabic_text',''))}</div>
              {translations}
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
                # only occurrences of this verb itself: the root-level
                # listing carries a caveat the printed sheet cannot show
                quranic_data=[ex for ex in (result.get('quranic_usage') or [])
                              if not ex.get('root_level')],
                root_info=result.get('root_info'), baab=result.get('baab'),
                afaal=result.get('afaal')),
            file_name='%s_detailed.pdf' % name, mime='application/pdf',
            key='dl_full', use_container_width=True)


if __name__ == '__main__':
    main()
