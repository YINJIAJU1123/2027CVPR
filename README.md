# AgenticRotation — CVPR 2027 working paper

**Learning Local Control for Asynchronous Visual Agents in Semantic In-Hand Reorientation**

2026-10-29：完整英文论文初稿及补充材料。当前只有正方体的完整测评数据。未完成的多物体、改进 predictor 和真机实验均明确标记 **TODO**，没有伪造实测数字。

## 阅读

- [论文 PDF](output/pdf/agenticrotation-2027.pdf)
- [补充材料 PDF](output/pdf/agenticrotation-2027-supplement.pdf)
- [四个实验问题与待补证据](docs/experiment_plan_zh.md)
- [新物体交接](docs/new_object_handoff_zh.md)
- [冻结的 cube-v1 证据](data/cube_v1/README.md)
- [官方 CVPR 2027 模板来源](TEMPLATE.md)

## 当前证据（2026-11-01 更新）

| 最新方块完整系统 | 成功 | 成功率 | 掉落 |
|---|---:|---:|---:|
| Astra + 新等待控制器 + 原执行控制器 | 35/40 | 87.5% | 3 |
| 裸微调 VLM | 30/40 | 75.0% | 9 |
| 裸规则 VLM | 17/40 | 42.5% | 12 |

本批没有服务异常剔除。Astra 对微调的配对 p=.267，尚未确立稳定显著优势。这是完整系统比较，不是孤立的上层模型能力对比。历史主实验与复验保留在正文及补充材料，不跨版本合并或选优。

- **等待控制器独立对照**：27/39→33/39，掉落10→5，p=.109。成功定义和执行控制器不变。
- **同一Astra一次计划 vs 完整反馈**：7/39→30/39。调用预算不同，说明完整反馈协议价值。
- **视觉语义干预**：换映射后Astra32/40→32/40，微调30/40→16/40，规则23/40→23/40。使用重建面图像，不能混同原生RGB主实验。
- **目标条件**：正确25/36、无显式24/36、打乱30/36，未支持正确显式目标收益。
- **执行门控开发**：学习26/40低于原执行29/40，候选淘汰、未部署。这是固定计划回放，没有新Astra调用。

[最新证据与边界](data/cube_completed_20261101/README.md)包含760次live试验与独立160次开发汇总。视觉试验与旧归档部分重叠，不重复计数。论文保留多物体、同事predictor改进与真机的TODO，没有伪造数值。

新student的160次追加DAgger开发诊断仍单独保留。它没有训练CNN，也不是Astra成功率，没有替换本次主实验student。

## 构建与数据

```bash
# 需要 matplotlib，图表已提交，可跳过重生成
python3 scripts/render_evidence.py
python3 scripts/render_followup.py
python3 scripts/render_completed.py
# 使用 Tectonic 或 latexmk
make
# 也可以 TECTONIC=/absolute/path/to/tectonic make
bash scripts/check_paper.sh
```

原始图表由400条冻结记录生成，新表按独立后续队列分别复算，不跨版本合并或手工填写占位百分比。`main.tex` 与 `supplement.tex` 可分别设为 Overleaf 主文件。当前 PDF 使用官方 2027 匿名 review 模板并包含 LLM Usage Statement。投稿前需要完成 TODO、人工审核科学论断和参考文献，并确认匿名提交包。

此前 2026-09-18 的研究骨架保留在 Git 历史 `c3784c6`，本次不混用早期 RGB-D 后端数据。
