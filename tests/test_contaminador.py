import pandas as pd
import numpy as np
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from contaminar_dataset import ContaminadorDataset


@pytest.fixture
def df_mixto(tmp_path):
    """Dataset de prueba con todos los tipos de columnas."""
    csv = tmp_path / "test.csv"
    df = pd.DataFrame({
        'transaction_id': [f'TXN{i:05d}' for i in range(100)],  # ID (>80% únicos)
        'gender': ['Male', 'Female'] * 50,                        # categórica
        'stress_level': ['Low', 'Medium', 'High', 'Low', 'High'] * 20,  # categórica
        'age': range(18, 118),                                    # numérica
        'sleep_hours': [7.5] * 100,                               # horas
        'score': range(0, 100),                                   # numérica
        'addicted_label': [0, 1] * 50,                            # binaria
    })
    df.to_csv(csv, index=False)
    return str(csv)


# ── Detección de columnas ─────────────────────────────────────────────────────

def test_detectar_ids(df_mixto, tmp_path):
    c = ContaminadorDataset(df_mixto, str(tmp_path / "out.csv"))
    c.cargar_dataset()
    assert 'transaction_id' in c.columnas_detectadas['cols_ids']


def test_detectar_categoricas(df_mixto, tmp_path):
    c = ContaminadorDataset(df_mixto, str(tmp_path / "out.csv"))
    c.cargar_dataset()
    cats = c.columnas_detectadas['cols_categoricas']
    assert 'gender' in cats
    assert 'stress_level' in cats
    assert 'transaction_id' not in cats


def test_detectar_binarias(df_mixto, tmp_path):
    c = ContaminadorDataset(df_mixto, str(tmp_path / "out.csv"))
    c.cargar_dataset()
    assert 'addicted_label' in c.columnas_detectadas['cols_binarias']
    assert 'addicted_label' not in c.columnas_detectadas['cols_numericas']


def test_detectar_horas(df_mixto, tmp_path):
    c = ContaminadorDataset(df_mixto, str(tmp_path / "out.csv"))
    c.cargar_dataset()
    assert 'sleep_hours' in c.columnas_detectadas['cols_horas']
    assert 'sleep_hours' not in c.columnas_detectadas['cols_numericas']


def test_detectar_numericas(df_mixto, tmp_path):
    c = ContaminadorDataset(df_mixto, str(tmp_path / "out.csv"))
    c.cargar_dataset()
    nums = c.columnas_detectadas['cols_numericas']
    assert 'age' in nums
    assert 'score' in nums
    assert 'addicted_label' not in nums
    assert 'sleep_hours' not in nums


# ── Caso 1 ────────────────────────────────────────────────────────────────────

def test_caso1_contamina_categoricas(df_mixto, tmp_path):
    from casos.caso1 import aplicar_caso1
    df = pd.read_csv(df_mixto)
    reporte = {}
    cols_detectadas = {
        'cols_ids': ['transaction_id'],
        'cols_categoricas': ['gender', 'stress_level'],
        'cols_binarias': ['addicted_label'],
        'cols_horas': ['sleep_hours'],
        'cols_numericas': ['age', 'score'],
    }
    aplicar_caso1(df, 0.10, reporte, cols_detectadas)
    assert reporte['caso1_normalizacion_categorias']['total_problemas'] > 0


def test_caso1_sin_categoricas(tmp_path):
    from casos.caso1 import aplicar_caso1
    df = pd.DataFrame({'age': range(100), 'score': range(100)})
    reporte = {}
    cols_detectadas = {
        'cols_ids': [], 'cols_categoricas': [], 'cols_binarias': [],
        'cols_horas': [], 'cols_numericas': ['age', 'score'],
    }
    aplicar_caso1(df, 0.10, reporte, cols_detectadas)
    assert reporte['caso1_normalizacion_categorias']['total_problemas'] == 0


# ── Caso 2 ────────────────────────────────────────────────────────────────────

def test_caso2_contamina_horas_y_numericas(tmp_path):
    from casos.caso2 import aplicar_caso2
    df = pd.DataFrame({
        'age': [20] * 100,
        'sleep_hours': [7.5] * 100,
        'score': [50] * 100,
        'addicted_label': [0, 1] * 50,
    })
    reporte = {}
    cols_detectadas = {
        'cols_ids': [], 'cols_categoricas': [],
        'cols_binarias': ['addicted_label'],
        'cols_horas': ['sleep_hours'],
        'cols_numericas': ['age', 'score'],
    }
    aplicar_caso2(df, 0.20, reporte, cols_detectadas)
    assert reporte['caso2_validacion_rangos']['total_problemas'] > 0
    assert df['addicted_label'].isin([0, 1]).all()


# ── Caso 3 ────────────────────────────────────────────────────────────────────

def test_caso3_outliers_columnas_numericas(tmp_path):
    from casos.caso3 import aplicar_caso3
    rng = np.random.default_rng(42)
    df = pd.DataFrame({
        'score': rng.integers(0, 100, 200).astype(float),
        'sleep_hours': rng.uniform(4, 10, 200),
        'addicted_label': [0, 1] * 100,
    })
    reporte = {}
    cols_detectadas = {
        'cols_ids': [], 'cols_categoricas': [],
        'cols_binarias': ['addicted_label'],
        'cols_horas': ['sleep_hours'],
        'cols_numericas': ['score'],
    }
    aplicar_caso3(df, 0.10, reporte, cols_detectadas)
    assert reporte['caso3_outliers']['total_problemas'] > 0
    assert df['addicted_label'].isin([0, 1]).all()


# ── Caso 4 ────────────────────────────────────────────────────────────────────

def test_caso4_detecta_pares_por_prefijo():
    from casos.caso4 import _detectar_pares
    pares = _detectar_pares(
        ['gad_7_score', 'phq_9_score'],
        ['gad_7_severity', 'phq_9_severity', 'gender']
    )
    assert ('gad_7_score', 'gad_7_severity') in pares
    assert ('phq_9_score', 'phq_9_severity') in pares
    assert len(pares) == 2


def test_caso4_sin_pares_no_falla(tmp_path):
    from casos.caso4 import aplicar_caso4
    df = pd.DataFrame({'score': range(100), 'gender': ['M', 'F'] * 50})
    reporte = {}
    cols_detectadas = {
        'cols_ids': [], 'cols_categoricas': ['gender'],
        'cols_binarias': [], 'cols_horas': [], 'cols_numericas': ['score'],
    }
    aplicar_caso4(df, 0.10, reporte, cols_detectadas)
    assert reporte['caso4_consistencia']['total_problemas'] == 0


# ── Casos 5, 6, 7 ─────────────────────────────────────────────────────────────

def test_caso5_introduce_faltantes(df_mixto, tmp_path):
    from casos.caso5 import aplicar_caso5
    df = pd.read_csv(df_mixto)
    reporte = {}
    cols_detectadas = {
        'cols_ids': ['transaction_id'],
        'cols_categoricas': ['gender', 'stress_level'],
        'cols_binarias': ['addicted_label'],
        'cols_horas': ['sleep_hours'],
        'cols_numericas': ['age', 'score'],
    }
    aplicar_caso5(df, 0.10, reporte, cols_detectadas)
    assert reporte['caso5_valores_faltantes']['total_problemas'] > 0
    # IDs no deben tener faltantes
    assert df['transaction_id'].str.startswith('TXN').all()


def test_caso6_introduce_texto_en_numericas(df_mixto, tmp_path):
    from casos.caso6 import aplicar_caso6
    df = pd.read_csv(df_mixto)
    reporte = {}
    cols_detectadas = {
        'cols_ids': ['transaction_id'],
        'cols_categoricas': ['gender', 'stress_level'],
        'cols_binarias': ['addicted_label'],
        'cols_horas': ['sleep_hours'],
        'cols_numericas': ['age', 'score'],
    }
    aplicar_caso6(df, 0.10, reporte, cols_detectadas)
    assert reporte['caso6_tipos_datos']['total_problemas'] > 0
    # binarias no deben tocarse
    assert df['addicted_label'].astype(str).isin(['0', '1']).all()


def test_caso7_introduce_formato(df_mixto, tmp_path):
    from casos.caso7 import aplicar_caso7
    df = pd.read_csv(df_mixto)
    reporte = {}
    cols_detectadas = {
        'cols_ids': ['transaction_id'],
        'cols_categoricas': ['gender', 'stress_level'],
        'cols_binarias': ['addicted_label'],
        'cols_horas': ['sleep_hours'],
        'cols_numericas': ['age', 'score'],
    }
    aplicar_caso7(df, 0.10, reporte, cols_detectadas)
    assert reporte['caso7_formato']['total_problemas'] > 0


# ── CLI ───────────────────────────────────────────────────────────────────────

def test_cli_genera_archivos(df_mixto, tmp_path):
    import subprocess, json, os
    salida = str(tmp_path / "out.csv")
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    result = subprocess.run(
        ['python3', 'contaminar_dataset.py', df_mixto, '--salida', salida, '--porcentaje', '0.10'],
        capture_output=True, text=True, cwd=project_root
    )
    assert result.returncode == 0, result.stderr
    assert os.path.exists(salida)
    reporte = salida.replace('.csv', '_reporte.json')
    assert os.path.exists(reporte)
    with open(reporte) as f:
        data = json.load(f)
    assert 'caso1_normalizacion_categorias' in data


def test_cli_casos_especificos(df_mixto, tmp_path):
    import subprocess, json, os
    salida = str(tmp_path / "out2.csv")
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    result = subprocess.run(
        ['python3', 'contaminar_dataset.py', df_mixto, '--salida', salida, '--casos', '1', '5'],
        capture_output=True, text=True, cwd=project_root
    )
    assert result.returncode == 0, result.stderr
    reporte = salida.replace('.csv', '_reporte.json')
    with open(reporte) as f:
        data = json.load(f)
    assert 'caso1_normalizacion_categorias' in data
    assert 'caso2_validacion_rangos' not in data
