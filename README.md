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

## 当前结果

| 完整系统 | 全部 40 次成功数 | 公共 eligible 集合 |
|---|---:|---:|
| Astra + 等待/执行控制器 | 29/40（72.5%） | 29/39（74.4%） |
| 微调 VLM，无附加控制器 | 27/40（67.5%） | 26/39（66.7%） |
| 规则 VLM，无附加控制器 | 14/40（35.0%） | 13/39（33.3%） |

Astra 对微调 VLM 的当前差异没有达到统计显著（配对精确 McNemar p=0.607）。共享相同控制器的辅助对照也保留，微调 VLM 是 30/40，不能据此宣布 Astra 全面领先。

新 student 的追加 DAgger 已完成。另一组新的 40 次底层测试中，原 student 39/40、冻结 latent 38/40、模拟噪声追加训练 39/40、CNN 反馈追加训练 40/40。这是单独的 160 次开发诊断，CNN 没有重新训练，**不改变本表的任何权重或结果，也不是 Astra 成功率**。见 [student 开发数据](data/student_adaptation_dev/README.md)。

## 构建与数据

```bash
# 需要 matplotlib，图表已提交，可跳过重生成
python3 scripts/render_evidence.py
# 使用 Tectonic 或 latexmk
make
# 也可以 TECTONIC=/absolute/path/to/tectonic make
bash scripts/check_paper.sh
```

图表由 400 条独立试验记录生成并校验，不手工填写占位百分比。`main.tex` 与 `supplement.tex` 可分别设为 Overleaf 主文件。当前 PDF 使用官方 2027 匿名 review 模板并包含 LLM Usage Statement。投稿前需要完成 TODO、人工审核科学论断和参考文献，并确认匿名提交包。

此前 2026-09-18 的研究骨架保留在 Git 历史 `c3784c6`，本次不混用早期 RGB-D 后端数据。
