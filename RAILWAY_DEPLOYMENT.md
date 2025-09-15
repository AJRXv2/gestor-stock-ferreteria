# Guía de Despliegue en Railway

Esta guía contiene los pasos necesarios para desplegar correctamente la aplicación Gestor de Stock en Railway y asegurar que la base de datos PostgreSQL esté correctamente configurada.

## Prerrequisitos

- Cuenta en [Railway](https://railway.app/)
- Repositorio en GitHub con el código del Gestor de Stock
- Git instalado en tu máquina local

## Pasos para el Despliegue

### 1. Preparar el Código (Ya Completado)

✅ El código ya ha sido adaptado para PostgreSQL.  
✅ El archivo `requirements.txt` incluye todas las dependencias necesarias.  
✅ El archivo `Procfile` está configurado correctamente.  
✅ Se han implementado endpoints de migración y diagnóstico.

### 2. Conectar Railway con GitHub

1. Inicia sesión en [Railway Dashboard](https://railway.app/dashboard)
2. Haz clic en "New Project"
3. Selecciona "Deploy from GitHub repo"
4. Si es la primera vez, conecta tu cuenta de GitHub:
   - Haz clic en "Connect GitHub"
   - Autoriza a Railway para acceder a tus repositorios
5. Busca y selecciona el repositorio `gestor-stock-ferreteria`
6. Haz clic en "Deploy Now"

### 3. Agregar Base de Datos PostgreSQL

1. En el panel del proyecto recién creado, haz clic en "New"
2. Selecciona "Database" y luego "PostgreSQL"
3. Espera a que se aprovisione la base de datos (esto puede tardar unos minutos)

### 4. Configurar Variables de Entorno

1. En el panel del proyecto, haz clic en el servicio web (no en la base de datos)
2. Ve a la pestaña "Variables"
3. Asegúrate de que `DATABASE_URL` ya está configurada (Railway lo hace automáticamente)
4. Agrega las siguientes variables:
   - `MIGRATION_TOKEN`: Genera un token seguro (por ejemplo, usando [este generador](https://generate-random.org/api-token-generator))
   - `PORT`: 8080 (el puerto que Railway espera)
   - `FLASK_ENV`: production
   - `SECRET_KEY`: Genera una clave secreta para Flask (distinta del token de migración)

### 5. Ejecutar los Diagnósticos

Una vez que el despliegue esté completo, primero debemos diagnosticar los problemas específicos:

1. Obtén la URL de tu aplicación desde el panel de Railway (algo como `https://gestor-stock-ferreteria-xxxx.up.railway.app`)
2. Accede a los endpoints de diagnóstico:

```
# Diagnóstico general de la base de datos
https://gestor-stock-ferreteria-xxxx.up.railway.app/diagnostico_railway

# Diagnóstico específico de búsqueda por proveedor
https://gestor-stock-ferreteria-xxxx.up.railway.app/diagnostico_busqueda?proveedor=jeluz&termino=cable
```

Revisa los resultados para identificar problemas específicos.

### 6. Ejecutar las Correcciones

Después de revisar los diagnósticos, ejecuta los endpoints de corrección:

1. Primero, aplica la migración de la estructura de la base de datos:

```bash
curl -X POST https://gestor-stock-ferreteria-xxxx.up.railway.app/api/fix_railway_db -H "X-Migration-Token: TU_TOKEN_AQUI"
```

2. Luego, normaliza los nombres de proveedores (esto puede resolver problemas de búsqueda por case sensitivity):

```bash
curl -X POST https://gestor-stock-ferreteria-xxxx.up.railway.app/api/fix_railway_proveedores_case -H "X-Migration-Token: TU_TOKEN_AQUI"
```

Alternativamente, puedes usar el script `test_migration_endpoint.py` actualizado para probar estos endpoints localmente antes de ejecutarlos en Railway:

```bash
# Configurar token
$env:MIGRATION_TOKEN = "tu_token_secreto"

# Ejecutar diagnóstico de Railway
python test_migration_endpoint.py diagnostico_railway

# Ejecutar diagnóstico de búsqueda
python test_migration_endpoint.py diagnostico_busqueda

# Ejecutar migración de base de datos
python test_migration_endpoint.py fix_db

# Ejecutar normalización de proveedores
python test_migration_endpoint.py fix_proveedores_case
```

### 7. Verificar las Correcciones

1. Vuelve a acceder a los endpoints de diagnóstico para verificar que los problemas se han resuelto.
2. Prueba la funcionalidad de búsqueda en la aplicación para asegurarte de que ahora funciona correctamente.

## Solución de Problemas Específicos

### Problemas con la Búsqueda por Proveedor

Si la búsqueda por proveedor sigue sin funcionar correctamente después de aplicar las correcciones, verifica:

1. **Sensibilidad a mayúsculas/minúsculas**: Asegúrate de que se ha ejecutado correctamente la normalización de proveedores.
2. **Estructura de la base de datos**: Verifica que todas las tablas necesarias existen y tienen la estructura correcta.
3. **Datos de proveedores**: Verifica que los proveedores existen en la tabla `proveedores_manual` y tienen el formato correcto.

### Errores en la Base de Datos

Si encuentras errores específicos de la base de datos:

1. En Railway, haz clic en el servicio de PostgreSQL
2. Ve a la pestaña "Data"
3. Puedes ejecutar consultas SQL directamente para verificar y modificar la estructura de la base de datos

```sql
-- Ver nombres de proveedores actuales
SELECT DISTINCT proveedor FROM productos_manual ORDER BY proveedor;

-- Verificar relaciones entre proveedores y dueños
SELECT pd.*, pm.nombre FROM proveedores_duenos pd
JOIN proveedores_manual pm ON pd.proveedor_id = pm.id;
```

## Comandos Útiles para Diagnóstico

```bash
# Ver logs de la aplicación en Railway
railway logs

# Conectarse directamente a la base de datos en Railway
railway connect

# Ejecutar una consulta SQL específica
railway run "SELECT * FROM proveedores_manual LIMIT 10"
```

## Contacto y Soporte

Si encuentras problemas durante el despliegue, puedes:

1. Revisar los logs en Railway para obtener más información sobre los errores
2. Consultar la [documentación de Railway](https://docs.railway.app/)
3. Utilizar los endpoints de diagnóstico para obtener información detallada
4. Contactar al desarrollador para soporte adicional