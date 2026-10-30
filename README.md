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

## 当前证据（2026-10-30 更新）

主指标统一为**剔除服务异常后的成功率**，方法对比使用相同有效试验。原始记录和服务异常数量仍保留。

| 已完成的原 cube-v1 系统 | 共同有效成功数 | 成功率 |
|---|---:|---:|
| Astra + 等待/执行控制器 | 29/39 | 74.4% |
| 微调 VLM，无附加控制器 | 26/39 | 66.7% |
| 规则 VLM，无附加控制器 | 13/39 | 33.3% |

Astra 对微调 VLM 的差异尚未统计显著（配对精确 McNemar p=0.607）。完整的等待×执行消融在共同37次上为：固定减速20/37、只学习等待25/37、只学习执行26/37、完整27/37。完整对固定基线p=0.210，不能宣称所有模块都独立必要。

**新独立复验已完成并通过审计。** 三方法各40次，3次服务异常对称排除后，共同37次上 Astra 26/37（70.3%）、裸微调VLM 27/37（73.0%）、裸规则VLM 21/37（56.8%）。Astra对微调的配对p=1.0，对规则p=0.332。这轮不支持确定的上层模型优势，完整结果单独报告，不覆盖或挑选原主表。

**视觉干预已有240次VLM结果。** 原图／置换／遮字分别为：微调VLM 30/40、16/40、3/40，规则VLM 23/40、23/40、0/40。Astra对应条件仍待完成。配对恢复有19个有效状态，显式actor目标输入尚未显示收益。

证据及复算范围见 [新数据说明](data/cube_followup_20261030/README.md)。目标条件正式消融、同一Astra一次计划vs反馈、多物体、predictor改进与真机数据仍有缺口。**论文结构已齐，投稿证据尚未齐。**

新 student 的追加 DAgger 已完成。另一组新的 40 次底层测试中，原 student 39/40、冻结 latent 38/40、模拟噪声追加训练 39/40、CNN 反馈追加训练 40/40。这是单独的 160 次开发诊断，CNN 没有重新训练，**不改变本表的任何权重或结果，也不是 Astra 成功率**。见 [student 开发数据](data/student_adaptation_dev/README.md)。

## 构建与数据

```bash
# 需要 matplotlib，图表已提交，可跳过重生成
python3 scripts/render_evidence.py
python3 scripts/render_followup.py
# 使用 Tectonic 或 latexmk
make
# 也可以 TECTONIC=/absolute/path/to/tectonic make
bash scripts/check_paper.sh
```

原始图表由400条冻结记录生成，新表按独立后续队列分别复算，不跨版本合并或手工填写占位百分比。`main.tex` 与 `supplement.tex` 可分别设为 Overleaf 主文件。当前 PDF 使用官方 2027 匿名 review 模板并包含 LLM Usage Statement。投稿前需要完成 TODO、人工审核科学论断和参考文献，并确认匿名提交包。

此前 2026-09-18 的研究骨架保留在 Git 历史 `c3784c6`，本次不混用早期 RGB-D 后端数据。
