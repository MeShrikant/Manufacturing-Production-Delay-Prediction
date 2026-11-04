# Project overview
Predicts production delay risk (Low / Medium / High), expected production quantity and target achievement % for a manufacturing line shift, with a rule-based "possible bottleneck" and a recommended action. Includes a FastAPI backend and a Streamlit demo.

Three different things are kept apart:
1. **Historical analysis** - what already happened (computed from past records).
2. **Current-shift risk estimate** - the `shift` model; uses downtime, cycle time, headcount and changeover for the shift.
3. **Pre-shift planning risk** - the `plan` model; uses only information known before the shift.

Not implemented: future multi-day production forecasting (the dataset has no continuous time series per line), and a "current production quantity" input (the dataset has no in-shift partial counts).
