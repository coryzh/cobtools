import platformdirs
import pandas as pd
from pathlib import Path
from abc import ABC, abstractmethod

_ROOT_CACHE_DIR: Path = Path(platformdirs.user_cache_dir("cobtools"))


class Cache(ABC):
    @property
    @abstractmethod
    def cache_dir(self) -> Path:
        pass

    @property
    @abstractmethod
    def cache_file_path(self) -> Path:
        pass

    @abstractmethod
    def load(self) -> ...:
        pass

    @abstractmethod
    def save(self, data: ...) -> None:
        pass

    @abstractmethod
    def get_source(self, source_id: int | str) -> pd.DataFrame | None:
        pass


class GaiaUsefulInfoCache(Cache):
    def __init__(self, dr: str, max_rows: int = 1000):
        if max_rows <= 1:
            raise ValueError("max_rows must be greater than 1")

        self.dr = dr
        self.max_rows = max_rows

    @property
    def cache_dir(self) -> Path:
        return (
            _ROOT_CACHE_DIR / "gaia_useful_info"
        )

    @property
    def cache_file_path(self) -> Path:
        return (
            self.cache_dir
            / f"gaia_single_source_useful_info_{self.dr}.csv"
        )

    def load(self) -> pd.DataFrame:
        if not self.cache_file_path.exists():
            return None
        return pd.read_csv(self.cache_file_path, index_col="source_id")

    def save(self, data: pd.DataFrame) -> None:
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        if data.empty:
            return

        data = data.set_index("source_id")

        if self.cache_file_path.exists():
            existing = pd.read_csv(self.cache_file_path, index_col="source_id")

            if data.index[0] in existing.index:
                return

            existing.iloc[-(self.max_rows - 1):].to_csv(self.cache_file_path)
            data.to_csv(self.cache_file_path, mode="a", header=False)
        else:
            data.to_csv(self.cache_file_path)

    def get_source(self, source_id):
        existing = self.load()
        if existing is None or source_id not in existing.index:
            return None

        return existing.loc[[source_id]]
