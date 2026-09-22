from fastapi import APIRouter, HTTPException
from app.schemas.schedule import BalanceAsOfRequest, ScheduleRequest
from app.services.mortgage_service import MortgageService
router = APIRouter()
@router.post("/schedule")
def post_schedule(body: ScheduleRequest):
    with MortgageService() as s:
        return s.schedule(body.principal, body.annual_rate, body.months, body.loan_id, body.persist, body.preview_rows)
@router.post("/schedule/balance-asof")
def post_balance_asof(body: BalanceAsOfRequest):
    with MortgageService() as s:
        try:
            return s.balance_asof(body.principal, body.annual_rate, body.months, body.period, body.loan_id, body.persist)
        except ValueError:
            raise HTTPException(status_code=400, detail="period 超出 1..总期数 范围")
