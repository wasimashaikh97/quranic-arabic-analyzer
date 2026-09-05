# -*- coding: utf-8 -*-
"""Tests for the complete Quranic verb index, suggestions and Islam360 status.

These cover the three headline requirements: search across the whole Quranic
verb inventory rather than a small dictionary, useful suggestions for a
misspelling, and honest reporting of Islam360 verification.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.analyzer import VerbAnalyzer                          # noqa: E402
from core.arabic_utils import canonical_marks                   # noqa: E402
from core.quran_index import key_bare                           # noqa: E402


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.analyzer = VerbAnalyzer()
        cls.index = cls.analyzer.quran_index


# ===========================================================================
class TestIndexCoverage(Base):
    """Not a small dictionary — the whole Quranic verb inventory."""

    def test_index_is_substantial(self):
        stats = self.index.stats()
        self.assertGreaterEqual(stats['lemmas'], 1400)
        self.assertGreaterEqual(stats['roots'], 900)
        self.assertGreaterEqual(stats['tokens'], 19000)
        self.assertGreaterEqual(stats['surfaces'], 5000)

    def test_verbs_outside_the_curated_lexicon_are_found(self):
        """Each of these was 'not found' before the index existed."""
        for word in ('خَتَمَ', 'يَعْمَهُونَ', 'سَبَّحَ', 'ٱهْدِنَا'):
            res = self.analyzer.analyze_verb(word)
            self.assertTrue(res.get('found'), '%s not found' % word)

    def test_root_and_baab_come_from_the_corpus(self):
        for word, root, baab in (('خَتَمَ', 'خ ت م', 1),
                                 ('سَبَّحَ', 'س ب ح', 2)):
            verb = self.analyzer.analyze_verb(word)['verb']
            self.assertEqual(verb['root'], root, word)
            self.assertEqual(verb['baab'], baab, word)

    def test_every_required_baab_is_represented(self):
        baabs = {v['baab'] for v in self.index.verbs if v.get('baab')}
        for required in (1, 2, 3, 4, 5, 6, 7, 8, 10):
            self.assertIn(required, baabs, 'باب %s missing' % required)

    def test_curated_lexicon_still_wins(self):
        """A curated verb keeps its fuller Sarf data."""
        res = self.analyzer.analyze_verb('أَنْزَلَ')
        self.assertNotEqual(res.get('source'), 'quran_index')
        self.assertEqual(res['verb']['masdar'], 'إِنْزَال')

    def test_index_verb_renders_as_a_normal_record(self):
        res = self.analyzer.analyze_verb('خَتَمَ')
        verb = res['verb']
        for field in ('arabic', 'root', 'baab', 'baab_name_arabic', 'wazn',
                      'past_3ms', 'derived_nouns', 'verb_type'):
            self.assertIn(field, verb)
        self.assertEqual(res['source'], 'quran_index')


# ===========================================================================
class TestSearchNormalisation(Base):
    """Arabic input in every spelling a student might use."""

    def test_inflected_quranic_forms_resolve(self):
        for word in ('قَالُوا', 'يَكْتُبُونَ', 'يَسْتَغْفِرُونَ', 'أَنزَلْنَٰهُ'):
            self.assertTrue(self.index.lookup(word), word)

    def test_harakat_optional(self):
        for bare, voweled in (('انزل', 'أَنزَلَ'), ('قال', 'قَالَ'),
                              ('استغفر', 'ٱسْتَغْفَرَ')):
            self.assertTrue(self.index.lookup(bare), bare)
            self.assertTrue(self.index.lookup(voweled), voweled)

    def test_alef_wasla_folds(self):
        """ٱهْدِنَا as the Quran writes it, اهدنا as a student types it."""
        a = self.index.lookup('ٱهْدِنَا')
        b = self.index.lookup('اهدنا')
        self.assertTrue(a and b)
        self.assertEqual(a[0]['entry']['root'], b[0]['entry']['root'])

    def test_quranic_recitation_marks_ignored(self):
        """The text writes قَالُوا۟; the student types قالوا."""
        self.assertTrue(self.index.lookup('قالوا'))

    def test_shadda_distinguishes_baab(self):
        """عَلَّمَ (تفعیل) must not collapse into عَلِمَ (مجرد)."""
        hits = self.index.lookup('عَلَّمَ')
        self.assertTrue(hits)
        self.assertEqual(hits[0]['entry']['baab'], 2)

    def test_no_duplicate_candidates(self):
        for word in ('نزل', 'قال', 'علم'):
            hits = self.index.lookup(word)
            ids = [(h['entry']['root'], h['entry']['baab']) for h in hits]
            self.assertEqual(len(ids), len(set(ids)), word)

    def test_root_query_works(self):
        self.assertTrue(self.index.lookup('كور'), 'root query failed')


# ===========================================================================
class TestNoInvention(Base):
    """A theoretical form, a lexical verb and a Quranic occurrence differ."""

    def test_principal_parts_are_attested_only(self):
        checked = 0
        for entry in self.index.verbs[:300]:
            forms = set(entry.get('segments', {}))
            for part in (entry.get('principal') or {}).values():
                self.assertIn(part, forms,
                              '%s: %s is not an attested form'
                              % (entry['headword'], part))
                checked += 1
        self.assertGreater(checked, 50)

    def test_unattested_forms_stay_empty(self):
        for entry in self.index.verbs[:400]:
            record = self.analyzer.quranic_to_record(entry)
            principal = entry.get('principal') or {}
            if 'past_active' not in principal:
                self.assertIsNone(record['past_3ms'], entry['headword'])
            if 'past_passive' not in principal:
                self.assertIsNone(record['past_passive_3ms'],
                                  entry['headword'])

    def test_cited_word_occurs_in_its_ayah(self):
        for entry in self.index.verbs[:200]:
            for occ in entry.get('occurrences', []):
                if occ.get('text'):
                    self.assertIn(occ['seg'].strip(), occ['text'],
                                  '%s not in %d:%d'
                                  % (occ['seg'], occ['s'], occ['a']))

    def test_surah_and_ayah_numbers_sane(self):
        for entry in self.index.verbs[:200]:
            for occ in entry.get('occurrences', []):
                self.assertTrue(1 <= occ['s'] <= 114)
                self.assertGreaterEqual(occ['a'], 1)


# ===========================================================================
class TestDidYouMean(Base):
    """A misspelling must lead somewhere, and somewhere relevant."""

    def test_suggestions_for_misspellings(self):
        for typo, expected in (('هدددى', 'هَدَى'), ('سبببح', 'سَبَّحَ'),
                               ('نصررر', 'نَصَرَ')):
            # compare canonically: the corpus writes shadda before the
            # vowel, a dictionary often the other way round
            names = [canonical_marks(e['headword'])
                     for e in self.analyzer.suggest(typo, 6)]
            self.assertIn(canonical_marks(expected), names,
                          '%s -> %s' % (typo, names))

    def test_suggestions_are_relevant_not_random(self):
        for typo in ('هدددى', 'كتببب', 'نصررر'):
            target = key_bare(typo)
            for entry in self.analyzer.suggest(typo, 5):
                shared = len(set(target) & set(key_bare(entry['headword'])))
                self.assertGreaterEqual(
                    shared, 2,
                    '%s -> %s looks unrelated' % (typo, entry['headword']))

    def test_random_input_suggests_nothing(self):
        for junk in ('زززز', 'قققق'):
            res = self.analyzer.analyze_verb(junk)
            self.assertFalse(res.get('found'))
            self.assertFalse(res.get('did_you_mean'))

    def test_search_never_crashes(self):
        for value in ('', '   ', 'hello', '12345', '!@#$%', 'ا', 'اب',
                      'زززززززز', 'كَتَبَ', 'قالوا', '،؟!', None):
            try:
                self.analyzer.analyze_verb(value)
            except Exception as exc:                # pragma: no cover
                self.fail('crashed on %r: %s' % (value, exc))


# ===========================================================================
class TestIslam360Status(Base):
    """Islam360 status must reflect reality — connected or not, never faked.

    Whether it is connected depends on the machine: the index is built from the
    locally installed Islam360 app and is git-ignored because the data is
    copyrighted.  So these assert the *consistency* of whichever state holds,
    which is the property that actually matters.
    """

    def setUp(self):
        from services import quran_source
        self.qs = quran_source
        self.status = quran_source.verification_status('ur')

    def test_status_matches_whether_the_index_exists(self):
        from pathlib import Path
        from services.quran_source import INDEX_PATH
        self.assertEqual(self.status['islam360_verified'],
                         Path(INDEX_PATH).exists())

    def test_message_matches_the_state(self):
        if self.status['islam360_verified']:
            self.assertIn('اسلام', self.status['ok_message'])
            self.assertEqual(self.status['active_source'], 'Islam360')
        else:
            self.assertIn('اسلام', self.status['blocked_message'])
            self.assertNotIn('Islam360', self.status['active_source'])

    def test_provider_refuses_to_invent_when_unconfigured(self):
        from services.quran_source import (Islam360Provider,
                                           Islam360NotConfigured)
        provider = Islam360Provider(index_path='/nonexistent/islam360.json')
        self.assertFalse(provider.configured)
        with self.assertRaises(Islam360NotConfigured):
            provider.ayah(1, 1)
        with self.assertRaises(Islam360NotConfigured):
            provider.grammar('ن ز ل')

    def test_corpus_index_never_claims_islam360(self):
        self.assertFalse(self.index.meta.get('islam360_verified', False))


@unittest.skipUnless(
    __import__('services.quran_source', fromlist=['x']).ACTIVE.islam360_verified,
    'Islam360 app data is not present on this machine')
class TestIslam360Data(Base):
    """When Islam360 is connected, its data must actually be used."""

    def setUp(self):
        from services import quran_source
        self.provider = quran_source.get_islam360()

    def test_ayah_comes_from_islam360(self):
        ayah = self.provider.ayah(97, 1)
        self.assertTrue(ayah['arabic_text'])
        self.assertTrue(ayah['translation_urdu'])
        self.assertTrue(ayah['translation_english'])
        self.assertEqual(ayah['source'], 'Islam360')

    def test_root_lookup_and_lughaat(self):
        entry = self.provider.grammar('ن ز ل')
        self.assertTrue(entry.get('lughaat'), 'no لغات for ن ز ل')
        self.assertGreater(entry.get('word_count', 0), 10)

    def test_occurrences_carry_text_and_translation(self):
        occs = self.provider.occurrences('ن ز ل', limit=4)
        self.assertTrue(occs)
        for occ in occs:
            self.assertTrue(occ['arabic_text'])
            self.assertTrue(occ['translation_urdu'])
            self.assertTrue(1 <= int(occ['surah_number']) <= 114)

    def test_analyzer_prefers_islam360_for_ayaat(self):
        res = self.analyzer.analyze_verb('أَنْزَلَ')
        usage = res.get('quranic_usage') or []
        self.assertTrue(usage)
        self.assertEqual(usage[0].get('source'), 'Islam360')

    def test_analyzer_exposes_lughaat(self):
        res = self.analyzer.analyze_verb('أَنْزَلَ')
        self.assertTrue((res.get('islam360_lughaat') or {}).get('lughaat'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
