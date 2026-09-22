from pydantic import BaseModel, Field, model_validator
class ScheduleRequest(BaseModel):
    principal: float = Field(gt=0)
    annual_rate: float = Field(ge=0)
    months: int = Field(gt=0, le=600)
    loan_id: int | None = None
    persist: bool = True
    preview_rows: int = Field(default=12, ge=1, le=600)

class BalanceAsofRequest(BaseModel):
    principal: float = Field(gt=0)
    annual_rate: float = Field(ge=0)
    months: int = Field(gt=0, le=600)
    target_period: int = Field(ge=1)
    loan_id: int | None = None
    persist: bool = False

    @model_validator(mode="after")
    def _check_period(self):
        if self.target_period > self.months:
            raise ValueError("target_period 须落在 1 到总期数之间")
        return self
