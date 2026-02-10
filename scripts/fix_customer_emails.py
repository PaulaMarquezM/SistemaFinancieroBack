import sys
import os
import unicodedata
from sqlalchemy.orm import Session

# Ajuste de path para que encuentre la carpeta 'app'
sys.path.append(os.getcwd())

from app.core.database import SessionLocal
from app.models.customer import Customer

def clean_string(input_str):
    if not input_str:
        return ""
    # 1. Convertir a minúsculas
    nfkd_form = unicodedata.normalize('NFKD', input_str.lower())
    # 2. Eliminar tildes (caracteres no-ASCII)
    only_ascii = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
    # 3. Eliminar espacios
    return only_ascii.replace(" ", "")

def fix_emails():
    db: Session = SessionLocal()
    print("🔧 Iniciando reparación de emails...")
    
    customers = db.query(Customer).all()
    count = 0
    
    for c in customers:
        old_email = c.email
        # Asumimos estructura nombre.apellido@ejemplo.com, limpiamos cada parte
        # O simplemente limpiamos todo el email si ya fue generado
        
        # Una forma más segura: reconstruir el email desde los nombres limpios
        clean_first = clean_string(c.first_name)
        clean_last = clean_string(c.last_name)
        new_email = f"{clean_first}.{clean_last}@ejemplo.com"
        
        if c.email != new_email:
            c.email = new_email
            count += 1
            print(f"   Corregido: {old_email} -> {new_email}")

    try:
        db.commit()
        print(f"✅ ¡Listo! Se corrigieron {count} clientes con emails inválidos.")
    except Exception as e:
        print(f"❌ Error al guardar cambios: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_emails()