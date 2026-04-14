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
    
    def __init__(self, archivo_entrada: str, archivo_salida: str,
                 porcentaje_contaminacion: float = 0.10, encoding: str = 'utf-8'):
        """
        Inicializa el contaminador de dataset.

        Args:
            archivo_entrada: Ruta al archivo CSV original (limpio)
            archivo_salida: Ruta donde se guardará el CSV contaminado
            porcentaje_contaminacion: Porcentaje de registros a contaminar por caso (0.10 = 10%)
            encoding: Encoding del CSV (default utf-8; usar latin-1 si hay problemas)
        """
        self.archivo_entrada = archivo_entrada
        self.archivo_salida = archivo_salida
        self.porcentaje_contaminacion = porcentaje_contaminacion
        self.encoding = encoding
        self.df = None
        self.reporte_problemas = {}
        self.columnas_detectadas = {}
        
    def cargar_dataset(self):
        """Carga el dataset original desde el archivo CSV."""
        self.df = pd.read_csv(self.archivo_entrada, encoding=self.encoding)
        print(f"Dataset cargado: {len(self.df)} registros, {len(self.df.columns)} columnas")
        self._detectar_columnas()

    def _detectar_columnas(self):
        """Clasifica las columnas del dataset en 5 grupos por tipo."""
        cols_ids = []
        cols_categoricas = []
        cols_binarias = []
        cols_horas = []
        cols_numericas = []

        n = len(self.df)
        keywords_horas = ['hour', 'hora', 'time']

        for col in self.df.columns:
            col_lower = col.lower()
            dtype = self.df[col].dtype

            if dtype == 'object':
                unique_ratio = self.df[col].nunique() / n
                if unique_ratio > 0.8:
                    cols_ids.append(col)
                else:
                    cols_categoricas.append(col)
            elif np.issubdtype(dtype, np.number):
                unique_vals = set(self.df[col].dropna().unique())
                if unique_vals <= {0, 1}:
                    cols_binarias.append(col)
                elif any(kw in col_lower for kw in keywords_horas):
                    cols_horas.append(col)
                else:
                    cols_numericas.append(col)

        self.columnas_detectadas = {
            'cols_ids': cols_ids,
            'cols_categoricas': cols_categoricas,
            'cols_binarias': cols_binarias,
            'cols_horas': cols_horas,
            'cols_numericas': cols_numericas,
        }

        print(f"\nColumnas detectadas:")
        for grupo, cols in self.columnas_detectadas.items():
            if cols:
                print(f"  {grupo}: {cols}")
        
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
            aplicar_caso1(self.df, self.porcentaje_contaminacion, self.reporte_problemas, self.columnas_detectadas)
        if 'caso2' in casos_activados:
            aplicar_caso2(self.df, self.porcentaje_contaminacion, self.reporte_problemas, self.columnas_detectadas)
        if 'caso3' in casos_activados:
            aplicar_caso3(self.df, self.porcentaje_contaminacion, self.reporte_problemas, self.columnas_detectadas)
        if 'caso4' in casos_activados:
            aplicar_caso4(self.df, self.porcentaje_contaminacion, self.reporte_problemas, self.columnas_detectadas)
        if 'caso5' in casos_activados:
            aplicar_caso5(self.df, self.porcentaje_contaminacion, self.reporte_problemas, self.columnas_detectadas)
        if 'caso6' in casos_activados:
            aplicar_caso6(self.df, self.porcentaje_contaminacion, self.reporte_problemas, self.columnas_detectadas)
        if 'caso7' in casos_activados:
            aplicar_caso7(self.df, self.porcentaje_contaminacion, self.reporte_problemas, self.columnas_detectadas)
        
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
    """Punto de entrada CLI del script."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Contamina intencionalmente un dataset CSV con 7 tipos de problemas de calidad de datos.'
    )
    parser.add_argument('archivo', help='Ruta al archivo CSV de entrada')
    parser.add_argument('--salida', default=None,
                        help='Ruta del CSV contaminado (default: <nombre>_contaminado.csv)')
    parser.add_argument('--porcentaje', type=float, default=0.10,
                        help='Porcentaje de registros a contaminar por caso (default: 0.10)')
    parser.add_argument('--casos', type=int, nargs='+', default=list(range(1, 8)),
                        choices=range(1, 8), metavar='N',
                        help='Casos a aplicar, p.ej. --casos 1 3 5 (default: todos)')
    parser.add_argument('--encoding', default='utf-8',
                        help='Encoding del CSV (default: utf-8). Usa latin-1 si hay problemas.')

    args = parser.parse_args()

    if args.salida is None:
        base = args.archivo.rsplit('.', 1)[0]
        args.salida = f"{base}_contaminado.csv"

    casos_activados = [f'caso{n}' for n in args.casos]

    try:
        contaminador = ContaminadorDataset(
            archivo_entrada=args.archivo,
            archivo_salida=args.salida,
            porcentaje_contaminacion=args.porcentaje,
            encoding=args.encoding,
        )
        contaminador.cargar_dataset()
        contaminador.contaminar_dataset(casos_activados=casos_activados)
        contaminador.guardar_dataset()
        contaminador.generar_reporte()

        print("\n✓ Proceso completado exitosamente!")
        print(f"  - Dataset original:    {args.archivo}")
        print(f"  - Dataset contaminado: {args.salida}")
        print(f"  - Reporte:             {args.salida.replace('.csv', '_reporte.json')}")

    except UnicodeDecodeError:
        print(f"\nError al leer el archivo: encoding incorrecto.")
        print(f"Prueba con --encoding latin-1")
        raise SystemExit(1)
    except FileNotFoundError:
        print(f"\nError: no se encontró el archivo '{args.archivo}'")
        raise SystemExit(1)


if __name__ == '__main__':
    main()
