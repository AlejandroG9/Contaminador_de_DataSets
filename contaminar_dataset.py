"""
Script para introducir intencionalmente problemas de calidad de datos en un dataset.
Propósito: Ejemplificar los 7 casos de uso para limpieza de datos durante clases.

Autor: Script educativo para Ingeniería de la Información
Fecha: 2024
"""

import pandas as pd
import numpy as np
import random
from typing import Dict, List
import json

# Importar los casos de contaminación desde la carpeta casos/
from casos import (
    aplicar_caso1,
    aplicar_caso2,
    aplicar_caso3,
    aplicar_caso4,
    aplicar_caso5,
    aplicar_caso6,
    aplicar_caso7
)


class ContaminadorDataset:
    """
    Clase para introducir problemas de calidad de datos en un dataset.
    Diseñada para ser reutilizable con otros datasets.
    """
    
    def __init__(self, archivo_entrada: str, archivo_salida: str, porcentaje_contaminacion: float = 0.10):
        """
        Inicializa el contaminador de dataset.
        
        Args:
            archivo_entrada: Ruta al archivo CSV original (limpio)
            archivo_salida: Ruta donde se guardará el CSV contaminado
            porcentaje_contaminacion: Porcentaje de registros a contaminar por caso (0.10 = 10%)
        """
        self.archivo_entrada = archivo_entrada
        self.archivo_salida = archivo_salida
        self.porcentaje_contaminacion = porcentaje_contaminacion
        self.df = None
        self.reporte_problemas = {}
        
    def cargar_dataset(self):
        """Carga el dataset original desde el archivo CSV."""
        self.df = pd.read_csv(self.archivo_entrada)
        print(f"Dataset cargado: {len(self.df)} registros, {len(self.df.columns)} columnas")
        
    def guardar_dataset(self):
        """Guarda el dataset contaminado en un nuevo archivo CSV."""
        self.df.to_csv(self.archivo_salida, index=False)
        print(f"Dataset contaminado guardado en: {self.archivo_salida}")
        
    def generar_reporte(self, archivo_reporte: str = None):
        """Genera un reporte JSON con los problemas introducidos."""
        if archivo_reporte is None:
            archivo_reporte = self.archivo_salida.replace('.csv', '_reporte.json')
        
        # Convertir tipos numpy a tipos nativos de Python para serialización JSON
        def convertir_tipos(obj):
            if isinstance(obj, (np.integer, np.int64)):
                return int(obj)
            elif isinstance(obj, (np.floating, np.float64)):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {key: convertir_tipos(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [convertir_tipos(item) for item in obj]
            return obj
        
        reporte_convertido = convertir_tipos(self.reporte_problemas)
        
        with open(archivo_reporte, 'w', encoding='utf-8') as f:
            json.dump(reporte_convertido, f, indent=2, ensure_ascii=False)
        print(f"Reporte de problemas guardado en: {archivo_reporte}")
        
    # ============================================================================
    # MÉTODO PRINCIPAL
    # ============================================================================
    
    def contaminar_dataset(self, casos_activados: List[str] = None):
        """
        Ejecuta todos los casos de contaminación o solo los especificados.
        
        Args:
            casos_activados: Lista de casos a ejecutar. Si es None, ejecuta todos.
                            Opciones: ['caso1', 'caso2', 'caso3', 'caso4', 'caso5', 'caso6', 'caso7']
        """
        if casos_activados is None:
            casos_activados = ['caso1', 'caso2', 'caso3', 'caso4', 'caso5', 'caso6', 'caso7']
        
        print("=" * 70)
        print("CONTAMINACIÓN DE DATASET - 7 CASOS DE USO PARA LIMPIEZA")
        print("=" * 70)
        
        # Establecer semilla para reproducibilidad
        random.seed(42)
        np.random.seed(42)
        
        # Aplicar los casos de contaminación desde los módulos separados
        if 'caso1' in casos_activados:
            aplicar_caso1(self.df, self.porcentaje_contaminacion, self.reporte_problemas)
        if 'caso2' in casos_activados:
            aplicar_caso2(self.df, self.porcentaje_contaminacion, self.reporte_problemas)
        if 'caso3' in casos_activados:
            aplicar_caso3(self.df, self.porcentaje_contaminacion, self.reporte_problemas)
        if 'caso4' in casos_activados:
            aplicar_caso4(self.df, self.porcentaje_contaminacion, self.reporte_problemas)
        if 'caso5' in casos_activados:
            aplicar_caso5(self.df, self.porcentaje_contaminacion, self.reporte_problemas)
        if 'caso6' in casos_activados:
            aplicar_caso6(self.df, self.porcentaje_contaminacion, self.reporte_problemas)
        if 'caso7' in casos_activados:
            aplicar_caso7(self.df, self.porcentaje_contaminacion, self.reporte_problemas)
        
        print("\n" + "=" * 70)
        print("CONTAMINACIÓN COMPLETADA")
        print("=" * 70)
        
        total_problemas = sum(caso['total_problemas'] for caso in self.reporte_problemas.values())
        print(f"\nTotal de problemas introducidos: {total_problemas}")
        print(f"Porcentaje de contaminación por caso: {self.porcentaje_contaminacion*100}%")
        


# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def main():
    """Función principal para ejecutar el script."""
    
    # Configuración
    archivo_entrada = 'social_media_mental_health.csv'
    archivo_salida = 'social_media_mental_health_contaminado.csv'
    porcentaje_contaminacion = 0.10  # 10% de los registros por caso
    
    # Crear instancia del contaminador
    contaminador = ContaminadorDataset(
        archivo_entrada=archivo_entrada,
        archivo_salida=archivo_salida,
        porcentaje_contaminacion=porcentaje_contaminacion
    )
    
    # Cargar dataset
    contaminador.cargar_dataset()
    
    # Ejecutar todos los casos de contaminación
    # Para ejecutar solo algunos casos, pasar: casos_activados=['caso1', 'caso2']
    contaminador.contaminar_dataset()
    
    # Guardar dataset contaminado
    contaminador.guardar_dataset()
    
    # Generar reporte
    contaminador.generar_reporte()
    
    print("\n✓ Proceso completado exitosamente!")
    print(f"  - Dataset original: {archivo_entrada}")
    print(f"  - Dataset contaminado: {archivo_salida}")
    print(f"  - Reporte de problemas: {archivo_salida.replace('.csv', '_reporte.json')}")


if __name__ == '__main__':
    main()
