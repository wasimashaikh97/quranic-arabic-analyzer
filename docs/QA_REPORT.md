# QA report — Quranic Arabic Verb & Sarf

Measured on 2026‑09‑06 on the development machine (Windows 11, Python 3.12,
Streamlit 1.62, Islam360 Universal 1.1.0.23 installed). Every number below
comes from a run, not an estimate; the scripts are the tests in `tests/` and
the checks described under each area.

| area | status | evidence |
|---|---|---|
| Search — complete Quranic verb dataset | **PASS** | 1,473 verb entries · 941 roots · 19,353 tokens · 8,551 written forms indexed from tagged corpus morphology. 34/34 regression verbs found; 8/8 conjugated inputs resolve to their verb; six spellings of أَنْزَلَ (with/without harakat, wasla, madda) give one answer. |
| Search normalisation | **PASS** | Harakat optional; Quranic recitation marks, dagger alef, alef‑wasla, hamza forms, Urdu keyboard letter shapes (ی ک ھ ہ) all fold. Shadda still separates عَلَّمَ from عَلِمَ. |
| Did‑you‑mean | **PASS** | نصرر → نَصَرَ, انزلل → أَنزَلَ, كتبب → كَتَبَ, استغفرر → ٱسْتَغْفَرَ; random input (زززز) suggests nothing. |
| Root that is Quranic but never a verb | **PASS** | نَامَ → «ن و م occurs only as نَوْم، مَنَام …», with Islam360's list; hollow‑root middle radical resolved. |
| No invented forms | **PASS** | 1,080 principal parts recorded, each attested; 4,812 deliberately absent. Audit: zero cases where a 3MS indicative is attested but its part was left empty. Unattested forms render × / «قابلِ اطلاق نہیں». |
| Islam360 — connection | **PASS (this machine)** | Read from the installed app's XML: 6,349 records (6,236 ayaat + بسم الله), 2,296 roots, 2,284 لغات articles. Bismillah `n:0` and Al‑Fatiha's different division are remapped to standard numbering. |
| Islam360 — curated verbs | **PASS** | 84/84 found; 81/84 roots in Islam360 (ر و ي and ك س ر are textbook verbs the Quran never uses — the app says so). 287/287 curated occurrences confirmed word‑for‑word. One error found and removed: 27:22 يَقِينٍ (noun, ي ق ن) was filed under وَقَى. |
| Islam360 — index verbs | **PASS** | 5,389 of 5,463 cited occurrences (98.6 %) confirmed word‑for‑word; 36 root‑at‑ayah only; 38 words Islam360 has not root‑tagged; 0 ayaat Islam360 lacks. 1,435 of 1,472 verbs fully confirmed; 930 of 941 roots resolve (the 11 others are quadriliterals / rarities Islam360 analyses differently). |
| Islam360 — honesty of labelling | **PASS** | ✓ shown per ayah only when Islam360's own tagging agrees. Text, translations, surah names and لغات labelled Islam360; صیغہ labelled as morphology. Root‑wide lists shown only folded away and labelled not صیغہ‑analysed; never in the PDF. |
| Islam360 — public deployment | **READY, pending permission** | The index is copyrighted and git‑ignored. A deployment fetches it once from a private URL via the `ISLAM360_INDEX_URL` + `ISLAM360_INDEX_TOKEN` secrets (gzip accepted, fails soft). Serving Islam360's data to others still needs Islam360's permission. |
| Arabic + harakat keyboard | **PASS** | 37 letters, 9 harakat, controls, live preview. Browser‑tested at 390 px: opens, keys fill the box, search runs, no horizontal overflow. |
| گردان — 14 صیغے, four mandatory forms | **PASS** | All 84 curated verbs; index verbs show only attested forms and say so. |
| Baab detection | **PASS** | باب from the corpus VF tag for index verbs; curated باب verified; all of 1–10 represented. |
| All Af'aal by root | **PASS** | Section ⑥ lists every attested باب of the root; unattested abwaab show ×. |
| PDF | **PASS** | 124 verbs × 2 PDFs opened with PyMuPDF: no zero‑page or blank‑page output. Ayah page carries Islam360 text, both translations, word, صیغہ and «اسلام۳۶۰ سے تصدیق شدہ» when confirmed. |
| UI — Streamlit harness | **PASS** | 124 verbs (84 curated + 40 index) swept: 0 exceptions, all sections present, Islam360 panel present. |
| UI — real browser (Chrome) | **PASS** | 20/20 checks on 1280 px desktop and 390 px phone: verb page, Quranic section with per‑ayah ✓, PDF buttons, did‑you‑mean click, نَامَ explanation, Latin input message, abwaab page, English mode, keyboard flow, no overflow. |
| Interface language | **PASS** | English mode shows English only (labels, صیغہ, meanings, translations, notices, باب names, keyboard help); Urdu mode Urdu only; Arabic mode Arabic labels with both glosses since no Arabic gloss exists. Verified in Chrome for all three. |
| Invalid input | **PASS** | 16 inputs (empty, spaces, Latin, digits, punctuation, single letters, RTL marks, 300 chars, lone ٱ) — 0 crashes, each with a message. |
| Performance | **PASS** | Cold analyzer init ≈ 0.1 s; warm search ≈ 1 ms; index and Islam360 data loaded once per process. |
| Unit tests | **PASS** | 165 tests, all passing (`tests.test_analyzer tests.test_ui tests.test_quran_index`). |
| GitHub push | **BLOCKED (credential)** | 9 commits ready on `main`; `git push origin main` needs the owner's GitHub sign‑in. |

## Remaining limitations, stated plainly

* 74 index occurrences (1.4 %) carry no ✓ because Islam360 itself has not
  root‑tagged that word or analyses the root differently. They are shown
  without the mark rather than with a fake one.
* 11 of 941 roots do not resolve in Islam360 (طمأن، زلزل، كبكب، حصحص …); the
  verb page still works, without لغات.
* 15 curated verbs are textbook forms with no occurrence in their باب
  (كَتَّبَ، اِنْكَتَبَ، اِسْتَكْتَبَ، أَضْرَبَ …). Both the corpus and Islam360
  agree they are absent; the app states this and offers the root's other
  Quranic words separately.
* Islam360 verification exists only where its data does. Without the index
  the app is honest about running on the corpus + Tanzil fallback.
