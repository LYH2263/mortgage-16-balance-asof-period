import json
import pytest
from app import db
from app import seed
from app.engines.amortization import balance_asof
from app.services.mortgage_service import MortgageService


def test_first_period():
    r = balance_asof(1_000_000, 3.5, 360, 1)
    assert r["period"] == 1
    assert r["interest"] == 2916.67
    assert r["principal"] == 1573.78
    assert r["balance"] == 998426.22
    assert r["principal_paid"] == 1573.78


def test_last_period_balance_zero():
    r = balance_asof(1_000_000, 3.5, 360, 360)
    assert r["balance"] == 0.0
    assert r["principal_paid"] == 1_000_000.0


def test_mid_period_paid_sum():
    r = balance_asof(120000, 0, 12, 6)
    assert r["balance"] == 60000.0
    assert r["principal"] == 10000.0
    assert r["interest"] == 0.0
    assert r["principal_paid"] == 60000.0


@pytest.mark.parametrize("p", [0, -1, 361])
def test_period_out_of_range(p):
    with pytest.raises(ValueError):
        balance_asof(1_000_000, 3.5, 360, p)


@pytest.fixture
def tmp_db(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "test.db")
    seed.init_db()
    yield


def test_out_of_range_does_not_persist(tmp_db):
    with MortgageService() as s:
        with pytest.raises(ValueError):
            s.balance_asof(1_000_000, 3.5, 360, 361, None, True)
        rows = s._c.execute("SELECT COUNT(*) c FROM calc_runs WHERE kind='balance_asof'").fetchone()["c"]
        assert rows == 0


def test_default_does_not_persist(tmp_db):
    with MortgageService() as s:
        out = s.balance_asof(1_000_000, 3.5, 360, 120, None, False)
        assert out["run_id"] is None
        rows = s._c.execute("SELECT COUNT(*) c FROM calc_runs WHERE kind='balance_asof'").fetchone()["c"]
        assert rows == 0


def test_persist_pins_period_and_balance(tmp_db):
    with MortgageService() as s:
        out = s.balance_asof(1_000_000, 3.5, 360, 120, 1, True)
        rid = out["run_id"]
        assert rid is not None
        rec = s._c.execute("SELECT * FROM calc_runs WHERE id=?", (rid,)).fetchone()
        payload = json.loads(rec["input_json"])
        result = json.loads(rec["result_json"])
        assert rec["kind"] == "balance_asof"
        assert payload["target_period"] == 120
        assert result["period"] == 120
        assert result["balance"] == out["balance"]
        # 事后改年利率再查，历史记录原样不动
        out2 = s.balance_asof(1_000_000, 4.8, 360, 120, 1, True)
        rec_again = s._c.execute("SELECT * FROM calc_runs WHERE id=?", (rid,)).fetchone()
        assert json.loads(rec_again["result_json"])["balance"] == result["balance"]
        assert out2["balance"] != out["balance"]
