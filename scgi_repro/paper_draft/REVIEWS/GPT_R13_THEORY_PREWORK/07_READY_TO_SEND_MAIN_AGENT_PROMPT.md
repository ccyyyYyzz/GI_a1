# 可直接发送给主 Agent 的提示词

下面代码块中的内容可原样发送。

```text
请执行 R13 理论修复与投稿收口。你是负责实际集成的主 Agent；前置 Agent 已完成证明重建、GPT Pro 协作、独立复算和 QA，但遵守用户要求没有改动任何既有项目文件，只新增了旁路材料。

项目：
- GitHub: https://github.com/ccyyyYyzz/GI_a1
- 分支: scgi-ceiling-diagnostic-r1
- 前置包基准 HEAD: bcbb31254c343eb04e8cb96d7c3157bfc9818b36
- 本地项目根: E:\GAN_FCC_WORK\github_sync\GI_a1_scgi_20260709_014434\scgi_repro
- 前置包目录: E:\GAN_FCC_WORK\github_sync\GI_a1_scgi_20260709_014434\scgi_repro\paper_draft\REVIEWS\GPT_R13_THEORY_PREWORK

第一步必须重新检查当前 HEAD、origin 对齐和 git status。前置包锚定 bcbb312；若 HEAD 已前进，先按语义迁移，不得机械覆盖。工作树中原先已有的 Fig. 7 E5b caption/manifest 修改属于用户/其他 Agent，必须保留。不要 reset、checkout 或覆盖无关改动。

本任务允许你修改现有论文、Markdown 母本、必要的 runner/测试并新增 provenance 导出；但不要 commit/push，除非用户另行明确授权。

一、强制阅读顺序

1. 总入口：
E:\GAN_FCC_WORK\github_sync\GI_a1_scgi_20260709_014434\scgi_repro\paper_draft\REVIEWS\GPT_R13_THEORY_PREWORK\00_HANDOFF.md

2. 逐文件集成地图：
E:\GAN_FCC_WORK\github_sync\GI_a1_scgi_20260709_014434\scgi_repro\paper_draft\REVIEWS\GPT_R13_THEORY_PREWORK\05_MAIN_AGENT_PATCH_MAP.md

3. 三份可搬运证明：
E:\GAN_FCC_WORK\github_sync\GI_a1_scgi_20260709_014434\scgi_repro\paper_draft\REVIEWS\GPT_R13_THEORY_PREWORK\01_D8_KNOWN_CARRIER_REPLACEMENT.tex
E:\GAN_FCC_WORK\github_sync\GI_a1_scgi_20260709_014434\scgi_repro\paper_draft\REVIEWS\GPT_R13_THEORY_PREWORK\02_F8_PROP3_REPLACEMENT.tex
E:\GAN_FCC_WORK\github_sync\GI_a1_scgi_20260709_014434\scgi_repro\paper_draft\REVIEWS\GPT_R13_THEORY_PREWORK\03_IDENTIFIABILITY_LOWER_FISHER_PERMUTATION.tex

4. Prop. 3 度量复算证据：
E:\GAN_FCC_WORK\github_sync\GI_a1_scgi_20260709_014434\scgi_repro\paper_draft\REVIEWS\GPT_R13_THEORY_PREWORK\04_C0_METRIC_REAUDIT.md

5. GPT Pro 协作与分歧记录：
E:\GAN_FCC_WORK\github_sync\GI_a1_scgi_20260709_014434\scgi_repro\paper_draft\REVIEWS\GPT_R13_THEORY_PREWORK\06_GPT_PRO_COLLAB_LOG.md

6. 片段语法 harness（只作参考，不并入论文）：
E:\GAN_FCC_WORK\github_sync\GI_a1_scgi_20260709_014434\scgi_repro\paper_draft\REVIEWS\GPT_R13_THEORY_PREWORK\99_FRAGMENT_SMOKE.tex

前置 LaTeX 中的 `-R13` 方程号是临时标签。集成时必须按最终 Appendix 编号重排，并建立正式 label/ref，不能原样保留临时编号。

二、必须按以下依赖顺序集成

A. 先重写 Appendix D.4 / Theorem C

- 使用 endpoint-clamped generalized inverse 的全局 1/kappa Lipschitz 性；精确有限窗风险直接为 (B_n^2+V_n)/kappa_n^2，不再添加独立 clamp-event 风险。clamp 概率只保留为诊断。
- 对近似单调校准曲线，统一响应误差贡献 epsilon_cal/kappa；bisection 已是 log-parameter 误差，直接加 epsilon_bis。禁止写成 (epsilon_cal+epsilon_bis)^2/kappa^2。
- 明确 calibration-safe interval 非空；all-zero 和边界窗由 clamped inverse 覆盖。
- 低光子一般主项必须保留：
  [sum_k w_nk^2 lambda_k(ell_k)] / [sum_k w_nk lambda_k(ell_n)]^2。
- 只有 distinct equal-weight、d=0、固定 alpha、窗内 gain flatness/no-clamp localization 和数值误差可忽略时，才能简化为 1/(W lambda_bar)。加入 W=2、ell=(0,log2) 的 3/2 反例。
- 任意 carrier 的一般结论限制为 beta<=1。beta>1 只陈述内部 sensitivity-balanced 窗；当前 truncated edge windows 即使 homogeneous carrier 也不满足一阶矩消失。
- 严格拆分：Theorem B 是 blind high-count；Poisson soft-log 是 oracle-known-carrier 或另行定义的 known-law estimator。禁止把 unknown carrier law 包装成当前 estimator 的 blind 定理。
- centered-log quotient 风险由正交投影非扩张直接继承。

B. 补 calibration theorem-level certificate

- 当前 1.6410165e-6 只是 midpoint empirical maximum，不是连续区间 uniform certificate。
- 优先实现/记录 log-lambda 线性插值误差证书：Delta_x^2 sup|f''|/8，加 certified Poisson tail/tabulation error。
- 若本轮不生成严格证书，全文只能称 empirical diagnostic，不能把该值写成已证明的统一误差常数。
- epsilon_bis<=1.5396755e-17 保持 log-parameter 单位。

C. 重写 F.8、F.10/F.11 和 Prop. 3

- F.8 将 Var(Delta) 改为 E[Delta^2]，除非额外假设 E Delta=0；加入 OU lognormal exact moments。
- 区分：fixed-design raw sampling floor、Lambda_lev=N B_L、population raw-moment constant。不得再用一个 pipeline C0 混称。
- Table I 的 7.38--7.68e5 改标 Lambda_lev；它来自 10 objects x 15 residual probes，不是 deterministic statistic。
- gain-known raw-MSE skeleton 才是严格 Prop. 3。same-record blind 只能使用 full covariance/cross terms，或明确标 conditional proxy。
- Q(rho) 依赖 blind residual 时是 fixed point，不是 explicit solution；写明 A_T>0、continuity、single-crossing 条件和 Q<=0/Q>=1 的正确含义。
- OU 路径不是 Lipschitz。当前 rho^(2/3) 不能称为 OU theorem；使用前置包中的 OU window lemma（interior leading s^2 rho W/6，优化 rho^(1/2)）或把 blind residual risk 当作外部测量函数。

D. 修复 Prop. 3 raw/aligned 度量错配

- runner 当前 C0=623.976--715.172 是 scale-aligned fixed-design floor；F.2/F.9 需要 raw floor=980.110--1114.529。
- raw/aligned ratio median=1.5398517，几乎精确解释旧 boundary factor 1.54；删除“1.54 consistent with O(Delta^3)”解释。
- 首选：从已有轨迹/重建导出 provenance-bearing raw MSE 和 raw crossings，无需重跑物理模拟。独立复算结果：sigma_a>=0.1 的 40/40 raw crossing，median factor=1.04387，max=1.19985。
- 若不做正式 raw export，只能把现有结果称为 scale-aligned empirical analogue，不能称 strict no-free-parameter validation。

E. 集成 gauge、lower bound、Fisher 和 permutation 修复

- 主文非法 `(a,T)->(a s^{-1},sT)` 改为精确 collision curve；区分 square exact collision、tall range condition 和 quotient tangent。
- Le Cam two-point 负责 pointwise；integrated quotient loss 使用带 guard bands 的 Assouad hypercube。
- 随机 carrier alternatives 不得依赖 realized B；先对 joint oracle experiment 计算 expected KL，再 marginalize。
- Fig. 5 的 sum lambda 只称 oracle common-shift diagnostic。MSE 在线上方不能证明 unbiased；线上下方不能解释为 quotient CRB efficiency。
- full exchangeability 归属于 acquisition-order randomization。pixel permutation 只保留相同 non-DC marginal/variance；加入 Walsh triple-moment 反例否定 full joint exchangeability。

F. 同步主文与母本

至少同步修改：
- paper_draft/latex/body.tex
- paper_draft/latex/appendix_body.tex
- paper_draft/MANUSCRIPT_DRAFT.md
- paper_draft/APPENDICES.md

同时处理第三轮已经确认的投稿阻断：
- XXEPSCALXX / XXEPSBISXX；
- Appendix D 中低光子 Fig. 7 应改为主文 Fig. 5，以及旧 Fig. S2/S3；
- abstract <=250 words、自包含，展开 SRHT/CIs，删除内部章节/定理指针；
- TABLE I / TABLE 1 重复及 Roman/Arabic 混用；
- Billingsley、Petrov、van der Vaart 加入正式参考文献；
- Fig. 5 实际五个 methods、SD error bars、requested W=64/effective 65；
- floor probe 10.92% 与 20.28% 不得统一写约11%。

作者/单位、supplement 28页策略、MIT 权利人仍是用户决策，不得擅自替用户决定。

三、测试和验收

必须新增/运行：
- exact carrier root；
- all-zero clamp；
- truncated edge membership 与 interior identity；
- centered-log projection/gauge；
- oracle local-shift Fisher；
- deterministic Delta 反例；
- raw vs aligned C0 regression；
- raw crossing export 的数据完整性和 provenance。

最终执行：
- 全量 pytest；
- main.tex 与 supplement.tex clean compile；
- 0 overfull、0 undefined refs/cites、0 placeholder；
- 检查主文13页和 supplement 当前页数；
- 逐项对照 05_MAIN_AGENT_PATCH_MAP.md 的 acceptance gates。

四、交付要求

完成后给我：
1. 结论先行的变更摘要；
2. 修改/新增文件清单；
3. 每个原复审指控如何闭环；
4. 新 raw-metric 结果及 provenance；
5. pytest/LaTeX/PDF 验证结果；
6. 尚需用户决定的事项；
7. git status 和建议提交信息。

不要因为原文曾被标记“科学内容冻结”而保留不可证主张；但也不要重跑已证明无需重跑的物理模拟。优先使用现有数据做 raw re-export，并保持改动可审计、可回滚。
```
