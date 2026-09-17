# Source ledger

Checked on 2026-09-18. Bibliographic metadata below were checked against the linked primary pages. These are starting references, not a completed systematic review. Abstract-level relevance checks do not establish full implementation equivalence.

| BibTeX key | Verified source | Use and boundary |
|---|---|---|
| `bao2023dexart` | [CVF, CVPR 2023](https://openaccess.thecvf.com/content/CVPR2023/html/Bao_DexArt_Benchmarking_Generalizable_Dexterous_Manipulation_With_Articulated_Objects_CVPR_2023_paper.html) | Articulated-object dexterous benchmark and generalization; different task from in-hand semantic search. |
| `zhang2026unidex` | [CVF, CVPR 2026](https://openaccess.thecvf.com/content/CVPR2026/html/Zhang_UniDex_A_Robot_Foundation_Suite_for_Universal_Dexterous_Hand_Control_CVPR_2026_paper.html) | Human-video-derived universal dexterous control; relevant pretrained adaptation candidate, not an already reproduced baseline. |
| `bhardwaj2026viserdex` | [arXiv:2604.11138](https://arxiv.org/abs/2604.11138) | Monocular RGB pose estimation, 3DGS, RL and teacher-student in-hand reorientation; not a hidden language-target search benchmark. Cited using verified arXiv metadata. |
| `chi2023diffusion` | [arXiv:2303.04137](https://arxiv.org/abs/2303.04137) | Action diffusion and visual conditioning; the proposed language-conditioned version is our adaptation. Cited using the arXiv entry, not an inferred venue/year. |
| `li2026actsenseact` | [arXiv:2602.04600](https://arxiv.org/abs/2602.04600), v2 dated 2026-07-10 | CoMe-VLA: cognitive/memory active perception from egocentric data. Precludes a generic novelty claim about adding language and memory to active perception. |

Implementation entry points from earlier project discussion; verify exact revisions, license, checkpoints, observation requirements, and hand compatibility before running:

- UniDex: https://github.com/unidex-ai/UniDex and https://huggingface.co/UniDex-ai/UniDex
- ViserDex: https://github.com/leggedrobotics/ViserDex
- Diffusion Policy: https://github.com/real-stanford/diffusion_policy
- CoMe-VLA: https://github.com/Joringell/ASA

## Literature still to inspect in depth

These links are research leads retained from the discussion; they are not additional fully audited bibliography entries in this scaffold.

- [Scaffolding Dexterous Manipulation with Vision-Language Models, NeurIPS 2025](https://proceedings.neurips.cc/paper_files/paper/2025/hash/862644b156e51c35dea5a7446d640b14-Abstract-Conference.html): grounding/planning with low-level RL.
- [VERA: Turning Video Models into Generalist Robot Policies](https://arxiv.org/abs/2605.27817): inspect the actual in-hand deployment availability before estimating adaptation work.
- [SaPaVe](https://arxiv.org/abs/2603.12193): active perception through camera/manipulation actions; check distinction from a fixed-camera hand changing object visibility.
- [HORA](https://arxiv.org/abs/2210.04887): in-hand rotation control and adaptation background.

## CVPR 2027 requirements checked

Primary source: https://cvpr.thecvf.com/Conferences/2027/CallForPapers

- Scope includes embodied vision/robotics, reasoning and reinforcement learning, agentic AI, and physical AI.
- Registration: 2026-11-10 AoE.
- Paper submission: 2026-11-16 AoE.
- Supplementary material: 2026-11-23 AoE.
- The CFP says work appearing online after 2026-09-15 is generally contemporaneous. Authors must still cite and discuss it, and compare empirically to the degree feasible. Work influencing the submission must be credited. The policy does not distinguish arXiv from conference/journal papers for this rule.
- The LLM usage policy is still being finalized on the checked page. Recheck before submission and retain an accurate record of assistance.
- The linked [2027 Author Guidelines](https://cvpr.thecvf.com/Conferences/2027/AuthorGuidelines) page returned page-not-found during this check. Therefore the exact 2027 page limit and final formatting rules are not certified by this scaffold.

No real-robot mandate was identified in the checked CFP. This observation is not a guarantee about final author policies or acceptance; simulation-only claims must stay within their evidence.
