# 新物体 student 交接清单

不要只传一个权重文件。每个物体建立独立 object_id 和 release_id，保留其原始运行条件。

- Student checkpoint、架构/配置、归一化统计、关节顺序和 action scale/映射/平滑。
- 姿态输入来源、坐标系和 quaternion 约定。无 predictor 的仿真路线需提供模拟器姿态输入、噪声与延迟设置；使用 predictor 的路线再提供匹配权重和关键点定义。
- USD/mesh、Gaussian 表示、纹理、碰撞形状、质量/惯量/摩擦和环境配置。
- 相机内外参、分辨率、裁剪/深度约定。
- 每个语义目标对应的表面、技能或规范姿态，物体对称性处理方式。
- 原 student 的评测脚本和指标、已知成功率及原始记录。
- 如果需要蒸馏/DAgger，提供匹配的 teacher checkpoint 与输入输出说明。
- 所有文件 SHA256、代码 commit、许可证/来源。

先复现原 student 的 40 次物理诊断，再适配 latent 输入，再冻结新的语义实验 release。不能直接把原 cube 的 goal mapping、controller 权重或成功率迁移为新物体的结果。

## 当前接入边界（2026-11-02）

方块和骰子的正式实验已完成。新增约三个物体可优先采用同事提供的无 predictor 控制策略，先验证原策略，再适配连续 latent。无需为新的仿真主实验强行安装 predictor。

旧 HORA/PTLD 权重不是当前 latent student 的直接替换件。已有 duck、octagonal、qabsorb、strawberry teacher/资产的结构审计保存在代码仓库 `outputs/pose_latent_student_v1/multi_object_readiness_20261102/compatibility_audit.json`。这些资产需要环境与策略适配，不能直接作为新增物体的合格 student 或实验结果。

真机交付需同时包含逐回合目标、最终独立评分、掉落/错误停止、模型调用和时间戳、同步视频及具体权重版本。单独汇总成功率不足以支持服务异常剔除或等待阶段分析。
