# -*- coding: utf-8 -*-
"""
Created on Fri May  9 06:33:26 2025

@author: kings
"""

# scripts/train_model.py
import os
import pandas as pd
import pickle
import sys
import logging
from datetime import datetime
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import mean_squared_error, accuracy_score, classification_report
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import xgboost as xgb
import numpy as np
from sklearn.model_selection import GridSearchCV

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import PROCESSED_DATA_DIR, MODEL_DIR, MODEL_PARAMS

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('model_training.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def load_training_data():
    """Load training data"""
    try:
        filepath = os.path.join(PROCESSED_DATA_DIR, 'train_data.csv')
        logger.info(f"Loading training data from {filepath}")
        return pd.read_csv(filepath)
    except Exception as e:
        logger.error(f"Error loading training data: {e}")
        return None

def prepare_features_and_target(data, target_column='JAMB_Score', threshold=200):
    """Prepare features and target variables"""
    # For regression model
    X = data.drop(columns=[target_column])
    y_reg = data[target_column]
    
    # For classification model (pass/fail based on threshold)
    y_cls = (data[target_column] >= threshold).astype(int)
    
    return X, y_reg, y_cls

def identify_categorical_columns(X):
    """Identify categorical columns in the dataset"""
    cat_columns = []
    for col in X.columns:
        if X[col].dtype == 'object' or pd.api.types.is_categorical_dtype(X[col]):
            cat_columns.append(col)
    return cat_columns

def train_regression_model(X, y):
    """Train regression model to predict exact JAMB score"""
    logger.info("Training regression model...")
    
    # Identify categorical columns
    categorical_columns = identify_categorical_columns(X)
    logger.info(f"Categorical columns detected: {categorical_columns}")
    
    # Get model params from config
    params = MODEL_PARAMS['random_forest']
    
    # Create preprocessing pipeline for categorical features
    if categorical_columns:
        preprocessor = ColumnTransformer(
            transformers=[
                ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical_columns)
            ],
            remainder='passthrough'
        )
        
        # Create pipeline with preprocessing and model
        model = Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('regressor', RandomForestRegressor(**params))
        ])
    else:
        # If no categorical columns, use model directly
        model = RandomForestRegressor(**params)
    
    # Train model
    model.fit(X, y)
    
    # Evaluate on training data
    y_pred = model.predict(X)
    mse = mean_squared_error(y, y_pred)
    rmse = np.sqrt(mse)
    logger.info(f"Training RMSE: {rmse:.4f}")
    
    # Feature importance (need to handle differently when using pipeline)
    if categorical_columns:
        # Get the trained regressor from the pipeline
        regressor = model.named_steps['regressor']
        
        # Get feature names after transformation
        ohe = model.named_steps['preprocessor'].transformers_[0][1]
        feature_names = list(ohe.get_feature_names_out(categorical_columns))
        # Add names of non-categorical columns
        feature_names.extend([col for col in X.columns if col not in categorical_columns])
        
        # Create feature importance DataFrame
        feature_importance = pd.DataFrame({
            'Feature': feature_names,
            'Importance': regressor.feature_importances_
        }).sort_values('Importance', ascending=False)
    else:
        feature_importance = pd.DataFrame({
            'Feature': X.columns,
            'Importance': model.feature_importances_
        }).sort_values('Importance', ascending=False)
    
    logger.info("Top 10 features by importance:")
    logger.info(feature_importance.head(10))
    
    return model, feature_importance

def train_classification_model(X, y):
    """Train classification model to predict pass/fail"""
    logger.info("Training classification model...")
    
    # Identify categorical columns
    categorical_columns = identify_categorical_columns(X)
    
    # Define preprocessing for categorical features
    if categorical_columns:
        preprocessor = ColumnTransformer(
            transformers=[
                ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical_columns)
            ],
            remainder='passthrough'
        )
    else:
        preprocessor = None
    
    # Use grid search to find best parameters
    param_grid = {
        'n_estimators': [50, 100],
        'max_depth': [5, 10, 15],
        'min_samples_split': [5, 10]
    }
    
    # Create the classifier
    classifier = RandomForestClassifier(random_state=42)
    
    # Create the pipeline
    if preprocessor:
        model = Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('classifier', classifier)
        ])
        
        # Adjust parameter grid to work with pipeline
        param_grid = {f'classifier__{param}': values for param, values in param_grid.items()}
    else:
        model = classifier
    
    # Grid search
    grid_search = GridSearchCV(
        estimator=model,
        param_grid=param_grid,
        cv=5,
        scoring='accuracy',
        verbose=1
    )
    
    grid_search.fit(X, y)
    
    # Get best model
    best_model = grid_search.best_estimator_
    logger.info(f"Best parameters: {grid_search.best_params_}")
    
    # Evaluate on training data
    y_pred = best_model.predict(X)
    accuracy = accuracy_score(y, y_pred)
    logger.info(f"Training accuracy: {accuracy:.4f}")
    
    # Classification report
    report = classification_report(y, y_pred)
    logger.info(f"Classification report:\n{report}")
    
    return best_model

def train_xgboost_model(X, y_reg):
    """Train XGBoost regression model"""
    logger.info("Training XGBoost model...")
    
    # Identify categorical columns
    categorical_columns = identify_categorical_columns(X)
    
    # Get model params from config
    params = MODEL_PARAMS['xgboost']
    
    # Create preprocessing pipeline for categorical features
    if categorical_columns:
        preprocessor = ColumnTransformer(
            transformers=[
                ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical_columns)
            ],
            remainder='passthrough'
        )
        
        # Create pipeline with preprocessing and model
        model = Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('xgboost', xgb.XGBRegressor(**params))
        ])
    else:
        # If no categorical columns, use model directly
        model = xgb.XGBRegressor(**params)
    
    # Train model
    model.fit(X, y_reg)
    
    # Evaluate on training data
    y_pred = model.predict(X)
    mse = mean_squared_error(y_reg, y_pred)
    rmse = np.sqrt(mse)
    logger.info(f"XGBoost training RMSE: {rmse:.4f}")
    
    return model

def save_model(model, model_name):
    """Save model to disk"""
    model_path = os.path.join(MODEL_DIR, f"{model_name}.pkl")
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    logger.info(f"Model saved to {model_path}")
    return model_path

def main():
    """Main function for model training"""
    # Record execution start time
    start_time = datetime.now()
    logger.info(f"Model training started at: {start_time}")
    
    # Load training data
    train_data = load_training_data()
    
    if train_data is not None:
        # Prepare features and targets
        X, y_reg, y_cls = prepare_features_and_target(train_data)
        
        # Train regression model
        reg_model, feature_importance = train_regression_model(X, y_reg)
        save_model(reg_model, "jamb_score_regressor")
        
        # Save feature importance
        importance_path = os.path.join(MODEL_DIR, "feature_importance.csv")
        feature_importance.to_csv(importance_path, index=False)
        logger.info(f"Feature importance saved to {importance_path}")
        
        # Train classification model
        cls_model = train_classification_model(X, y_cls)
        save_model(cls_model, "jamb_pass_classifier")
        
        # Train XGBoost model
        xgb_model = train_xgboost_model(X, y_reg)
        save_model(xgb_model, "jamb_xgb_regressor")
    
    # Record execution end time
    end_time = datetime.now()
    execution_time = end_time - start_time
    logger.info(f"Model training completed at: {end_time}")
    logger.info(f"Total execution time: {execution_time}")

if __name__ == "__main__":
    main()