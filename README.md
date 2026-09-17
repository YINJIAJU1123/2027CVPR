# CVPR 2027: Language-Guided Active In-Hand Search

研究问题：在无需人类任务操作示范的条件下，如何学会根据语言搜索指定表面或标记，并将其转出、稳定展示？进一步检验交互学习能否改善有限示范覆盖不到的探索与恢复行为。

**状态：研究设计与论文骨架，2026-09-18。方法尚未定稿，新任务尚无实验结果。** 本仓库用于论文、实验协议和证据记录；训练代码位于独立的 [agent-inhand-manipulation](https://github.com/YINJIAJU1123/agent-inhand-manipulation) 仓库。

## 入口

- [中文研究计划](docs/research_plan_zh.md)：研究问题、候选方法、第一阶段实验和待讨论决策。
- [任务与 baseline 协议](docs/task_and_baselines_zh.md)：语义信息公平性、成功定义、数据与计算预算。
- [现有资产与证据边界](docs/current_assets_zh.md)：已有控制器、视觉原型，以及尚缺少的部分。
- [文献与会议要求](docs/sources.md)：已核对来源、可支持的表述、后续调研入口。
- [论文结构](docs/paper_outline_zh.md)：各节需要回答的问题、证据与图表。
- [模板来源](TEMPLATE.md)：官方 author kit 的固定版本及 2027 待核对项。

英文主文件为 `main.tex`，分节位于 `sections/`。当前 PDF 使用明确标注的计划性表述，不包含占位实验数字。

## 编译

需要 Tectonic（本次验证为 0.17.0），或安装了常用 TeX 包的 `latexmk` / pdfLaTeX。

```bash
make check
```

如 Tectonic 不在 PATH 中：

```bash
TECTONIC=/absolute/path/to/tectonic make check
```

首次使用 Tectonic 可能需要联网获取 TeX 包。输出为 `output/pdf/research_scaffold.pdf`；`make check` 检查编译日志与引用。版式修改后还需渲染检查：

```bash
mkdir -p tmp/pdfs
pdftoppm -r 120 -png output/pdf/research_scaffold.pdf tmp/pdfs/page
```

在 Overleaf 中上传源文件并将 `main.tex` 设为主文件即可。PDF、编译缓存和模型权重不提交到 Git。

## 当前边界

主对比必须接收相同语言目标和可部署观测，不要求全部采用预训练 VLA。先验证扫描识别、普通历史 PPO 和候选方法，再加入一个认真调试的模仿学习对照及同架构交互实验。UniDex 和 VLM 分层方案列为后续适配候选。

已有状态控制结果不属于本任务结果。本文暂不声称 RL 普遍优于 IL、首次实现语言手内操作，或已验证实机迁移。此次仓库初始化不启动新的训练任务。
