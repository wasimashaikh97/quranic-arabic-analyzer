# 📖 عربی فعل اور گردان — Quranic Arabic Verb & Sarf Analyzer

A digital **Sarf textbook**. A student types one Arabic word; the application
identifies its **مادہ، باب، وزن** and shows the complete **گردان** — all four
mandatory forms, امر، نہی، مصدر، اسم فاعل، اسم مفعول, the other verified verbs
of the same root, and a one-page printable chart.

Built for older Quran students: one input box, one button, very large Arabic,
light high-contrast page, RTL throughout, and A− / A / A+ text sizing.

---

## Running it

```bash
pip install -r requirements.txt
streamlit run app.py
```

Then open <http://localhost:8501>. To use it on a phone on the same WiFi:

```bash
streamlit run app.py --server.address 0.0.0.0
```

and open `http://<your-computer-ip>:8501`.

### Rebuilding the data

`data/verbs.json` and `data/roots.json` are **generated**. Edit the curated
lexicon in `data/lexicon.py`, then:

```bash
python data/build_lexicon.py
```

### Running the tests

```bash
python -m unittest tests.test_analyzer tests.test_ui
```

---

## Deploying (public URL)

```bash
git push -u origin main       # username = your GitHub name, password = a PAT
```

Then **share.streamlit.io** → *New app* → pick the repo → branch `main`,
main file `app.py` → **Deploy**. The public URL is `https://<name>.streamlit.app`.

Nothing else is needed: the Arabic fonts are bundled in `assets/fonts/`, so the
PDF renders identically on Linux, and `data/user_data.db` is created on first
run (it is git-ignored, being per-user data).

---

## The accuracy rule this project is built on

> Arabic morphology must be accurate. Do **not** generate a form merely because
> a pattern allows it.

So the design puts the hard part in **verified data** and only the regular part
in code:

* The **four principal parts** of every verb —
  ماضی معروف / مضارع معروف / ماضی مجہول / مضارع مجہول — are recorded per verb in
  `data/lexicon.py` from dictionary and textbook attestation.
* `core/conjugation.py` performs only the **regular** inflection of those
  verified stems across the 14 صیغے, and derives امر / نہی from the مجزوم.
* When a form is genuinely not applicable — an intransitive verb has no passive,
  باب انفعال has no اسم مفعول, a root has no verb in a given باب — the
  application prints **«قابلِ اطلاق نہیں»** with the reason, and invents nothing.

That is why an unknown word returns
*«اس لفظ کی مستند صرفی معلومات دستیاب نہیں۔»* rather than a plausible-looking
conjugation.

**Coverage:** 84 verified verbs · 51 roots · 9 ابواب · 5,208 generated forms ·
63 Quranic occurrences.

---

## The eight ابواب ثلاثی مزید فیہ

Shown with their Arabic names and patterns, in the reference book's order —
never as "Form II, Form III":

| # | باب | ماضی | مضارع | ماضی مجہول | مضارع مجہول | مصدر |
|---|---|---|---|---|---|---|
| ۱ | إفعال | أَفْعَلَ | يُفْعِلُ | أُفْعِلَ | يُفْعَلُ | إِفْعَال |
| ۲ | تفعیل | فَعَّلَ | يُفَعِّلُ | فُعِّلَ | يُفَعَّلُ | تَفْعِيل |
| ۳ | مفاعلة | فَاعَلَ | يُفَاعِلُ | فُوعِلَ | يُفَاعَلُ | مُفَاعَلَة |
| ۴ | تفعّل | تَفَعَّلَ | يَتَفَعَّلُ | تُفُعِّلَ | يُتَفَعَّلُ | تَفَعُّل |
| ۵ | تفاعل | تَفَاعَلَ | يَتَفَاعَلُ | تُفُوعِلَ | يُتَفَاعَلُ | تَفَاعُل |
| ۶ | انفعال | اِنْفَعَلَ | يَنْفَعِلُ | — | — | اِنْفِعَال |
| ۷ | افتعال | اِفْتَعَلَ | يَفْتَعِلُ | اُفْتُعِلَ | يُفْتَعَلُ | اِفْتِعَال |
| ۸ | استفعال | اِسْتَفْعَلَ | يَسْتَفْعِلُ | اُسْتُفْعِلَ | يُسْتَفْعَلُ | اِسْتِفْعَال |

باب انفعال is intransitive by meaning (مطاوعت), so it correctly has no passive
and no اسم مفعول. باب ثلاثی مجرد and باب افعلال are also included.

---

## What the student sees

**Home** — one box, one button, ten example verbs. No root/باب/tense selectors.

**Result** — 📖 فعل کی معلومات: فعل، مادہ، باب، وزن, all four principal parts,
مصدر، اسم فاعل، اسم مفعول, Urdu and English meaning. Then large buttons:

| Button | What it shows |
|---|---|
| 📊 جدول | `باب \| مادہ \| ماضی معروف \| مضارع معروف \| ماضی مجہول \| مضارع مجہول`, one clickable row per verb of the root, then the six full gardaan tables |
| 🌳 درخت | مادہ ↓ فعل ↓ باب ↓ وزن ↓ the four forms ↓ مکمل گردان — clickable nodes |
| 📚 مکمل صرف | Everything, in the taught order (19 sections) |
| 📚 تمام افعال | Every باب of the root: the verified verb, or an explicit gap |
| 📖 مکمل گردان | The traditional tables, 14 صیغے each |
| 🧠 کیوں؟ | Plain-language explanation of every صیغہ |
| 📖 قرآن میں استعمال | Verified Surah/Ayah occurrences |
| 📚 آٹھ ابواب | The teaching page for all eight ابواب |

Typing an **inflected** word works too: `يُنْزِلُ`, `أُنْزِلَ`, `كَتَبْتُمَا`,
`قَالُوا`, `دَعَوْا`, `كُلْ` are each parsed to their dictionary form with tense,
person, number and gender named.

**Also kept:** ⚖ تقابل, ✍ مشق, 🗂 فلیش کارڈ (SM-2), 📊 پیش رفت, ⭐ محفوظ افعال,
🔊 pronunciation, and 🕘 recent searches.

---

## PDF

Two layouts, both with correct Arabic/Urdu shaping and RTL:

* **📄 One-page chart (A4 landscape)** — the whole verb on **one printable
  sheet**: header (فعل، مادہ، باب، وزن، مصدر، اسم فاعل، اسم مفعول، معنی), the
  four gardaans side by side at 14 rows each, then امر، نہی، مشتقات and the
  hierarchical summary. Type scales down automatically so it *never* spills onto
  a second page — verified for all 84 verbs.
* **📚 Detailed booklet** — every صیغہ with its Urdu and English gloss, plus
  derivatives, related افعال and Quranic usage.

> A note on why this needed care: `arabic_reshaper` **deletes all harakat by
> default** (`أَنْزَلَ` would print as `أنزل`), which would make a Sarf sheet
> useless. `services/pdf_generator.py` overrides that, and substitutes glyphs
> the font lacks (arrows) so no empty boxes can appear.

---

## Test report

`python -m unittest tests.test_analyzer tests.test_ui` → **104 tests, all
passing.** Every row below is asserted against the form a textbook gives, not
merely that a page loaded.

| Feature | Status | How it is verified |
|---|---|---|
| Root detection | **PASS** | 9 verbs across all ابواب map to the right مادہ |
| Baab detection | **PASS** | Arabic باب name asserted (إفعال، تفعیل، …), not "Form IV" |
| Wazn | **PASS** | أَفْعَلَ / فَعَّلَ / فَاعَلَ / … asserted per verb |
| Past Active | **PASS** | 14 صیغے compared to textbook tables |
| Present Active | **PASS** | 14 صیغے compared to textbook tables |
| Past Passive | **PASS** | 14 صیغے, incl. قِيلَ→قِلْتُ, دُعِيَ→دُعُوا, رُدَّ→رُدِدْتُ |
| Present Passive | **PASS** | 14 صیغے, incl. يُدْعَى، يُؤْكَلُ→أُوكَلُ |
| Complete Gardaan | **PASS** | No doubled diacritics; no unvowelled endings; 14/6 or 0 everywhere |
| Imperative | **PASS** | 15 verbs: اُكْتُبْ، اِعْلَمْ، قُلْ، عِدْ، اُدْعُ، أَنْزِلْ، رُدَّ، كُلْ، مُرْ |
| Prohibition | **PASS** | لَا + مجزوم; hollow shortens (لَا تَقُلْ) |
| Af'aal | **PASS** | ن ز ل returns باب I, II, IV, V, X and reports the gaps |
| All 8 Abwaab | **PASS** | Names, 4 patterns, مصدر/فاعل/مفعول, examples, pattern conjugates |
| Weak verbs | **PASS** | hollow قَالَ بَاعَ صَامَ خَافَ · defective دَعَا رَمَى سَعَى هَدَى · assimilated وَعَدَ وَجَدَ وَقَفَ · lafeef وَفَى وَقَى رَوَى |
| Hamzated verbs | **PASS** | أَكَلَ سَأَلَ قَرَأَ أَمَرَ; آكُلُ, قَرَآ, قَرَؤُوا, تَقْرَئِينَ |
| Doubled verbs | **PASS** | رَدَّ مَدَّ شَدَّ; رَدَدْتُ, يَرْدُدْنَ |
| Derived forms | **PASS** | All 49 specified verbs resolve to themselves |
| Urdu | **PASS** | Every row glossed; اُس (ایک مرد) نے لکھا / وہ (ایک عورت) لکھتی ہے |
| English | **PASS** | He wrote / He writes / He was written |
| Arabic RTL | **PASS** | Tables reverse column order in ur/ar; `dir` set per block |
| Table | **PASS** | Six required columns present; rows clickable and open the gardaan |
| Hierarchy | **PASS** | All nodes present; tense nodes clickable |
| Complete Sarf | **PASS** | All 19 sections render, derivatives included |
| PDF | **PASS** | One page for all 84 verbs; no blank pages; harakat kept; opens |
| Mobile UI | **PASS** | Breakpoints at 720px/460px; tables scroll in their own box |
| Invalid input | **PASS** | Empty → براہ کرم عربی لفظ درج کریں۔ · English → Please enter an Arabic word. · unknown → اس لفظ کی مستند صرفی معلومات دستیاب نہیں۔ |
| No invention | **PASS** | 13 intransitive verbs have no passive + a stated reason; absent باب reported, not generated |
| Conjugated input | **PASS** | 17 inflected forms parsed to verb + tense + صیغہ |
| Languages | **PASS** | Every label present in اردو / العربية / English |
| Text size | **PASS** | A− / A / A+ change `font_scale` and re-render |
| Existing features | **PASS** | Bookmarks, study history, practice, SM-2 intervals all round-trip |

### Bugs found and fixed along the way

| Bug | Effect before | Now |
|---|---|---|
| `arabic_reshaper` deletes harakat by default | Every PDF printed `أنزل` for `أَنْزَلَ` — no vowels at all | Configured to keep them |
| Shadda stripped when matching | `عَلَّمَ` resolved to `عَلِمَ`; باب تفعیل unreachable | Shadda kept in the lookup key |
| Suffix truncation off by one | `تَعْلَمُُوا`, `اِرْمِيََا` — doubled vowels throughout | Rebuilt from stems |
| Defective/doubled/hollow paradigms | `يَدْعُوُ`, `يَرْدُدُ`, `دُعِو` | `يَدْعُو`, `يَرُدُّ`, `دُعِيَ` |
| Form I past 3ms lost its final vowel | `وَعَد`, `أَكَل` | `وَعَدَ`, `أَكَلَ` |
| Form VII/VIII imperative dropped the alif | `نْتَصِرْ` | `اِنْتَصِرْ` |
| Hamzat al-wasl vowel from wrong letter | `اِدْعِي` beside `اُدْعُ` | `اُدْعِي` — from the stem vowel |
| Final ن did not assimilate | `تَعَاوَنْنَ` | `تَعَاوَنَّ` |
| `compare_view.py`: `{{}}` inside an f-string | Page crashed with `TypeError: unhashable type: 'dict'` | Rewritten |
| `compare_view.py`: tense keys `past`/`present` | Comparison tables were always empty | `past_active` / `present_active` |
| PDF Quranic section read wrong keys | Section printed blank | Correct keys |
| `afaal_view` iterated a dict as a list | `AttributeError` on open | Rewritten |
| `abwaab_view` / `afaal_view` never wired up | Unreachable code | Both are now navigation destinations |

---

## Layout

```
app.py                  home page, result page, navigation, PDF buttons
core/
  arabic_utils.py       diacritics, canonical mark order, comparison keys
  conjugation.py        the inflection engine (14 صیغے, jussive, امر, نہی)
  abwaab.py             the ابواب: names, patterns, explanations, examples
  morphology.py         verb/root type classification
  search.py             layered lookup (exact → vowel-free → loose)
  validation.py         input checks and the friendly messages
  analyzer.py           orchestration, reverse parsing, user data
data/
  lexicon.py            ← the curated, verified source of truth
  build_lexicon.py      generates the JSON below
  verbs.json            84 verbs (generated)
  roots.json            51 roots (generated)
  quranic_occurrences.json   63 verified references
services/pdf_generator.py    one-page chart + detailed booklet
ui/
  theme.py              palette, translations, CSS, shared HTML builders
  table_view.py  tree_view.py  sarf_view.py  gardaan_view.py
  afaal_view.py  abwaab_view.py  learning_view.py
  compare_view.py  practice.py  dashboard.py
assets/fonts/           Amiri + Noto Naskh Arabic (bundled for the PDF)
tests/
  test_analyzer.py      73 engine tests
  test_ui.py            31 AppTest interface tests
```

## Licence of bundled fonts

Amiri and Noto Naskh Arabic are under the SIL Open Font License 1.1.
