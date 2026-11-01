# Figures

`method.pdf`: vector system schematic, not a measured trajectory.

`cube_results.pdf`: generated from frozen eligible outcomes and raw drop contexts.

`observations.pdf`: uncropped real model-input frames from formal Astra trial 183101000, requests 1–3. They are Gaussian-rendered object observations with live black hand occlusion. They are not real-robot images.

Regenerate with `python3 scripts/render_evidence.py`. Source images remain in `assets/`.

`native_comparison.pdf` and `.png`: latest 40-per-method native cube comparison (35/40, 30/40, 17/40). Copied from the independently verified experiment figure. Source file hashes are in `data/cube_completed_20261101/provenance.json`. This is separate from the historical `cube_results.pdf`.

`feedback_example.pdf` and `.png`: unchanged native request images from trial 185501000 in the matched Q2/Q3 cohort, with recorded public decisions and control-step timing. Rebuild with `python3 scripts/render_feedback_example.py` in an environment with matplotlib and Pillow. Source frames, sanitized trace, selection rule, and hashes are in `data/feedback_example_20261101/`. The selected sequence illustrates inspection followed by binding, not correction of a previously wrong binding.

`waiting_feedback.pdf` and `.png`: final 200-trial matched waiting/feedback study. Rebuild with `python3 scripts/render_ablation_v3_figure.py`. Bars and Wilson intervals come only from `data/cube_waiting_feedback_20261101/summary.json`. Q2 has 40 eligible trials, Q3 has 39, and its full arm is shared rather than a new set of trials.
