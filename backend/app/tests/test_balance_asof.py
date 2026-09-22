import os, tempfile
os.environ.setdefault("DATA_DIR", tempfile.mkdtemp())
import json
import pytest
from app.engines.amortization import balance_asof, equal_payment_schedule

def test_first_period_matches_schedule():
    row = equal_payment_schedule(1_000_000, 3.5, 360)["rows"][0]
    b = balance_asof(1_000_000, 3.5, 360, 1)
    assert b["balance"] == row["balance"]
    assert b["principal"] == row["principal"]
    assert b["interest"] == row["interest"]

def test_last_period_balance_zero():
    b = balance_asof(1_000_000, 3.5, 360, 360)
    assert b["balance"] == 0
    assert b["principal_paid"] == 1_000_000

def test_principal_paid_plus_balance_is_principal():
    b = balance_asof(800000, 4.2, 360, 60)
    assert round(b["principal_paid"] + b["balance"], 2) == 800000

def test_zero_rate():
    b = balance_asof(120000, 0, 12, 5)
    assert b["balance"] == 70000.0
    assert b["principal_paid"] == 50000.0
    assert b["interest"] == 0.0

@pytest.mark.parametrize("p", [0, -1, 361])
def test_period_out_of_range(p):
    with pytest.raises(ValueError):
        balance_asof(1_000_000, 3.5, 360, p)

from app import seed
from app.db import connect
from app.services.mortgage_service import MortgageService

def _run_count():
    c = connect()
    n = c.execute("SELECT COUNT(*) x FROM calc_runs").fetchone()["x"]
    c.close()
    return n

def test_service_default_no_persist():
    seed.init_db()
    before = _run_count()
    with MortgageService() as s:
        out = s.balance_asof(1_000_000, 3.5, 360, 12, None, False)
    assert out["run_id"] is None
    assert _run_count() == before

def test_service_persist_pins_period_and_balance():
    seed.init_db()
    with MortgageService() as s:
        out = s.balance_asof(1_000_000, 3.5, 360, 12, None, True)
    assert out["run_id"]
    c = connect()
    row = c.execute("SELECT * FROM calc_runs WHERE id=?", (out["run_id"],)).fetchone()
    c.close()
    assert row["kind"] == "balance_asof"
    inp, res = json.loads(row["input_json"]), json.loads(row["result_json"])
    assert inp["period"] == 12
    assert res["period"] == 12
    assert res["balance"] == out["balance"]

def test_service_rejects_out_of_range_without_writing():
    seed.init_db()
    before = _run_count()
    with MortgageService() as s:
        with pytest.raises(ValueError):
            s.balance_asof(1_000_000, 3.5, 360, 361, None, True)
    assert _run_count() == before

def test_snapshot_immune_to_later_rate_change():
    seed.init_db()
    with MortgageService() as s:
        out = s.balance_asof(1_000_000, 3.5, 360, 12, 1, True)
    c = connect()
    c.execute("UPDATE loans SET annual_rate=9.9 WHERE id=1")
    c.commit()
    row = c.execute("SELECT result_json FROM calc_runs WHERE id=?", (out["run_id"],)).fetchone()
    c.close()
    assert json.loads(row["result_json"])["balance"] == out["balance"]
