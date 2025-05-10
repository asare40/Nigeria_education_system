
"""
Created on Fri May  9 06:33:42 2025

@author: kings
"""

# scripts/evaluate_model.py
import os
import pandas as pd
import pickle
import sys
import logging
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    mean_squared_error, accuracy_score, 
    classification_report, confusion_matrix,
    roc_curve, auc, precision_recall_curve
)
import numpy as np
import shap

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import PROCESSED_DATA_DIR, MODEL_DIR

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('model_evaluation.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def load_test_data():
    """Load test data"""
    try:
        filepath = os.path.join(PROCESSED_DATA_DIR, 'test_data.csv')
        logger.info(f"Loading test data from {filepath}")
        return pd.read_csv(filepath)
    except Exception as e:
        logger.error(f"Error loading test data: {e}")
        return None

def load_model(model_name):
    """Load model from disk"""
    model_path = os.path.join(MODEL_DIR, f"{model_name}.pkl")
    try:
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        logger.info(f"Model loaded from {model_path}")
        return model
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        return None

def prepare_features_and_target(data, target_column='JAMB_Score', threshold=200):
    """Prepare features and target variables"""
    # For regression model
    X = data.drop(columns=[target_column])
    y_reg = data[target_column]
    
    # For classification model (pass/fail based on threshold)
    y_cls = (data[target_column] >= threshold).astype(int)
    
    return X, y_reg, y_cls

def evaluate_regression_model(model, X, y, model_name="Regression Model"):
    """Evaluate regression model"""
    logger.info(f"Evaluating {model_name}...")
    
    # Make predictions
    y_pred = model.predict(X)
    
    # Calculate metrics
    mse = mean_squared_error(y, y_pred)
    rmse = np.sqrt(mse)
    mae = np.mean(np.abs(y - y_pred))
    r2 = 1 - np.sum((y - y_pred) ** 2) / np.sum((y - np.mean(y)) ** 2)
    
    logger.info(f"{model_name} metrics:")
    logger.info(f"  RMSE: {rmse:.2f}")
    logger.info(f"  MAE: {mae:.2f}")
    logger.info(f"  R²: {r2:.4f}")
    
    # Create scatter plot of actual vs predicted
    plt.figure(figsize=(10, 6))
    plt.scatter(y, y_pred, alpha=0.5)
    plt.plot([y.min(), y.max()], [y.min(), y.max()], 'r--')
    plt.xlabel('Actual JAMB Score')
    plt.ylabel('Predicted JAMB Score')
    plt.title(f'{model_name}: Actual vs Predicted JAMB Scores')
    
    # Save plot
    plot_path = os.path.join(MODEL_DIR, f"{model_name.replace(' ', '_').lower()}_scatter_plot.png")
    plt.savefig(plot_path)
    plt.close()
    logger.info(f"Scatter plot saved to {plot_path}")
    
    # Return metrics as dictionary
    return {
        'rmse': rmse,
        'mae': mae,
        'r2': r2
    }

def evaluate_classification_model(model, X, y, model_name="Classification Model"):
    """Evaluate classification model"""
    logger.info(f"Evaluating {model_name}...")
    
    # Make predictions
    y_pred = model.predict(X)
    y_prob = model.predict_proba(X)[:, 1]  # Probability of class 1 (pass)
    
    # Calculate metrics
    accuracy = accuracy_score(y, y_pred)
    report = classification_report(y, y_pred)
    cm = confusion_matrix(y, y_pred)
    
    logger.info(f"{model_name} accuracy: {accuracy:.4f}")
    logger.info(f"Classification report:\n{report}")
    
    # Create confusion matrix plot
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=['Fail', 'Pass'], yticklabels=['Fail', 'Pass'])
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.title(f'{model_name}: Confusion Matrix')
    
    # Save confusion matrix plot
    cm_path = os.path.join(MODEL_DIR, f"{model_name.replace(' ', '_').lower()}_confusion_matrix.png")
    plt.savefig(cm_path)
    plt.close()
    logger.info(f"Confusion matrix saved to {cm_path}")
    
    # Create ROC curve
    fpr, tpr, _ = roc_curve(y, y_prob)
    roc_auc = auc(fpr, tpr)
    
    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, label=f'AUC = {roc_auc:.4f}')
    plt.plot([0, 1], [0, 1], 'k--')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title(f'{model_name}: ROC Curve')
    plt.legend(loc='lower right')
    
    # Save ROC curve plot
    roc_path = os.path.join(MODEL_DIR, f"{model_name.replace(' ', '_').lower()}_roc_curve.png")
    plt.savefig(roc_path)
    plt.close()
    logger.info(f"ROC curve saved to {roc_path}")
    
    # Return metrics as dictionary
    return {
        'accuracy': accuracy,
        'report': report,
        'auc': roc_auc
    }

def generate_shap_analysis(model, X, model_name="Model"):
    """Generate SHAP analysis for model interpretability"""
    logger.info(f"Generating SHAP analysis for {model_name}...")
    
    # Take a sample of data for SHAP analysis if dataset is large
    X_sample = X.sample(min(len(X), 100), random_state=42)
    
    try:
        # Create explainer
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_sample)
        
        # Summary plot
        plt.figure(figsize=(12, 8))
        shap.summary_plot(shap_values, X_sample, show=False)
        plt.title(f'{model_name}: SHAP Feature Importance')
        
        # Save SHAP summary plot
        shap_path = os.path.join(MODEL_DIR, f"{model_name.replace(' ', '_').lower()}_shap_summary.png")
        plt.savefig(shap_path)
        plt.close()
        logger.info(f"SHAP summary plot saved to {shap_path}")
        
        # SHAP dependence plots for top features
        feature_importance = np.mean(np.abs(shap_values), axis=0)
        top_indices = np.argsort(-feature_importance)[:3]  # Top 3 features
        
        for i in top_indices:
            feature_name = X.columns[i]
            plt.figure(figsize=(10, 6))
            shap.dependence_plot(i, shap_values, X_sample, show=False)
            plt.title(f'{model_name}: SHAP Dependence Plot for {feature_name}')
            
            # Save dependence plot
            dep_path = os.path.join(MODEL_DIR, f"{model_name.replace(' ', '_').lower()}_shap_{feature_name}.png")
            plt.savefig(dep_path)
            plt.close()
            logger.info(f"SHAP dependence plot for {feature_name} saved to {dep_path}")
            
        return True
    except Exception as e:
        logger.error(f"Error generating SHAP analysis: {e}")
        return False

def main():
    """Main function for model evaluation"""
    # Record execution start time
    start_time = datetime.now()
    logger.info(f"Model evaluation started at: {start_time}")
    
    # Load test data
    test_data = load_test_data()
    
    if test_data is not None:
        # Prepare features and targets
        X, y_reg, y_cls = prepare_features_and_target(test_data)
        
        # Load and evaluate regression model
        reg_model = load_model("jamb_score_regressor")
        if reg_model:
            reg_metrics = evaluate_regression_model(reg_model, X, y_reg, "Random Forest Regressor")
            generate_shap_analysis(reg_model, X, "Random Forest Regressor")
        
        # Load and evaluate XGBoost model
        xgb_model = load_model("jamb_xgb_regressor")
        if xgb_model:
            xgb_metrics = evaluate_regression_model(xgb_model, X, y_reg, "XGBoost Regressor")
            generate_shap_analysis(xgb_model, X, "XGBoost Regressor")
        
        # Load and evaluate classification model
        cls_model = load_model("jamb_pass_classifier")
        if cls_model:
            cls_metrics = evaluate_classification_model(cls_model, X, y_cls, "Pass/Fail Classifier")
            generate_shap_analysis(cls_model, X, "Pass/Fail Classifier")
        
        # Compare models
        if reg_model and xgb_model:
            logger.info("Model comparison:")
            logger.info(f"  Random Forest RMSE: {reg_metrics['rmse']:.2f}")
            logger.info(f"  XGBoost RMSE: {xgb_metrics['rmse']:.2f}")
            logger.info(f"  Improvement: {(reg_metrics['rmse'] - xgb_metrics['rmse']) / reg_metrics['rmse'] * 100:.2f}%")
    
    # Record execution end time
    end_time = datetime.now()
    execution_time = end_time - start_time
    logger.info(f"Model evaluation completed at: {end_time}")
    logger.info(f"Total execution time: {execution_time}")

if __name__ == "__main__":
    main()