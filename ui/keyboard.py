# -*- coding: utf-8 -*-
"""⌨ On-screen Arabic keyboard for the search box.

Added *to* the existing search interface, not in place of it: the box, the
button and the styling are untouched, and the keyboard sits underneath in a
collapsed panel the student opens when they want it.  A device Arabic keyboard
still works exactly as before.

Why it exists: the reader is an older Quran student on a phone or tablet who
very often has no Arabic keyboard installed, and typing harakat on a mobile
keyboard is painful even when one is.

Harakat attach correctly because they are Unicode combining marks — appending
one puts it on the letter already typed, which is precisely the required
behaviour.  Nothing is inserted out of order.
"""

import streamlit as st

from . import theme
from .theme import t

#: the field the keyboard types into
FIELD = 'search_box'

#: letters, laid out as on a real Arabic keyboard row by row
LETTER_ROWS = [
    ['ا', 'أ', 'إ', 'آ', 'ب', 'ت', 'ث', 'ج'],
    ['ح', 'خ', 'د', 'ذ', 'ر', 'ز', 'س', 'ش'],
    ['ص', 'ض', 'ط', 'ظ', 'ع', 'غ', 'ف', 'ق'],
    ['ك', 'ل', 'م', 'ن', 'ه', 'و', 'ي', 'ى'],
    ['ء', 'ؤ', 'ئ', 'ة', 'لا'],
]

#: harakat, with the name a student knows them by
HARAKAT = [
    ('َ', 'فتحہ', 'fatha'),
    ('ِ', 'کسرہ', 'kasra'),
    ('ُ', 'ضمہ', 'damma'),
    ('ْ', 'سکون', 'sukun'),
    ('ّ', 'تشدید', 'shadda'),
    ('ً', 'تنوین فتح', 'tanwin fath (-an)'),
    ('ٍ', 'تنوین کسر', 'tanwin kasr (-in)'),
    ('ٌ', 'تنوین ضم', 'tanwin damm (-un)'),
    ('ٰ', 'کھڑا زبر', 'dagger alef'),
]


#: where a keypress parks its text until the next run
PENDING = 'pending_input'


def _buffer() -> str:
    """What the box will contain — the parked text if any, else the widget's."""
    pending = st.session_state.get(PENDING)
    if pending is not None:
        return pending
    return st.session_state.get(FIELD, '') or ''


def _set(text: str):
    """Park the text.

    Streamlit forbids assigning to a widget's key once that widget exists in
    the current run, and the keyboard is drawn *below* the search box — so a
    keypress records what the box should hold and ``render_home`` applies it at
    the top of the next run, before the box is created.
    """
    st.session_state[PENDING] = text


def append(ch: str):
    _set(_buffer() + ch)


def backspace():
    _set(_buffer()[:-1])


def clear():
    _set('')


def render_keyboard(lang: str = 'ur', on_search=None):
    """Draw the keyboard panel beneath the search box.

    ``on_search`` is called when the student presses the keyboard's own search
    key, so it runs exactly the same analysis as the main button.
    """
    label = {'ur': '⌨ عربی کی بورڈ — انگلی سے لکھیں',
             'ar': '⌨ لوحة المفاتيح العربية',
             'en': '⌨ Arabic keyboard'}.get(lang, '⌨ عربی کی بورڈ')

    with st.expander(label, expanded=False):
        # ---- what has been typed so far ---------------------------------
        typed = _buffer()
        st.markdown(
            '<div class="qa-kb-preview">%s</div>'
            % (theme.esc(typed) if typed else
               '<span class="qa-kb-empty">…</span>'),
            unsafe_allow_html=True)

        # ---- letters -----------------------------------------------------
        for r, row in enumerate(LETTER_ROWS):
            cols = st.columns(8)
            for i, ch in enumerate(row):
                if cols[i].button(ch, key='kb_l_%d_%d' % (r, i),
                                  use_container_width=True):
                    append(ch)
                    st.rerun()

        # ---- harakat -----------------------------------------------------
        st.markdown(
            '<div class="qa-kb-section">%s</div>'
            % theme.esc({'en': 'Harakat — they attach to the letter before',
                         'ar': 'الحركات',
                         'ur': 'حرکات — پچھلے حرف پر لگتی ہیں'}.get(lang,
                                                                    'حرکات')),
            unsafe_allow_html=True)
        cols = st.columns(len(HARAKAT))
        for i, (mark, name_ur, name_en) in enumerate(HARAKAT):
            # ـ is a tatweel: it gives the mark something to sit on so the
            # button shows «ـَ» rather than a mark floating on its own
            if cols[i].button('ـ' + mark, key='kb_h_%d' % i,
                              help=name_en if lang == 'en' else name_ur,
                              use_container_width=True):
                append(mark)
                st.rerun()

        # ---- controls ----------------------------------------------------
        st.markdown('<div class="qa-kb-section">&nbsp;</div>',
                    unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        if c1.button('⌫', key='kb_back', use_container_width=True,
                     help={'en': 'Backspace', 'ar': 'حذف حرف'}.get(lang, 'ایک حرف مٹائیں')):
            backspace()
            st.rerun()
        if c2.button({'en': 'Space', 'ar': 'مسافة'}.get(lang, 'فاصلہ'),
                     key='kb_space', use_container_width=True):
            append(' ')
            st.rerun()
        if c3.button({'en': 'Clear', 'ar': 'مسح'}.get(lang, 'سب مٹائیں'),
                     key='kb_clear', use_container_width=True):
            clear()
            st.rerun()
        if c4.button(t('analyze', lang), key='kb_search',
                     use_container_width=True, type='primary'):
            if on_search:
                on_search(_buffer())
                st.rerun()


def inject_keyboard_css(font_scale: float = 1.0):
    """Styling for the keyboard only — the rest of the page is untouched."""
    st.markdown(f"""
    <style>
    /* the running preview of what has been typed */
    .qa-kb-preview {{
        background: {theme.C['card']};
        border: 2px dashed {theme.C['brand_edge']};
        border-radius: 12px;
        padding: 10px 14px; margin-bottom: 10px;
        min-height: 2.2em; direction: rtl; text-align: center;
        font-family: {theme.ARABIC_STACK};
        font-size: {1.8 * font_scale:.2f}em; color: {theme.C['accent']};
        word-break: break-all;
    }}
    .qa-kb-empty {{ color: {theme.C['ink_faint']}; }}
    .qa-kb-section {{
        color: {theme.C['ink_faint']}; direction: rtl; text-align: right;
        font-size: {0.95 * font_scale:.2f}em; margin: 10px 0 4px 0;
    }}
    /* keyboard keys: big enough for a fingertip on a phone */
    [class*="st-key-kb_l_"] button {{
        font-family: {theme.ARABIC_STACK};
        font-size: {1.6 * font_scale:.2f}em !important;
        min-height: 2.4em !important;
        padding: 0.15em 0.1em !important;
        color: {theme.C['accent']} !important;
    }}
    /* a harakat is a small mark on a tatweel, so it needs to be drawn
       larger than a letter to be legible — and tappable — at all */
    [class*="st-key-kb_h_"] button {{
        font-family: {theme.ARABIC_STACK};
        font-size: {2.3 * font_scale:.2f}em !important;
        min-height: 2.0em !important;
        padding: 0 !important;
        color: {theme.C['accent']} !important;
        font-weight: 700 !important;
    }}
    /* the keyboard's own search key must not overflow its column */
    [class*="st-key-kb_search"] button {{
        font-size: {1.0 * font_scale:.2f}em !important;
        padding: 0.4em 0.3em !important;
    }}
    [class*="st-key-kb_l_"] button:hover,
    [class*="st-key-kb_h_"] button:hover {{
        background: {theme.C['accent_soft']} !important;
    }}
    [class*="st-key-kb_back"] button, [class*="st-key-kb_space"] button,
    [class*="st-key-kb_clear"] button {{
        font-size: {1.15 * font_scale:.2f}em !important;
        min-height: 2.6em !important;
    }}
    /* Streamlit stacks st.columns vertically on a narrow screen, which would
       turn the keyboard into 37 rows of a single key — unusable on exactly
       the device it exists for.  Keep the keyboard's own rows horizontal. */
    /* NB: the selector must match only the keyboard's own row.  Matching any
       block that merely *contains* a key also caught the page's outer
       [1,3,1] layout columns, which then refused to stack and squeezed the
       whole page into a narrow strip — hence the direct-child path. */
    [data-testid="stHorizontalBlock"]:has(> [data-testid="stColumn"]
        > [data-testid="stVerticalBlock"] > [class*="st-key-kb_"]) {{
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 4px !important;
    }}
    [data-testid="stHorizontalBlock"]:has(> [data-testid="stColumn"]
        > [data-testid="stVerticalBlock"] > [class*="st-key-kb_"])
        > [data-testid="stColumn"] {{
        flex: 1 1 0 !important;
        width: auto !important;
        min-width: 0 !important;
    }}

    @media (max-width: 720px) {{
        [class*="st-key-kb_l_"] button {{
            font-size: {1.25 * font_scale:.2f}em !important;
            min-height: 2.5em !important;
            padding: 0 !important;
        }}
        [class*="st-key-kb_h_"] button {{
            font-size: {1.8 * font_scale:.2f}em !important;
            min-height: 2.1em !important;
        }}
        [class*="st-key-kb_back"] button, [class*="st-key-kb_space"] button,
        [class*="st-key-kb_clear"] button,
        [class*="st-key-kb_search"] button {{
            font-size: {0.85 * font_scale:.2f}em !important;
            padding: 0.4em 0.1em !important;
        }}
        .qa-kb-preview {{ font-size: {1.5 * font_scale:.2f}em; }}
    }}
    </style>
    """, unsafe_allow_html=True)
