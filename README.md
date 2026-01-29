# Script de Contaminación de Datos

## Propósito

Este script está diseñado para **propósitos educativos** en la materia de Ingeniería de la Información. Introduce intencionalmente problemas de calidad de datos en un dataset limpio para poder ejemplificar durante las clases cómo identificar y resolver cada tipo de problema.

## Los 7 Casos de Uso para Limpieza

El script introduce los siguientes tipos de problemas:

### Caso 1: Normalización de Categorías
- **Problema**: Variaciones en mayúsculas/minúsculas, espacios extra, variaciones en guiones
- **Ejemplos**: `"male"`, `"MALE"`, `" Male "`, `"hyper-connected"` vs `"Hyper-Connected"`
- **Columnas afectadas**: Gender, User_Archetype, Primary_Platform, Dominant_Content_Type, Activity_Type, GAD_7_Severity, PHQ_9_Severity

### Caso 2: Validación de Rangos Numéricos
- **Problema**: Valores fuera de rangos lógicos o válidos
- **Ejemplos**: `Age = 100`, `Daily_Screen_Time_Hours = 30`, `GAD_7_Score = 25`
- **Columnas afectadas**: Age, Daily_Screen_Time_Hours, GAD_7_Score, PHQ_9_Score

### Caso 3: Detección de Outliers
- **Problema**: Valores estadísticamente extremos pero técnicamente válidos
- **Ejemplos**: `Daily_Screen_Time_Hours = 23.5`, `Sleep_Duration_Hours = 11.8`
- **Columnas afectadas**: Daily_Screen_Time_Hours, Sleep_Duration_Hours

### Caso 4: Validación de Consistencia entre Columnas
- **Problema**: Inconsistencias entre columnas relacionadas
- **Ejemplos**: `GAD_7_Score = 15` pero `GAD_7_Severity = "Mild"` (debería ser "Severe")
- **Columnas afectadas**: GAD_7_Score ↔ GAD_7_Severity, PHQ_9_Score ↔ PHQ_9_Severity

### Caso 5: Manejo de Valores Faltantes
- **Problema**: Celdas vacías, nulos, o valores como "N/A", "NULL", etc.
- **Ejemplos**: `Age = ""`, `Gender = "N/A"`, `Daily_Screen_Time_Hours = "NULL"`
- **Columnas afectadas**: Todas las columnas principales

### Caso 6: Normalización de Tipos de Datos
- **Problema**: Valores que deberían ser numéricos pero están como texto
- **Ejemplos**: `Age = "dieciocho"`, `GAD_7_Score = "nueve"`, `Late_Night_Usage = "sí"`
- **Columnas afectadas**: Age, Daily_Screen_Time_Hours, Sleep_Duration_Hours, GAD_7_Score, PHQ_9_Score, Late_Night_Usage, Social_Comparison_Trigger

### Caso 7: Limpieza de Formato
- **Problema**: Espacios extra, caracteres especiales, formato inconsistente
- **Ejemplos**: `User_ID = " U-b23639d2 "`, `Primary_Platform = "*Facebook*"`
- **Columnas afectadas**: User_ID, Primary_Platform, Gender

## Uso del Script

### Requisitos

```bash
pip install pandas numpy
```

### Uso Básico

```bash
python3 contaminar_dataset.py
```

Esto ejecutará todos los 7 casos de contaminación sobre el archivo `social_media_mental_health.csv` y generará:
- `social_media_mental_health_contaminado.csv`: Dataset con problemas introducidos
- `social_media_mental_health_contaminado_reporte.json`: Reporte detallado de los problemas

### Configuración

Puedes modificar el script para cambiar:

1. **Porcentaje de contaminación**: Por defecto es 10% por caso
   ```python
   porcentaje_contaminacion = 0.10  # Cambiar a 0.05 para 5%, 0.15 para 15%, etc.
   ```

2. **Archivos de entrada/salida**:
   ```python
   archivo_entrada = 'social_media_mental_health.csv'
   archivo_salida = 'social_media_mental_health_contaminado.csv'
   ```

3. **Casos específicos**: Para ejecutar solo algunos casos, modifica la función `main()`:
   ```python
   contaminador.contaminar_dataset(casos_activados=['caso1', 'caso2', 'caso5'])
   ```

### Uso Programático

```python
from contaminar_dataset import ContaminadorDataset

# Crear instancia
contaminador = ContaminadorDataset(
    archivo_entrada='mi_dataset.csv',
    archivo_salida='mi_dataset_contaminado.csv',
    porcentaje_contaminacion=0.10
)

# Cargar dataset
contaminador.cargar_dataset()

# Ejecutar casos específicos
contaminador.contaminar_dataset(casos_activados=['caso1', 'caso3', 'caso5'])

# Guardar resultados
contaminador.guardar_dataset()
contaminador.generar_reporte('mi_reporte.json')
```

## Reutilización con Otros Datasets

El script está diseñado para ser reutilizable. Para adaptarlo a otro dataset:

1. **Identifica las columnas categóricas** y modifica `caso1_normalizacion_categorias()`:
   ```python
   configuracion = {
       'Tu_Columna_Categorica': {
           'variaciones': ['variacion1', 'variacion2', ...],
           'descripcion': 'Descripción del problema'
       }
   }
   ```

2. **Identifica las columnas numéricas** y modifica `caso2_validacion_rangos_numericos()`:
   - Define los rangos válidos para cada columna
   - Genera valores fuera de esos rangos

3. **Identifica relaciones entre columnas** y modifica `caso4_validacion_consistencia_columnas()`:
   - Define las reglas de consistencia
   - Introduce inconsistencias intencionales

4. **Ajusta los demás casos** según las características de tu dataset

## Estructura del Reporte JSON

El reporte generado contiene información detallada sobre cada problema introducido:

```json
{
  "caso1_normalizacion_categorias": {
    "descripcion": "Problemas de normalización en categorías...",
    "total_problemas": 5600,
    "problemas": [
      {
        "indice": 123,
        "columna": "Gender",
        "valor_original": "Male",
        "valor_contaminado": "male"
      }
    ]
  },
  ...
}
```

## Notas Importantes

1. **El dataset original NO se modifica**: El script siempre crea un nuevo archivo
2. **Reproducibilidad**: El script usa semillas aleatorias (`random.seed(42)`) para resultados consistentes
3. **Warnings de pandas**: Los warnings sobre tipos incompatibles son **esperados** ya que estamos introduciendo problemas intencionalmente
4. **Sobrescritura**: Si ejecutas el script múltiples veces, sobrescribirá los archivos de salida

## Ejemplo de Uso en Clase

1. **Mostrar el dataset original** (limpio)
2. **Ejecutar el script** para generar el dataset contaminado
3. **Mostrar ejemplos de cada tipo de problema** usando el reporte JSON
4. **Ejercitar la limpieza** de cada caso de uso
5. **Comparar** el dataset original con el limpio después de la limpieza

## Autor

Script educativo para Ingeniería de la Información - 2024
