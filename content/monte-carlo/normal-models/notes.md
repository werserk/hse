**Как обновить знание о среднем и дисперсии нормальных данных?** Это глава 4: вторая половина лекции 3, слайды 17–30. Глава продолжает [«Байесовский вывод»](../bayesian-inference/): там априорное, правдоподобие, апостериорное, краевое правдоподобие (evidence) и предсказательные распределения разобраны на бете и кнопке, здесь та же схема работает для нормальных данных. Нужны [нормальное распределение](../distributions/#4-нормальное-распределение) и [гамма-распределение](../distributions/#гамма-сумма-показательных) из «Распределений», [преобразования СВ](../random-variables/#4-преобразования-случайных-величин) из «Случайных величин». Оценка максимального правдоподобия и её состоятельность (слайды 31–37) — в кейсе [«ОМП и состоятельность»](../mle-consistency/).

**Сквозной пример — гемоглобин пациента.** Истинный уровень гемоглобина пациента $\theta$ (г/л) неизвестен. Прибор показывает его с независимой нормальной ошибкой: показание $y\sim\mathcal N(\theta,\sigma^2)$. По популяции известно, что гемоглобин около 140 г/л с разбросом 10. Четыре показания одного пациента:

$$
\boldsymbol y=(120,\ 127,\ 116,\ 125),\quad \bar y=122,\quad s^2=\tfrac13\big(2^2+5^2+6^2+3^2\big)=\tfrac{74}{3}\approx24{,}7 .
$$

Глава отвечает на четыре вопроса: что известно о $\theta$ после одного показания (раздел 1) и после четырёх (раздел 2); как оценить ошибку прибора $\sigma^2$ по эталонному образцу (раздел 3); что делать, если неизвестны и $\theta$, и $\sigma^2$ (разделы 4–5). Раздел 6 объясняет, почему все сопряжённые пары курса устроены одинаково.

## 1. Одно наблюдение: нормальное среднее с нормальным априорным

**Модель** (слайд 17). Дисперсия прибора $\sigma^2$ известна, неизвестно только среднее $\theta$:

$$
y\mid\theta\sim\mathcal N(\theta,\sigma^2)\ \ \text{— правдоподобие},\qquad \theta\sim\mathcal N(\mu,\tau^2)\ \ \text{— априорное}.
$$

Числа $\mu,\tau,\sigma$ заданы заранее и называются **гиперпараметрами** модели. В примере $\mu=140$, $\tau=10$, $\sigma=5$, и прибор показал $y=120$. Лектор называет эту модель «смесью нормальных распределений»: $y$ — нормальное со случайным средним, как [смеси из «Распределений»](../distributions/#5-смеси-распределение-со-случайным-параметром). Принятое название — **нормально-нормальная модель**. Рис. 1.1 показывает все её объекты на одной оси, формулы идут следом.

<figure markdown>
<iframe class="widget" data-src="widgets/update.html" data-zoom="1.05"></iframe>
<figcaption>Рис. 1.1. Нормально-нормальная модель на одном показании $y=120$. Параметр $\theta$ и показания измеряются в одних единицах, поэтому все пять кривых лежат на одной оси. Кнопки «дальше ▶» и номера шагов добавляют кривые.</figcaption>
</figure>

**Совместная плотность.** Перемножаем две нормальные плотности, константы уходят в $\propto$:

$$
p(y,\theta;\mu,\tau,\sigma)=\mathcal N(y;\theta,\sigma^2)\,\mathcal N(\theta;\mu,\tau^2)\propto\exp\Big(-\frac{(y-\theta)^2}{2\sigma^2}-\frac{(\theta-\mu)^2}{2\tau^2}\Big).
$$

### а) Краевое правдоподобие

Краевое правдоподобие (КФП) — плотность показания до того, как известно $\theta$: $p(y)=\int p(\theta,y)\,d\theta$. Интеграл можно не считать. Запишем показание как $y=\theta+\varepsilon$, где $\varepsilon=y-\theta\sim\mathcal N(0,\sigma^2)$ — ошибка прибора, она не зависит от $\theta$. Тогда $\mathcal N(y;\theta,\sigma^2)=\mathcal N(y-\theta;0,\sigma^2)$, и интеграл — формула **свёртки**, плотности суммы двух независимых СВ:

$$
\begin{aligned}
p(y)&=\int_{-\infty}^{+\infty}\mathcal N(y-\theta;0,\sigma^2)\,\mathcal N(\theta;\mu,\tau^2)\,d\theta\\
&=\mathcal N(y;\,0+\mu,\ \sigma^2+\tau^2)=\mathcal N(y;\mu,\sigma^2+\tau^2).
\end{aligned}
$$

Последнее равенство — теорема о сумме независимых нормальных СВ: сумма нормальна, средние и дисперсии складываются ([свойство (c)](../distributions/#4-нормальное-распределение)). Смысл: показание разбросано и из-за пациента ($\tau^2$), и из-за прибора ($\sigma^2$). В примере $p(y)=\mathcal N(120;140,125)\approx0{,}0072$ (шаг 2 рис. 1.1).

### б) Апостериорное: выделить полный квадрат

По Байесу $p(\theta\mid y)=p(y,\theta)/p(y)$. Знаменатель уже известен, поэтому у лектора в показателе три слагаемых:

$$
p(\theta\mid y)\propto\exp\Big(-\frac{(y-\theta)^2}{2\sigma^2}-\frac{(\theta-\mu)^2}{2\tau^2}+\frac{(y-\mu)^2}{2(\sigma^2+\tau^2)}\Big).
$$

Показатель — квадратный трёхчлен по $\theta$, а экспонента от квадратного трёхчлена с отрицательным старшим коэффициентом — нормальная плотность. Найдём её параметры, выделив полный квадрат. Раскроем скобки, собирая степени $\theta$:

$$
\begin{aligned}
\frac{(y-\theta)^2}{\sigma^2}+\frac{(\theta-\mu)^2}{\tau^2}
&=\underbrace{\Big(\frac1{\sigma^2}+\frac1{\tau^2}\Big)}_{1/U^2}\theta^2-2\theta\Big(\frac y{\sigma^2}+\frac\mu{\tau^2}\Big)+\frac{y^2}{\sigma^2}+\frac{\mu^2}{\tau^2}\\
&=\frac{(\theta-M)^2}{U^2}+\underbrace{\frac{y^2}{\sigma^2}+\frac{\mu^2}{\tau^2}-\frac{M^2}{U^2}}_{\text{не зависит от }\theta},
\end{aligned}
$$

$$
U^2=\Big(\frac1{\sigma^2}+\frac1{\tau^2}\Big)^{-1},\qquad M=U^2\Big(\frac y{\sigma^2}+\frac\mu{\tau^2}\Big)=\frac{\dfrac y{\sigma^2}+\dfrac\mu{\tau^2}}{\dfrac1{\sigma^2}+\dfrac1{\tau^2}} .
$$

Второе равенство проверяется раскрытием $(\theta-M)^2/U^2=\theta^2/U^2-2\theta M/U^2+M^2/U^2$: член с $\theta$ совпадает, потому что $M/U^2=y/\sigma^2+\mu/\tau^2$. Остаток упрощается. Приведём к общему знаменателю, учитывая $U^2=\frac{\sigma^2\tau^2}{\sigma^2+\tau^2}$:

$$
\begin{aligned}
\frac{y^2}{\sigma^2}+\frac{\mu^2}{\tau^2}-\frac{M^2}{U^2}
&=\frac{(y^2\tau^2+\mu^2\sigma^2)(\sigma^2+\tau^2)-(y\tau^2+\mu\sigma^2)^2}{\sigma^2\tau^2(\sigma^2+\tau^2)}\\
&=\frac{\sigma^2\tau^2(y-\mu)^2}{\sigma^2\tau^2(\sigma^2+\tau^2)}=\frac{(y-\mu)^2}{\sigma^2+\tau^2}.
\end{aligned}
$$

В числителе $y^2\tau^4$ и $\mu^2\sigma^4$ сокращаются, остаётся $\sigma^2\tau^2(y^2-2y\mu+\mu^2)$. Подставляем в показатель: остаток $-\frac{(y-\mu)^2}{2(\sigma^2+\tau^2)}$ взаимно уничтожается с третьим слагаемым лектора, и

$$
p(\theta\mid y)\propto\exp\Big(-\frac{(\theta-M)^2}{2U^2}\Big)\quad\Rightarrow\quad\theta\mid y\sim\mathcal N(M,U^2).
$$

> Слайды 17–18: у лектора в ответе лишний множитель $\exp\big(-\frac{\mu^2}{2\tau^2}\big)$. Он от $\theta$ не зависит, так что под знаком $\propto$ ответ верен, но выкладка выше показывает, что весь остаток равен нулю.

Заодно получилось тождество, из которого следуют и а), и б):

$$
\mathcal N(y;\theta,\sigma^2)\,\mathcal N(\theta;\mu,\tau^2)=\underbrace{\mathcal N(\theta;M,U^2)}_{p(\theta\mid y)}\ \underbrace{\mathcal N(y;\mu,\sigma^2+\tau^2)}_{p(y)} .
$$

Нормирующие константы тоже сходятся: $\sigma^2\tau^2=U^2(\sigma^2+\tau^2)$.

**Как читать ответ.** Величину, обратную дисперсии, называют **точностью** (precision). Формула для $U^2$ говорит: точность апостериорного — сумма точностей априорного и измерения. Формула для $M$ — взвешенное среднее показания и априорного среднего с весами-точностями:

$$
M=w\,y+(1-w)\,\mu,\qquad w=\frac{1/\sigma^2}{1/\sigma^2+1/\tau^2}=\frac{\tau^2}{\sigma^2+\tau^2}.
$$

В примере точности $1/25=0{,}04$ и $1/100=0{,}01$, сумма $0{,}05$, поэтому $U^2=20$, $U\approx4{,}47$, $w=0{,}8$ и $M=0{,}8\cdot120+0{,}2\cdot140=124$ (шаг 4 рис. 1.1). Апостериорное уже обеих кривых: $U<\sigma<\tau$. Это та же картина, что у беты: [прогноз — взвешенное среднее априорного и данных](../bayesian-inference/#8-влияние-априорного-и-выбор-гиперпараметров), только вместо счётчиков веса задают точности.

### в) Апостериорное предсказательное

Какое показание $\tilde y$ даст прибор при следующем измерении того же пациента (слайд 18)? По [общей формуле](../bayesian-inference/#5-предсказательные-распределения) усредняем $p(\tilde y\mid\theta)$ по апостериорному. Новое показание при известном $\theta$ не зависит от старого, поэтому

$$
\begin{aligned}
p(\tilde y\mid y)&=E_{\theta\mid y}\big[p(\tilde y\mid\theta)\big]=\int_{-\infty}^{+\infty}\mathcal N(\tilde y-\theta;0,\sigma^2)\,\mathcal N(\theta;M,U^2)\,d\theta\\
&=\mathcal N(\tilde y;M,\sigma^2+U^2).
\end{aligned}
$$

Это та же свёртка, что в пункте а), только вместо априорного $\mathcal N(\mu,\tau^2)$ стоит апостериорное $\mathcal N(M,U^2)$: $\tilde y=\theta+\tilde\varepsilon$. Дисперсия прогноза складывается из шума прибора $\sigma^2$ и оставшейся неуверенности в $\theta$, $U^2$. В примере $\tilde y\mid y\sim\mathcal N(124,45)$, стандартное отклонение $6{,}71$ (шаг 5).

## 2. Несколько наблюдений и неинформативный предел

**Модель** (слайд 19): $n$ независимых показаний $y_i\mid\theta\sim\mathcal N(\theta,\sigma^2)$, $i=1,\dots,n$, то же априорное $\theta\sim\mathcal N(\mu,\tau^2)$. Обозначения выборки:

$$
\bar y=\frac1n\sum_{i=1}^ny_i,\qquad s^2=\frac1{n-1}\sum_{i=1}^n(y_i-\bar y)^2 .
$$

**Главный шаг — разложить сумму квадратов.** Правдоподобие — произведение $n$ нормальных плотностей, в показателе сумма $\sum_i(y_i-\theta)^2$. Добавим и вычтем $\bar y$:

$$
\begin{aligned}
\sum_{i=1}^n(y_i-\theta)^2&=\sum_{i=1}^n\big((y_i-\bar y)+(\bar y-\theta)\big)^2\\
&=\sum_{i=1}^n(y_i-\bar y)^2+2(\bar y-\theta)\underbrace{\sum_{i=1}^n(y_i-\bar y)}_{=0}+n(\bar y-\theta)^2\\
&=(n-1)s^2+n(\bar y-\theta)^2 .
\end{aligned}
$$

Перекрёстный член исчез, потому что отклонения от среднего в сумме дают ноль. Это разложение понадобится ещё дважды, в разделах 3 и 5. В примере $74+4(122-\theta)^2$.

**Совместная плотность.** Подставим разложение:

$$
p(\theta,\boldsymbol y)\propto\exp\Big(-\frac{(n-1)s^2}{2\sigma^2}\Big)\exp\Big(-\frac{(\bar y-\theta)^2}{2\sigma^2/n}-\frac{(\theta-\mu)^2}{2\tau^2}\Big).
$$

Первый множитель от $\theta$ не зависит. Второй — ровно показатель раздела 1, где $y$ заменён на $\bar y$, а $\sigma^2$ — на $\sigma^2/n$. Поэтому тождество раздела 1 сразу даёт ответ лектора:

$$
p(\theta,\boldsymbol y)\propto\exp\Big(-\frac{(n-1)s^2}{2\sigma^2}\Big)\exp\Big(-\frac{(\bar y-\mu)^2}{2(\tau^2+\sigma^2/n)}\Big)\exp\Big(-\frac{(\theta-M)^2}{2U^2}\Big),
$$

$$
U^2=\Big(\frac n{\sigma^2}+\frac1{\tau^2}\Big)^{-1},\qquad M=\frac{\dfrac{n\bar y}{\sigma^2}+\dfrac\mu{\tau^2}}{\dfrac n{\sigma^2}+\dfrac1{\tau^2}} .
$$

У лектора средний множитель записан как $\exp\big(-\frac{n(\bar y-\mu)^2}{2(n\tau^2+\sigma^2)}\big)$, и показатель при $(\theta-M)^2$ как $\frac{n\tau^2+\sigma^2}{2\tau^2\sigma^2}$. Это те же выражения: домножьте числитель и знаменатель на $n$ и заметьте $\frac{n\tau^2+\sigma^2}{\tau^2\sigma^2}=\frac n{\sigma^2}+\frac1{\tau^2}=\frac1{U^2}$.

**б) Апостериорное.** От $\theta$ зависит только последний множитель:

$$
p(\theta\mid\boldsymbol y)=\mathcal N(\theta;M,U^2).
$$

Каждое показание добавляет к точности $1/\sigma^2$. В примере $1/U^2=4/25+1/100=0{,}17$, $U\approx2{,}43$, $M\approx123{,}06$: вес данных $0{,}16/0{,}17\approx0{,}94$.

**а) Краевое правдоподобие.** Интегрируем совместную плотность по $\theta$, теперь с константами $(2\pi\sigma^2)^{-n/2}$ от правдоподобия и $(2\pi\tau^2)^{-1/2}$ от априорного. Гауссов интеграл $\int e^{-(\theta-M)^2/2U^2}d\theta=\sqrt{2\pi U^2}$, поэтому

$$
p(\boldsymbol y)=(2\pi\sigma^2)^{-n/2}\,\frac U\tau\,\exp\Big(-\frac{(n-1)s^2}{2\sigma^2}\Big)\exp\Big(-\frac{(\bar y-\mu)^2}{2(\tau^2+\sigma^2/n)}\Big).
$$

Данные входят в неё только через $\bar y$ и $s^2$. Лектор называет $(\bar y,s^2)$ достаточными статистиками. Точнее: пара $(\bar y,s^2)$ достаточна для $(\theta,\sigma^2)$ вместе (раздел 5), а при известной $\sigma^2$ для $\theta$ достаточно одного $\bar y$: множитель с $s^2$ от $\theta$ не зависит и в апостериорном сократился. Второй экспоненциальный множитель — плотность $\bar y\sim\mathcal N(\mu,\tau^2+\sigma^2/n)$ с точностью до константы: это пункт а) раздела 1 для одного «наблюдения» $\bar y$ с дисперсией $\sigma^2/n$.

Апостериорное предсказательное для $n$ наблюдений — пункт в) раздела 1 с новыми $M,U^2$: $\tilde y\mid\boldsymbol y\sim\mathcal N(M,\sigma^2+U^2)$.

### Предельные переходы к неинформативному априорному

**Неинформативное** (noninformative) априорное почти ничего не говорит о параметре до данных. Слайд 20 получает его двумя предельными переходами (рис. 2.1).

<figure markdown>
<iframe class="widget" data-src="widgets/plots.html" data-mode="limits" data-zoom="1.05"></iframe>
<figcaption>Рис. 2.1. Два пути к $\mathcal N(\bar y,\sigma^2/n)$ на данных примера. а) Априорное расплывается, $\tau\to\infty$: $M$ уходит от априорного среднего 140 к $\bar y=122$. б) Данных всё больше при $\tau=10$: доля априорного в $M$ исчезает, а $U$ сравнивается с $\sigma/\sqrt n$.</figcaption>
</figure>

- **а) $\tau\to\infty$, $n$ фиксировано.** Точность априорного $1/\tau^2\to0$, поэтому $U^2\to\sigma^2/n$ и $M\to\frac{n\bar y/\sigma^2}{n/\sigma^2}=\bar y$.
- **б) $n\to\infty$, $\tau$ фиксировано.** Слагаемое $n/\sigma^2$ растёт и подавляет $1/\tau^2$. Вес априорного в $M$ равен $\frac{1/\tau^2}{n/\sigma^2+1/\tau^2}\to0$, поэтому $M-\bar y\to0$ и $U^2\cdot n/\sigma^2\to1$.

В обоих случаях

$$
p(\theta\mid\boldsymbol y;\sigma)\approx\mathcal N\Big(\theta;\ \bar y,\ \frac{\sigma^2}n\Big).
$$

Тот же ответ даёт априорное $p(\theta)\propto1$ на всей прямой: тогда $p(\theta\mid\boldsymbol y)\propto e^{-n(\bar y-\theta)^2/2\sigma^2}$. Такое априорное — **неправильное** (improper): интеграл $\int d\theta$ бесконечен, плотностью оно не является. Апостериорное при этом нормируется. В примере это $\mathcal N(122;\,6{,}25)$ со стандартным отклонением $2{,}5$. Случай б) — частный случай общей теоремы Бернштейна–фон Мизеса: при большом $n$ апостериорное забывает априорное ([«ОМП и состоятельность»](../mle-consistency/#5-байесовская-оценка-теорема-бернштейнафон-мизеса)).

## 3. Неизвестная дисперсия при известном среднем: обратное χ²

Как оценить ошибку прибора $\sigma^2$? Возьмём **эталонный образец** с известным уровнем $\theta=150$ г/л и измерим его пять раз (слайд 21):

$$
\boldsymbol z=(146,\ 153,\ 149,\ 157,\ 145),\qquad z_i-\theta=(-4,\ 3,\ -1,\ 7,\ -5).
$$

В формулах раздела данные, как на слайде, обозначены $\boldsymbol y$; в примере это $\boldsymbol z$.

Теперь $\theta$ известно, а неизвестная $\sigma^2$ — случайная величина. Лектор называет $\theta$ «гиперпараметром модели».

**Правдоподобие как функция $\sigma^2$.** Это произведение $n$ нормальных плотностей:

$$
p(\boldsymbol y\mid\sigma^2;\theta)=\prod_{i=1}^n\frac1{\sqrt{2\pi\sigma^2}}e^{-\frac{(y_i-\theta)^2}{2\sigma^2}}\propto(\sigma^2)^{-\frac n2}\exp\Big(-\frac{n}{2\sigma^2}v\Big),\qquad v=\frac1n\sum_{i=1}^n(y_i-\theta)^2 .
$$

Данные входят только через $v$, средний квадрат отклонения от известного среднего, поэтому $v$ — достаточная статистика. В примере $v=(16+9+1+49+25)/5=20$.

**Какое априорное сопряжено.** Как функция $\sigma^2$ правдоподобие — степень $\sigma^2$, умноженная на $e^{-c/\sigma^2}$. Произведение двух таких функций снова такого вида: степени складываются, коэффициенты при $1/\sigma^2$ тоже. Плотность этого вида — **обратное гамма-распределение** (inverse gamma). Если $X\sim\mathrm{Gamma}(\alpha,\beta)$ с интенсивностью $\beta$ (в «Распределениях» гамма записана через масштаб $\theta=1/\beta$), то $1/X\sim\text{Inv-Gamma}(\alpha,\beta)$. Его плотность получается [заменой переменной](../random-variables/#4-преобразования-случайных-величин) $x=1/y$, $|dx/dy|=1/y^2$:

$$
p(y)=\frac{\beta^\alpha}{\Gamma(\alpha)}\Big(\frac1y\Big)^{\alpha-1}e^{-\beta/y}\cdot\frac1{y^2}=\frac{\beta^\alpha}{\Gamma(\alpha)}\,y^{-(\alpha+1)}e^{-\beta/y},
$$

$$
p(\sigma^2)=\text{Inv-Gamma}(\sigma^2;\alpha,\beta)\propto(\sigma^2)^{-(\alpha+1)}e^{-\beta/\sigma^2}.
$$

**Масштабированное обратное χ²** (scaled inverse chi-squared) — то же семейство в параметрах, удобных для дисперсии. Пусть $X\sim\chi^2_{\nu_0}$, тогда

$$
Y=\frac{\nu_0\sigma_0^2}{X}\sim\text{Inv-}\chi^2(\nu_0,\sigma_0^2),\qquad
p(\sigma^2;\nu_0,\sigma_0^2)\propto\Big(\frac{\sigma_0^2}{\sigma^2}\Big)^{\frac{\nu_0}2+1}\exp\Big(-\frac{\nu_0\sigma_0^2}{2\sigma^2}\Big).
$$

$\nu_0$ — **число степеней свободы**, $\sigma_0^2$ — **масштаб**. Откуда формула: $\chi^2_\nu=\mathrm{Gamma}(\nu/2,\ 1/2)$ с интенсивностью $1/2$ (слайд 26, раздел 5), при делении на $\nu_0\sigma_0^2$ интенсивность умножается на $\nu_0\sigma_0^2$. Значит, $X/(\nu_0\sigma_0^2)\sim\mathrm{Gamma}\big(\frac{\nu_0}2,\frac{\nu_0\sigma_0^2}2\big)$, а обратная к ней величина $Y$ распределена как $\text{Inv-Gamma}\big(\frac{\nu_0}2,\frac{\nu_0\sigma_0^2}2\big)$. Подставляем $\alpha=\nu_0/2$, $\beta=\nu_0\sigma_0^2/2$ в формулу выше.

> Слайд 21: в определении и в обеих плотностях стоит $\sigma_0$ там, где должно быть $\sigma_0^2$: $Y=\nu_0\sigma_0^2/X$, $\exp\big(-\frac{\nu_0\sigma_0^2}{2\sigma^2}\big)$, а в ответе $\nu_0\sigma_0^2+nv$. Интеграл в знаменателе берётся по $\sigma^2$ от 0, а не от $-\infty$. Та же опечатка с $\sigma_0$ повторяется в напоминании об $\text{Inv-}\chi^2$ на слайдах 23–24.

**Апостериорное.** Перемножаем и складываем показатели:

$$
p(\sigma^2\mid\boldsymbol y;\theta)\propto(\sigma^2)^{-\frac n2}e^{-\frac{nv}{2\sigma^2}}\cdot(\sigma^2)^{-(\frac{\nu_0}2+1)}e^{-\frac{\nu_0\sigma_0^2}{2\sigma^2}}
=(\sigma^2)^{-(\frac{\nu_0+n}2+1)}\exp\Big(-\frac{\nu_0\sigma_0^2+nv}{2\sigma^2}\Big),
$$

$$
\sigma^2\mid\boldsymbol y\sim\text{Inv-}\chi^2\Big(\nu_0+n,\ \frac{\nu_0\sigma_0^2+nv}{\nu_0+n}\Big).
$$

Справа ядро $\text{Inv-}\chi^2$: степень $-(\nu/2+1)$ при $\nu=\nu_0+n$, и в экспоненте $\nu\cdot(\text{масштаб})$ при масштабе $\frac{\nu_0\sigma_0^2+nv}{\nu_0+n}$.

**Как читать.** Априорное ведёт себя как $\nu_0$ воображаемых измерений со средним квадратом отклонения $\sigma_0^2$. Степени свободы складываются как числа измерений, а новый масштаб — взвешенное среднее $\sigma_0^2$ и $v$ с весами $\nu_0$ и $n$. Это та же арифметика, что у беты с её [воображаемыми бросками](../bayesian-inference/#8-влияние-априорного-и-выбор-гиперпараметров).

<figure markdown>
<iframe class="widget" data-src="widgets/plots.html" data-mode="invchi2" data-zoom="1.05"></iframe>
<figcaption>Рис. 3.1. Калибровка прибора по эталону. Априорное «как будто 4 прошлых измерения со средним квадратом 25» и пять новых показаний с $v=20$ дают $\text{Inv-}\chi^2(9;\,22{,}2)$.</figcaption>
</figure>

В примере возьмём $\nu_0=4$, $\sigma_0^2=25$: производитель обещает ошибку около 5 г/л, но уверен в этом, как будто сделал всего 4 измерения. Тогда $\nu=9$, масштаб $(4\cdot25+5\cdot20)/9\approx22{,}2$. Полезные моменты (через $\text{Inv-Gamma}(\alpha,\beta)$: среднее $\beta/(\alpha-1)$, мода $\beta/(\alpha+1)$):

$$
E(\sigma^2)=\frac{\nu}{\nu-2}\,\sigma_\nu^2\ \ (\nu>2),\qquad \text{мода}=\frac{\nu}{\nu+2}\,\sigma_\nu^2 ,
$$

где $\sigma_\nu^2$ — масштаб. У апостериорного среднее $28{,}6$, мода $18{,}2$. Распределение скошено вправо (рис. 3.1): большие $\sigma^2$ данные исключают хуже, чем малые.

При $\nu_0\to0$ априорное становится $p(\sigma^2)\propto1/\sigma^2$, а апостериорное — $\text{Inv-}\chi^2(n,v)$. Это неинформативное априорное для дисперсии; оно вернётся в разделе 5.

## 4. Краевые апостериорные: избавиться от лишнего параметра

Пусть параметров два, $\theta=(\theta_1,\theta_2)$, а интересует только $\theta_1$. Второй параметр тогда **мешающий** (nuisance). Например, нужен гемоглобин пациента, а ошибка прибора неизвестна. Ответ — **краевое апостериорное** $p(\theta_1\mid\boldsymbol y)$, интеграл совместного апостериорного по $\theta_2$ (слайд 22):

$$
p(\theta\mid\boldsymbol y)\propto p(\boldsymbol y\mid\theta_1,\theta_2)\,p(\theta_1,\theta_2),\qquad
p(\theta_2\mid\boldsymbol y)\propto\int_{\Theta_1}p(\boldsymbol y\mid\theta_1,\theta_2)\,p(\theta_1,\theta_2)\,d\theta_1 .
$$

Множитель пропорциональности в обеих формулах — $1/p(\boldsymbol y)$. Лектор пишет «проп. $p^{-1}(\boldsymbol y)$».

Слайд разбирает случай, когда $p(\theta_2\mid\boldsymbol y)$ считается аналитически, а $p(\theta_1\mid\boldsymbol y)$ — нет. Тогда нужна ещё **условная** плотность $\theta_1$ при фиксированном $\theta_2$:

$$
p(\theta_1\mid\theta_2,\boldsymbol y)=\frac{p(\boldsymbol y,\theta_1\mid\theta_2)}{p(\boldsymbol y\mid\theta_2)}=\frac{p(\boldsymbol y,\theta_1,\theta_2)}{p(\theta_2)}\cdot\frac{p(\theta_2)}{p(\boldsymbol y,\theta_2)}\propto\frac{p(\boldsymbol y\mid\theta_1,\theta_2)\,p(\theta_1,\theta_2)}{p(\theta_2\mid\boldsymbol y)} .
$$

Первое равенство — определение условной плотности, второе — расписали обе дроби через совместную плотность, в третьем $p(\boldsymbol y,\theta_2)=p(\theta_2\mid\boldsymbol y)\,p(\boldsymbol y)$. На практике это значит: закрепить $\theta_2$, прочитать совместное апостериорное как функцию $\theta_1$ и нормировать.

Теперь краевое — среднее условных плотностей по апостериорному $\theta_2$, и его можно оценить **методом Монте-Карло**:

$$
\begin{aligned}
p(\theta_1\mid\boldsymbol y)&=\int_{\Theta_2}p(\theta_1\mid\theta_2,\boldsymbol y)\,p(\theta_2\mid\boldsymbol y)\,d\theta_2=E_{\theta_2\mid\boldsymbol y}\big[p(\theta_1\mid\theta_2,\boldsymbol y)\big]\\
&\approx\frac1N\sum_{j=1}^Np(\theta_1\mid\theta_2^{(j)},\boldsymbol y),\qquad\theta_2^{(j)}\sim p(\theta_2\mid\boldsymbol y).
\end{aligned}
$$

Первое равенство — формула полной вероятности для плотностей. Приближение — замена ожидания средним по $N$ независимым розыгрышам: по закону больших чисел оно сходится к ожиданию. Подробно метод Монте-Карло — в лекции 5. Шаг 4 рис. 5.1 делает это для нормальной модели.

> Слайд 22 (добавлен в v2): перед суммой пропущен множитель $1/N$. Без него получается не среднее, а сумма, которая растёт с $N$.

## 5. Оба параметра неизвестны: неинформативное априорное и распределение Стьюдента

Теперь неизвестны и гемоглобин $\theta$, и ошибка прибора $\sigma^2$, а есть только четыре показания пациента (слайды 23–29). Модель: $y_i\mid\theta,\sigma^2\sim\mathcal N(\theta,\sigma^2)$, $i=1,\dots,n$.

**Неинформативное априорное.** Лектор берёт $\theta$ и $\ln\sigma^2$ равномерными на всей прямой: $\theta,\ln(\sigma^2)\sim U[-\infty,\infty]$, то есть $p(\theta,\ln\sigma^2)\propto1$. Для $\theta$ это «любое среднее одинаково возможно». Для дисперсии равномерен логарифм, потому что $\sigma^2$ — масштаб: при смене единиц $\sigma^2\to c\,\sigma^2$ логарифм лишь сдвигается на $\ln c$, и равномерное на прямой остаётся равномерным. Переход к плотности по $\sigma^2$ — замена переменной с якобианом $\big|\frac{d\ln\sigma^2}{d\sigma^2}\big|=\frac1{\sigma^2}$:

$$
p(\theta,\sigma^2)\propto\frac1{\sigma^2}.
$$

Это неправильное априорное (improper uninformative prior): его интеграл бесконечен. Апостериорное при этом нормируется, если $n\ge2$ и не все $y_i$ равны (слайд 27: «неправильная апр-ФПВ может приводить к правильной пост-ФПВ»).

**Совместное апостериорное.** Правдоподобие $n$ наблюдений даёт $(\sigma^2)^{-n/2}$, априорное — ещё $(\sigma^2)^{-1}$, сумму квадратов раскладываем как в разделе 2:

$$
\begin{aligned}
p(\theta,\sigma^2\mid\boldsymbol y)&\propto\frac1{\sigma^2}\cdot\frac1{\sigma^n}\exp\Big(-\frac{\sum_i(y_i-\theta)^2}{2\sigma^2}\Big)\\
&=(\sigma^2)^{-(\frac n2+1)}\exp\Big(-\frac{(n-1)s^2+n(\bar y-\theta)^2}{2\sigma^2}\Big).
\end{aligned}
$$

Данные входят только через $\bar y$ и $s^2$.

<figure markdown>
<iframe class="widget" data-src="widgets/student.html" data-zoom="1.05"></iframe>
<figcaption>Рис. 5.1. Откуда берётся распределение Стьюдента. Сверху — совместное апостериорное $p(\theta,\sigma^2\mid\boldsymbol y)$ для четырёх показаний пациента и краевое по $\sigma^2$ справа. Снизу — плотности $\theta$: срезы, их среднее по Монте-Карло, точный ответ. Кнопки «дальше ▶» и номера шагов добавляют слои.</figcaption>
</figure>

### Краевое апостериорное дисперсии

Интегрируем по $\theta$ (слайд 23). Множитель $(\sigma^2)^{-(n/2+1)}e^{-(n-1)s^2/2\sigma^2}$ от $\theta$ не зависит и выносится, остаётся гауссов интеграл с дисперсией $\sigma^2/n$:

$$
\begin{aligned}
p(\sigma^2\mid\boldsymbol y)&\propto(\sigma^2)^{-(\frac n2+1)}e^{-\frac{(n-1)s^2}{2\sigma^2}}\int_{-\infty}^{\infty}e^{-\frac{n(\bar y-\theta)^2}{2\sigma^2}}d\theta=\sqrt{\frac{2\pi\sigma^2}n}\,(\sigma^2)^{-(\frac n2+1)}e^{-\frac{(n-1)s^2}{2\sigma^2}}\\
&\propto(\sigma^2)^{-(\frac{n-1}2+1)}e^{-\frac{(n-1)s^2}{2\sigma^2}} .
\end{aligned}
$$

Множитель $\sqrt{\sigma^2}$ поднял степень на $1/2$: $-\frac n2-1+\frac12=-\big(\frac{n-1}2+1\big)$. Сравниваем с ядром из раздела 3:

$$
\sigma^2\mid\boldsymbol y\sim\text{Inv-}\chi^2(n-1,\ s^2).
$$

Это ответ раздела 3 при $\nu_0\to0$, но с $n-1$ степенями свободы вместо $n$ и с $s^2$ вместо $v$: одна степень свободы ушла на то, что среднее $\theta$ пришлось оценить через $\bar y$. В примере $\text{Inv-}\chi^2(3;\,24{,}7)$ (шаг 2 рис. 5.1).

> Слайд 23: гауссов интеграл равен $\sqrt{2\pi\sigma^2/n}$, на слайде $\sqrt{2\pi\sigma^2}$. Множитель $\sqrt n$ от $\sigma^2$ не зависит, поэтому ответ верен.

### Условное апостериорное среднего

Делим совместное на краевое (слайд 24). Всё, кроме множителя с $\theta$, сокращается:

$$
p(\theta\mid\sigma^2,\boldsymbol y)=\frac{p(\theta,\sigma^2\mid\boldsymbol y)}{p(\sigma^2\mid\boldsymbol y)}\propto\exp\Big(-\frac{n(\bar y-\theta)^2}{2\sigma^2}\Big)\quad\Rightarrow\quad\theta\mid\sigma^2,\boldsymbol y\sim\mathcal N\Big(\bar y,\frac{\sigma^2}n\Big).
$$

При известной $\sigma^2$ это ответ раздела 2 с плоским априорным. Получилась схема из раздела 4: сначала $\sigma^2\sim\text{Inv-}\chi^2(n-1,s^2)$, потом $\theta\mid\sigma^2\sim\mathcal N(\bar y,\sigma^2/n)$. Отсюда оценка Монте-Карло слайда 24 (шаги 3–4 рис. 5.1):

$$
p(\theta\mid\boldsymbol y)=E_{\sigma^2\mid\boldsymbol y}\big[p(\theta\mid\sigma^2,\boldsymbol y)\big]\approx\frac1N\sum_{j=1}^N\mathcal N\Big(\theta;\bar y,\frac{\sigma_j^2}n\Big),\qquad\sigma_j^2\sim\text{Inv-}\chi^2(n-1,s^2).
$$

> Слайд 24: нормирующая константа $\mathcal N(\theta;\bar y,\sigma^2/n)$ равна $\sqrt{n/(2\pi\sigma^2)}$, на слайде $1/\sqrt{2\pi\sigma^2}$.

### Краевое апостериорное среднего: распределение Стьюдента

Теперь возьмём интеграл по $\sigma^2$ явно (слайд 25). Обозначим $A=(n-1)s^2+n(\theta-\bar y)^2$, от $\sigma^2$ оно не зависит:

$$
p(\theta\mid\boldsymbol y)\propto\int_0^\infty(\sigma^2)^{-(\frac n2+1)}e^{-\frac{A}{2\sigma^2}}\,d\sigma^2 .
$$

Замена $z=\frac{A}{2\sigma^2}$ превращает интеграл в гамма-функцию. Выразим всё через $z$:

- $\sigma^2=\frac A{2z}$, поэтому $(\sigma^2)^{-(\frac n2+1)}=\big(\frac{2z}A\big)^{\frac n2+1}$;
- $d\sigma^2=-\frac A{2z^2}\,dz$, а пределы $\sigma^2:0\to\infty$ переходят в $z:\infty\to0$; минус уходит при перестановке пределов.

$$
\int_0^\infty\Big(\frac2A\Big)^{\frac n2+1}z^{\frac n2+1}e^{-z}\,\frac A2\,\frac1{z^2}\,dz=\Big(\frac2A\Big)^{\frac n2}\int_0^\infty z^{\frac n2-1}e^{-z}dz=\Big(\frac2A\Big)^{\frac n2}\Gamma\Big(\frac n2\Big)\propto A^{-\frac n2}.
$$

Делим $A$ на постоянную $(n-1)s^2$, от этого меняется только константа:

$$
p(\theta\mid\boldsymbol y)\propto\Big(1+\frac{n(\theta-\bar y)^2}{(n-1)s^2}\Big)^{-\frac n2}.
$$

Это ядро **распределения Стьюдента** (Student's t). Плотность $t_\nu$ (слайд 26):

$$
t_\nu(x)=\frac{\Gamma\big(\frac{\nu+1}2\big)}{\sqrt{\pi\nu}\,\Gamma\big(\frac\nu2\big)}\Big(1+\frac{x^2}\nu\Big)^{-\frac{\nu+1}2}=\frac1{\sqrt\nu\,\mathrm B\big(\frac12,\frac\nu2\big)}\Big(1+\frac{x^2}\nu\Big)^{-\frac{\nu+1}2}.
$$

Положим $\nu=n-1$ и $x=\frac{\theta-\bar y}{s/\sqrt n}$. Тогда $\frac{x^2}\nu=\frac{n(\theta-\bar y)^2}{(n-1)s^2}$ и $\frac{\nu+1}2=\frac n2$, ядра совпадают:

$$
p(\theta\mid\boldsymbol y)=t_{n-1}\Big(\theta;\ \bar y,\ \frac s{\sqrt n}\Big),\qquad\frac{\theta-\bar y}{\sqrt{s^2/n}}\ \Big|\ \boldsymbol y\sim t_{n-1}.
$$

Третий аргумент в $t_{n-1}(\theta;\bar y,s/\sqrt n)$ — **масштаб** (стандартное отклонение сдвинутого распределения), а не дисперсия, как в $\mathcal N(\theta;\bar y,\sigma^2/n)$.

> Слайд 25 называет это «нецентрированным распределением Стьюдента». Точнее — сдвинутое и масштабированное: $\theta=\bar y+\frac s{\sqrt n}T$, $T\sim t_{n-1}$. Нецентральным распределением Стьюдента (noncentral t) называют другое распределение.

**Определение Стьюдента и короткая проверка.** На слайде 26: если $X\sim\mathcal N(0,1)$ и $V\sim\chi^2_\nu$ независимы, то $T=X/\sqrt{V/\nu}\sim t_\nu$. Здесь $\chi^2_\nu$ — сумма квадратов $\nu$ независимых стандартных нормальных, $\chi^2_\nu(x)=\mathrm{Gamma}(x;\nu/2,1/2)=\frac1{2^{\nu/2}\Gamma(\nu/2)}x^{\nu/2-1}e^{-x/2}$. При $\nu\to\infty$ знаменатель $\sqrt{V/\nu}\to1$ и $t_\nu\to\mathcal N(0,1)$. Наш ответ получается из этого определения без интегралов. Двухшаговая схема даёт $\theta=\bar y+\frac\sigma{\sqrt n}X$ с $X\sim\mathcal N(0,1)$, независимой от $\sigma^2$. По разделу 3 $\sigma^2=\frac{(n-1)s^2}V$ с $V\sim\chi^2_{n-1}$. Значит,

$$
\frac{\theta-\bar y}{s/\sqrt n}=\frac{\sigma}{s}X=\frac{X}{\sqrt{V/(n-1)}}\sim t_{n-1}.
$$

Смысл слов лектора «смешанное распределение»: Стьюдент — нормальные колокола $\mathcal N(\bar y,\sigma^2/n)$, усреднённые по неизвестной $\sigma^2$. Колокола с большими $\sigma^2$ дают тяжёлые хвосты (шаги 4–5 рис. 5.1).

**В примере.** $\theta\mid\boldsymbol y\sim t_3(122;\,2{,}48)$. 95 %-ный интервал $122\pm t_{3;\,0{,}975}\cdot2{,}48=122\pm3{,}18\cdot2{,}48$, то есть $[114{,}1;\ 129{,}9]$. Если бы $\sigma=5$ была известна, было бы $\mathcal N(122;\,6{,}25)$ и интервал $122\pm4{,}9=[117{,}1;\ 126{,}9]$. За неизвестную $\sigma$ платим шириной: при $n=4$ хвост $P(\theta>130\mid\boldsymbol y)$ равен $0{,}024$ против $0{,}0007$.

### Сравнение с классической статистикой

Слайд 27 сравнивает с известным результатом классической статистики:

$$
\text{байес:}\quad\frac{\theta-\bar y}{\sqrt{s^2/n}}\ \Big|\ \boldsymbol y\sim t_{n-1},\qquad\qquad
\text{классика:}\quad T=\frac{\bar y-\theta}{\sqrt{s^2/n}}\ \Big|\ \theta,\sigma^2\sim t_{n-1}.
$$

Формулы совпадают, а случайное в них разное. В классике $\theta$ и $\sigma^2$ фиксированы, случайны данные: $T$ — статистика выборки, её распределение не зависит от неизвестной $\sigma^2$. В байесовском ответе данные фиксированы, случайно $\theta$. Поэтому при плоском априорном 95 %-ный байесовский интервал численно равен классическому доверительному интервалу $\bar y\pm t_{n-1;\,0{,}975}\,s/\sqrt n$. Подробно о двух точках зрения — в [«ОМП и состоятельность»](../mle-consistency/#1-две-точки-зрения-на-параметр).

### Апостериорное предсказательное

Какое показание даст прибор в следующий раз, если неизвестны и $\theta$, и $\sigma^2$ (слайды 28–29)? Добавим новое $\tilde y\mid\theta,\sigma^2\sim\mathcal N(\theta,\sigma^2)$ в совместную плотность. Его плотность даёт ещё $(\sigma^2)^{-1/2}$ и множитель с $(\tilde y-\theta)^2$:

$$
\begin{aligned}
p(\tilde y,\theta,\sigma^2,\boldsymbol y)\propto{}&(\sigma^2)^{-(\frac{n+1}2+1)}\exp\Big(-\frac{(n-1)s^2}{2\sigma^2}\Big)\\
&\times\exp\Big(-\frac{n(\bar y-\theta)^2}{2\sigma^2}\Big)\exp\Big(-\frac{(\tilde y-\theta)^2}{2\sigma^2}\Big).
\end{aligned}
$$

**Шаг 1: интеграл по $\theta$.** Отделим $(\sigma^2)^{-1}$ и два последних множителя. С точностью до константы $2\pi/\sqrt n$ это $\mathcal N(\theta;\bar y,\sigma^2/n)\,\mathcal N(\tilde y-\theta;0,\sigma^2)$: у произведения двух плотностей как раз множитель $\sqrt n/(2\pi\sigma^2)$. Интеграл по $\theta$ — свёртка, как в разделе 1:

$$
\int_{-\infty}^{\infty}\mathcal N\Big(\theta;\bar y,\frac{\sigma^2}n\Big)\mathcal N(\tilde y-\theta;0,\sigma^2)\,d\theta=\mathcal N\Big(\tilde y;\ \bar y,\ \sigma^2\Big(\frac1n+1\Big)\Big).
$$

Остаётся степень $(\sigma^2)^{-(\frac{n+1}2+1)+1}=(\sigma^2)^{-(\frac{n-1}2+1)}$, как у лектора.

**Шаг 2: интеграл по $\sigma^2$.** Нормальная плотность $\tilde y$ даёт ещё $(\sigma^2)^{-1/2}$, и подынтегральное принимает вид раздела 5 с другим $A$:

$$
\begin{aligned}
p(\tilde y\mid\boldsymbol y)&\propto\int_0^\infty(\sigma^2)^{-\frac n2-1}\exp\Big(-\frac{(n-1)s^2+\big(\frac1n+1\big)^{-1}(\tilde y-\bar y)^2}{2\sigma^2}\Big)d\sigma^2\\
&\propto\Big(1+\frac{\big(\frac1n+1\big)^{-1}(\tilde y-\bar y)^2}{(n-1)s^2}\Big)^{-\frac n2}.
\end{aligned}
$$

Та же замена $z=A/2\sigma^2$ дала $A^{-n/2}$. Это ядро Стьюдента с масштабом $s\sqrt{1+1/n}$:

$$
p(\tilde y\mid\boldsymbol y)=t_{n-1}\Big(\tilde y;\ \bar y,\ s\sqrt{\tfrac1n+1}\Big).
$$

Под корнем $s^2$ — разброс прибора, $s^2/n$ — неуверенность в $\theta$, как $\sigma^2+U^2$ в разделе 1. В примере масштаб $4{,}97\cdot\sqrt{1{,}25}\approx5{,}55$, 95 %-ный интервал для следующего показания $[104{,}3;\ 139{,}7]$.

## 6. Экспоненциальное семейство: откуда сопряжённые пары

Бета для бросков, нормальное для среднего, обратное χ² для дисперсии устроены одинаково: апостериорное — это априорное с прибавленной достаточной статистикой. Слайд 30 объясняет, почему.

**Экспоненциальное семейство** (exponential family) — распределения, правдоподобие которых записывается как

$$
p(D\mid\boldsymbol\theta)=h(D)\exp\big(\boldsymbol\theta^T\boldsymbol s(D)-\psi(\boldsymbol\theta)\big),
$$

$$
\boldsymbol\theta^T=(\theta_1,\dots,\theta_m),\quad\boldsymbol s(D)^T=(s_1(D),\dots,s_m(D)).
$$

- $\boldsymbol\theta$ — **естественный параметр**; он бывает функцией привычного параметра.
- $\boldsymbol s(D)$ — достаточная статистика. От данных правдоподобие зависит через $\boldsymbol s(D)$ и множитель $h(D)$, а $h(D)$ от $\boldsymbol\theta$ не зависит. Поэтому $\boldsymbol s$ достаточна в смысле [главы 3](../bayesian-inference/#10-достаточная-статистика-и-сопряжённые-априорные).
- $\psi(\boldsymbol\theta)=\ln\int h(D)\,e^{\boldsymbol\theta^T\boldsymbol s(D)}dD$ — нормировка, с ней плотность интегрируется в 1.

**Пример 1 — броски кнопки.** Серия $D_n$ с $n_h$ «головами», вероятность «головы» $q$:

$$
q^{n_h}(1-q)^{n-n_h}=\exp\Big(n_h\ln\frac q{1-q}+n\ln(1-q)\Big):
$$

$$
\theta=\ln\frac q{1-q},\quad s(D)=n_h,\quad\psi(\theta)=n\ln(1+e^\theta),\quad h=1.
$$

Естественный параметр — логарифм шансов; $\ln(1-q)=-\ln(1+e^\theta)$.

**Пример 2 — нормальное с известной $\sigma^2$.** Раскроем квадрат в $\prod_i\mathcal N(y_i;\theta,\sigma^2)$:

$$
(2\pi\sigma^2)^{-\frac n2}e^{-\frac{\sum_iy_i^2}{2\sigma^2}}\cdot\exp\Big(\theta\,\frac{\sum_iy_i}{\sigma^2}-\frac{n\theta^2}{2\sigma^2}\Big):\qquad s(D)=\frac{\sum_iy_i}{\sigma^2},\quad\psi(\theta)=\frac{n\theta^2}{2\sigma^2}.
$$

**Сопряжённое априорное.** Возьмём априорное того же вида, что правдоподобие как функция $\boldsymbol\theta$, с гиперпараметрами $\boldsymbol\alpha$ и $\gamma$:

$$
p(\boldsymbol\theta\mid\boldsymbol\alpha,\gamma)\propto\exp\big(\boldsymbol\theta^T\boldsymbol\alpha-\gamma\,\psi(\boldsymbol\theta)\big).
$$

При умножении на правдоподобие показатели складываются:

$$
p(\boldsymbol\theta\mid D,\boldsymbol\alpha,\gamma)\propto\exp\big(\boldsymbol\theta^T(\boldsymbol\alpha+\boldsymbol s(D))-(\gamma+1)\psi(\boldsymbol\theta)\big)=p\big(\boldsymbol\theta\mid\boldsymbol\alpha+\boldsymbol s(D),\ \gamma+1\big).
$$

Это общий вид обновления «гиперпараметры плюс достаточная статистика» из главы 3. $\boldsymbol\alpha$ копит статистики, $\gamma$ считает, сколько наборов данных такого же размера, как $D$, уже учтено (с воображаемыми включительно).

> Слайд 30: $\psi$ записана для всего набора $D$, поэтому $\gamma$ растёт на 1. Часто $\psi_1$ пишут для одного наблюдения. Тогда для $n$ независимых наблюдений $\boldsymbol s(D)=\sum_i\boldsymbol s(x_i)$, $\psi=n\psi_1$, и обновление $\gamma\to\gamma+n$.

**Проверка на примере 2.** Априорное $\exp\big(\theta\alpha-\gamma\frac{n\theta^2}{2\sigma^2}\big)$ — нормальное по $\theta$ с точностью $\frac{\gamma n}{\sigma^2}$ и $\frac{\text{среднее}}{\text{дисперсия}}=\alpha$. Сопоставим с $\mathcal N(\mu,\tau^2)$: $\frac1{\tau^2}=\frac{\gamma n}{\sigma^2}$, $\frac\mu{\tau^2}=\alpha$. После обновления точность $\frac{(\gamma+1)n}{\sigma^2}=\frac1{\tau^2}+\frac n{\sigma^2}=\frac1{U^2}$, а $\alpha+\frac{\sum_iy_i}{\sigma^2}=\frac\mu{\tau^2}+\frac{n\bar y}{\sigma^2}=\frac M{U^2}$. Это ответ раздела 2.

**Проверка на примере 1** (с $\psi_1=\ln(1+e^\theta)$ на один бросок). Априорное $e^{\theta\alpha}(1+e^\theta)^{-\gamma}$ перепишем через $q$: $e^\theta=\frac q{1-q}$, $1+e^\theta=\frac1{1-q}$, а якобиан $\frac{d\theta}{dq}=\frac1{q(1-q)}$. Получаем плотность по $q$, пропорциональную $q^{\alpha-1}(1-q)^{\gamma-\alpha-1}$, то есть $\text{Beta}(\alpha,\gamma-\alpha)$. Обновление $\alpha\to\alpha+n_h$, $\gamma\to\gamma+n$ даёт $\text{Beta}(\alpha+n_h,\ \gamma-\alpha+n_t)$ — [обновление беты из главы 3](../bayesian-inference/#4-апостериорное-прибавить-счётчики) с $\alpha_h=\alpha$, $\alpha_t=\gamma-\alpha$.

Члены семейства со слайда и их сопряжённые априорные:

| Правдоподобие | Достаточная статистика | Сопряжённое априорное | Где |
|---|---|---|---|
| биномиальное (известное $n$) | $n_h$ | бета | глава 3 |
| мультиномиальное | счётчики $\boldsymbol n$ | Дирихле | глава 3 |
| Пуассона | $\sum_ix_i$ | гамма | [«Байес для параметра»](../bayes-conjugate/) |
| экспоненциальное, гамма (известная форма) | $\sum_ix_i$ | гамма | — |
| нормальное, известная $\sigma^2$ | $\sum_iy_i$ | нормальное | разделы 1–2 |
| нормальное, известное $\theta$ | $\sum_i(y_i-\theta)^2$ | $\text{Inv-}\chi^2$ | раздел 3 |

В последней строке естественный параметр — $-\frac1{2\sigma^2}$, а не сама $\sigma^2$.

## План устного ответа

**Нормально-нормальная модель, одно наблюдение**

1. Модель: $y\mid\theta\sim\mathcal N(\theta,\sigma^2)$, $\theta\sim\mathcal N(\mu,\tau^2)$, гиперпараметры $\mu,\tau,\sigma$; совместная плотность (рис. 1.1).
2. КФП: $y=\theta+\varepsilon$, свёртка, сумма независимых нормальных, $\mathcal N(y;\mu,\sigma^2+\tau^2)$.
3. Апостериорное: показатель с тремя слагаемыми, полный квадрат по $\theta$, остаток $\frac{(y-\mu)^2}{\sigma^2+\tau^2}$ сокращается; $\mathcal N(M,U^2)$; точности складываются, $M$ — взвешенное среднее.
4. Пост-ПФПВ: $E_{\theta\mid y}[p(\tilde y\mid\theta)]$, та же свёртка с апостериорным, $\mathcal N(M,\sigma^2+U^2)$.

**Несколько наблюдений и неинформативный предел**

1. Разложение $\sum(y_i-\theta)^2=(n-1)s^2+n(\bar y-\theta)^2$, перекрёстный член равен нулю.
2. Сведение к одному наблюдению $\bar y$ с дисперсией $\sigma^2/n$; три множителя совместной плотности; $U^2=(n/\sigma^2+1/\tau^2)^{-1}$, $M$.
3. КФП с константами; достаточные статистики $\bar y$, $s^2$.
4. Пределы $\tau\to\infty$ и $n\to\infty$; $\mathcal N(\bar y,\sigma^2/n)$; неправильное априорное $p(\theta)\propto1$ (рис. 2.1).

**Неизвестная дисперсия при известном среднем**

1. Правдоподобие $(\sigma^2)^{-n/2}e^{-nv/2\sigma^2}$, достаточная статистика $v$.
2. Inv-Gamma и $\text{Inv-}\chi^2(\nu_0,\sigma_0^2)$: определение через $\chi^2$, плотность, вывод заменой переменной.
3. Апостериорное $\text{Inv-}\chi^2\big(\nu_0+n,\frac{\nu_0\sigma_0^2+nv}{\nu_0+n}\big)$; смысл $\nu_0$ и $\sigma_0^2$ (рис. 3.1).

**Оба параметра неизвестны**

1. Априорное $\theta,\ln\sigma^2\sim U$, якобиан, $p\propto1/\sigma^2$, неправильное.
2. Совместное апостериорное; $p(\sigma^2\mid\boldsymbol y)=\text{Inv-}\chi^2(n-1,s^2)$ через гауссов интеграл.
3. $p(\theta\mid\sigma^2,\boldsymbol y)=\mathcal N(\bar y,\sigma^2/n)$; краевые через условные и Монте-Карло с $1/N$ (рис. 5.1).
4. $p(\theta\mid\boldsymbol y)$: замена $z=A/2\sigma^2$, $A^{-n/2}$, $t_{n-1}(\bar y,s/\sqrt n)$; определение $t_\nu$ и $\chi^2_\nu$; сравнение с классическим $T$.
5. Пост-ПФПВ $t_{n-1}(\bar y,s\sqrt{1+1/n})$.

**Экспоненциальное семейство**

1. Форма $h(D)\exp(\boldsymbol\theta^T\boldsymbol s(D)-\psi(\boldsymbol\theta))$; примеры Бернулли и нормальное.
2. Сопряжённое $\exp(\boldsymbol\theta^T\boldsymbol\alpha-\gamma\psi)$, обновление $(\boldsymbol\alpha+\boldsymbol s(D),\gamma+1)$; проверка на нормальном.

## Обозначения лекции

| Объект | Лекция 3 | Здесь |
|---|---|---|
| гиперпараметры в записи | $p(\theta\mid y;\mu,\tau,\sigma)$: после «;» — известные числа | в формулах после раздела 1 часто опущены |
| параметры апостериорного | $M$, $U^2$ | так же; $w$ — вес данных |
| обратное χ² | $\text{Inv-}\chi^2(\nu_0,\sigma_0^2)$, Inv-Gamma$(\alpha,\beta)$ | так же; $\beta$ — интенсивность гаммы (в «Распределениях» масштаб $\theta=1/\beta$) |
| Стьюдент | $t_{n-1}(\theta;\bar y,s/\sqrt n)$: третий аргумент — масштаб | так же; у $\mathcal N(\cdot;m,v)$ второй аргумент — дисперсия |
| КФП, апрФПВ, пост-ФПВ, пост-ПФПВ | краевая функция правдоподобия, априорная, апостериорная, апостериорная предсказательная ФПВ | краевое правдоподобие, априорное, апостериорное, предсказательное |
| экспоненциальное семейство | $\boldsymbol\theta$, $\boldsymbol s(D)$, $\psi(\theta)$, $h(D)$; $\boldsymbol\alpha,\gamma$ | так же; в примере 1 $q$ — вероятность «головы» |

## Источники

Курс «Стохастические модели и методы Монте-Карло» (НИУ ВШЭ, А. Д. Неверов), лекция 3 «Введение в байесовскую статистику», слайды 17–30 (версия 2). Лектор ссылается на A. Gelman et al., *Bayesian Data Analysis*, 3rd ed. (CRC Press), где те же модели разобраны в главах 2–3. Пример с гемоглобином, все числа, розыгрыши Монте-Карло (фиксированное зерно генератора) и выкладки, которых нет на слайдах (сокращение остатка, КФП для $n$ наблюдений с константами, вывод Стьюдента из определения, проверки экспоненциального семейства), — собственные; числа пересчитаны в коде виджетов.
