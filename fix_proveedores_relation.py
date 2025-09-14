import os
import sys
import sqlite3
import traceback

# Importar psycopg2 si está disponible
try:
    import psycopg2
    import psycopg2.extras
    HAS_POSTGRES = True
except ImportError:
    HAS_POSTGRES = False

# Ruta a la base de datos SQLite
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_SQLITE_PATH = os.path.join(BASE_DIR, os.getenv('DATABASE_FILE', 'gestor_stock.db'))

def is_postgres():
    """Determinar si se usa PostgreSQL basado en variable de entorno DATABASE_URL."""
    url = os.environ.get('DATABASE_URL', '')
    return 'postgres' in url.lower()

def get_connection():
    """Obtener conexión a la base de datos (PostgreSQL o SQLite)."""
    if is_postgres():
        if not HAS_POSTGRES:
            print("[ERROR] psycopg2-binary no instalado para PostgreSQL")
            sys.exit(1)
        dsn = os.environ.get('DATABASE_URL')
        if dsn.startswith('postgres://'):
            dsn = 'postgresql://' + dsn[len('postgres://'):]
        conn = psycopg2.connect(dsn)
        conn.autocommit = False
        return conn
    else:
        conn = sqlite3.connect(DB_SQLITE_PATH)
        conn.row_factory = sqlite3.Row
        return conn

def execute_query(conn, query, params=(), fetch=False):
    """Ejecutar una consulta SQL con parámetros opcionales."""
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        if fetch:
            if is_postgres():
                result = [dict(row) for row in cursor.fetchall()]
            else:
                result = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
            return result
        else:
            return True
    except Exception as e:
        print(f"Error en consulta: {query}\nParams: {params}\nError: {e}")
        return None if fetch else False
    finally:
        cursor.close()

def get_all_providers(conn):
    """Obtener todos los proveedores desde la tabla proveedores_manual."""
    try:
        # Intentar con la columna oculto
        if is_postgres():
            query = "SELECT id, nombre, dueno FROM proveedores_manual WHERE oculto = 0 OR oculto IS NULL"
        else:
            query = "SELECT id, nombre, dueno FROM proveedores_manual WHERE oculto = 0 OR oculto IS NULL"
        result = execute_query(conn, query, fetch=True)
        if result is not None:
            return result
    except Exception as e:
        print(f"Advertencia: Error al consultar con filtro oculto: {e}")
        
    # Fallback: obtener todos los proveedores sin filtrar por oculto
    query = "SELECT id, nombre, dueno FROM proveedores_manual"
    return execute_query(conn, query, fetch=True)

def get_provider_owners(conn, provider_id):
    """Obtener los dueños asociados a un proveedor desde la tabla proveedores_duenos."""
    query = "SELECT dueno FROM proveedores_duenos WHERE proveedor_id = %s" if is_postgres() else "SELECT dueno FROM proveedores_duenos WHERE proveedor_id = ?"
    return execute_query(conn, query, (provider_id,), fetch=True)

def add_provider_owner(conn, provider_id, owner):
    """Agregar una relación proveedor-dueño a la tabla proveedores_duenos."""
    # Verificar si ya existe
    query = "SELECT 1 FROM proveedores_duenos WHERE proveedor_id = %s AND dueno = %s" if is_postgres() else "SELECT 1 FROM proveedores_duenos WHERE proveedor_id = ? AND dueno = ?"
    exists = execute_query(conn, query, (provider_id, owner), fetch=True)
    
    if not exists:
        query = "INSERT INTO proveedores_duenos (proveedor_id, dueno) VALUES (%s, %s)" if is_postgres() else "INSERT INTO proveedores_duenos (proveedor_id, dueno) VALUES (?, ?)"
        return execute_query(conn, query, (provider_id, owner))
    return True

def get_all_manual_products(conn):
    """Obtener todos los productos manuales que tengan un proveedor asignado."""
    query = """
    SELECT DISTINCT proveedor, dueno 
    FROM productos_manual 
    WHERE proveedor IS NOT NULL AND proveedor != '' AND dueno IS NOT NULL AND dueno != ''
    """
    return execute_query(conn, query, fetch=True)

def get_provider_id_by_name(conn, provider_name):
    """Obtener el ID de un proveedor por su nombre."""
    query = "SELECT id FROM proveedores_manual WHERE LOWER(nombre) = LOWER(%s) LIMIT 1" if is_postgres() else "SELECT id FROM proveedores_manual WHERE LOWER(nombre) = LOWER(?) LIMIT 1"
    result = execute_query(conn, query, (provider_name,), fetch=True)
    return result[0]['id'] if result else None

def fix_provider_duenos_relations():
    """Reparar la tabla proveedores_duenos basándose en proveedores existentes."""
    try:
        conn = get_connection()
        
        print("=== REPARACIÓN DE RELACIONES PROVEEDOR-DUEÑO ===")
        print(f"Motor de base de datos: {'PostgreSQL' if is_postgres() else 'SQLite'}")
        
        # 1. Obtener todos los proveedores
        providers = get_all_providers(conn)
        if not providers:
            print("No se encontraron proveedores.")
            return False
            
        print(f"Encontrados {len(providers)} proveedores activos.")
        
        # 2. Verificar cada proveedor y sus relaciones con dueños
        for provider in providers:
            provider_id = provider['id']
            provider_name = provider['nombre']
            provider_owner = provider.get('dueno', '')
            
            # Obtener dueños actuales del proveedor
            current_owners = get_provider_owners(conn, provider_id)
            current_owner_list = [o['dueno'] for o in current_owners] if current_owners else []
            
            # Si el proveedor tiene un dueño asignado en proveedores_manual, asegurar que exista en proveedores_duenos
            owners_to_add = []
            if provider_owner and provider_owner not in current_owner_list:
                owners_to_add.append(provider_owner)
                
            # Agregar los dueños inferidos de los productos manuales
            print(f"Analizando productos para proveedor '{provider_name}'...")
            
            # 3. Buscar este proveedor en productos_manual para inferir dueños adicionales
            all_products = get_all_manual_products(conn)
            if all_products:
                for product in all_products:
                    product_provider = product['proveedor']
                    product_owner = product['dueno']
                    
                    # Si el nombre del proveedor coincide y el dueño no está ya asociado, agregarlo
                    if product_provider.lower() == provider_name.lower() and product_owner and product_owner not in current_owner_list and product_owner not in owners_to_add:
                        owners_to_add.append(product_owner)
            
            # 4. Agregar las relaciones faltantes
            for owner in owners_to_add:
                success = add_provider_owner(conn, provider_id, owner)
                if success:
                    print(f"Agregada relación: Proveedor '{provider_name}' -> Dueño '{owner}'")
                else:
                    print(f"Error al agregar relación: Proveedor '{provider_name}' -> Dueño '{owner}'")
            
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
                    update_query = "UPDATE proveedores_manual SET dueno = %s WHERE id = %s" if is_postgres() else "UPDATE proveedores_manual SET dueno = ? WHERE id = ?"
                    execute_query(conn, update_query, (default_owner, provider_id))
                    print(f"Actualizado proveedor '{provider_name}' con dueño '{default_owner}'")
                
                # Agregar la relación en proveedores_duenos
                success = add_provider_owner(conn, provider_id, default_owner)
                if success:
                    print(f"Agregada relación predeterminada: Proveedor '{provider_name}' -> Dueño '{default_owner}'")
                else:
                    print(f"Error al agregar relación predeterminada: Proveedor '{provider_name}' -> Dueño '{default_owner}'")
        
        # Confirmar cambios
        conn.commit()
        print("\n=== REPARACIÓN COMPLETADA ===")
        print("Todos los proveedores han sido verificados y reparados.")
        
        # Mostrar estadísticas finales
        query = "SELECT COUNT(*) as count FROM proveedores_manual"
        result = execute_query(conn, query, fetch=True)
        total_providers = result[0]['count'] if result else 0
        
        query = "SELECT COUNT(DISTINCT proveedor_id) as count FROM proveedores_duenos"
        result = execute_query(conn, query, fetch=True)
        providers_with_relations = result[0]['count'] if result else 0
        
        print(f"\nEstadísticas:")
        print(f"- Total de proveedores: {total_providers}")
        print(f"- Proveedores con relaciones: {providers_with_relations}")
        if total_providers > 0:
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
            conn.close()
        except:
            pass

if __name__ == "__main__":
    fix_provider_duenos_relations()