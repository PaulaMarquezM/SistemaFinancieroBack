from datetime import date, timedelta
from app.core.database import SessionLocal, engine, Base
from app.models.account_receivable import AccountReceivable
from app.models.credit import Credit # ✅ Importamos Créditos para vincular

def seed_accounts_receivable():
    # Aseguramos que las tablas existan antes de sembrar
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
        # 1. Buscamos los últimos créditos creados
        credits = db.query(Credit).limit(5).all()
        
        if not credits:
            print("⚠️ No hay créditos en la base de datos. Ejecuta primero seed_credits.")
            return

        print(f"🌱 Sembrando cuotas para {len(credits)} créditos...")

        for credit in credits:
            # Obtenemos el nombre del cliente desde la relación
            customer_name = "Cliente SF"
            if credit.customer:
                customer_name = f"{credit.customer.first_name} {credit.customer.last_name}"

            # Creamos una cuota de prueba para cada crédito
            item_data = {
                "customer_id": credit.customer_id,
                "credit_id": credit.id, # ✅ LA LLAVE MAESTRA
                "customer_name": customer_name,
                "amount_due": round(credit.principal / credit.periods, 2),
                "due_date": date(2026, 2, 10), # Fecha actual de tus pruebas
                "status": "pending",
                "description": f"Crédito #{credit.id} - Cuota 1", # ✅ PARA LA BURBUJA AZUL
            }

            # Evitar duplicados para el mismo crédito y fecha
            existing = (
                db.query(AccountReceivable)
                .filter(AccountReceivable.credit_id == item_data["credit_id"])
                .filter(AccountReceivable.due_date == item_data["due_date"])
                .first()
            )

            if not existing:
                db.add(AccountReceivable(**item_data))
                print(f"✅ Cobro generado: {customer_name} (Crédito #{credit.id})")

        db.commit()
        print("🚀 Siembra de cobranzas completada con éxito.")
        
    except Exception as e:
        print(f"❌ Error en la siembra: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_accounts_receivable()