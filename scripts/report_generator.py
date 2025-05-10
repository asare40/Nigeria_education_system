# -*- coding: utf-8 -*-
"""
Created on Fri May  9 06:37:18 2025

@author: kings
"""

# scripts/report_generator.py
import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from jinja2 import Template

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import PROCESSED_DATA_DIR

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('reports.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Create reports directory if it doesn't exist
REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

# HTML template for report
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>{{ title }}</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 40px;
            line-height: 1.6;
        }
        h1, h2, h3 {
            color: #1C4E80;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }
        th, td {
            text-align: left;
            padding: 8px;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #f2f2f2;
            font-weight: bold;
        }
        .metric {
            font-size: 24px;
            font-weight: bold;
            color: #1C4E80;
        }
        .metric-label {
            font-size: 14px;
            color: #666;
        }
        .metrics-container {
            display: flex;
            justify-content: space-between;
            margin: 20px 0;
        }
        .metric-box {
            flex: 1;
            padding: 15px;
            background: #f9f9f9;
            border-radius: 5px;
            margin-right: 10px;
            text-align: center;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        img.plot {
            width: 100%;
            max-width: 800px;
            margin: 20px 0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .footer {
            margin-top: 50px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            color: #666;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <h1>{{ title }}</h1>
    <p>Generated: {{ generation_time }}</p>
    
    <h2>Summary</h2>
    <div class="metrics-container">
        <div class="metric-box">
            <div class="metric">{{ avg_score }}</div>
            <div class="metric-label">Average JAMB Score</div>
        </div>
        <div class="metric-box">
            <div class="metric">{{ pass_rate }}%</div>
            <div class="metric-label">Pass Rate (≥200)</div>
        </div>
        <div class="metric-box">
            <div class="metric">{{ top_performers }}%</div>
            <div class="metric-label">Top Performers (≥250)</div>
        </div>
        <div class="metric-box">
            <div class="metric">{{ at_risk_count }}</div>
            <div class="metric-label">At Risk Students</div>
        </div>
    </div>
    
    <h2>Performance Analysis</h2>
    <img src="cid:score_distribution" class="plot" alt="Score Distribution">
    
    <h2>Key Factors Affecting Performance</h2>
    <img src="cid:factor_analysis" class="plot" alt="Factor Analysis">
    
    <h2>Top 10 At-Risk Students</h2>
    <table>
        <tr>
            {{ at_risk_headers|safe }}
        </tr>
        {{ at_risk_rows|safe }}
    </table>
    
    <h2>Recommendations</h2>
    <ul>
        {% for recommendation in recommendations %}
        <li>{{ recommendation }}</li>
        {% endfor %}
    </ul>
    
    <div class="footer">
        <p>Nigerian Educational Analytics Project - Confidential Report</p>
        <p>Report ID: {{ report_id }}</p>
    </div>
</body>
</html>
"""

def load_processed_data():
    """Load processed data for reporting"""
    try:
        filepath = os.path.join(PROCESSED_DATA_DIR, 'jamb_enhanced.csv')
        logger.info(f"Loading data from {filepath}")
        return pd.read_csv(filepath)
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        