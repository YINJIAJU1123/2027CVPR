# REVEAL — CVPR 2027 working paper

**REVEAL: Agentic In-Hand Manipulation for Language-Guided Target Presentation**

2026-11-07 更新：新增 Q3 固定巡检与自主巡检的 80 次配对实验，以及已有图像干预的绑定时序分析。成功率为 95.0% vs 77.5%，配对检验 p=0.0654，保留“观察到优势、尚未达到统计显著”的解释。此前三 seed 控制器结果、图像和命名保持一致。

## 阅读

- [论文 PDF](output/pdf/agenticrotation-2027.pdf)
- [补充材料 PDF](output/pdf/agenticrotation-2027-supplement.pdf)
- [本次范围与命名更正](docs/seed_scope_and_labels_20261107.txt)
- [23 条引用核对记录](docs/reference_verification_20261107.txt)
- [官方模板来源](TEMPLATE.md)

## 当前实验口径

| 问题 | 范围 | 当前结果与边界 |
|---|---|---|
| Q1 系统比较 | 六物体、原映射与换映射；另有三物体双语研究 | 映射比较 1,440 次；语言研究 2,160 次；均为物体专属系统 |
| Q2 等待控制器消融 | 仅正方体 | 187102、187103、187104，每 seed 每方法 40 次；每方法合计 120 次 |
| Q3 视觉反馈与巡检 | 仅正方体 | 一次计划 vs 持续反馈；新图像 vs 重复首帧；自主 vs 固定巡检；三个独立队列分别报告 |
| Q4 真机 | 按实际物体逐项报告 | 待补，已有独立仿真位姿研究不能替代真机结果 |

Q2 四组成功数为 73、88、82、104 / 120，依次对应持续执行、固定减速、学习减速、学习减速＋修正。等待掉落为 24、13、7、5；执行掉落为 14、8、14、4；其他失败为 9、11、17、7。[汇总及来源说明](data/controller_three_seed_20261107/README.md)。后两 seed 暂仅有合计数，不生成 seed 方差或配对显著性。

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

若重新生成语言表，先运行 `python3 scripts/render_language_objects.py --verify-paper .`，再运行 `python3 scripts/render_language_table_image.py`。构建时会检查表格图像来源哈希，并重算 Q1 汇总、Q2 三 seed 表及 Q3 巡检表和配对统计。旧归档图表脚本仅用于其对应历史数据，不作为当前结果口径的入口。

`main.tex` 与 `supplement.tex` 可分别设为 Overleaf 主文件。使用官方 CVPR 2027 匿名 review 模板；正文 8 页，引用与 LLM Usage Statement 另页。现存硬件与复现信息 TODO 保留，不代表相关工作已经完成。
