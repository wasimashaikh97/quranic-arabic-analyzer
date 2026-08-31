import unittest
import sys
import os
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.analyzer import VerbAnalyzer
from core.conjugation import ConjugationEngine
from core.morphology import ArabicMorphology
from services.pdf_generator import PDFGenerator

class TestQuranicArabicAnalyzer(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.analyzer = VerbAnalyzer()
        cls.conjugator = ConjugationEngine()
        cls.pdf_gen = PDFGenerator()

    def test_01_sound_verb_kataba(self):
        res = self.analyzer.analyze_verb("كَتَبَ")
        self.assertTrue(res.get("found"))
        verb = res.get("verb")
        self.assertEqual(verb.get("arabic"), "كَتَبَ")
        self.assertEqual(verb.get("root"), "ك ت ب")
        
        conjugations = res.get("conjugations")
        self.assertIn("past_active", conjugations)
        self.assertIn("present_active", conjugations)
        
        past_list = conjugations["past_active"]
        self.assertEqual(len(past_list), 14)
        self.assertEqual(past_list[0]["arabic"], "كَتَبَ") # هو
        self.assertEqual(past_list[7]["arabic"], "كَتَبْتُمَا") # أنتما
        self.assertEqual(past_list[12]["arabic"], "كَتَبْتُ") # أنا

    def test_02_reverse_analysis_katabtuma(self):
        quick_res = self.analyzer.quick_analyze("كَتَبْتُمَا")
        self.assertTrue(quick_res.get("found"))
        self.assertEqual(quick_res.get("base_verb"), "كَتَبَ")
        self.assertEqual(quick_res.get("root"), "ك ت ب")
        self.assertEqual(quick_res.get("pronoun"), "أَنْتُمَا")

    def test_03_hollow_verb_qala(self):
        res = self.analyzer.analyze_verb("قَالَ")
        self.assertTrue(res.get("found"))
        verb = res.get("verb")
        self.assertEqual(verb.get("verb_type"), "hollow")
        
        conjugations = res.get("conjugations")
        past_list = conjugations["past_active"]
        self.assertEqual(past_list[0]["arabic"], "قَالَ")
        self.assertEqual(past_list[6]["arabic"], "قُلْتَ")

    def test_04_defective_verb_daaa(self):
        res = self.analyzer.analyze_verb("دَعَا")
        self.assertTrue(res.get("found"))
        verb = res.get("verb")
        self.assertEqual(verb.get("verb_type"), "defective")

    def test_05_assimilated_verb_waada(self):
        res = self.analyzer.analyze_verb("وَعَدَ")
        self.assertTrue(res.get("found"))
        verb = res.get("verb")
        self.assertEqual(verb.get("verb_type"), "assimilated")

    def test_06_doubled_verb_radda(self):
        res = self.analyzer.analyze_verb("رَدَّ")
        self.assertTrue(res.get("found"))
        verb = res.get("verb")
        self.assertEqual(verb.get("verb_type"), "doubled")

    def test_07_form_iv_arsala(self):
        res = self.analyzer.analyze_verb("أَرْسَلَ")
        self.assertTrue(res.get("found"))
        verb = res.get("verb")
        self.assertEqual(verb.get("form"), 4)

    def test_08_pdf_generation(self):
        res = self.analyzer.analyze_verb("كَتَبَ")
        verb_info = res.get("verb")
        conjugations = res.get("conjugations")
        
        pdf_bytes = self.pdf_gen.generate_study_sheet(
            verb_data=verb_info,
            conjugations=conjugations,
            include_quranic=False,
            include_english=True,
            include_urdu=True
        )
        self.assertIsNotNone(pdf_bytes)
        self.assertTrue(len(pdf_bytes) > 1000)

    def test_09_quranic_corpus_coverage(self):
        """Verify Quranic occurrences exist for all 16 verb IDs."""
        for vid in ["v001", "v002", "v003", "v004", "v005", "v006", "v007",
                     "v008", "v009", "v010", "v011", "v012", "v013", "v014",
                     "v015", "v016"]:
            usage = self.analyzer.get_quranic_usage(vid)
            self.assertGreater(len(usage), 0, f"No Quranic occurrences found for {vid}")
        
        # Verify total coverage is substantial
        total = len(self.analyzer.quranic)
        self.assertGreaterEqual(total, 60, f"Expected 60+ occurrences, got {total}")

    def test_10_quranic_entry_structure(self):
        """Verify each Quranic entry has all required fields."""
        required_fields = ["verb_id", "root", "surah_number", "surah_name_arabic",
                          "surah_name_english", "surah_name_urdu", "ayah_number",
                          "arabic_text", "highlighted_word", "word_form",
                          "translation_urdu", "translation_english", "grammatical_note"]
        for entry in self.analyzer.quranic[:5]:
            for field in required_fields:
                self.assertIn(field, entry, f"Missing field '{field}' in Quranic entry")

    def test_11_sm2_algorithm(self):
        """Test SM-2 spaced repetition card creation and interval calculation."""
        import sqlite3
        test_card_id = "_test_sm2_card"
        
        # Clean up any stale test data from previous runs
        with sqlite3.connect(self.analyzer.db_path, check_same_thread=False) as conn:
            conn.execute('DELETE FROM flashcard_sm2 WHERE card_id LIKE ?', ('_test_%',))
            conn.commit()
        
        # First review - quality 5 (perfect) should give interval=1
        updated = self.analyzer.update_sm2_card(test_card_id, "v001", "meaning", 5)
        self.assertEqual(updated["interval"], 1)
        self.assertEqual(updated["repetitions"], 1)
        self.assertGreaterEqual(updated["easiness_factor"], 2.5)
        
        # Second review - quality 5 should give interval=6
        updated = self.analyzer.update_sm2_card(test_card_id, "v001", "meaning", 5)
        self.assertEqual(updated["interval"], 6)
        self.assertEqual(updated["repetitions"], 2)

    def test_12_sm2_incorrect_resets(self):
        """Test that an incorrect answer resets repetitions."""
        import sqlite3
        test_card_id = "_test_sm2_reset"
        
        # Clean up stale test data
        with sqlite3.connect(self.analyzer.db_path, check_same_thread=False) as conn:
            conn.execute('DELETE FROM flashcard_sm2 WHERE card_id = ?', (test_card_id,))
            conn.commit()
        
        # Build up some repetitions
        self.analyzer.update_sm2_card(test_card_id, "v001", "meaning", 5)
        self.analyzer.update_sm2_card(test_card_id, "v001", "meaning", 5)
        
        # Incorrect answer (quality < 3) should reset
        updated = self.analyzer.update_sm2_card(test_card_id, "v001", "meaning", 1)
        self.assertEqual(updated["repetitions"], 0)
        self.assertEqual(updated["interval"], 1)

    def test_13_sm2_stats(self):
        """Test SM-2 statistics retrieval."""
        stats = self.analyzer.get_sm2_stats()
        self.assertIn("total_cards", stats)
        self.assertIn("due_today", stats)
        self.assertIn("average_ef", stats)

    def test_14_all_required_verbs_analyze(self):
        """Test that all 8 required verbs analyze correctly."""
        required_verbs = ["كَتَبَ", "عَلِمَ", "قَالَ", "دَعَا", "رَمَى", "وَعَدَ", "رَدَّ", "أَكَلَ"]
        for verb_arabic in required_verbs:
            res = self.analyzer.analyze_verb(verb_arabic)
            self.assertTrue(res.get("found"), f"Verb '{verb_arabic}' not found")
            verb = res.get("verb")
            self.assertIsNotNone(verb, f"No verb data for '{verb_arabic}'")
            self.assertTrue(len(verb.get("root", "")) > 0, f"No root for '{verb_arabic}'")

    def test_15_complete_14_form_gardaan(self):
        """Verify Past/Present conjugations always produce exactly 14 forms."""
        for verb in self.analyzer.verbs:
            conjugations = self.conjugator.conjugate_verb(verb)
            past = conjugations.get("past_active", [])
            present = conjugations.get("present_active", [])
            self.assertEqual(len(past), 14, f"Past tense of {verb.get('arabic')} has {len(past)} forms, expected 14")
            self.assertEqual(len(present), 14, f"Present tense of {verb.get('arabic')} has {len(present)} forms, expected 14")
            
            imperative = conjugations.get("imperative", [])
            prohibition = conjugations.get("prohibition", [])
            self.assertEqual(len(imperative), 6, f"Imperative of {verb.get('arabic')} has {len(imperative)} forms, expected 6")
            self.assertEqual(len(prohibition), 6, f"Prohibition of {verb.get('arabic')} has {len(prohibition)} forms, expected 6")

    def test_16_root_explorer(self):
        """Test get_verb_forms_for_root returns correct results."""
        # Root ك ت ب should return at least v001
        ktb_verbs = self.analyzer.get_verb_forms_for_root("ك ت ب")
        self.assertGreater(len(ktb_verbs), 0)
        self.assertTrue(any(v.get("id") == "v001" for v in ktb_verbs))

    def test_17_get_all_verbs(self):
        """Test get_all_verbs returns all verbs (16 original + 15 derived)."""
        all_verbs = self.analyzer.get_all_verbs()
        self.assertEqual(len(all_verbs), 31)

    def test_18_verb_type_classifications(self):
        """Verify each verb type is correctly classified."""
        type_map = {
            "كَتَبَ": "sound",
            "قَالَ": "hollow",
            "دَعَا": "defective",
            "وَعَدَ": "assimilated",
            "رَدَّ": "doubled",
            "أَكَلَ": "hamzated",
        }
        for arabic, expected_type in type_map.items():
            res = self.analyzer.analyze_verb(arabic)
            self.assertTrue(res.get("found"), f"Cannot find {arabic}")
            actual_type = res.get("verb", {}).get("verb_type")
            self.assertEqual(actual_type, expected_type, f"{arabic}: expected {expected_type}, got {actual_type}")

    def test_19_passive_conjugation(self):
        """Verify passive conjugations exist and have correct count."""
        res = self.analyzer.analyze_verb("كَتَبَ")
        conj = res.get("conjugations", {})
        past_passive = conj.get("past_passive", [])
        present_passive = conj.get("present_passive", [])
        self.assertEqual(len(past_passive), 14)
        self.assertEqual(len(present_passive), 14)

    def test_20_multi_verb_root_lookup(self):
        """Root ك ت ب should now have multiple verbs (Form I + derived forms)."""
        ktb_verbs = self.analyzer.get_verb_forms_for_root("ك ت ب")
        self.assertGreaterEqual(len(ktb_verbs), 4, f"Root ك ت ب should have at least 4 verbs, got {len(ktb_verbs)}")
        forms_found = sorted([v.get("form", 1) for v in ktb_verbs])
        self.assertIn(1, forms_found, "Form I كَتَبَ missing")
        self.assertIn(2, forms_found, "Form II كَتَّبَ missing")

    def test_21_derived_form_conjugation(self):
        """Test that Form II, IV, VIII verbs conjugate with 14 past + 14 present forms."""
        from core.conjugation import ConjugationEngine
        engine = ConjugationEngine()
        
        test_verbs = [
            {"arabic": "كَتَّبَ", "root_letters": ["ك", "ت", "ب"], "form": 2, "verb_type": "sound",
             "meaning_urdu": "لکھوانا", "meaning_english": "to make write"},
            {"arabic": "أَخْرَجَ", "root_letters": ["خ", "ر", "ج"], "form": 4, "verb_type": "sound",
             "meaning_urdu": "نکالنا", "meaning_english": "to extract"},
            {"arabic": "اِكْتَتَبَ", "root_letters": ["ك", "ت", "ب"], "form": 8, "verb_type": "sound",
             "meaning_urdu": "نقل کرنا", "meaning_english": "to copy"},
        ]
        for v in test_verbs:
            conj = engine.conjugate_verb(v)
            for tense in ['past_active', 'present_active', 'past_passive', 'present_passive']:
                self.assertEqual(len(conj[tense]), 14,
                    f"Form {v['form']} {v['arabic']} {tense} has {len(conj[tense])} forms, expected 14")
            for tense in ['imperative', 'prohibition']:
                self.assertEqual(len(conj[tense]), 6,
                    f"Form {v['form']} {v['arabic']} {tense} has {len(conj[tense])} forms, expected 6")

    def test_22_derived_form_passive(self):
        """Verify derived forms produce passive conjugations."""
        from core.conjugation import ConjugationEngine
        engine = ConjugationEngine()
        v = {"arabic": "عَلَّمَ", "root_letters": ["ع", "ل", "م"], "form": 2,
             "verb_type": "sound", "meaning_urdu": "سکھانا", "meaning_english": "to teach"}
        conj = engine.conjugate_verb(v)
        pp = conj['past_passive']
        self.assertEqual(len(pp), 14)
        # Form II passive past 3ms should start with عُ (فُعِّلَ pattern)
        self.assertTrue(pp[0]['arabic'].startswith('عُ'),
            f"Form II passive past should start with عُ, got: {pp[0]['arabic']}")

if __name__ == '__main__':
    unittest.main()

