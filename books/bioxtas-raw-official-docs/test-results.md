# test-results.md — 第 3 本（官方文档卷）阶段 4 压力测试

## 判定口径

沿用前两册并收紧一条：**只给评测者 description 的前 57 字符 + "..."**（本机索引真实可见窗口，实测 `agent/skill_utils.py:761`，`SKILL_PROMPT_DESC_LIMIT=60`），
不给正文、不给 references。13 个 skill 固定映射为 A–M（按 slug 字母序，见下表），另有 `none` 选项。

## 被测技能（索引可见描述）

- **A** = 时间分辨/多序列 SAXS 精修（一批 series 要一起逐点平均与扣减）：多 series 载入（文件名模板 ...
- **B** = 从一条扣减过的 SAXS 曲线读 Rg/I0，并判断这次 Guinier 拟合信不信得过：n_min 低 q 取点...
- **C** = SEC-SAXS/SAXS 分子量该用哪一法、能不能信：两轴定位（RAW 原生 4 法 vs ATSAS 2 法；...
- **D** = 要算 P(r)/距离分布、定 Dmax、选 GNOM/DIFT/BIFT 时用：三法按下游重建程序选，Dmax 八...
- **E** = 处理 SAXS 图像前先核对该会话已加载当天的 .cfg（定心/样品-探测器距离/掩膜/标样），否则积分不报错但 ...
- **F** = 扣减后强度-帧号仍漂移时按性质选基线校正：束流/仪器漂移→Linear，毛细管污垢→Integral；含过校正识别...
- **G** = 重叠洗脱峰去卷积（SEC 主峰有肩、IEC 盐梯度、滴定/时间分辨）按复杂度选 SVD/EFA/REGALS：判分...
- **H** = DAMMIF/DENSS 形状重建做完后评估能不能用：a-score/平均 NSD/被剔模型数/聚类数/各模型 χ...
- **I** = 把高分辨结构（晶体/CryoEM/AlphaFold）对照 SAXS 数据时用「计算即拟合」：不要先生成 mini...
- **J** = 处理 SEC-SAXS 系列（连续洗脱帧）→Rg/MW 平台判据与 MW(Vc/Vp) 成一条曲线：色谱图→buf...
- **K** = SAXS 强度要放到绝对刻度（cm⁻¹）、算水/玻碳绝对标度常数时用它：按可用条件在水、玻碳 Simple、玻碳 ...
- **L** = 把 SAXS 帧还原成 1D 曲线（积分→平均→扣减→存 .dat）；A_/S_/* 自检进度。SEC-SAXS ...
- **M** = 用 RAW 的 Python API（RAWAPI）写脚本批量处理 SAXS：load→analyse→save ...

## 测试集（26 条 = 13 正面 + 13 诱饵/边界；按固定种子打乱）

| n | 提问 | 出处（owner） | 类型 | 判分目标 |
|---|---|---|---|---|
| 1 | 我把线站的数据拷回自己电脑，用 RAW 积分出来的 q 轴跟文献差了一个数量级，Rg 也完全对不上，是数据坏了吗？ | configure-bioxtas-raw-for-a-dataset | should_trigger | = 本 skill |
| 2 | 手上是一个样品的 20 张 tif，怎么平均成一条曲线并扣掉缓冲液？ | process-sec-saxs-series | should_not_trigger | reduce-saxs-frames-to-curves |
| 3 | BioXTAS RAW 在哪儿下载？Windows 和 Mac 分别装哪个包？ | configure-bioxtas-raw-for-a-dataset | should_not_trigger | none |
| 4 | DAMMIF 跑完了，出来一堆数字，我怎么判断这个形状能不能写进文章？ | evaluate-a-shape-reconstruction | should_trigger | = 本 skill |
| 5 | 我这条曲线的 Rg 是 2.4 nm，能说明我的蛋白是什么状态吗？单体还是二聚体 | reduce-saxs-frames-to-curves | should_not_trigger | assess-guinier-fit-quality |
| 6 | 我的 DAMMIF 重建跑完了，怎么判断这个形状能不能用？ | fit-a-high-resolution-model-to-data | should_not_trigger | evaluate-a-shape-reconstruction |
| 7 | SEC 那一千多帧怎么变成一条曲线，LC Analysis 里 buffer 自动选的能信吗？ | analyze-time-resolved-series | should_not_trigger | process-sec-saxs-series |
| 8 | 手上是一个样品的 20 张 tif，怎么平均成一条曲线并扣掉缓冲液？ | choose-a-molecular-weight-method | should_not_trigger | reduce-saxs-frames-to-curves |
| 9 | 我的 SEC-SAXS 数据能不能也做绝对刻度，顺便定个浓度/分子量？ | put-saxs-data-on-an-absolute-scale | should_not_trigger | process-sec-saxs-series |
| 10 | 线站刚下机，我手上有 20 张 tif，怎么把它们变成一条能用的曲线？ | reduce-saxs-frames-to-curves | should_trigger | = 本 skill |
| 11 | Guinier 拟合该取哪些点？Rg 值信不信得过要看什么？ | script-raw-with-the-python-api | should_not_trigger | assess-guinier-fit-quality |
| 12 | SEC 一千多帧的数据，怎么选哪一段是缓冲液、哪一段是样品，最后变成一条曲线？ | deconvolve-overlapping-elution-peaks | should_not_trigger | process-sec-saxs-series |
| 13 | 我做的时间分辨 SAXS，一批 series 要怎么一起逐点平均、扣掉 buffer，再接上时间轴？ | analyze-time-resolved-series | should_trigger | = 本 skill |
| 14 | 我的 P(r) 末端被压得直直地掉到零，是不是 Dmax 取小了？ | evaluate-a-shape-reconstruction | should_not_trigger | compute-and-validate-p-of-r |
| 15 | 我有 30 条曲线要都跑一遍 Guinier 并出一份报告，GUI 要点 30 次，有没有别的办法？ | script-raw-with-the-python-api | should_trigger | = 本 skill |
| 16 | Guinier 窗口里 n_min 显示 11，这是什么意思？我应该把它调成多少 | assess-guinier-fit-quality | should_trigger | = 本 skill |
| 17 | 我的 P(r) 末端被压得直直地掉到零，是不是 Dmax 取小了？ | compute-and-validate-p-of-r | should_trigger | = 本 skill |
| 18 | SEC-SAXS 跑完了一条曲线，分子量该用哪个方法算、该报哪个结果？ | choose-a-molecular-weight-method | should_trigger | = 本 skill |
| 19 | 怎么把这批 tif 积分、平均、扣完缓冲液导出成 .dat？ | assess-guinier-fit-quality | should_not_trigger | reduce-saxs-frames-to-curves |
| 20 | SEC-SAXS 的主峰有很明显的肩，我怀疑峰里不止一个物种。怎么判断到底有几个组分？ | deconvolve-overlapping-elution-peaks | should_trigger | = 本 skill |
| 21 | 我的 SAXS 曲线现在还是任意刻度，怎么把它放到绝对刻度上？ | put-saxs-data-on-an-absolute-scale | should_trigger | = 本 skill |
| 22 | 在 BL19U2 做了一轮 SEC-SAXS，一千多帧，怎么弄成一条能用的曲线？ | process-sec-saxs-series | should_trigger | = 本 skill |
| 23 | 我算的理论曲线和实验曲线在低 q 差很多，是模型错了吗？ | fit-a-high-resolution-model-to-data | should_trigger | = 本 skill |
| 24 | SEC 的一千多帧怎么变成一条曲线？buffer 区怎么定？ | correct-sec-saxs-baseline | should_not_trigger | process-sec-saxs-series |
| 25 | SEC 数据扣完缓冲液之后，峰后面的基线回不到零、整体还抬着，怎么办？ | correct-sec-saxs-baseline | should_trigger | = 本 skill |
| 26 | Guinier 窗口里 n_min 显示 11，怎么调才能读准 lysozyme 的 Rg？ | compute-and-validate-p-of-r | should_not_trigger | assess-guinier-fit-quality |

## 本轮结果

| 评测者 | 正面题正确 | 诱饵/边界题正确 | 总正确率 | 备注 |
|---|---|---|---|---|
| A（独立） | 待补 | 待补 | 待补 | 待补 |
| B（独立） | 待补 | 待补 | 待补 | 待补 |

## 残留问题与处置

待补（评测者返回后按前两册的口径记录：哪些题两人同错、是否回炉改可见头、是否判为真歧义并接受代价）。

## 与前两册的可比性

- 相同：57 字符截断 + 双评测者 + 逐条理由；不同：本轮是**首次跨 13 个 skill 的路由**（前几轮最多 5 个），同义竞争（如"把 tif 变成曲线"同时出现在 4 个 skill 的题面里）显著更强。
- 判分只会更严：诱饵题的目标是**另一个具体 skill**（不是 none），答对要求"不该用它 + 该用谁"两层都对。