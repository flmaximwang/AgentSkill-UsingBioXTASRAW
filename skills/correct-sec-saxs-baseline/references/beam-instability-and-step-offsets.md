# 束流不稳定 → 基线抖动/漂移/台阶：三层判别（reference）

源：用户实际遇到的问题（"每 ~300 帧整体偏移一些"）+ BioXTAS RAW 官方教程（*Basic SEC-SAXS processing* / *Baseline correction*）
+ `RAWAPI.py` / `SASM.py` / `SECM.py` 源码核对（master 分支，函数见 `sec-saxs-baseline-api.md`）。

**为什么单列一层**：`SKILL.md` 正文与 GUI 的 Baseline Correction 只覆盖"平滑漂移"。
束流不稳定引起的东西其实是**三种不同性质**，混在一起处理会把真实信号当噪声扣掉。

---

## 一、三层的症状、机制、正解

| 层 | 症状（在强度-帧号图上） | 机制 | 正解 | RAW 里的落点 |
|---|---|---|---|---|
| **① 强度起伏（乘性）** | 曲线**整体高低起伏**，q 形状不变；在 log-log 上是平行上下移 | 束流强度/注入效率变化 → 整条 I(q) 被乘一个因子 | **逐帧按通量归一化**（入射/透射通量、pin-diode 监视器） | RAW 的 API **没有**归一化函数；最接近的是 `superimpose(profiles, ref_profile, scale=True, offset=False)`。GUI 里 Series 右键 **Adjust scale, offset, q range** 只给"整个系列一个系数"，**不是逐帧** |
| **② 平滑漂移（加性为主）** | 峰前后基线不等；强度-帧号有单调趋势 | 束流位置/能量缓漂；样品池窗口被污染（随剂量累积） | RAW 的 **Linear**（仪器/束流型）/ **Integral**（污垢型） | LC Analysis → Baseline Correction；脚本见 `scripts/baseline_correction.py` |
| **③ 分块台阶（每 N 帧整体偏移）** | 每隔固定帧数出现一次**台阶**（分段常数），峰前后各段水平不同 | 存储环 **top-up 补注**（≈5 min 周期）、采集分块、重复上样等离散事件 | **按块估水平后逐块校正**（本项目 `scripts/block_step_correction.py`），或改回 ① 的通量归一化 | RAW 的两套都不适用：Linear 是一条直线（会把台阶摊成斜坡）、Integral 只允许基线单调不降；多个缓冲液区会被**平均成一条全局缓冲液**，没有"块内缓冲液" |

**判型优先级**：先做 ①，再做 ③/②。顺序错了等于在缩放的坐标系里找漂移。

## 二、怎么判断是 ①还是③（判据，不用猜）

1. **看监视器**：把该次的入射/透射通量（BL19U2 采集界面显示的 incident flux / pin-diode transmitted flux）画成帧号曲线。
   **台阶出现在同样的帧号上 → 是 ①**，应做逐帧归一化（这也是 19U2 那句"如果需要强度校正，则由于统计规则**最后一帧不能用**"所指向的操作——末帧计数不完整，当不了参考）。
2. **同一个台阶在 q 方向上的形状**：
   - 高 q 与低 q 的台阶**绝对高度相同** → 加性（常数平移）→ 用 `--mode offset`；
   - 台阶高度**与强度成正比**（高 q 几乎看不出、低 q 很明显）→ 乘性 → 用 `--mode scale`。
3. **周期数量级**：1 s/帧 × 300 帧 ≈ 5 min，与存储环 top-up 补注周期同量级；采集分块通常是 2 的幂或探测器缓冲区大小。先把这条对上，再看数据。

## 三、脚本：`scripts/block_step_correction.py`

```bash
# 1) 先诊断（不改文件）：看每块水平与校正量
python scripts/block_step_correction.py series.hdf5 --block 300 --q-ref 0.20 --buffer 0 250 --dry-run

# 2) 乘性（束流强度型）/ 加性（常数平移型）
python scripts/block_step_correction.py series.hdf5 --block 300 --q-ref 0.20 --buffer 0 250 --mode scale
python scripts/block_step_correction.py series.hdf5 --block 300 --q-ref 0.20 --mode offset
```

做法与参数要点：

- **估水平的帧会自动排除洗脱峰**（总积分强度 `> median + K×MAD`，`--peak-mad` 默认 3.0），
  再用 `--q-ref` 处的中位数作该块水平。**不要把缓冲液区限制在峰前然后就指望它覆盖所有块**——
  单侧缓冲液通常只落在第一块里，那样估不出后面的台阶（这是本脚本第一版的设计缺陷，被自测抓到）。
- `--buffer` 只用于**校正后重算扣减**（`set_buffer_range` 会重算 sub 曲线）；`--est-frames` 可显式指定"只有背景"的帧区间。
- 校正写进 raw 强度：乘性用 `SASM.scaleRelative`，加性用 `SASM.offsetRawIntensity`（均已在源码里核对语义）。
- 之后若**块级水平本身仍在平滑漂移** → 再上 RAW 的 `Linear`；若台阶与通量曲线同位置 → 回到 ①。

## 四、本脚本的自测（无 RAW 环境下的桩测试，实跑数字）

合成 900 帧、每 300 帧一个乘性台阶（×1.00 / ×1.15 / ×0.90），帧 380–460 为洗脱峰（只抬高低 q，参考 q=0.20 干净）：

```
[peak] 总强度 median=1.562 MAD=0.1562 阈值=2.0306 → 排除 81 帧，保留 819 帧用于估水平
  block  frames          level          correction
      1  [    0,  299]          0.05  scale ×1.000000   (n=300)  (基准)
      2  [  300,  599]        0.0575  scale ×0.869565   (n=219)
      3  [  600,  899]         0.045  scale ×1.111111   (n=300)
校正前  块水平: [0.05, 0.0575, 0.045]
校正后  块水平: [0.05, 0.05, 0.05]
峰/背景比：帧420 q=0.05 = 3.0 | 帧100 q=0.05 = 1.0
```

- 排峰正好排除 81 帧（= 真实峰帧数），块水平恰好复原 ×1.15 与 ×0.90 的台阶；
- 校正后三块回到同一水平，且**峰/背景比 3.0 未被吃掉**——证明它扣的是台阶而不是样品信号。

> **未在真实数据上跑过**：本机未安装 RAW、也没有 SEC-SAXS 数据。上面是桩测试（替换 `bioxtasraw` 的接口）
> 验证算法与流程；接口语义（`scaleRelative` / `offsetRawIntensity` / `getIofQ` / `getAllSASMs` / `getIntI`）
> 已逐条核对 `SASM.py` / `SECM.py` 源码。首次用于真实数据时先用 `--dry-run` 看诊断表。
