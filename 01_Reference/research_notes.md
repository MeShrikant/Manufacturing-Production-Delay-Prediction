# Research notes (design decisions, not literature review)
- OEE = availability x performance x quality. In this dataset achievement tracks `oee_overall` almost exactly (corr 0.99), so any OEE column is leakage.
- Synthetic data has clean, near-deterministic relations between downtime / cycle time and output. The high in-shift accuracy reflects that, not real-factory performance.
- Pre-shift attributes (age, condition, line type, planned load) carry little signal here; the plan model is only slightly better than guessing.
- Bottleneck wording is rule-based on the largest loss among downtime share, changeover share and cycle-time slowdown. Checked against the dataset's own `oee_loss_primary_driver` on the test split: the cycle-time rule matched performance_loss in 249 of 252 rows; the downtime rule matched availability_loss in 114 of 152 rows.
- No academic papers are cited. Add any you rely on here.
