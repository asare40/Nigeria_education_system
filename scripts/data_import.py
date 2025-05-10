# -*- coding: utf-8 -*-
"""
Created on Fri May  9 06:32:58 2025

@author: kings
"""

# scripts/data_import.py
import os
import pandas as pd
import sys
import logging
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import RAW_DATA_DIR, PROCESSED_DATA_DIR

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('data_import.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def load_csv(filename):
    """Load CSV file from data directory"""
    try:
        filepath = os.path.join(RAW_DATA_DIR, filename)
        logger.info(f"Loading data from {filepath}")
        return pd.read_csv(filepath)
    except Exception as e:
        logger.error(f"Error loading {filename}: {e}")
        return None

def main():
    """Main function to import and preprocess data"""
    # Record execution start time
    start_time = datetime.now()
    logger.info(f"Data import started at: {start_time}")
    
    # Load datasets
    jamb_data = load_csv('jamb_exam_results.csv')
    edu_indicators = load_csv('education_nga.csv')
    
    if jamb_data is not None:
        # Basic preprocessing
        logger.info(f"JAMB dataset shape: {jamb_data.shape}")
        
        # Check for missing values
        missing_values = jamb_data.isnull().sum()
        logger.info(f"Missing values in JAMB data:\n{missing_values}")
        
        # Save processed data
        processed_path = os.path.join(PROCESSED_DATA_DIR, 'jamb_processed.csv')
        jamb_data.to_csv(processed_path, index=False)
        logger.info(f"Processed JAMB data saved to {processed_path}")
    
    if edu_indicators is not None:
        # Process education indicators
        logger.info(f"Education indicators shape: {edu_indicators.shape}")
        
        # Filter relevant columns and years
        # This would be customized based on analysis needs
        
        # Save processed data
        processed_path = os.path.join(PROCESSED_DATA_DIR, 'indicators_processed.csv')
        edu_indicators.to_csv(processed_path, index=False)
        logger.info(f"Processed education indicators saved to {processed_path}")
    
    # Record execution end time
    end_time = datetime.now()
    execution_time = end_time - start_time
    logger.info(f"Data import completed at: {end_time}")
    logger.info(f"Total execution time: {execution_time}")

if __name__ == "__main__":
    main()