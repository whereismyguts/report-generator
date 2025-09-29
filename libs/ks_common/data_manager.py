from pathlib import Path
import json
from typing import Any, Optional
import pandas as pd


class DataManager:
    def __init__(self, data_dir: str = 'data'):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

    def save_json(self, data: Any, filename: str) -> str:
        path = self.data_dir / filename
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return str(path)

    def load_json(self, filename: str) -> Optional[Any]:
        path = self.data_dir / filename
        if not path.exists():
            return None
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_csv(self, data: Any, filename: str) -> str:
        path = self.data_dir / filename
        df = pd.DataFrame(data)
        df.to_csv(path, index=False, encoding='utf-8')
        return str(path)
