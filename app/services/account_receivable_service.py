from datetime import date
import calendar
from typing import List, Dict

from sqlalchemy.orm import Session

from app.models.account_receivable import AccountReceivable


def list_pending(db: Session) -> List[AccountReceivable]:
    return (
        db.query(AccountReceivable)
        .filter(AccountReceivable.status == "pending")
        .order_by(AccountReceivable.due_date.asc())
        .all()
    )


def get_monthly_report(db: Session, month: str) -> Dict:
    # month: YYYY-MM
    year_str, month_str = month.split("-")
    year = int(year_str)
    month_num = int(month_str)

    start = date(year, month_num, 1)
    end_day = calendar.monthrange(year, month_num)[1]
    end = date(year, month_num, end_day)

    rows = (
        db.query(AccountReceivable)
        .filter(AccountReceivable.due_date >= start)
        .filter(AccountReceivable.due_date <= end)
        .order_by(AccountReceivable.due_date.asc())
        .all()
    )

    total = sum(r.amount_due for r in rows)
    report_rows = [
        {
            "id": r.id,
            "customer_name": r.customer_name,
            "amount_due": r.amount_due,
            "due_date": r.due_date,
            "status": r.status,
        }
        for r in rows
    ]

    return {
        "month": month,
        "total_amount": round(float(total), 2),
        "count": len(rows),
        "rows": report_rows,
    }
