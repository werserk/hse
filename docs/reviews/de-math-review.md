# Math review: differential-equations beta cases

Date: 2026-11-20. Reviewer thread: thr_iyiw5gzbsr. Scope: `~/Projects/hse/content/differential-equations/{difference-equations,first-integrals-pde,planar-systems,second-order-linear,problem-map}` (notes.md, widgets), `problem-map/main.pdf` (source: `~/Projects/_work/hse-ami-cheatsheets/cheatsheets/math/differential-equations/topics/M01–M13*.tex`), live https://hse.werserk.dev/beta/differential-equations/. Content was not edited.

## Verdict

**No critical or major errors.** Every boxed answer, derivation and numeric example checks out symbolically. There are 3 minor findings (one false side claim, one false caption, one misleading figure) and some cosmetic items, listed below.

## Severity scale

- **critical**: a wrong answer, formula or computation.
- **major**: a wrong statement of method that would mislead a solution.
- **minor**: a false side claim, caption or figure; the answer is unaffected.
- **cosmetic**: wording, notation or a stale label.

## Findings

| # | File:line | Wrong | Correct | Severity |
|---|---|---|---|---|
| 1 | `difference-equations/notes.md:98` | «Это следует из условия вещественных коэффициентов (с комплексными коэффициентами хватило бы одного корня).» | False. $\alpha^t\sin\omega t=\frac{1}{2i}\bigl((\alpha e^{i\omega})^t-(\alpha e^{-i\omega})^t\bigr)$ requires both roots for any coefficient field. Example: $y_t=2^t\sin\frac{\pi t}{3}$ has $y_0=0$ and $y_1=\sqrt3$, so no first-order recurrence $y_{t+1}=cy_t$ with $c\in\mathbb C$ fits it. The sine itself forces the pair. One root would be enough only for the complex solution $\alpha^te^{i\omega t}$. Suggested text: «корни приходят парой, потому что синус (и косинус) — комбинация двух экспонент $(\alpha e^{\pm i\omega})^t$». | minor |
| 2 | `first-integrals-pde/notes.md:147` (caption of Fig. 3.1) | «справа пересекает все окружности» | The line $x=1+y$ is at distance $1/\sqrt2\approx0.707$ from the origin. It misses the drawn circle $R=0.7$ completely and meets $R=0.85$ twice, at $s=-0.834$ and $s=-0.166$ (computed by running the widget in node). Correct: «справа пересекает каждую окружность около (1, 0) один раз», which matches the widget's own text. A useful addition: at $(\frac12,-\frac12)$ the line touches the circle $R=1/\sqrt2$, where $\Delta=1+2s=0$. That is why the answer $-1+\sqrt{2(x^2+y^2)-1}$ exists only for $x^2+y^2\ge\frac12$. | minor |
| 3 | `planar-systems/widgets/phase3.html:45-46` (Fig. 1.2) | The code comment says «spirals into the focus», and the side text says «Фокус: траектории навиваются на точку по спирали». Of the five trajectories drawn in the focus colour, only the one from $(0.2,-1.15)$ reaches the focus (1.8 turns; it ends 0.026 from the focus). The other four start outside its basin: from $(1.4,-1.5)$, $(0.95,0.2)$, $(1.8,-0.6)$ and $(0.2,0.05)$ they pass by (≤0.39 turns) and leave through the top edge. Checked by running the widget's RK4 in node and on the live screenshot. | The trajectories are numerically correct, but the figure shows one spiral, not "trajectories spiralling in". Choose starting points inside the basin (near $(\frac34,-\frac34)$, between the stable separatrices), or recolour the four passing curves and say that they go past. | minor |
| 4 | `planar-systems/widgets/plane.html:33,43` (Fig. 1.1) | The thick line $\operatorname{tr}=0$ runs over the whole det range, including $\det<0$ (saddles), under the label «tr = 0: центр или негиперболика». | Start the line at $\det=0$ (the centre ray is $\operatorname{tr}=0,\det>0$). The other non-hyperbolic set, $\det=0$, is not marked at all. The label «D = 0» is rotated −36°, while the parabola there slopes at about 58° on screen. | cosmetic |
| 5 | `planar-systems/notes.md:122` | «Если $h_k$ зависит от θ и меняет знак, решает усреднение по обороту, и знак ответа не даёт.» | Garbled. Intended meaning: «знак $h_k(\theta)$ в отдельной точке ответа не даёт; решает знак среднего $\frac1{2\pi}\int_0^{2\pi}h_k\,d\theta$ (если оно ≠ 0)». | cosmetic |
| 6 | `first-integrals-pde/notes.md:63` | «найти первые интегралы системы из главы 1» | The characteristic system is a different system. Should read «первые интегралы характеристической системы, как в главе 1». | cosmetic |
| 7 | `first-integrals-pde/notes.md:89,91` | The substitution variable $u=y/x$ clashes with the unknown $u(x,y,z)$ of the same chapter. | Rename it, for example $w=y/x$. | cosmetic |
| 8 | widget HTML comments: `chars.html:1` (Fig. 6.1), `phase3.html:1` (Fig. 3.2), `plane.html:1` (Fig. 3.1), `polar.html:1` (Fig. 8.1), `well.html:1` (Fig. 12.1), `zeros.html:1` (Fig. 11.1, "chapter 11") | Figure and chapter numbers left over from the cheatsheet. | Not visible to readers; update when the files are next edited. | cosmetic |

### Print PDF (`problem-map/main.pdf`)

The live PDF is byte-identical to the local file and to `main.pdf` built from the cheatsheet sources (md5 `417e9b1e…`), and it was built after the last `.tex` change. Every worked example in M1–M13 matches its chapter. The notes say «при расхождении верна глава», but these differences in the PDF are still worth knowing:

| # | Source:line | Wrong | Correct | Severity |
|---|---|---|---|---|
| P1 | `M03-…tex:62` | Table row «$\det=0$ или ($\det>0$, $\operatorname{tr}=0$) — негиперболика (центр линейной части)» | $\det=0$ means a zero eigenvalue, not a centre. Only $\operatorname{tr}=0,\det>0$ is a linear centre. | minor |
| P2 | `M03-…tex:60` | The $D=0$ row is named «вырожденный узел» and then says «узел или фокус линеаризация не решает». | This contradicts itself. Drop the type name, as the chapter does at `planar-systems/notes.md:41`. | cosmetic |
| P3 | `M06-…tex:132` | «$\Delta=0\Rightarrow$ ветвление или неединственность» | The worked case (a) has $\Delta=0$ and **no** solution. Correct: «решения может не быть или их много» (chapter `first-integrals-pde/notes.md:143`). | minor |
| P4 | `M08-…tex:161-165,194-197` | «$k=0,\ h_0\ne0$ ⇒ фокус» without a condition on rotation. | A focus needs $a_0\ne0$; with $a_0=0$ the point is a node. The chapter has the condition (`planar-systems/notes.md:122`). The case where $h_k(\theta)$ changes sign is also missing from the PDF. | minor |
| P5 | `M02-…tex:140` | «(Решение здесь не приводится; это контекст для главы.)» | §4 of the same section gives the full solution; delete the sentence. | cosmetic |
| P6 | `M06-…tex:110` | Calls $a z_x+b z_y=0$ «квазилинейное». | It is linear. | cosmetic |
| P7 | `M13-…tex:200,238` | The block $S$ is typeset with `smallmatrix` and no brackets. The formula for $\Phi_t^{-1}$ omits $0\notin\sigma(A)$. | Add brackets and the condition (the chapter states it at `difference-equations/notes.md:198,240`). | cosmetic |
| P8 | `M12-…tex:111` | Step 5 concludes stability from $\lVert\mathbf x(t)\rVert<\varepsilon$ alone. | Lyapunov stability of $(\mathbf0,\mathbf0)$ needs the velocity bound too; it is in step 4. Merge the two steps (the chapter does). | cosmetic |

## What was checked and how

| Item | Method | Result |
|---|---|---|
| Difference eq. ch. 1: $\chi=(r-1)(r^2+4)$, $\chi(3)=26$, $L[t^2]=10t+9$, $L[t]=5$, $y^{(p)}=3^t+t^2$, $y^{(h)}$ | sympy: residual of $L[y^{(p)}]$ and of $L[y^{(h)}]$ for t=0..5 | 0 |
| Inverse problem: $\lambda^3-5\lambda^2+10\lambda-12$; check values $y_1=\sqrt3$, $y_2=2\sqrt3$, $y_3=0$ | sympy: expansion and residual for t=0..5 | 0 |
| Ch. 2: $A^t$ (triangular sum $\frac{2^t-(-1)^t}{3}$) | sympy: $A^k$ vs formula, k=0..7 | equal |
| Ch. 3 ex. 1: $(I-A)^{-1}$, $X_*=(-\frac12,-\frac12)$, coordinate formulas | sympy: symbolic iteration from $(x_0,y_0)$, t=1..6 | equal |
| Ch. 3 ex. 2: spectrum $\{1,-2\}$, $\Phi_t$, $\Phi_{t+1}^{-1}b=(-\frac12)^{t+1}(1,-1)$, closed form, $X_*=(\frac13,-\frac13)$, checks $X_1$, $X_2$ | sympy: $A^k$ vs $\Phi_k$, iteration t=1..7, $(I-A)X_*=b$ | equal |
| First integrals: $\dot I_1=\dot I_2=0$, ansatz solution $a=b+\frac12,\ c=0$, $\nabla I_1\times\nabla I_2=(2yz,2z,-2y)$ | sympy | equal |
| PDE: $V(y/x)=V(ze^{-(x+y)})=0$; Cauchy (b): PDE residual of $z=-1+\sqrt{2(x^2+y^2)-1}$, restriction to $x=1+y$ gives $2y$, root branch; (a) $\Delta=s$; (b) $\Delta=1+2s$ | sympy and by hand | equal |
| Planar ch. 1: equilibria, $J$, tr/det/D, eigenvalues 3/2 and −1/2, eigenvectors $(2,-5)$ and $(2,-1)$ | sympy | equal |
| Planar ch. 2: $xf+yg=r^4$, $xg-yf=-ar^2$, $r(t)=r_0/\sqrt{1-2r_0^2t}$ | sympy | equal |
| Planar ch. 3: Lyapunov proof (choice of δ, $E(0)<\min(m(\varepsilon),\varepsilon^2/2)$, no asymptotic stability), $C^2$ remark | by hand | correct |
| Second order: $W'=-pW$; $y=\varphi z$ expansion; $Q=q-\frac{p'}2-\frac{p^2}4$; integral argument for $Q\le0$; maximum argument; Sturm boundary term $\alpha(z(a)+z(b))$; Bessel $Q=1-\frac1{4x^2}$ (also by direct substitution $y=x^{-1/2}z$) | sympy and by hand | equal |
| Floquet: $\det M=e^{-\int p}$, $C=v'(1)=y'(1)/y'(0)$, $M$ lower-triangular with $\det=1$, multipliers $C$ and $C^{-1}$ | by hand | correct |
| Widgets: all 6 scripts run in node with a DOM stub; computed values cross-checked | node | see below |
| `zeros.html` | RK4 zeros of z: 2.685, 5.850, 9.000; zeros of v: 1, 4.628, 8.255, 11.883. Exactly one z-zero lies between each pair of adjacent v-zeros. The text «у z — 3, у v — 3» is correct | correct |
| `well.html` | $m=V(1)=0.75$, $E=0.4125$, $x_e=0.792$, $V(x_e)=E$ | correct |
| `polar.html` | $T=(1/r_0^2-1/r_{max}^2)/2$ reaches $r_{max}$; $\theta=\theta_0-at$ runs clockwise; arrow on the linear-part panel points down at $(r,0)$, matching $\dot y=-ax$ | correct |
| `phase3.html` | Separatrix directions and all four arrows agree with the flow (cos = 1.000). Nullclines and the forbidden corner $1+x+y<0$ are correct. Spirals: finding 3 | see #3 |
| `plane.html` | Region polygons, labels and points A(1, −¾) and B(−½, ¾) are correct | see #4 |
| `chars.html` | Panel (a) is correct; panel (b): see #2 | see #2 |
| Steppers | None of these widgets has a stepper (all six are static), so there were no frames to check. | n/a |
| Live site | All 5 pages load with 0 KaTeX errors and no raw `$…$`. All 6 widgets render. All 13 anchors linked from the problem map exist on their target pages. The live text matches the local notes (spot check of finding 1). The live PDF md5 equals the local one. | correct |

Scripts: `check/sym.py` (sympy) and `check/run.js` (node widget runner), next to this file. Screenshots: `check/phase3.png`, `check/chars.png`.
