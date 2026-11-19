# Math review: Monte Carlo beta cases (2026-11-19)

Scope: `~/Projects/hse/content/monte-carlo/{probability,markov-chains,bayes-conjugate,kr2-practice}`:
notes.md, every widget, the 4 PDFs in `kr2-practice/entry.json`. Live https://hse.werserk.dev/beta/monte-carlo/
checked: every widget HTML is identical to the source (only the `robots` meta line differs); the pages contain the same numbers.
Reviewer did not edit content.

## Verdict

Every number in the four notes, the KR-2 mock (problems and solutions), the A4 sheet and the 7-page cheatsheet recomputes correctly.
**One real error:** the class-graph widget in the Markov chains case has two wrong edge labels.
The rest are clarity and precision notes (medium/low). The lecture numbers in the sources match the course (L1–L2, L3, L4).

## Findings

| # | Severity | Where | What is wrong | Correct |
|---|---|---|---|---|
| 1 | **high** | `markov-chains/widgets/classes.html`, the `lineArrow(1,2,8,'1/2')` and `lineArrow(2,4,0,'1/4')` lines (Fig. 4.1) | Edge 1→2 is labelled 1/2 and edge 2→4 is labelled 1/4. As drawn, row 1 sums to 1/4+1/2+1/4+1/4 = 5/4 and row 2 to 3/4. This contradicts the equations in notes.md:113 (`g_1=¼g_1+¼g_2+…`, `g_2=½g_1+½`) and the matrix in `limit.html` (`P1`). The screenshot confirms "1/2 1/2" between 1 and 2 and "1/4" on 2→4. Live has the same bug. | 1→2 = **1/4**, 2→4 = **1/2** (row 1: ¼,¼,¼,0,¼; row 2: ½,0,0,½,0). |
| 2 | medium | `bayes-conjugate/notes.md:72` | One letter D stands for both a chain state and the data: `P(X_7=D\mid D)`, "переход U→D", while ch. 1–4 use D for the data. The formula is ambiguous. | Rename the data (e.g. 𝒟 or "данные") or the states (e.g. 0/1). The value 3/8 is correct. |
| 3 | medium | `bayes-conjugate/notes.md:82` | "Сопряжённые пары — только Beta для вероятности и Gamma для интенсивности" is false as a general claim: Normal–Normal, Dirichlet–Multinomial, Gamma–Exp (the cheatsheet p. 4 itself uses Gamma for Exp lifetimes) and others exist. | "В этом курсе нужны две сопряжённые пары: …" or list Gamma also for Exp times. |
| 4 | low | `bayes-conjugate/notes.md:66` | "Различие — это дисперсия апостериорного" holds exactly only for g(p)=p² (ch. 4 shows it for that case). For a general non-linear g the gap is not Var p (≈ g''·Var/2 to second order). | "Для g=p² различие — ровно дисперсия; в общем случае оно тоже исчезает, когда данных много". |
| 5 | low | `markov-chains/notes.md:123` | "В примере выше…": the period-2 chain (3→4 and 4→3 with probability 1) is defined only in the caption of Fig. 4.2, not in the text. The boundary values also give only `a_3, b_3` and omit `a_4=0, b_4=1` and `a_5=b_5=0`, which the recipe needs. | Name the modified rows in the text and list all boundary values. The numbers 2/15 and 7/15 are correct. |
| 6 | low | `probability/notes.md:40` | `Y=⌈X⌉` is called "геометрическое с p=1−e^{−2}" without its support. In lecture 2 (and course-study.md) Geom is the number of failures, k≥0, mean (1−p)/p. Here k≥1, mean 1/p. | Add "на k=1,2,… (номер первого успеха)". The cheatsheet p. 1 already says k≥1. |
| 7 | low | `probability/notes.md:26` | "несовместные события не независимы" holds only when P(A),P(B)>0. | Add "(если обе вероятности положительны)". |
| 8 | low | `kr2-practice/cheatsheet-v3.2.pdf` p. 2, 3, 7 | It cites "мок №1 з.1/з.3/з.5", "видео 3A/3B, 5B, 6A, 6B" and "ДЗ5 №1–5", but the case ships only mock №2 and none of these. Also, "ДЗ5" (the file `Дз_к_лекции05.pdf`) is the Markov-chain homework, while Markov chains are lecture **4** and lecture 5 is MC. A reader can take ДЗ5 to be the MC homework. | Note in the case that mock №1 and the videos are not attached, and write "ДЗ5 (к лекции 4, цепи Маркова)" or rename it. The math is correct. |
| 9 | nit | `kr2-practice/notes.md:11` | `1-\prod(1-p_i)` assumes independence; the table does not say so. | "(независимые)". |
| 10 | nit | `bayes-conjugate/notes.md:13` | "Сквозной пример главы 2–4". | "глав 2–4". |
| 11 | nit | `probability/widgets/maxmin.html`, side text | "EТ" uses a Cyrillic Т. | Latin T. |

## Recomputed (all correct)

Scripts: `scripts/check_markov.py`, `check_prob_bayes.py`, `check_mock.py` (sympy via `uv run --with sympy`), `beta_frac.js`, `limit.js` (node, the widgets' own code).

- **probability**: P(D)=0.032, P(A|D)=3/8; 0.999; 2/13, ratio 5.5; geometric ratio e²; lamps 13/12; 216/625; Var Y=2, Cov=1; Var S=20; EW=1/3, 7/16, E max=2/3; ∫(4p³−3p⁴)=2/5 vs 5/16. Widgets: tree 0.012/0.588/0.02/0.38 and 3/8; maxmin ticks 1/4, 7/12, 13/12, 25/12.
- **markov-chains**: q₃=(16,8,2,1)/27; 4/27; 1/2; 2-state 4/5, 19/25 → 3/4; h=(1/15,1/5,7/15), 4/15; t=(44/15,24/5,68/15); P(T≤4)=5/81 (taboo-matrix check); fill t=(33,30,21); π=(8,4,2,1)/15, 15/8; π{3,4}=(3/5,2/5); g₁=3/5, limit (0,0,9/25,6/25,2/5), leave time 2; period 2 → (0,0,2/15,7/15,2/5) / (0,0,7/15,2/15,2/5) (P^200, P^201); Q²_AB=4/9; ν=(1/2,1/2); S² non-chain example. Widgets: chain matrix, firststep h/t values and loop step, limit bars at n=40/41, lump good (sums 2/3,2/3,1/3,1/3) and bad (16/39 vs 11/24).
- **bayes-conjugate**: Beta(3,6): Ep=1/3, Ep²=2/15, Var=1/45, 2/5; Laplace 4/5; ∫p(1−p)=1/6; Gamma(7,5): 7/5, (5/6)⁷=78125/279936≈0.279; chain Beta(3,5): 3/8, 29/48 vs 37/64; 2/5 vs 5/16. Widget: midpoint integral = 2/15 (error 1.7e−16).
- **mock-2**: π=(9,6,4)/19; t₀=35/4, t₁=25/4; P(T≤3)=32/125; Q, b₃=21/32, ν=(1/3,2/3); task 3: 1/2, 1/10 vs 1/2; task 4: g=(2/5,4/5), t=(16/5,12/5), limit (0,0,3/5,2/5); task 5: d₀=−7/29, limits (11/29,18/29) / (18/29,11/29) (P^300, P^301).
- **A4 sheet**: 1/4 (posterior 3(1−u)²); robot h₂=4/5, t₂=18/5, 11/15, limit (4/15,0,0,0,11/15); formulas for Beta moments and Gamma prediction.
- **cheatsheet v3.2**: 91/100; 7/12, 7/36, 21/65; 17/20; urns row (1/4,1/2,1/4), π=(1/6,4/6,1/6); robot h, t and closed forms; loop trick 1/3, 2; ρ=p/(1−p)=2/3; G/B return 3/2 vs 2; ДЗ5 №4 Q; video 5B 3/8 vs 2/5; period 2 (1/6,1/3); shooter 5/9, 1/3, 3/5; Gamma 5/3, 243/1024; chain-Bayes 2/5, 32/55, 14/25, Var 6/275; max of walk p² vs p; urns detailed balance; 2-state Pᵗ induction; ∫ table; 1−½ln3≈0.451; 2/5; BF=3/2, 3/5; 5/6, 7/10. Distribution table moments are correct.

## Lecture numbers

Course files (`~/Projects/monte-carlo/materials/archive/course-study.md`, lecture PDFs 01–05): L1 probability basics, L2 distributions and epidemic models, L3 Bayesian inference, L4 Markov chains, L5 MC/IS/MH/Gibbs.
The cases cite: probability "лекции 1–2", bayes-conjugate "лекция 3", markov-chains "лекция 4". **All three are consistent.** kr2-practice cites no lecture.
Only one numbering can confuse a reader, the homework number "ДЗ5" (finding 8).

## Not checked

Colours in the widget captions ("розовые/серо-голубые"); cover images; the visual layout of the PDFs beyond pages 3 and 5, which were rendered to resolve formulas garbled by text extraction.
