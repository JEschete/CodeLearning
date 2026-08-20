# Reference Library Audit — `Education/`

**Audited:** 2026-08-20 · **Scope:** 51 PDFs across 39 course folders (12 folders are empty) · **Total on disk:** ~1.6 GB

Goal assumed: a **permanent reference library**, not coursework support. Recommendations therefore favor books
worth *keeping and returning to* over books that were merely assigned.

**How quality was measured:** every PDF was probed with `pdfinfo` / `pdftotext` / `pdfimages` (page count,
extractable characters per page, KB per page, image codec, page geometry, producer chain), and suspect files were
rendered to PNG and read directly. "No text layer" = 0 extractable characters, i.e. an image-only scan that cannot
be searched, copied, or indexed.

---

## 1. Scoreboard

| Status | Count |
|---|---|
| Empty course folders (no book at all) | **12** |
| Books superseded by a newer edition | **14** |
| Poor-quality files worth replacing | **11** |
| Redundant duplicates / same book twice | **4 pairs** |
| Misfiled | **1** |
| Good as-is, current edition, clean file | **21** |

---

## 2. Missing books — 12 empty folders

### Stevens (graduate)

#### `AAI627 — Data Acquisition, Modeling and Analysis`

| Pick | Book | Why |
|---|---|---|
| **Primary** | **An Introduction to Statistical Learning, with Applications in Python** — James, Witten, Hastie, Tibshirani, Taylor (2023) | The single best entry point to applied statistical modeling. Free legal PDF at statlearning.com. |
| Depth | **The Elements of Statistical Learning**, 2e — Hastie, Tibshirani, Friedman (2009) | The mathematical version of the above. Free legal PDF from Stanford. |
| Tooling | **Python for Data Analysis**, 3e — Wes McKinney (2022) | pandas/NumPy reference by pandas' author. Free online. |

#### `AAI628 — Data Acquisition & Deep Learning`

| Pick | Book | Why |
|---|---|---|
| **Primary** | **Understanding Deep Learning** — Simon Prince (MIT Press, 2023) | Best modern single volume — covers transformers, diffusion, RL. Free PDF from the author. |
| Canon | **Deep Learning** — Goodfellow, Bengio, Courville (2016) | Still the theory reference, though pre-transformer. Free at deeplearningbook.org. |
| Hands-on | **Dive into Deep Learning (D2L)** — Zhang, Lipton, Li, Smola (Cambridge UP, 2023) | Every equation has runnable PyTorch next to it. Free. |

#### `CPE517 — Digital and Computer Systems Architecture`

| Pick | Book | Why |
|---|---|---|
| **Primary** | **Computer Architecture: A Quantitative Approach**, 6e — Hennessy & Patterson (2017) | The graduate companion to the Patterson & Hennessy you already own. This is *the* architecture reference. |
| Alt | **Digital Design and Computer Architecture, RISC-V Edition** — Harris & Harris (2021) | Bridges gates → microarchitecture in one book; complements your Floyd/Tocci digital texts. |

#### `CPE552 — Engineering Programming: Java`

| Pick | Book | Why |
|---|---|---|
| **Primary** | **Effective Java**, 3e — Joshua Bloch (2018) | The one Java book that stays useful for decades. Pure reference value. |
| Reference | **Core Java, Volumes I & II**, 13e — Horstmann (2024, Java 21) | The comprehensive language/library reference. |

*(You already have Liang 11e for the introductory layer — see §3.)*

#### `CPE555 — Real-Time and Embedded Systems`

| Pick | Book | Why |
|---|---|---|
| **Primary** | **Hard Real-Time Computing Systems**, 3e — Giorgio Buttazzo (2011) | The scheduling-theory canon: RM, EDF, priority inversion, resource protocols. Nothing has replaced it. |
| Practical | **Making Embedded Systems**, 2e — Elecia White (O'Reilly, 2024) | How embedded work is actually done — architecture, drivers, debugging. |
| Systems | **Computers as Components**, 5e — Marilyn Wolf (2022) | Ties embedded software to the hardware platform. |
| Free | **Mastering the FreeRTOS Real Time Kernel** — Richard Barry | Free from FreeRTOS.org; pairs with your AVR book. |

#### `CPE593 — Applied Data Structures and Algorithms`

| Pick | Book | Why |
|---|---|---|
| **Primary** | **Introduction to Algorithms (CLRS)**, 4e — Cormen, Leiserson, Rivest, Stein (2022) | The reference. 4e adds ML-adjacent and matching material. |
| Practical | **The Algorithm Design Manual**, 3e — Skiena (2020) | The "war stories" + catalog half is what you'll actually reach for. |

*(Your Weiss C++ copy is 3e and a bad photocopy — see §3 and §4.)*

#### `EE551 — Engineering Programming: Python`

| Pick | Book | Why |
|---|---|---|
| **Primary** | **Fluent Python**, 2e — Luciano Ramalho (2022) | The keeper. Data model, descriptors, async, typing — the book you re-open years later. |
| Compact | **Python Distilled** — David Beazley (2021) | A tight, high-signal core-language reference. |

*(Your two CMPS 150 Python books are 2013/2016 intro texts — fine for beginners, not reference material.)*

#### `EE605 — Probability and Statistics`

| Pick | Book | Why |
|---|---|---|
| **Primary** | **Introduction to Probability**, 2e — Blitzstein & Hwang (2019) | Best modern treatment; free PDF, and the Harvard Stat 110 lectures are free too. |
| Engineering | **Probability and Statistics for Engineers and Scientists**, 9e — Walpole, Myers, Myers, Ye | Covers the applied-statistics side (CIs, hypothesis testing, regression, DOE) that your EECE 380 books skip. |

⚠️ You already own **Papoulis 4e** and **Yates & Goodman 3e** under `EECE/380`. Those cover the probability half well.
Buy for the **statistics** half only.

#### `EE608 — Applied Modeling and Optimization`

| Pick | Book | Why |
|---|---|---|
| **Primary** | **Convex Optimization** — Boyd & Vandenberghe (2004) | The canon. Free PDF from Stanford, plus free lecture videos. |
| Numerical | **Numerical Optimization**, 2e — Nocedal & Wright (2006) | The algorithms behind every solver you'll call. |
| OR side | **Introduction to Operations Research**, 11e — Hillier & Lieberman (2021) | LP/IP/network flow/queueing — the modeling half of the course title. |

### ULL (undergraduate)

#### `CompSci/453 — Intro to Software Methodology`

| Pick | Book | Why |
|---|---|---|
| **Primary** | **A Philosophy of Software Design**, 2e — John Ousterhout (2021) | Short, dense, genuinely changes how you decompose systems. Best value per page in the category. |
| Classic | **The Pragmatic Programmer**, 20th Anniversary Ed. — Hunt & Thomas (2019) | Craft-level reference that ages well. |
| Textbook | **Software Engineering**, 10e — Ian Sommerville (2015) | If you want the formal process / requirements / V&V coverage the course actually taught. |
| Reference | **Design Patterns** — Gamma, Helm, Johnson, Vlissides (1994) | Dated examples, permanent vocabulary. |

#### `EECE/233 — Telecommunications`

| Pick | Book | Why |
|---|---|---|
| **Primary** | **Computer Networking: A Top-Down Approach**, 8e — Kurose & Ross (2020) | If "telecom" meant networks/protocols. The standard, and it's readable. |
| Alt | **Data and Computer Communications**, 10e — Stallings (2013) | If the course leaned toward transmission, multiplexing, and the link layer. |
| ⭐ Given your EW focus | **Wireless Communications: Principles and Practice**, 3e — Rappaport (2024) | Propagation, fading, link budgets — directly useful alongside your EW shelf. |

#### `EECE/433 — Machine Learning`

| Pick | Book | Why |
|---|---|---|
| **Primary** | **Probabilistic Machine Learning: An Introduction** — Kevin Murphy (2022) | The most complete modern reference; free PDF. Volume 2 (*Advanced Topics*, 2023) is also free. |
| Hands-on | **Hands-On Machine Learning with Scikit-Learn, Keras & TensorFlow**, 3e — Géron (2022) | The practical counterpart. |
| Classic | **Pattern Recognition and Machine Learning** — Bishop (2006) | Still the best Bayesian / graphical-models treatment. Free PDF from Microsoft Research. |

⚠️ Heavy overlap with `AAI628`. Pick **one** deep-learning book and **one** classical-ML book across both folders
rather than four.

---

## 3. Superseded editions

Ordered by how much the new edition actually matters.

| Folder | What you have (full title) | Current edition (full title) | Worth upgrading? |
|---|---|---|---|
| `EECE/459` | **Computer Organization and Design: The Hardware/Software Interface**, 4th ed. (MIPS) — Patterson & Hennessy (2012) *and* 5th ed. (MIPS), 2014 | **Computer Organization and Design RISC-V Edition: The Hardware Software Interface**, 2nd ed. — Patterson & Hennessy (Morgan Kaufmann, 2020) | ⭐⭐⭐ **Yes.** The ISA change is the point — RISC-V is what industry and every modern course use now. Adds domain-specific architectures. Replaces both files. |
| `CompSci/Misc` | **Operating System Concepts**, 8th ed. — Silberschatz, Galvin & Gagne (Wiley, 2008) | **Operating System Concepts**, 10th ed. — Silberschatz, Galvin & Gagne (Wiley, 2018) | ⭐⭐⭐ **Yes.** Your copy predates modern Linux/Android/iOS, NVMe, and containers. Also a bad scan (§4). |
| `EECE/452` | **Modern Digital and Analog Communication Systems**, 4th ed. — Lathi & Ding (Oxford, 2009) — ×2 copies | **Modern Digital and Analog Communication Systems**, 5th ed. — Lathi & Ding (Oxford, 2018) | ⭐⭐⭐ **Yes.** 5e is native digital, adds MATLAB throughout, and kills both bad scans at once. |
| `CompSci/Misc/Cpp` | **Data Structures and Algorithm Analysis in C++**, 3rd ed. — Mark Allen Weiss (Pearson, 2006) | **Data Structures and Algorithm Analysis in C++**, 4th ed. — Mark Allen Weiss (Pearson, 2013) | ⭐⭐⭐ **Yes.** 4e is C++11-modernized; your 3e is also a degraded photocopy (§4). |
| `EECE/260` | **Applied Numerical Methods with MATLAB for Engineers and Scientists**, 3rd ed. — Steven C. Chapra (McGraw-Hill, 2012) | **Applied Numerical Methods with MATLAB for Engineers and Scientists**, 5th ed. — Steven C. Chapra (McGraw-Hill, 2023) | ⭐⭐ Yes — MATLAB syntax and toolbox usage drifted a lot across those editions. |
| `Electronic Warfare/Radar` | **Introduction to Airborne Radar**, 2nd ed. — George W. Stimson (SciTech, 1998) | **Stimson's Introduction to Airborne Radar**, 3rd ed. — Stimson, Griffiths, Baker, Adamy & Adamy (SciTech/IET, 2014) | ⭐⭐⭐ **Yes.** Near-total rewrite — Griffiths, Baker, and Adamy joined; expanded to 744 pages with modern AESA/EW content. Big upgrade for your interests. |
| `EECE/353` | **Microelectronic Circuits**, 7th ed. — Sedra & Smith (Oxford, 2014) | **Microelectronic Circuits**, 8th ed. — Sedra, Smith, Carusone & Gaudet (Oxford, 2020) | ⭐⭐ Yes if convenient — 8e is restructured and trimmed, with updated CMOS process nodes. |
| `EECE/461` | **Feedback Control of Dynamic Systems**, 7th ed. — Franklin, Powell & Emami-Naeini (Pearson, 2015) — US *and* Global Edition | **Feedback Control of Dynamic Systems**, 8th ed. — Franklin, Powell & Emami-Naeini (Pearson, 2019) | ⭐⭐ Yes — and it lets you collapse the duplicate pair. |
| `CompSci/Misc` *(misfiled)* | **Distribution System Modeling and Analysis**, 4th ed. — William H. Kersting (CRC Press, 2017) | **Distribution System Modeling and Analysis with MATLAB® and WindMil®**, 5th ed. — Kersting & Kerestes (CRC Press, 2022) | ⭐⭐ Yes if you care about distribution — 5e adds EV loads and a corrected tape-shield cable model. |
| `Math/350` | **Elementary Differential Equations**, 11th ed. — Boyce & DiPrima (Wiley, 2017) | **Elementary Differential Equations**, 12th ed. — Boyce, DiPrima & Meade (Wiley, 2021) | ⭐ Marginal. 11e is perfectly good. Skip unless free. |
| `Math/270_301_302` | **Calculus: Early Transcendentals**, 11th ed. — Anton, Bivens & Davis (Wiley, 2016) | **Calculus: Early Transcendentals**, 12th ed. — Anton, Bivens & Davis (Wiley, 2021) | ⭐ Marginal. Skip. |
| `Math/362` | **Elementary Linear Algebra: Applications Version**, 11th ed. — Anton & Rorres (Wiley, 2014) | **Elementary Linear Algebra: Applications Version**, 12th ed. — Anton, Rorres & Kaul (Wiley, 2019) | ⭐ Marginal. Skip — see §6 for a better *addition*. |
| `201_202` | **Fundamentals of Physics, Extended**, 10th ed. *and* 11th ed. — Halliday, Resnick & Walker (Wiley, 2013 / 2018) | **Fundamentals of Physics**, 12th ed. — Halliday, Resnick & Walker (Wiley, 2021) | ⭐ Marginal. Delete the 10e, keep the 11e. |
| `EECE/355_356` | **Fundamentals of Electric Circuits**, 6th ed. — Alexander & Sadiku (McGraw-Hill, 2016) | **Fundamentals of Electric Circuits**, 7th ed. — Alexander & Sadiku (McGraw-Hill, 2021) | ⭐ Marginal. 6e is fine. |
| `EECE/344` | **Fundamentals of Applied Electromagnetics**, 7th ed. — Ulaby & Ravaioli (Pearson, 2015) | **Fundamentals of Applied Electromagnetics**, 8th ed. — Ulaby & Ravaioli (Pearson, 2020) | ⭐ Marginal. |
| `Misc/201` | **Statics and Mechanics of Materials**, 5th ed. — Russell C. Hibbeler (Pearson, 2017) | **Statics and Mechanics of Materials**, 6th ed. — Russell C. Hibbeler (Pearson, 2021) | ⭐ Marginal (mostly new problem sets). |
| `CompSci/260_261` | **Introduction to Java Programming and Data Structures, Comprehensive Version**, 11th ed., Global Edition — Y. Daniel Liang (Pearson, 2018) | **Introduction to Java Programming and Data Structures**, 13th ed. — Y. Daniel Liang (Pearson, 2023, Java 18) | ⭐ Marginal for reference use; get *Effective Java* instead (§2). |
| `CompSci/150` | **Python for Everyone**, 2nd ed. — Horstmann & Necaise (Wiley, 2016) | **Python for Everyone**, 3rd ed. — Horstmann & Necaise (Wiley, 2020) | ⭐ Marginal. Both are intro-level. |

### Already at current edition — no action

| Folder | Full title, edition and authors |
|---|---|
| `EECE/240` | **The Designer's Guide to VHDL**, 3rd ed. — Peter J. Ashenden (Morgan Kaufmann, 2008) |
| `EECE/240` | **Digital Systems: Principles and Applications**, 12th ed. — Tocci, Widmer & Moss (Pearson, 2017) |
| `EECE/140` | **Digital Fundamentals**, 11th ed., Global Edition — Thomas L. Floyd (Pearson, 2015) |
| `EECE/335` | **Fundamentals of Semiconductor Devices**, 2nd ed. — Betty Lise Anderson & Richard L. Anderson (McGraw-Hill, 2018) |
| `EECE/444` | **Signals and Systems: Analysis Using Transform Methods and MATLAB**, 3rd ed. — Michael J. Roberts (McGraw-Hill, 2018) |
| `EECE/380` | **Probability, Random Variables and Stochastic Processes**, 4th ed. — Papoulis & Pillai (McGraw-Hill, 2002) |
| `EECE/380` | **Probability and Stochastic Processes: A Friendly Introduction for Electrical and Computer Engineers**, 3rd ed. — Yates & Goodman (Wiley, 2014) |
| `EECE/Misc` | **The Art of Electronics**, 3rd ed. — Horowitz & Hill (Cambridge University Press, 2015) |
| `CompSci/341` | **Discrete Structures, Logic, and Computability**, 4th ed. — James L. Hein (Jones & Bartlett, 2017) |
| `CompSci/Misc/C` | **The C Programming Language**, 2nd ed. — Kernighan & Ritchie (Prentice Hall, 1988) |
| `CompSci/Misc/C` | **C Programming: A Modern Approach**, 2nd ed. — K. N. King (W. W. Norton, 2008) |
| `Math/Misc` | **A Transition to Advanced Mathematics**, 8th ed. — Smith, Eggen & St. Andre (Cengage, 2014) |
| `Math/Misc` | **Probability and Statistics with R**, 2nd ed. — Ugarte, Militino & Arnholt (CRC Press, 2015) |
| `Misc/430` | **Fundamentals of Engineering Economics**, 4th ed. — Chan S. Park (Pearson, 2019) |
| `EW Fundamentals` | **Electronic Warfare and Radar Systems Engineering Handbook**, 4th ed. — NAWCWD TP 8347 (Naval Air Warfare Center Weapons Division, 2013) |
| `EW Fundamentals` | **EW 101: A First Course in Electronic Warfare** — David L. Adamy (Artech House, 2001) |
| `EW Fundamentals` | **EW 102: A Second Course in Electronic Warfare** — David L. Adamy (Artech House, 2004) |
| `EW Fundamentals` | **EW 103: Tactical Battlefield Communications Electronic Warfare** — David L. Adamy (Artech House, 2008) |
| `EW Fundamentals` | **EW 104: Electronic Warfare Against a New Generation of Threats** — David L. Adamy (Artech House, 2015) |
| `EW Fundamentals` | **EW 105: Space Electronic Warfare** — David L. Adamy (Artech House, 2021) |

---

## 4. Poor-quality files

Ranked worst first. "No text layer" means the PDF is pure images — unsearchable, uncopyable, and invisible to any
indexing tool.

### 🔴 Critical — replace these

**1. `Math/Misc_ClassesIDidntTake/Math 360 - A Transition to Advanced Mathematics.pdf`** — *the worst file in the library*
`134 MB · 450 pp · 305 KB/page · ~285 chars/page`

This is not a scan of a book — it's a stack of **browser screenshots of the VitalSource web reader**, printed to PDF.
Every page carries a `4/20/2018` timestamp, a `https://cengagebrain.vitalsource.com/#/books/9781305177192/...` footer,
a `6/10` print counter, and a DRM watermark line. The actual book content occupies roughly the top 40% of each page;
the rest is white space. Text is a low-resolution raster.

→ **Replace with a proper copy of Smith, Eggen & St. Andre, *A Transition to Advanced Mathematics*, 8e.**
→ Free alternative worth having regardless: **Hammack, *Book of Proof*, 3e** (free PDF, richmond.edu) — arguably better for self-study.

**2. `CompSci/Misc/Programming Languages/C/C Programming a Modern Approach.pdf`**
`102 MB · 830 pp · 125 KB/page · no text layer · RGB JPEG at 1072×1517 pt`

King 2e. The scan itself is clean and legible, but it is 100% images — you cannot search it, and it's oversized by
roughly 20×. For a book you'd use as a C reference, unsearchable is close to unusable.
→ **Replace with a native-text edition.**

**3. `EECE/447_450/EECE 447_450 Power Systems Analysis.pdf`**
`27 MB · 720 pp · no text layer · CCITT G4 from a Toshiba e-STUDIO copier`

Grainger & Stevenson. Photocopier output with visible spine-gutter shadows down one edge, and the front-matter pages
have **corrupt CCITT data** (rows decode to the wrong length and render as noise). Body pages are legible.
→ Grainger & Stevenson (1994) was never revised. **Better move: switch to Glover, Overbye, Sarma & Birchfield,
*Power System Analysis and Design*, 7e** — actively maintained and better on modern grid topics.

**4. `EECE/452/EECE 452 - Digital and Analog Communication Systems 4e.pdf`**
`11 MB · 926 pp · no text layer · JBIG2 from a Canon iR7105`

**Mislabeled.** The copyright page reads *"Modern digital and analog communication systems / B. P. Lathi, Zhi Ding — 4th ed.,
ISBN 978-0-19-538493-2"* — identical ISBN to the other file in the same folder. This is a **duplicate of Lathi 4e**, and the
worse of the two copies. → Delete; upgrade to **Lathi & Ding 5e**.

**5. `EECE/340/EECE 340 - AVR Microcontroller and Embedded Systems 1e.pdf`**
`43 MB · 781 pp · no text layer · CCITT G4`

Mazidi. Bilevel scan, genuinely crisp and readable, but zero text layer — you can't search for a register name, which is
the entire reason to keep a microcontroller book. → Replace with a text-layer copy, or OCR this one.

**6. `EECE/Misc/Laboratory Explorations for Microelectronic Circuits.pdf`**
`3.3 MB · 146 pp · no text layer · JBIG2 stencil via CVISION PdfCompressor`

Aggressively compressed lab manual, no OCR. Low stakes (it's a supplement to Sedra & Smith), but it's the lowest-fidelity
file here after #1. → Low priority; delete or replace when you upgrade Sedra & Smith to 8e.

### 🟡 Degraded but usable

**7. `CompSci/Misc/Programming Languages/Cpp/Data Structures and Algorithm Analysis in C++.pdf`**
`14.5 MB · 602 pp · JBIG2 photocopy, Toshiba e-STUDIO352`

Weiss **3e**. Grey, low-contrast, slightly skewed pages. It *has* an OCR layer, but the OCR is mangled — the copyright
page extracts as `\\leiss, Mark Allen ... ivlark Allen \Vdss ~Jrd cd`, so search results will be unreliable.
→ Double hit: bad scan **and** outdated (§3). Replace with **Weiss 4e**.

**8. `Misc/430-EconomicsForEngineers/Fundamentals of Engineering Economics.pdf`**
`105 MB · 1447 pp · calibre 3.26 EPUB→PDF conversion`

Not a scan, but a **lossy reflow**. The original page design is gone, replaced by generic sans-serif body text at roughly
one book page per two PDF pages. Figures are rasterized, and cross-references render as dead text with stray glyphs
(*"In Section 11.4 🖥"*). For engineering economics specifically this matters — the **interest-factor tables** are the part
you'd actually look things up in, and reflow is exactly what destroys wide tables.
→ Content is current (Park 4e); **re-acquire as a native publisher PDF.**

**9. `EECE/380/EECE 380 - Book 2 - Probability and Stochastic Processes 3e.pdf`**
`110 MB · 513 pp · 219 KB/page · Acrobat Paper Capture OCR at 1180×1463 pt`

Yates & Goodman. OCR'd and readable, but scanned at absurd resolution — 110 MB for a 500-page book is ~10× larger than
it needs to be. → Cosmetic. Re-download, or run it through a downsampling optimizer if disk space matters.

**10. `Electronic Warfare/EW Fundamentals/EW 101 - A first course in Electronic Warfare.pdf`**
`70 MB · 330 pp · 217 KB/page · Acrobat Paper Capture OCR`

Same story: greyish grayscale scan, legible with a working OCR layer, but ~15× oversized. Note this is the largest file in
your EW folder and the *only* one that's a scan — EW 102–105 are all clean native PDFs. → Cosmetic.

**11. `EECE/335/EECE 335 - Fundamentals of Semiconductor Devices 2nd Ed.pdf`**
`44 MB · calibre 3.32 EPUB→PDF conversion`

Body text is vector and clean, but **inline equations are rasterized as small boxed images** — a classic calibre artifact.
They won't scale cleanly and can't be copied. It also mixes in the online supplement chapters (S1.x) without clear separation.
→ Usable; upgrade opportunistically. Edition is current.

---

## 5. Duplicates and filing

| Folder | Issue | Action |
|---|---|---|
| `ULL/201_202-PhysicsI_II/` | `Fundamentals of Physics 10th Extended.pdf` (31 MB) **and** `Fundamentals of Physics 11ed.pdf` (40 MB) | **Delete the 10e.** The 11e supersedes it and is the better file. *(The 10e is a fine vector PDF, just at a small 252 pt trim size.)* |
| `ULL/EECE/461-ControlSystems/` | `Feedback Control of Dynamic Systems 7e.pdf` (US) **and** `Feedback Control of Dynamic Systems.pdf` (**7e Global Edition**) | Same edition, two printings. **Delete the Global Edition** (renumbered problems, no content gain) — or delete both and get 8e. |
| `ULL/EECE/459-ComputerHardwareDesign/` | `Computer Organizationand Design.pdf` (**4e**, 2012) **and** `... 5e.pdf` | **Delete the 4e.** Confirmed via its Library of Congress page. Then replace the 5e with the RISC-V 2e. |
| `ULL/EECE/452-CommunicationsEngineering/` | Both files are **Lathi & Ding 4e**, same ISBN, one page offset apart — verified by rendering p.277/278 of each | **Delete `Digital and Analog Communication Systems 4e.pdf`** (no text layer). Keep the OCR'd `Modern...(1).pdf` until you get 5e. |
| `ULL/CompSci/Misc/Distributed Modeling and Analysis.pdf` | **Misfiled.** This is Kersting, ***Distribution* System Modeling and Analysis, 4e** — a power-distribution engineering text, not a distributed-computing book. The filename dropped the "-ution". | **Move to `ULL/EECE/447_450-ElectricalMachinesAndPower_PowerSystems/`** and rename to `Distribution System Modeling and Analysis 4e.pdf`. |

**Reclaimable space from duplicates alone: ~87 MB.** Full cleanup of §4 + §5 would cut roughly 450 MB.

---

## 6. Better books for subjects you already cover

Not replacements — these are the volumes that earn permanent shelf space in a reference library.

| Subject | You have | Add |
|---|---|---|
| **DSP** `EECE/430` | Smith, *Scientist and Engineer's Guide to DSP* | ⭐ **Lyons, *Understanding Digital Signal Processing*, 3e** — the best practitioner's DSP book, and the natural next step from Smith. Then **Oppenheim & Schafer, *Discrete-Time Signal Processing*, 3e** for rigor. Your current book is free and intuition-building but has no real depth. |
| **Radar / EW** | Adamy EW 101–105, Stimson 2e, NAWCWD Handbook | ⭐ **Richards, Scheer & Holm, *Principles of Modern Radar* (Vol. I–III)** — the modern working radar reference. Plus **Balanis, *Antenna Theory: Analysis and Design*, 4e** — you have no antenna book at all, which is a real gap given the rest of this shelf. |
| **Control** `EECE/461` | Franklin 7e | ⭐ **Åström & Murray, *Feedback Systems*, 2e (2021)** — free PDF from Caltech, and a genuinely different, systems-level perspective. |
| **Linear Algebra** `Math/362` | Anton 11e | ⭐ **Strang, *Introduction to Linear Algebra*, 6e** (with the free MIT 18.06 lectures) and **Axler, *Linear Algebra Done Right*, 4e** (free PDF). Anton is a fine course text; neither of these is. |
| **Theory / Discrete** `CompSci/341` | Hein 4e | ⭐ **Sipser, *Introduction to the Theory of Computation*, 3e** — the standard for the automata/computability half. **Graham, Knuth & Patashnik, *Concrete Mathematics*** if you want a keeper. |
| **Operating Systems** | Silberschatz 8e (bad scan) | ⭐ **Arpaci-Dusseau, *Operating Systems: Three Easy Pieces*** — free, and better written than Silberschatz. Get this even if you also upgrade to OS Concepts 10e. |
| **C** | K&R 2e, King 2e | ⭐ **Gustedt, *Modern C*, 2e** — free PDF, covers C17/C23. K&R is C89 and 38 years old; it's a classic, not a current reference. |
| **C++** | Weiss (data structures only) | ⭐ **Stroustrup, *A Tour of C++*, 3e (C++20)** — you have no C++ *language* book at all, only an algorithms book that happens to use C++. |
| **Algorithms** | Weiss 3e | ⭐ **CLRS 4e** (see §2, `CPE593`). |
| **Analog / Microelectronics** `EECE/353` | Sedra & Smith 7e, Art of Electronics 3e | ⭐ **Gray, Hurst, Lewis & Meyer, *Analysis and Design of Analog Integrated Circuits*, 5e** — the IC-design reference. Also **Horowitz & Hill, *The Art of Electronics: The x-Chapters* (2020)** — the deep-dive companion to the 3e you own. |
| **Semiconductors** `EECE/335` | Anderson 2e | ⭐ **Sze & Lee, *Physics of Semiconductor Devices*, 4e** — the device-physics reference. |
| **Nonlinear / Dynamics** `Math/350` | Boyce 11e | ⭐ **Strogatz, *Nonlinear Dynamics and Chaos*, 2e** — the best-written applied math book on this list. |
| **Numerical Methods** `EECE/260` | Chapra 3e | ⭐ **Press et al., *Numerical Recipes*, 3e** — as a lookup reference for algorithms, not a course text. |
| **Physics** `201_202` | Halliday 11e | ⭐ **The Feynman Lectures on Physics** — free and authorized online at Caltech. Reference-library essential. |
| **Digital Design** `EECE/140`, `240` | Floyd 11e, Tocci 12e, Ashenden VHDL 3e | ⭐ **Harris & Harris, *Digital Design and Computer Architecture, RISC-V Edition*** — bridges your digital-logic shelf to your computer-architecture shelf, which currently have nothing connecting them. |

---

## 7. Suggested order of work

**Do first — fixes that cost nothing:**

1. Delete 4 redundant duplicates (§5) — Physics 10e, Feedback Control Global, COD 4e, the mislabeled Lathi scan. *(~87 MB)*
2. Move and rename the misfiled Kersting book out of `CompSci/Misc/` (§5).

**Do next — highest quality-of-life gain per download:**

3. `Math 360` — replace the VitalSource screenshot file. It's the only genuinely unpleasant file to read.
4. `C: A Modern Approach` — get a searchable copy.
5. `Operating System Concepts` — 8e scan → 10e native. Fixes an edition gap *and* a quality problem at once.
6. `Weiss C++` — 3e photocopy → 4e native. Same double win.
7. `Lathi & Ding` — 4e scan → 5e native. Same double win.

**Then — fill the gaps that matter for where you're actually headed:**

8. `EECE/433` + `AAI628` → **Understanding Deep Learning** (free) and **Murphy PML** (free). Zero cost.
9. `EE608` → **Boyd & Vandenberghe** (free).
10. `CPE593` → **CLRS 4e**.
11. `EECE/233` → **Rappaport 3e**, given the EW shelf.
12. Radar → **Stimson 3e** and **Balanis, *Antenna Theory***.

**Free and worth grabbing regardless** (all legal author/publisher PDFs):
*Understanding Deep Learning* · *Probabilistic Machine Learning* I & II · *An Introduction to Statistical Learning* ·
*The Elements of Statistical Learning* · *Convex Optimization* · *Operating Systems: Three Easy Pieces* ·
*Feedback Systems* (Åström & Murray) · *Linear Algebra Done Right* 4e · *Modern C* 2e · *Book of Proof* ·
*Dive into Deep Learning* · *The Feynman Lectures* · *Pattern Recognition and Machine Learning*

---

## Appendix — full inventory

| Folder | File | Pages | Size | File quality |
|---|---|---|---|---|
| `EW/EW Fundamentals` | EW 101 — Adamy | 330 | 70 MB | 🟡 OCR'd scan, oversized |
| `EW/EW Fundamentals` | EW 102 | 291 | 7.7 MB | 🟢 native |
| `EW/EW Fundamentals` | EW 103 | 348 | 5.5 MB | 🟢 native |
| `EW/EW Fundamentals` | EW 104 | 491 | 18 MB | 🟢 native (calibre, clean) |
| `EW/EW Fundamentals` | EW 105 — Space EW | 247 | 20 MB | 🟢 native |
| `EW/EW Fundamentals` | EW & Radar Systems Handbook 4e (NAWCWD) | 455 | 6.5 MB | 🟢 native |
| `EW/Radar` | Intro to Airborne Radar **2e** — Stimson | 570 | 14 MB | 🟢 native · ⬆ 3e exists |
| `ULL/201_202` | Fundamentals of Physics **10e** Ext. | 1450 | 31 MB | 🟢 native · ♻ duplicate |
| `ULL/201_202` | Fundamentals of Physics 11e | 1452 | 40 MB | 🟢 native |
| `ULL/CompSci/150` | Intro to Programming Using Python — Liang (2013) | 582 | 8.8 MB | 🟢 native |
| `ULL/CompSci/150` | Python for Everyone **2e** — Horstmann | 759 | 21 MB | 🟢 native · ⬆ 3e |
| `ULL/CompSci/260_261` | Intro to Java Prog. & DS **11e Global** — Liang | 1711 | 24 MB | 🟢 native · ⬆ 13e |
| `ULL/CompSci/341` | Discrete Structures, Logic & Computability 4e — Hein | 1007 | 14 MB | 🟢 native (Zamzar) |
| `ULL/CompSci/Misc` | **Distribution** System Modeling & Analysis 4e — Kersting | 547 | 11 MB | 🟢 native · 📁 **misfiled** · ⬆ 5e |
| `ULL/CompSci/Misc` | Operating System Concepts **8e** | 982 | 19 MB | 🟡 JBIG2 scan · ⬆ 10e |
| `ULL/CompSci/Misc/…/C` | C Programming Language 2e — K&R | 238 | 0.9 MB | 🟡 Word-reflow, not original layout |
| `ULL/CompSci/Misc/…/C` | C: A Modern Approach 2e — King | 830 | **102 MB** | 🔴 **no text layer** |
| `ULL/CompSci/Misc/…/Cpp` | DS & Algorithm Analysis in C++ **3e** — Weiss | 602 | 14 MB | 🔴 bad photocopy, broken OCR · ⬆ 4e |
| `ULL/EECE/140` | Digital Fundamentals 11e Global — Floyd | 953 | 45 MB | 🟢 native |
| `ULL/EECE/240` | Digital Systems 12e — Tocci | 1027 | 15 MB | 🟢 native |
| `ULL/EECE/240` | Designer's Guide to VHDL 3e — Ashenden | 910 | 4.0 MB | 🟢 native |
| `ULL/EECE/260` | Applied Numerical Methods MATLAB **3e** — Chapra | 673 | 5.5 MB | 🟢 native · ⬆ 5e |
| `ULL/EECE/335` | Fundamentals of Semiconductor Devices 2e — Anderson | 1132 | 44 MB | 🟡 calibre, raster equations |
| `ULL/EECE/340` | AVR Microcontroller & Embedded Systems — Mazidi | 781 | 43 MB | 🔴 **no text layer** |
| `ULL/EECE/344` | Fundamentals of Applied Electromagnetics **7e** — Ulaby | 530 | 12 MB | 🟢 native · ⬆ 8e |
| `ULL/EECE/353` | Microelectronic Circuits **7e** — Sedra & Smith | 1489 | 53 MB | 🟢 native · ⬆ 8e |
| `ULL/EECE/355_356` | Fundamentals of Electric Circuits **6e** — Sadiku | 990 | 12 MB | 🟢 native · ⬆ 7e |
| `ULL/EECE/380` | Probability, Random Variables & Stoch. Proc. 4e — Papoulis | 861 | 26 MB | 🟡 OCR'd scan, acceptable |
| `ULL/EECE/380` | Probability & Stochastic Processes 3e — Yates & Goodman | 513 | **110 MB** | 🟡 OCR'd scan, badly oversized |
| `ULL/EECE/430` | Scientist & Engineer's Guide to DSP 2e — Smith | 664 | 12 MB | 🟢 native |
| `ULL/EECE/444` | Signals and Systems 3e — Roberts | 794 | 21 MB | 🟢 native |
| `ULL/EECE/447_450` | Power Systems Analysis — Grainger & Stevenson | 720 | 27 MB | 🔴 **no text layer**, corrupt front matter |
| `ULL/EECE/452` | "Digital and Analog Comm Systems 4e" (= **Lathi 4e**) | 926 | 11 MB | 🔴 **no text layer** · ♻ **duplicate** |
| `ULL/EECE/452` | Modern Digital & Analog Comm Systems **4e Intl** — Lathi & Ding | 927 | 30 MB | 🟡 OCR'd scan, decent · ⬆ 5e |
| `ULL/EECE/459` | Computer Organization & Design **4e** | 919 | 17 MB | 🟢 native · ♻ duplicate |
| `ULL/EECE/459` | Computer Organization & Design **5e** | 793 | 29 MB | 🟢 native · ⬆ RISC-V 2e |
| `ULL/EECE/461` | Feedback Control of Dynamic Systems **7e** | 885 | 24 MB | 🟢 native · ⬆ 8e |
| `ULL/EECE/461` | Feedback Control of Dynamic Systems **7e Global** | 881 | 36 MB | 🟢 native · ♻ duplicate |
| `ULL/EECE/Misc` | Lab Explorations for Microelectronic Circuits | 146 | 3.3 MB | 🔴 **no text layer** |
| `ULL/EECE/Misc` | The Art of Electronics 3e — Horowitz & Hill | 1225 | 29 MB | 🟢 native, excellent |
| `ULL/Math/109_110` | Precalculus 2e — Young | 1208 | 34 MB | 🟢 native |
| `ULL/Math/270_301_302` | Calculus: Early Transcendentals **11e** — Anton | 1166 | 92 MB | 🟢 native (LaTeX) · ⬆ 12e |
| `ULL/Math/350` | Elementary Differential Equations **11e** — Boyce | 625 | 16 MB | 🟢 native · ⬆ 12e |
| `ULL/Math/362` | Elementary Linear Algebra **11e** — Anton & Rorres | 802 | 8.1 MB | 🟢 native · ⬆ 12e |
| `ULL/Math/Misc` | Algebra: Form and Function — Hughes-Hallett et al. | 576 | 6.8 MB | 🟢 native |
| `ULL/Math/Misc` | Technical Mathematics with Calculus (Canadian ed.) | 1032 | 15 MB | 🟢 native |
| `ULL/Math/Misc` | Applied Calculus **5e** — Hughes-Hallett | 565 | 4.2 MB | 🟢 native · ⬆ 7e |
| `ULL/Math/Misc` | Probability and Statistics with R 2e — Ugarte | 967 | 15 MB | 🟢 native (LaTeX) |
| `ULL/Math/Misc` | A Transition to Advanced Mathematics 8e | 450 | **134 MB** | 🔴 **VitalSource screenshots — worst file** |
| `ULL/Misc/201` | Statics and Mechanics of Materials **5e** — Hibbeler | 933 | 91 MB | 🟡 good color scan, OCR'd · ⬆ 6e |
| `ULL/Misc/430` | Fundamentals of Engineering Economics 4e — Park | 1447 | **105 MB** | 🔴 calibre reflow, layout destroyed |

**Legend:** 🟢 clean native PDF · 🟡 usable but degraded · 🔴 replace · ⬆ newer edition exists · ♻ duplicate · 📁 misfiled

---

# 8. Beyond the Curriculum — 78 books to plug the real gaps

## What the library says about you

Reading the shelf rather than the folder names: you're an **ECE generalist with unusual breadth** — circuits,
electronics, EM, DSP, comms, control, power, embedded, computer architecture — who then went and got a graduate
layer in **ML, optimization, and real-time systems**. The `Electronic Warfare/` folder is the one collection nobody
assigned you; you built it yourself, which says where the curiosity points. The `Math/Misc_ClassesIDidntTake/`
folder says you collect things you *might* want later. And you're doing this now, out of school, for reference —
so the criterion is **"will I open this in five years,"** not "will this get me through a final."

**The honest gaps that follow from that:**

- You have EM theory but nothing on **RF/microwave practice**, and no **EMC/signal-integrity** book at all — the two
  things that actually decide whether hardware works.
- You have probability but nothing on **detection and estimation**, which is the mathematics underneath radar, comms,
  sensors, and tracking alike.
- You have a computer architecture book and a Java book, but **nothing connecting them** — no OS internals, no
  systems programming, no networking, no security, no databases.
- Your math is entirely **course-shaped**: no complex analysis, no numerical linear algebra, no information theory,
  no Fourier reference.
- Your physics stops at Halliday. No **electrodynamics, optics, quantum, or thermal**.
- Nothing at all on **how engineering actually goes wrong** — reliability, failure analysis, systems thinking — or on
  **writing, thinking, and the history of your own field**.

The list below is built for intuition first. Where two books cover the same ground, the one that explains *why*
wins over the one that's more complete. **🆓 = legally free from the author or publisher** (23 of the 78).

---

## A. RF & microwave — where your EM theory becomes hardware

*You own Ulaby (fields) and Sedra & Smith (low-frequency circuits). Above ~100 MHz neither applies, and that's a
cliff you'll hit in any RF, radar, comms, or high-speed-digital work.*

| Book | What it covers | Why you want it |
|---|---|---|
| **1. Microwave Engineering**, 4e — David Pozar | Transmission lines, S-parameters, Smith chart, matching networks, filters, couplers, amplifiers, noise | The RF canon. This is the book that turns Maxwell's equations into a design procedure. If you buy one book from this whole list, it's this one. |
| **2. Fundamentals of Microwave and RF Design**, 3e — Michael Steer 🆓 | Same territory as Pozar, condensed, plus a 5-volume expanded series | Free open-access from NC State (Steer got his copyrights back and released it). Cheapest possible way to find out whether you like this field before buying Pozar. |
| **3. Radio-Frequency Electronics: Circuits and Applications**, 2e — Jon Hagen | Mixers, oscillators, filters, receivers, transmitters, noise, propagation — at the physical-intuition level | The most *readable* RF book in print. Hagen explains why an intuition works before formalizing it. Perfect bridge from your Sedra & Smith background. |
| **4. RF Circuit Design**, 2e — Chris Bowick | Component behavior at RF, resonant circuits, impedance matching, small-signal amplifier design | Short, practical, and unusually clear on *why real capacitors stop being capacitors*. A working bench reference. |
| **5. The ARRL Handbook for Radio Communications** (current ed.) | Everything: RF, antennas, propagation, test equipment, construction, digital modes | The engineer's almanac. Ham-radio origins, but it's a genuinely broad practical RF reference that gets a new edition every year. |

## B. Detection & estimation — the mathematics under every sensor

*Papoulis and Yates & Goodman give you probability. Neither tells you how to decide whether a signal is present, or
how to estimate a parameter optimally. That gap sits under radar, comms, sensors, tracking, and half of ML.*

| Book | What it covers | Why you want it |
|---|---|---|
| **6. Fundamentals of Statistical Signal Processing, Vol. I: Estimation Theory** — Steven Kay | MVU estimators, Cramér–Rao bound, MLE, least squares, Bayesian estimation, Kalman filtering | The standard. Kay is unusually good at motivating each estimator with a concrete problem before deriving it. The CRB alone is worth the book — it tells you what performance is *possible* before you design anything. |
| **7. Fundamentals of Statistical Signal Processing, Vol. II: Detection Theory** — Steven Kay | Neyman–Pearson, matched filters, ROC curves, GLRT, detection of signals in noise | This is where "did I detect a target / a bit / an anomaly?" gets a rigorous answer. ROC curves show up everywhere from radar to medical imaging to ML classifiers. |
| **8. Optimal State Estimation** — Dan Simon | Kalman, extended/unscented Kalman, H∞, particle filters — with working code | The *intuitive* Kalman filter book. Simon derives it four different ways so at least one clicks. Directly useful for sensor fusion, navigation, and control. |
| **9. Estimation with Applications to Tracking and Navigation** — Bar-Shalom, Li & Kirubarajan | Multi-target tracking, data association, IMM, maneuvering targets | The tracking reference. Where Simon gives you one filter, this gives you the architecture around it when there are many targets and ambiguous measurements. |

## C. Radar, EW & software radio — depth past what you have

*Adamy's EW 101–105 is an excellent conceptual overview, but it's deliberately light on math. Stimson is systems-level.
Neither shows you the signal processing.*

| Book | What it covers | Why you want it |
|---|---|---|
| **10. Fundamentals of Radar Signal Processing**, 2e — Mark Richards | Pulse compression, Doppler processing, CFAR, MTI, SAR, tracking — the DSP layer of radar | The missing middle between Adamy's concepts and Skolnik's encyclopedia. Uses exactly the DSP and detection theory from §B, which is why they belong together. |
| **11. Radar Handbook**, 3e — Merrill Skolnik (ed.) | Every radar subsystem and mission type, chapter per topic by a specialist | The lookup reference. You don't read it; you own it for the day you need to know how a monopulse tracker or an OTH radar actually works. |
| **12. Microwave Receivers with Electronic Warfare Applications** — James Tsui | Crystal video, IFM, channelized, superhet, and compressive receivers; EW receiver tradeoffs | The classic on the *receiver* side of EW, which Adamy covers only briefly. Direct complement to what's already on your shelf. |
| **13. Software-Defined Radio for Engineers** — Collins, Getz, Pu & Wyglinski 🆓 | SDR architecture, sampling, synchronization, real hardware labs (Pluto SDR) | Free from Analog Devices. The best way to make everything in §A–§C *tangible* — a $200 SDR plus this book turns theory into captured signals on your own bench. |
| **14. Digital Communications: A Discrete-Time Approach** — Michael Rice | Modulation, pulse shaping, carrier and timing synchronization, equalization — all in DSP form | The book that actually explains how a modem is *implemented*, not just analyzed. Fills the gap between your Lathi (analysis) and any real receiver. |

## D. Navigation & GNSS

*A gap worth closing regardless of field — GNSS is where estimation theory, RF, signal processing, and relativity all
meet in one system you use daily.*

| Book | What it covers | Why you want it |
|---|---|---|
| **15. Principles of GNSS, Inertial, and Multisensor Integrated Navigation Systems**, 2e — Paul Groves | GNSS signals and receivers, INS mechanization, Kalman-based integration, error modeling | The definitive integrated-navigation book, and the best practical application of §B you'll find. Also the standard reference on GPS vulnerabilities. |
| **16. Understanding GPS/GNSS: Principles and Applications**, 3e — Kaplan & Hegarty | Signal structure, receiver design, error sources, augmentation, all constellations | The systems-level companion to Groves. Between them you'll understand GNSS end to end. |

## E. Practical electronics — the things that break real hardware

*This is your biggest silent gap. You have circuit theory and device physics; you have nothing about why a working
schematic becomes a non-working board.*

| Book | What it covers | Why you want it |
|---|---|---|
| **17. Electromagnetic Compatibility Engineering** — Henry Ott | Grounding, shielding, cable coupling, PCB layout, ESD, emissions and susceptibility | **The single most practically valuable book on this list.** Every EE eventually loses weeks to a noise problem. Ott is the reason you won't lose a month. Nothing else in your library touches this. |
| **18. High-Speed Digital Design: A Handbook of Black Magic** — Johnson & Graham | Transmission-line effects in digital systems, ringing, crosstalk, ground bounce, terminations | Your digital books (Floyd, Tocci) treat signals as ideal 1s and 0s. This is where that stops being true — above a few tens of MHz, digital *is* an RF problem. Bridges your digital and RF shelves. |
| **19. Practical Electronics for Inventors**, 4e — Scherz & Monk | Everything from passives to microcontrollers, sensors, motors, and power supplies, hands-on | The wide, practical, do-it-now book. Great for the moments when you want to build something rather than analyze it. |
| **20. Fundamentals of Power Electronics**, 3e — Erickson & Maksimović | Converter topologies, averaged modeling, magnetics design, control loops, efficiency | You own a power *systems* book (grid scale) and nothing on power *electronics* (board scale) — despite it being in every device you'll ever design. The standard text, and unusually well structured. |
| **21. Op Amp Applications Handbook** — Walt Jung / Analog Devices 🆓 | Real op-amp behavior, noise, precision design, signal conditioning, application circuits | Free from ADI. Sedra & Smith teaches ideal op-amps; this is what they actually do. The best free analog reference in existence. |
| **22. Analog Circuit Design: Art, Science and Personalities** — Jim Williams (ed.) | Essays by working analog designers on how they actually think and troubleshoot | Not a textbook — a book about *engineering judgment*. Williams was the best analog intuition writer who ever lived. Read it for how these people reason, which no textbook teaches. |

## F. Digital hardware beyond the intro

*You have Ashenden's VHDL book (excellent) and two intro digital texts. Nothing about building real hardware with them.*

| Book | What it covers | Why you want it |
|---|---|---|
| **23. FPGA Prototyping by SystemVerilog Examples**, 2e — Pong Chu | RTL coding style, testbenches, timing, working peripherals and soft-core designs on real boards | Takes you from "I know VHDL syntax" to "I've built something that runs on an FPGA." SystemVerilog also broadens you past VHDL, which matters industrially. |
| **24. The Design Warrior's Guide to FPGAs** — Clive Maxfield | What FPGAs are, how they're structured, tool flows, and where they fit versus ASICs and CPUs | Dated on specific parts, still the most *readable* explanation of the FPGA landscape. Read it first; use Chu second. |
| **25. CMOS VLSI Design: A Circuits and Systems Perspective**, 4e — Weste & Harris | Transistor-level design, logical effort, timing, power, layout, memory design | Connects your semiconductor physics (Anderson) to your computer architecture (Patterson) — the layer neither book covers. Logical effort alone is a permanently useful mental model. |

## G. How computers actually work

*You have a Java book, a Python book, and an architecture textbook. There is nothing in between — no OS internals,
no memory model, no idea what happens between your source code and the silicon.*

| Book | What it covers | Why you want it |
|---|---|---|
| **26. Computer Systems: A Programmer's Perspective**, 3e — Bryant & O'Hallaron | Machine code, memory hierarchy, linking, exceptions, virtual memory, I/O, concurrency — from a programmer's view | **The highest-value CS book you don't own.** It's the missing bridge between Patterson (hardware) and any language book (software). Explains *why* your code is slow, in terms you can act on. |
| **27. The Linux Programming Interface** — Michael Kerrisk | Every Linux/UNIX system call, with worked examples: processes, signals, IPC, files, sockets, threads | The definitive systems-programming reference, 1500 pages of it. Directly useful for embedded Linux, which is where most embedded work has gone. |
| **28. Linux Device Drivers**, 3e — Corbet, Rubini & Kroah-Hartman 🆓 | Kernel modules, char devices, interrupts, DMA, memory mapping, hardware access | Free from LWN. Written for the 2.6 kernel so the APIs have drifted, but the *concepts* are unchanged and it's the natural next step from your AVR/bare-metal background. |
| **29. The Definitive Guide to Arm Cortex-M3 and Cortex-M4 Processors**, 3e — Joseph Yiu | Cortex-M architecture, NVIC, exceptions, low power, debug, DSP instructions, CMSIS | Your only microcontroller book is 8-bit AVR. Cortex-M is what industry actually ships. Yiu is an Arm engineer and this is the clearest treatment available. |
| **30. Code: The Hidden Language of Computer Hardware and Software**, 2e — Charles Petzold | Builds a working computer from relays and logic, one idea at a time, from Morse code up | Pure intuition. You already know the material — read it anyway, because Petzold assembles it in an order that makes the whole thing feel inevitable. The 2e (2022) adds interactive online figures. |
| **31. The Elements of Computing Systems**, 2e — Nisan & Schocken | Build a computer from NAND gates to an OS: hardware, assembler, VM, compiler, OS — as projects | "nand2tetris." The single most effective way to make computing feel like one connected thing rather than twelve courses. All course material is free online. |

## H. Software craft & architecture

*You have language books, not engineering books. Nothing on how software is structured, maintained, or reasoned about.*

| Book | What it covers | Why you want it |
|---|---|---|
| **32. Designing Data-Intensive Applications**, 2e — Kleppmann & Riccomini (2026) | Storage engines, replication, partitioning, transactions, consistency, consensus, stream processing | The best systems book of the last decade, and the 2e substantially rewrote the consistency and consensus material. Explains distributed-systems tradeoffs so clearly that it works as a *thinking* book, not just a reference. |
| **33. Working Effectively with Legacy Code** — Michael Feathers | Dependency-breaking techniques, seams, characterization tests, safely changing untested code | Every real codebase is legacy code. This is the only book that treats "how do I change this safely" as a discipline with named techniques. |
| **34. The Mythical Man-Month** — Fred Brooks | Why software projects fail, conceptual integrity, the second-system effect, communication overhead | Fifty years old and still correct, which is itself the lesson. Short. Everything you'll ever see go wrong on a team is described here. |
| **35. Crafting Interpreters** — Robert Nystrom 🆓 | Build two complete language interpreters — a tree-walker in Java and a bytecode VM in C | Free online, beautifully written and illustrated. Demystifies compilers permanently, and the C bytecode VM is a masterclass in low-level design. |
| **36. Structure and Interpretation of Computer Programs** — Abelson & Sussman 🆓 | Abstraction, higher-order procedures, state, streams, metalinguistic abstraction, register machines | Free from MIT. The book that argues programming is about controlling complexity, not about a language. Hard, worth it, and permanently changes how you decompose problems. |
| **37. Effective C**, 2e — Robert Seacord | Modern C (C17/C23) done correctly: undefined behavior, memory, strings, error handling, portability | You own K&R (C89, 1988) and King (2008). Neither covers what the standards committee has since decided, or the undefined-behavior minefield that modern compilers exploit. |

## I. Distributed systems, data & networks

| Book | What it covers | Why you want it |
|---|---|---|
| **38. Distributed Systems**, 4e — Tanenbaum & Van Steen 🆓 | Communication, naming, coordination, consistency, replication, fault tolerance, security | Free from distributed-systems.net. The textbook complement to Kleppmann's practitioner view. |
| **39. Database Internals** — Alex Petrov | B-trees, LSM trees, WAL, buffer management, then distributed consensus and replication | Storage engines from the inside. Answers "why is my database doing that?" at a level no usage guide reaches. |
| **40. TCP/IP Illustrated, Vol. 1: The Protocols**, 2e — Stevens & Fall | ARP, IP, ICMP, TCP, UDP, DNS, DHCP — traced packet by packet with real captures | You have no networking book at all. This one teaches by *showing you the bytes*, which is why it has never been superseded. |
| **41. Systems Performance**, 2e — Brendan Gregg | CPU, memory, filesystem, disk, network performance; methodologies, tracing, flame graphs | Turns "it's slow" from a complaint into a measurement procedure. The USE method is a genuinely portable mental tool. |
| **42. Site Reliability Engineering** — Beyer, Jones, Petoff & Murphy (eds.) 🆓 | SLOs, error budgets, monitoring, incident response, postmortems, capacity planning | Free from Google. Even outside web operations, the framing of reliability as a *budgeted, measured* property is a discipline your reliability-engineering side will recognize. |

## J. Security & cryptography

*Zero coverage currently — a real gap for anyone working near communications, embedded systems, or defense.*

| Book | What it covers | Why you want it |
|---|---|---|
| **43. Security Engineering**, 3e — Ross Anderson 🆓 | Threat modeling, access control, crypto in practice, hardware security, side channels, banking, surveillance, physical security | **Free from Cambridge**, and arguably the best engineering book of any kind on this list. Anderson thinks in systems and failure modes; the chapters on hardware attacks, emission security, and signals intelligence connect directly to what you already know. Start here. |
| **44. Serious Cryptography**, 2e — Jean-Philippe Aumasson (2024) | Randomness, hashing, MACs, AEAD, RSA, elliptic curves, TLS, post-quantum | The rare crypto book that's rigorous *and* readable, written by a working cryptographer. 2e adds post-quantum coverage. |
| **45. Introduction to Modern Cryptography**, 3e — Katz & Lindell | Formal definitions, proofs of security, reductions — the theory side | If you want to know *why* a scheme is secure rather than how to use it. The standard graduate text. |
| **46. Practical Reverse Engineering** — Dang, Gazet & Bachaalany | x86/x64 and ARM disassembly, Windows internals, kernel debugging, obfuscation | The natural extension of your assembly and architecture background into a genuinely useful skill. Strong ARM coverage, which pairs with the Cortex-M book. |
| **47. Hacking: The Art of Exploitation**, 2e — Jon Erickson | Buffer overflows, shellcode, format strings, networking attacks, from C and assembly first principles | Teaches offense by teaching how memory and the stack really work. Also one of the better practical explanations of C memory layout you'll find anywhere. |

## K. Information theory & coding

*The mathematics of "how much can this channel carry, and how do I protect what I send" — foundational for comms,
compression, ML, and inference alike, and entirely absent from your shelf.*

| Book | What it covers | Why you want it |
|---|---|---|
| **48. Information Theory, Inference, and Learning Algorithms** — David MacKay 🆓 | Entropy, channel capacity, source and channel coding, Bayesian inference, neural networks, LDPC codes | **Free from Cambridge.** MacKay treats information theory, inference, and machine learning as one subject — which they are — and writes with more personality and clarity than any comparable book. If you read one book in this section, read this. |
| **49. Elements of Information Theory**, 2e — Cover & Thomas | Entropy, mutual information, AEP, channel and rate-distortion theory, network information theory | The rigorous standard. Where MacKay gives intuition, Cover & Thomas gives you the theorems to cite. |
| **50. Channel Codes: Classical and Modern** — Ryan & Lin | Block codes, convolutional codes, turbo codes, LDPC, iterative decoding | The coding half. Explains how modern systems get within a fraction of a dB of Shannon capacity — the practical payoff of the two books above. |

## L. Mathematics, with intuition

*Your math shelf is entirely course-shaped: calculus, linear algebra, ODEs, probability. Missing are the tools you'd
actually reach for, and any book that makes math feel like seeing rather than computing.*

| Book | What it covers | Why you want it |
|---|---|---|
| **51. Visual Complex Analysis** — Tristan Needham | Complex numbers, analytic functions, conformal mapping, Cauchy's theorem — all geometrically | You've used complex numbers as phasors for years without ever seeing what they *are*. Needham shows you, with pictures, and it's one of the genuinely beautiful math books. Directly relevant: transfer functions, stability, and the Smith chart are all conformal mapping. |
| **52. Visual Differential Geometry and Forms** — Tristan Needham (2021) | Curvature, manifolds, differential forms, connections — geometrically, ending at general relativity | The sequel. Differential forms are the right language for electromagnetics, and this is the only book that makes them intuitive rather than symbolic. |
| **53. Numerical Linear Algebra** — Trefethen & Bau | QR, SVD, conditioning, stability, iterative methods, eigenvalue algorithms | The best-written numerical book in existence — 40 short lectures, each one idea. The SVD chapters alone will change how you think about every matrix you meet, including in ML. |
| **54. Introduction to Applied Linear Algebra (VMLS)** — Boyd & Vandenberghe 🆓 | Vectors, matrices, least squares, and applications — no proofs, all modeling | Free from Stanford. The applications-first counterweight to Anton. Least squares is the workhorse of engineering and this is the clearest treatment of it. |
| **55. The Fourier Transform and Its Applications**, 3e — Ronald Bracewell | Fourier transforms, convolution, sampling, the impulse function, 2-D transforms, applications | You use Fourier methods constantly across DSP, comms, optics, and EM, and own no book about them. Bracewell is the reference, and unusually good at building geometric intuition for transform pairs. |
| **56. Mathematical Methods for Physics and Engineering**, 3e — Riley, Hobson & Bence | Vector calculus, complex analysis, PDEs, special functions, tensors, group theory, statistics — 1300 pages | The one-volume lookup reference for every method you half-remember. Buy it for the shelf, not to read. |
| **57. How to Solve It** — George Pólya | A general heuristic for attacking problems you don't know how to attack | Eighty years old, seventy pages of actual content, and still the best short book on problem-solving strategy ever written. |

## M. Physics past the first year

*You stop at Halliday. These are the five that pay off directly in electrical engineering.*

| Book | What it covers | Why you want it |
|---|---|---|
| **58. Introduction to Electrodynamics**, 4e — David Griffiths | Electrostatics, magnetostatics, Maxwell's equations, EM waves, radiation, relativistic E&M | The most enjoyable physics textbook ever written, and *the* undergraduate E&M book. Ulaby teaches you to apply EM; Griffiths makes you understand it. |
| **59. Electricity and Magnetism**, 3e — Purcell & Morin | Same territory, but derives magnetism from electrostatics plus special relativity | Read alongside Griffiths for the single best insight in classical physics: magnetism *is* electrostatics seen from a moving frame. It reframes everything you know about circuits and fields. |
| **60. Optics**, 5e — Eugene Hecht | Wave optics, interference, diffraction, polarization, Fourier optics, lasers | Optics is EM at shorter wavelengths — the same math you already know, with a different set of instincts. Increasingly relevant as photonics, lidar, and EO/IR sensing converge with RF. |
| **61. Introduction to Quantum Mechanics**, 3e — Griffiths & Schroeter | Wave functions, operators, the hydrogen atom, spin, perturbation theory, scattering | Your semiconductor book asserts quantum results; this derives them. Also the foundation for lasers, quantum sensing, and anything you'll read about quantum computing. |
| **62. An Introduction to Thermal Physics** — Daniel Schroeder | Thermodynamics, entropy, statistical mechanics, Boltzmann and quantum statistics | The clearest stat-mech book there is — and the physical origin of **thermal noise**, which sets the floor on every receiver, amplifier, and sensor you will ever design. Directly load-bearing for RF work. |

## N. How engineering actually fails

*Nothing in your library discusses reliability, risk, or failure. For someone building systems that have to work, this
is a stranger gap than any of the technical ones.*

| Book | What it covers | Why you want it |
|---|---|---|
| **63. What Engineers Know and How They Know It** — Walter Vincenti | Case studies in aeronautical history examining how engineering knowledge is actually generated | The best book on engineering *epistemology*. Argues convincingly that engineering is not applied science but its own way of knowing. Changes how you read every other technical book. |
| **64. Practical Reliability Engineering**, 5e — O'Connor & Kleyner | Failure distributions, Weibull analysis, FMECA, accelerated testing, reliability prediction and growth | The working reference for MTBF, derating, and test planning — vocabulary you'll meet immediately in aerospace, defense, or automotive work, and won't have seen anywhere in your coursework. |
| **65. Normal Accidents** — Charles Perrow | Why tightly coupled, complex systems fail in ways no component analysis predicts | The origin of the "complexity plus tight coupling equals inevitable accidents" argument. Explains a category of failure that redundancy makes *worse*, not better. |
| **66. The Logic of Failure** — Dietrich Dörner | Experimental psychology of how people mismanage complex, dynamic systems | Dörner put people in charge of simulated systems and watched them fail in consistent, predictable ways. You will recognize yourself. Short and genuinely unsettling. |
| **67. To Engineer Is Human** — Henry Petroski | Structural failure case studies — Tacoma Narrows, Hyatt Regency, the Comet — and what they taught | Petroski's thesis is that engineering advances through failure, not success. The most readable entry point to this whole section. |

## O. Thinking, writing, seeing

| Book | What it covers | Why you want it |
|---|---|---|
| **68. The Art of Doing Science and Engineering** — Richard Hamming | Hamming's Bell Labs course on how to do work that matters: style, luck, compounding, choosing problems | Includes "You and Your Research," the best talk ever given on technical careers. Written by someone who was in the room for the invention of modern computing. Read it once a year. |
| **69. The Visual Display of Quantitative Information**, 2e — Edward Tufte | Graphical excellence, data-ink ratio, chartjunk, small multiples, the history of statistical graphics | You will spend your career making plots that either persuade people or don't. This is the foundational book, and it's beautiful as an object. |
| **70. On Writing Well**, 30th Anniv. Ed. — William Zinsser | Clear nonfiction prose: simplicity, clutter, structure, voice — with a chapter on writing about technology | The highest-leverage non-technical skill an engineer can improve. Zinsser's chapter on science and technology writing is aimed directly at people like you. |
| **71. Thinking, Fast and Slow** — Daniel Kahneman | Two-system cognition, heuristics, biases, anchoring, overconfidence, prospect theory | The reference work on how your own estimates go wrong. Pairs naturally with §N — most engineering failures are judgment failures first. |
| **72. The Art of Statistics** — David Spiegelhalter | Statistical reasoning through real cases: uncertainty, causation, evidence quality, communicating risk | Your stats books teach mechanics. This teaches *judgment* — when a number means something and when it doesn't. Ideal counterweight to a library heavy on formalism. |

## P. History that's actually load-bearing

*Not entertainment. Each of these explains why a field you work in looks the way it does.*

| Book | What it covers | Why you want it |
|---|---|---|
| **73. Instruments of Darkness: The History of Electronic Warfare** — Alfred Price | The WWII origins of EW: the Battle of the Beams, Window/chaff, radar countermeasures, the measure/countermeasure cycle | The historical foundation under your entire EW shelf. Adamy tells you how it works; Price tells you why it exists and how the action/reaction cycle was discovered the hard way. |
| **74. Most Secret War** — R. V. Jones | Jones's own account of running British scientific intelligence, 1939–45 | A first-person masterclass in inference from fragmentary evidence — the intellectual core of both intelligence and debugging. Also very funny. One of the great engineering memoirs. |
| **75. The Invention That Changed the World** — Robert Buderi | The MIT Radiation Lab, the birth of radar, and its postwar spillover into everything | Explains where microwave engineering, systems engineering, and much of modern EE institutionally came from. Connects your RF, radar, and EW shelves to their shared origin. |
| **76. Crystal Fire** — Riordan & Hoddeson | The invention of the transistor at Bell Labs and the birth of the semiconductor industry | The other origin story your library depends on. Anderson's book gives you the physics; this gives you how the physics became an industry. |
| **77. The Codebreakers** — David Kahn | Cryptography from antiquity through WWII and the founding of the NSA | The definitive history of signals intelligence — the field adjacent to everything in §C and §J. Enormous, and worth owning even if you read it in pieces. |
| **78. The Soul of a New Machine** — Tracy Kidder | A year inside a Data General team racing to build a 32-bit minicomputer | Pulitzer-winning, and the truest book ever written about what engineering *feels like* — the debugging, the politics, the cost. Read it when the reference books get heavy. |

---

## Where to start

If 78 is too many to act on, these ten are the ones whose absence you'd most notice, and they're spread deliberately
across domains:

| # | Book | Fills |
|---|---|---|
| 26 | **Computer Systems: A Programmer's Perspective** | The hardware↔software gap in the middle of your CS shelf |
| 17 | **Electromagnetic Compatibility Engineering** — Ott | The single most useful practical EE book you don't own |
| 43 | **Security Engineering** — Anderson 🆓 | An entire missing discipline; free; best-written book on the list |
| 48 | **Information Theory, Inference, and Learning** — MacKay 🆓 | Information theory + inference + ML as one subject; free |
| 1 | **Microwave Engineering** — Pozar | Everything above 100 MHz |
| 6 | **Statistical Signal Processing Vol. I** — Kay | The estimation theory under sensors, comms, and ML |
| 58 | **Introduction to Electrodynamics** — Griffiths | Understanding the EM you've only been applying |
| 51 | **Visual Complex Analysis** — Needham | Seeing the math you've been computing |
| 32 | **Designing Data-Intensive Applications** 2e | Systems thinking at scale |
| 68 | **The Art of Doing Science and Engineering** — Hamming | How to choose what to work on |

**Free right now, no decision required (23 titles):**
Steer *Fundamentals of Microwave and RF Design* · Collins *SDR for Engineers* · ADI *Op Amp Applications Handbook* ·
Corbet *Linux Device Drivers* · Nystrom *Crafting Interpreters* · Abelson & Sussman *SICP* ·
Tanenbaum *Distributed Systems* 4e · Google *SRE* · Anderson *Security Engineering* 3e ·
MacKay *Information Theory, Inference, and Learning Algorithms* · Boyd & Vandenberghe *VMLS* —
plus the twelve already listed in §7.
