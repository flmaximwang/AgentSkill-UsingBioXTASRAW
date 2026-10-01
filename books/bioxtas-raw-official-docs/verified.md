# verified.md — 阶段 1.5 三重验证记录（官方文档卷）

- **候选池**：147 条，来自 `candidates/` 5 个文件
  分布：frameworks 18（f01–f18）/ principles 22（p2o-01–22）/ cases 20（a01–a20）/ counter-examples 20（ce01–ce20，含 3 条 A 级对照）/ glossary 67（g01–g67）
- **合并规则**：同一件事被多个视角重复提取的，合并成一条「方法论单元」。合并只影响归组，候选原文一律保留在 `candidates/`。
- **通过**：**13 个单元** → 进入阶段 2（其中 **8 个新建** skill / **5 个扩写**现有 skill）
- **淘汰**：6 组 → `rejected/`（其中 4 组是「降级为 reference 并入」而非丢弃）
- **通过率**：13/19 = 68%（比前两册高，原因见文末「为什么本册通过率更高」）

每条编号格式：`V1` 跨域验证 / `V2` 预测力测试 / `V3` 独特性检验。
**本材料的 V1 判据**（照前两册的调整版）：*该单元所依赖的事实必须在至少两个互相独立的使用场景里被依赖*——本册的"独立场景"= 不同 tutorial 章节 / 不同方法学章节 / GUI 与 API 两条互不依赖的路径。**手册（20-manual，A 级）不出现在任何 V1 证据里。**

---

# 一、扩写现有 5 个 skill（X 组）

## X1 — 扩写 `configure-bioxtas-raw-for-a-dataset`（配置就绪 → 加「配置怎么造出来 + 两个静默失效」）

- **候选**：f02（造 cfg 六步链）、ce01（没载配置就积分）、ce02（掩膜只 Save to File 没按 Set）、a19（绝对刻度三基准常数）、a20（Energy/pixel/AgBh + 归一化 /I1 得 7200.0）、g51–g61（配置类术语）

**V1 跨域** — 通过。三处互不依赖：① `tutorial/s3_*`（造 cfg 本身）；② `tutorial/s1_basic`（"Any time you are going to process images, you need to load the appropriate configuration"）；③ `tutorial/s3_masking` 的 Set 语义（掩膜生效路径与载入路径不同）。三处没有一处依赖另两处成立。

**V2 预测力** — 通过。新问题：*"我画了掩膜、也存了 .msk，为什么曲线里 beamstop 的阴影还在？"* → 答：`Save to File` 只写磁盘 `.msk`，进内存必须按 `Set`（Clear 之后同样要 Set）。文档把这两条路并列写出但没有把"不生效"作为结论讲；本单元把它变成判据。

**V3 独特性** — 通过。「配置错是静默的」这个性质外行猜不到（直觉是"程序会报错"）；「掩膜有两套保存语义」更是纯操作语义。

→ 扩写：SKILL.md 增「配置怎么造出来（六步链）」+ 两条静默失效；新增 `references/build-a-configuration-file.md`（六步链细节 + 绝对刻度顺序约束的指向）。

---

## X2 — 扩写 `reduce-saxs-frames-to-curves`（还原 → 加 WAXS 合并 / 相似性 / 文件格式）

- **候选**：f01、f16（WAXS 双探测器合并）、f15（残差/比率/CorMap 三视图）、f18（.dat/.out/.ift 三格式与不可读回导出）、a01、a02

**V1 跨域** — 通过。① `s1_basic`（同一批帧的还原主线）；② `s1_waxs`（双探测器时"先各自还原、再按标度归并"是另一条独立主线）；③ `s1_similarity`（曲线之间是否可比）与 ④ `s4_external_data`（落盘格式决定下游能不能读）——四者互不依赖。

**V2 预测力** — 通过。新问题：*"我把 WAXS 和 SAXS 一起载进来积分，为什么 SAXS 的曲线全废了？"* → 答：含 PIL3 的 WAXS 文件绝不能与 SAXS 一起积分（各自要各自的 cfg，先各自还原再 Merge，WAXS 侧需乘 scale factor，示例 0.000014）。

**V3 独特性** — 通过。`merge` 的方向性（给 WAXS 标星、对 SAXS 做 Merge 生成 `M_`）、CorMap 驱动的「Average Only Similar Files」都是 RAW 特有语义。

→ 扩写：加 WAXS 合并段、相似性三视图段；新增 `references/raw-file-formats-and-cormap.md`（.dat/.out/.ift 段结构与 Excel 导入坑 + CorMap 阈值与人工复核）。

---

## X3 — 扩写 `assess-guinier-fit-quality`（Guinier 判读 → 补全四条判据 + 形状分档 + Kratky 交叉验证）

- **候选**：p2o-01（q_min·Rg<0.65）、p2o-02（形状分档 1.0/1.3/1.7）、p2o-03（smile/frown）、p2o-04（排除 >3–5 点即报警）、ce04（坏 buffer 让 Kratky 像柔性）、ce05（<1% 聚集）、a03（GI q_max·Rg≈1.32、文献 Rg=32.7 Å）、a05（无量纲 Kratky 峰位 √3、峰高 3/e）

**V1 跨域** — 通过。① `saxs_guinier`（四条判据本身）；② `tutorial/s1_guinier`（GUI 里 n_min/n_max 的操作）；③ `tutorial/s1_kratky` 与 `saxs_ift`（用 Kratky 判柔性、用 P(r) 交叉验证）——三条互不依赖，且第 ③ 条能独立推翻第 ① 条的结论（轻聚集形似柔性）。

**V2 预测力** — 通过。新问题：*"我的蛋白在 Kratky 图上有上翘，是不是部分解折叠？"* → 答：先排除 buffer 扣减不准（文档明写坏扣减可让 Kratky 看似有柔性）；再用 Guinier 残差形态（smile=聚集）与 P(r) 交叉验证。文档没有把这条"先证伪再下结论"的次序写成判据。

**V3 独特性** — 通过。q_min·Rg<0.65 的下限、按形状分档的 1.0/1.3/1.7、无量纲 Kratky 的 √3 与 3/e 都是具体阈值而非常识。

→ 扩写：补四条判据与形状分档；加「Kratky 交叉验证」段与"坏扣减伪装柔性"的坑；新增 `references/kratky-and-flexibility.md`。

---

## X4 — 扩写 `process-sec-saxs-series`（SEC 系列 → 补第二 buffer 区 / 文件格式 / 导出列义）

- **候选**：f05、a06（buffer 504–562 / sample 699–713 / 第二 buffer ~840–896）、a07（BSA Rg~28 Å / MW~66 kDa / scale 1800）、ce18（A 级对照：.sec vs .hdf5）

**V1 跨域** — 通过。① `s1_sec`（GUI 流程）；② `tutorial/s4_external_data` 与 `api/getting_started`（序列文件在文档与 API 两侧都是 `.hdf5`）；③ `s2_baseline`（基线校正章节预设了 buffer 区已定）——三条独立。

**V2 预测力** — 通过。新问题：*"别人给我的 SEC 序列是 .sec，我的脚本读不了，是我做错了什么吗？"* → 答：`.sec` 是 RAW 私有、非人类可读、只有 RAW 能读；跨工具交换应走 `.hdf5`（`load_series` 文档写 "a .hdf5 or .sec"）；旧手册说 SEC 存 `.sec` 是 A 级过时信息。

**V3 独特性** — 通过。第二 buffer 区的处理（Add region → Pick → Set buffer → 删旧 sample region → Auto）与 scale 作用于整 series 都是 RAW 特有语义。

---

## X5 — 扩写 `correct-sec-saxs-baseline`（基线 → 补积分法的单侧限制与截断策略）

- **候选**：f06、ce11（积分基线只允许正向 → 需负校正的 q 被整体过校）

**V1 跨域** — 通过。① `s2_baseline` 的 Linear 分支（仪器/束流漂移）；② 同章 Integral 分支（毛细管污垢，随 q 变化）；③ `saxs_ift` 对"轻聚集被误读成柔性"的交叉验证提醒——三者独立。

**V2 预测力** — 通过。新问题：*"我用 Integral 校正完，高 q 反而更奇怪了，是数据坏了吗？"* → 答：不是，是 Integral 只允许正向或不校正，需要负校正的 q 会被整体过校；正确动作是先确认该 q 段是否本就是噪声，是则**先截断到低 q 再做校正**。

**V3 独特性** — 通过。「校正方法有方向性限制」这件事与直觉相反（直觉是"校正总是把基线拉平"）。

---

# 二、新建 8 个 skill（N 组）

## N1 — `put-saxs-data-on-an-absolute-scale`（绝对刻度：三法分叉 + 顺序约束）

- **候选**：f03、p2o-22、ce03、ce12、a19
**V1**：通过 —— 水力法（`s3_abswater`）与玻碳法（`s3_abscarbon` 的 Simple/Full）两条独立路线共享同一顺序约束；反例 ce03/ce12 又从"失效"侧独立证实。
**V2**：通过 —— 新问题：*"我按教程算了玻碳常数，得到 400 多，是数据不行吗？"* → 先查"算常数前是否关掉了绝对刻度"与"算完之后是否又改过归一化（含通量/透射）"，两条都能得到坏常数；示例期望值 324（Simple 1.0 mm）/198（NIST 1.5 mm）/水 4 °C 0.00077。
**V3**：通过 —— "先关掉它才能算它"极反直觉，且"改归一化就要重算常数"是隐性依赖，不是常识。
→ 新建。

## N2 — `compute-and-validate-p-of-r`（IFT 三法分工 + Dmax 定法 + P(r) 判据 + 截断规则）

- **候选**：f07、f08、p2o-05、p2o-06、p2o-07、p2o-08、ce07、ce13、ce14、a08、a09
**V1**：通过 —— 方法学（`saxs_ift` 讲判据与 Dmax 步骤）与操作（`s2_gnom`/`s2_dift`/`s2_bift` 三条 GUI 路线）独立；且 `saxs_bead_models` 从下游需求（DAMMIF 要截断）反向约束 P(r) 的产出形态。
**V2**：通过 —— 新问题：*"我的 P(r) 末端被压得直直地掉到零，是不是 Dmax 取小了？"* → 是（低估→陡降，高估→绕零振荡）；正确动作是关掉 force-to-zero 上下扫 Dmax，看它自然落零处；且 Dmax 精度不优于 5%（有时 ~10%）。
**V3**：通过 —— 「直接对 I(q) 做傅里叶变换是错的」、三法按"下游用哪个重建程序"而不是"哪个更准"选、BIFT 的 .ift 不兼容 DAMMIF 但兼容 DENSS，三条都是反直觉的具体知识。
→ 新建。

## N3 — `choose-a-molecular-weight-method`（MW 六法两轴 + 不确定度 + 失效点）

- **候选**：f14、p2o-09、p2o-10、p2o-11、p2o-12、ce08、ce09、a04
**V1**：通过 —— 方法学（`saxs_mw` 给六法公式、不确定度与失效点）与操作（`s1_mw` 的 GUI 面板与浓度输入）独立；SEC 语境（浓度未知 → 只能用浓度无关法）是第三个独立场景。
**V2**：通过 —— 新问题：*"我的 SEC-SAXS 里能不能用绝对刻度法算 MW？"* → 不能（浓度依赖法与 SEC 不兼容，应用 Vc/Vp/Shape&Size/Bayesian 这类浓度无关法）；而且 SAXS 通则 ~10% 不确定度，不该用来"定"分子量（用 MALS）。
**V3**：通过 —— 「同一个蛋白该报哪个 MW」的答案是"看能用哪一类方法"，而不是"选最准的那个"；Vc 对 <15–20 kDa 与蛋白-核酸复合物系统性失效。
→ 新建。

## N4 — `evaluate-a-shape-reconstruction`（重建→评估闭环：珠模型 + DENSS + 对齐）

- **候选**：f09、p2o-13、p2o-14、p2o-15、p2o-16、p2o-17、ce06、ce10、a10、a11
**V1**：通过 —— `saxs_bead_models`（方法学判据）、`s2_dammif`（GUI 流程与 DAMAVER/DAMCLUST/SASRES）、`s2_denss`（DENSS 与 FSC 分辨率）、`s2_align`（对齐到高分辨结构）四条独立。
**V2**：通过 —— 新问题：*"我的 DAMMIF 结果里平均 NSD=0.8、15 个模型剔除了 4 个、DAMCLUST 说有 2 个簇，这个重建能用吗？"* → 不能（剔除 >~2 个、多簇、NSD 0.6–1.0 只是 fair 三条同时不达标）；另一条判据链是 a-score、χ²≈1、模型 Rg/Dmax 对上 P(r)（Rg ~5%、Dmax ~10%）、体积估 MW 差 >20–25% 即可疑。
**V3**：通过 —— 「高质量数据不保证好重建」「重建的输出是带评估指标的模型集，不是最好看的那张图」「多簇不代表溶液里真有多个形状」三条都反直觉。
→ 新建。

## N5 — `fit-a-high-resolution-model-to-data`（CRYSOL / PDB2SAS：计算即拟合）

- **候选**：f17、ce17
**V1**：通过 —— CRYSOL 路线（需 ATSAS，`s2_crysol`）与 PDB2SAS 路线（DENSS 内建且为默认，`s2_pdb2sas`）两条独立；`saxs_bead_models` 的"用 CRYSOL/FoXS 直接拟合数据判优劣，而不是把结构 dock 进珠模型"是第三处独立使用。
**V2**：通过 —— 新问题：*"我算出的理论曲线和实验曲线在低 q 差很多，是模型错了吗？"* → 先看是不是生成的 minimal 曲线（未把数据纳入拟合）：minimal 曲线即使模型相符也常拟合差（溶剂/水化层/排除体积难建模），应让数据参与计算；再查 harmonics（高长径比需更多，如 100）与 PDB2SAS 的 N samples（默认 128 对细长蛋白不足 → 256，用 2 的幂）。
**V3**：通过 —— 「理论曲线应当"计算即拟合"」与「默认计算器可能被改过、.cif 不被 PDB2SAS 支持」都是具体到会踩坑的知识。
→ 新建。

## N6 — `deconvolve-overlapping-elution-peaks`（SVD → EFA → REGALS 阶梯 + 三阶调参 + 复核）

- **候选**：f10、f11、p2o-18、p2o-19、p2o-20、p2o-21、ce15、ce16、a12、a13、a14、a15、a16
**V1**：通过 —— EFA 路线（标准 SEC，`s2_efa`）、REGALS 路线（IEC/时间分辨/滴定，`s2_regals`）、API 路径（`ex_sec_saxs` 里 `svd/efa/regals` 与 REGALS 组件字典）三条独立；`s2_svd` 又是 EFA 的独立前置。
**V2**：通过 —— 新问题：*"REGALS 里我把缓冲分量的 lambda 调到 1e10，结果分量 1 的曲线突然大变，为什么？"* → 过平滑（文档：高 q 背景趋同 + 某分量 profile 突变 = oversmoothing）；lambda 应按数量级调、示例最优 ~4e8；且 REGALS 不会自动更新结果（按钮黄底才是"有改动"），最终运行必须关掉 "Start with previous results"。
**V3**：通过 —— 「分量数要先用 SVD 独立核对」「浓度峰高度本身任意（面积归一）」「正性约束取消后浓度不应显著变化」是别人猜不到的具体判据。
→ 新建。

## N7 — `analyze-time-resolved-series`（多序列精修：校准 → 裁剪/rebin → 排除帧 → 帧合并）

- **候选**：f12、a17、a18
**V1**：通过 —— 教程主体（多 series 逐点平均/扣减）与"设置可存 json 再 Load 复用"这条独立支线；`s4_export_plots` 的导出路径是第三处。
**V2**：通过 —— 新问题：*"时间分辨数据里我的 Rg 曲线第一个点是 0，正常吗？"* → 不正常，首帧常需排除（Exclude profiles 填 "0" 后重算），且低 q 常被寄生散射污染、最高 q 处约半数点为负（无信号）→ 应裁剪 q 范围后 rebin 再降噪（Rebin series factor 2 会让时点数减半）。
**V3**：通过 —— 「时间轴要先用 Load Calibration 从流量校准换算（x→time + offset）」和「rebin 后帧号报的是该段首帧」是具体到会误报的操作语义。
→ 新建。

## N8 — `script-raw-with-the-python-api`（RAWAPI 三段骨架 + 能力清单）

- **候选**：f13、g18–g30（对象与方法名）、`50-api` 全部 11 节
**V1**：通过 —— 三个官方示例脚本（`ex_analyze_profile` 单曲线全流程 / `ex_batch_profile` 批量扣背景 / `ex_sec_saxs` SEC 全流程）是三条互不依赖的路径，且都遵循同一 load→analyse→save 骨架。
**V2**：通过 —— 新问题：*"我想批量把 30 条曲线都跑 Guinier 并出一份报告，GUI 要点 30 次，有没有别的办法？"* → 用 API：`load_settings` → `load_profiles` → 循环 `auto_guinier` → `save_report`；且"GUI 里能对 series 做的分析 API 都能做"，但无 GUI 时 EFA 需自行给出分量区间。
**V3**：通过 —— 具体函数签名与返回元组顺序（如 `auto_guinier` 返回 11 元组、`set_baseline_correction` 返回 10 元组）只存在于官方示例里，属**独家知识**（文档的 API 参考页是空壳）。
→ 新建。**边界必须写明**：官方 API 参考正文为空，本 skill 的函数清单来自 examples，签名以实测为准。

---

# 三、淘汰（6 组）

| 组 | 内容 | 处置 | 理由 |
|---|---|---|---|
| R1 | 「造一份配置文件」独立成 skill（f02、ce02、a20） | **降级**：并入 X1 的 `references/build-a-configuration-file.md` | 与 X1 是同一个决策点（配置），拆成两个 skill 会在路由上互相竞争 |
| R2 | 「Kratky 柔性判读」独立成 skill（ce04、a05） | **降级**：并入 X3 | 它是 Guinier 判读的**证伪步骤**（先排除坏扣减），不是独立决策点 |
| R3 | 「曲线相似性/CorMap 三视图」独立成 skill（f15） | **降级**：并入 X2 的 reference | 「Average Only Similar Files」是还原流程里的一步；CorMap 无算法描述，只有阈值级证据 |
| R4 | 「导出与格式互操作」独立成 skill（f18） | **降级**：并入 X2 的 reference | V3 不成立：文件格式清单属"查表"，不是判断 |
| R5 | 纯界面罗列 / 安装步骤 / changelog / 引文库 / 视频清单 | **淘汰** | 见 `source/README.md` §6（随 UI 与平台变化即失效、一次性动作、与"怎么做"无关） |
| R6 | 术语池里纯事实条目（pilatus_1m 参数、beamstop、AgBh 的具体设置值等 g51–g61 的一部分） | **降级**：进各 skill 的 glossary reference | 是"查表值"而非判断；单独成 skill 无路由价值 |

## 为什么本册通过率（68%）比前两册（43%）高

前两册的源是**公众号操作说明**：作者按"一次演练"组织，很多知识只在被使用的地方出现一次，V1 需要放宽才够用。
本册的源是**官方全站文档**（97 节 / 16,010 行），同一判据天然出现在四处（方法学 `30-saxs` 讲判据、`tutorial` 讲操作、`api` 讲脚本、反例从失效侧再次确认），因此 V1 大多数单元天然满足；淘汰集中在 V3（"查表值"不构成判断）与"同一决策点被拆成两个技能"这两类。这也意味着本册的**证据密度高于前两册**——每条单元都能追到 2 个以上互不依赖的出处。
