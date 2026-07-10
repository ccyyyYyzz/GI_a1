# Counterexamples and proof notes

## 1. Corollary 2: differential failure does not force an exact local alias

Use

\[
H=\begin{pmatrix}
1&0&0\\
0&1&0\\
-1&2&1
\end{pmatrix},
\qquad
H^{-1}=\begin{pmatrix}
1&0&0\\
0&1&0\\
1&-2&1
\end{pmatrix},
\qquad
T=(1,1,0)^\top .
\]

Let the known support be Omega = {1,2}, let

\[
u=(-1,0,1)^\top,\qquad S=\operatorname{span}\{\mathbf 1,u\}.
\]

Then HT = (1,1,1) transpose, and the support-restricted first-order map has the non-gauge direction u in its kernel. Thus the proposed kernel = gauge necessity for ordinary local identifiability fails.

For the exact nonlinear support constraint used in the appendix, displacement t u gives

\[
F(tu)=e^t-2+e^{-t}=2(\cosh t-1)>0
\]

for every nonzero sufficiently small t. Hence there is no non-gauge exact alias along the only extra differential direction, even though the first-order kernel is larger than gauge. This is an isolated singular zero, as in solving x-squared = 0: derivative singularity does not imply failure of local identification of the zero set.

Every s in S has the form a times the all-ones vector plus t u, and the appendix's own gauge identity gives F(a times all-ones plus t u) = exp(-a) F(tu). Therefore F(s) = 0 if and only if t = 0: the example is ordinarily identifiable modulo gauge, not merely free of aliases along one selected curve.

**Safe theorem split**

1. Kernel = gauge is necessary and sufficient for differential identifiability.
2. Kernel = gauge implies ordinary local identifiability on a gauge slice by the immersion theorem.
3. Ordinary local identifiability holds exactly when zero is an isolated zero of the gauge-fixed nonlinear map. The converse from ordinary to differential identifiability is false.
4. The Taylor bound printed in the appendix proves a radius min{1, gamma / C_H}, because its remainder estimate assumes the infinity norm is at most one.

The count K0 >= p - 1 is likewise a count for differential full rank, not a necessary count for ordinary local identifiability. A concrete higher-order example is obtained with K = 5, Omega = {1,2,3,4}, and

\[
H^{-1}=
\begin{pmatrix}
1&0&0&0&0\\
0&1&0&0&0\\
0&0&1&0&0\\
0&0&0&1&0\\
1&1&1&1&-4
\end{pmatrix}.
\]

Let T = H^{-1} times the all-ones vector = (1,1,1,1,0) transpose, u = (1,-1,0,0,0) transpose, v = (0,0,1,-1,0) transpose, and S = span{all-ones,u,v}. There is only K0 = 1 known zero for p - 1 = 2 non-gauge directions, and the quotient Jacobian vanishes on both. Yet for s = a times all-ones + x u + y v,

\[
F(s)=2e^{-a}\{\cosh x+\cosh y-2\},
\]

which is zero only when x = y = 0. Ordinary identifiability modulo gauge holds even though differential identifiability fails.

## 2. Theorem B triangular-array counterexample

For row N, let K_N = N and take independent

\[
z_{N,n}\sim \mathcal N(0,N),\qquad n=1,\ldots,N,
\]

set ell = 0, and choose W_N = floor(sqrt(N)).

This is compatible with the positive-carrier log model while both K_N and N tend to infinity: take T_N to be the first coordinate vector, set the first coordinate of pattern n to exp(z_{N,n}), and let the unused coordinates be any positive variables. Then B_{N,n} = exp(z_{N,n}) and m_T = E log B_{N,n} = 0. The pattern law is allowed to vary along the triangular array.

For every fixed row:

- the process is centered, strictly stationary, and iid;
- it is alpha-mixing with zero lag-positive mixing coefficients;
- every 2+eta moment is finite;
- the absolute covariance sum is finite and equals sigma_abs,N squared = N.

The theorem’s window conditions hold:

\[
W_N\to\infty,\qquad W_N/N\to0.
\]

But

\[
\operatorname{Var}\left(W_N^{-1}\sum_{k=1}^{W_N}z_{N,k}\right)
=\frac{N}{W_N}\asymp \sqrt N,
\]

so the estimator is not consistent. The displayed term sigma_abs,N squared / W_N does not tend to zero.

**Correct array condition**

The exact pointwise L2 requirement is that the actual variance of the window at the claimed n tends to zero, together with vanishing smoothing bias; a uniform-in-n theorem needs the supremum of these variances to vanish. For equal-weight consecutive windows, a convenient sufficient condition is

\[
\frac{\sigma_{\mathrm{abs},N}^2}{W_N}\to0
\quad\text{and}\quad
L_N(W_N/N)^\beta\to0.
\]

A uniform-bound formulation is also acceptable, but the constants then must be explicitly uniform over N. If the signed long-run variance is used as an asymptotic constant for a changing row law, uniform covariance-tail tightness is additionally required; otherwise retain the exact finite-window covariance sum.

## 3. Finite-window form of the minimax comparison

The unconstrained interior optimizer

\[
W_0\asymp(\sigma^2/L_a^2)^{1/(2\beta+1)}
\]

is meaningful only when it lies inside the feasible window set and inside any gain-coherence constraint. A finite-N lower-bound form that retains the correct regimes is

\[
c_\beta\sup_{1\le W\le W_{\max}}
\min\{L_a^2W^{2\beta},\,\sigma^2/W\},
\]

up to the precise discrete Hölder-ball diameter and gauge convention. Equivalently, state the interior power law only when 1 is much less than W_0 and W_0 is much less than N, and give one-frame and full-record saturation outside that regime.

This correction is forced by a trivial estimator bound: for bounded finite-sample parameter diameter, risk cannot grow without limit as L_a grows, while the present D.5 right side can.

For the oracle-known-carrier soft-log estimator, keep (D.8) as the primary result and optimize only over

\[
\mathcal W_n=\{W:1\le W\le W_{\max},\ \underline\kappa_n(W)>0\}.
\]

Any simplified D.9 rate additionally needs uniform control of the sensitivity ratio kappa_max / underline-kappa and the beta/window moment conditions.

## 4. What a Gaussian submodel proves

For a fixed noise law F, define

\[
R_N(F)=\inf_{\hat\ell}\sup_{\ell\in H_\beta(L_a)}
\mathbb E_{\ell,F}L(\hat\ell,\ell).
\]

A lower bound under a Gaussian law G proves a bound for R_N(G), not for R_N(F) for every other fixed mixing law.

The Gaussian submodel proves a full-class lower bound only if the actual minimax experiment is defined as

\[
\inf_{\hat\ell}\sup_{P_z\in\mathcal Z}\sup_{\ell\in H_\beta(L_a)}
\mathbb E_{\ell,P_z}L(\hat\ell,\ell),
\]

where the class Z contains the Gaussian member and is normalized so that the upper bound holds uniformly. The low-cost alternative is to state Theorem D for the fixed iid Gaussian experiment.

## 5. Implemented S1 normalization changes (F.7)

Equation (F.7) uses true S1. Let the implementation use

\[
\widehat S_1=\gamma S_1
\]

and write x = c/S1. Direct algebra gives an additional global and cross-term contribution; one useful form of the coefficient error is

\[
\widehat c-c
=S_1\,
\frac{2x(\gamma-1)-\Delta(1-x)(\gamma+x)}
{2+\Delta(1-x)}.
\]

When gamma = 1 this reduces to (F.7). Otherwise the raw reconstruction risk contains the gauge term and its cross term with the differential-gain error. In scale-aligned loss much of the global term can disappear, which is exactly why a scale-aligned validation cannot silently stand in for the raw-MSE proposition.

**Safe validation design**

- oracle-S1 arm: exact check of (F.7)–(F.8);
- median-pair-sum arm: practical implementation result;
- if raw-MSE theory is desired for the latter, include the random gamma term and its covariance with Delta.

## 6. Gaussian noise in a random denominator

Specialize to the manuscript's paired estimator. Let

\[
R^+=\mu_+ + \epsilon_+,\qquad R^-=\mu_-+\epsilon_-,
\]

where epsilon-plus and epsilon-minus are independent equal-variance nondegenerate Gaussian read noises. Put U = R-plus minus R-minus and D = R-plus plus R-minus. The Gaussian noise parts of U and D are independent, Var(U) is positive, and D has positive density at zero. Therefore, conditioning on D,

\[
\mathbb E[(S_1U/D-c)^2\mid D]\ge S_1^2\operatorname{Var}(U)/D^2,
\]

whose expectation is infinite. Thus 2 sigma_read squared / S2 cannot be an exact unconditional MSE identity for this unregularized noisy ratio. The conclusion uses the noncancelling paired numerator; density of a denominator near zero alone would not prove divergence for an arbitrary ratio.

It can be:

- exact for a linear estimator with a fixed/noiseless normalization, under the stated independent-noise model; or
- a high-SNR delta-method approximation after expanding around a nonzero deterministic denominator.

For iid equal-variance read noise in gain-corrected units, common known unit gain, no differential pair-gain mismatch, and fixed true S1, that expansion gives coefficient variance approximately 2 sigma squared times (1 + x_k squared), hence the aggregate pair risk

\[
\frac{2\sigma^2}{S_2}\left(1+\frac{1}{K_{\mathrm{eff}}}\right),
\]

before accounting for noise in a global median normalization. If sigma_read is detector-domain noise under a common gain a, multiply this display by a to the power minus two. Unequal pair gains require the general delta-method expression. Clipping, an offset, or conditioning away from zero changes the estimator and must be included in the theorem; the resulting exact risk depends on the regularization and full denominator distribution.

## 7. Soft-log limit at zero offset

At fixed finite Poisson intensity lambda,

\[
P(C=0)=e^{-\lambda}>0.
\]

Therefore log(C + alpha) does not approach an integrable plain-log statistic as alpha tends to zero: the zero-count contribution grows like e^{-lambda} log(alpha). A safe limit is fixed alpha with lambda tending to infinity, or a joint limit satisfying an explicit condition such as

\[
e^{-\lambda}|\log\alpha|\to0.
\]

## 8. Exact overcomplete reconstruction can have leverage below one

Take one unknown coefficient, two repeated measurements, and their averaging left inverse:

\[
A=(1,1)^\top,\qquad L=(1/2,1/2),\qquad T=1.
\]

Then LA = 1, so the fixed-design reconstruction floor is zero. The carrier is b = AT = (1,1) transpose, S2 = 1, and

\[
B_L=\sum_{n=1}^{2} b_n^2\|Le_n\|_2^2
=\frac14+\frac14=\frac12<1.
\]

Thus square orthogonal inversion has unit leverage, but is not universally the minimum-leverage exact conduit. Any “best” statement needs a fixed frame/energy/noise-budget constraint and a comparison restricted to the named pipelines.

## 9. Centered-gain identification is not full object identification in the bucket-only marginal experiment

Let the illumination coordinates be iid and exchangeable, and compare two objects

\[
T=(1,2)^\top,\qquad T'=(2,1)^\top.
\]

For every frame, the random carriers I1 + 2 I2 and 2 I1 + I2 have the same distribution. With the same deterministic gain path, the marginal bucket-record laws used in Theorem B are therefore identical, although T-prime is not a scalar multiple of T. Theorem B can still consistently identify centered log-gain because that is a functional shared by these models. It cannot use that consistency to conclude that the full bucket-only model has only the one-dimensional scale ambiguity. If the realized illumination pattern is also observed, the joint (I,Y) experiment is richer and this coordinate-permutation example is not an alias; that experiment requires a separate identifiability statement.
