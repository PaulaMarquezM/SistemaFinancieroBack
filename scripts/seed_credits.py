import sys
import os
import random
from datetime import datetime
from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import Session

# Ajuste de path
sys.path.append(os.getcwd())

from app.core.database import SessionLocal
from app.models.customer import Customer
from app.models.credit import Credit
from app.models.account_receivable import AccountReceivable

def seed_credits_with_amortization():
    db: Session = SessionLocal()
    print("🌱 Sembrando Créditos REALES con sus Tablas de Amortización...")

    # 1. Obtener clientes
    customers = db.query(Customer).all()
    if not customers:
        print("⚠️ No hay clientes. Corre 'seed_customers.py' primero.")
        return

    # 2. Configuración de simulación
    cantidad_creditos = 25
    
    # Fecha base: Hoy es Feb 2026 en tu sistema.
    fecha_referencia = datetime(2026, 2, 10) 

    for _ in range(cantidad_creditos):
        cliente = random.choice(customers)
        monto = random.choice([1000, 3000, 5000, 10000, 15000, 20000])
        tasa_anual = random.choice([12, 15, 18, 20, 25])
        plazo_meses = random.choice([12, 24, 36, 48])
        metodo = random.choice(["frances", "aleman"])
        
        # Empezaron hace 1 a 6 meses
        meses_atras = random.randint(1, 6)
        fecha_inicio = fecha_referencia - relativedelta(months=meses_atras)

        # --- CÁLCULOS FINANCIEROS ---
        tasa_mensual = (tasa_anual / 100) / 12
        
        # Cuota Referencial
        cuota_ref = 0
        if metodo == 'frances':
            cuota_ref = (monto * tasa_mensual) / (1 - (1 + tasa_mensual) ** -plazo_meses)
        else: # Aleman
            cuota_ref = (monto / plazo_meses) + (monto * tasa_mensual)

        # 3. Crear el Crédito Padre
        credit = Credit(
            customer_id=cliente.id,
            principal=float(monto),
            annual_rate=float(tasa_anual),
            periods=plazo_meses,
            method=metodo,
            start_date=fecha_inicio,
            status="active",
            total_interest=0, 
            total_amount=0,   
            monthly_payment=round(cuota_ref, 2),
            description=f"Préstamo {metodo.capitalize()} - {cliente.first_name}"
        )
        db.add(credit)
        db.commit() 
        db.refresh(credit)

        # 4. Generar la Tabla de Amortización (Cuentas por Cobrar)
        saldo = float(monto)
        amortizacion_fija_aleman = monto / plazo_meses if plazo_meses > 0 else 0
        
        acumulado_interes = 0
        acumulado_total = 0

        for i in range(1, plazo_meses + 1):
            # Fecha de vencimiento
            fecha_venc = fecha_inicio + relativedelta(months=i)
            
            # Cálculos
            interes_mes = saldo * tasa_mensual
            if metodo == 'frances':
                cuota_mes = cuota_ref
                capital_mes = cuota_mes - interes_mes
            else: # Aleman
                capital_mes = amortizacion_fija_aleman
                cuota_mes = capital_mes + interes_mes
            
            saldo -= capital_mes
            if saldo < 0: saldo = 0

            acumulado_interes += interes_mes
            acumulado_total += cuota_mes

            # Determinar estado
            estado_cuota = "pending"
            
            if fecha_venc < fecha_referencia:
                if random.random() > 0.1: # 90% pagado
                    estado_cuota = "paid"
                else:
                    estado_cuota = "overdue" # Mora
            
            # Crear Cuenta por Cobrar (SOLO CAMPOS BÁSICOS SEGUROS)
            ar = AccountReceivable(
                customer_id=cliente.id,
                customer_name=f"{cliente.first_name} {cliente.last_name}",
                amount_due=round(cuota_mes, 2),
                due_date=fecha_venc,
                status=estado_cuota,
                description=f"Cuota {i}/{plazo_meses} - Crédito #{credit.id}"
            )
            db.add(ar)

        # 5. Actualizar totales
        credit.total_interest = round(acumulado_interes, 2)
        credit.total_amount = round(acumulado_total, 2)
        db.add(credit)

    try:
        db.commit()
        print(f"✅ Generados {cantidad_creditos} créditos con sus respectivas tablas de amortización.")
    except Exception as e:
        print(f"❌ Error al guardar datos: {e}")
        print("💡 CONSEJO: Si vuelve a fallar, pásame el contenido de 'app/models/account_receivable.py'")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_credits_with_amortization()