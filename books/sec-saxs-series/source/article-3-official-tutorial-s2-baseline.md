# 源文本快照 — 官方教程《Advanced Series processing – Baseline correction》

- 来源：BioXTAS RAW 官方文档（v2.4.1/latest）
- URL：https://bioxtas-raw.readthedocs.io/en/latest/tutorial/s2_baseline.html
- 抓取：curl + HTML 剥离；RAW 采用 GPLv3，文档随程序分发（本地 `docs/` 亦有一份）
- 用途：本包的**第二源**（权威原文）。微信文章是该教程的翻译+线站增补；
  两源冲突时以官方教程为准，并在 skill 的 R 段分别标注。

---

Advanced Series processing – Baseline correction — BioXTAS RAW 2.4.2 documentation

 BioXTAS RAW

Installation

Getting Help

RAW Tutorial

Introduction

Basic processing

Advanced processing

Pair-distance distribution analysis – GNOM in RAW

Pair-distance distribution analysis – DIFT (DENSS IFT) in RAW

Pair-distance distribution analysis – BIFT in RAW

Assessing ambiguity of 3D shape information - AMBIMETER in RAW

3D reconstruction with bead models – DAMMIF/N and DAMAVER in RAW

3D reconstruction with electron density – DENSS in RAW

Aligning reconstructions with high resolution shapes

Theoretical profiles and fitting from models – CRYSOL in RAW

Theoretical profiles and fitting from models – PDB2SAS (DENSS) in RAW

Advanced Series processing – Singular value decomposition (SVD)

Advanced Series processing – Evolving factor analysis (EFA)

Advanced Series processing – Regularized Alternating Least Squares (REGALS)

Advanced Series processing – Baseline correction

Linear Baseline Correction

Integral Baseline Correction

Multi-series analysis

Saving plots and data, opening data externally

Creating a configuration file

SAXS Tutorial

Videos

Cite

RAW API

Manual

Changes

 BioXTAS RAW

RAW Tutorial

Advanced processing

Advanced Series processing – Baseline correction

 View page source

Advanced Series processing – Baseline correction

Sometimes SEC data shows a baseline drift. This can be due either to instrumental
changes (such as beam drift), or changes in the measured system, such as capillary
fouling. RAW provides the ability to correct for these forms of baseline drift
using either a linear or integral baseline method. The linear baseline method
is best for instrumental drifts, while the integral baseline method is best
for capillary fouling. Both baseline methods apply a distinct correction for each
q value.

If you use integral baseline correction in RAW, in addition to citing the RAW
paper, please cite this paper: E. Brookes, P. Vachette, M. Rocco, and J. Pérez.
Journal of Applied Crystallography (2016). 49, 1827-1841.
DOI: 10.1107/S1600576716011201

A video version of this tutorial is available:

The written version of the tutorial follows.

Linear Baseline Correction

Clear all of the data in RAW. Load the xylanase.hdf5 SEC data in the
series_data folder.

When it loads in, you will see there is a distinct constant upward slope in the
integrated intensity. This usually happens due to instrumental drift,
and can often be mostly corrected for.

[IMG]

Open the LC Series analysis panel. Set a buffer range (‘Auto’ is fine).
You’ll still see the slope in the subtracted integrated intensity plot.

Note: To baseline correct data, you should only have buffer regions
selected before the peak.

Use the triangle to expand the Baseline Correction section.

Note: On windows it will look like a button with ‘>>’ after the
name.

[IMG]

Set baseline correction to ‘Linear’. You should see the start and end
controls become active, and two blue regions representing your selected
start and end regions appear on the ‘Subtracted’ plot.

Note: This should automatically show the ‘Subtracted’ plot tab. If
it doesn’t, select the ‘Subtracted’ plot tab.

[IMG]

If you look closely, it looks like the baseline may level off a little bit
at the start of the series curve. So we will select a start range closer
to the peak. Click the ‘Pick’ button for the baseline correction start region
and select a start region about halfway to the peak. Roughly 30-50 frames
is a good length for the start and end regions.

[IMG]

Expand the end range to be 50 frames long.

[IMG]

Click ‘Set baseline and calculate’. You may see a warning, click ‘Continue’.

Note: The warning simply informs you that the slope of the linear correction
is not the same in the start and end region at all q values. This is usually
the case, and mostly can be ignored.

[IMG]

The ‘Baseline Corrected’ plot should automatically show after you set the
baseline region and calculate. If not, change to that plot tab. You can
see that the upward drift is essentially gone.

[IMG]

Switch back to the subtracted plot. You’ll see the calculated baseline
shown in orange.

[IMG]

Switch back to displaying the Baseline Corrected plot.

Remove any existing sample region and find a new sample region using the ‘Auto’
button. Send that region to the Profiles plot.

You can remove the baseline correction by changing the ‘Baseline correction’
selection from ‘Linear’ to ‘None’. Do this, then send the sample region to the
Profiles plot again.

Change the ‘Baseline correction’ selection back to ‘Linear’. Click ‘Set Baseline
and calculate’ to redo the linear correction. Click ‘OK’ to exit the LC Series
Analysis window. Now if you save series or reopen the window you will see
your baseline correction.

Switch to the profiles plot. Put the subtracted plot on a Log-Log scale.
You can see a difference in the profiles due to the baseline correction at
low q.

[IMG]

Integral Baseline Correction

Integral baseline correction proceeds very similarly to linear baseline correction.
Here we provide detail only where the procedures are different.

Clear all of the data in RAW. Load the baseline.hdf5 SEC data in the
series_data folder.

Note: This is the same as what you previously saved in
an earlier part of the tutorial.

Open the LC Series analysis panel. Verify that your buffer regions
are before the peak of interest.

Set baseline correction to ‘Integral’.

Zoom in near the base of the subtracted peak. Pick a start region in the
flat baseline area just before the start of the peaks.

Pick an end region in the flat region just after the end of the peaks.

Note: You should end up with regions ~460-480 and 860-880

Try: You can use the ‘Auto’ button to automatically find start and end
regions. For this dataset, it ends up a little close to the peaks, so
some manual adjustment is necessary.

[IMG]

Click the ‘Set baseline and calculate’ button.

Note: The start and end points should be set in regions with no change
in the baseline. If they aren’t, RAW will give a warning. Try changing the
end region to ~800-820 to see such a warning.

Zoom in on the base of the peak in the baseline corrected dataset. You should
see that the baseline is actually a little overcorrected. This is because
the integral baseline correction only allows for positive or no change in the
baseline, so if some q values need a negative correction the total baseline
ends up overcorrected, as the positive values are brought down but the negative
values are not brought up.

Note: You can change the intensity display to individual q values or
a q range and look at different points in q to try figure out which q
values are causing the issue.

[IMG]

Switch back to the subtracted plot and zoom in on the base of the peak.
You’ll see the calculated baseline shown in orange.

[IMG]

Change the intensity display to ‘Intensity in q range’ and try several
different q ranges. This will allow you to see what q values are getting
the baseline overcompensated.

Try: Recommended regions to try for this dataset are 0.01-0.02, 0.05-0.06,
0.1-0.2, 0.2-0.27.

Note: You should find that it is the high q ranges that are being
overcorrected. This may imply that the profiles are mostly noise in
that range. If you examine the profiles and determine that is the case,
you could truncate the profiles to lower q before doing the baseline
correction.

Switch back to displaying the total intensity and the Baseline Corrected plot.

Remove any existing sample region and find a new sample region using the “Auto”
button. Send that sample region to the main plot.

 Previous
 Next 

© Copyright 2017-2023, Jesse B. Hopkins.

 Built with Sphinx using a
 theme
 provided by Read the Docs.