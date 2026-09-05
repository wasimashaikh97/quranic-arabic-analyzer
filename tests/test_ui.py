# -*- coding: utf-8 -*-
"""End-to-end interface tests.

These drive the real Streamlit app through ``AppTest`` — the same script the
browser runs — so a broken control or an exception in a section is caught here
rather than by the student.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from streamlit.testing.v1 import AppTest                        # noqa: E402

from core.arabic_utils import canonical_marks                   # noqa: E402

APP = str(Path(__file__).parent.parent / 'app.py')
TIMEOUT = 120

SPEC_VERBS = ['كَتَبَ', 'أَنْزَلَ', 'أَخْرَجَ', 'عَلَّمَ', 'تَقَبَّلَ',
              'اِخْتَلَفَ', 'اِنْتَفَعَ', 'اِسْتَهْزَأَ', 'قَالَ', 'دَعَا',
              'رَمَى', 'رَدَّ', 'أَكَلَ', 'قَرَأَ']


def fresh() -> AppTest:
    at = AppTest.from_file(APP, default_timeout=TIMEOUT)
    at.run()
    return at


def submit(at: AppTest, word: str) -> AppTest:
    at.text_input[0].set_value(word)
    for btn in at.button:
        if btn.proto.form_id:
            btn.click().run()
            return at
    raise AssertionError('search submit button not found')


def click_key(at: AppTest, key: str) -> AppTest:
    for btn in at.button:
        if btn.key == key:
            btn.click().run()
            return at
    raise AssertionError('button %r not found; have: %s'
                         % (key, [b.key for b in at.button][:30]))


def all_text(at: AppTest) -> str:
    """Everything on the page, including the collapsible section headings.

    The numbered sections are expanders, so their titles live in the expander
    label rather than in a markdown block.
    """
    parts = [str(m.value) for m in at.markdown]
    try:
        parts += [str(e.label) for e in at.expander]
    except Exception:                                   # pragma: no cover
        pass
    return '\n'.join(parts)


def contains_ar(haystack: str, needle: str) -> bool:
    """Substring test that ignores the order the marks were written in.

    The Quran text and a dictionary head-word may order shadda and the vowel
    differently; both spellings are the same word.
    """
    return canonical_marks(needle) in canonical_marks(haystack)


# ===========================================================================
class TestSimplicity(unittest.TestCase):
    """The interface must stay small enough for an older reader."""

    def test_home_is_one_box_and_one_button(self):
        at = fresh()
        self.assertFalse(at.exception, at.exception)
        self.assertEqual(len(at.text_input), 1)
        self.assertIn('عربی فعل اور گردان', all_text(at))

    def test_no_root_baab_or_tense_selectors(self):
        at = fresh()
        self.assertEqual(len(at.selectbox), 0)
        self.assertEqual(len(at.radio), 1)          # only the language switch
        self.assertIn('زبان', at.radio[0].label)

    @staticmethod
    def _chrome(at):
        """Buttons that are page furniture, excluding the keyboard.

        The on-screen keyboard is a required input aid and ships collapsed, so
        its keys are not clutter the reader has to wade through; what these
        guards protect against is navigation creeping back.
        """
        return [b for b in at.button if not str(b.key).startswith('kb_')]

    def test_home_button_count_is_small(self):
        """Home used to render 28 buttons; keep it lean."""
        at = fresh()
        chrome = self._chrome(at)
        self.assertLessEqual(len(chrome), 14,
                             'home has too many controls: %s'
                             % [b.key for b in chrome])

    def test_result_button_count_is_small(self):
        """The result page used to render 42 buttons."""
        at = submit(fresh(), 'أَنْزَلَ')
        chrome = self._chrome(at)
        self.assertLessEqual(len(chrome), 20,
                             'result page has too many controls: %s'
                             % [b.key for b in chrome])

    def test_keyboard_is_collapsed_by_default(self):
        """It must be available without being in the way."""
        at = fresh()
        kb = [e for e in at.expander if 'کی بورڈ' in str(e.label)
              or 'keyboard' in str(e.label).lower()]
        self.assertTrue(kb, 'the Arabic keyboard panel is missing')
        self.assertFalse(kb[0].proto.expanded,
                         'the keyboard should start closed')

    def test_removed_features_are_gone(self):
        at = fresh()
        keys = {str(b.key) for b in at.button}
        for gone in ('side_practice', 'side_flashcards', 'side_dashboard',
                     'side_compare', 'side_bookmarks', 'listen_btn',
                     'save_btn', 'nav_table', 'nav_tree', 'nav_learn'):
            self.assertNotIn(gone, keys, '%s should have been removed' % gone)


# ===========================================================================
class TestVerbPage(unittest.TestCase):
    def test_every_spec_verb_renders(self):
        for word in SPEC_VERBS:
            at = submit(fresh(), word)
            self.assertFalse(at.exception, '%s -> %s' % (word, at.exception))
            text = all_text(at)
            self.assertIn('فعل کی معلومات', text, word)
            self.assertIn(word, text, word)

    def test_all_eight_sections_present(self):
        at = submit(fresh(), 'أَنْزَلَ')
        text = all_text(at)
        for section in ('فعل کی معلومات', 'چار بنیادی صورتیں', 'مکمل گردان',
                        'امر', 'نہی', 'مشتقات', 'تمام افعال', 'باب',
                        'قرآن میں استعمال'):
            self.assertIn(section, text, section)

    def test_identity_facts(self):
        at = submit(fresh(), 'أَنْزَلَ')
        text = all_text(at)
        for expected in ('ن ز ل', 'إفعال', 'أَفْعَلَ', 'إِنْزَال',
                         'مُنْزِل', 'مُنْزَل'):
            self.assertIn(expected, text, expected)

    def test_four_principal_parts_shown(self):
        at = submit(fresh(), 'أَنْزَلَ')
        text = all_text(at)
        for expected in ('أَنْزَلَ', 'يُنْزِلُ', 'أُنْزِلَ', 'يُنْزَلُ'):
            self.assertIn(expected, text, expected)

    def test_gardaan_uses_the_book_grid(self):
        """واحد / مثنی / جمع columns and غائب / حاضر / متکلم rows."""
        at = submit(fresh(), 'أَنْزَلَ')
        text = all_text(at)
        for label in ('واحد', 'مثنی', 'جمع',
                      'غائب مذکر', 'غائب مؤنث', 'حاضر مذکر', 'حاضر مؤنث',
                      'متکلم'):
            self.assertIn(label, text, label)
        self.assertIn('qa-grid-table', text)

    def test_grid_contains_the_right_forms(self):
        at = submit(fresh(), 'أَنْزَلَ')
        text = all_text(at)
        for form in ('أَنْزَلَا', 'أَنْزَلُوا', 'أَنْزَلْنَ', 'أَنْزَلْتُمَا',
                     'أَنْزَلْنَا', 'يُنْزِلُونَ', 'أُنْزِلَتْ', 'تُنْزَلِينَ'):
            self.assertIn(form, text, form)

    def test_intransitive_shows_not_applicable(self):
        at = submit(fresh(), 'اِنْكَسَرَ')
        text = all_text(at)
        self.assertIn('قابلِ اطلاق نہیں', text)
        self.assertIn('مطاوعت', text)

    def test_absent_baab_marked_with_times(self):
        """The book's × for a باب with no attested verb for the root."""
        at = submit(fresh(), 'أَنْزَلَ')
        self.assertIn('×', all_text(at))

    def test_afaal_lists_the_root(self):
        at = submit(fresh(), 'أَنْزَلَ')
        text = all_text(at)
        for expected in ('نَزَلَ', 'نَزَّلَ', 'أَنْزَلَ', 'اِسْتَنْزَلَ'):
            self.assertIn(expected, text, expected)

    def test_other_root_verbs_are_clickable(self):
        at = submit(fresh(), 'أَنْزَلَ')
        buttons = [b for b in at.button if str(b.key).startswith('afaal_')]
        self.assertTrue(buttons, 'no clickable sibling verbs')
        at2 = buttons[0].click().run()
        self.assertFalse(at2.exception, at2.exception)
        self.assertIn('فعل کی معلومات', all_text(at2))

    def test_conjugated_input_is_parsed(self):
        at = submit(fresh(), 'يُنْزِلُ')
        text = all_text(at)
        self.assertIn('آپ کا لکھا ہوا لفظ', text)
        self.assertIn('أَنْزَلَ', text)
        self.assertIn('مضارع معروف', text)


# ===========================================================================
class TestQuranicSection(unittest.TestCase):
    """The Quranic ayaat — one of the three things the app exists to do."""

    def test_ayaat_shown_with_reference_and_sigha(self):
        at = submit(fresh(), 'أَنْزَلَ')
        text = all_text(at)
        self.assertIn('سورۃ', text)
        self.assertIn('أَنزَلْنَا', text)
        self.assertIn('جمع متکلم', text)

    def test_ayaat_carry_both_translations(self):
        at = submit(fresh(), 'كَوَّرَ')
        text = all_text(at)
        self.assertTrue(contains_ar(text, 'كُوِّرَتْ'), '81:1 not shown')
        self.assertIn('qa-ayah-ur', text)
        self.assertIn('qa-ayah-en', text)

    def test_verb_without_occurrence_says_so(self):
        at = submit(fresh(), 'اِنْكَسَرَ')
        self.assertIn('قرآن مجید میں کوئی مستند استعمال', all_text(at))

    def test_book_examples_appear(self):
        """Verbs from the reference book's مجہول page find their ayaat."""
        for word, expected in (('اِنْفَطَرَ', 'ٱنفَطَرَتْ'),
                               ('كَوَّرَ', 'كُوِّرَتْ'),
                               ('خَفَّفَ', 'يُخَفَّفُ'),
                               ('تَقَبَّلَ', 'تَقَبَّلْ')):
            at = submit(fresh(), word)
            self.assertTrue(contains_ar(all_text(at), expected),
                            '%s / %s' % (word, expected))


# ===========================================================================
class TestInvalidInput(unittest.TestCase):
    def test_empty(self):
        at = submit(fresh(), '')
        self.assertFalse(at.exception)
        self.assertIn('براہ کرم عربی لفظ درج کریں۔', all_text(at))

    def test_english(self):
        at = submit(fresh(), 'hello')
        self.assertFalse(at.exception)
        self.assertIn('براہ کرم عربی حروف', all_text(at))

    def test_unknown_arabic_invents_nothing(self):
        at = submit(fresh(), 'زززز')
        self.assertFalse(at.exception)
        text = all_text(at)
        self.assertIn('مستند صرفی معلومات دستیاب نہیں', text)
        self.assertNotIn('چار بنیادی صورتیں', text)


# ===========================================================================
class TestControls(unittest.TestCase):
    def test_text_size(self):
        at = fresh()
        before = at.session_state['font_scale']
        at = click_key(at, 'font_up')
        self.assertGreater(at.session_state['font_scale'], before)
        at = click_key(at, 'font_reset')
        self.assertAlmostEqual(at.session_state['font_scale'], 1.15, places=2)

    def test_three_languages(self):
        for code, expected in (('en', 'Arabic Verbs'),
                               ('ar', 'الأفعال العربية'),
                               ('ur', 'عربی فعل')):
            at = fresh()
            at.radio[0].set_value(code).run()
            self.assertFalse(at.exception, at.exception)
            self.assertIn(expected, all_text(at), code)

    def test_english_verb_page(self):
        at = fresh()
        at.radio[0].set_value('en').run()
        at = submit(at, 'كَتَبَ')
        self.assertFalse(at.exception, at.exception)
        self.assertIn('Verb information', all_text(at))

    def test_abwaab_page(self):
        at = click_key(fresh(), 'go_abwaab')
        self.assertFalse(at.exception, at.exception)
        text = all_text(at)
        self.assertIn('ابواب ثلاثی مزید فیہ', text)
        for name in ('إفعال', 'تفعیل', 'مفاعلة', 'تفعّل', 'تفاعل',
                     'انفعال', 'افتعال', 'استفعال'):
            self.assertIn(name, text, name)

    def test_home_button_returns(self):
        at = click_key(fresh(), 'go_abwaab')
        at = click_key(at, 'go_home')
        self.assertFalse(at.exception, at.exception)
        self.assertEqual(at.session_state['page'], 'home')

    def test_example_chip(self):
        at = click_key(fresh(), 'ex_أَنْزَلَ')
        self.assertFalse(at.exception, at.exception)
        self.assertIn('فعل کی معلومات', all_text(at))


# ===========================================================================
class TestPdfButtons(unittest.TestCase):
    def test_both_downloads_render(self):
        at = submit(fresh(), 'أَنْزَلَ')
        self.assertFalse(at.exception, at.exception)
        downloads = at.get('download_button')
        self.assertGreaterEqual(len(downloads), 2,
                                'expected the one-page and detailed PDFs')

    def test_pdf_generation_never_raises(self):
        for word in ('أَنْزَلَ', 'خَرَجَ', 'دَعَا', 'رَدَّ', 'اِنْكَسَرَ'):
            at = submit(fresh(), word)
            self.assertFalse(at.exception, '%s -> %s' % (word, at.exception))


if __name__ == '__main__':
    unittest.main(verbosity=2)


# ===========================================================================
class TestCollapsibleSections(unittest.TestCase):
    """The verb page is an accordion: only the first section opens itself."""

    def test_sections_are_expanders(self):
        at = submit(fresh(), 'أَنْزَلَ')
        labels = [str(e.label) for e in at.expander]
        for number in ('①', '②', '③', '④', '⑤', '⑥', '⑦', '⑧'):
            self.assertTrue(any(number in l for l in labels),
                            'section %s is not collapsible' % number)

    def test_only_the_first_section_starts_open(self):
        at = submit(fresh(), 'أَنْزَلَ')
        numbered = [e for e in at.expander
                    if any(n in str(e.label) for n in '①②③④⑤⑥⑦⑧')]
        # the open/closed state lives on the proto, not on the wrapper
        opened = [str(e.label) for e in numbered if e.proto.expanded]
        self.assertEqual(len(opened), 1,
                         'expected one open section, got %s' % opened)
        self.assertIn('①', opened[0])

    def test_collapsed_sections_still_hold_their_content(self):
        """Collapsed only hides it visually — the content is rendered."""
        at = submit(fresh(), 'أَنْزَلَ')
        text = all_text(at)
        self.assertIn('أَنْزَلْتُمَا', text)      # inside ③
        self.assertIn('إِنْزَال', text)           # inside ⑤
        self.assertIn('اِسْتَنْزَلَ', text)        # inside ⑥
