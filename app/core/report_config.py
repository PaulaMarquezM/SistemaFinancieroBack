from datetime import datetime

# NOTE:
# Keep this as a simple config file for now.
# If you create a DB table for cooperative settings later, load it here.

COOP_NAME = "Cooperativa de Ahorro y Credito"
COOP_LOGO = "LOGOSF.png"
REPORT_RESPONSIBLE = "Equipo 1"


def get_report_header(report_type: str) -> dict:
    now = datetime.now()
    return {
        "coop_name": COOP_NAME,
        "coop_logo": COOP_LOGO,
        "report_type": report_type,
        "issued_at": now.isoformat(timespec="seconds"),
        "issued_date": now.date().isoformat(),
        "responsible": REPORT_RESPONSIBLE,
    }
