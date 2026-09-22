def equal_payment_schedule(principal: float, annual_rate: float, months: int) -> dict:
    P = float(principal)
    n = int(months)
    r = float(annual_rate) / 12.0 / 100.0
    if n <= 0:
        raise ValueError("months")
    if r == 0:
        pay = P / n
    else:
        pay = P * r * (1 + r) ** n / ((1 + r) ** n - 1)
    rows = []
    bal = P
    interest_sum = 0.0
    for i in range(1, n + 1):
        interest = bal * r
        principal_part = pay - interest
        if i == n:
            principal_part = bal
            pay_i = principal_part + interest
        else:
            pay_i = pay
        bal = max(0.0, bal - principal_part)
        interest_sum += interest
        rows.append({
            "period": i,
            "payment": round(pay_i, 2),
            "principal": round(principal_part, 2),
            "interest": round(interest, 2),
            "balance": round(bal, 2),
        })
    return {
        "monthly_payment": round(pay if n else 0, 2),
        "total_interest": round(interest_sum, 2),
        "total_payment": round(sum(x["payment"] for x in rows), 2),
        "rows": rows,
    }


def balance_asof(principal: float, annual_rate: float, months: int, period: int) -> dict:
    """第 period 期期末的剩余本金快照,行数据与 equal_payment_schedule 完全一致。"""
    n = int(months)
    p = int(period)
    if p < 1 or p > n:
        raise ValueError("period")
    row = equal_payment_schedule(principal, annual_rate, n)["rows"][p - 1]
    return {
        "period": p,
        "payment": row["payment"],
        "principal": row["principal"],
        "interest": row["interest"],
        "balance": row["balance"],
        "principal_paid": round(float(principal) - row["balance"], 2),
    }
