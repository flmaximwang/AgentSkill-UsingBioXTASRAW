# AgentSkill-UsingBioXTASRAW

把 BioXTAS RAW 的操作与判据蒸馏成一组可被 agent 调用的 skill。三份来源、三本审计轨迹：

| 来源 | 内容 | 审计轨迹 |
|---|---|---|
| 《BioXTAS RAW程序使用说明》（公众号「生物小角」· 刘广峰，2024-04-26） | 安装 / 界面 / 配置 / 批次数还原 / Guinier 判读 | [`books/bioxtas-raw-manual/`](books/bioxtas-raw-manual/) |
| 《利用BioXTAS RAW程序处理SEC-SAXS数据》（同上，2024-04-28）+ 官方教程 *Basic SEC-SAXS processing* 与 *Baseline correction* | SEC 系列处理 / 基线校正（**第二源 = 官方文档**，因为译文砍掉了整节） | [`books/sec-saxs-series/`](books/sec-saxs-series/) |
| **BioXTAS RAW v2.4.2 官方文档全站**（97 文件 / 16,010 行；tutorial 37 节 + manual 19 节 + saxs 5 节 + api 11 节 + install 16 节） | 整条判据流水线：配置 / 还原 / Guinier / IFT 与 P(r) / MW / 绝对刻度 / 重建评估 / 模型拟合 / 去卷积 / 时间分辨 / RAWAPI | [`books/bioxtas-raw-official-docs/`](books/bioxtas-raw-official-docs/) |

**15 个 skill**：13 个「决策点」skill（下面索引表）+ 2 个**端到端流水线** skill（第 14–15 行，工程产物、非蒸馏）：配置是否就绪 → 一批帧怎么变成曲线 → 读出的 Rg 信不信得过 → SEC 洗脱里哪一段算一个样品 → 扣减后还在漂怎么办 → 强度怎么钉到绝对刻度 → 从 I(q) 到 P(r) 与 Dmax → 分子量该用哪一法 → 重建做完能不能用 → 高分辨模型怎么对照 → 峰重叠怎么分解 → 时间分辨怎么精修 → 怎么用脚本批量做；两条流水线分别吃 **SEC 连续洗脱帧**与**管式/静态帧**（差别在 control 从哪来）。

蒸馏流水线是 **cangjie-skill（book2skill）的 RIA-TV++**：整文理解 → 5 视角提取（三本共 **224 条候选**）→ 三重验证（V1 跨域 / V2 预测力 / V3 独特性）→ RIA++ 构造 → Zettelkasten 链接 → 压力测试（独立盲测）→ 人性化输出（学习笔记 + 话术库）。

> **状态**：本地仓库已建、已提交；**尚未 push 到 GitHub、尚未安装进任何 profile**（等确认）。
> README 里的安装命令按"将要发布为 `flmaximwang/AgentSkill-UsingBioXTASRAW`（private）"写。

## 索引

| skill | 用途 | 可执行入口 |
|---|---|---|
| [configure-bioxtas-raw-for-a-dataset](skills/configure-bioxtas-raw-for-a-dataset/SKILL.md) | 确证会话已加载当天的 `.cfg`（定心 / 距离 / 掩膜 / 标样），用标样峰位把"配置对不对"变成可检验事实；含"配置怎么造出来"六步链与两条静默失效（未载配置、掩膜只 Save 未 Set） | `references/build-a-configuration-file.md`、`references/bioxtas-raw-glossary.md` |
| [reduce-saxs-frames-to-curves](skills/reduce-saxs-frames-to-curves/SKILL.md) | 2D 帧 → 1D 曲线（积分 / 平均 / 扣减 / 落盘）+ `A_`·`S_`·`*` 自检信号；WAXS 双探测器合并；相似性三视图（残差 / 比率 / CorMap） | `references/raw-file-formats-and-cormap.md`、`references/raw-workspace-and-naming.md` |
| [assess-guinier-fit-quality](skills/assess-guinier-fit-quality/SKILL.md) | Guinier 取点与判读：`q_min·Rg<0.65` 下界、按形状分档上界（棒 1.0 / 球 1.3 / 盘 1.7）、残差 smile=聚集 / frown=排斥、Kratky 交叉验证；报告必须带 q 区间 | `references/kratky-and-flexibility.md` |
| [process-sec-saxs-series](skills/process-sec-saxs-series/SKILL.md) | SEC 系列 → 一条可信曲线：色谱图 → buffer/sample 帧区间 → 逐帧扣减 → Rg/MW 平台判据 → 送 Profiles；含第二 buffer 区与 `.sec` vs `.hdf5` | `references/sec-saxs-series-workspace.md` |
| [correct-sec-saxs-baseline](skills/correct-sec-saxs-baseline/SKILL.md) | 扣减后仍漂移时按性质选校正：束流/仪器 → `Linear`，毛细管污垢 → `Integral`；积分法只允许正向校正（需负校正的 q 会过校，先截断到低 q） | `references/sec-saxs-baseline-api.md`、`references/beam-instability-and-step-offsets.md`、`scripts/` |
| [put-saxs-data-on-an-absolute-scale](skills/put-saxs-data-on-an-absolute-scale/SKILL.md) | 强度钉到绝对刻度（cm⁻¹）：水 / 玻碳 Simple / 玻碳 Full NIST 三法分叉 + **两条顺序约束**（算常数前先关刻度；算完不得再改归一化） | `references/absolute-scale-and-normalization.md` |
| [compute-and-validate-p-of-r](skills/compute-and-validate-p-of-r/SKILL.md) | 从 I(q) 到 P(r)：GNOM / DIFT / BIFT 按下游重建程序选、Dmax 八步定法、五条判据、截断规则（DAMMIF 要截断 / DENSS 不截断） | `references/ift-methods-and-dmax.md` |
| [choose-a-molecular-weight-method](skills/choose-a-molecular-weight-method/SKILL.md) | 六种 MW 方法选哪一个、能不能信（浓度依赖 vs 浓度无关；SEC 只能用后者）；SAXS 不应用来定 MW 而应判低聚态 | `references/mw-methods-comparison.md` |
| [evaluate-a-shape-reconstruction](skills/evaluate-a-shape-reconstruction/SKILL.md) | 重建做完怎么判：a-score / 平均 NSD / 被剃模型数 / 聚类数 / χ² / Rg·Dmax 对上 P(r) / 体积 MW（含 DENSS 的 FSC 与对齐） | `references/reconstruction-evaluation-criteria.md` |
| [fit-a-high-resolution-model-to-data](skills/fit-a-high-resolution-model-to-data/SKILL.md) | 高分辨模型对照 SAXS 的"计算即拟合"（CRYSOL / PDB2SAS）：harmonics、N samples、默认计算器漂移 | `references/model-fitting-parameters.md` |
| [deconvolve-overlapping-elution-peaks](skills/deconvolve-overlapping-elution-peaks/SKILL.md) | 峰重叠按复杂度选 SVD / EFA / REGALS；分量数 → 区间 → λ 三阶调参 + χ² 与正性约束复核 | `references/deconvolution-workflow.md` |
| [analyze-time-resolved-series](skills/analyze-time-resolved-series/SKILL.md) | 一批 series 一起精修：时间校准 → q 裁剪/rebin → 排除帧 → 帧合并；S/N 与测量次数判据 | `references/multi-series-workflow.md` |
| [script-raw-with-the-python-api](skills/script-raw-with-the-python-api/SKILL.md) | 用 RAWAPI 批量/可复现地做同一件事（load → analyse → save 三段骨架 + 函数清单 + 对象访问） | `references/rawapi-function-inventory.md` |
| [run-a-sec-saxs-pipeline-end-to-end](skills/run-a-sec-saxs-pipeline-end-to-end/SKILL.md) | **端到端跑一条 SEC-SAXS 系列**（图像→报告，全在 RAW 里做）：补逐帧 BL19U2 header txt 让 RAW 归一化（不写归一化 tif）→ 归一化裁剪视频 → buffer/sample 区与扣减 → 多区间 Guinier → IFT → MW → DAMMIF/DENSS → 各节点 `.dat`/表/PDF 报告 | `references/bl19u2-header-normalization.md`、`scripts/`（3 个可执行脚本） |
| [run-a-tube-saxs-pipeline-end-to-end](skills/run-a-tube-saxs-pipeline-end-to-end/SKILL.md) | **端到端跑一批管式/静态 SAXS 帧**（目录内样品 + 夹着它的 control，图像→报告，全程 RAW）：归一化开关（`ImageHdrFormat`/`EnableNormalization`）→ control 相对缩放（1–3% 高 q 残留用 `scaleRelative` 定标）→ 多区间 Guinier 闸门表（Rg 漂移/`chi2_red`/curvature/`qRg`）→ BIFT 的 Dmax 搜索域 → MW → DENSS（DAMMIF 需 ATSAS）→ 各节点 `.dat`/表/PDF/GUI workspace | `references/tube-control-pairing-and-scaling.md`、`scripts/run-raw-tube-pipeline.py` |

给人看的文档：[第 1 本学习笔记](books/bioxtas-raw-manual/LEARNING_NOTE.md) · [SEC 本](books/sec-saxs-series/LEARNING_NOTE.md) · [官方文档本](books/bioxtas-raw-official-docs/LEARNING_NOTE.md)；
话术库：[第 1 本](books/bioxtas-raw-manual/TALKING_POINTS.md) · [SEC 本](books/sec-saxs-series/TALKING_POINTS.md) · [官方文档本](books/bioxtas-raw-official-docs/TALKING_POINTS.md)。
skill 总览与引用图：[第 1 本](books/bioxtas-raw-manual/INDEX.md) · [SEC 本](books/sec-saxs-series/INDEX.md) · [官方文档本](books/bioxtas-raw-official-docs/INDEX.md)。

## 质量凭据（阶段 4 盲测）

把 description **按 Hermes 路由时真实的 57 字符截断**（实测 `agent/skill_utils.py:761`，`SKILL_PROMPT_DESC_LIMIT=60`）+ 全部 prompt 交给 2 位独立评测者逐条判路由：

| 轮次 | 对象 | 评测者 A | 评测者 B | 处置 |
|---|---|---|---|---|
| 1（初始） | 第一本 3 个 skill | 78% | 81% | 两人在**同样 4 条**上判错 → 回炉阶段 2 改 description 的可见头 |
| 2（修后） | 同上 | **96%** | **89%** | 导出格式、`*`/`S_` 符号两条两位都改对 |
| 3（再挪排除条款） | 同上，8 条子集 | **88%** | **100%** | SEC-SAXS 残留为真歧义（低风险） |
| 4（升级后跨 skill 边界） | 5 个 skill，20 条 | **90%** | **90%** | SEC 连续帧题由 `reduce-…` 正确转到新 skill；两条一致错误（MW、Rg 平台）→ 再改可见头 |
| 5–6（子集校验） | 5–6 条 | 80% → **83%** | 80% → **83%** | 残留一条真歧义（"SEC 一千多帧怎么变成曲线"），代价为多一跳，已评估并停止调参 |
| 7（官方文档卷） | **13 个 skill，26 条**（13 正面 + 13 诱饵） | **92%**（正面 13/13 · 诱饵 11/13） | **77%**（正面 12/13 · 诱饵 8/13） | 5 条错归因到"可见窗口缺排除条款" → 回炉改 3 个 description 窗口 + 金标修订 1 条；复测（10 条子集，2 位新评测者）**100% / 100%** |
| 7b（复测子集） | 受影响 6 条 + 对照 4 条 | **100%** | **100%** | 折扣已记：此轮部分在考"是否读了排除条款"，真实难度基线取第 7 轮 |
| 8（管式流水线） | 新增 `run-a-tube-saxs-pipeline-end-to-end`，16 个候选，12 条（管式正面 5 + 诱饵 7） | 6/12（金标修正后 **8/12**） | 5/12（修正后 **7/12**） | 一致错误 5 条：**2 条是金标定错**（判据题被本 skill 边界主动转走）、1 条真漏（多区间产物抢不到"拟合/范围/结论"三个词）、1 条 = 姐妹 skill 已记录的同一真歧义（"SEC 一千多帧"）、1 条 57 字窗口内不可达（归一化视频）。按第 5–6 轮的处置口径：记代价、不再调参 |

细节（含判定口径的调整与理由、残留问题评估）见三本各自的 `test-results.md`。

## 安装（三段式标识符，按仓库内路径，不需要 tap；`--category` 只决定落点）

```bash
for s in configure-bioxtas-raw-for-a-dataset reduce-saxs-frames-to-curves assess-guinier-fit-quality \
         process-sec-saxs-series correct-sec-saxs-baseline put-saxs-data-on-an-absolute-scale \
         compute-and-validate-p-of-r choose-a-molecular-weight-method evaluate-a-shape-reconstruction \
         fit-a-high-resolution-model-to-data deconvolve-overlapping-elution-peaks \
         analyze-time-resolved-series script-raw-with-the-python-api \
         run-a-sec-saxs-pipeline-end-to-end; do
  hermes skills install "flmaximwang/AgentSkill-UsingBioXTASRAW/skills/$s" --category saxs -y
done
```

## 端到端流水线（第 14 个 skill：非蒸馏产物）

`run-a-sec-saxs-pipeline-end-to-end` 不是从书里蒸出来的，是**按用户验收条件 + 真实数据实测**写出来的工程产物
（2026-10-01 BL19U2 的 BSA SEC-SAXS 数据，2000 帧）。它的三个脚本，每一步都跑过真数据：

| 脚本 | 做什么 | 实测凭据 |
|---|---|---|
| `scripts/emit-bl19u2-header-txt.py` | 监视器 + 采集日志 → **每帧 BL19U2 header txt**（`Transmitted_Beam` = 该帧曝光窗口内监视器中位数），写到源目录与 tif 并排 | 2000 帧全出；监视器 19651 行 ≙ 9.83 采样/帧（**行≠帧**，必须按时间窗口取）；开头 5 个 `~1e-13` 野值按 5% 中位阈值丢弃；lag 自动扫出 **−32 帧 ≈ −48 s，corr 0.869**；逐帧因子全在 ±5% 内 |
| `scripts/crop-video-normalized.py` | 裁剪区（左下原点坐标）→ **读入时乘归一化因子** → rawvideo 管道给 ffmpeg；不落归一化 tif | 试片 120 帧 / 0.5 MB / 8× / 20 fps，`frame=120` 核对通过，抽帧确认落在束挡区 |
| `scripts/run-raw-sec-pipeline.py` | RAWAPI 全程：积分（含逐帧 header 归一化）→ series → buffer/sample 区 → 扣减/基线 → 逐帧 Rg/I0/MW → **多区间 Guinier** → IFT → MW → DAMMIF/DENSS → RAW PDF 报告；**每个节点都落 `.dat`** | 2000 帧积分 ~80 s；`counters.TB` 与 txt 完全一致；开/关归一化的 I(q) 之比 = 1/TB（逐帧 <1e-6 偏差） |

真实数据上撞到的两条结论（已写进 skill 的坑与边界）：

- **RAW 的 BL19U2 header 归一化是"内建"的**：`SASFileIO.py:909` 按 `<图像名>.txt` 读 header，
  `NormalizationList=[['/','Transmitted_Beam']]` 逐帧求值（`SASImage.py:366-380`）。线站 `.cfg` 里这套**已经写好了**，
  只差 `ImageHdrFormat` 与 `EnableNormalization` 两个开关 → **不需要写归一化 tif**（省 18 GB）。
- **`find_buffer_range` 会在"弱峰 + 强漂移"的 SEC 系列上失败**（返回 `success=False`、区间 `None`）：
  本次 BSA 数据的低 q 强度在 50 min 里单调抬升 ~40%（束位/几何漂移，与 `beam-instability` 参考档一致），
  洗脱峰只是骑在漂移上的一个小包（中 q 去漂移后在 **≈第 690 帧**附近 +1~2 个单位，峰宽约 620–760 帧）。
  这种系列必须**手工给 `--buffer-range/--sample-range`**，并在扣减后考虑 Integral 基线校正。



## 蒸馏来源与边界（必读）

- **源 1/2（微信文章）**：作者 **刘广峰**，公众号「生物小角」；两篇都是 BioXTAS RAW 官方文档的**翻译 + BL19U2 线站本地化增补**（作者自己在文中给出官方链接）。
- **源 3（官方教程）**：BioXTAS RAW 官方文档 *Basic SEC-SAXS processing* 与 *Advanced Series processing – Baseline correction*。
- **源 4（官方文档全站，v2.4.2）**：本机源码克隆 `~/Repositories/bioxtasraw/docs/source/`（`git clone --branch v2.4.2`），与 readthedocs 同源。**证据分级**：manual（19 节自承"落后好几个版本"）为 **A 级、只作对照不作依据**；tutorial / api / saxs / index 为 **B 级（当前权威）**。文档自身的 11 条矛盾（含 manual↔tutorial 的 8 处硬冲突）逐条记录在 [`books/bioxtas-raw-official-docs/source/README.md`](books/bioxtas-raw-official-docs/source/README.md)。
- **授权差异（重要）**：源 1/2 是受版权保护的公众号文章 → 相关 skill 的 R 段只做 **≤150 字/条**的引用，仓库整体按衍生作品处理、**只在私有范围存档**（见 [`NOTICE.md`](NOTICE.md)）；源 3/4 来自 **GPLv3 项目文档**，可按其许可随附署名转载。两部分在同一仓库内已按来源分别标注（skill frontmatter 的 `source_book`）。
- **版本时效**：源 4 绑定 **RAW v2.4.2**（tutorial 要求 ≥v2.3.0、ATSAS ≥3.1.1）；源 1/2 写于 2024，其中探测器参数（Pilatus 2M / 1679×1475 / 172 µm）、标样（山嵛酸银 5.8 nm，一级峰 1.076 nm⁻¹）、BL19U2 的"末帧不参与强度校正"都是**该线站当时的配置**，不是通用事实。
- **明确不覆盖**：实验设计（选柱 / 上样量 / 缓冲液匹配）、从零标定一台陌生仪器、安装与平台差异、纯界面罗列、SAXS 完整理论体系；以及文档自身没讲清的部分（官方 **API 参考正文是空壳**，函数签名只存在于 examples → API skill 的边界已写明"以实测为准"）。淘汰理由见三本的 `rejected/README.md`。

## 目录

```
books/bioxtas-raw-manual/          # 第 1 本（RAW 基本操作）的审计轨迹
  source/article.md                # 源文本快照（抓取方式与元信息见文件头）
  BOOK_OVERVIEW.md  candidates/（34 条）  verified.md（3 通过 / 4 淘汰）
  rejected/README.md  INDEX.md  LEARNING_NOTE.md  TALKING_POINTS.md  test-results.md
books/sec-saxs-series/             # 第 2 本（SEC-SAXS + 基线校正）
  source/article-1..3.md           # 微信文章 + 官方两页
  BOOK_OVERVIEW.md  candidates/（43 条）  verified.md（2 通过 / 3 淘汰）
  rejected/README.md  INDEX.md  LEARNING_NOTE.md  TALKING_POINTS.md  test-results.md
books/bioxtas-raw-official-docs/   # 第 3 本（官方文档全站 v2.4.2）
  source/README.md                 # 来源档：规模 / 语料生成脚本 / A·B·C 证据分级 / 11 条文档矛盾 / 盲区
  BOOK_OVERVIEW.md                 # 阶段 0：Adler 四步 + 25 项能力归属表 + 合并策略
  candidates/                      # 阶段 1：5 个视角的 147 条原始候选（含逐字原文引用）
  verified.md                      # 阶段 1.5：19 组单元 → 13 组通过（8 新建 + 5 扩写）
  rejected/README.md               # 6 组淘汰/降级理由
  INDEX.md  LEARNING_NOTE.md  TALKING_POINTS.md  test-results.md
skills/<name>/SKILL.md             # 阶段 2 产出（+ references/、test-prompts.json）
```
