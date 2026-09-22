from fastapi import APIRouter
from app.schemas.schedule import BalanceAsofRequest, ScheduleRequest
from app.services.mortgage_service import MortgageService
router = APIRouter()
@router.post("/schedule")
def post_schedule(body: ScheduleRequest):
    with MortgageService() as s:
        return s.schedule(body.principal, body.annual_rate, body.months, body.loan_id, body.persist, body.preview_rows)
@router.post("/balance-asof")
def post_balance_asof(body: BalanceAsofRequest):
    with MortgageService() as s:
        return s.balance_asof(body.principal, body.annual_rate, body.months, body.target_period, body.loan_id, body.persist)
