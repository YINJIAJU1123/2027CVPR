# AIMI — CVPR 2027 working paper

**AIMI: Agentic In-Hand Manipulation for Language-Guided Visual Exploration**

2026-11-09 AIMI 命名统一版（包含 2026-11-08 真机结果与图表修订）：按 Q3 主动目标搜索 → Q2 推理期间控制 → Q1 跨物体系统表现组织正文，Q3 为第一张结果表。Teacher–student 明确为参考 ViserDex、适配 Revo3 的运动基础；补充状态重建辅助监督的说明。Q2 三个评估 seed 的 480 个汇总结果逐项闭合，数据未改变。附录按证据主题重排；历史开发版本保存在 `archive/editorial_20261107/`。英文改为正文与补充材料两个独立编译入口；摘要不再提及 ViserDex，方法中的来源说明保留。Q4 恢复独立 RGB/RGB-D 位姿评测摘要。2026-11-08 补入 cube、die、ball、duck 四物体真机汇总：每物体每方法 20 次，共 240 次；Rule / Fine-tuned / AIMI 为 32/80、53/80、70/80。正文 Q1 使用柱状图；2026-11-09 真机结果按作者要求恢复为表格。Q1 的完整数值表保留在补充材料。实拍图和相机/评分设置仍待补入。可见性与持续保持需要单独报告。

## 阅读

- [正文 PDF（含参考文献）](output/pdf/main.pdf)
- [补充材料 PDF](output/pdf/supplyment.pdf)
- [本次范围与命名更正](docs/seed_scope_and_labels_20261107.txt)
- [23 条引用核对记录](docs/reference_verification_20261107.txt)
- [官方模板来源](TEMPLATE.md)

## AIMI 全文修订

- 名称展开：Agentic In-hand Manipulation for Inspection。正式标题为 AIMI: Agentic In-Hand Manipulation for Language-Guided Visual Exploration。
- 视觉探索由语言目标驱动，服务于找到目标、确认绑定和最终展示；任务指标和原始实验结果不变。
- 摘要、引言、相关工作、任务定义、方法、实验分析、讨论、结论及补充材料均已修订。摘要仅在首次介绍方法时出现 AIMI。
- 图内旧名称已更新；控制器输入明确为 goal-bank vector，速度调节明确只用于 waiting。PPT 的嵌入式仿真图片保持不变。
- 英文正文与补充材料是本次权威版本。旧中文对照仍属于此前修订，尚未同步本轮全文。
- [修订及验证说明](docs/aimi_revision_20261109.txt)。

## 当前呈现调整

- Related Work 顺序为 Agentic reasoning → Visual / goal-conditioned dexterity → RL for dexterous manipulation → Asynchronous policies。
- 摘要参考 SimToolReal（arXiv:2602.16863）与 GoalDex（arXiv:2611.02171v1）的“任务难点—方法—实验”组织方式，保持 AIMI 自身的方法与证据范围。
- Q2 正文改为四类结局的堆叠条形图，完整计数保留在补充材料；图由冻结汇总数据直接生成。
- Q4 分为感知适配和完整方法真机评测：保留 RGB/RGB-D 位姿小表，真机采用成功次数与成功率表格。RGB-D 的仿真感知评测与 RGB pose 真机任务结果分别报告。
- `scripts/render_result_presentation.py` 生成 Q2 的 PDF/SVG/PNG 和 Q4 小表；重绘需 Matplotlib，直接编译 TeX 可使用已生成的文件。

## 当前实验口径

| 问题 | 范围 | 当前结果与边界 |
|---|---|---|
| Q1 系统比较 | 六物体、原映射与换映射；另有三物体双语研究 | 映射比较 1,440 次；语言研究 2,160 次；均为物体专属系统 |
| Q2 等待控制器消融 | 仅正方体 | 187102、187103、187104，每 seed 每方法 40 次；每方法合计 120 次 |
| Q3 视觉反馈与巡检 | 仅正方体 | 一次计划 vs 持续反馈；新图像 vs 重复首帧；自主 vs 固定巡检；三个独立队列分别报告 |
| Q4 感知与真机 | 独立 cube 位姿评测；真机按物体报告 | RGB/RGB-D 位姿达标率 37.53%/64.73%，6,144 帧；四物体真机 Rule/Fine-tuned/AIMI 为 40.0%/66.25%/87.5%，各 80 次；图片待补 |

Q2 四组成功数为 73、88、82、104 / 120，依次对应持续执行、固定减速、学习减速、学习减速＋修正。等待掉落为 24、13、7、5；执行掉落为 14、8、14、4；其他失败为 9、11、17、7。[汇总及来源说明](data/controller_three_seed_20261107/README.md)。

Q3 的持续反馈组复用 Q2 中 187102 的 40 次，不能重复当作独立样本。一次计划与反馈为 6/39 vs 33/39（原始 6/40 vs 34/40）。图像干预是另外 40 对，使用 187201/187202，每 seed 每臂 20 次；成功为 32/40 vs 9/40。新增离线终态分类：正确绑定 34 vs 9、错误绑定 1 vs 3、未绑定 5 vs 28。终态分类本身不测量首次绑定、初始可见性或稳定展示。另一次离线轨迹审计发现：两组在相同 9 个任务的第一次调用就正确绑定；新图像组后续新增 25 次正确绑定，其中 23 次最终成功，重复首帧组后续无新增正确绑定。这是已执行的语义声明，不是首次视觉识别准确率。

新增 Q3 巡检策略研究使用独立 seeds 187301/187302，每 seed 每组 20 次，共 80 次正式实验，无服务排除。自主组 38/40 成功、39 次终态正确绑定；固定组 31/40 成功、32 次终态正确绑定。9 对仅自主成功、2 对仅固定成功，双侧精确 McNemar p=0.0654297。固定组只替换巡检方向和时长，其余决策仍由同一语义模型完成；两组均重新运行。不能与旧 Q3 成功率作跨队列因果比较，也不能称为“显著优于”。[汇总、协议与核验](data/q3_inspection_20261107/README.md)。初始可见性仅完成初步标注，未作为论文结果发布。

旧归档的种子标签及 trial IDs 保持原样，不伪造新逐次编号。旧 controller confirmation 不再作为现行 Q2 呈现。历史笔记单独保存在 [归档说明](docs/README_history_before_scope_cleanup_20261107.md)，其中过时口径不能替代本页及当前论文。

## 构建与核对

```bash
# 使用系统 latexmk 或 Tectonic
bash scripts/build_paper.sh
bash scripts/check_paper.sh
python3 scripts/analyze_q3_terminal_bindings.py --check
python3 scripts/render_q3_inspection.py --check
```

当前检出的仓库未包含 `data/language_objects_20261106/trials.json` 和 `results.json`，因此本轮不声称重新计算了语言实验的逐试验配对统计。现有表格数字与修订前逐项一致。仅重排现有语言表可运行 `python3 scripts/render_language_table_image.py`；取得原始导出后，再运行 `python3 scripts/render_language_objects.py --verify-paper .` 和图像生成脚本。构建时会检查表格图像来源哈希，并重算 Q1 汇总、Q2 三 seed 表及 Q3 巡检表和配对统计；同时从固定计数重新生成 Q1 选定样式图、真机汇总及表格。旧归档图表脚本仅用于其对应历史数据，不作为当前结果口径的入口。

两个英文编译入口：`main.tex`（正文和参考文献）与 `supplyment.tex`（补充材料及其参考文献，文件名按本项目约定保留此拼写）。在 Overleaf 中分别选作 Main document 即可独立编译。`sections/`、`tables/`、`preamble.tex` 和 `supplement_setup.tex` 是共用内容或设置文件，无需单独编译。

也可以在仓库根目录分别运行：

```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=build/main main.tex
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=build/supplyment supplyment.tex
```

`build_paper.sh` 会编译两部分并将 PDF 放入 `output/pdf/`。补充材料的图、表、公式以 S 编号，两份 PDF 各自从第 1 页开始。使用 CVPR 2027 匿名 review 模板；正文内容 8 页，引用与 LLM Usage Statement 另页。真机与复现信息 TODO 仍保留。

位姿结果支持仿真感知精度的改善；它使用真实相机标定和 Gaussian-splat 外观资产，但不等于真实相机精度或下游任务成功率的改善。若要主张后两者，需要对应评测。完整协议见补充材料的独立位姿估计章节。

## 可编辑插图

`figures/AIMI_paper_figures.pptx` 保留六页原布局、字体、渐变和图片，仅更新名称与方法标签。`scripts/export_aimi_figures.py` 用 LibreOffice 和 PyMuPDF 导出论文所用矢量图。正常编译使用已导出的 PDF，不要求安装 LibreOffice。

## 2026-11-08 真机数据来源

`data/hardware_author_report_20261108/results.json` 保存作者转交的同事汇总计数与确认的 RGB pose 流程。成功标准：到达目标后停止、停止时姿态误差不超过 15°、没有掉落。数据为汇总计数，未构造逐次记录、seed、配对信息、失败分类或显著性检验。角度评分工具和误差定义尚待确认；详见修订记录。

## 2026-11-09 Q1 样式备选与 Q4 表格

Q1 已确定采用 A（蓝灰＋珊瑚红）。`python3 scripts/render_q1_variants.py --all` 生成六种配色／图形备选；`--select A` 至 `--select F` 可保存选定样式，常规构建会保留该选择。若改用点图或热力图，需同时调整 Q1 图注的 Bars/Labels 表述。所有备选使用同一份冻结计数。Q4 真机结果恢复为表格，仅显示已提供的成功计数和成功率；掉落次数及失败分类待作者提供，不推算。
