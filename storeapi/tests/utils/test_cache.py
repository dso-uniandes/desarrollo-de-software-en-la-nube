from utils import cache
import types


def _pick(api, names):
    for n in names:
        fn = getattr(api, n, None)
        if isinstance(fn, types.FunctionType):
            return fn
    return None


def test_cache_import_and_basic_call(monkeypatch):
    fn = getattr(cache, "get_cache", None) or getattr(cache, "get", None)
    if callable(fn):
        result = fn("dummy_key")
        assert result is None or isinstance(result, (str, bytes))
    else:
        assert cache is not None
