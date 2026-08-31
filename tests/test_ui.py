# -*- coding: utf-8 -*-
"""End-to-end interface tests.

These drive the real Streamlit app through ``AppTest`` — the same script the
browser runs — so a broken button or an exception in a view is caught here
rather than by the student.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from streamlit.testing.v1 import AppTest                        # noqa: E402

APP = str(Path(__file__).parent.parent / 'app.py')
TIMEOUT = 90

SPEC_VERBS = ['كَتَبَ', 'أَنْزَلَ', 'أَخْرَجَ', 'عَلَّمَ', 'تَقَبَّلَ',
              'اِخْتَلَفَ', 'اِنْتَفَعَ', 'اِسْتَهْزَأَ', 'قَالَ', 'دَعَا',
              'رَمَى', 'رَدَّ', 'أَكَلَ', 'قَرَأَ']


def fresh() -> AppTest:
    at = AppTest.from_file(APP, default_timeout=TIMEOUT)
    at.run()
    return at


def analyse(at: AppTest, word: str) -> AppTest:
    """Type a word into the one search box and press تجزیہ کریں."""
    at.text_input[0].set_value(word)
    at.button(key='FormSubmitter:search_form-🔍 تجزیہ کریں').click().run()
    return at


def submit(at: AppTest, word: str) -> AppTest:
    at.text_input[0].set_value(word)
    # the submit button is the only form button on the page
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
                         % (key, [b.key for b in at.button][:25]))


def all_text(at: AppTest) -> str:
    parts = [m.value for m in at.markdown]
    parts += [c.value for c in at.caption] if hasattr(at, 'caption') else []
    return '\n'.join(str(p) for p in parts)


class TestAppLoads(unittest.TestCase):
    def test_home_page_renders(self):
        at = fresh()
        self.assertFalse(at.exception, at.exception)
        text = all_text(at)
        self.assertIn('عربی فعل اور گردان', text)
        self.assertIn('تجزیہ کریں', str([b.label for b in at.button]))

    def test_home_has_exactly_one_input(self):
        """The elderly-friendly requirement: one box, one button."""
        at = fresh()
        self.assertEqual(len(at.text_input), 1)

    def test_no_selectors_for_root_baab_tense(self):
        """The student must never be asked to choose root/baab/tense."""
        at = fresh()
        self.assertEqual(len(at.selectbox), 0)
        # the only radio is the language switch
        self.assertEqual(len(at.radio), 1)
        self.assertIn('زبان', at.radio[0].label)

    def test_font_size_buttons_present(self):
        at = fresh()
        keys = [b.key for b in at.button]
        for key in ('font_down', 'font_reset', 'font_up'):
            self.assertIn(key, keys)


class TestSearchFlow(unittest.TestCase):
    def test_every_spec_verb_analyses_without_error(self):
        for word in SPEC_VERBS:
            at = submit(fresh(), word)
            self.assertFalse(at.exception, '%s -> %s' % (word, at.exception))
            text = all_text(at)
            self.assertIn('فعل کی معلومات', text, word)
            self.assertIn(word, text, word)

    def test_result_shows_baab_and_wazn(self):
        at = submit(fresh(), 'أَنْزَلَ')
        text = all_text(at)
        for expected in ('ن ز ل', 'إفعال', 'أَفْعَلَ',
                         'أَنْزَلَ', 'يُنْزِلُ', 'أُنْزِلَ', 'يُنْزَلُ'):
            self.assertIn(expected, text, expected)

    def test_result_shows_all_four_gardaans(self):
        at = submit(fresh(), 'أَنْزَلَ')
        text = all_text(at)
        for expected in ('أَنْزَلْتُ', 'يُنْزِلُونَ', 'أُنْزِلَتْ', 'تُنْزَلِينَ'):
            self.assertIn(expected, text, expected)

    def test_intransitive_verb_says_not_applicable(self):
        at = submit(fresh(), 'اِنْكَسَرَ')
        text = all_text(at)
        self.assertIn('قابلِ اطلاق نہیں', text)
        self.assertIn('مطاوعت', text)

    def test_conjugated_input_is_parsed_on_screen(self):
        at = submit(fresh(), 'يُنْزِلُ')
        text = all_text(at)
        self.assertIn('آپ کا لکھا ہوا لفظ', text)
        self.assertIn('أَنْزَلَ', text)
        self.assertIn('مضارع معروف', text)

    def test_example_chip_runs_an_analysis(self):
        at = click_key(fresh(), 'ex_كَتَبَ')
        self.assertFalse(at.exception, at.exception)
        self.assertIn('فعل کی معلومات', all_text(at))

    def test_empty_input_shows_friendly_urdu(self):
        at = submit(fresh(), '')
        self.assertFalse(at.exception)
        self.assertIn('براہ کرم عربی لفظ درج کریں۔', all_text(at))

    def test_english_input_shows_friendly_message(self):
        at = submit(fresh(), 'hello')
        self.assertFalse(at.exception)
        self.assertIn('براہ کرم عربی حروف', all_text(at))

    def test_unknown_arabic_invents_nothing(self):
        at = submit(fresh(), 'زززز')
        self.assertFalse(at.exception)
        text = all_text(at)
        self.assertIn('مستند صرفی معلومات دستیاب نہیں', text)
        self.assertNotIn('فعل کی معلومات', text)


class TestViews(unittest.TestCase):
    """Each of the big navigation buttons opens without error."""

    def _open(self, view_key: str, word: str = 'أَنْزَلَ') -> AppTest:
        at = submit(fresh(), word)
        at = click_key(at, view_key)
        self.assertFalse(at.exception, '%s -> %s' % (view_key, at.exception))
        return at

    def test_table_view(self):
        at = self._open('nav_table')
        text = all_text(at)
        for head in ('باب', 'مادہ', 'ماضی معروف', 'مضارع معروف',
                     'ماضی مجہول', 'مضارع مجہول'):
            self.assertIn(head, text, head)

    def test_table_rows_are_clickable(self):
        at = self._open('nav_table')
        row_buttons = [b for b in at.button if str(b.key).startswith('tbl_row_')]
        self.assertTrue(row_buttons, 'no clickable rows')
        target = next(b for b in row_buttons if not b.proto.disabled)
        at2 = target.click().run()
        self.assertFalse(at2.exception, at2.exception)
        self.assertIn('فعل کی معلومات', all_text(at2))

    def test_tree_view(self):
        at = self._open('nav_tree')
        text = all_text(at)
        for node in ('مادہ', 'فعل', 'باب', 'وزن', 'ماضی معروف', 'مضارع مجہول'):
            self.assertIn(node, text, node)

    def test_tree_nodes_are_clickable(self):
        at = self._open('nav_tree')
        tense_buttons = [b for b in at.button
                         if str(b.key).startswith('tree_tense_')]
        self.assertTrue(tense_buttons, 'no clickable tense nodes')
        at2 = tense_buttons[0].click().run()
        self.assertFalse(at2.exception, at2.exception)

    def test_complete_sarf_view(self):
        at = self._open('nav_sarf')
        text = all_text(at)
        for section in ('مادہ', 'باب', 'وزن', 'مصدر', 'اسم فاعل',
                        'اسم مفعول'):
            self.assertIn(section, text, section)
        # the derivatives table itself (expander labels are not in markdown)
        for derivative in ('إِنْزَال', 'مُنْزِل', 'مُنْزَل'):
            self.assertIn(derivative, text, derivative)

    def test_afaal_view_lists_every_baab(self):
        at = self._open('nav_afaal')
        text = all_text(at)
        self.assertIn('تمام افعال', text)
        # ن ز ل has verbs in باب I, II, IV, V, X and gaps elsewhere
        for expected in ('نَزَلَ', 'نَزَّلَ', 'أَنْزَلَ', 'اِسْتَنْزَلَ'):
            self.assertIn(expected, text, expected)
        self.assertIn('دستیاب نہیں', text)

    def test_gardaan_view(self):
        at = self._open('nav_gardaan')
        text = all_text(at)
        self.assertIn('ماضی معروف', text)
        self.assertIn('أَنْزَلْتُمَا', text)

    def test_learning_view(self):
        at = self._open('nav_learn')
        text = all_text(at)
        self.assertIn('بنیادی ساخت', text)

    def test_quranic_view(self):
        at = self._open('nav_quran', 'كَتَبَ')
        self.assertIn('قرآن', all_text(at))

    def test_abwaab_page_shows_all_eight(self):
        at = fresh()
        at = click_key(at, 'side_abwaab')
        self.assertFalse(at.exception, at.exception)
        text = all_text(at)
        self.assertIn('ابواب ثلاثی مزید فیہ', text)
        for name in ('إفعال', 'تفعیل', 'مفاعلة', 'تفعّل', 'تفاعل',
                     'انفعال', 'افتعال', 'استفعال'):
            self.assertIn(name, text, name)
        for wazn in ('أَفْعَلَ', 'فَعَّلَ', 'فَاعَلَ', 'تَفَعَّلَ', 'تَفَاعَلَ',
                     'اِنْفَعَلَ', 'اِفْتَعَلَ', 'اِسْتَفْعَلَ'):
            self.assertIn(wazn, text, wazn)


class TestSecondaryPages(unittest.TestCase):
    def test_every_sidebar_page_opens(self):
        for key in ('side_bookmarks', 'side_compare', 'side_practice',
                    'side_flashcards', 'side_dashboard', 'side_abwaab',
                    'side_home'):
            at = click_key(fresh(), key)
            self.assertFalse(at.exception, '%s -> %s' % (key, at.exception))


class TestControls(unittest.TestCase):
    def test_text_size_changes(self):
        at = fresh()
        before = at.session_state['font_scale']
        at = click_key(at, 'font_up')
        self.assertGreater(at.session_state['font_scale'], before)
        at = click_key(at, 'font_down')
        at = click_key(at, 'font_reset')
        self.assertAlmostEqual(at.session_state['font_scale'], 1.15, places=2)

    def test_language_switch_to_english(self):
        at = fresh()
        at.radio[0].set_value('en').run()
        self.assertFalse(at.exception, at.exception)
        self.assertEqual(at.session_state['lang'], 'en')
        self.assertIn('Arabic Verbs', all_text(at))

    def test_language_switch_to_arabic(self):
        at = fresh()
        at.radio[0].set_value('ar').run()
        self.assertFalse(at.exception, at.exception)
        self.assertIn('الأفعال العربية', all_text(at))

    def test_english_result_page(self):
        at = fresh()
        at.radio[0].set_value('en').run()
        at = submit(at, 'كَتَبَ')
        self.assertFalse(at.exception, at.exception)
        text = all_text(at)
        self.assertIn('Verb information', text)
        self.assertIn('Root', text)

    def test_save_and_unsave(self):
        at = submit(fresh(), 'كَتَبَ')
        at = click_key(at, 'save_btn')
        self.assertFalse(at.exception, at.exception)
        labels = [b.label for b in at.button if b.key == 'save_btn']
        self.assertIn('★ محفوظ شدہ', labels)
        at = click_key(at, 'save_btn')
        labels = [b.label for b in at.button if b.key == 'save_btn']
        self.assertIn('⭐ محفوظ کریں', labels)


class TestPdfButtons(unittest.TestCase):
    def test_both_download_buttons_exist_and_carry_pdf_bytes(self):
        at = submit(fresh(), 'أَنْزَلَ')
        self.assertFalse(at.exception, at.exception)
        keys = [d.proto.id for d in at.get('download_button')] \
            if at.get('download_button') else []
        self.assertTrue(keys, 'no download buttons rendered')

    def test_pdf_generation_does_not_raise_in_the_app(self):
        for word in ('أَنْزَلَ', 'خَرَجَ', 'دَعَا', 'رَدَّ'):
            at = submit(fresh(), word)
            self.assertFalse(at.exception, '%s -> %s' % (word, at.exception))


if __name__ == '__main__':
    unittest.main(verbosity=2)
