"""
CASO 6: Normalización de Tipos de Datos
Introduce valores que deberían ser numéricos pero están como texto:
- Números escritos en palabras
- Números con formato incorrecto
- Texto en lugar de números
"""

import random
import pandas as pd
from typing import Dict


def aplicar_caso6(df: pd.DataFrame, porcentaje_contaminacion: float, reporte_problemas: Dict) -> None:
    """
    Introduce valores que deberían ser numéricos pero están como texto.
    
    Args:
        df: DataFrame a contaminar
        porcentaje_contaminacion: Porcentaje de registros a contaminar
        reporte_problemas: Diccionario donde se guardarán los problemas introducidos
    """
    print("\n=== CASO 6: Normalización de Tipos de Datos ===")
    problemas_introducidos = []
    
    num_registros = len(df)
    num_contaminar = int(num_registros * porcentaje_contaminacion)
    
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
        if columna not in df.columns:
            continue
            
        indices = random.sample(range(num_registros), min(num_contaminar//len(numeros_palabras), num_registros))
        
        for idx in indices:
            valor_original = df.at[idx, columna]
            valor_texto = random.choice(valores_texto)
            df.at[idx, columna] = valor_texto
            problemas_introducidos.append({
                'indice': idx,
                'columna': columna,
                'valor_original': valor_original,
                'valor_texto': valor_texto,
                'problema': f'Valor numérico representado como texto: {valor_texto}'
            })
    
    reporte_problemas['caso6_tipos_datos'] = {
        'descripcion': 'Valores numéricos representados como texto',
        'total_problemas': len(problemas_introducidos),
        'problemas': problemas_introducidos[:20]
    }
    print(f"  ✓ Introducidos {len(problemas_introducidos)} valores numéricos como texto")
