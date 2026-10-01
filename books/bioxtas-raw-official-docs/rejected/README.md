# rejected/ — 阶段 1.5 淘汰与降级记录

本册候选池 147 条 → 合并为 19 组单元 → **13 组通过**、**4 组降级为 reference 并入现有 skill**、**2 组整类淘汰**。
通过理由见 [`../verified.md`](../verified.md)。此处只记"为什么没成为独立 skill"，保留审计轨迹，允许日后捞回。

---

## R1 · 「造一份配置文件」不独立成 skill → 并入 `configure-bioxtas-raw-for-a-dataset`

- 候选：f02（造 cfg 六步链）、ce02（掩膜 Save to File ≠ Set）、a20（Energy/pixel/AgBh、归一化 /I1→7200.0）
- 理由：与 X1 是**同一个决策点**（"配置对不对/从哪来"）。若拆成两个 skill，二者 description 都会指向"配置"这个词，路由上互相竞争 —— 本机索引只显示 description 前 57 字符，两个同义触发语会直接导致误路由。
- 处置：X1 的 SKILL.md 增"配置怎么造出来（六步链）"一节，细节落 `references/build-a-configuration-file.md`。

## R2 · 「Kratky 柔性判读」不独立成 skill → 并入 `assess-guinier-fit-quality`

- 候选：ce04（坏 buffer 扣减让 Kratky 看似有柔性）、a05（无量纲 Kratky 峰位 √3≈1.73、峰高 3/e≈1.1）
- 理由：它在实际判读里是 Guinier 的**证伪步骤**（"看着像柔性"必须先排除坏扣减与聚集），单独成 skill 会鼓励"只看一张 Kratky 图就下结论"——正是文档警告的误用。
- 处置：X3 增「Kratky 交叉验证」段 + `references/kratky-and-flexibility.md`。

## R3 · 「曲线相似性三视图（残差/比率/CorMap）」不独立成 skill → 并入 `reduce-saxs-frames-to-curves`

- 候选：f15
- 理由：① `Average Only Similar Files` 本身就是还原流程里的一步（"哪些帧可以一起平均"）；② 文档对 CorMap 只有阈值级描述（tutorial 2 处 + api 2 处，无算法、无阈值推导），证据密度不足以支撑独立决策点。
- 处置：X2 增相似性段 + `references/raw-file-formats-and-cormap.md`。

## R4 · 「导出与数据格式互操作」不独立成 skill → 并入 X2 的 reference

- 候选：f18（.dat/.out/.ift 段结构、导出格式不可读回、Excel 导入）
- 理由：V3 不成立 —— 格式清单是"查表值"，不是需要判断的决策点（对照：本册通过的 13 组全部含"该不该信/该选哪个"的判断）。
- 处置：X2 的 reference 收录段结构 + Excel 导入坑。

## R5 · 整类淘汰：界面罗列 / 安装步骤 / changelog / 引文库 / 视频清单

- 候选：`20-manual` 的 The_Files_tab / The_Manipulation_Panel / Menus / Line_properties 等；`10-install` 全 16 节；`00-root` cite_raw / videos / changes
- 理由：
  1. 界面罗列与安装步骤**随版本与平台立即失效**（本册已实测到 manual 与 tutorial 的 8 处冲突）；
  2. 属"照抄即可用"而非"需要判断"，作为 skill 只会制造过时噪声；
  3. 引文库/视频清单与"怎么做"无关（引文已在 `candidates/` 留档，需要引用时查 `source/README.md` 与官方 cite 页）。
- 例外保留：`cite_raw` 里"用什么方法要引哪篇"的对应关系，作为事实存档留在 `candidates/`。

## R6 · 整类降级：术语池里纯事实条目 → 进各 skill 的 glossary reference

- 候选：g51–g61 中的具体设置值（pilatus_1m 参数、beamstop、AgBh）、g18–g30 中的文件后缀等
- 理由：这些是**查表值**，作为 skill 无路由价值；但它们是真做分析时的必需品。
- 处置：全部 67 条术语保留在 `candidates/glossary.md`；其中与某个 skill 强相关的搬进该 skill 的 `references/`（如 `.dat/.out/.ift` → X2，`a-score/NSD/χ²` → N4，`Vc/Vp/SAXSMoW 2` → N3，`Dmax/Shannon` → N2/N6）。
