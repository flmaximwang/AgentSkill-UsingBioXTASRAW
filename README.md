# AgentSkill-UsingBioXTASRAW

把**公众号「生物小角」· 刘广峰**关于 BioXTAS RAW 的两篇操作说明，蒸馏成一组可被 agent 调用的 skill：

| 来源 | 内容 | 审计轨迹 |
|---|---|---|
| 《BioXTAS RAW程序使用说明》（2024-04-26） | 安装 / 界面 / 配置 / 批次数还原 / Guinier 判读 | [`books/bioxtas-raw-manual/`](books/bioxtas-raw-manual/) |
| 《利用BioXTAS RAW程序处理SEC-SAXS数据》（2024-04-28）+ 官方教程 *Basic SEC-SAXS processing* 与 *Baseline correction* | SEC 系列处理 / 基线校正（**第二源 = 官方文档**，因为译文砍掉了整节） | [`books/sec-saxs-series/`](books/sec-saxs-series/) |

覆盖 5 个决策点：**配置是否就绪 → 一批帧怎么变成曲线 → 读出的 Rg 信不信得过 → SEC 洗脱过程里哪一段算一个样品 → 扣减后还在漂怎么办**。

蒸馏流水线是 **cangjie-skill（book2skill）的 RIA-TV++**：整文理解 → 5 视角提取（两本共 77 条候选）→ 三重验证（V1 跨域 / V2 预测力 / V3 独特性）→ RIA++ 构造 → Zettelkasten 链接 → 压力测试（独立盲测）→ 人性化输出（学习笔记 + 话术库）。

> **状态**：本地仓库已建、已提交；**尚未 push 到 GitHub、尚未安装进任何 profile**（等确认）。
> README 里的安装命令按"将要发布为 `flmaximwang/AgentSkill-UsingBioXTASRAW`（private）"写。

## 索引

| skill | 用途 | 可执行入口 |
|---|---|---|
| [configure-bioxtas-raw-for-a-dataset](skills/configure-bioxtas-raw-for-a-dataset/SKILL.md) | 确证会话已加载当天的 `.cfg`（定心 / 样品-探测器距离 / 掩膜 / 标样），用标样一级峰（1.076 nm⁻¹）把"q 轴对不对"变成可检验事实 | `references/bioxtas-raw-glossary.md` |
| [reduce-saxs-frames-to-curves](skills/reduce-saxs-frames-to-curves/SKILL.md) | 2D 帧 → 1D 曲线的四段流水线（积分 / 平均 / 扣减 / 落盘），含 `A_`·`S_`·颜色·`*` 四个自检信号 | `references/raw-workspace-and-naming.md` |
| [assess-guinier-fit-quality](skills/assess-guinier-fit-quality/SKILL.md) | Guinier 取点（n_min/n_max）与判读（残差形态、q_max·Rg ≈ 1.3、Rg 单位 = 1/q），报告必须带 q 区间 | —（判据写在正文节） |
| [process-sec-saxs-series](skills/process-sec-saxs-series/SKILL.md) | SEC 系列 → 一条可信曲线：色谱图 → buffer/sample 帧区间 → 逐帧扣减 → **Rg/MW 平台判据** → 送 Profiles；含端点帧例外与"浓度未知 ⇒ 不能用 I0 标样" | `references/sec-saxs-series-workspace.md` |
| [correct-sec-saxs-baseline](skills/correct-sec-saxs-baseline/SKILL.md) | 扣减后基线仍漂移时按性质选校正：束流/仪器 → `Linear`，毛细管污垢 → `Integral`；含过校正识别、与 EFA 互斥、只保留峰前缓冲液区 | —（判据写在正文节） |

给人看的文档：[第一本学习笔记](books/bioxtas-raw-manual/LEARNING_NOTE.md) · [第一本话术库](books/bioxtas-raw-manual/TALKING_POINTS.md) · [SEC 本学习笔记](books/sec-saxs-series/LEARNING_NOTE.md) · [SEC 本话术库](books/sec-saxs-series/TALKING_POINTS.md)。
skill 总览与引用图：[第一本](books/bioxtas-raw-manual/INDEX.md) · [SEC 本](books/sec-saxs-series/INDEX.md)。

## 质量凭据（阶段 4 盲测）

把 description **按 Hermes 路由时真实的 57 字符截断**（实测 `agent/skill_utils.py:761`，`SKILL_PROMPT_DESC_LIMIT=60`）+ 全部 prompt 交给 2 位独立评测者逐条判路由：

| 轮次 | 对象 | 评测者 A | 评测者 B | 处置 |
|---|---|---|---|---|
| 1（初始） | 第一本 3 个 skill | 78% | 81% | 两人在**同样 4 条**上判错 → 回炉阶段 2 改 description 的可见头 |
| 2（修后） | 同上 | **96%** | **89%** | 导出格式、`*`/`S_` 符号两条两位都改对 |
| 3（再挪排除条款） | 同上，8 条子集 | **88%** | **100%** | SEC-SAXS 残留为真歧义（低风险） |
| 4（升级后跨 skill 边界） | 5 个 skill | 见 `test-results.md` | 见 `test-results.md` | 新增两个 SEC skill 与 `reduce-…` 的边界重测 |

细节（含判定口径的调整与理由、残留问题评估）见 [`books/bioxtas-raw-manual/test-results.md`](books/bioxtas-raw-manual/test-results.md) 与 [`books/sec-saxs-series/test-results.md`](books/sec-saxs-series/test-results.md)。

## 安装（三段式标识符，按仓库内路径，不需要 tap；`--category` 只决定落点）

```bash
for s in configure-bioxtas-raw-for-a-dataset reduce-saxs-frames-to-curves assess-guinier-fit-quality \
         process-sec-saxs-series correct-sec-saxs-baseline; do
  hermes skills install "flmaximwang/AgentSkill-UsingBioXTASRAW/skills/$s" --category saxs -y
done
```

## 蒸馏来源与边界（必读）

- **源 1/2（微信文章）**：作者 **刘广峰**，公众号「生物小角」；两篇都是 BioXTAS RAW 官方文档的**翻译 + BL19U2 线站本地化增补**（作者自己在文中给出官方链接）。
- **源 3（官方教程）**：BioXTAS RAW 官方文档 *Basic SEC-SAXS processing* 与 *Advanced Series processing – Baseline correction*（GPLv3 项目文档，程序安装目录 `docs/` 下亦有一份）。**用它的原因**：微信那篇把基线校正整节、"浓度未知 ⇒ 不能用绝对校准"的限制、区间质量警告都省掉了。
- **本仓库的性质**：微信文章的**衍生作品**（skill 的 R 段逐字引用了原文片段，每条 ≤150 字）。因此本仓库按上游材料的性质**只在私有范围存档、不公开分发**；引用与改编声明见 [`NOTICE.md`](NOTICE.md)。
- **明确不覆盖**：SVD / EFA / REGALS 分解、多序列（时间分辨）分析、WAXS 合并、IFT/GNOM、Shape&Size、3D 重建、RAW 的安装、从零标定一台陌生仪器、SEC 的实验设计（选柱/上样量/缓冲液匹配）。淘汰理由分别见两本的 `rejected/README.md`。
- **版本时效**：文字写于 2024（RAW 迭代会改变菜单文字与默认值）；探测器参数（Pilatus 2M / 1679×1475 / 172 µm）、标样（山嵛酸银 5.8 nm，一级峰 1.076 nm⁻¹）、BL19U2 的"末帧不参与强度校正"都是**该线站当时的配置**，不是通用事实。

## 目录

```
books/bioxtas-raw-manual/          # 第 1 本（RAW 基本操作）的审计轨迹
  source/article.md                # 源文本快照（抓取方式与元信息见文件头）
  BOOK_OVERVIEW.md                 # 阶段 0：结构 / 解释 / 批判 / 应用潜力
  candidates/                      # 阶段 1：5 个视角的 34 条原始候选
  verified.md                      # 阶段 1.5：三重验证（3 通过 / 4 淘汰）
  rejected/README.md
  INDEX.md  LEARNING_NOTE.md  TALKING_POINTS.md  test-results.md
books/sec-saxs-series/             # 第 2 本（SEC-SAXS + 基线校正）的审计轨迹
  source/article-1-wechat-sec-saxs.md            # 微信文章快照
  source/article-2-official-tutorial-s1-sec.md   # 官方 Basic SEC-SAXS processing
  source/article-3-official-tutorial-s2-baseline.md  # 官方 Baseline correction
  BOOK_OVERVIEW.md  candidates/（43 条）  verified.md（2 通过 / 3 淘汰）
  rejected/README.md  INDEX.md  LEARNING_NOTE.md  TALKING_POINTS.md  test-results.md
skills/<name>/SKILL.md             # 阶段 2 产出（+ references/、test-prompts.json）
```
