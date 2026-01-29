"""
Ejemplo de uso del script de contaminación de datos.
Este script muestra diferentes formas de usar el ContaminadorDataset.
"""

from contaminar_dataset import ContaminadorDataset

def ejemplo_basico():
    """Ejemplo básico: ejecutar todos los casos."""
    print("=" * 70)
    print("EJEMPLO 1: Uso Básico - Todos los casos")
    print("=" * 70)
    
    contaminador = ContaminadorDataset(
        archivo_entrada='social_media_mental_health.csv',
        archivo_salida='ejemplo_basico_contaminado.csv',
        porcentaje_contaminacion=0.10
    )
    
    contaminador.cargar_dataset()
    contaminador.contaminar_dataset()  # Todos los casos
    contaminador.guardar_dataset()
    contaminador.generar_reporte()
    
    print("\n✓ Ejemplo básico completado\n")


def ejemplo_casos_especificos():
    """Ejemplo: ejecutar solo algunos casos específicos."""
    print("=" * 70)
    print("EJEMPLO 2: Casos Específicos - Solo Caso 1, 2 y 5")
    print("=" * 70)
    
    contaminador = ContaminadorDataset(
        archivo_entrada='social_media_mental_health.csv',
        archivo_salida='ejemplo_casos_especificos_contaminado.csv',
        porcentaje_contaminacion=0.05  # 5% en lugar de 10%
    )
    
    contaminador.cargar_dataset()
    # Solo ejecutar casos 1, 2 y 5
    contaminador.contaminar_dataset(casos_activados=['caso1', 'caso2', 'caso5'])
    contaminador.guardar_dataset()
    contaminador.generar_reporte()
    
    print("\n✓ Ejemplo de casos específicos completado\n")


def ejemplo_porcentaje_personalizado():
    """Ejemplo: usar un porcentaje de contaminación diferente."""
    print("=" * 70)
    print("EJEMPLO 3: Porcentaje Personalizado - 15%")
    print("=" * 70)
    
    contaminador = ContaminadorDataset(
        archivo_entrada='social_media_mental_health.csv',
        archivo_salida='ejemplo_15pct_contaminado.csv',
        porcentaje_contaminacion=0.15  # 15% de contaminación
    )
    
    contaminador.cargar_dataset()
    contaminador.contaminar_dataset()
    contaminador.guardar_dataset()
    contaminador.generar_reporte()
    
    print("\n✓ Ejemplo con porcentaje personalizado completado\n")


if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("EJEMPLOS DE USO DEL SCRIPT DE CONTAMINACIÓN")
    print("=" * 70 + "\n")
    
    # Descomentar el ejemplo que quieras ejecutar:
    
    # ejemplo_basico()
    # ejemplo_casos_especificos()
    # ejemplo_porcentaje_personalizado()
    
    print("Nota: Descomenta el ejemplo que quieras ejecutar en el código.")
    print("Los ejemplos están comentados para evitar ejecución automática.")
