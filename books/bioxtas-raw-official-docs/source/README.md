# 来源档案 — BioXTAS RAW 官方文档（v2.4.2）

## 1. 这份语料是什么

- **实体**：BioXTAS RAW **v2.4.2** 官方 Sphinx 文档源码树，随源码同仓发布（GPLv3）。
- **本机位置**：`~/Repositories/bioxtasraw/docs/source/`（来自 `git clone --branch v2.4.2 --depth 1 https://github.com/jbhopkins/bioxtasraw.git`）。
- **在线同一份**：<https://bioxtas-raw.readthedocs.io/en/latest/>。
- **规模**：**98 个 rst 文件 / 18,646 行**；剔除 `changes.rst`（2,636 行 changelog）后为 **97 文件 / 16,010 行**。
- **分节规模**（清理后文本行）：

  | 分节 | 文件数 | 行数 | 作用 |
  |---|---|---|---|
  | `00-root` | 9 | 404 | 首页/引用/求助/安装总入口/教程与手册索引 |
  | `10-install` | 16 | 730 | 三平台预构建与源码安装、故障排查 |
  | `20-manual` | 19 | 4,605 | **旧版 GUI 手册（已自我声明过时）** |
  | `30-saxs` | 5 | 1,572 | SAXS 方法学与最佳实践（Guinier/P(r)/MW/珠模型） |
  | `40-tutorial` | 37 | 6,591 | **现行操作权威**：s1 基础 / s2 进阶 / s3 配置 / s4 导出 |
  | `50-api` | 11 | 673 | RAWAPI（脚本化） |

## 2. 语料是怎么生成的（可复现）

```bash
# 1) 克隆（本机已验证可达）
git clone --branch v2.4.2 --depth 1 https://github.com/jbhopkins/bioxtasraw.git ~/Repositories/bioxtasraw
# 2) rst → 纯文本语料（剔除 sphinx 指令、把下划线标题转 markdown、展开 :ref:/:doc: 角色）
python3 ~/.hermes/cache/scratch/rawdocs_make_corpus.py
# 产物：~/.hermes/cache/scratch/rawdocs/{00-root,10-install,20-manual,30-saxs,40-tutorial,50-api}.md
#       与 index.txt（逐文件行数）
```

清洗规则：丢 `.. directive::` 及其缩进块（保留 note/warning 的正文）、标题下划线 → `#/##/###`、`:ref:`/`:doc:`/`:func:` 等角色只留目标名、`choices.rst` 不纳入。

## 3. 证据分级（本项目的判据来源）

蒸馏时**只有 B 级可作 skill 的事实依据**；A 级仅作矛盾对照与历史说明。

- **A 级 · 文档自我声明过时**（不得作为唯一依据）
  - `20-manual` 全部 19 节：每节首行同一句警告 —— `The manual is current several versions out of date`（grep 命中 19 处；加 `00-root` 的 1 处共 20 处），原文要求「please refer to the tutorial for the most up-to-date information」。
  - `00-root` videos.rst：旧版视频自承「may be out of date」。
- **B 级 · 当前版本权威**
  - `00-root` index.rst / install.rst / cite_raw.rst（给出 2.4.2 下载物与当前特性表）。
  - `40-tutorial`（37 节，操作权威；manual 反复指向它）。
  - `50-api`（RAWAPI 唯一权威）。
  - `30-saxs`（方法学权威，且自称不讲 RAW 操作）。
- **C 级 · 有版本锚点但内容偏旧**
  - `10-install`：仍写「tested on Python 3.7/3.8」，并保留 Python 2 段落（Py2 已 EOL）。

## 4. 已记录的文档内部矛盾（来自 digest-90-audit，逐条带文件行号）

| # | 矛盾 | 证据 |
|---|---|---|
| C1 | Python 版本 | `20-manual` 称「only compatible with Python 2.7, not 3.x」 ↔ `10-install` 三处「As of 2.0.0, RAW is Python 3 compatible」 |
| C2 | MW 方法数 | `20-manual`「Four different methods」 ↔ `40-tutorial`/`30-saxs`「4 + ATSAS 2 = 六法」；Bayesian 在 manual 命中 0 |
| C3 | 绝对校准标准 | manual 只讲 water；`glassy carbon` 在 tutorial 命中 18、其余文件 0 |
| C4 | ATSAS 集成范围 | manual「GNOM/DAMMIF/AMBIMETER，需 ≥2.7.1」 ↔ tutorial 用到 10 个 ATSAS 程序、要求 ≥3.1.1 |
| C5 | 特性总表 | 现行 index.rst 含 DENSS/DIFT/REGALS/Eiger/Shape&Size/Bayesian；manual 特性表全缺 |
| C6 | 分析窗口清单 | manual 列 8 个窗口，无 REGALS/DENSS/DIFT/Similarity |
| C7 | 序列文件格式 | manual 称 `.sec` ↔ tutorial/API 用 `.hdf5`（`load_series` 文档写「.hdf5 or .sec」） |
| C8 | 平台支持 | manual「macOS 10.9–10.12 / Win 7、8.1、10」 ↔ install.rst「macOS 13+ / Win11」；Win10 预构建止于 2.3.1 |
| C9 | tutorial 自身编号错位 | introduction 把小节号与 section3/section4 文件号互换了 |
| C10 | 行为随版本变化 | `30-saxs` 自承「newer versions of RAW do this automatically」 |
| C11 | water 校准数值 | manual 无具体值 ↔ tutorial 给「4 C、应近 0.00077」 |

## 5. 已知盲区（影响后续 skill 的边界声明）

1. **API 参考正文是空壳**：`50-api` 的 `main_api.rst / profiles_and_ifts.rst / series.rst / settings.rst` **每个只有标题、零正文**；函数清单与参数只存在于 examples 里。→ 涉及 API 的 skill 只能声明「依据 examples 实测签名」，不能声称有完整参考。
2. **CorMap 只有一句话级**：全库 `CorMap` 仅 4 处（tutorial 2 / api 2），无算法描述、无阈值推导。
3. **循环引用**：`30-saxs` 把 GUI 操作全部外包给 tutorial，tutorial 的绝对刻度细节又写「see the manual for details」——而 manual 自承过时。
4. **默认值表缺失**：manual 只到「有该控件」；多处默认值（如 Vc 经验系数、Vp 密度）不在文档中成表。

## 6. 不做成 skill 的内容（含理由）

1. **纯界面罗列**（Files tab / Manipulation Panel / Information panel / Line properties / Menus 逐项说明）：随 UI 改版即失效，且属"照抄即可用"而非"需要判断"。
2. **安装步骤**（`10-install` 全 16 节）：强绑平台与包管理器、一次性动作，且带 C1/C8 类版本矛盾。→ 只把「配置来源（cfg）与校准状态」这类**判据**留在 skill 里。
3. **changelog / 引文库 / 视频清单**：一次性、易腐、与"怎么做"无关；`cite_raw.rst` 作为事实存档保留在 candidates 里。
4. **A 级 manual 正文细节**：与 tutorial 冲突者一律以 tutorial 为准，manual 只作历史对照。
