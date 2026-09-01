# 📖 عربی فعل اور گردان — Quranic Arabic Verb & Sarf

A digital **Sarf textbook** for Quran students, built around three jobs:

1. a student types **any Arabic verb** and gets every form and its grammar;
2. they can **download a PDF** of that verb to print and keep;
3. they can see the **Quranic ayaat** where that verb actually occurs.

The reader is an older student (50+). So there is **one box, one button**, and
then **one page that reads straight down** — nothing is hidden behind
navigation, because for this reader anything behind a button is effectively not
there.

---

## Running it

```bash
pip install -r requirements.txt
streamlit run app.py
```

Open <http://localhost:8501>. For a phone on the same WiFi:

```bash
streamlit run app.py --server.address 0.0.0.0
```

## Deploying

```bash
git push -u origin main       # username = your GitHub name, password = a PAT
```

Then **share.streamlit.io** → *New app* → the repo → branch `main`, main file
`app.py` → **Deploy**. Nothing else is needed: the Arabic fonts are bundled in
`assets/fonts/` so the PDF renders identically on Linux, and the Quranic index
is committed, so the app never needs the network at runtime.

## Rebuilding the data

Both JSON files are **generated**:

```bash
python data/build_lexicon.py                    # verbs.json + roots.json
python data/build_quran_index.py --download     # quranic_occurrences.json
```

## Tests

```bash
python -m unittest tests.test_analyzer tests.test_ui     # 120 tests
```

---

## The accuracy rule

> Arabic morphology must be accurate. Do **not** generate a form merely because
> a pattern allows it. Do not write Quranic text from memory.

Both halves are enforced by the architecture:

**Verb forms.** The **four principal parts** of every verb —
ماضی معروف / مضارع معروف / ماضی مجہول / مضارع مجہول — are recorded per verb in
`data/lexicon.py` from dictionary and textbook attestation.
`core/conjugation.py` performs only the **regular** inflection of those verified
stems, and derives امر / نہی from the مجزوم. Where a form genuinely does not
exist — an intransitive verb has no passive, باب انفعال has no اسم مفعول, a root
has no verb in some باب — the app prints **«قابلِ اطلاق نہیں»** or the book's
**×**, with the reason, and invents nothing.

**Quranic ayaat.** Not one ayah is typed by hand. `data/build_quran_index.py`
reads the **Tanzil uthmani** text, then searches it for the forms the engine
generates, matching on letters and vowels position by position. A hit is kept
only if the letters agree and no letter carries a contradicting mark — which is
what keeps `نَادِيَهُ` (96:17, the noun *his assembly*) out of نَادَى's results
and `أَعْنَتَ` (root ع‑ن‑ت) out of أَعَانَ's. Translations are Jalandhry (Urdu)
and Sahih International (English).

**Coverage:** 84 verified verbs · 51 roots · 9 ابواب · 288 Quranic ayaat across
65 verbs · 281 of those labelled with the exact صیغہ.

---

## What a student sees

**Home** — the title, one input, one button, six examples. No selectors for
root, باب, tense, gender: the app works those out.

**One page per verb**, numbered in teaching order:

| | Section | Contents |
|---|---|---|
| ① | فعل کی معلومات | مادہ، باب، وزن، قسم، مصدر، اسم فاعل، اسم مفعول، متعدی/لازم |
| ② | چار بنیادی صورتیں | the four mandatory forms |
| ③ | مکمل گردان | four grids, 14 صیغے each, with the Urdu/English gloss one tap away |
| ④ | امر · نہی | side by side |
| ⑤ | مشتقات | with its وزن |
| ⑥ | تمام افعال | every باب of the root: the attested verb, or **×** |
| ⑦ | باب کی وضاحت | what this باب does to the meaning, in Urdu and English |
| ⑧ | قرآن میں استعمال | the ayaat, with the matched word and its صیغہ named |
| | 📥 | the two PDFs |

Typing an **inflected** word works too — `يُنْزِلُ`, `أُنْزِلَ`, `كَتَبْتُمَا`,
`قَالُوا`, `دَعَوْا`, `كُلْ` are each traced back to their dictionary form with
tense, person, number and gender named.

Also: 📚 **ابواب** — the eight ثلاثی مزید فیہ with their patterns, explanations,
examples, and the وزن itself fully conjugated. Three languages (اردو /
العربية / English) and 👓 A− / A / A+ text sizing on every page.

### The گردان follows your book

Not a 14-row list but the grid the printed book uses — five rows, three
columns, first person merged:

| | جمع | مثنی | واحد |
|---|---|---|---|
| **غائب مذکر** (3rd m.) | أَنْزَلُوا | أَنْزَلَا | أَنْزَلَ |
| **غائب مؤنث** (3rd f.) | أَنْزَلْنَ | أَنْزَلَتَا | أَنْزَلَتْ |
| **حاضر مذکر** (2nd m.) | أَنْزَلْتُمْ | أَنْزَلْتُمَا | أَنْزَلْتَ |
| **حاضر مؤنث** (2nd f.) | أَنْزَلْتُنَّ | أَنْزَلْتُمَا | أَنْزَلْتِ |
| **متکلم** (1st) | أَنْزَلْنَا (merged) || أَنْزَلْتُ |

A third of the height of the old list, so all four tenses fit on one screen,
in the shape the student already recognises.

---

## PDF

* **📄 One-page chart (A4 landscape)** — the whole verb on **one printable
  sheet**: the identity header, the four gardaan grids two-by-two, then
  امر، نہی، مشتقات and the hierarchical summary. Type scales down automatically,
  so it never spills onto a second page — verified for all 84 verbs.
* **📚 Detailed booklet** — every صیغہ with its Urdu and English gloss, plus
  derivatives, related افعال and the Quranic ayaat.

> `arabic_reshaper` **deletes all harakat by default** (`أَنْزَلَ` would print as
> `أنزل`), which would make a Sarf sheet useless. `services/pdf_generator.py`
> overrides that and substitutes glyphs the font lacks, so no empty boxes appear.

---

## The eight ابواب ثلاثی مزید فیہ

Shown with their Arabic names, in the reference book's order — never as
"Form II, Form III":

| # | باب | ماضی | مضارع | ماضی مجہول | مضارع مجہول | مصدر |
|---|---|---|---|---|---|---|
| ۱ | إفعال | أَفْعَلَ | يُفْعِلُ | أُفْعِلَ | يُفْعَلُ | إِفْعَال |
| ۲ | تفعیل | فَعَّلَ | يُفَعِّلُ | فُعِّلَ | يُفَعَّلُ | تَفْعِيل |
| ۳ | مفاعلة | فَاعَلَ | يُفَاعِلُ | فُوعِلَ | يُفَاعَلُ | مُفَاعَلَة |
| ۴ | تفعّل | تَفَعَّلَ | يَتَفَعَّلُ | تُفُعِّلَ | يُتَفَعَّلُ | تَفَعُّل |
| ۵ | تفاعل | تَفَاعَلَ | يَتَفَاعَلُ | تُفُوعِلَ | يُتَفَاعَلُ | تَفَاعُل |
| ۶ | انفعال | اِنْفَعَلَ | يَنْفَعِلُ | × | × | اِنْفِعَال |
| ۷ | افتعال | اِفْتَعَلَ | يَفْتَعِلُ | اُفْتُعِلَ | يُفْتَعَلُ | اِفْتِعَال |
| ۸ | استفعال | اِسْتَفْعَلَ | يَسْتَفْعِلُ | اُسْتُفْعِلَ | يُسْتَفْعَلُ | اِسْتِفْعَال |

باب انفعال is intransitive by meaning (مطاوعت), so it correctly has no passive
and no اسم مفعول. ثلاثی مجرد and باب افعلال are included too.

---

## Test report

`python -m unittest tests.test_analyzer tests.test_ui` → **120 tests, all
passing.** Assertions compare against the form a textbook gives, not merely
that a page loaded.

| Feature | Status | How it is verified |
|---|---|---|
| Root detection | **PASS** | 9 verbs across all ابواب map to the right مادہ |
| Baab detection | **PASS** | the Arabic باب name is asserted, not "Form IV" |
| Wazn | **PASS** | أَفْعَلَ / فَعَّلَ / فَاعَلَ … per verb |
| Past & Present Active | **PASS** | 14 صیغے compared to textbook tables |
| Past & Present Passive | **PASS** | incl. قِيلَ→قِلْتُ، دُعِيَ→دُعُوا، رُدَّ→رُدِدْتُ |
| Complete Gardaan | **PASS** | no doubled diacritics; no unvowelled endings; 14/6 or 0 everywhere |
| Book's 5×3 grid | **PASS** | row/column labels, merged first person, × for absent |
| Imperative | **PASS** | 15 verbs: اُكْتُبْ، اِعْلَمْ، قُلْ، عِدْ، اُدْعُ، أَنْزِلْ، رُدَّ، كُلْ، مُرْ |
| Prohibition | **PASS** | لَا + مجزوم; hollow shortens (لَا تَقُلْ) |
| منصوب / مجزوم | **PASS** | يَقُولَ/يَقُلْ، يَدْعُوَ/يَدْعُ، يَسْعَى/يَسْعَ |
| Af'aal by root | **PASS** | ن ز ل returns باب I, II, IV, V, X and marks the gaps |
| All 8 Abwaab | **PASS** | names, 4 patterns, مصدر/فاعل/مفعول, examples, pattern conjugates |
| Weak verbs | **PASS** | hollow · defective · assimilated · lafeef |
| Hamzated verbs | **PASS** | آكُلُ، قَرَآ، قَرَؤُوا، تَقْرَئِينَ |
| Doubled verbs | **PASS** | رَدَدْتُ، يَرْدُدْنَ |
| Reference-book data | **PASS** | the 4 passives and نَادَى's root ن د ي asserted |
| **Quranic ayaat** | **PASS** | 81:1، 82:1، 1:6، 55:2، 4:140 each cited correctly |
| Ayah integrity | **PASS** | every cited word really occurs in the ayah quoted, and shares the verb's root |
| Urdu | **PASS** | every صیغہ glossed; اُس (ایک مرد) نے لکھا |
| English | **PASS** | He wrote / He writes / He was written |
| Arabic RTL | **PASS** | tables reverse column order in ur/ar |
| Complete verb page | **PASS** | all 8 sections render for 14 spec verbs |
| Simplicity | **PASS** | ≤14 buttons on home, ≤20 on a verb page, 0 selectors |
| Removed features | **PASS** | asserted absent, so they cannot creep back |
| PDF | **PASS** | one page for all 84 verbs; no blanks; harakat kept; opens |
| Mobile UI | **PASS** | breakpoints at 720/460px; tables scroll in their own box |
| Invalid input | **PASS** | empty · English · unknown each get their own message |
| No invention | **PASS** | 13 verbs have no passive + a stated reason; absent باب reported |
| Conjugated input | **PASS** | 17 inflected forms parsed to verb + tense + صیغہ |
| Languages | **PASS** | every label present in اردو / العربية / English |

### Bugs found and fixed

| Bug | Effect before | Now |
|---|---|---|
| `arabic_reshaper` deletes harakat by default | every PDF printed `أنزل` for `أَنْزَلَ` | configured to keep them |
| Shadda stripped when matching | `عَلَّمَ` resolved to `عَلِمَ`; باب تفعیل unreachable | shadda kept in the lookup key |
| Suffix truncation off by one | `تَعْلَمُُوا`, `اِرْمِيََا` — doubled vowels | rebuilt from stems |
| Defective/doubled/hollow paradigms | `يَدْعُوُ`, `يَرْدُدُ`, `دُعِو` | `يَدْعُو`, `يَرُدُّ`, `دُعِيَ` |
| Form I past lost its final vowel | `وَعَد`, `أَكَل` | `وَعَدَ`, `أَكَلَ` |
| Form VII/VIII imperative dropped the alif | `نْتَصِرْ` | `اِنْتَصِرْ` |
| Hamzat al-wasl vowel from the wrong letter | `اِدْعِي` beside `اُدْعُ` | `اُدْعِي` |
| Final ن did not assimilate | `تَعَاوَنْنَ` | `تَعَاوَنَّ` |
| Four passives wrongly marked absent | اِسْتَهْزَأَ showed no مجہول, though 4:140 has يُسْتَهْزَأُ | present, per the book |
| Quranic coverage | 16 of 84 verbs (19%); أَنْزَلَ showed nothing | 65 of 84 (77%), found in the verified text |
| `ٱ` stripped as a mark | `ٱنفَطَرَتْ` became `نفَطَرَتْ`, losing 82:1 | `ٱ` treated as the letter it is |
| Weak radical required literally | every hollow verb's ayaat rejected (خ‑و‑ف → خَافَ has no و) | weak radicals matched loosely |
| Vowel *prefix* matching | `نَادِيَهُ` (a noun) cited as a form of نَادَى | position-by-position comparison |
| PDF grid header reversed | plurals printed under واحد | column order matched to the data |
| `compare_view.py`: `{{}}` in an f-string | page crashed with `TypeError` | view removed |
| `compare_view.py`: tense keys `past`/`present` | comparison tables always empty | view removed |
| `afaal_view` iterated a dict as a list | `AttributeError` on open | rewritten, then inlined |
| `abwaab_view`/`afaal_view` never wired up | unreachable code | ابواب is a destination; افعال is section ⑥ |
| PDF Quranic section read wrong keys | section printed blank | correct keys |

### Removed, to keep it usable for an older reader

مشق · فلیش کارڈ · میری پیش رفت · تقابل · محفوظ افعال · تلفظ · حالیہ تلاش · the
sidebar · the 8-button view navigation · the separate درخت and کیوں؟ pages.
**A verb page went from 42 buttons to 12.** The tests assert these stay gone.

---

## Layout

```
app.py                  the whole interface: home, the verb page, PDFs
core/
  arabic_utils.py       diacritics, canonical mark order, comparison keys
  conjugation.py        the inflection engine (14 صیغے, منصوب, مجزوم, امر, نہی)
  abwaab.py             the ابواب: names, patterns, explanations, examples
  morphology.py         verb/root type classification
  search.py             layered lookup (exact → vowel-free → loose)
  validation.py         input checks and the friendly messages
  analyzer.py           orchestration, reverse parsing
data/
  lexicon.py            ← the curated, verified source of truth
  build_lexicon.py      generates verbs.json + roots.json
  build_quran_index.py  searches the verified Quran text
  verbs.json  roots.json  quranic_occurrences.json    (all generated)
services/pdf_generator.py    one-page chart + detailed booklet
ui/
  theme.py              palette, translations, CSS, the گردان grid
  abwaab_view.py        the ابواب reference page
assets/fonts/           Amiri + Noto Naskh Arabic (bundled for the PDF)
tests/
  test_analyzer.py      89 engine, data and Quran-index tests
  test_ui.py            31 AppTest interface tests
```

## Sources & licences

* Quran text — [Tanzil](https://tanzil.net) uthmani edition
* Urdu translation — Fateh Muhammad Jalandhry · English — Sahih International
  (both via alquran.cloud)
* Amiri and Noto Naskh Arabic — SIL Open Font License 1.1
