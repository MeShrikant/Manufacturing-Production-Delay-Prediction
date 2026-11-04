import sys, subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import config as C  # noqa: E402
import pytest  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def trained_project():
    """Make sure processed data and models exist (runs preprocessing/training once if they do not)."""
    if not C.CLEAN_FILE.exists() or not C.SAMPLE_FILE.exists():
        subprocess.run([sys.executable, str(ROOT / "03_Data_Preprocessing" / "preprocess.py")], check=True)
    if not (C.MODELS_DIR / "production_delay_model.pkl").exists():
        subprocess.run([sys.executable, str(ROOT / "04_Training" / "train_model.py")], check=True)
    if not (C.RESULTS_DIR / "model_metrics.json").exists():
        subprocess.run([sys.executable, str(ROOT / "04_Training" / "evaluate_model.py")], check=True)
