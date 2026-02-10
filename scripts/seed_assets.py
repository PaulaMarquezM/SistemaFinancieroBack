import sys
import os
import random
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import Session

# Ajuste de path para que encuentre la carpeta 'app'
sys.path.append(os.getcwd())

from app.core.database import SessionLocal
# Importamos AMBOS modelos
from app.models.asset import Asset, AssetDepreciation 

def seed_assets_complete():
    db: Session = SessionLocal()
    print("🌱 Sembrando Activos Fijos con sus Tablas de Depreciación...")

    # Configuración de categorías según normativa común
    categorias = [
        {"name": "Equipos de cómputo y software", "vida": 3},
        {"name": "Vehículos", "vida": 5},
        {"name": "Maquinarias y equipos", "vida": 10},
        {"name": "Muebles y Enseres", "vida": 10}
    ]

    nombres = [
        "Laptop Dell Latitude", "MacBook Pro", "Servidor HP", 
        "Camioneta Hilux", "Moto Honda", "Panel de Reparto",
        "Escritorio Gerencial", "Silla Ergonómica", "Estantería Metálica",
        "Impresora Industrial", "Torno CNC"
    ]

    # Crear 15 activos
    for _ in range(15):
        cat = random.choice(categorias)
        nombre_activo = f"{random.choice(nombres)} - {random.randint(1000, 9999)}"
        costo = random.choice([800, 1200, 2500, 5000, 15000, 28000, 45000])
        
        # Fecha de compra (entre hace 1 mes y 2 años atrás)
        dias_atras = random.randint(30, 700)
        fecha_compra = datetime.now() - timedelta(days=dias_atras)

        # 1. CREAR EL ACTIVO (PADRE)
        asset = Asset(
            name=nombre_activo,
            category=cat["name"],
            cost=float(costo),
            residual_rate=0.10, # 10% estándar
            useful_life_years=cat["vida"],
            acquisition_date=fecha_compra.date(), # .date() porque tu modelo es Date
            is_active=True
        )
        db.add(asset)
        db.commit()
        db.refresh(asset) # Obtenemos el ID generado

        # 2. CALCULAR Y GUARDAR LA TABLA (HIJOS)
        # Método de Línea Recta
        valor_residual = costo * asset.residual_rate
        valor_a_depreciar = costo - valor_residual
        meses_totales = asset.useful_life_years * 12
        depreciacion_mensual = valor_a_depreciar / meses_totales
        
        dep_acumulada = 0
        
        # Generar fila por cada mes
        for i in range(1, meses_totales + 1):
            fecha_periodo = fecha_compra + relativedelta(months=i)
            
            dep_acumulada += depreciacion_mensual
            valor_libros = costo - dep_acumulada

            # Ajuste de redondeo final para que no baje del residual
            if i == meses_totales:
                valor_libros = valor_residual
                dep_acumulada = costo - valor_residual

            # Crear registro en AssetDepreciation
            dep_row = AssetDepreciation(
                asset_id=asset.id,
                period_number=i,
                period_date=fecha_periodo.date(),
                depreciation_amount=round(depreciacion_mensual, 2),
                accumulated_depreciation=round(dep_acumulada, 2),
                book_value=round(valor_libros, 2)
            )
            db.add(dep_row)
        
        # Guardar todas las filas de este activo
        db.commit()

    print("✅ Activos y sus tablas generados correctamente.")
    db.close()

if __name__ == "__main__":
    seed_assets_complete()