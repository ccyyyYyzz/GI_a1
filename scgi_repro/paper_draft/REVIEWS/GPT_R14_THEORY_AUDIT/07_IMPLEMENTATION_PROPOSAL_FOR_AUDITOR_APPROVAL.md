# R15 修订实施提案：供审核 agent 批准

基准提交：402c8d6db9d8fc4dce225700f0b6a3561885009e  
分支：scgi-ceiling-diagnostic-r1  
提案性质：**只供审核，尚未授权实施**  
实施者：Codex  
审核者职责：只审核本方案和后续 diff，不直接改稿

## 一、请求审核的结论

我建议保留论文的核心贡献，但收窄它的逻辑合同：

> Acquisition design determines whether gain–object separation is algebraically identifiable or statistically recoverable. Under explicit carrier, window, and estimator assumptions, scoped gain estimators attain finite-window or interior rates, and their residual errors propagate through a basis-dependent reconstruction identity.

这仍保留四条主线：

1. 方阵设计的代数不可识别性；
2. 高矩形设计的已证明局部/全局充分阈值；
3. 随机载波下相对增益的统计恢复；
4. 残余增益误差到重建误差的传播与设计选择。

我不会继续维持以下过宽表述：

- 普通局部可识别性与 Jacobian 满秩“当且仅当”；
- 对任意三角阵载波，仅凭逐行有限常数即可一致估计；
- 混合噪声、Gaussian、blind high-count 与 oracle Poisson 共用一个无条件 minimax 定理；
- 使用 median(pair_sum) 的实现直接验证 true-S1 的 F.7；
- noisy Gaussian ratio 的读噪声风险精确等于 2 sigma squared / S2；
- same-record overlapping-window 盲估计器可被一个标量 v_blind 精确概括；
- 正交反演在所有高矩形/冗余设计中普遍最优。

## 二、建议直接批准的四个关键取舍

### 决策 A：Theorem D 采用固定 Gaussian 实验

**建议：批准。**

不建立“所有 mixing noise laws 上的统一 minimax 定理”。Theorem D 改为：

> 在 iid Gaussian noise、明确 gauge-fixed Hölder/Sobolev 类、可行内部带宽条件下，匹配阶数的窗口或局部多项式估计器达到 minimax rate；有限 N 时使用带 one-frame/interior/full-record 饱和的包络。

理由：这是证明成本最低、量词最清楚、不会损伤论文主要信息的版本。一般 mixing law 仍保留上界，不再声称其固定实验下的匹配下界。

主文 Theorem D 将严格限定在已证明的 interior regime。有限 N 三段包络只有在附录中同时明确定义并证明以下对象后才称为 minimax equivalence：

- gauge slice；
- 参数类及其有限直径/低阶多项式分量约束；
- pointwise 或 integrated loss；
- feasible bandwidth set；
- Gaussian noise normalization；
- matching upper 与 lower bounds。

若上述任一环节不能在本轮完整证明，则附录只保留有证明的 finite-N lower bound、trivial upper caps 和 regime discussion，不把它们合并成“精确三段 minimax 等价”。

### 决策 B：known-zero 结果降级为 rank-conditional

**建议：批准。**

主文不再宣称仅凭 K0 >= p - 1 就“generic restore ordinary local identifiability”。改为：

- K0 >= p - 1 是 quotient Jacobian 满列秩的必要维数条件；
- 实际充分性由显示的 rank condition 决定；
- 满秩推出普通局部可识别；
- 普通局部可识别的精确条件是 gauge-fixed nonlinear support map 的零点孤立；
- 不再把维数条件称为普通局部可识别的必要条件。

理由：无需再补一条依赖 witness 的泛化证明，而且与 R14 的 3 维和 5 维高阶反例完全兼容。

### 决策 C：Prop. 3 使用双估计器验证

**建议：批准。**

不改变生产管线的 median(pair_sum) 行为。新增一个明确的 theorem-faithful true-S1 QA arm：

- true-S1 arm：验证 F.7/F.8；
- median-normalized arm：验证实际生产估计器，并使用含 gamma = S1hat/S1 的精确误差式；
- 两臂使用同一对象、同一 OU path、同一 raw metric；
- 文稿分别报告约 1.020/1.037 与 1.044/1.200 的 boundary factor，不再混称。

理由：保留工程实现，同时得到真正的 same-estimator theory validation。

### 决策 D：重建桥以 raw metric 为定理主指标

**建议：批准。**

- Theorem 1 和 Prop. 3 的主验证统一使用 raw relative MSE；
- scale-aligned relMSE 保留为图像质量的次级指标，明确不用于验证 raw identity；
- Fig. 9、caption、结果 summary 和 runner 输出同步标注；
- 若当前图内不同 arm 使用不同 metric，则重出受影响面板，不用文字掩盖。

理由：这是消除 figure–text–runner 漂移的最直接方案。

## 三、我准备实施的修改

## WP1 — 先修附录中的数学合同

目标文件：

- paper_draft/latex/appendix_body.tex
- paper_draft/APPENDICES.md

准备修改：

1. **Corollary 2**
   - 将 iff 限定为 differential identifiability；
   - 普通局部充分性保留 Taylor/immersion 证明；
   - 精确普通局部条件写为 nonlinear zero isolation；
   - 半径改为 min{1, gamma / C_H}；
   - K0 维数计数只用于 differential full-rank；
   - 删除“普通局部必需一零点/漂移维度”的表述。

2. **Theorem B**
   - 显式写出 triangular-array 下标；
   - 点态结论要求目标窗口实际方差趋零；
   - uniform-in-n 结论要求窗口方差上确界趋零；
   - sigma_abs,N squared / W_N 作为可检查的充分条件；
   - 同时要求实际 deterministic window bias 趋零，例如 L_N(W_N/N) to the power beta tends to zero；
   - 截断窗、单边窗和边界窗的一般结论限定 beta <= 1；beta > 1 只有在对称矩消除成立或给出已定义并证明的边界局部多项式估计器时才声明；
   - B2b 的 beta0 放回 block length；
   - long-run variance 使用 additive remainder；三角阵极限增加 uniform covariance-tail 条件；
   - “only ambiguity”限定为 bucket-only centered-gain estimand，不推广到完整 joint pattern–bucket experiment。

3. **Theorem C / Appendix D.4**
   - 分离 blind high-count 与 oracle-known-carrier Poisson 两个实验；
   - D.8 保持 finite-window master bound；
   - general arbitrary-carrier theorem 限定 beta <= 1；
   - beta > 1 只保留 sensitivity-balanced/internal-window 或已证明 local-polynomial 情形；
   - 在定理陈述中加入跨帧 conditional count independence；
   - 修正 Remark D.4.1 的 log-gain theta、safe interval 和 Poisson mean；
   - alpha-to-zero/plain-log 改为明确 joint limit；
   - D.9 写成 feasible-window infimum，power law 只在内部 optimizer 和统一 sensitivity 下出现。

4. **Theorem D**
   - 采用决策 A 的 fixed-Gaussian 版本；
   - 主定理只声称已证明的 interior minimax rate；
   - D.5 改为有证明的 finite-N lower-bound envelope，并分别列出 direct-observation/class-diameter upper caps；
   - 只有在固定 gauge slice、参数类、loss、feasible bandwidth 和 noise scale 下补齐 matching upper/lower proof 后，才将三种饱和区间写成 minimax equivalence；
   - 对 beta > 1，若低阶多项式 nullspace 未被约束，则不声称完整 finite-N 三段包络；
   - Gaussian submodel 不再被用于声称每个 fixed mixing law 的下界；
   - van Trees/Pinsker 段改成有标准定理支撑的 rate-level statement，或保留 Assouad 主证明；不再把截断独立 Gaussian prior 的两句话称为完整证明；
   - finite-window correlated Gaussian CRB 先写 exact 1-transpose Sigma-inverse 1，再给有条件的 LRV 渐近式。

## WP2 — 主文收窄到与附录完全一致

目标文件：

- paper_draft/latex/abstract.tex
- paper_draft/latex/body.tex
- paper_draft/MANUSCRIPT_DRAFT.md

准备修改：

1. Abstract、Introduction、Conclusion 不再把 B–D 合并成一个无条件“blind minimax optimal”结论。
2. Theorem B 主文补 triangular-array rate condition。
3. Theorem C 主文分成 blind high-count 与 oracle Poisson 两个部分或两个命名结果。
4. Theorem D 主文明确 fixed iid Gaussian experiment 和 interior/finite-N scope。
5. Corollary 2 主文改成 differential rank criterion + ordinary-local sufficiency。
6. N = K + p - 1 边界与真正 below-wall failure 分开叙述；stationarity/support/sparsity 只列为附加信息的非穷尽例子。
7. “orthogonal is the best conduit”改成“本稿比较中的 unit-leverage square benchmark”；注明冗余设计可有 B_L < 1。
8. P_col/D ensemble whitening、P_row acquisition-order exchangeability、fixed draw deterministic sequence 三种语义统一。
9. signed coefficient 与 physical nonnegative Poisson acquisition 分开。本轮采取最低风险方案：**删除 signed orthogonal transform 的 direct-Poisson specialization**。F.2 的 exact Poisson 式只用于非负 physical measurements；互补掩模或 positive-offset 路径必须使用其单独推导的 photon allocation 和差分 covariance，不能沿用旧 signed F.6 Poisson 项。

## WP3 — 修正 Appendix F 和 Prop. 3 合同

目标文件：

- paper_draft/latex/appendix_body.tex
- paper_draft/APPENDICES.md
- paper_draft/latex/body.tex
- paper_draft/MANUSCRIPT_DRAFT.md

准备修改：

1. 保留 true-S1 的 F.7/F.8。
2. 增加或紧邻给出 estimated-S1 恒等式：

\[
\widehat c_k-c_k
=S_1\frac{2x_k(\gamma-1)-\Delta_k(1-x_k)(\gamma+x_k)}
{2+\Delta_k(1-x_k)}
=\gamma e_{k,\mathrm{F.7}}+(\gamma-1)c_k.
\]

3. 当前 40/40 crossing 改称 production-estimator robustness check。
4. true-S1 arm 改称 same-estimator validation，并更新 slope/boundary 数字。
5. noisy ratio read-noise：
   - fixed/noiseless normalization 才保留 exact linear term；
   - unregularized Gaussian ratio 明确无 finite second moment；
   - high-SNR 公式写全适用条件和 common-gain factor；
   - clamped implementation 标记为 regularization-dependent。
6. Prop. 3 主文使用 general Gamma_blind；
   - scalar specialization仅用于 exogenous、centered、frame-uncorrelated residual；
   - same-record arm 报告 raw q_delta、mean、projected temporal covariance 和 residual–noise cross term，或明确称 conditional proxy。
7. 删除或改写不能由 raw 数据支持的 “empirical -2.11 versus predicted -2.07”。

## WP4 — 最小代码和实验补充

原则：不重写生产算法，只增加 theorem-contract QA。

建议新增：

- run_prop3_estimator_contract_r15.py
- tests/test_r15_theory_contract.py
- results/prop3_estimator_contract_r15/

可能需要同步修改：

- run_prop3_raw_metric_export.py
- run_prop3_boundary.py
- run_prop3_verdict_tables.py
- run_paper_fig4_bridge.py
- paper_draft/latex/make_pub_figures.py

实施内容：

1. 增加 true_s1 与 median_pair_sum 明确开关；
2. 对 true-S1 arm 做 coefficient-wise F.7 regression test；
3. 对 median arm 验证 gamma 恒等式；
4. 导出 gamma、(gamma-1) squared、normalization–increment cross term；
5. 导出 q_delta_raw、m_delta、projected covariance/cross term；
6. Prop. 3 两臂在同一 OU traces 上重跑；
7. Fig. 9 所有 theorem-validation arm 改用统一 raw metric；
8. 审核批准后先从未提交修改生成明确标记为 provisional 的 QA 结果；不把它们称为 submission-authoritative。
9. 只有用户另行授权 commit 后，才从该 clean commit 重跑 submission-authoritative 结果并生成最终 v2.1 manifest。

如果审核者认为 projected covariance 实验超出本轮必要范围，最低可接受降级是：

- same-record blind result只保留为 empirical conditional proxy；
- 不再声称它是 scalar theorem validation；
- oracle v = 0 skeleton 与 true-S1 pair law 仍完成严格闭环。

## WP5 — 图、caption、结果 summary 同步

准备修改：

- Fig. 9 及其 caption；
- Prop. 3 相关图表、caption 和 summary；
- results/paper_fig4_bridge_r2b/fig4_caption.md；
- results/prop3_raw_metric_r1 只作为历史结果，不覆盖原目录；
- results/paper_fig7_lowphoton_r5_final/summary.md 中 calibration/bisection 的 RMSE 单位；
- 主文和 supplement 中所有 raw/scale-aligned、oracle/blind、P_col/P_row 名称。

不会把旧结果原地改写为新结果；新跑数进入新目录并保留旧 provenance。

## WP6 — 最终同步与验收

实施完成后我会交给审核 agent：

1. 完整 git diff；
2. finding-by-finding closure ledger；
3. 两个反例为何不再矛盾新定理的说明；
4. Prop. 3 双估计器表格；
5. 新结果 manifest 和精确命令；
6. 全测试输出；
7. main/supplement 编译日志、页数和抽页视觉 QA；
8. risky-phrase grep 结果；
9. claim-to-evidence map，确保 Abstract/Introduction 不强于正文和附录。

最低验收门槛：

- R14 每个 High 和 Medium 均有 closure；
- 3 维、5 维和 triangular-array 反例要么被新假设排除，要么对应旧结论已删除；
- equation、estimator、normalization、metric、result directory 五者完全一致；
- 原有测试全绿，新 contract tests 全绿；
- 零 undefined reference、零 overfull、图文数字一致；
- tracked 改动只落在批准范围；
- 审核 agent 的批准只授权编辑、测试和 provisional 运行，不等于 commit/push 授权；
- 未经用户再次授权不 commit、不 push，也不把 provisional 结果标为 submission-authoritative。

## 四、本轮明确不做

- 不补硬件实验；
- 不建立所有 mixing laws 上的完整 sharp minimax 理论；
- 不替作者决定作者/单位块；
- 不替作者决定 supplement 长度策略；
- 不替作者确认 MIT 许可证；
- 不在审核通过前修改任何现有文件。

## 五、请审核 agent 按以下格式回复

你是本项目的**只读审核 agent**。请审核本提案，不要修改仓库、不要写代码、不要生成替代稿。

必须基于 HEAD 402c8d6 和 R14 审计文件 00–06，逐项判断：

1. 决策 A：fixed-Gaussian Theorem D — APPROVE / REVISE / REJECT
2. 决策 B：known-zero 降级为 rank-conditional — APPROVE / REVISE / REJECT
3. 决策 C：Prop. 3 true-S1 + median 双臂 — APPROVE / REVISE / REJECT
4. 决策 D：raw metric 作为定理验证主指标 — APPROVE / REVISE / REJECT
5. WP1–WP6 是否覆盖 R14 全部 High/Medium
6. 是否存在我准备删除但其实已证明、应该保留的结论
7. 是否存在会引入新数学错误、实验错配或不必要大改的步骤

最终只允许三种总裁决：

- **APPROVE AS WRITTEN**
- **APPROVE WITH CONDITIONS**：逐条列出实施前必须加入的条件
- **REJECT**：给出具体反例或文件/行号依据

请不要用“基本可以”“建议进一步看看”等模糊措辞。审核通过后，Codex 才开始修改；修改完成后仍由你做最终 diff 审核。
