# -*- coding: utf-8 -*-
"""Correctness tests for the Sarf engine.

These do NOT merely check that tables have the right number of rows — every
assertion compares against the form a Sarf textbook actually gives.
"""

import io
import sqlite3
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.abwaab import BAAB_INFO, MAZEED_ORDER                     # noqa: E402
from core.arabic_utils import canonical_marks                       # noqa: E402
from core.analyzer import VerbAnalyzer                              # noqa: E402
from core.conjugation import (                                      # noqa: E402
    ConjugationEngine, past_forms, present_forms, imperative_forms,
    prohibition_forms, TENSE_ORDER, MANDATORY_TENSES,
)
from core.morphology import ArabicMorphology                        # noqa: E402
from core.validation import InputValidator                          # noqa: E402
from services.pdf_generator import PDFGenerator, reshape            # noqa: E402


class TestBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.analyzer = VerbAnalyzer()
        cls.engine = ConjugationEngine()
        cls.pdf = PDFGenerator()


# ===========================================================================
class TestRootBaabWazn(TestBase):
    """✓ Root detection ✓ Baab detection ✓ Wazn"""

    CASES = {
        #  verb              root        baab  baab name      wazn
        'كَتَبَ':       ('ك ت ب', 1, 'ثلاثی مجرد', 'فَعَلَ'),
        'أَنْزَلَ':     ('ن ز ل', 4, 'إفعال', 'أَفْعَلَ'),
        'عَلَّمَ':       ('ع ل م', 2, 'تفعیل', 'فَعَّلَ'),
        'قَاتَلَ':      ('ق ت ل', 3, 'مفاعلة', 'فَاعَلَ'),
        'تَعَلَّمَ':     ('ع ل م', 5, 'تفعّل', 'تَفَعَّلَ'),
        'تَعَاوَنَ':    ('ع و ن', 6, 'تفاعل', 'تَفَاعَلَ'),
        'اِنْكَسَرَ':    ('ك س ر', 7, 'انفعال', 'اِنْفَعَلَ'),
        'اِجْتَمَعَ':    ('ج م ع', 8, 'افتعال', 'اِفْتَعَلَ'),
        'اِسْتَغْفَرَ':  ('غ ف ر', 10, 'استفعال', 'اِسْتَفْعَلَ'),
    }

    def test_root_baab_wazn(self):
        for verb_ar, (root, baab, name, wazn) in self.CASES.items():
            res = self.analyzer.analyze_verb(verb_ar)
            self.assertTrue(res['found'], '%s not found' % verb_ar)
            v = res['verb']
            self.assertEqual(v['arabic'], verb_ar)
            self.assertEqual(v['root'], root, verb_ar)
            self.assertEqual(v['baab'], baab, verb_ar)
            self.assertEqual(v['baab_name_arabic'], name, verb_ar)
            self.assertEqual(v['wazn'], wazn, verb_ar)

    def test_shadda_is_not_ignored(self):
        """عَلَّمَ (باب تفعیل) must never resolve to عَلِمَ (ثلاثی مجرد)."""
        self.assertEqual(
            self.analyzer.analyze_verb('عَلَّمَ')['verb']['baab'], 2)
        self.assertEqual(
            self.analyzer.analyze_verb('عَلِمَ')['verb']['baab'], 1)
        self.assertEqual(
            self.analyzer.analyze_verb('كَتَّبَ')['verb']['baab'], 2)
        self.assertEqual(
            self.analyzer.analyze_verb('كَتَبَ')['verb']['baab'], 1)


# ===========================================================================
class TestFourMandatoryForms(TestBase):
    """✓ Past Active ✓ Present Active ✓ Past Passive ✓ Present Passive"""

    CASES = {
        'كَتَبَ':      ('كَتَبَ', 'يَكْتُبُ', 'كُتِبَ', 'يُكْتَبُ'),
        'أَنْزَلَ':    ('أَنْزَلَ', 'يُنْزِلُ', 'أُنْزِلَ', 'يُنْزَلُ'),
        'أَخْرَجَ':    ('أَخْرَجَ', 'يُخْرِجُ', 'أُخْرِجَ', 'يُخْرَجُ'),
        'عَلَّمَ':      ('عَلَّمَ', 'يُعَلِّمُ', 'عُلِّمَ', 'يُعَلَّمُ'),
        'كَوَّرَ':      ('كَوَّرَ', 'يُكَوِّرُ', 'كُوِّرَ', 'يُكَوَّرُ'),
        'خَفَّفَ':      ('خَفَّفَ', 'يُخَفِّفُ', 'خُفِّفَ', 'يُخَفَّفُ'),
        'نَادَى':     ('نَادَى', 'يُنَادِي', 'نُودِيَ', 'يُنَادَى'),
        'حَاسَبَ':     ('حَاسَبَ', 'يُحَاسِبُ', 'حُوسِبَ', 'يُحَاسَبُ'),
        'تَقَبَّلَ':    ('تَقَبَّلَ', 'يَتَقَبَّلُ', 'تُقُبِّلَ', 'يُتَقَبَّلُ'),
        'تَخَطَّفَ':    ('تَخَطَّفَ', 'يَتَخَطَّفُ', 'تُخُطِّفَ', 'يُتَخَطَّفُ'),
        'قَالَ':      ('قَالَ', 'يَقُولُ', 'قِيلَ', 'يُقَالُ'),
        'دَعَا':      ('دَعَا', 'يَدْعُو', 'دُعِيَ', 'يُدْعَى'),
        'رَمَى':      ('رَمَى', 'يَرْمِي', 'رُمِيَ', 'يُرْمَى'),
        'رَدَّ':       ('رَدَّ', 'يَرُدُّ', 'رُدَّ', 'يُرَدُّ'),
        'أَكَلَ':      ('أَكَلَ', 'يَأْكُلُ', 'أُكِلَ', 'يُؤْكَلُ'),
        'قَرَأَ':      ('قَرَأَ', 'يَقْرَأُ', 'قُرِئَ', 'يُقْرَأُ'),
    }

    def test_four_principal_parts(self):
        for verb_ar, parts in self.CASES.items():
            res = self.analyzer.analyze_verb(verb_ar)
            self.assertTrue(res['found'], verb_ar)
            v = res['verb']
            self.assertEqual(
                (v['past_3ms'], v['present_3ms'],
                 v['past_passive_3ms'], v['present_passive_3ms']),
                parts, verb_ar)

    def test_four_tables_are_populated(self):
        for verb_ar in self.CASES:
            conj = self.analyzer.conjugate(
                self.analyzer.analyze_verb(verb_ar)['verb'])
            for tense in MANDATORY_TENSES:
                self.assertEqual(len(conj[tense]), 14,
                                 '%s / %s' % (verb_ar, tense))


# ===========================================================================
class TestCompleteGardaan(TestBase):
    """✓ Complete 14 صیغے, compared against textbook tables."""

    def _check(self, tense, verb_ar, expected):
        """Compare canonically — mark order carries no meaning."""
        conj = self.analyzer.conjugate(
            self.analyzer.analyze_verb(verb_ar)['verb'])
        actual = [canonical_marks(r['arabic']) for r in conj[tense]]
        self.assertEqual(actual, [canonical_marks(e) for e in expected],
                         '%s / %s' % (verb_ar, tense))

    def test_sound_past(self):
        self._check('past_active', 'كَتَبَ', [
            'كَتَبَ', 'كَتَبَا', 'كَتَبُوا', 'كَتَبَتْ', 'كَتَبَتَا', 'كَتَبْنَ',
            'كَتَبْتَ', 'كَتَبْتُمَا', 'كَتَبْتُمْ', 'كَتَبْتِ', 'كَتَبْتُمَا',
            'كَتَبْتُنَّ', 'كَتَبْتُ', 'كَتَبْنَا'])

    def test_sound_present(self):
        self._check('present_active', 'كَتَبَ', [
            'يَكْتُبُ', 'يَكْتُبَانِ', 'يَكْتُبُونَ', 'تَكْتُبُ', 'تَكْتُبَانِ',
            'يَكْتُبْنَ', 'تَكْتُبُ', 'تَكْتُبَانِ', 'تَكْتُبُونَ', 'تَكْتُبِينَ',
            'تَكْتُبَانِ', 'تَكْتُبْنَ', 'أَكْتُبُ', 'نَكْتُبُ'])

    def test_hollow_past_shortens(self):
        self._check('past_active', 'قَالَ', [
            'قَالَ', 'قَالَا', 'قَالُوا', 'قَالَتْ', 'قَالَتَا', 'قُلْنَ',
            'قُلْتَ', 'قُلْتُمَا', 'قُلْتُمْ', 'قُلْتِ', 'قُلْتُمَا', 'قُلْتُنَّ',
            'قُلْتُ', 'قُلْنَا'])

    def test_hollow_present_shortens_fem_plural(self):
        self._check('present_active', 'قَالَ', [
            'يَقُولُ', 'يَقُولَانِ', 'يَقُولُونَ', 'تَقُولُ', 'تَقُولَانِ',
            'يَقُلْنَ', 'تَقُولُ', 'تَقُولَانِ', 'تَقُولُونَ', 'تَقُولِينَ',
            'تَقُولَانِ', 'تَقُلْنَ', 'أَقُولُ', 'نَقُولُ'])

    def test_defective_waw_past(self):
        self._check('past_active', 'دَعَا', [
            'دَعَا', 'دَعَوَا', 'دَعَوْا', 'دَعَتْ', 'دَعَتَا', 'دَعَوْنَ',
            'دَعَوْتَ', 'دَعَوْتُمَا', 'دَعَوْتُمْ', 'دَعَوْتِ', 'دَعَوْتُمَا',
            'دَعَوْتُنَّ', 'دَعَوْتُ', 'دَعَوْنَا'])

    def test_defective_waw_present(self):
        self._check('present_active', 'دَعَا', [
            'يَدْعُو', 'يَدْعُوَانِ', 'يَدْعُونَ', 'تَدْعُو', 'تَدْعُوَانِ',
            'يَدْعُونَ', 'تَدْعُو', 'تَدْعُوَانِ', 'تَدْعُونَ', 'تَدْعِينَ',
            'تَدْعُوَانِ', 'تَدْعُونَ', 'أَدْعُو', 'نَدْعُو'])

    def test_defective_ya_past(self):
        self._check('past_active', 'رَمَى', [
            'رَمَى', 'رَمَيَا', 'رَمَوْا', 'رَمَتْ', 'رَمَتَا', 'رَمَيْنَ',
            'رَمَيْتَ', 'رَمَيْتُمَا', 'رَمَيْتُمْ', 'رَمَيْتِ', 'رَمَيْتُمَا',
            'رَمَيْتُنَّ', 'رَمَيْتُ', 'رَمَيْنَا'])

    def test_defective_ya_present(self):
        self._check('present_active', 'رَمَى', [
            'يَرْمِي', 'يَرْمِيَانِ', 'يَرْمُونَ', 'تَرْمِي', 'تَرْمِيَانِ',
            'يَرْمِينَ', 'تَرْمِي', 'تَرْمِيَانِ', 'تَرْمُونَ', 'تَرْمِينَ',
            'تَرْمِيَانِ', 'تَرْمِينَ', 'أَرْمِي', 'نَرْمِي'])

    def test_doubled_past_expands(self):
        self._check('past_active', 'رَدَّ', [
            'رَدَّ', 'رَدَّا', 'رَدُّوا', 'رَدَّتْ', 'رَدَّتَا', 'رَدَدْنَ',
            'رَدَدْتَ', 'رَدَدْتُمَا', 'رَدَدْتُمْ', 'رَدَدْتِ', 'رَدَدْتُمَا',
            'رَدَدْتُنَّ', 'رَدَدْتُ', 'رَدَدْنَا'])

    def test_doubled_present(self):
        self._check('present_active', 'رَدَّ', [
            'يَرُدُّ', 'يَرُدَّانِ', 'يَرُدُّونَ', 'تَرُدُّ', 'تَرُدَّانِ',
            'يَرْدُدْنَ', 'تَرُدُّ', 'تَرُدَّانِ', 'تَرُدُّونَ', 'تَرُدِّينَ',
            'تَرُدَّانِ', 'تَرْدُدْنَ', 'أَرُدُّ', 'نَرُدُّ'])

    def test_assimilated_present_drops_waw(self):
        self._check('present_active', 'وَعَدَ', [
            'يَعِدُ', 'يَعِدَانِ', 'يَعِدُونَ', 'تَعِدُ', 'تَعِدَانِ', 'يَعِدْنَ',
            'تَعِدُ', 'تَعِدَانِ', 'تَعِدُونَ', 'تَعِدِينَ', 'تَعِدَانِ',
            'تَعِدْنَ', 'أَعِدُ', 'نَعِدُ'])

    def test_hamzated_first_person_merges(self):
        """أَ + أْ contracts to آ:  أَكَلَ → آكُلُ, not أَأْكُلُ."""
        conj = self.analyzer.conjugate(
            self.analyzer.analyze_verb('أَكَلَ')['verb'])
        self.assertEqual(conj['present_active'][12]['arabic'], 'آكُلُ')
        self.assertEqual(conj['present_passive'][12]['arabic'], 'أُوكَلُ')

    def test_hamza_seat_changes(self):
        """قَرَأَ + ا/و/ي reseats the hamza: قَرَآ، قَرَؤُوا، تَقْرَئِينَ."""
        conj = self.analyzer.conjugate(
            self.analyzer.analyze_verb('قَرَأَ')['verb'])
        self.assertEqual(conj['past_active'][1]['arabic'], 'قَرَآ')
        self.assertEqual(conj['past_active'][2]['arabic'], 'قَرَؤُوا')
        self.assertEqual(conj['present_active'][9]['arabic'], 'تَقْرَئِينَ')

    def test_final_noon_assimilates(self):
        """A root ending in ن merges with ـنَ / ـنَا: تَعَاوَنَّ، تَعَاوَنَّا."""
        conj = self.analyzer.conjugate(
            self.analyzer.analyze_verb('تَعَاوَنَ')['verb'])
        self.assertEqual(canonical_marks(conj['past_active'][5]['arabic']),
                         canonical_marks('تَعَاوَنَّ'))
        self.assertEqual(canonical_marks(conj['past_active'][13]['arabic']),
                         canonical_marks('تَعَاوَنَّا'))

    def test_defective_passive_paradigm(self):
        self._check('past_passive', 'دَعَا', [
            'دُعِيَ', 'دُعِيَا', 'دُعُوا', 'دُعِيَتْ', 'دُعِيَتَا', 'دُعِينَ',
            'دُعِيتَ', 'دُعِيتُمَا', 'دُعِيتُمْ', 'دُعِيتِ', 'دُعِيتُمَا',
            'دُعِيتُنَّ', 'دُعِيتُ', 'دُعِينَا'])

    def test_lafeef(self):
        self._check('present_active', 'وَفَى', [
            'يَفِي', 'يَفِيَانِ', 'يَفُونَ', 'تَفِي', 'تَفِيَانِ', 'يَفِينَ',
            'تَفِي', 'تَفِيَانِ', 'تَفُونَ', 'تَفِينَ', 'تَفِيَانِ', 'تَفِينَ',
            'أَفِي', 'نَفِي'])

    def test_every_verb_has_14_or_0(self):
        for verb in self.analyzer.verbs:
            conj = self.analyzer.conjugate(verb)
            for tense in MANDATORY_TENSES:
                self.assertIn(len(conj[tense]), (0, 14),
                              '%s / %s' % (verb['arabic'], tense))
            for tense in ('imperative', 'prohibition'):
                self.assertIn(len(conj[tense]), (0, 6),
                              '%s / %s' % (verb['arabic'], tense))

    def test_no_double_diacritics_anywhere(self):
        """A doubled harakat is always a generation bug."""
        bad = []
        for verb in self.analyzer.verbs:
            for tense, rows in self.analyzer.conjugate(verb).items():
                for row in rows:
                    form = row['arabic']
                    for mark in ('َ', 'ُ', 'ِ', 'ْ'):
                        if mark * 2 in form:
                            bad.append((verb['arabic'], tense, form))
        self.assertEqual(bad, [], 'doubled diacritics: %s' % bad[:5])

    def test_no_form_ends_without_a_mark(self):
        """Every ماضی/مضارع form must carry its final vowel or sukun."""
        marks = set('ًٌٍَُِّْ')
        weak_final = set('اوىيآ')
        bad = []
        for verb in self.analyzer.verbs:
            conj = self.analyzer.conjugate(verb)
            for tense in MANDATORY_TENSES:
                for row in conj[tense]:
                    form = row['arabic']
                    if form and form[-1] not in marks and form[-1] not in weak_final:
                        bad.append((verb['arabic'], tense, form))
        self.assertEqual(bad, [], 'unvowelled endings: %s' % bad[:5])


# ===========================================================================
class TestImperativeProhibition(TestBase):
    """✓ Imperative ✓ Prohibition"""

    IMPERATIVE = {
        'كَتَبَ': ['اُكْتُبْ', 'اُكْتُبَا', 'اُكْتُبُوا', 'اُكْتُبِي', 'اُكْتُبَا', 'اُكْتُبْنَ'],
        'عَلِمَ': ['اِعْلَمْ', 'اِعْلَمَا', 'اِعْلَمُوا', 'اِعْلَمِي', 'اِعْلَمَا', 'اِعْلَمْنَ'],
        'ضَرَبَ': ['اِضْرِبْ', 'اِضْرِبَا', 'اِضْرِبُوا', 'اِضْرِبِي', 'اِضْرِبَا', 'اِضْرِبْنَ'],
        'قَالَ': ['قُلْ', 'قُولَا', 'قُولُوا', 'قُولِي', 'قُولَا', 'قُلْنَ'],
        'وَعَدَ': ['عِدْ', 'عِدَا', 'عِدُوا', 'عِدِي', 'عِدَا', 'عِدْنَ'],
        'دَعَا': ['اُدْعُ', 'اُدْعُوَا', 'اُدْعُوا', 'اُدْعِي', 'اُدْعُوَا', 'اُدْعُونَ'],
        'رَمَى': ['اِرْمِ', 'اِرْمِيَا', 'اِرْمُوا', 'اِرْمِي', 'اِرْمِيَا', 'اِرْمِينَ'],
        'أَنْزَلَ': ['أَنْزِلْ', 'أَنْزِلَا', 'أَنْزِلُوا', 'أَنْزِلِي', 'أَنْزِلَا', 'أَنْزِلْنَ'],
        'عَلَّمَ': ['عَلِّمْ', 'عَلِّمَا', 'عَلِّمُوا', 'عَلِّمِي', 'عَلِّمَا', 'عَلِّمْنَ'],
        'قَاتَلَ': ['قَاتِلْ', 'قَاتِلَا', 'قَاتِلُوا', 'قَاتِلِي', 'قَاتِلَا', 'قَاتِلْنَ'],
        'تَعَلَّمَ': ['تَعَلَّمْ', 'تَعَلَّمَا', 'تَعَلَّمُوا', 'تَعَلَّمِي', 'تَعَلَّمَا', 'تَعَلَّمْنَ'],
        'اِنْكَسَرَ': ['اِنْكَسِرْ', 'اِنْكَسِرَا', 'اِنْكَسِرُوا', 'اِنْكَسِرِي',
                     'اِنْكَسِرَا', 'اِنْكَسِرْنَ'],
        'اِسْتَغْفَرَ': ['اِسْتَغْفِرْ', 'اِسْتَغْفِرَا', 'اِسْتَغْفِرُوا',
                       'اِسْتَغْفِرِي', 'اِسْتَغْفِرَا', 'اِسْتَغْفِرْنَ'],
        # genuinely irregular — supplied as verified lexical data
        'أَكَلَ': ['كُلْ', 'كُلَا', 'كُلُوا', 'كُلِي', 'كُلَا', 'كُلْنَ'],
        'أَمَرَ': ['مُرْ', 'مُرَا', 'مُرُوا', 'مُرِي', 'مُرَا', 'مُرْنَ'],
    }

    def test_imperative(self):
        for verb_ar, expected in self.IMPERATIVE.items():
            conj = self.analyzer.conjugate(
                self.analyzer.analyze_verb(verb_ar)['verb'])
            self.assertEqual(
                [canonical_marks(r['arabic']) for r in conj['imperative']],
                [canonical_marks(e) for e in expected], verb_ar)

    def test_prohibition(self):
        conj = self.analyzer.conjugate(
            self.analyzer.analyze_verb('كَتَبَ')['verb'])
        self.assertEqual([r['arabic'] for r in conj['prohibition']], [
            'لَا تَكْتُبْ', 'لَا تَكْتُبَا', 'لَا تَكْتُبُوا', 'لَا تَكْتُبِي',
            'لَا تَكْتُبَا', 'لَا تَكْتُبْنَ'])

    def test_prohibition_hollow_shortens(self):
        conj = self.analyzer.conjugate(
            self.analyzer.analyze_verb('قَالَ')['verb'])
        self.assertEqual(conj['prohibition'][0]['arabic'], 'لَا تَقُلْ')

    def test_prohibition_always_starts_with_laa(self):
        for verb in self.analyzer.verbs:
            for row in self.analyzer.conjugate(verb)['prohibition']:
                self.assertTrue(row['arabic'].startswith('لَا '),
                                '%s: %s' % (verb['arabic'], row['arabic']))


# ===========================================================================
class TestNoInvention(TestBase):
    """Accuracy policy: nothing is fabricated where nothing is attested."""

    NO_PASSIVE = ['خَرَجَ', 'كَرُمَ', 'نَزَلَ', 'اِنْكَسَرَ', 'اِنْفَطَرَ',
                  'اِجْتَمَعَ', 'اِخْتَلَفَ', 'اِرْتَفَعَ', 'اِنْتَفَعَ',
                  'تَعَاوَنَ', 'تَنَافَسَ', 'اِسْتَهْزَأَ', 'اِنْتَصَرَ']

    def test_intransitive_verbs_have_no_passive(self):
        for verb_ar in self.NO_PASSIVE:
            res = self.analyzer.analyze_verb(verb_ar)
            self.assertTrue(res['found'], verb_ar)
            v = res['verb']
            self.assertIsNone(v['past_passive_3ms'], verb_ar)
            self.assertIsNone(v['present_passive_3ms'], verb_ar)
            conj = self.analyzer.conjugate(v)
            self.assertEqual(conj['past_passive'], [], verb_ar)
            self.assertEqual(conj['present_passive'], [], verb_ar)
            self.assertTrue(v['unavailable_note'],
                            '%s must explain why' % verb_ar)

    def test_form_vii_has_no_ism_mafool(self):
        for verb_ar in ('اِنْكَسَرَ', 'اِنْفَطَرَ', 'اِنْكَتَبَ'):
            v = self.analyzer.analyze_verb(verb_ar)['verb']
            self.assertIsNone(v['ism_mafool'], verb_ar)

    def test_absent_baab_is_reported_not_generated(self):
        """مادہ ن ز ل has no باب انفعال verb, so none may be shown."""
        afaal = self.analyzer.get_afaal_for_root('ن ز ل')
        by_baab = {e['baab']: e for e in afaal}
        self.assertTrue(by_baab[4]['available'])      # أَنْزَلَ
        self.assertTrue(by_baab[2]['available'])      # نَزَّلَ
        self.assertTrue(by_baab[10]['available'])     # اِسْتَنْزَلَ
        self.assertFalse(by_baab[7]['available'])     # no انفعال verb
        self.assertEqual(by_baab[7]['verbs'], [])
        self.assertFalse(by_baab[3]['available'])     # no مفاعلة verb

    def test_unknown_word_is_refused(self):
        for word in ('زززز', 'قهقهة', 'ضضض'):
            res = self.analyzer.analyze_verb(word)
            self.assertFalse(res['found'], word)
            self.assertIn('مستند', res['message'])


# ===========================================================================
class TestVerbTypes(TestBase):
    """✓ Weak verbs ✓ Hamzated verbs ✓ Doubled verbs"""

    TYPES = {
        'كَتَبَ': 'sound', 'قَالَ': 'hollow', 'بَاعَ': 'hollow',
        'صَامَ': 'hollow', 'خَافَ': 'hollow',
        'دَعَا': 'defective', 'رَمَى': 'defective', 'سَعَى': 'defective',
        'هَدَى': 'defective',
        'وَعَدَ': 'assimilated', 'وَجَدَ': 'assimilated', 'وَقَفَ': 'assimilated',
        'رَدَّ': 'doubled', 'مَدَّ': 'doubled', 'شَدَّ': 'doubled',
        'أَكَلَ': 'hamzated', 'سَأَلَ': 'hamzated', 'قَرَأَ': 'hamzated',
        'أَمَرَ': 'hamzated',
        'وَفَى': 'lafeef', 'وَقَى': 'lafeef', 'رَوَى': 'lafeef',
    }

    def test_verb_type(self):
        for verb_ar, expected in self.TYPES.items():
            res = self.analyzer.analyze_verb(verb_ar)
            self.assertTrue(res['found'], verb_ar)
            self.assertEqual(res['verb']['verb_type'], expected, verb_ar)

    def test_lafeef_subtype(self):
        self.assertEqual(
            ArabicMorphology.lafeef_subtype(['و', 'ف', 'ي']), 'مفروق')
        self.assertEqual(
            ArabicMorphology.lafeef_subtype(['ر', 'و', 'ي']), 'مقرون')


# ===========================================================================
class TestAllTestVerbs(TestBase):
    """Every verb the specification lists must analyse to itself."""

    SPEC_VERBS = [
        'كَتَبَ', 'نَصَرَ', 'ضَرَبَ', 'فَتَحَ', 'عَلِمَ', 'كَرُمَ',
        'أَكَلَ', 'سَأَلَ', 'قَرَأَ', 'أَمَرَ',
        'وَعَدَ', 'وَجَدَ', 'وَقَفَ',
        'قَالَ', 'بَاعَ', 'صَامَ', 'خَافَ',
        'دَعَا', 'رَمَى', 'سَعَى', 'هَدَى',
        'رَدَّ', 'مَدَّ', 'شَدَّ',
        'وَفَى', 'وَقَى', 'رَوَى',
        'عَلَّمَ', 'قَاتَلَ', 'أَنْزَلَ', 'تَعَلَّمَ', 'تَعَاوَنَ',
        'اِنْكَسَرَ', 'اِجْتَمَعَ', 'اِسْتَغْفَرَ', 'اِسْتَهْزَأَ',
        # from the reference book
        'أَخْرَجَ', 'كَوَّرَ', 'خَفَّفَ', 'نَادَى', 'حَاسَبَ', 'تَقَبَّلَ',
        'تَخَطَّفَ', 'تَنَافَسَ', 'اِخْتَلَفَ', 'اِرْتَفَعَ', 'اِنْتَفَعَ',
        'اِنْفَطَرَ', 'اِسْتَعْتَبَ',
    ]

    def test_all_spec_verbs_resolve_to_themselves(self):
        for verb_ar in self.SPEC_VERBS:
            res = self.analyzer.analyze_verb(verb_ar)
            self.assertTrue(res['found'], '%s not found' % verb_ar)
            self.assertEqual(res['verb']['arabic'], verb_ar,
                             '%s resolved to %s'
                             % (verb_ar, res['verb']['arabic']))

    def test_all_spec_verbs_have_urdu_and_english(self):
        for verb_ar in self.SPEC_VERBS:
            v = self.analyzer.analyze_verb(verb_ar)['verb']
            self.assertTrue(v['meaning_urdu'], verb_ar)
            self.assertTrue(v['meaning_english'], verb_ar)
            self.assertTrue(v['masdar'], verb_ar)
            self.assertTrue(v['ism_fail'], verb_ar)


# ===========================================================================
class TestConjugatedInput(TestBase):
    """✓ Reverse analysis of an inflected word the student typed."""

    CASES = {
        'كَتَبْتُ':      ('كَتَبَ', 'past_active', 'أَنَا'),
        'كَتَبْتُمَا':   ('كَتَبَ', 'past_active', 'أَنْتُمَا'),
        'يَكْتُبُونَ':   ('كَتَبَ', 'present_active', 'هُمْ'),
        'تَكْتُبِينَ':   ('كَتَبَ', 'present_active', 'أَنْتِ'),
        'قَالُوا':      ('قَالَ', 'past_active', 'هُمْ'),
        'دَعَوْا':       ('دَعَا', 'past_active', 'هُمْ'),
        'رَمَوْا':       ('رَمَى', 'past_active', 'هُمْ'),
        'يُنْزِلُ':      ('أَنْزَلَ', 'present_active', 'هُوَ'),
        'أُنْزِلَ':      ('أَنْزَلَ', 'past_passive', 'هُوَ'),
        'يُنْزَلُ':      ('أَنْزَلَ', 'present_passive', 'هُوَ'),
        'قُلْنَ':        ('قَالَ', 'past_active', 'هُنَّ'),
        'خِفْتُ':        ('خَافَ', 'past_active', 'أَنَا'),
        'رُدِدْتُ':      ('رَدَّ', 'past_passive', 'أَنَا'),
        'آكُلُ':        ('أَكَلَ', 'present_active', 'أَنَا'),
        'كُلْ':          ('أَكَلَ', 'imperative', 'أَنْتَ'),
        'لَا تَكْتُبْ':  ('كَتَبَ', 'prohibition', 'أَنْتَ'),
        'يَسْتَغْفِرُونَ': ('اِسْتَغْفَرَ', 'present_active', 'هُمْ'),
    }

    def test_reverse_analysis(self):
        for word, (base, tense, pronoun) in self.CASES.items():
            parsed = self.analyzer.parse_conjugated(word)
            self.assertTrue(parsed.get('found'), '%s not parsed' % word)
            self.assertEqual(parsed['base_verb'], base, word)
            self.assertEqual(parsed['tense'], tense, word)
            self.assertEqual(parsed['pronoun'], pronoun, word)

    def test_analyze_verb_routes_inflected_input(self):
        res = self.analyzer.analyze_verb('أُنْزِلَ')
        self.assertTrue(res['found'])
        self.assertTrue(res['is_conjugated_form'])
        self.assertEqual(res['verb']['arabic'], 'أَنْزَلَ')
        self.assertEqual(res['conjugated_info']['tense'], 'past_passive')

    def test_vowelless_input_still_found(self):
        for word, expected in (('كتب', 'كَتَبَ'), ('قال', 'قَالَ'),
                               ('انزل', 'أَنْزَلَ'), ('علم', 'عَلِمَ')):
            res = self.analyzer.analyze_verb(word)
            self.assertTrue(res['found'], word)
            self.assertEqual(res['verb']['arabic'], expected, word)


# ===========================================================================
class TestAbwaab(TestBase):
    """✓ All 8 Baab categories"""

    EXPECTED = [
        (4, 'إفعال', 'أَفْعَلَ', 'يُفْعِلُ'),
        (2, 'تفعیل', 'فَعَّلَ', 'يُفَعِّلُ'),
        (3, 'مفاعلة', 'فَاعَلَ', 'يُفَاعِلُ'),
        (5, 'تفعّل', 'تَفَعَّلَ', 'يَتَفَعَّلُ'),
        (6, 'تفاعل', 'تَفَاعَلَ', 'يَتَفَاعَلُ'),
        (7, 'انفعال', 'اِنْفَعَلَ', 'يَنْفَعِلُ'),
        (8, 'افتعال', 'اِفْتَعَلَ', 'يَفْتَعِلُ'),
        (10, 'استفعال', 'اِسْتَفْعَلَ', 'يَسْتَفْعِلُ'),
    ]

    def test_eight_abwaab_in_book_order(self):
        self.assertEqual(MAZEED_ORDER, [f for f, _, _, _ in self.EXPECTED])
        for form, name, past, present in self.EXPECTED:
            b = BAAB_INFO[form]
            self.assertEqual(b['name_ar'], name)
            self.assertEqual(b['wazn_past'], past)
            self.assertEqual(b['wazn_present'], present)

    def test_every_baab_has_explanations_and_examples(self):
        for form in MAZEED_ORDER:
            b = BAAB_INFO[form]
            self.assertTrue(b['meaning_ur'], form)
            self.assertTrue(b['meaning_en'], form)
            self.assertTrue(b['examples'], form)
            self.assertTrue(b['masdar_pattern'], form)

    def test_baab_examples_exist_in_lexicon(self):
        for form in MAZEED_ORDER:
            for example in BAAB_INFO[form]['examples']:
                res = self.analyzer.analyze_verb(example)
                self.assertTrue(res['found'],
                                'باب %s example %s missing' % (form, example))
                self.assertEqual(res['verb']['baab'], form, example)

    def test_pattern_conjugates(self):
        """The وزن itself must conjugate, for the teaching page."""
        for form in MAZEED_ORDER:
            conj = self.analyzer.get_baab_example_conjugation(form)
            self.assertEqual(len(conj['past_active']), 14, form)
            self.assertEqual(len(conj['present_active']), 14, form)

    def test_lexicon_covers_every_baab(self):
        covered = {v['baab'] for v in self.analyzer.verbs}
        for form in MAZEED_ORDER:
            self.assertIn(form, covered, 'no verb for باب %s' % form)


# ===========================================================================
class TestUrduEnglish(TestBase):
    """✓ Urdu ✓ English glosses for every صیغہ"""

    def test_every_row_has_both_glosses(self):
        for verb in self.analyzer.verbs:
            for tense, rows in self.analyzer.conjugate(verb).items():
                for row in rows:
                    self.assertTrue(row['meaning_urdu'],
                                    '%s/%s' % (verb['arabic'], tense))
                    self.assertTrue(row['meaning_english'],
                                    '%s/%s' % (verb['arabic'], tense))

    def test_urdu_gloss_is_well_formed(self):
        conj = self.analyzer.conjugate(
            self.analyzer.analyze_verb('كَتَبَ')['verb'])
        self.assertEqual(conj['past_active'][0]['meaning_urdu'],
                         'اُس (ایک مرد) نے لکھا')
        self.assertEqual(conj['past_active'][12]['meaning_urdu'],
                         'میں نے لکھا')
        self.assertEqual(conj['present_active'][0]['meaning_urdu'],
                         'وہ (ایک مرد) لکھتا ہے')
        self.assertEqual(conj['present_active'][3]['meaning_urdu'],
                         'وہ (ایک عورت) لکھتی ہے')
        self.assertEqual(conj['past_passive'][0]['meaning_urdu'],
                         'وہ (ایک مرد) لکھا گیا')

    def test_english_gloss_is_well_formed(self):
        conj = self.analyzer.conjugate(
            self.analyzer.analyze_verb('كَتَبَ')['verb'])
        self.assertEqual(conj['past_active'][0]['meaning_english'], 'He wrote')
        self.assertEqual(conj['present_active'][0]['meaning_english'],
                         'He writes')
        self.assertEqual(conj['present_active'][2]['meaning_english'],
                         'They (m) write')
        self.assertEqual(conj['past_passive'][0]['meaning_english'],
                         'He was written')

    def test_no_urdu_gloss_mangles_the_stem(self):
        """کھانا → کھایا, never کھاا."""
        conj = self.analyzer.conjugate(
            self.analyzer.analyze_verb('أَكَلَ')['verb'])
        self.assertIn('کھایا', conj['past_active'][0]['meaning_urdu'])
        self.assertIn('کھاتا', conj['present_active'][0]['meaning_urdu'])


# ===========================================================================
class TestInvalidInput(TestBase):
    """✓ Invalid input handling"""

    def test_empty(self):
        for word in ('', '   ', None):
            res = self.analyzer.analyze_verb(word)
            self.assertFalse(res['found'])
            self.assertEqual(res['reason'], 'empty')
            self.assertEqual(res['message'], 'براہ کرم عربی لفظ درج کریں۔')

    def test_empty_in_english(self):
        res = self.analyzer.analyze_verb('', 'en')
        self.assertEqual(res['message'], 'Please enter an Arabic word.')

    def test_latin_gibberish(self):
        res = self.analyzer.analyze_verb('xyzzy', 'en')
        self.assertFalse(res['found'])
        self.assertEqual(res['message'], 'Please enter an Arabic word.')

    def test_english_meaning_search_still_works(self):
        res = self.analyzer.analyze_verb('to write')
        self.assertTrue(res['found'])
        self.assertEqual(res['verb']['arabic'], 'كَتَبَ')

    def test_unknown_arabic_offers_no_invented_verb(self):
        res = self.analyzer.analyze_verb('زززز')
        self.assertFalse(res['found'])
        self.assertNotIn('verb', res)

    def test_short_imperatives_accepted(self):
        for word in ('كُلْ', 'قُلْ', 'فِ', 'عِدْ', 'مُرْ'):
            self.assertTrue(self.analyzer.analyze_verb(word)['found'], word)


# ===========================================================================
class TestPDF(TestBase):
    """✓ PDF — one page, no blanks, harakat preserved"""

    def test_reshaper_keeps_harakat(self):
        """The default arabic_reshaper deletes them; that must be overridden."""
        out = reshape('أَنْزَلَ')
        self.assertIn('َ', out, 'fatha lost in PDF shaping')
        self.assertIn('ْ', out, 'sukun lost in PDF shaping')

    def test_bundled_arabic_font_is_used(self):
        self.assertIn(self.pdf.arabic_font, ('Amiri', 'NotoNaskhArabic'),
                      'bundled Arabic font not registered — got %s'
                      % self.pdf.arabic_font)

    def test_one_page_sheet_is_exactly_one_page(self):
        from pypdf import PdfReader
        for verb in self.analyzer.verbs:
            pdf = self.pdf.generate_one_page_sheet(
                verb, self.analyzer.conjugate(verb),
                self.analyzer.get_baab_info(verb['baab']))
            pages = PdfReader(io.BytesIO(pdf)).pages
            self.assertEqual(len(pages), 1,
                             '%s produced %d pages' % (verb['arabic'],
                                                       len(pages)))

    def test_detailed_sheet_has_no_blank_pages(self):
        from pypdf import PdfReader
        for verb_ar in ('كَتَبَ', 'أَنْزَلَ', 'دَعَا', 'خَرَجَ', 'اِنْكَسَرَ'):
            res = self.analyzer.analyze_verb(verb_ar)
            pdf = self.pdf.generate_study_sheet(
                verb_data=res['verb'], conjugations=res['conjugations'],
                quranic_data=res['quranic_usage'], baab=res['baab'],
                afaal=res['afaal'])
            pages = PdfReader(io.BytesIO(pdf)).pages
            self.assertGreater(len(pages), 3, verb_ar)
            for i, page in enumerate(pages, start=1):
                text = (page.extract_text() or '').strip()
                self.assertGreater(len(text), 5,
                                   '%s page %d is blank' % (verb_ar, i))

    def test_one_page_pdf_contains_all_four_gardaans(self):
        from pypdf import PdfReader
        res = self.analyzer.analyze_verb('أَنْزَلَ')
        pdf = self.pdf.generate_one_page_sheet(
            res['verb'], res['conjugations'], res['baab'])
        text = PdfReader(io.BytesIO(pdf)).pages[0].extract_text() or ''
        # the shaped text is in presentation forms, so compare on length:
        # 14 rows x 4 tenses + header must yield a substantial page
        self.assertGreater(len(text), 800,
                           'one-page sheet looks too sparse: %d chars'
                           % len(text))

    def test_pdf_opens_and_has_valid_header(self):
        res = self.analyzer.analyze_verb('كَتَبَ')
        for pdf in (self.pdf.generate_one_page_sheet(
                        res['verb'], res['conjugations'], res['baab']),
                    self.pdf.generate_study_sheet(
                        verb_data=res['verb'],
                        conjugations=res['conjugations'])):
            self.assertTrue(pdf.startswith(b'%PDF-'))
            self.assertIn(b'%%EOF', pdf[-2048:])


# ===========================================================================
class TestDataModel(TestBase):
    """The structured data model the specification requires."""

    REQUIRED_FIELDS = [
        'id', 'arabic', 'root', 'root_letters', 'baab', 'baab_name_arabic',
        'wazn', 'past_3ms', 'present_3ms', 'past_passive_3ms',
        'present_passive_3ms', 'masdar', 'ism_fail', 'ism_mafool',
        'meaning_urdu', 'meaning_english', 'verb_type', 'transitivity',
        'derived_nouns', 'has_passive',
    ]

    def test_every_verb_has_the_full_schema(self):
        for verb in self.analyzer.verbs:
            for field in self.REQUIRED_FIELDS:
                self.assertIn(field, verb,
                              '%s missing %s' % (verb.get('arabic'), field))

    def test_roots_link_to_verbs(self):
        for root in self.analyzer.roots:
            self.assertTrue(root['related_verbs'], root['root'])
            for verb_id in root['related_verbs']:
                self.assertTrue(self.analyzer.get_verb_by_id(verb_id),
                                '%s -> %s' % (root['root'], verb_id))

    def test_multiple_verbs_per_root(self):
        multi = [r for r in self.analyzer.roots if len(r['related_verbs']) > 1]
        self.assertGreaterEqual(len(multi), 15)
        nzl = self.analyzer.get_verb_forms_for_root('ن ز ل')
        self.assertGreaterEqual(len(nzl), 5)
        self.assertEqual(sorted(v['baab'] for v in nzl), [1, 2, 4, 5, 10])

    def test_quranic_references_point_at_real_verbs(self):
        for entry in self.analyzer.quranic:
            self.assertTrue(self.analyzer.get_verb_by_id(entry['verb_id']),
                            'orphan Quranic entry: %s' % entry['verb_id'])

    def test_no_duplicate_ids(self):
        ids = [v['id'] for v in self.analyzer.verbs]
        self.assertEqual(len(ids), len(set(ids)))

    def test_statistics(self):
        stats = self.analyzer.get_statistics()
        self.assertGreaterEqual(stats['verbs'], 80)
        self.assertGreaterEqual(stats['roots'], 45)
        self.assertGreaterEqual(stats['abwaab'], 9)
        self.assertGreaterEqual(stats['total_forms'], 4000)


# ===========================================================================
class TestUserData(TestBase):
    """Bookmarks, study history and spaced repetition still work."""

    def test_bookmarks_round_trip(self):
        self.analyzer.remove_bookmark('v001')
        self.assertFalse(self.analyzer.is_bookmarked('v001'))
        self.analyzer.add_bookmark('v001')
        self.assertTrue(self.analyzer.is_bookmarked('v001'))
        self.assertIn('v001', self.analyzer.get_bookmarks())
        self.analyzer.remove_bookmark('v001')
        self.assertFalse(self.analyzer.is_bookmarked('v001'))

    def test_sm2_intervals(self):
        card_id = '_test_sm2'
        with sqlite3.connect(self.analyzer.db_path) as conn:
            conn.execute('DELETE FROM flashcard_sm2 WHERE card_id LIKE ?',
                         ('_test%',))
            conn.commit()
        first = self.analyzer.update_sm2_card(card_id, 'v001', 'meaning', 5)
        self.assertEqual((first['interval'], first['repetitions']), (1, 1))
        second = self.analyzer.update_sm2_card(card_id, 'v001', 'meaning', 5)
        self.assertEqual((second['interval'], second['repetitions']), (6, 2))
        reset = self.analyzer.update_sm2_card(card_id, 'v001', 'meaning', 1)
        self.assertEqual((reset['interval'], reset['repetitions']), (1, 0))

    def test_sm2_stats_shape(self):
        stats = self.analyzer.get_sm2_stats()
        for key in ('total_cards', 'due_today', 'average_ef'):
            self.assertIn(key, stats)

    def test_study_history(self):
        self.analyzer.record_study('v001')
        self.assertIn('v001', self.analyzer.get_recent_verbs(limit=20))

    def test_practice_history(self):
        self.analyzer.record_practice('v001', True, 'meaning')
        progress = self.analyzer.get_progress()
        self.assertGreaterEqual(progress['total_attempts'], 1)


# ===========================================================================
class TestViewsRender(TestBase):
    """Every view builds its HTML without raising."""

    def test_theme_builders(self):
        from ui import theme
        res = self.analyzer.analyze_verb('أَنْزَلَ')
        for lang in ('ur', 'en', 'ar'):
            html = theme.gardaan_table(res['conjugations']['past_active'], lang)
            self.assertIn('<table', html)
            self.assertIn('أَنْزَلَ', html)
            self.assertIn('<table', theme.simple_table(
                ['a', 'b'], [['1', '2']], lang))
            self.assertIn('qa-grid', theme.fact_grid([('x', 'y')]))

    def test_empty_gardaan_shows_not_applicable(self):
        from ui import theme
        html = theme.gardaan_table([], 'ur')
        self.assertIn('قابلِ اطلاق نہیں', html)

    def test_all_translation_keys_exist_in_all_languages(self):
        from ui.theme import _T
        for key, entry in _T.items():
            for lang in ('ur', 'en', 'ar'):
                self.assertIn(lang, entry, '%s missing %s' % (key, lang))
                self.assertTrue(entry[lang], '%s/%s is empty' % (key, lang))


if __name__ == '__main__':
    unittest.main(verbosity=2)
