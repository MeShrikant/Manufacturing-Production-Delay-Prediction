# User guide (Streamlit demo)
One page. Left = input, right = output.
1. Pick an example scenario (Good / Average / Bad shift) - it fills the numbers - or type your own: planned quantity, shift duration, planned cycle time, actual cycle time, machine downtime, changeover time.
2. Click **Predict**.
3. Output: delay risk (Low / Medium / High), predicted production quantity vs plan, target achievement %, possible bottleneck, recommended action.

Other model inputs (line type, equipment age, headcount etc.) use fixed typical values in this demo. The full set of fields is available through the API (`API_DOCUMENTATION.md`) and batch CSV prediction through `POST /upload-csv`.
The UI is intentionally a single-page demo. Batch CSV prediction is available through the API (`POST /upload-csv`).
