"""
Script para reparar la relación entre proveedores y dueños
Este script está diseñado para ser ejecutado directamente en Railway
"""
import os
import sys
import traceback

try:
    import psycopg2
    import psycopg2.extras
    HAS_POSTGRES = True
except ImportError:
    HAS_POSTGRES = False
    print("ADVERTENCIA: psycopg2 no está instalado, este script solo funcionará con PostgreSQL")
    sys.exit(1)

def fix_proveedores_duenos():
    """
    Reparar las relaciones entre proveedores y dueños en Railway
    """
    if not os.environ.get('DATABASE_URL'):
        print("ERROR: La variable DATABASE_URL no está definida. Este script debe ejecutarse en Railway.")
        return False
        
    # Conectar a la base de datos
    dsn = os.environ.get('DATABASE_URL')
    if dsn.startswith('postgres://'):
        dsn = 'postgresql://' + dsn[len('postgres://'):]
    
    print(f"Conectando a la base de datos: {dsn[:20]}...")
    
    try:
        conn = psycopg2.connect(dsn)
        conn.autocommit = False
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        print("Conexión establecida. Reparando relaciones proveedor-dueño...")
        
        # 1. Obtener todos los proveedores
        cursor.execute("SELECT id, nombre, dueno FROM proveedores_manual WHERE oculto = 0 OR oculto IS NULL")
        providers = cursor.fetchall()
        print(f"Encontrados {len(providers)} proveedores activos.")
        
        # 2. Verificar cada proveedor y sus relaciones con dueños
        fixed_count = 0
        for provider in providers:
            provider_id = provider['id']
            provider_name = provider['nombre']
            provider_owner = provider.get('dueno', '')
            
            # Obtener dueños actuales del proveedor
            cursor.execute("SELECT dueno FROM proveedores_duenos WHERE proveedor_id = %s", (provider_id,))
            current_owners = cursor.fetchall()
            current_owner_list = [o['dueno'] for o in current_owners] if current_owners else []
            
            # Si el proveedor tiene un dueño asignado en proveedores_manual, asegurar que exista en proveedores_duenos
            owners_to_add = []
            if provider_owner and provider_owner not in current_owner_list:
                owners_to_add.append(provider_owner)
                
            # Agregar los dueños inferidos de los productos manuales
            print(f"Analizando productos para proveedor '{provider_name}'...")
            
            # 3. Buscar este proveedor en productos_manual para inferir dueños adicionales
            cursor.execute("""
                SELECT DISTINCT proveedor, dueno 
                FROM productos_manual 
                WHERE proveedor IS NOT NULL AND proveedor != '' AND dueno IS NOT NULL AND dueno != ''
            """)
            all_products = cursor.fetchall()
            
            for product in all_products:
                product_provider = product['proveedor']
                product_owner = product['dueno']
                
                # Si el nombre del proveedor coincide y el dueño no está ya asociado, agregarlo
                if product_provider.lower() == provider_name.lower() and product_owner and product_owner not in current_owner_list and product_owner not in owners_to_add:
                    owners_to_add.append(product_owner)
            
            # 4. Agregar las relaciones faltantes
            for owner in owners_to_add:
                # Verificar si ya existe
                cursor.execute("SELECT 1 FROM proveedores_duenos WHERE proveedor_id = %s AND dueno = %s", (provider_id, owner))
                exists = cursor.fetchone()
                
                if not exists:
                    try:
                        cursor.execute("INSERT INTO proveedores_duenos (proveedor_id, dueno) VALUES (%s, %s)", (provider_id, owner))
                        print(f"Agregada relación: Proveedor '{provider_name}' -> Dueño '{owner}'")
                        fixed_count += 1
                    except Exception as e:
                        print(f"Error al agregar relación: Proveedor '{provider_name}' -> Dueño '{owner}': {e}")
            
            # 5. Si no tiene dueños aún, asignar uno por defecto basado en el nombre
            if not current_owner_list and not owners_to_add:
                # Proveedores conocidos de Ricky
                ricky_providers = ['Berger', 'BremenTools', 'Cachan', 'Chiesa', 'Crossmaster', 'brementools', 'berger', 'cachan', 'chiesa', 'crossmaster']
                fg_providers = ['DeWalt', 'Sica', 'Sorbalok', 'Nortedist', 'dewalt', 'sica', 'sorbalok', 'nortedist']
                
                # Determinar el dueño por defecto basado en el nombre
                default_owner = None
                if any(p.lower() == provider_name.lower() for p in ricky_providers):
                    default_owner = 'ricky'
                elif any(p.lower() == provider_name.lower() for p in fg_providers):
                    default_owner = 'ferreteria_general'
                else:
                    # Si no está en las listas conocidas, asignar a ferreteria_general por defecto
                    default_owner = 'ferreteria_general'
                
                # Actualizar el dueño en proveedores_manual si estaba vacío
                if not provider.get('dueno'):
                    cursor.execute("UPDATE proveedores_manual SET dueno = %s WHERE id = %s", (default_owner, provider_id))
                    print(f"Actualizado proveedor '{provider_name}' con dueño '{default_owner}'")
                
                # Agregar la relación en proveedores_duenos
                try:
                    cursor.execute("INSERT INTO proveedores_duenos (proveedor_id, dueno) VALUES (%s, %s)", (provider_id, default_owner))
                    print(f"Agregada relación predeterminada: Proveedor '{provider_name}' -> Dueño '{default_owner}'")
                    fixed_count += 1
                except Exception as e:
                    print(f"Error al agregar relación predeterminada: Proveedor '{provider_name}' -> Dueño '{default_owner}': {e}")
        
        # Confirmar cambios
        conn.commit()
        print("\n=== REPARACIÓN COMPLETADA ===")
        print(f"Se han reparado {fixed_count} relaciones entre proveedores y dueños.")
        
        # Mostrar estadísticas finales
        cursor.execute("SELECT COUNT(*) as count FROM proveedores_manual")
        total_providers = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(DISTINCT proveedor_id) as count FROM proveedores_duenos")
        providers_with_relations = cursor.fetchone()['count']
        
        print(f"\nEstadísticas:")
        print(f"- Total de proveedores: {total_providers}")
        print(f"- Proveedores con relaciones: {providers_with_relations}")
        print(f"- Cobertura: {providers_with_relations/total_providers*100:.1f}%")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Error durante la reparación: {e}")
        traceback.print_exc()
        try:
            conn.rollback()
        except:
            pass
        return False
    finally:
        try:
            if 'conn' in locals():
                conn.close()
        except:
            pass

if __name__ == "__main__":
    fix_proveedores_duenos()