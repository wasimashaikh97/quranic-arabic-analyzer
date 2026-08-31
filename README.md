# 📖 Quranic Arabic Verb Analyzer (قرآنک عربی فعل تجزیہ)

A complete, deployment-ready digital Quranic Arabic reference book and morphology analyzer built for Quran students and teachers, especially older learners who prefer simple, high-contrast, accessible visual interfaces over technical complex software.

---

## 🌟 Key Features

1. **Elderly-First Accessible Interface**:
   - Single large input box (`عربی فعل یہاں لکھیں`) and single large search button (`🔍 تجزیہ کریں`).
   - One-click example verb chips: `كَتَبَ`, `نَصَرَ`, `عَلِمَ`, `قَالَ`, `دَعَا`, `رَمَى`, `وَعَدَ`, `رَدَّ`, `أَرْسَلَ`, `كَتَبْتُمَا`.
   - **👓 بڑا حروف (Large Text Mode)** with A-, A, A+ font scaling controls.
   - Audio pronunciation trigger (🔊) using Web Speech Synthesis API.

2. **Deterministic Morphology Engine**:
   - Rule-based conjugation generation supporting Form I (ثلاثی مجرد) and Forms II–X (ثلاثی مزید).
   - Full support for **Sound** (`كَتَبَ`), **Hollow** (`قَالَ`), **Defective** (`دَعَا`, `رَمَى`), **Assimilated** (`وَعَدَ`), **Doubled** (`رَدَّ`), **Hamzated** (`أَكَلَ`), and **Form IV** (`أَرْسَلَ`) verbs.

3. **Quick Word Analysis (Reverse Parser)**:
   - Input conjugated forms like `كَتَبْتُمَا` to instantly reverse-analyze root, base verb, tense (`ماضی`), pronoun (`أَنْتُمَا`), person (2nd person), number (dual), gender, Urdu meaning (`تم دونوں نے لکھا`), English meaning (`You two wrote`), and a direct `[ مکمل گردان دیکھیں ]` button.

4. **Complete 14/6 Gardaan Tables**:
   - Past Active (14 forms), Present Active (14 forms), Past Passive (14 forms), Present Passive (14 forms), Imperative (6 forms), Prohibition (6 forms), and Derived Nouns (Ism Fa'il, Ism Maf'ul, Masdar).
   - RTL Arabic & Urdu column alignment with complete pronoun translations and no abbreviating `...`.

5. **Visual Views**:
   - **📊 جدول (Table View)**: Clean high-contrast tables.
   - **🌳 درخت (Hierarchical View)**: Interactive tree visualizer.
   - **🧠 سیکھیں (Learning View)**: Step-by-step Q&A breakdowns (`یہ کیا ہے؟`, `کس نے؟`, `کتنے؟`, `جنس؟`, `معنی`).
   - **📖 قرآنی استعمال (Quranic Usage)**: Surah/Ayah references with highlighted verbs and translations.

6. **Print-Ready PDF Study Sheet**:
   - Multi-page study sheet styled like a traditional printed reference sheet with proper Arabic/Urdu reshaped characters.
   - Download options for Urdu, English, and Quranic examples.

7. **Practice & Flashcards**:
   - MCQ practice drills generated from verb data with instant explanations and score tracking.
   - Interactive flashcards with Flip action and Easy/Medium/Hard ratings.

---

## 📁 Project Architecture

```
quranic_arabic_analyzer/
├── app.py                     # Main Streamlit web application orchestrator
├── core/
│   ├── analyzer.py            # Main VerbAnalyzer API and reverse parser
│   ├── morphology.py          # Morphological classification & verb type definitions
│   ├── conjugation.py         # Deterministic rule-based conjugation engine
│   ├── search.py              # Diacritic-insensitive search & conjugated matching
│   └── validation.py          # Input validation and language detection
├── data/
│   ├── verbs.json             # Validated verb dataset (Forms I-X & weak categories)
│   ├── roots.json             # Root dictionary metadata
│   ├── quranic_occurrences.json # Verified Quranic verse occurrences
│   ├── generate_jsons.py      # Seed dataset generator script
│   └── user_data.db           # SQLite database for bookmarks & practice history
├── services/
│   ├── pdf_generator.py       # ReportLab PDF study sheet generator with Arabic reshaping
│   └── ai_service.py          # Graceful AI helper service
├── ui/
│   ├── table_view.py          # Gardaan table view component
│   ├── tree_view.py           # Interactive Plotly tree diagram
│   ├── learning_view.py       # Educational step-by-step breakdown
│   ├── practice.py            # MCQ Quiz & Flashcards components
│   └── dashboard.py           # User study statistics & bookmarks
├── tests/
│   └── test_analyzer.py       # Automated unit test suite
├── requirements.txt           # Dependency requirements
└── README.md                  # Project documentation
```

---

## 🚀 How to Run Locally

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start the Streamlit application:
   ```bash
   streamlit run app.py
   ```

---

## 🧪 How to Run Automated Tests

To run the full test suite validating sound, weak, reverse parsing, and PDF export:
```bash
python -m unittest discover -s tests
```

---

## ➕ How to Add More Verbs

1. Open `data/generate_jsons.py` or edit `data/verbs.json`.
2. Add a new verb object:
   ```json
   {
     "id": "v017",
     "arabic": "عَلَّمَ",
     "root": "ع ل م",
     "root_letters": ["ع", "ل", "م"],
     "form": 2,
     "pattern": "فَعَّلَ",
     "masdar": "تَعْلِيمًا",
     "meaning_urdu": "سکھانا",
     "meaning_english": "to teach",
     "verb_type": "sound"
   }
   ```
3. Run `python data/generate_jsons.py` to compile the dataset into `data/verbs.json`.

---

## ☁️ Deployment Guide

### Deploying to Streamlit Community Cloud:
1. Push this repository to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io/).
3. Connect your GitHub account and select this repository.
4. Set main file path to `app.py`.
5. Click **Deploy**.

---

## 🔮 Future Enhancements
- Integration of complete 114 Surah Quranic corpus index.
- Spaced repetition algorithm (SM-2) for flashcards.
- Offline desktop PWA installer.
