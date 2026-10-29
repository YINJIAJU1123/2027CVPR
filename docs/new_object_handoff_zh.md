# 新物体 student 交接清单

不要只传一个权重文件。每个物体建立独立 object_id 和 release_id，保留其原始运行条件。

- Student checkpoint、架构/配置、归一化统计、关节顺序和 action scale/映射/平滑。
- 匹配的 pose predictor checkpoint、关键点定义、姿态坐标系和 quaternion 约定。
- USD/mesh、Gaussian 表示、纹理、碰撞形状、质量/惯量/摩擦和环境配置。
- 相机内外参、分辨率、裁剪/深度约定。
- 每个语义目标对应的表面、技能或规范姿态，物体对称性处理方式。
- 原 student 的评测脚本和指标、已知成功率及原始记录。
- 如果需要蒸馏/DAgger，提供匹配的 teacher checkpoint 与输入输出说明。
- 所有文件 SHA256、代码 commit、许可证/来源。

先复现原 student 的 40 次物理诊断，再适配 latent 输入，再冻结新的语义实验 release。不能直接把原 cube 的 goal mapping、controller 权重或成功率迁移为新物体的结果。
