# Independent pose estimation under hand occlusion

This is an offline perception study on a 58.5 mm marked cube, not an agent task-success cohort. The report and integrity summary were delivered by a separate experiment task. Integration re-sums 12 shard counts: 2,306/6,144 RGB and 3,977/6,144 RGB-D predictions meet strict translation <10 mm AND rotation <10 degrees. Invalid predictions remain failures. There are 6,144 unique observations, not 30,720 independent frames; the latter counts all five inference conditions.

`summary.json` contains report-derived numbers. `integrity_summary.json` is the supplied verification report. `provenance.json` records original file hashes and our narrower aggregate check. The supplied report documents pose-error recomputation and 129 unchanged frozen files. These checks and the cluster bootstrap were not rerun during paper integration: per-frame results, source and raw images remain in the external archive, which was unreachable at integration time. Restoring a sanitized per-frame archive remains a reproducibility task, not a missing accuracy result.

The 95% intervals use 10,000 paired environment-cluster bootstrap draws stratified by seed, with all views and temporal samples kept together. They are not IID-frame intervals. Training histories and camera adaptation differ. RGB-D uses virtual co-located depth and ideal target segmentation. Occlusion covaries with viewing angle. No-hand RGB controls have a different mask boundary. Deep occlusion still fails. These data do not establish an isolated fusion-architecture effect, downstream agent improvement, or physical-camera accuracy.

The RGB checkpoint here differs from the frozen CNN in the agent's cube evaluation. None of these pose percentages can be substituted for autonomous manipulation success. The 5 mm/5 degree, ADD and noise metrics are secondary report-derived measurements. The pose metric uses strict thresholds and full semantic orientation without cube-symmetry minimization.

Generate tables with `python3 scripts/render_pose_occlusion.py` from the repository root. No model call or training is required.
