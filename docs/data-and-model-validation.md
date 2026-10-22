# Data and model validation plan

## Required inputs

- Product family, SKU/variant, inspection station, camera position, lens, resolution, lighting, and takt time.
- Defect taxonomy with examples, severity, acceptable tolerances, and disposition rules.
- Representative good and defective samples across shifts, suppliers, finishes, and production batches.
- Approved data retention and image-access policy.

## Dataset controls

- Split train/validation/test by physical unit or production batch to prevent near-duplicate leakage.
- Track class counts and missing/ambiguous labels.
- Include hard negatives: reflections, dust, packaging marks, harmless seams, and normal product variation.
- Keep a locked acceptance set that is not used for tuning.

## Evaluation

Report per-defect precision, recall, false-accept rate, false-reject rate, confusion matrix, and confidence intervals where sample sizes allow. Measure end-to-end latency and sustained throughput on target hardware, including decode and preprocessing time.

A generic confidence threshold is not an acceptance criterion. Thresholds must be selected against agreed quality-risk targets. Unknown or out-of-distribution inputs should route to REVIEW or an explicit error policy, never silently pass.

## Model approval gates

1. Define intended use and defect classes.
2. Confirm dataset rights and model/runtime licensing.
3. Train or select candidates.
4. Evaluate on locked, representative data.
5. Review failure examples with quality engineers.
6. Version model weights and preprocessing/rules together.
7. Approve a controlled rollout and rollback plan.
