# BOOK_OVERVIEW — BioXTAS RAW 官方文档（v2.4.2 全站）

> 阶段 0 产出（Adler 四步：结构 / 解释 / 批判 / 应用）。
> 语料与证据分级见 [`source/README.md`](source/README.md)。判据来源：`digest-00-root-install`、`digest-20-manual`、`digest-30-saxs`、`digest-40-tutorial-api`、`digest-90-audit`。
> 本文件只依据 B 级来源（tutorial / api / saxs / index+install）下结论；A 级（manual）仅用于矛盾对照。

---

## 0. 一句话主旨

**这是一套"从 2D 图像到 3D 模型"的完整可执行流水线手册**：它真正教给读者的是**一串判据**——每一步都告诉你"什么样的结果才算数、什么样的结果其实是伪影"；而 RAW 只是承载这些判据的 GUI/API。

---

## 1. 结构（Adler 第一步：这本书在讲什么、怎么分块）

文档不是按"线性章节"组织的，而是**按职责分四层**，四层各有一份权威：

| 层 | 分节 | 职责 | 权威度 |
|---|---|---|---|
| ① 索引与安装 | `00-root`、`10-install` | 我该装哪个包、这软件能干什么、引用谁 | B（index/install） |
| ② 操作流程 | `40-tutorial`（37 节：s1 基础 9 / s2 进阶 14 / s3 配置 6 / s4 导出 3 + 导航） | 每个任务**怎么点、参数填什么、看到什么才算成功** | **B（最高）** |
| ③ 方法学 | `30-saxs`（5 节：Guinier / P(r) / MW / 珠模型 / 引言） | 为什么这么判、阈值从哪来、适用边界 | B |
| ④ 脚本化 | `50-api`（11 节） | 同样的事怎么用 Python 批量做 | B（但参考正文是空壳，见 §3.3） |
| （对照层） | `20-manual` | 旧版 GUI 手册，**全 19 节自承过时** | **A（不作依据）** |

**四条操作主线**（tutorial 的实际组织方式）：

- **Section 1 · 基础处理**：载 cfg → 载图像 → 积分 → 平均 → 扣背景 → 存 `.dat`；Guinier；MW；Kratky；相似性；SEC-SAXS 基础；WAXS 合并；保存报告。
- **Section 2 · 进阶分析**：IFT 三法（GNOM / DIFT / BIFT）→ 形状歧义（AMBIMETER）→ 3D 重建（DAMMIF/N、DENSS）→ 对齐（CIFSUP / DENSS align）→ 理论曲线（CRYSOL / PDB2SAS）→ 去卷积（SVD / EFA / REGALS）→ 基线校正 → 多序列（时间分辨）。
- **Section 3 · 造一份配置文件**：做掩膜 → 定心/几何标定 → 归一化 → 绝对刻度（水 / 玻碳）→ 指定 MW 标准 → 存 `SAXS.cfg`。
- **Section 4 · 出数据**：绘图定制与导出 CSV → 外部软件读 RAW 数据（`.dat`/`.out`/`.ift`/`.csv` 格式与 Excel 导入）。

---

## 2. 解释（Adler 第二步：它的内在逻辑是什么）

### 2.1 贯穿全篇的三条"事实链"

1. **配置链**：`图像 = f(几何, 掩膜, 归一化)` → 配置错 ⇒ **不报错但 q 轴与 Rg 全错**（s3 三节 + s1_basic 的"处理前必须载入 cfg"）。
2. **强度链**：`I(q) = (样品 - 缓冲液) × 归一化 × 绝对刻度` → 顺序不可换：绝对刻度算常数前**必须关掉**绝对刻度、改归一化后必须重算（s3_abswater / s3_abscarbon）。
3. **判据链**：每一步都有"通过条件"：
   - Guinier：`q_min·Rg < 0.65`、`q_max·Rg ≈ 1.3`（球/盘）/ `1.0`（棒）、残差平坦随机分布（smile=聚集、frown=排斥）。
   - P(r)：Dmax 处平滑趋零、χ²≈1、`P(0)=P(Dmax)=0`、Rg/I(0) 与 Guinier 自洽、恒正（膜蛋白例外）；**Dmax 精度不优于 5%**。
   - MW：SAXS 通则 ~10% 不确定度、**不该用来定分子量**（该用 MALS）；六法各带不确定度与失效域。
   - 珠模型：a-score<2.5（最好<1.5）、NSD<1.0、剔除 0–2 个、单一簇、χ²≈1、模型 Rg/Dmax 对上 P(r)（Rg ~5%、Dmax ~10%）、体积估 MW 差 >20–25% ⇒ 可疑。
   - 去卷积：自相关 >0.6–0.7 才算显著分量；EFA 的 χ² 应均匀≈1；REGALS 的 lambda 按数量级调。
4. **可证伪优先**：文档反复强调 SAXS「擅长证伪而非生成形状」——同一曲线可对应多个形状，**数据质量高不保证重建好**。

### 2.2 能力地图（index.rst 的 25 项 → 谁覆盖）

| 能力 | 文档出处 | 现有 skill 是否覆盖 |
|---|---|---|
| 图像→1D 曲线（积分/平均/扣减/合并/rebinn） | s1_basic、s1_waxs | ✅ `reduce-saxs-frames-to-curves`（缺 Merge / rebin / WAXS） |
| 配置就绪核对 | s3_*、s1_basic | ✅ `configure-bioxtas-raw-for-a-dataset`（缺掩膜/定心/归一化/绝对刻度/标样整章） |
| Guinier / Rg / I(0) | s1_guinier、saxs_guinier | ✅ `assess-guinier-fit-quality`（缺 q_min·Rg 下限、形状分档 1.0/1.3/1.7、Kratky 交叉验证） |
| 分子量六法 | s1_mw、saxs_mw | ❌ **新** |
| IFT / P(r)（GNOM、DIFT、BIFT）与 Dmax 选择 | s2_gnom、s2_dift、s2_bift、saxs_ift | ❌ **新** |
| 形状歧义 AMBIMETER | s2_ambimeter、saxs_bead_models | ❌ **新** |
| 3D 珠模型 + 平均/聚类评估 | s2_dammif、saxs_bead_models | ❌ **新** |
| DENSS 电子密度 | s2_denss | ❌ **新** |
| 对齐（CIFSUP / DENSS alignment） | s2_align | ❌ 可并入重建评审技能 |
| 理论曲线拟合（CRYSOL / PDB2SAS） | s2_crysol、s2_pdb2sas | ❌ **新** |
| 去卷积 SVD / EFA / REGALS | s2_svd、s2_efa、s2_regals | ❌ **新** |
| SEC-SAXS 系列处理 | s1_sec | ✅ `process-sec-saxs-series` |
| 基线校正（Linear / Integral） | s2_baseline | ✅ `correct-sec-saxs-baseline` |
| 多序列（时间分辨） | s2_multiseries | ❌ **新** |
| 绝对刻度（水 / 玻碳 Simple+NIST） | s3_abswater、s3_abscarbon | ❌ **新** |
| 相似性检验 CorMap / 平均只取相似帧 | s1_similarity | ❌ 可并入还原或新技能 |
| 图形导出 / 数据格式互操作 | s4_* | ❌ 可并入还原或 API 技能 |
| RAWAPI 脚本化 | `50-api` | ❌ **新** |

---

## 3. 批判（Adler 第三步：它靠不住的地方）

### 3.1 证据分层是硬性的

manual 全部 19 节顶部都有同一句「落后好几个版本」；它与 tutorial 在 **Python 版本、MW 方法数、绝对校准标准、ATSAS 集成范围、特性表、窗口清单、序列文件格式、平台支持** 八处直接冲突（完整 11 条见 `source/README.md` §4）。⇒ **本项目一律以 tutorial + api + saxs 为准；manual 只做对照**，并且任何"手册说 X、教程说 Y"的地方都以教程为事实。

### 3.2 文档自己承认行为会随版本漂移

`30-saxs` 明写「newer versions of RAW do this automatically」（指 GNOM 起始 q 对齐 Guinier）；DAMCLUST 在 ATSAS ≥3.1.1 下部分字段为空、DAMMIN 不提供 Dmax；PDB2SAS 是"当前默认"但可被用户改回 CRYSOL。⇒ 相关 skill 必须**绑定版本并给出"如果不一致该怎么核对"**。

### 3.3 盲区（影响 skill 能承诺什么）

- **API 参考正文为空壳**（4 个文件只有标题），函数清单只在 examples 中 → API 类 skill 的边界必须写"依据 examples 的实测签名"。
- **CorMap 无算法与阈值推导**，只给"less stringent threshold / longest edge"级经验。
- **tutorial ↔ manual 互相指认**形成循环引用（saxs 说操作看 tutorial，tutorial 说绝对刻度细节看 manual，而 manual 过时）。
- **默认值不成表**：如 Vc 经验系数、Vp 密度只在文中零散出现。

### 3.4 不适合当作 skill 的部分

纯界面罗列、安装步骤、changelog/引文/视频清单（理由见 `source/README.md` §6）。

---

## 4. 应用（Adler 第四步：这份文档能变成什么）

### 4.1 蒸馏目标（与现有仓库合并后的形态）

保持现有 5 个 skill 的**"决策点"风格**（每个 skill = 一个判断点，description 写触发语与不覆盖范围），把官方文档补成一条**完整的判据流水线**：

```
[配置就绪] → [图像→曲线] → [Guinier 可信度] → [IFT/P(r) 与 Dmax] → [MW 方法选择]
      ↓                                                                   ↓
[绝对刻度/掩膜/标定]  ←（造 cfg）                            [形状歧义 AMBIMETER]
                                                                          ↓
[SEC 系列处理] → [基线校正] → [去卷积 SVD/EFA/REGALS]        [3D 重建：珠模型/DENSS → 评估]
                                                                          ↓
                                          [理论曲线拟合 CRYSOL/PDB2SAS] ←（对照）
                                          [多序列时间分辨]  [RAWAPI 脚本化]  [导出与格式互操作]
```

### 4.2 与现有 5 个 skill 的合并策略（扩写 vs 新建）

| 现有 skill | 处理 | 具体补什么 |
|---|---|---|
| `configure-bioxtas-raw-for-a-dataset` | **扩写** | 加"配置来源链"（掩膜→定心→归一化→绝对刻度→MW 标准各自失效时的症状）；保留"用 AgBh 一级峰把配置变成可检验事实" |
| `reduce-saxs-frames-to-curves` | **扩写** | Merge（SAXS/WAXS，scale 0.000014）、Rebin、"Average Only Similar Files"（CorMap）、Save report / export CSV、`.dat` 格式细节 |
| `assess-guinier-fit-quality` | **扩写** | 加 `q_min·Rg < 0.65` 下限、形状分档 1.0/1.3/1.7、残差 smile/frown 的归因（聚集/排斥）与补救清单 |
| `process-sec-saxs-series` | **扩写** | 加第二 buffer 区的处理、双 buffer 警告、Series 导出 CSV 的列语义 |
| `correct-sec-saxs-baseline` | **扩写** | 加"警告通常可忽略"的判据（起止区斜率跨 q 不一致）、积分法只允许正向校正 ⇒ 需负校正的 q 会被整体过校、先截断到低 q 再校 |
| — | **新建候选** | ① IFT/P(r) 与 Dmax；② MW 六法选择；③ 绝对刻度（水/玻碳）；④ 造 cfg（掩膜/定心/归一化）；⑤ 3D 重建与评估（珠模型 + DENSS + 对齐）；⑥ 理论曲线拟合（CRYSOL/PDB2SAS）；⑦ 去卷积（SVD/EFA/REGALS）；⑧ 多序列时间分辨；⑨ RAWAPI 脚本化；⑩ Kratky 柔性判读（含"坏扣减也会像柔性"） |

### 4.3 验收标准（沿用本项目既有红线 + 本卷追加）

1. 每个 skill 通过三重验证：**V1 跨域**（≥2 个互不依赖的文档场景依赖它）/ **V2 预测力**（能回答文档没明说的新问题）/ **V3 独特性**（不是任何聪明人都会说的常识）。
2. 每个 skill 六段齐全：R（引用 ≤150 字/段，标 FILE）/ I / A1 / A2（= description 的触发语）/ E（可执行步骤）/ B（边界 + 不覆盖什么）。
3. 事实层必须标证据级别；**凡 manual 与 tutorial 冲突处，一律采 tutorial 并显式标注**。
4. 数值阈值必须逐字准确（qRg 上限、8/Rg、0.25–0.30 1/Å、Dmax 5%、NSD 0.6/1.0、a-score 1.5/2.5、χ²、体积/MW 常数 1.66、λ 数量级、CorMap p 阈值等）。
5. 每条 description 的前 57 字符必须是可路由的触发信号（本机索引只显示前 57 字符 + "..."）。
6. 每个 skill 带 `test-prompts.json`，含"应调用 / 诱饵（不该调用）/ 边界模糊"三类；最后跑独立盲测。
