from datetime import datetime
from pathlib import Path
import shutil

from app.config import DB_PATH


def create_backup():
    src = Path(DB_PATH)
    if not src.exists():
        raise FileNotFoundError("No se encontró la base de datos")
    backups_dir = src.parent / "backups"
    backups_dir.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    dst = backups_dir / f"sgv_backup_{ts}.db"
    shutil.copy2(src, dst)
    return str(dst)
