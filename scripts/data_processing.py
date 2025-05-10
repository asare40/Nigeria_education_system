# -*- coding: utf-8 -*-
"""
Created on Fri May  9 06:33:24 2025

@author: kings
"""

# scripts/data_processing.py
import os
import pandas as pd
import numpy as np
import sys
import logging
from datetime import datetime
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import PROCESSED_DATA_DIR

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('data_processing.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def load_processed_data(filename):
    """Load processed CSV file"""
    try:
        filepath = os.path.join(PROCESSED_DATA_DIR, filename)
        logger.info(f"Loading processed data from {filepath}")
        return pd.read_csv(filepath)
    except Exception as e:
        logger.error(f"Error loading {filename}: {e}")
        return None

def create_feature_pipeline():
    """Create preprocessing pipeline for feature engineering"""
    # Define numeric and categorical features
    numeric_features = [
        'Study_Hours_Per_Week', 'Attendance_Rate', 'Teacher_Quality',
        'Distance_To_School'
    ]
    categorical_features = [
        'School_Type', 'School_Location', 'Extra_Tutorials',
        'Access_To_Learning_Materials', 'Parent_Involvement',
        'IT_Knowledge'
    ]
    
    # Define transformers
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])
    
    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('onehot', OneHotEncoder(handle_unknown='ignore'))
    ])
    
    # Create column transformer
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ],
        remainder='drop'  # Drop any columns not specified
    )
    
    return preprocessor

def engineer_features(df):
    """Engineer additional features from existing data"""
    # Create copy to avoid modifying original
    df_new = df.copy()
    
    # Feature: Study efficiency (Score per study hour)
    df_new['Study_Efficiency'] = df_new['JAMB_Score'] / df_new['Study_Hours_Per_Week'].replace(0, 0.1)
    
    # Feature: School environment quality (combination of factors)
    df_new['School_Quality_Index'] = df_new['Teacher_Quality'] * 0.6 + \
                                    (df_new['Access_To_Learning_Materials'] == 'Yes').astype(int) * 0.4
    
    # Feature: Student engagement level
    df_new['Engagement_Level'] = (df_new['Attendance_Rate'] / 20) + \
                                (df_new['Extra_Tutorials'] == 'Yes').astype(int) + \
                                (df_new['Parent_Involvement'] == 'High').astype(int)
    
    # Feature: Distance barrier (inverse relationship with distance)
    df_new['Distance_Barrier'] = 1 / (1 + df_new['Distance_To_School'])
    
    return df_new

def main():
    """Main function for data preprocessing"""
    # Record execution start time
    start_time = datetime.now()
    logger.info(f"Data preprocessing started at: {start_time}")
    
    # Load processed JAMB data
    jamb_data = load_processed_data('jamb_processed.csv')
    
    if jamb_data is not None:
        # Engineer features
        logger.info("Engineering additional features...")
        enhanced_data = engineer_features(jamb_data)
        
        # Save enhanced data
        enhanced_path = os.path.join(PROCESSED_DATA_DIR, 'jamb_enhanced.csv')
        enhanced_data.to_csv(enhanced_path, index=False)
        logger.info(f"Enhanced JAMB data saved to {enhanced_path}")
        
        # Create train-test split files for modeling
        # This is simplified - in practice we'd use proper train_test_split
        n = len(enhanced_data)
        train_idx = np.random.choice(n, int(0.8*n), replace=False)
        test_idx = np.array(list(set(range(n)) - set(train_idx)))
        
        train_data = enhanced_data.iloc[train_idx]
        test_data = enhanced_data.iloc[test_idx]
        
        # Save train and test datasets
        train_path = os.path.join(PROCESSED_DATA_DIR, 'train_data.csv')
        test_path = os.path.join(PROCESSED_DATA_DIR, 'test_data.csv')
        
        train_data.to_csv(train_path, index=False)
        test_data.to_csv(test_path, index=False)
        
        logger.info(f"Training data saved to {train_path}")
        logger.info(f"Testing data saved to {test_path}")
    
    # Record execution end time
    end_time = datetime.now()
    execution_time = end_time - start_time
    logger.info(f"Data preprocessing completed at: {end_time}")
    logger.info(f"Total execution time: {execution_time}")

if __name__ == "__main__":
    main()