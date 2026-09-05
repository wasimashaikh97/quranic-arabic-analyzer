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
python data/build_quran_verb_index.py --download # quran_verbs.json (the index)
```

## Tests

```bash
python -m unittest tests.test_analyzer tests.test_ui tests.test_quran_index   # 149 tests
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

## Search coverage — the complete Quranic verb index

Search is not limited to a hand-entered dictionary.  `data/quran_verbs.json`
is built from tagged corpus morphology and holds **every verb that occurs in
the Quran**:

| | |
|---|---|
| verb entries (root + باب) | **1,473** |
| distinct roots | **941** |
| verb tokens in the Quran | **19,353** |
| distinct written forms indexed | **8,551** |
| ابواب represented | 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 |

Two layers answer a search. The **curated lexicon** (84 verbs) is tried first
because it carries the fuller Sarf data — مصدر، اسم فاعل، اسم مفعول، meanings,
and a complete verified گردان. Anything it does not know falls through to the
**Quranic index**, which supplies the root, the باب, every form the Quran
contains, and the ayaat.

Entries are keyed on **(root, باب)** rather than on the corpus `LEM` tag,
because in 13% of verb tokens that tag is simply the surface form again
(`LEM:كُوِّرَتْ`, `LEM:يَشْعُرُ`) and would split one verb across several bogus
head-words. `ROOT` and `VF` are dependable, and together they are exactly how
this application models a verb.

The corpus splits a word into morphemes — `أَنزَلْنَٰهُ` is stored as
`أَنزَلْ` + `نَٰ` + `هُ` — so every token is also reassembled and indexed under
the spelling a student would actually type.

**Nothing is generated.** A principal part is recorded only when that exact
form occurs in the Quran; where it does not, the page shows `×` and says the
remaining forms were not invented.

### What the search accepts

با harakat or without, in any spelling a student is likely to use:

`أَنزَلَ` · `انزل` · `أَنْزَلَ` · `أُنزِلَ` · `أَنزَلْنَٰهُ` · `قالوا` ·
`يَكْتُبُونَ` · `يَسْتَغْفِرُونَ` · `ٱهْدِنَا` · `اهدنا` · `كور` · `ن ز ل`

Three normalisation bugs were fixed to make that work: `ٱ` (alef wasla) was
never folded to `ا`, so every Quranic word opening with it failed; Quranic
recitation marks (`قَالُوا۟`) were not stripped before comparison; and shadda
matches did not outrank vowel-blind ones, so `عَلَّمَ` (باب تفعیل) resolved to
the commoner `عَلِمَ` (باب اوّل).

### «کیا آپ کا مطلب یہ تھا؟»

A misspelling is not a dead end. `هدددى` → **هَدَى**, `سبببح` → **سَبَّحَ**,
`نصررر` → **نَصَرَ** — suggestions are drawn from verbs that really occur in
the Quran and filtered so an unrelated verb is never offered merely for
sharing a couple of letters. Truly random input (`زززز`) correctly suggests
nothing.

---

## ⌨ On-screen Arabic keyboard

Added *to* the existing search box, not in place of it — the box, the button
and the styling are untouched, and a device keyboard still works as before.
It sits in a collapsed panel underneath, because the reader is often an older
student on a phone with no Arabic keyboard installed.

* **37 letters** — ا أ إ آ ب ت ث ج ح خ د ذ ر ز س ش ص ض ط ظ ع غ ف ق ك ل م ن ه و ي ى,
  plus ء ؤ ئ ة لا
* **9 harakat** — َ ِ ُ ْ ّ ً ٍ ٌ ٰ, each labelled (فتحہ، کسرہ، ضمہ، سکون،
  تشدید …). They attach to the letter already typed, because they are Unicode
  combining marks.
* **Controls** — ⌫ · فاصلہ · سب مٹائیں · تجزیہ کریں, plus a live preview of
  what has been typed.

Verified on a 390 px phone, a 768 px tablet and a 1440 px desktop: keys stay
in an 8-across grid with no horizontal overflow. Streamlit stacks `st.columns`
vertically below ~640 px, which would have turned the keyboard into 37 rows of
a single key, so the keyboard's own rows are pinned horizontal.

---

## Quranic sources and Islam360

The specification requires Quranic references, meanings and grammar to come
from **Islam360 only**, and requires the application to say so plainly if
authorized access is unavailable rather than substitute another source.

> **Islam360 verification: CONNECTED on this machine.**
> Quranic verse text, surah names and both translations come from the Islam360
> Universal app installed on this computer.

### How it connects

Islam360 publishes no API — the network was probed and there is nothing to call:

| host | result |
|---|---|
| `islam360.com` | responds, but serves a **domain-parking page** ("ISLAM360.COM MAY BE AVAILABLE!") — not the app's site, no data |
| `islam360.pk` | connection times out |
| `api.islam360.pk` | DNS does not resolve |
| `quran.islam360.pk` | DNS does not resolve |

What Islam360 *does* have is a Windows app, and where it is installed its data
ships as XML. `data/build_islam360_index.py` reads that folder read-only and
writes `data/islam360_index.json`:

```
C:\Program Files\WindowsApps\48071ZahidHussainChihpa.Islam360Universal_…\XmlFiles\
    QuranComplete.xml   →  6,349 ayaat: Islam360's Arabic, Urdu, English, surah names
    RootWords.xml       →  2,296 roots, 15,749 words, 2,284 لغات articles
```

Run it once after installing the app:

```bash
python data/build_islam360_index.py
```

`services/quran_source.py` picks its provider from what is present: the
Islam360 index when it exists, otherwise the labelled fallback. Nothing is
ever presented as Islam360-verified when it is not.

### What Islam360 answers, and what it does not

Islam360 indexes by **root**. It does not tag صیغہ, and asking it for "every
word of this root" returns the wrong words — searching تَقَبَّلَ would come
back showing the preposition قَبْلِكَ. So the two questions are kept apart:

| question | answered by |
|---|---|
| which words in the Quran belong to *this verb* | Quranic Arabic Corpus tagged morphology |
| what صیغہ each occurrence is | Quranic Arabic Corpus tagged morphology |
| the verse text, and the surah's name | **Islam360** |
| the Urdu and English meanings | **Islam360** |
| the root's لغات article | **Islam360** |

The Quranic panel says this on screen rather than leaving it implied. Where a
verb has no attested occurrence in its باب, the app says so plainly and offers
Islam360's root-wide word list separately, folded away and labelled as *not*
صیغہ-analysed — it never stands in for the verb.

### Licensing

`data/islam360_index.json` holds Islam360's copyrighted content. It is built
locally and **git-ignored on purpose**: publishing it would be redistribution.

A deployment therefore cannot read it from the repository — so an operator who
*does* hold the right to use that data on their own server names its location
instead of committing it:

```bash
ISLAM360_INDEX_PATH=/srv/private/islam360_index.json
```

On Streamlit Cloud the same key works as a secret. Anything absent or
unreadable leaves the app in its honest NOT CONNECTED state, falling back to
the sources below and naming them openly — it never fails and never pretends.

**The fallback, labelled truthfully in the app when Islam360 is absent:**

| what | source |
|---|---|
| grammar (root, باب, tense, voice, person/gender/number) | Quranic Arabic Corpus tagged morphology |
| ayah text | Tanzil uthmani |
| Urdu translation | Fateh Muhammad Jalandhry |
| English translation | Sahih International |


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
