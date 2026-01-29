"""
CASO 7: Limpieza de Formato
Introduce problemas de formato:
- Espacios extra en User_ID
- Caracteres especiales inesperados
- Formato inconsistente
"""

import random
import pandas as pd
from typing import Dict


def aplicar_caso7(df: pd.DataFrame, porcentaje_contaminacion: float, reporte_problemas: Dict) -> None:
    """
    Introduce problemas de formato.
    
    Args:
        df: DataFrame a contaminar
        porcentaje_contaminacion: Porcentaje de registros a contaminar
        reporte_problemas: Diccionario donde se guardarán los problemas introducidos
    """
    print("\n=== CASO 7: Limpieza de Formato ===")
    problemas_introducidos = []
    
    num_registros = len(df)
    num_contaminar = int(num_registros * porcentaje_contaminacion)
    indices = random.sample(range(num_registros), min(num_contaminar, num_registros))
    
    # User_ID: agregar espacios o caracteres extra
    for idx in indices[:num_contaminar//3]:
        user_id_original = df.at[idx, 'User_ID']
        # Introducir problemas de formato
        problemas_formato = [
            f" {user_id_original}",  # Espacio al inicio
            f"{user_id_original} ",  # Espacio al final
            f" {user_id_original} ",  # Espacios en ambos lados
            user_id_original.replace('-', ' - '),  # Espacios alrededor del guión
            user_id_original.replace('U-', 'U -'),  # Espacio después de U
        ]
        user_id_contaminado = random.choice(problemas_formato)
        df.at[idx, 'User_ID'] = user_id_contaminado
        problemas_introducidos.append({
            'indice': idx,
            'columna': 'User_ID',
            'valor_original': user_id_original,
            'valor_contaminado': user_id_contaminado,
            'problema': 'Espacios extra en formato'
        })
    
    # Primary_Platform: agregar caracteres especiales o espacios
    for idx in indices[num_contaminar//3:2*num_contaminar//3]:
        plataforma_original = df.at[idx, 'Primary_Platform']
        problemas_formato = [
            f"  {plataforma_original}  ",  # Múltiples espacios
            f"{plataforma_original}\t",  # Tab al final
            f"*{plataforma_original}*",  # Caracteres especiales
            f"[{plataforma_original}]",  # Corchetes
        ]
        plataforma_contaminada = random.choice(problemas_formato)
        df.at[idx, 'Primary_Platform'] = plataforma_contaminada
        problemas_introducidos.append({
            'indice': idx,
            'columna': 'Primary_Platform',
            'valor_original': plataforma_original,
            'valor_contaminado': plataforma_contaminada,
            'problema': 'Caracteres especiales o espacios extra'
        })
    
    # Gender: agregar caracteres invisibles o espacios
    for idx in indices[2*num_contaminar//3:]:
        gender_original = df.at[idx, 'Gender']
        problemas_formato = [
            f"  {gender_original}  ",
            f"\t{gender_original}\t",
            f"{gender_original}\n",
        ]
        gender_contaminado = random.choice(problemas_formato)
        df.at[idx, 'Gender'] = gender_contaminado
        problemas_introducidos.append({
            'indice': idx,
            'columna': 'Gender',
            'valor_original': gender_original,
            'valor_contaminado': repr(gender_contaminado),  # repr para ver caracteres especiales
            'problema': 'Caracteres de control o espacios extra'
        })
    
    reporte_problemas['caso7_formato'] = {
        'descripcion': 'Problemas de formato (espacios extra, caracteres especiales)',
        'total_problemas': len(problemas_introducidos),
        'problemas': problemas_introducidos[:20]
    }
    print(f"  ✓ Introducidos {len(problemas_introducidos)} problemas de formato")
