import pytest
import pandas as pd
from cobtools.query.cache import GaiaUsefulInfoCache


def make_row(source_id: int) -> pd.DataFrame:
    return pd.DataFrame([{
        "source_id": source_id,
        "ra": 10.0,
        "dec": 20.0,
    }])


@pytest.fixture
def cache(tmp_path, monkeypatch):
    monkeypatch.setattr(
        GaiaUsefulInfoCache,
        "cache_dir",
        property(lambda self: tmp_path / "gaia_useful_info"),
    )
    return GaiaUsefulInfoCache(dr="dr3", max_rows=5)


class TestGaiaUsefulInfoCache:

    def test_load_returns_none_when_no_cache_file(self, cache):
        assert cache.load() is None

    def test_save_creates_file(self, cache):
        cache.save(make_row(1))
        assert cache.cache_file_path.exists()

    def test_save_and_load_roundtrip(self, cache):
        cache.save(make_row(1))
        df = cache.load()
        assert df is not None
        assert 1 in df.index
        assert df.loc[1, "ra"] == 10.0
        assert df.loc[1, "dec"] == 20.0

    def test_load_uses_source_id_as_index(self, cache):
        cache.save(make_row(42))
        df = cache.load()
        assert df.index.name == "source_id"
        assert 42 in df.index

    def test_save_multiple_sources(self, cache):
        for sid in [1, 2, 3]:
            cache.save(make_row(sid))
        df = cache.load()
        assert set(df.index.tolist()) == {1, 2, 3}

    def test_save_skips_duplicate_source_id(self, cache):
        cache.save(make_row(1))
        cache.save(make_row(1))
        df = cache.load()
        assert len(df) == 1

    def test_eviction_removes_oldest_row(self, cache):
        for sid in [1, 2, 3, 4, 5]:
            cache.save(make_row(sid))
        # max_rows=5, adding a 6th should evict source_id=1
        cache.save(make_row(6))
        df = cache.load()
        assert len(df) == 5
        assert 1 not in df.index
        assert 6 in df.index

    def test_eviction_preserves_newest_rows(self, cache):
        for sid in [1, 2, 3, 4, 5]:
            cache.save(make_row(sid))
        cache.save(make_row(6))
        df = cache.load()
        assert set(df.index.tolist()) == {2, 3, 4, 5, 6}

    def test_cache_dir_is_created_on_save(self, cache):
        assert not cache.cache_dir.exists()
        cache.save(make_row(1))
        assert cache.cache_dir.exists()

    def test_cache_file_path_includes_data_release(self, cache):
        assert "dr3" in cache.cache_file_path.name

    def test_get_source_returns_none_for_empty_cache(self, cache):
        assert cache.load() is None
        assert cache.get_source(1) is None

    def test_get_source_returns_none_for_missing_source_id(self, cache):
        cache.save(make_row(1))
        assert 1 in cache.load().index
        assert cache.get_source(2) is None

    def test_get_source_returns_dataframe_for_existing_source_id(self, cache):
        cache.save(make_row(114514))
        assert cache.load() is not None
        assert 114514 in cache.load().index
        result = cache.get_source(114514)
        assert result is not None
        assert isinstance(result, pd.DataFrame)
        assert result.index.name == "source_id"
        assert 114514 in result.index
        assert result.loc[114514, "ra"] == 10.0
        assert result.loc[114514, "dec"] == 20.0
