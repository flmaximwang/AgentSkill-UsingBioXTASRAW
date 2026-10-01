# CRYSOL / PDB2SAS 参数、症状—处方与产物清单（reference）

源：BioXTAS RAW 官方文档 v2.4.2 —— `40-tutorial.md · tutorial/s2_crysol.rst` 与 `tutorial/s2_pdb2sas.rst`；对照出处 `30-saxs.md · saxs/saxs_bead_models.rst`（FAQ：拟合 vs dock）。
供 `fit-a-high-resolution-model-to-data` 引用。所有数值逐字取自源（教程示例值明确标注"示例"）。

> 界面文字随 RAW 版本变化；定位不到控件时以程序自带 `docs/` 或在线文档为准。

---

## 一、两个计算器：概念与输入差异

| | CRYSOL | PDB2SAS |
|---|---|---|
| 归属 | ATSAS 包；**RAW 调用它需要装 ATSAS** | **DENSS 内建**（对应 DENSS 命令行工具 `denss.pdb2mrc.py`） |
| RAW 默认 | 否（但**可被用户设成默认**） | **是**（除非被改过） |
| 输入结构 | `.pdb` 或 `.cif` | **只支持 `.pdb`**（`.cif` 目前不支持） |
| 算法 | 球谐展开（harmonics 数为关键） | 先算实空间电子密度图（原子 / 排除溶剂 / 水化层）→ 傅里叶变换 + 球平均 → 1D 曲线 |
| 能拟合什么 | 排除溶剂、水化层（作为拟合参数） | 排除溶剂、水化层（作为拟合参数） |
| 结果里的标志量 | Data、**Chi²、Prob** | Data、**Chi²** |
| 额外产物 | `.abs`（绝对刻度 1/(cm·(mg/ml))）与 `.int`（任意刻度）成对 | 单条理论曲线（教程示例 `1XIB_4mer.dat`） |

**"计算即拟合"在这两个计算器上的含义相同**：把实验数据加入计算，溶剂/水化层/排除体积与数据一起拟合；**不加数据**则得到 minimal 曲线（官方：minimal "即使模型与溶液结构吻合也常常拟合不好"）。

---

## 二、参数表

### 2.1 CRYSOL

| 参数 / 设置 | 位置 | 说明 |
|---|---|---|
| **Harmonics** | 参数面板 | 球谐项数。**高长径比物体需要更多**；官方示例：对细长棒蛋白把 harmonics 设为 **100** 后拟合明显优于默认。球状蛋白几乎无差别。 |
| 溶剂密度与对比度 | Advanced Settings | **需先关掉 "Fit solvent"** 才能手改。 |
| Save all outputs to folder | Advanced Settings | 勾选后可保存全部 CRYSOL 输出（如 `.log`、`.alm`）。 |
| 其它高级设置 | Advanced Settings | 见 CRYSOL 手册；教程只点名了上述两项。 |

### 2.2 PDB2SAS

| 参数 / 设置 | 位置 | 说明 |
|---|---|---|
| **N samples (real space)** | 主参数面板 | 默认 **128**，对细长蛋白不足（实空间 voxel 太大 → 理论拟合的最大 q 太小）→ 改 **256**。**取 2 的幂（64/128/256…）速度最好**，任意偶数也可用。 |
| **Voxel size** | Advanced Settings | **显式指定会覆盖 N samples**——与 N samples 是同一件事的两种给法。 |
| 溶剂密度与对比度 | Advanced Settings | **需先关掉 "Fit solvent" 与 "Fit hydration shell"** 才能手改。 |
| Save all outputs to folder | Advanced Settings | 保存全部 PDB2SAS 输出（如 `.dat`、`.fit`）。 |
| 其它高级设置 | Advanced Settings | 见 PDB2SAS 手册。 |

### 2.3 程序级设置（不是窗口内参数）

| 项 | 位置 | 说明 |
|---|---|---|
| **Default structure calculator** | `Options → Advanced Options → General Settings` | 决定"直接 Plot 一个 `.pdb` 时用谁"。默认 = PDB2SAS，但**可能已被某个用户改成 CRYSOL**；要重置就选 PDB2SAS。 |
| Model 勾选状态 | 两个窗口的 Models 列表 | **只有被勾选的模型参与计算**；取消勾选即停用（不必删除）。 |
| Experimental data 勾选状态 | 两个窗口的 Experimental data 列表 | 勾上才会拟合；**只有已载入 RAW 的数据才能加进该列表**。不勾任何数据 = 算 minimal 曲线。 |

---

## 三、症状 → 处方

| 症状 | 最可能的原因 | 处方 |
|---|---|---|
| 低 q 差很多 | 算的是 minimal 曲线（数据未参与） | 把数据加入并勾选后重算；看结果表是否出现 Chi² |
| 结果表 Data/Chi²/Prob 为空 | 未拟合数据 | 同上（CRYSOL 有 Prob，PDB2SAS 只有 Data/Chi²） |
| 细长蛋白怎么调都拟合差 | harmonics 不够 | 提高 harmonics（示例 100）；同时确认 N samples 足够 |
| PDB2SAS 理论曲线 q_max 到不了实验最大 q | N samples（128）太小 | 改 256（2 的幂）；或显式设 voxel size |
| 想改溶剂密度却改不动 | "Fit solvent"（PDB2SAS 还有 "Fit hydration shell"）仍开着 | 先关掉对应 Fit 开关 |
| `.cif` 给 PDB2SAS 没结果 | 不支持 `.cif` | 转 `.pdb`；或走 CRYSOL |
| 换了电脑后结果不一样（来源/尺度/参数集都变） | 默认计算器被改过 | 去 General Settings 核对/重置 |
| 想判断"该信珠模型还是该信高分辨结构" | 次序问题 | 用拟合裁决：拟合差 → 结构不匹配数据；拟合好而珠模型不吻合 → **错的是珠模型** |

---

## 四、结果字段与落盘产物

| 项 | CRYSOL | PDB2SAS |
|---|---|---|
| 结果字段（拟合时） | Data、Chi²、Prob | Data、Chi² |
| 结果字段（未拟合） | 仅部分参数；Data/Chi²/Prob 缺 | 仅部分参数；Data/Chi² 缺 |
| 窗口右侧图 | 理论曲线；拟合时另加数据与不确定度归一化残差 | 同左 |
| 送回 Profiles 的曲线 | `<模型>_<数据>_FIT` | `<模型>_<数据>_FIT` |
| 表导出 | 结果表右键 Export Data → `.csv` | 同左 |
| 全部计算输出 | `Save all outputs to folder`（`.log`/`.alm` 等） | `Save all outputs to folder`（`.dat`/`.fit` 等） |
| 报告 | 右键 Profiles 里的 `_FIT` 曲线 → Save report → pdf（含理论曲线参数汇总表） | 同左 |

**`_FIT` 后缀是"这是拟合结果"的机检标记**；只有 `.abs`/`.int` 而没有 `_FIT` 时，说明算的是独立生成的理论曲线。

---

## 五、把教程的操作序列留档（可复现的最小集）

**CRYSOL 路线（示例数据 `1XIB_4mer.pdb` + `glucose_isomerase.dat`）**

1. Files 面板点 `1XIB_4mer.pdb` 的 Plot → 得 `1XIB_4mer.abs` 与 `1XIB_4mer.int`（**minimal**，默认参数）。
2. `Tools → ATSAS → CRYSOL` → Models 区 Add `1XIB_4mer.pdb` → Start（仍是 minimal：结果表 Data/Chi²/Prob 空）。
3. 载入 `glucose_isomerase.dat` → Experimental data 区 Add 并勾选 → Start → 得全部参数 + 残差图。
4. OK → `1XIB_4mer_glucose_isomerase_FIT` 进入 Profiles。
5. 参数验证：`SASDP43.dat` + `Brpt55_M_Zn.pdb`，两个窗口分别用默认与 **100 harmonics** 跑，比较拟合。

**PDB2SAS 路线（示例数据同上，结构须为 `.pdb`）**

1. Files 面板点 `1XIB_4mer.pdb` 的 Plot → 得一条理论曲线（教程示例显示为 `1XIB_4mer.dat`）。
2. `Tools → DENSS → PDB2SAS` → Add 模型 → Start。
3. 加 `glucose_isomerase.dat` 并勾选 → Start → 得 Data/Chi² 与残差图 → OK 送回 Profiles。
4. 参数验证：`SASDP43.dat` + `Brpt55_M_Zn.pdb`，默认（**N samples 128**）先跑一遍 → 第二个窗口改 **256** 再跑 → 曲线覆盖全 q。

**多模型/多数据的入口**：Profiles 面板选中要用的 profile(s) → 右键其一 → `Other Analysis → Fit Model (CRYSOL)` 或 `Fit Model (DENSS PDB2SAS)` → 窗口自动带上选中数据。

---

## 六、版本、依赖与引用

| 项 | 说明 |
|---|---|
| 教程基线 | 本 reference 的界面/字段按 **RAW v2.4.2** 的 CRYSOL 与 PDB2SAS 教程；教程中 CRYSOL 路线要求安装 ATSAS。 |
| ATSAS | CRYSOL 来自 ATSAS；教程其他章节用 ATSAS 3.1.1（本流程本身不依赖 CIFSUP 的 ≥3.1.0 约束，但若同时用对齐分支需注意）。 |
| 引用 | 用 RAW 跑 CRYSOL → 引用 CRYSOL 手册给出的文献；用 PDB2SAS → 引用其论文（`https://www.cell.com/biophysj/abstract/S0006-3495(23)00670-7`）；两者都应同时引用 RAW 论文。 |

---

## 七、材料盲点（不要在回答里补造）

- **Chi² 的好/坏阈值**：文档只做相对比较（100 harmonics 优于默认、256 优于 128），**没有给"多大算拟合好"的判据**。不要从别处（例如珠模型章节的 χ² 讨论）搬阈值过来。
- **`Prob` 的定义与判读**：文档只说它在拟合数据时出现，未给解释。
- **Volatility / 拟合优度之外的判据**：官方没有给"两个候选模型谁是溶液态"的 SAXS 判据，只有"拟合差 = 不匹配"这个方向性结论。
- **FoXS**：方法学章节把它与 CRYSOL 并列为"直接拟合"的推荐程序，但 **RAW 未集成**；提及时应注明是文档之外的选项。
- **minimal 曲线的用途**：文档只警告它不适合用来判拟合好坏，**没有给出其它合法用途**（例如只做可视化的场景未被讨论）。
