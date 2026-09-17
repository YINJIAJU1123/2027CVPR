# 现有资产与证据边界

整理日期：2026-09-18。工程证据来自 2026-09-16 的检查与已有会话记录；本文件不是当前 GPU 作业监控结果。此次只建立论文项目，没有新启动训练。

## 已有部分

训练代码仓库：[agent-inhand-manipulation](https://github.com/YINJIAJU1123/agent-inhand-manipulation)。以下均为该代码工程内的相对位置，不复制训练数据或权重到论文仓库。

| 资产 | 已知状态 | 不能据此声称什么 |
|---|---|---|
| Revo3 状态 PPO teacher | 152 维 privileged state + 6 维目标面，158 维输入；21 维动作 | 不是从图像语言寻找隐藏目标 |
| 六面状态任务评估 | 576 episodes，详细计数见下 | 不是新展示指标，不是多训练种子对照 |
| A100 续训 | 500 次额外 PPO iteration、512 env、seed 123，保存 `model_998.pt` | 新 checkpoint 尚未评估，不能宣称改善 |
| `visual_semantic_reorient.py` | RGB-D 相机、六色表面 patch、隐藏 debug goal marker | 固定颜色布局不是组合语义泛化 |
| `brainco_hand_visual_semantic_reorient_env_cfg.py` | 256×256 RGB-D；固定颜色与面对应；canonical yaw 为 0 | 新任务需要随机布局和非唯一目标姿态 |
| `algo/agentic/visual_student.py` | 冻结特征融合、GRU、21 维动作、evidence/stop heads | GRU 不自动等于表面证据记忆；存在 head 不等于训练过 |
| `scripts/vision/train_feature_student.py` | 当前优化动作 MSE | 不是视觉 PPO，也未训练 evidence/stop heads |
| `algo/agentic/consequence_predictor.py` | 候选动作块后果预测器代码与接口 | 不代表已经训练、消融或证实有效 |

相机本地 smoke test 已通过；A100 视觉渲染链路尚未验证。旧 5090 驱动/渲染问题属于部署事项，不能推断 A100 视觉训练已打通。

## 状态任务 pilot：只作为控制基础

原始 checkpoint：`shaping_model_499.pt`。

- SHA256：`28c9206c44f890f8f363eebac9c5ce458de9b86771d148567e8523a81e728bfe`。
- 相关运行代码 revision：`238df55f36b3e4e86ad6b3399ef0b3efd1e1b3dc`。
- 评估：6 个目标面 × 3 个 evaluation seeds × 32 episodes = 576。
- 旧协议：姿态误差 < 0.16 rad；连续保持 0.5 秒；随机 yaw。

| 旧协议指标 | 原始计数 | 比例 |
|---|---|---|
| 瞬时到达 | 530 / 576 | 92.01% |
| 曾连续保持 | 472 / 576 | 81.94% |
| 终态保持且不掉落 | 359 / 576 | 62.33% |
| 掉落 | 7 / 576 | 1.22% |

来源定位：该运行的 `reports/summary_576.json`。本论文仓库没有收录原始报告，写入正式论文前需从原始 artifact 重新核验。3 个评估种子不是 3 个独立训练种子。

续训结束记录为 2026-09-16 19:11；最终 checkpoint 为 `training/shaping_continue/2026-09-16_18-33-32_a100_continue/model_998.pt`，没有新的对应评估。本表只描述原始 checkpoint 的成绩。

## 视觉模仿原型

已记录 3,528 transitions，训练 2,676、验证 852；SigLIP2 图像和文本特征各 768 维；动作验证 MSE 0.24346。需复查轨迹级划分是否充分隔离后，再作正式泛化分析。

`outputs/eval_feature_student_balanced_96_mini.json` 只包含 1 个 episode、30 步超时，无成功、无掉落。它说明评估链路曾做过小规模尝试，不能说明 IL 在此任务上失败，更不能支持 RL 优于 IL。

## 新任务还缺什么

1. 随机标记布局、指令生成、无泄漏的数据切分和隐藏目标初始状态。
2. 清晰可见 + 稳定 dwell 的评价器，以及渲染样例验证。
3. 真正接入相机与语言历史的视觉 PPO 训练闭环。
4. 一个完整、可审计的扫描识别保持 baseline。
5. 候选证据记忆的实现及同预算消融。
6. 完整示范生成、认真调试的 IL 对照和受控恢复评估。

因此，目前最准确的表述是：已有手内控制基础、视觉环境和学生网络原型；语言引导的隐藏目标搜索与稳定展示尚未完成。
