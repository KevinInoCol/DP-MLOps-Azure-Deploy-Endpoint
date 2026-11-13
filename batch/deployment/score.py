"""
Scoring script para batch deployment con environment custom.

Carga el modelo MLflow desde AZUREML_MODEL_DIR y procesa cada mini-batch.
"""

import os
import logging
from pathlib import Path

import mlflow
import pandas as pd

logger = logging.getLogger(__name__)


def init():
    global model
    model_dir = os.environ.get("AZUREML_MODEL_DIR")
    logger.info(f"AZUREML_MODEL_DIR={model_dir}")

    candidates = [
        Path(model_dir) / "mlflow-model",
        Path(model_dir) / "Modelo_Salud_Ensemble_V1" / "mlflow-model",
        Path(model_dir),
    ]
    for c in candidates:
        if (c / "MLmodel").exists():
            logger.info(f"Cargando modelo MLflow desde: {c}")
            model = mlflow.pyfunc.load_model(str(c))
            return

    raise FileNotFoundError(
        f"No se encontró el archivo MLmodel en ninguno de: {candidates}"
    )


def run(mini_batch):
    if isinstance(mini_batch, pd.DataFrame):
        df = mini_batch
    else:
        dfs = [pd.read_csv(p) for p in mini_batch]
        df = pd.concat(dfs, ignore_index=True)

    logger.info(f"Inferencia sobre {len(df)} filas, columnas={list(df.columns)}")
    preds = model.predict(df)

    df_out = df.copy()
    df_out["prediction"] = preds
    return df_out
