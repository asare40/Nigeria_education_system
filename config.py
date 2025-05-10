# -*- coding: utf-8 -*-
"""
Created on Fri May  9 05:01:55 2025

@author: kings
"""

# config.py
import os
from datetime import datetime

# Project metadata
PROJECT_NAME = "Nigerian Educational Analytics Project"
PROJECT_CREATION_DATE = "2025-05-09 04:32:28"
CURRENT_VERSION = "1.0.0"

# Data paths
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")
MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")

# Ensure directories exist
for directory in [RAW_DATA_DIR, PROCESSED_DATA_DIR, MODEL_DIR]:
    os.makedirs(directory, exist_ok=True)

# Database configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "database": os.getenv("DB_NAME", "edu_analytics"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "password")
}

# Model parameters
MODEL_PARAMS = {
    "random_forest": {
        "n_estimators": 100,
        "max_depth": 15,
        "min_samples_split": 10,
        "random_state": 42
    },
    "xgboost": {
        "n_estimators": 100,
        "max_depth": 7,
        "learning_rate": 0.1,
        "subsample": 0.8,
        "random_state": 42
    }
}