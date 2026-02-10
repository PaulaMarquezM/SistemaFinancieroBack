import sys
import os
import random
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import Session
from sqlalchemy import text

# Ajuste de path
sys.path.append(os.getcwd())

from app.core.database import SessionLocal
from app.models.asset import Asset, AssetDepreciation

# Importamos tu lógica de negocio para usarla directamente
# Esto garantiza que el script haga EXACTAMENTE lo mismo que el botón "Guardar" del frontend
from app.services.asset_service import create_asset

def reset_and_seed_assets():
    db: Session = SessionLocal()
    print("🔄 Reiniciando módulo de Activos Fijos...")

    try:
        # 1. ELIMINAR TODOS LOS ACTIVOS EXISTENTES (Limpieza total)
        # Usamos SQL directo para mayor rapidez y limpiar cascadas si la configuración falla
        print("🗑️ Eliminando datos antiguos...")
        db.execute(text("DELETE FROM asset_depreciations"))
        db.execute(text("DELETE FROM assets"))
        db.commit()
        print("   Base de datos de activos limpia.")

        # 2. GENERAR NUEVOS ACTIVOS CONECTADOS AL SERVICIO
        print("🌱 Sembrando nuevos activos calculados...")
        
        categorias = [
            {"name": "Equipos de cómputo y software", "vida": 3},
            {"name": "Vehículos", "vida": 5},
            {"name": "Maquinarias y equipos", "vida": 10},
            {"name": "Muebles y Enseres", "vida": 10}
        ]

        nombres = [
            "Laptop Dell Vostro", "MacBook Air M2", "Servidor Rack Dell", 
            "Toyota Hilux 4x4", "Honda Cargo 150", "Furgoneta DFSK",
            "Silla Gerencial Mesh", "Escritorio en L", "Archivador Metálico"
        ]

        for _ in range(15):
            cat = random.choice(categorias)
            nombre = f"{random.choice(nombres)} - {random.randint(100, 999)}"
            costo = random.choice([800, 1500, 4500, 18000, 25000, 42000])
            
            # Fecha compra aleatoria
            dias = random.randint(30, 600)
            fecha_compra = datetime.now() - timedelta(days=dias)

            # Preparamos el objeto Asset (sin guardarlo aún)
            nuevo_activo = Asset(
                name=nombre,
                category=cat["name"],
                cost=float(costo),
                residual_rate=0.10,
                useful_life_years=cat["vida"],
                acquisition_date=fecha_compra.date(),
                is_active=True
            )

            # ¡AQUÍ ESTÁ LA CLAVE!
            # Usamos tu función 'create_asset' del servicio.
            # Ella se encarga de guardar el activo Y calcular la tabla automáticamente.
            create_asset(db, nuevo_activo)
        
        print("✅ 15 Activos generados exitosamente con sus tablas.")

    except Exception as e:
        print(f"❌ Error crítico: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    reset_and_seed_assets()