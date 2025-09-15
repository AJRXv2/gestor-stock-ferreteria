# Migración de Productos Manuales desde Excel a Base de Datos

Este documento explica la migración de productos manuales desde el archivo Excel `productos_manual.xlsx` a la tabla `productos_manual` en la base de datos.

## Objetivo

El objetivo de esta migración es mejorar el rendimiento y la confiabilidad del sistema al almacenar los productos manuales en la base de datos en lugar de un archivo Excel, mientras se mantiene la compatibilidad con el resto del sistema que seguirá utilizando archivos Excel para los productos de Ricky.

## Cambios Realizados

1. **Migración de Datos**: Todos los productos del archivo `productos_manual.xlsx` han sido migrados a la tabla `productos_manual` en la base de datos.

2. **Actualización de Funciones de Búsqueda**:
   - `buscar_en_excel_manual`
   - `buscar_en_excel_manual_por_nombre_proveedor`
   - `buscar_en_excel_manual_por_proveedor`

   Estas funciones ahora buscan en la base de datos en lugar del archivo Excel, manteniendo el mismo formato de resultados.

3. **Actualización de Funciones de Gestión**:
   - `agregar_producto_manual_excel`
   - `agregar_producto_excel_manual`

   Ahora añaden productos directamente a la base de datos y actualizan el Excel como respaldo.

4. **Actualización de Funciones de Eliminación**:
   - `manual_eliminar_seleccionados_ajax`
   - `manual_eliminar_por_proveedor_ajax`

   Ahora eliminan productos de la base de datos y actualizan el Excel como respaldo.

## Compatibilidad

Para mantener la compatibilidad con el sistema actual:

- El archivo Excel `productos_manual.xlsx` se sigue actualizando como respaldo.
- Se agregó una función `export_db_to_excel()` que sincroniza los datos de la base de datos con el Excel.
- No se modificó ninguna función relacionada con otros archivos Excel (productos de Ricky).

## Ventajas

1. **Mejor Rendimiento**: Las consultas a la base de datos son más rápidas que la lectura del archivo Excel.
2. **Mayor Confiabilidad**: Evita problemas de bloqueo o corrupción del archivo Excel.
3. **Soporte para Búsquedas Complejas**: Las consultas SQL permiten búsquedas más eficientes y complejas.
4. **Compatibilidad con PostgreSQL**: Funciona tanto en SQLite (local) como en PostgreSQL (Railway).

## Archivos Creados

- `migrate_productos_manual.py`: Script para migrar datos del Excel a la base de datos.
- `update_search_functions.py`: Script para actualizar las funciones de búsqueda.
- `update_product_functions.py`: Script para actualizar las funciones de agregación de productos.
- `update_delete_functions.py`: Script para actualizar las funciones de eliminación.
- `install_migracion.py`: Script de instalación que ejecuta todos los pasos anteriores.
- `README_migracion.md`: Este documento de documentación.

## Cómo Verificar la Migración

1. **Verificar que los productos existentes estén en la base de datos**:
   ```sql
   SELECT * FROM productos_manual;
   ```

2. **Probar la búsqueda**:
   - Buscar productos manuales con diferentes criterios.
   - Verificar que se muestren correctamente en la interfaz.

3. **Probar la agregación**:
   - Agregar un nuevo producto manual.
   - Verificar que se guarde en la base de datos y se actualice el Excel.

4. **Probar la eliminación**:
   - Eliminar un producto manual.
   - Verificar que se elimine de la base de datos y se actualice el Excel.

## Solución de Problemas

Si se encuentran problemas durante la migración:

1. **Restaurar el archivo Excel original**: Se creó una copia de seguridad en la carpeta `backups/`.
2. **Verificar los logs**: Los mensajes de error se imprimen en la consola con prefijos como `[DB ERROR]`.
3. **Probar manualmente**: Utilizar los scripts individuales para diagnosticar problemas específicos.

## Conclusión

Esta migración mejora significativamente el rendimiento y la confiabilidad del sistema para los productos manuales, mientras mantiene la compatibilidad con el resto del sistema. Los productos de Ricky siguen utilizando archivos Excel como antes, sin ningún cambio.