from app.models.user import User
from app.models.customer import Customer
from app.models.credit import Credit
from app.models.credit_payment import CreditPayment
from app.models.asset import Asset
from app.models.account_receivable import AccountReceivable
# Así debe quedar tu import de activos:
from app.models.asset import Asset, AssetDepreciation

__all__ = [
    "User",
    "Customer",
    "Credit",
    "CreditPayment",
    "Asset",
    "AssetDepreciation",
    "AccountReceivable",
]
