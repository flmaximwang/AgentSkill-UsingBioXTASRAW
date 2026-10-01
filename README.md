# AgentSkill-UsingBioXTASRAW

把微信公众号文章 **《BioXTAS RAW程序使用说明》**（「生物小角」· 刘广峰，2024-04-26）蒸馏成的一组可被 agent 调用的 skill。
覆盖 3 个决策点：**配置是否就绪 → 一批帧怎么变成曲线 → 读出来的 Rg 信不信得过**。

蒸馏流水线是 **cangjie-skill（book2skill）的 RIA-TV++**：整文理解 → 5 视角提取（34 条候选）→ 三重验证（V1 跨域 / V2 预测力 / V3 独特性）→ RIA++ 构造 → Zettelkasten 链接 → 压力测试（独立盲测）→ 人性化输出（学习笔记 + 话术库）。
审计轨迹全部留在 [`books/bioxtas-raw-manual/`](books/bioxtas-raw-manual/)。

> **状态**：本地仓库已建、已提交；**尚未 push 到 GitHub、尚未安装进任何 profile**（等确认）。
> README 里的安装命令按"将要发布为 `flmaximwang/AgentSkill-UsingBioXTASRAW`（private）"写。

## 索引

| skill | 用途 | 可执行入口 |
|---|---|---|
| [configure-bioxtas-raw-for-a-dataset](skills/configure-bioxtas-raw-for-a-dataset/SKILL.md) | 确证会话已加载当天的 `.cfg`（定心 / 样品-探测器距离 / 掩膜 / 标样），用标样一级峰（1.076 nm⁻¹）把"q 轴对不对"变成可检验事实 | `references/bioxtas-raw-glossary.md` |
| [reduce-saxs-frames-to-curves](skills/reduce-saxs-frames-to-curves/SKILL.md) | 2D 帧 → 1D 曲线的四段流水线（积分 / 平均 / 扣减 / 落盘），含 `A_`·`S_`·颜色·`*` 四个自检信号 | `references/raw-workspace-and-naming.md` |
| [assess-guinier-fit-quality](skills/assess-guinier-fit-quality/SKILL.md) | Guinier 取点（n_min/n_max）与判读（残差形态、q_max·Rg ≈ 1.3、Rg 单位 = 1/q），报告必须带 q 区间 | —（判据写在正文节） |

给人看的两份文档：[学习笔记](books/bioxtas-raw-manual/LEARNING_NOTE.md) · [话术库](books/bioxtas-raw-manual/TALKING_POINTS.md)。
skill 总览与引用图：[`books/bioxtas-raw-manual/INDEX.md`](books/bioxtas-raw-manual/INDEX.md)。

## 安装（三段式标识符，按仓库内路径，不需要 tap；`--category` 只决定落点）

```bash
for s in configure-bioxtas-raw-for-a-dataset reduce-saxs-frames-to-curves assess-guinier-fit-quality; do
  hermes skills install "flmaximwang/AgentSkill-UsingBioXTASRAW/skills/$s" --category saxs -y
done
```

## 蒸馏来源与边界（必读）

- **源**：微信公众号文章（作者 **刘广峰**，公众号「生物小角」），是 BioXTAS RAW 官方文档的**翻译 + BL19U2 线站本地化增补**。
- **本仓库的性质**：该文章的**衍生作品**（skill 的 R 段逐字引用了原文片段，每条 ≤150 字）。
  因此本仓库按上游材料的性质**只在私有范围存档、不公开分发**；引用与改编声明见 [`NOTICE.md`](NOTICE.md)。
- **原文只覆盖到"基本还原 + 一次 Guinier 判读"**。明确不覆盖：SEC-SAXS 处理、分子量测定（原文只有六条路线名）、IFT/GNOM、Shape&Size、3D 重建、RAW 的安装、从零标定一台陌生仪器。淘汰理由见 [`rejected/README.md`](books/bioxtas-raw-manual/rejected/README.md)。
- **版本时效**：文字写于 2024（RAW 的迭代会改变菜单文字与默认值）；文中的探测器参数（Pilatus 2M / 1679×1475 / 172 µm）与标样（山嵛酸银 5.8 nm，一级峰 1.076 nm⁻¹）是 **BL19U2 当时的配置**，不是通用事实。

## 目录

```
books/bioxtas-raw-manual/        # 审计轨迹（阶段 0–5 的全部产出）
  source/article.md              # 源文本快照（抓取方式与元信息见文件头）
  BOOK_OVERVIEW.md               # 阶段 0：结构 / 解释 / 批判 / 应用潜力
  candidates/                    # 阶段 1：5 个视角的 34 条原始候选
  verified.md                    # 阶段 1.5：三重验证记录（3 通过 / 4 淘汰）
  rejected/README.md             # 淘汰与降级理由
  INDEX.md  LEARNING_NOTE.md  TALKING_POINTS.md   # 阶段 3 / 5
  test-results.md                # 阶段 4：盲测结果
skills/<name>/SKILL.md           # 阶段 2 产出（+ references/、test-prompts.json）
```
