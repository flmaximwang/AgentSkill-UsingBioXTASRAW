# 源文本快照 —《BioXTAS RAW程序使用说明》

- 来源：微信公众号「生物小角」· 作者 刘广峰
- URL：https://mp.weixin.qq.com/s/Ul201MtOPO5DpVkpIomwZg
- 发布时间：1714111329（2024-04-26）
- 体裁：BioXTAS RAW 官方文档的翻译 + BL19U2 线站本地化增补（作者自述「本文档是对上述教程的翻译，针对配置文件及其他操作使用了部分 BL19U2 的数据」）
- 抓取方式：curl（Chrome UA）→ 剥离 js_content 容器 → 文本 + 图片占位符；正文 5877 字，界面截图 13 张
- 用途：本书（本文章）蒸馏的审计轨迹。正文引用均 ≤150 字/条，见 `NOTICE.md`。

---

BioXTAS RAW 是一款免费的开源程序，主要用于分析溶液小角 X 射线散射(SAXS)数据。RAW 基于 Python 语言编写，具有友好的图形界面，现被用作上海光源 BL19U2 线站主要的分析软件。

该软件专为生物 SAXS 数据而设计，具备以下特性：

能够从 2D 探测器图像（包括 Pilatus、Eiger 等探测器产生的 tif、cbf 等 20 多种类型的图像）创建和绘制 1D 散射曲线图；

标准数据操作，例如平均、扣减、合并等；

可以进行吉尼尔拟合分析回转半径 (Rg) 和 I_0 ；

通过与标准样品的 I0 比较、绝对校准、相关体积 (Vc)、校正的 Porod 体积 (Vp)、ATSAS 程序包中的 Shape&Size 和 Bayesian 方法分析分子量（MW）；

……

1、RAW 的安装

RAW可从SourceForge下载，有适用于Windows、MacOs和Debian/Ubuntu的预构建安装程序，在其他Linux 发行版上安装需要从源代码构建。

在 Windows 上安装RAW有两种方法。最简单的方法是使用预构建的安装程序（.msi 文件），强烈推荐使用此方法安装，程序的稳定性及运行速度比源码安装都要好。如果要安装没有预构建安装程序的版本，则需要从源代码编译安装，可参考说明文件。

Sourceforge地址：https://sourceforge.net/projects/bioxtasraw。

2、RAW 程序界面

RAW 的主屏幕显示三个不同的面板：信息面板（左上）、控制面板（左下）和绘图面板（右）。 可以显示的其他窗口是选项窗口和各种分析窗口。 此外，RAW 顶部有一个菜单栏。

[[IMG: https://mmbiz.qpic.cn/mmbiz_png/q6n1Jc4oAKQeDbjib2ShyvdsOPQrReZY8pkdVzGRnqA6yoCF43T8dZyf4T3yfBjP2iaPhwvSsweoIxTAJfn3PVOw/640?wx_fmt=png&from=appmsg]]

 停靠在RAW主窗口中的三个面板中的任何一个都可以相对于其他面板移动。单击面板的标题栏，然后将面板拖动到所需位置（按住应该会看到一个蓝色矩形，指示面板的放置位置）。

RAW 左侧（信息和控制）和右侧（绘图）可用的总区域部分由分隔条控制，可以单击并拖动此栏来更改此比例。可以通过单击并拖动角落或边缘来调整RAW主窗口的大小。

绘图面板包含四个选项卡：主绘图（Profiles）、IFT绘图（IFTs）、图像绘图（Image）和SEC绘图（Series）。Profiles选项卡用于查看单个散射曲线。IFTs选项卡用于查看逆傅立叶变换，Image选项卡用于查看探测器图像，Series选项卡用于查看SEC-SAXS 数据。可以通过单击和拖动来更改选项卡的顺序。每个绘图选项卡底部都有一个导航/控制栏。大多数导航栏都有一些独特的按钮，但它们都共享以下按钮：

[[IMG: https://mmbiz.qpic.cn/mmbiz_png/q6n1Jc4oAKQeDbjib2ShyvdsOPQrReZY8drMibh8jj6GyL61Xk2vcskE6dguuVWtL9PTqiakD889BEfKy1EsJqxWw/640?wx_fmt=png&from=appmsg]]

RAW 的顶部菜单栏包含文件（Files）、选项（Opitons）、视图（View）、工具（Tools）和帮助（Help）菜单。“视图”和“工具”菜单只是访问其他地方的选项的另一种方式，而“文件”、“选项”和“帮助”菜单具有其他方式无法访问的项目。

文件（Files）菜单有五个选项：

[[IMG: https://mmbiz.qpic.cn/mmbiz_png/q6n1Jc4oAKQeDbjib2ShyvdsOPQrReZY8Msy0dTCPWY69yffibD11P9Nou1vib1QjBoy2j0z5N27KB3BMzd5equZw/640?wx_fmt=png&from=appmsg]]

Loading Settings，这将从.cfg文件加载 RAW 设置。这也可以通过双击"控制面板"的"文件"选项卡中的.cfg文件来完成。

Save Settings，这会将所有 RAW 设置（包括图像校准和图像蒙版）保存到.cfg文件中，以便以后可以再次加载。

3、RAW 程序配置文件

配置文件允许RAW将2D图像积分为1D散射曲线。为了实现该功能，首先需要对散射图像进行定心和校准，即确定光斑中心即样品到探测器的距离，然后需要对探测器的坏点及Beamstop进行遮盖（Masking），让这些点不参与数据积分过程。针对特殊实验样品，还可以设置水或玻璃碳作为绝对标度，或一个分子量已知的标样作为分子量标准。

BL19U2使用山嵛酸银（Silver Behenate，二十二酸银盐）作为SAXS标样，该样品具有5.8 nm的周期结构，第一个峰的q值为1.076 nm-1。线站使用的探测器为Pilatus 2M，该探测器具有1679*1475像素，单个像素尺寸为172*172微米。

注意：任何时候要处理图像，都需要加载适当的配置！

 在BL19U2进行实验之前，线站工作人员会将当前实验参数设定好，导入RAW程序。如果在自己的计算机上使用RAW程序，只需点击File-Load Setting，找到实验当天对应的cfg文件导入，即可完成程序的配置工作。

如有其他设置问题，请联系线站工作人员。

4、数据预处理

①、在文件选项卡中，单击文件夹按钮并导航到目标文件夹。单击打开按钮以在 RAW 文件浏览器中显示该文件夹。

提示：也可以在文件列表中导航。使用向上箭头（文件名：“..”）向上移动目录级别或双击目录将其打开。

[[IMG: https://mmbiz.qpic.cn/mmbiz_png/q6n1Jc4oAKQeDbjib2ShyvdsOPQrReZY8U9mxWBOZzhCBGqoKqGSrufsLunFp3gv05Eea0Z76BxFdz1QtMzvMUQ/640?wx_fmt=png&from=appmsg]]

②、在控制面板的文件选项卡底部，使用下拉菜单将文件类型过滤器设置为“TIF 文件 (*.tif)”。

[[IMG: https://mmbiz.qpic.cn/mmbiz_png/q6n1Jc4oAKQeDbjib2ShyvdsOPQrReZY8o26dU19ffcYRSPurjLziaJkukOkQ67DYNBXriaszVOSibmKxHOKiaYo9ibg/640?wx_fmt=png&from=appmsg]]

③、在BL19U2线站，通常会从给定样本中收集约 20 张图像。要加载牛血清蛋白 (BSA) 样本的 20 个图像，首先选择文件 bsa10_0002_000xx.tif，其中 xx 的范围为 01 到 20。这些文件是从 10 mg/ml BSA 散射测量的。

提示：可以按住 ctrl 键同时单击以分别选择多个文件。也可以单击一个文件，然后按住 shift 单击另一个文件以选择这些文件以及它们之间的所有内容。

[[IMG: https://mmbiz.qpic.cn/mmbiz_png/q6n1Jc4oAKQeDbjib2ShyvdsOPQrReZY8bZffHczfvU9PL0KAFI9REeVmc0egScVFa8ZXcYCYPZfhYCmO6dyU2w/640?wx_fmt=png&from=appmsg]]

④、单击绘图按钮以对所有图像进行积分并在 Profiles 图中绘制积分散射曲线图。

注意：通常，一旦图像被积分，我们只使用散射曲线文件。但是，如果想重新处理数据，保留图像很有用。

⑤、单击Profiles文件控制选项卡。可以在此处查看哪些散射配置文件加载到 RAW 中，并对其进行操作/分析。

[[IMG: https://mmbiz.qpic.cn/mmbiz_png/q6n1Jc4oAKQeDbjib2ShyvdsOPQrReZY8B86bWBHbP7y2417Co9xr1nqMtibKoWqFbHgygnVRpQmmnDibtjbAmXkw/640?wx_fmt=png&from=appmsg]]

⑥、单击文件名以选择散射配置文件。 背景应变为蓝色，表明它已被选中。

⑦、使用“平均（Average）”按钮将收集到的所有散射曲线平均到一条曲线中。平均散射曲线应出现在Profiles列表的底部。文件名将以绿色显示，并以 A_ 开头，表示它是平均散射曲线。

⑧、为了清楚地看到平均散射曲线，需要从图中隐藏各个曲线。单击文件名左侧的眼睛将显示/隐藏散射曲线文件。当眼睛被显示时，轮廓显示在绘图上，当眼睛有一条线穿过它时，轮廓被隐藏。隐藏除两条平均曲线之外的所有轮廓。

[[IMG: https://mmbiz.qpic.cn/mmbiz_png/q6n1Jc4oAKQeDbjib2ShyvdsOPQrReZY8O01CbdltdX6oh9X9gyEN6glFicPliblTOluBlRdvqf6EM9YdteB6wZkg/640?wx_fmt=png&from=appmsg]]

⑨、接下来，需要从测量的蛋白质散射（实际上是蛋白质的散射加上缓冲液的散射）中减去缓冲液散射曲线。给平均的缓冲液文件标星，并选择平均的蛋白质散射文件，然后单击“Subtract”按钮。

[[IMG: https://mmbiz.qpic.cn/mmbiz_png/q6n1Jc4oAKQeDbjib2ShyvdsOPQrReZY8Mb85Sfun3fjIk7FIOnIlP8ZXosqm3MO7iaLTYnHyxvh8VIsGGX8ovRQ/640?wx_fmt=png&from=appmsg]]

扣减过的散射曲线应显示在下方的图中。新散射文件应显示在散射文件列表中，名称为红色，并带有 S_ 前缀，表示它是一个扣减过的曲线文件。

[[IMG: https://mmbiz.qpic.cn/mmbiz_png/q6n1Jc4oAKQeDbjib2ShyvdsOPQrReZY8JVaC7CTIm6UAopeLyCvL7Fgibj4ibURVHib4zeUcVYzoUC1wC8pUEnRew/640?wx_fmt=png&from=appmsg]]

⑩、选择所有散射曲线文件，然后单击“保存”按钮将它们保存在目标文件夹中。 请注意，在 Profiles 列表中的文件名中，前面的 * 消失了，这表明这些散射曲线没有未保存的更改。现在可以删除它们。

注意：这会将它们保存为 .dat 扩展名。这是 SAXS 散射曲线的标准格式。

[[IMG: https://mmbiz.qpic.cn/mmbiz_png/q6n1Jc4oAKQeDbjib2ShyvdsOPQrReZY8dLPGQYY2srkF9ZsGsiaqa9Zc75ZG3HaDM37CDMCEETfZAjU5O3t9hpw/640?wx_fmt=png&from=appmsg]]

5、吉尼尔分析

本节将简单介绍如何使用 RAW 进行吉尼尔分析。这不是关于进行吉尼尔分析的基本原则和最佳实践的教程。

①、在 RAW 中，在 Profiles 列表中的扣减过的lyz2散射文件上单击鼠标右键并选择“Guinier fit”。 Guinier 拟合窗口将打开。

注意：也可以单击“Profiles”控制面板底部的“Guinier”按钮。

[[IMG: https://mmbiz.qpic.cn/mmbiz_png/q6n1Jc4oAKQeDbjib2ShyvdsOPQrReZY8lQv6lbajeTGxlXC1BNaPzty5QyLibCh8LwT3EjL9PHO4lQSNgEWicsyA/640?wx_fmt=png&from=appmsg]]

②、在 Guinier 窗口中，顶部图显示了 Guinier 图和拟合，而底部图显示了拟合的残差。

注意：第一次打开 Guinier 窗口时，RAW 会自动尝试找到最佳的 Guinier 区域。

注意：Rg 值的单位为 1/q（例如，如果 q 的单位为 Å-1，则Rg 的单位为 Å）。

[[IMG: https://mmbiz.qpic.cn/mmbiz_png/q6n1Jc4oAKQeDbjib2ShyvdsOPQrReZY87LZelGdUSLOfgAdibT3ccYJSrpQ2L2TiahSvbQl1UKWicTsJXXswgdKdQ/640?wx_fmt=png&from=appmsg]]

③、在“控制”面板中，可以看到 n_min 为 11。这意味着 RAW 跳过了 Guinier 拟合的前几个低 q 点。可以看到最低的 q 值略有下降，这可能是它被跳过的原因。使用 n_min 框旁边的箭头按钮将其向下调整几个点并检查 Rg 是否发生变化。完成后，将 n_min 返回到 8。

④、在“参数”面板中，请注意 q_max*Rg 为 ~1.27。回想一下，对于像 lyz 这样的球状蛋白质，q_max*Rg 通常约为 1.3。稍微调整 n_max，观察 Rg和残差的变化。

6、总结

RAW的功能还有很多，这里只是给出了基本操作。对于高级处理，如使用 GNOM 和 BIFT 方法进行对距离分布分析、形状重建的模糊性评估、使用串珠模型和电子密度的 3D 重建、将 3D 重建与 PDB 文件对齐等。可以参考 RAW 程序的在线文档，链接如下：

https://bioxtas-raw.readthedocs.io/en/latest/index.html

程序安装后，在 docs文件夹下也有当前版本的使用说明及教程。 

本文档是对上述教程的翻译，针对配置文件及其他操作使用了部分BL19U2 的数据，以更贴合实际使用场景。

由于水平限制，难免会有疏漏之处，还请大家批评指正。