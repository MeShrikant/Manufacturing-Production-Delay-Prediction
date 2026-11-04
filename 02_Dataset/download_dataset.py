"""Download the dataset from Hugging Face into 02_Dataset/raw/.
Run:  pip install huggingface_hub   then   python 02_Dataset/download_dataset.py
The CSV is already included in raw/, so you normally do not need this script.
Manual alternative: open https://huggingface.co/datasets/xpertsystems/mfg005-sample -> Files -> download
`mfg005_synthetic_line_performance.csv` and save it into 02_Dataset/raw/."""
import shutil, sys
from pathlib import Path

RAW = Path(__file__).resolve().parent / "raw"
TARGET = RAW / "mfg005_synthetic_line_performance.csv"
try:
    from huggingface_hub import snapshot_download
except ImportError:
    sys.exit("Install huggingface_hub first: pip install huggingface_hub  (or download the CSV manually, see docstring)")
folder = Path(snapshot_download(repo_id="xpertsystems/mfg005-sample", repo_type="dataset"))
cands = [p for p in folder.rglob("*.csv") if "line_performance" in p.name]
if not cands:
    sys.exit(f"No *line_performance*.csv found in {folder}. Download manually.")
RAW.mkdir(parents=True, exist_ok=True)
shutil.copy(cands[0], TARGET)
print("Saved", TARGET)
