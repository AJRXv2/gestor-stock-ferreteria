# Corrección de Proveedores en Railway

Este documento contiene instrucciones para corregir el problema de los proveedores que no aparecen en el formulario de agregar productos manual en la versión online de Railway.

## Problema

En la versión online de Railway (PostgreSQL), los proveedores no aparecen en el formulario de agregar productos manual. Esto se debe a un problema de sincronización entre las tablas `proveedores_duenos` y `proveedores_meta`.

## Solución

Para resolver este problema, es necesario sincronizar la tabla `proveedores_meta` con los datos de `proveedores_duenos` en la base de datos PostgreSQL de Railway.

### Método 1: Ejecutar el script directamente en Railway

1. Sube el archivo `railway_proveedores_meta_fix.py` a tu repositorio de Railway.
2. Conéctate a la consola de Railway y ejecuta el siguiente comando:

```bash
python railway_proveedores_meta_fix.py
```

Este script realizará las siguientes acciones:
- Verificará si existe la tabla `proveedores_meta` y la creará si no existe.
- Limpiará los datos existentes en `proveedores_meta`.
- Obtendrá todas las relaciones de `proveedores_duenos` y las sincronizará en `proveedores_meta`.
- Verificará que la sincronización se haya realizado correctamente.

### Método 2: Ejecutar manualmente en la consola SQL de Railway

Si prefieres ejecutar las consultas manualmente, sigue estos pasos desde la consola SQL de Railway:

1. Crea la tabla `proveedores_meta` si no existe:

```sql
CREATE TABLE IF NOT EXISTS proveedores_meta (
    id SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL,
    dueno TEXT NOT NULL
);
```

2. Limpia los datos existentes en `proveedores_meta`:

```sql
DELETE FROM proveedores_meta;
```

3. Inserta los datos de `proveedores_duenos` en `proveedores_meta`:

```sql
INSERT INTO proveedores_meta (nombre, dueno)
SELECT p.nombre, pd.dueno
FROM proveedores_manual p
JOIN proveedores_duenos pd ON p.id = pd.proveedor_id
ORDER BY p.nombre, pd.dueno;
```

4. Verifica que la sincronización se haya realizado correctamente:

```sql
SELECT COUNT(*) FROM proveedores_meta;
SELECT nombre, dueno FROM proveedores_meta LIMIT 10;
```

## Verificación

Para verificar que el problema se ha resuelto correctamente:

1. Accede a la aplicación en Railway.
2. Ve a la página de agregar productos manual.
3. Verifica que los selectores de proveedores muestran correctamente los proveedores para cada dueño (Ricky y Ferretería General).

## Información adicional

Este problema ocurre porque la aplicación utiliza la tabla `proveedores_meta` para poblar los selectores de proveedores en el formulario de agregar productos manual, pero esta tabla no estaba sincronizada con `proveedores_duenos`.

La tabla `proveedores_duenos` contiene las relaciones entre proveedores y dueños, mientras que `proveedores_meta` es utilizada por el frontend para mostrar estas relaciones en los formularios.

El script y las consultas proporcionadas aseguran que ambas tablas estén sincronizadas correctamente.