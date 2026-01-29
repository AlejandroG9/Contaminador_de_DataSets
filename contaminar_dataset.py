"""
Script para introducir intencionalmente problemas de calidad de datos en un dataset.
Propósito: Ejemplificar los 7 casos de uso para limpieza de datos durante clases.

Autor: Script educativo para Ingeniería de la Información
Fecha: 2024
"""

import pandas as pd
import numpy as np
import random
from typing import Dict, List, Tuple
import json


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
    # CASO 1: NORMALIZACIÓN DE CATEGORÍAS
    # ============================================================================
    
    def caso1_normalizacion_categorias(self):
        """
        Introduce problemas de normalización en columnas categóricas:
        - Variaciones de mayúsculas/minúsculas
        - Espacios extra al inicio/final
        - Variaciones en guiones y espacios
        """
        print("\n=== CASO 1: Normalización de Categorías ===")
        problemas_introducidos = []
        
        # Configuración de problemas por columna
        configuracion = {
            'Gender': {
                'variaciones': ['male', 'MALE', 'female', 'FEMALE', ' Male', 'Female ', '  Male  '],
                'descripcion': 'Variaciones de mayúsculas/minúsculas y espacios en Gender'
            },
            'User_Archetype': {
                'variaciones': ['hyper-connected', 'HYPER-CONNECTED', 'Hyper Connected', 'hyper connected', ' Average User'],
                'descripcion': 'Variaciones de formato en User_Archetype'
            },
            'Primary_Platform': {
                'variaciones': ['facebook', 'FACEBOOK', 'twitter', 'Twitter', ' YouTube ', 'instagram'],
                'descripcion': 'Variaciones de mayúsculas y espacios en Primary_Platform'
            },
            'Dominant_Content_Type': {
                'variaciones': ['gaming', 'GAMING', 'Educational-Tech', 'Educational Tech', ' Entertainment/Comedy '],
                'descripcion': 'Variaciones de formato en Dominant_Content_Type'
            },
            'Activity_Type': {
                'variaciones': ['active', 'ACTIVE', ' passive', 'Passive '],
                'descripcion': 'Variaciones de mayúsculas y espacios en Activity_Type'
            },
            'GAD_7_Severity': {
                'variaciones': ['minimal', 'MILD', 'moderate', ' severe', 'Severe '],
                'descripcion': 'Variaciones de mayúsculas y espacios en GAD_7_Severity'
            },
            'PHQ_9_Severity': {
                'variaciones': ['mild', 'MODERATE', 'none-minimal', 'None Minimal', ' Moderately Severe '],
                'descripcion': 'Variaciones de formato en PHQ_9_Severity'
            }
        }
        
        num_registros = len(self.df)
        num_contaminar = int(num_registros * self.porcentaje_contaminacion)
        
        for columna, config in configuracion.items():
            if columna not in self.df.columns:
                continue
                
            # Seleccionar registros aleatorios para contaminar
            indices = random.sample(range(num_registros), min(num_contaminar, num_registros))
            
            for idx in indices:
                valor_original = self.df.at[idx, columna]
                valor_contaminado = random.choice(config['variaciones'])
                self.df.at[idx, columna] = valor_contaminado
                problemas_introducidos.append({
                    'indice': idx,
                    'columna': columna,
                    'valor_original': valor_original,
                    'valor_contaminado': valor_contaminado
                })
        
        self.reporte_problemas['caso1_normalizacion_categorias'] = {
            'descripcion': 'Problemas de normalización en categorías (mayúsculas, espacios, guiones)',
            'total_problemas': len(problemas_introducidos),
            'problemas': problemas_introducidos[:20]  # Guardar solo los primeros 20 para el reporte
        }
        print(f"  ✓ Introducidos {len(problemas_introducidos)} problemas de normalización")
        
    # ============================================================================
    # CASO 2: VALIDACIÓN DE RANGOS NUMÉRICOS
    # ============================================================================
    
    def caso2_validacion_rangos_numericos(self):
        """
        Introduce valores fuera de rango en columnas numéricas:
        - Edades fuera del rango 18-22
        - Tiempo de pantalla > 24 horas
        - Scores fuera de rangos válidos
        - Valores negativos donde no aplican
        """
        print("\n=== CASO 2: Validación de Rangos Numéricos ===")
        problemas_introducidos = []
        
        num_registros = len(self.df)
        num_contaminar = int(num_registros * self.porcentaje_contaminacion)
        indices = random.sample(range(num_registros), min(num_contaminar, num_registros))
        
        # Age: valores fuera de rango 18-22
        for idx in indices[:num_contaminar//4]:
            valor_contaminado = random.choice([0, 15, 17, 23, 25, 30, 100])
            valor_original = self.df.at[idx, 'Age']
            self.df.at[idx, 'Age'] = valor_contaminado
            problemas_introducidos.append({
                'indice': idx,
                'columna': 'Age',
                'valor_original': valor_original,
                'valor_contaminado': valor_contaminado,
                'problema': 'Valor fuera de rango válido (18-22)'
            })
        
        # Daily_Screen_Time_Hours: valores > 24 o negativos
        for idx in indices[num_contaminar//4:num_contaminar//2]:
            valor_contaminado = random.choice([-5.5, 25.0, 30.5, 48.0])
            valor_original = self.df.at[idx, 'Daily_Screen_Time_Hours']
            self.df.at[idx, 'Daily_Screen_Time_Hours'] = valor_contaminado
            problemas_introducidos.append({
                'indice': idx,
                'columna': 'Daily_Screen_Time_Hours',
                'valor_original': valor_original,
                'valor_contaminado': valor_contaminado,
                'problema': 'Valor fuera de rango lógico (>24 horas o negativo)'
            })
        
        # GAD_7_Score: valores fuera de rango 0-21
        for idx in indices[num_contaminar//2:3*num_contaminar//4]:
            valor_contaminado = random.choice([-1, 22, 25, 30])
            valor_original = self.df.at[idx, 'GAD_7_Score']
            self.df.at[idx, 'GAD_7_Score'] = valor_contaminado
            problemas_introducidos.append({
                'indice': idx,
                'columna': 'GAD_7_Score',
                'valor_original': valor_original,
                'valor_contaminado': valor_contaminado,
                'problema': 'Valor fuera de rango válido (0-21)'
            })
        
        # PHQ_9_Score: valores fuera de rango 0-27
        for idx in indices[3*num_contaminar//4:]:
            valor_contaminado = random.choice([-2, 28, 30, 35])
            valor_original = self.df.at[idx, 'PHQ_9_Score']
            self.df.at[idx, 'PHQ_9_Score'] = valor_contaminado
            problemas_introducidos.append({
                'indice': idx,
                'columna': 'PHQ_9_Score',
                'valor_original': valor_original,
                'valor_contaminado': valor_contaminado,
                'problema': 'Valor fuera de rango válido (0-27)'
            })
        
        self.reporte_problemas['caso2_validacion_rangos'] = {
            'descripcion': 'Valores numéricos fuera de rangos válidos o lógicos',
            'total_problemas': len(problemas_introducidos),
            'problemas': problemas_introducidos[:20]
        }
        print(f"  ✓ Introducidos {len(problemas_introducidos)} valores fuera de rango")
        
    # ============================================================================
    # CASO 3: DETECCIÓN DE OUTLIERS
    # ============================================================================
    
    def caso3_deteccion_outliers(self):
        """
        Introduce outliers estadísticamente extremos pero técnicamente válidos:
        - Tiempos de pantalla muy altos (pero < 24 horas)
        - Duraciones de sueño extremas (pero dentro de límites físicos)
        """
        print("\n=== CASO 3: Detección de Outliers ===")
        problemas_introducidos = []
        
        num_registros = len(self.df)
        num_contaminar = int(num_registros * self.porcentaje_contaminacion)
        indices = random.sample(range(num_registros), min(num_contaminar, num_registros))
        
        # Calcular estadísticas para identificar outliers
        screen_time_mean = self.df['Daily_Screen_Time_Hours'].mean()
        screen_time_std = self.df['Daily_Screen_Time_Hours'].std()
        sleep_mean = self.df['Sleep_Duration_Hours'].mean()
        sleep_std = self.df['Sleep_Duration_Hours'].std()
        
        # Daily_Screen_Time_Hours: valores extremadamente altos (pero < 24)
        for idx in indices[:num_contaminar//2]:
            # Valores > 3 desviaciones estándar pero < 24 horas
            valor_contaminado = min(23.5, screen_time_mean + random.uniform(3.5, 5) * screen_time_std)
            valor_original = self.df.at[idx, 'Daily_Screen_Time_Hours']
            self.df.at[idx, 'Daily_Screen_Time_Hours'] = round(valor_contaminado, 2)
            problemas_introducidos.append({
                'indice': idx,
                'columna': 'Daily_Screen_Time_Hours',
                'valor_original': round(valor_original, 2),
                'valor_contaminado': round(valor_contaminado, 2),
                'problema': 'Outlier estadístico (valor extremo pero técnicamente válido)'
            })
        
        # Sleep_Duration_Hours: valores extremos
        for idx in indices[num_contaminar//2:]:
            # Valores muy altos o muy bajos pero físicamente posibles
            if random.random() > 0.5:
                valor_contaminado = min(12.0, sleep_mean + random.uniform(3, 4) * sleep_std)
            else:
                valor_contaminado = max(1.5, sleep_mean - random.uniform(3, 4) * sleep_std)
            valor_original = self.df.at[idx, 'Sleep_Duration_Hours']
            self.df.at[idx, 'Sleep_Duration_Hours'] = round(valor_contaminado, 2)
            problemas_introducidos.append({
                'indice': idx,
                'columna': 'Sleep_Duration_Hours',
                'valor_original': round(valor_original, 2),
                'valor_contaminado': round(valor_contaminado, 2),
                'problema': 'Outlier estadístico (valor extremo pero técnicamente válido)'
            })
        
        self.reporte_problemas['caso3_outliers'] = {
            'descripcion': 'Outliers estadísticamente extremos pero técnicamente válidos',
            'total_problemas': len(problemas_introducidos),
            'problemas': problemas_introducidos[:20]
        }
        print(f"  ✓ Introducidos {len(problemas_introducidos)} outliers")
        
    # ============================================================================
    # CASO 4: VALIDACIÓN DE CONSISTENCIA ENTRE COLUMNAS
    # ============================================================================
    
    def caso4_validacion_consistencia_columnas(self):
        """
        Introduce inconsistencias entre columnas relacionadas:
        - GAD_7_Score vs GAD_7_Severity
        - PHQ_9_Score vs PHQ_9_Severity
        """
        print("\n=== CASO 4: Validación de Consistencia entre Columnas ===")
        problemas_introducidos = []
        
        num_registros = len(self.df)
        num_contaminar = int(num_registros * self.porcentaje_contaminacion)
        indices = random.sample(range(num_registros), min(num_contaminar, num_registros))
        
        # Mapeo de scores a severidades esperadas
        def get_gad_severity(score):
            if score <= 4:
                return 'Minimal'
            elif score <= 9:
                return 'Mild'
            elif score <= 14:
                return 'Moderate'
            else:
                return 'Severe'
        
        def get_phq_severity(score):
            if score <= 4:
                return 'None-Minimal'
            elif score <= 9:
                return 'Mild'
            elif score <= 14:
                return 'Moderate'
            elif score <= 19:
                return 'Moderately Severe'
            else:
                return 'Severe'
        
        # GAD_7: Cambiar severidad a una incorrecta
        for idx in indices[:num_contaminar//2]:
            score = int(self.df.at[idx, 'GAD_7_Score'])
            severidad_correcta = get_gad_severity(score)
            severidades_incorrectas = [s for s in ['Minimal', 'Mild', 'Moderate', 'Severe'] if s != severidad_correcta]
            severidad_contaminada = random.choice(severidades_incorrectas)
            
            valor_original = self.df.at[idx, 'GAD_7_Severity']
            self.df.at[idx, 'GAD_7_Severity'] = severidad_contaminada
            problemas_introducidos.append({
                'indice': idx,
                'columna': 'GAD_7_Severity',
                'score': score,
                'severidad_correcta': severidad_correcta,
                'severidad_contaminada': severidad_contaminada,
                'problema': f'Inconsistencia: Score {score} debería ser {severidad_correcta}, pero es {severidad_contaminada}'
            })
        
        # PHQ_9: Cambiar severidad a una incorrecta
        for idx in indices[num_contaminar//2:]:
            score = int(self.df.at[idx, 'PHQ_9_Score'])
            severidad_correcta = get_phq_severity(score)
            severidades_incorrectas = [s for s in ['None-Minimal', 'Mild', 'Moderate', 'Moderately Severe', 'Severe'] if s != severidad_correcta]
            severidad_contaminada = random.choice(severidades_incorrectas)
            
            valor_original = self.df.at[idx, 'PHQ_9_Severity']
            self.df.at[idx, 'PHQ_9_Severity'] = severidad_contaminada
            problemas_introducidos.append({
                'indice': idx,
                'columna': 'PHQ_9_Severity',
                'score': score,
                'severidad_correcta': severidad_correcta,
                'severidad_contaminada': severidad_contaminada,
                'problema': f'Inconsistencia: Score {score} debería ser {severidad_correcta}, pero es {severidad_contaminada}'
            })
        
        self.reporte_problemas['caso4_consistencia'] = {
            'descripcion': 'Inconsistencias entre scores y severidades',
            'total_problemas': len(problemas_introducidos),
            'problemas': problemas_introducidos[:20]
        }
        print(f"  ✓ Introducidas {len(problemas_introducidos)} inconsistencias entre columnas")
        
    # ============================================================================
    # CASO 5: MANEJO DE VALORES FALTANTES
    # ============================================================================
    
    def caso5_manejo_valores_faltantes(self):
        """
        Introduce valores faltantes de diferentes formas:
        - Celdas vacías
        - Valores como "N/A", "NULL", "NaN", etc.
        """
        print("\n=== CASO 5: Manejo de Valores Faltantes ===")
        problemas_introducidos = []
        
        num_registros = len(self.df)
        num_contaminar = int(num_registros * self.porcentaje_contaminacion)
        
        # Valores faltantes comunes
        valores_faltantes = ['', 'N/A', 'NULL', 'NaN', 'null', 'na', 'N/A', '?', '-']
        
        # Seleccionar columnas para introducir valores faltantes
        columnas_objetivo = ['Age', 'Gender', 'Primary_Platform', 'Daily_Screen_Time_Hours', 
                            'Sleep_Duration_Hours', 'GAD_7_Score', 'PHQ_9_Score']
        
        for columna in columnas_objetivo:
            if columna not in self.df.columns:
                continue
                
            indices = random.sample(range(num_registros), min(num_contaminar//len(columnas_objetivo), num_registros))
            
            for idx in indices:
                valor_original = self.df.at[idx, columna]
                valor_faltante = random.choice(valores_faltantes)
                self.df.at[idx, columna] = valor_faltante
                problemas_introducidos.append({
                    'indice': idx,
                    'columna': columna,
                    'valor_original': valor_original,
                    'valor_faltante': valor_faltante,
                    'problema': f'Valor faltante representado como: {valor_faltante}'
                })
        
        self.reporte_problemas['caso5_valores_faltantes'] = {
            'descripcion': 'Valores faltantes (vacíos, N/A, NULL, etc.)',
            'total_problemas': len(problemas_introducidos),
            'problemas': problemas_introducidos[:20]
        }
        print(f"  ✓ Introducidos {len(problemas_introducidos)} valores faltantes")
        
    # ============================================================================
    # CASO 6: NORMALIZACIÓN DE TIPOS DE DATOS
    # ============================================================================
    
    def caso6_normalizacion_tipos_datos(self):
        """
        Introduce valores que deberían ser numéricos pero están como texto:
        - Números escritos en palabras
        - Números con formato incorrecto
        - Texto en lugar de números
        """
        print("\n=== CASO 6: Normalización de Tipos de Datos ===")
        problemas_introducidos = []
        
        num_registros = len(self.df)
        num_contaminar = int(num_registros * self.porcentaje_contaminacion)
        
        # Mapeo de números a palabras (en español e inglés)
        numeros_palabras = {
            'Age': ['dieciocho', 'veinte', 'veintiuno', 'eighteen', 'twenty', 'twenty-one'],
            'Daily_Screen_Time_Hours': ['ocho punto cinco', 'cinco horas', '8.5 horas', 'five hours'],
            'Sleep_Duration_Hours': ['siete horas', 'seis punto dos', '7 hrs', 'six hours'],
            'GAD_7_Score': ['nueve', 'cinco', 'cero', 'nine', 'five', 'zero'],
            'PHQ_9_Score': ['doce', 'siete', 'tres', 'twelve', 'seven', 'three'],
            'Late_Night_Usage': ['sí', 'no', 'yes', 'no', 'true', 'false'],
            'Social_Comparison_Trigger': ['sí', 'no', 'yes', 'no', 'true', 'false']
        }
        
        for columna, valores_texto in numeros_palabras.items():
            if columna not in self.df.columns:
                continue
                
            indices = random.sample(range(num_registros), min(num_contaminar//len(numeros_palabras), num_registros))
            
            for idx in indices:
                valor_original = self.df.at[idx, columna]
                valor_texto = random.choice(valores_texto)
                self.df.at[idx, columna] = valor_texto
                problemas_introducidos.append({
                    'indice': idx,
                    'columna': columna,
                    'valor_original': valor_original,
                    'valor_texto': valor_texto,
                    'problema': f'Valor numérico representado como texto: {valor_texto}'
                })
        
        self.reporte_problemas['caso6_tipos_datos'] = {
            'descripcion': 'Valores numéricos representados como texto',
            'total_problemas': len(problemas_introducidos),
            'problemas': problemas_introducidos[:20]
        }
        print(f"  ✓ Introducidos {len(problemas_introducidos)} valores numéricos como texto")
        
    # ============================================================================
    # CASO 7: LIMPIEZA DE FORMATO
    # ============================================================================
    
    def caso7_limpieza_formato(self):
        """
        Introduce problemas de formato:
        - Espacios extra en User_ID
        - Caracteres especiales inesperados
        - Formato inconsistente
        """
        print("\n=== CASO 7: Limpieza de Formato ===")
        problemas_introducidos = []
        
        num_registros = len(self.df)
        num_contaminar = int(num_registros * self.porcentaje_contaminacion)
        indices = random.sample(range(num_registros), min(num_contaminar, num_registros))
        
        # User_ID: agregar espacios o caracteres extra
        for idx in indices[:num_contaminar//3]:
            user_id_original = self.df.at[idx, 'User_ID']
            # Introducir problemas de formato
            problemas_formato = [
                f" {user_id_original}",  # Espacio al inicio
                f"{user_id_original} ",  # Espacio al final
                f" {user_id_original} ",  # Espacios en ambos lados
                user_id_original.replace('-', ' - '),  # Espacios alrededor del guión
                user_id_original.replace('U-', 'U -'),  # Espacio después de U
            ]
            user_id_contaminado = random.choice(problemas_formato)
            self.df.at[idx, 'User_ID'] = user_id_contaminado
            problemas_introducidos.append({
                'indice': idx,
                'columna': 'User_ID',
                'valor_original': user_id_original,
                'valor_contaminado': user_id_contaminado,
                'problema': 'Espacios extra en formato'
            })
        
        # Primary_Platform: agregar caracteres especiales o espacios
        for idx in indices[num_contaminar//3:2*num_contaminar//3]:
            plataforma_original = self.df.at[idx, 'Primary_Platform']
            problemas_formato = [
                f"  {plataforma_original}  ",  # Múltiples espacios
                f"{plataforma_original}\t",  # Tab al final
                f"*{plataforma_original}*",  # Caracteres especiales
                f"[{plataforma_original}]",  # Corchetes
            ]
            plataforma_contaminada = random.choice(problemas_formato)
            self.df.at[idx, 'Primary_Platform'] = plataforma_contaminada
            problemas_introducidos.append({
                'indice': idx,
                'columna': 'Primary_Platform',
                'valor_original': plataforma_original,
                'valor_contaminado': plataforma_contaminada,
                'problema': 'Caracteres especiales o espacios extra'
            })
        
        # Gender: agregar caracteres invisibles o espacios
        for idx in indices[2*num_contaminar//3:]:
            gender_original = self.df.at[idx, 'Gender']
            problemas_formato = [
                f"  {gender_original}  ",
                f"\t{gender_original}\t",
                f"{gender_original}\n",
            ]
            gender_contaminado = random.choice(problemas_formato)
            self.df.at[idx, 'Gender'] = gender_contaminado
            problemas_introducidos.append({
                'indice': idx,
                'columna': 'Gender',
                'valor_original': gender_original,
                'valor_contaminado': repr(gender_contaminado),  # repr para ver caracteres especiales
                'problema': 'Caracteres de control o espacios extra'
            })
        
        self.reporte_problemas['caso7_formato'] = {
            'descripcion': 'Problemas de formato (espacios extra, caracteres especiales)',
            'total_problemas': len(problemas_introducidos),
            'problemas': problemas_introducidos[:20]
        }
        print(f"  ✓ Introducidos {len(problemas_introducidos)} problemas de formato")
        
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
        
        if 'caso1' in casos_activados:
            self.caso1_normalizacion_categorias()
        if 'caso2' in casos_activados:
            self.caso2_validacion_rangos_numericos()
        if 'caso3' in casos_activados:
            self.caso3_deteccion_outliers()
        if 'caso4' in casos_activados:
            self.caso4_validacion_consistencia_columnas()
        if 'caso5' in casos_activados:
            self.caso5_manejo_valores_faltantes()
        if 'caso6' in casos_activados:
            self.caso6_normalizacion_tipos_datos()
        if 'caso7' in casos_activados:
            self.caso7_limpieza_formato()
        
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
