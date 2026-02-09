from pathlib import Path
import sys
from datetime import date

# Configuración para que Python encuentre tu app
ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from app.core.database import SessionLocal
# Importamos los modelos
from app.models.credit import Credit
from app.models.customer import Customer
from app.models.account_receivable import AccountReceivable 

def fix_data():
    db = SessionLocal()
    try:
        # Obtenemos todos los créditos para crearles cobros asociados
        credits = db.query(Credit).all()
        
        if not credits:
            print("❌ No hay créditos. Corre 'python -m scripts.seed_credits' primero.")
            return

        print(f"✅ Encontrados {len(credits)} créditos. Generando cobros compatibles con tu modelo...")
        
        count = 0
        for cred in credits:
            # Buscamos el cliente para obtener su nombre (obligatorio en tu modelo)
            cliente = db.query(Customer).filter(Customer.id == cred.customer_id).first()
            nombre_cliente = cliente.full_name if cliente else "Cliente Desconocido"

            # Creamos 3 cobros falsos para CADA crédito (Feb, Mar, Abr)
            # Usamos tus columnas exactas: amount_due, customer_name, description...
            
            # 1. FEBRERO
            r1 = AccountReceivable(
                customer_id=cred.customer_id,
                customer_name=nombre_cliente,
                amount_due=150.50,  # Tu modelo usa 'amount_due'
                due_date=date(2026, 2, 28),
                status="pending",
                description=f"Cuota Febrero - Crédito #{cred.id}"
            )
            db.add(r1)

            # 2. MARZO
            r2 = AccountReceivable(
                customer_id=cred.customer_id,
                customer_name=nombre_cliente,
                amount_due=150.50,
                due_date=date(2026, 3, 30),
                status="pending",
                description=f"Cuota Marzo - Crédito #{cred.id}"
            )
            db.add(r2)

            # 3. ABRIL
            r3 = AccountReceivable(
                customer_id=cred.customer_id,
                customer_name=nombre_cliente,
                amount_due=150.50,
                due_date=date(2026, 4, 30),
                status="pending",
                description=f"Cuota Abril - Crédito #{cred.id}"
            )
            db.add(r3)
            
            count += 3

        db.commit()
        print(f"🎉 ¡ÉXITO! Se inyectaron {count} cobros (Feb, Mar, Abr).")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    fix_data()