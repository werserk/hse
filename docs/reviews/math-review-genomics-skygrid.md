# Math review: comp-genomics beta cases + Skygrid (НИС АДНЖ)

Reviewer thread: thr_cja98xbn2c · 2026-11-20 · read-only, no content edited.

## Scope and state

| Item | Source reviewed | Live check |
|---|---|---|
| `content/comp-genomics/{hardy-weinberg-ld,drift-ne,coalescent,formula-sheet}` notes, 5 widgets, `cheatsheet_formulas.pdf` | `~/Projects/hse` working tree | identical to `origin/main` (`git diff --stat origin/main` empty); live PDF md5 = repo md5 `6a69b264…`; live pages contain the reviewed strings |
| `content/genomics/skygrid` notes, 8 widgets, deck `site/index.html` (39 slides + speaker notes) | same | `/beta/genomics/skygrid/` 200; this case has **no PDF** on live (`/pdf/` → 404) and none in the repo, so the "PDFs" item covers only the formula-sheet PDF |
| Paper Gill et al. 2013 | PMC3563973 HTML; formula images viewed (eq. 1–4, 6–9, 13–15, i76–i85, i141) | — |

Method: every formula re-derived by hand or in sympy, every numeric example recomputed, every widget's `<script>` executed in node with a DOM shim (all states stepped). Scripts: `scripts/check.py`, `scripts/run-widget.js` in this thread's storage.
Not done: visual rendering of widgets in a browser (checked only computed text/numbers, not layout).

Severity: **High** — wrong math a reader would learn; **Medium** — wrong statement that changes a method or conclusion; **Low** — mislabel, cross-reference, notation, wording.

## Findings

| # | File:line | Wrong | Correct | Sev. |
|---|---|---|---|---|
| 1 | `genomics/skygrid/notes.md:267`; deck `site/index.html:3165-3167`, `:3187` | τ-proposal "f ∝ f + 1/f on [1/F, F]" is called symmetric ("симметрично относительно замены f↔1/f"; deck: "симметричное мультипликативное предложение… что упрощает шаг MH"). For τ* = τf the proposal density is q(τ*\|τ) = π(τ*/τ)/τ; with π ∝ f+1/f the Hastings ratio q(τ\|τ*)/q(τ*\|τ) = **1/f**, not 1 (sympy, checked). The paper writes the same formula (image i141, checked), so the notes copy a paper slip and add a wrong justification. | Symmetric multiplicative proposal: π(f) ∝ **1 + 1/f** on [1/F, F] (Knorr-Held & Rue 2002; Hastings ratio = 1, sympy checked). That BEAST implements 1+1/f is from memory, not re-checked. Suggested text: «в статье напечатано ∝ f+1/f; симметричное предложение даёт плотность ∝ 1+1/f (Knorr-Held, Rue 2002), иначе в отношение MH входит множитель 1/f». Line 271 («приближение влияет только на скорость») stays true only with a correct Hastings ratio. | Medium |
| 2 | `comp-genomics/hardy-weinberg-ld/notes.md:76` | «В примере рис. 1.1» | «рис. 2.1» (the Wahlund figure is Рис. 2.1, line 59) | Low |
| 3 | `comp-genomics/drift-ne/notes.md:21`, `:25` | «На рис. 2.1 видно…», «На рис. 2.1 P(X=0)…» | «рис. 1.1» (the WF figure is Рис. 1.1, line 18) | Low |
| 4 | `comp-genomics/drift-ne/notes.md:25` | «Вероятность утраты за один шаг проще считать через дополнение: P(X≥1)=1−P(X=0)» — the formula is the probability of **keeping** the allele | «Вероятность сохранить аллель — через дополнение: P(X≥1)=1−(1−p)^{2N}; утрата P(X=0)=0,7^{10}≈0,028» (PDF item ДЗ2.6 already says «не потерять») | Low |
| 5 | `comp-genomics/coalescent/widgets/coal-tree.html:36` | «Первый интервал (k = 2) один длиннее всех остальных» | k = 2 is the **last/oldest** interval (the list starts at k = 6; Skygrid notes:30 also says «последний»): «Последний, самый древний интервал (k = 2)…». Numbers 1.00 of 1.67 are right. | Low |
| 6 | `comp-genomics/coalescent/notes.md:92` | `L` means total branch length (lines 81, 87) and, in the same chapter, region length («θ=4N_eμL на регион длины L») | rename region length, e.g. `ℓ` сайтов: θ = 4N_eμℓ | Low |
| 7 | `genomics/skygrid/notes.md:68` | «ступеней на одну больше, чем внутренних точек» | M grid points x_1…x_M (x_M = K is itself a grid point) give M+1 steps: «на одну больше, чем точек сетки» | Low |
| 8 | `genomics/skygrid/notes.md:291-295` | R in the integral limit is not defined («интегрирование идёт до информативной части оси») | Paper: R = maximum of the mean estimated root heights for the data set; R_max = root height of the tallest true tree. The deck already says this (`site/index.html:3388`). | Low |
| 9 | `genomics/skygrid/notes.md:331` | «спад … за пять лет до последнего отбора» (reads as a point 5 years before) | Paper: "a dip … over the 5 years prior to the most recent sampling time" → «в последние пять лет перед последним отбором» | Low |
| 10 | `genomics/skygrid/widgets/hazard.html:7-8` | `const S=[1]` and then a push at i = 0 too, so `S[round(t/dt)]` is the survival at t − dt (one-step lag, 0.005; invisible) | `const S=[]` | Low |
| 11 | `comp-genomics/formula-sheet/notes.md:16` | «H_t=H_0(1−1/2N)^t» | E[H_t] = H_0(1−1/2N)^t (drift-ne:45 and its trap :60 insist on the expectation) | Low |
| 12 | `comp-genomics/formula-sheet/notes.md:1` vs `cheatsheet_formulas.pdf` | «Печатная версия — все формулы на одном листе», but the PDF (titled «ДЗ 1–4») lacks the variable-N_e formula P(T_2>t)=exp(−∫du/2N_e(u)) from table row :18 | add the formula to the PDF, or say the PDF covers ДЗ 1–4 only | Low |
| 13 | deck `site/index.html:2294` (slide 16, also slide 17) | «P(g_i\|θ) = ∏(1/θ_k)^{c}exp(−SS/θ_k)» with "=" after the combinatorial factors were dropped (slide 15 uses ∝) | ∝ (notes:124 already uses ∝). Paper eq. 8 has the same "=". | Low |
| 14 | deck `site/index.html:3042` (slide 29); `notes.md:238` | Gaussian approximation written «≈ τ^{M/2} exp[…]» (deck) / «≈ exp[…]» (notes): constants exp(−Σh_k(γ̂_k)+…) are dropped, and τ^{M/2} is irrelevant for the conditional of γ | «∝ (приближённо) exp[−½γᵀ(τQ+Diag(SS_k e^{−γ̂_k}))γ + Σ(SS_k e^{−γ̂_k}(1+γ̂_k)−c_k)γ_k]» — the exponent itself is correct (sympy) | Low |
| 15 | `comp-genomics/hardy-weinberg-ld/notes.md:15` (nit) | «за одно поколение случайного скрещивания частоты генотипов принимают такой вид» stated generally, while :35 then discusses X-linked genes | true for an autosomal locus with equal allele frequencies in both sexes; an X-linked locus approaches HWE over several generations | Low |

No High findings.

## Checked and correct

Each item recomputed (sympy/numpy or node output; script `scripts/check.py`).

- **Hardy–Weinberg / LD.** 2pq=0.0198 (≈1/50); χ² for 42/46/12 = 0.0121, df = 1; Wahlund ΔH = 2σ²_p (symbolic identity); example ΔH 0.48−0.30 = 0.18, F_ST = 0.375; D₀ = αβ = 0.21, D₅ = 0.124, half-life ln0.5/ln0.9 = 6.58; ABO and X-linked frequencies.
- **Drift / N_e.** Binomial step, mean 3, SD 1.45, P(X=0) = 0.7¹⁰ = 0.028 (widget); E[H_t] recursion; F recursion; harmonic mean (B: mean 802, N_e = 48.1); bound N_e ≤ T·N_min; **growth N_t = N₀2^{t−1}** (the prior fix holds): Σ1/N_t = (2/N₀)(1−2^{−T}) symbolically, N₀=100, T=5 → sizes 100…1600, mean 620, N_e = 258.06; sex ratio p_A+p_B+p_C = 1, N_e = 4N_mN_f/(N_m+N_f), 30/70 → 84.
- **Coalescent.** P(T₂>t) for variable N_e; two-epoch example E[T₂] = 1000(1−e⁻¹)+10000e⁻¹ = 4310.9 (MC 1e6 draws: 4326, within MC error); Var(T_k) = 4/(k²(k−1)²); E[T_MRCA] = 2(1−1/n) (telescoping, symbolic); E[L] = 2a_n (n=6: 4.567); L = 3T₃+2T₂; d=20, μ=1e−3 → T₂ = 10⁴; E[S] = θa_n, E[π] = θ; SFS θ/i (n=6, θ=10: E[S] = 22.83, singletons 1/a_n = 0.438); Tajima sign table.
- **Formula-sheet PDF.** All formulas in ДЗ 1–4 match the notes (text extraction plus a page render).
- **Skygrid notes vs paper.** Pair rate 1/N_e convention, λ_k, E w_k = 2N_e/(k(k−1)); interval density; grid x_j = jK/M and M+1 parameters (paper's typo "x_{k−1} ≤ θ_k < x_k" is correctly written with t in the notes); c_ik/SS_ik likelihood (eq. 8–9); multi-locus sum (eq. 10–12); GMRF prior τ^{M/2} (eq. 13–14), Q for M=4 gives γᵀQγ = Σ(Δγ)² (symbolic, rank 4); h′, h″, linear term SS e^{−γ̂}(1+γ̂)−c and quadratic term (symbolic); Newton gradient/Hessian; scenarios incl. continuity at t=1.5 (3.51063 vs 3.51064); error/size metrics (eq. 2–4); Tables 1–4, bison TMRCA (101.45 [87.12–117.5], 133.56, 130.39 [99.99–159.54]), simulation 69.79/1 %, 9.29/96 %, 9.90/96 %; ESS > 1000, ESS/min 126.9–493.1 → 41.3–137.4; τ prior a = b = 0.001 (prior means 1…100 with b fixed); 29 grid points, K = 10; HIV growth/decline statements; "monotone decrease" claim holds for every column of Table 1; "only value below 1 in Table 2 errors is 0.97" holds.
- **Skygrid widgets (node).** coalesce: λ_k, E w_k, roots 1.67 / 5.00. lik: segments, c = (2,1,1), SS = (6.30, 1.80, 0.60), SS/c = (3.15, 1.80, 0.60), ln P = −7.42 vs −6.37 (matches notes:119, :129). newton: 0.444 → 0.578 → 0.588 = ln 1.8; "precision = c at the mode". gmrf: penalties 26.47 / 0.69, means 2.05 / 2.06. loci (seeded): 1 locus c = (26,1,1,0,1,0), 10 loci (260,16,6,4,2,1); text claims hold. grid, scen, hazard: shapes match the text (hazard lag: finding 10).
- **Deck formulas** (slides 6–34): same as the notes, apart from findings 1, 13 and 14.

---
**Materials**
- This report: `/home/werserk/.bb/thread-storage/thr_cja98xbn2c/math-review-genomics-skygrid.md`
- Checks: `/home/werserk/.bb/thread-storage/thr_cja98xbn2c/scripts/check.py`, `/home/werserk/.bb/thread-storage/thr_cja98xbn2c/scripts/run-widget.js`
- Paper text and formula images: `/home/werserk/.bb/thread-storage/thr_cja98xbn2c/paper/` (`gill.txt`, `sheet1.png`, `sheet2.png`)
- Reviewed repo state: `~/Projects/hse` = `origin/main` `f9b414c` for these paths
