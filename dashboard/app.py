# -*- coding: utf-8 -*-
"""
Created on Fri May  9 06:33:54 2025

@author: kings
"""

# dashboard/app.py
import os
import sys
import pandas as pd
import dash
from dash import dcc, html, Input, Output, State, dash_table
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import numpy as np
import pickle
from datetime import datetime, timezone, UTC  # Import UTC for timezone-aware dates
import atexit

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import PROCESSED_DATA_DIR, MODEL_DIR

# Import resource library components
from assets.resources import create_resource_library, register_callbacks, on_exit

# Load data and models
def load_data():
    """Load processed data for dashboard"""
    try:
        jamb_data = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, 'jamb_enhanced.csv'))
        return jamb_data
    except Exception as e:
        print(f"Error loading data: {e}")
        return pd.DataFrame()

def load_models():
    """Load trained models"""
    models = {}
    try:
        for model_name in ["jamb_score_regressor", "jamb_pass_classifier", "jamb_xgb_regressor"]:
            model_path = os.path.join(MODEL_DIR, f"{model_name}.pkl")
            with open(model_path, 'rb') as f:
                models[model_name] = pickle.load(f)
        return models
    except Exception as e:
        print(f"Error loading models: {e}")
        return {}

# Load data and models
data = load_data()
models = load_models()

# Initialize Dash app
app = dash.Dash(__name__, 
                meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
                title="Nigerian Educational Analytics Dashboard")

# Expose the Flask server for deployment (if needed)
server = app.server

# Add custom CSS for header styling
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
        <style>
            .header-container {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 10px 20px;
                margin-bottom: 20px;
                background-color: #f8f9fa;
                border-radius: 5px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .header-left {
                flex: 1;
            }
            .header-right {
                text-align: right;
                padding: 10px;
                background-color: #f0f7ff;
                border-radius: 4px;
                border-left: 4px solid #1C4E80;
            }
            .user-info {
                font-size: 0.9rem;
                color: #555;
            }
            .user-name {
                color: #1C4E80;
                font-weight: bold;
            }
            .time-info {
                font-size: 0.9rem;
                margin-top: 4px;
                color: #666;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Define app layout
app.layout = html.Div([
    # Header with title, date/time, and user info
    html.Div([
        # Title and main header
        html.Div([
            html.H1("Nigerian Educational Analytics Dashboard By Data Aspire", 
                    style={'color': '#1C4E80', 'marginBottom': 10}),
            html.P("Analyze student performance and predict JAMB scores", 
                   style={'color': '#64748b', 'fontSize': '1.1rem'})
        ], className="header-left"),
        
        # User and time info
        html.Div([
            html.Div([
                html.Span("Current User: ", className="user-label"),
                html.Span("asare40", className="user-name")
            ], className="user-info"),
            html.Div([
                html.Span("Date/Time (UTC): ", className="time-label"),
                html.Span(id="live-clock", className="time-value")
            ], className="time-info"),
            
            # Add an invisible interval component for updating the clock
            dcc.Interval(
                id='clock-interval',
                interval=1000,  # in milliseconds, updates every 1 second
                n_intervals=0
            )
        ], className="header-right")
    ], className="header-container"),
    
    html.Div([
        # Main tabs
        dcc.Tabs([
            # Overview tab
            dcc.Tab(label="Overview", children=[
                html.Div([
                    html.H3("Overview Statistics", style={'color': '#1C4E80'}),
                    html.Div(id="overview-stats", className="stats-container")
                ], className="overview-section")
            ], className="custom-tab"),
            
            # Analysis tab
            dcc.Tab(label="Performance Analysis", children=[
                html.Div([
                    html.H3("Performance Analysis", style={'color': '#1C4E80'}),
                    dcc.Tabs([
                        dcc.Tab(label="Score Distribution", children=[
                            html.Div([
                                html.P("This chart shows the distribution of JAMB scores across the student population.", 
                                       className="chart-description"),
                                html.P("The red dashed line indicates the passing threshold (200).", 
                                       className="chart-insight"),
                                dcc.Graph(id="score-distribution")
                            ])
                        ]),
                        dcc.Tab(label="Factor Analysis", children=[
                            html.Div([
                                html.P("Explore how different factors affect JAMB scores.", 
                                       className="chart-description"),
                                html.Div([
                                    html.Label("Select Factor:"),
                                    dcc.Dropdown(
                                        id="factor-dropdown",
                                        options=[
                                            {'label': 'Study Hours', 'value': 'Study_Hours_Per_Week'},
                                            {'label': 'Teacher Quality', 'value': 'Teacher_Quality'},
                                            {'label': 'Distance to School', 'value': 'Distance_To_School'},
                                            {'label': 'School Type', 'value': 'School_Type'},
                                            {'label': 'Parent Involvement', 'value': 'Parent_Involvement'},
                                            {'label': 'Access to Learning Materials', 'value': 'Access_To_Learning_Materials'}
                                        ],
                                        value='Study_Hours_Per_Week'
                                    )
                                ]),
                                html.Div(id="factor-insights", className="insights-container"),
                                dcc.Graph(id="factor-analysis")
                            ])
                        ]),
                        dcc.Tab(label="Correlation Matrix", children=[
                            html.Div([
                                html.P("This heatmap shows the correlation between various factors affecting JAMB scores.", 
                                       className="chart-description"),
                                html.P("Positive values (blue) indicate factors that tend to increase together, while negative values (red) indicate inverse relationships.", 
                                       className="chart-insight"),
                                dcc.Graph(id="correlation-matrix")
                            ])
                        ])
                    ])
                ], className="analysis-section")
            ], className="custom-tab"),
            
            # Prediction tab
            dcc.Tab(label="Score Prediction", children=[
                html.Div([
                    html.H3("Student Prediction Tool", style={'color': '#1C4E80'}),
                    html.P("Enter student details to predict their JAMB score and get personalized recommendations",
                           style={'color': '#64748b', 'marginBottom': '20px'}),
                    html.Div([
                        # Two-column layout for better organization
                        html.Div([
                            # Academic Factors Column
                            html.Div([
                                html.H4("Academic Factors", style={'color': '#2563eb', 'marginBottom': '15px'}),
                                
                                html.Div([
                                    html.Label("Study Hours Per Week:"),
                                    dcc.Slider(
                                        id="study-hours-input",
                                        min=0,
                                        max=40,
                                        step=1,
                                        value=20,
                                        marks={i: str(i) for i in range(0, 41, 5)}
                                    )
                                ], className="input-group"),
                                
                                html.Div([
                                    html.Label("Teacher Quality (1-5):"),
                                    dcc.Slider(
                                        id="teacher-quality-input",
                                        min=1,
                                        max=5,
                                        step=1,
                                        value=3,
                                        marks={i: str(i) for i in range(1, 6)}
                                    )
                                ], className="input-group"),
                                
                                html.Div([
                                    html.Label("Attendance Rate (%):"),
                                    dcc.Slider(
                                        id="attendance-input",
                                        min=50,
                                        max=100,
                                        step=5,
                                        value=80,
                                        marks={i: str(i) for i in range(50, 101, 10)}
                                    )
                                ], className="input-group"),
                                
                                html.Div([
                                    html.Label("Extra Tutorials:"),
                                    dcc.RadioItems(
                                        id="tutorials-input",
                                        options=[
                                            {'label': 'Yes', 'value': 'Yes'},
                                            {'label': 'No', 'value': 'No'}
                                        ],
                                        value='No',
                                        labelStyle={'marginRight': '15px'}
                                    )
                                ], className="input-group"),
                            ], className="column"),
                            
                            # Environmental Factors Column
                            html.Div([
                                html.H4("Environmental Factors", style={'color': '#2563eb', 'marginBottom': '15px'}),
                                
                                html.Div([
                                    html.Label("Distance to School (km):"),
                                    dcc.Input(
                                        id="distance-input",
                                        type="number",
                                        min=0.1,
                                        max=20,
                                        step=0.1,
                                        value=5.0,
                                        className="number-input"
                                    )
                                ], className="input-group"),
                                
                                html.Div([
                                    html.Label("School Type:"),
                                    dcc.RadioItems(
                                        id="school-type-input",
                                        options=[
                                            {'label': 'Public', 'value': 'Public'},
                                            {'label': 'Private', 'value': 'Private'}
                                        ],
                                        value='Public',
                                        labelStyle={'marginRight': '15px'}
                                    )
                                ], className="input-group"),
                                
                                html.Div([
                                    html.Label("School Location:"),
                                    dcc.RadioItems(
                                        id="location-input",
                                        options=[
                                            {'label': 'Urban', 'value': 'Urban'},
                                            {'label': 'Rural', 'value': 'Rural'}
                                        ],
                                        value='Urban',
                                        labelStyle={'marginRight': '15px'}
                                    )
                                ], className="input-group"),
                                
                                html.Div([
                                    html.Label("Access to Learning Materials:"),
                                    dcc.RadioItems(
                                        id="materials-input",
                                        options=[
                                            {'label': 'Yes', 'value': 'Yes'},
                                            {'label': 'No', 'value': 'No'}
                                        ],
                                        value='Yes',
                                        labelStyle={'marginRight': '15px'}
                                    )
                                ], className="input-group"),
                            ], className="column"),
                        ], className="two-column-form"),
                        
                        # Additional Factors
                        html.Div([
                            html.H4("Additional Factors", style={'color': '#2563eb', 'marginBottom': '15px'}),
                            html.Div([
                                html.Div([
                                    html.Label("Parent Involvement:"),
                                    dcc.RadioItems(
                                        id="parent-input",
                                        options=[
                                            {'label': 'Low', 'value': 'Low'},
                                            {'label': 'Medium', 'value': 'Medium'},
                                            {'label': 'High', 'value': 'High'}
                                        ],
                                        value='Medium',
                                        labelStyle={'marginRight': '15px'}
                                    )
                                ], className="input-group half-width"),
                                
                                html.Div([
                                    html.Label("IT Knowledge:"),
                                    dcc.RadioItems(
                                        id="it-input",
                                        options=[
                                            {'label': 'Low', 'value': 'Low'},
                                            {'label': 'Medium', 'value': 'Medium'},
                                            {'label': 'High', 'value': 'High'}
                                        ],
                                        value='Medium',
                                        labelStyle={'marginRight': '15px'}
                                    )
                                ], className="input-group half-width"),
                            ], style={'display': 'flex', 'flexWrap': 'wrap'}),
                        ], className="additional-factors"),
                        
                        html.Button(
                            [html.I(className="fas fa-calculator", style={"marginRight": "10px"}), "Predict Score"],
                            id="predict-button", 
                            className="predict-button"
                        ),
                        
                        html.Div(id="prediction-output", className="prediction-output")
                    ], className="prediction-form")
                ], className="prediction-section")
            ], className="custom-tab"),
            
            # Digital Library tab
            dcc.Tab(label="Digital Library", children=[
                # This function creates the resource library component
                create_resource_library()
            ], className="custom-tab"),
            
            # Documentation tab
            dcc.Tab(label="Documentation", children=[
                html.Div([
                    html.Iframe(
                        src="/assets/documentation.html",
                        style={"width": "100%", "height": "800px", "border": "none", "borderRadius": "10px"}
                    )
                ])
            ], className="custom-tab"),
        ], className="main-tabs")
    ], className="main-container"),
    
    html.Footer([
        html.P("Nigerian Educational Analytics Project | Created by Korletey Asare Enock on May 9, 2025",
              style={'textAlign': 'center', 'color': '#666666'})
    ], className="footer")
])

# Add this callback to update the clock
@app.callback(
    Output("live-clock", "children"),
    Input("clock-interval", "n_intervals")
)
def update_clock(n):
    """Update the clock display with current UTC time"""
    # Use timezone-aware object with UTC as recommended
    return datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")

# Define callback for overview statistics
@app.callback(
    Output("overview-stats", "children"),
    Input("overview-stats", "children")
)
def update_stats(n):
    if data.empty:
        return html.Div("No data available")
        
    avg_score = data['JAMB_Score'].mean()
    pass_rate = (data['JAMB_Score'] >= 200).mean() * 100
    top_performers = (data['JAMB_Score'] >= 250).mean() * 100
    
    stats = [
        html.Div([
            html.Div([html.I(className="fas fa-chart-line", style={"fontSize": "24px", "color": "#2563eb", "marginBottom": "10px"})]),
            html.H4(f"{avg_score:.1f}"),
            html.P("Average JAMB Score")
        ], className="stat-card"),
        html.Div([
            html.Div([html.I(className="fas fa-check-circle", style={"fontSize": "24px", "color": "#16a34a", "marginBottom": "10px"})]),
            html.H4(f"{pass_rate:.1f}%"),
            html.P("Pass Rate (≥200)")
        ], className="stat-card"),
        html.Div([
            html.Div([html.I(className="fas fa-trophy", style={"fontSize": "24px", "color": "#f59e0b", "marginBottom": "10px"})]),
            html.H4(f"{top_performers:.1f}%"),
            html.P("Top Performers (≥250)")
        ], className="stat-card")
    ]
    
    return stats

# Define callback for score distribution
@app.callback(
    Output("score-distribution", "figure"),
    Input("score-distribution", "id")
)
def update_score_distribution(n):
    if data.empty:
        return {}
        
    fig = px.histogram(
        data, 
        x="JAMB_Score",
        nbins=30,
        color_discrete_sequence=['#2563eb'],
        title="JAMB Score Distribution"
    )
    
    fig.add_vline(x=200, line_dash="dash", line_color="red",
                  annotation_text="Pass Threshold", annotation_position="top right")
    
    fig.update_layout(
        xaxis_title="JAMB Score",
        yaxis_title="Number of Students",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#4b5563'),
        title_font=dict(color='#1a3b66', size=18)
    )
    
    return fig

# Define callback for factor insights
@app.callback(
    Output("factor-insights", "children"),
    Input("factor-dropdown", "value")
)
def update_factor_insights(factor):
    if not factor:
        return []
    
    insights = {
        'Study_Hours_Per_Week': [
            html.P("Students who study more than 20 hours per week show significantly higher scores.", 
                   className="insight-item"),
            html.P("Each additional hour of study correlates with approximately 2-3 additional points on the JAMB exam.", 
                   className="insight-item"),
            html.P("The relationship is almost linear, indicating consistent returns on time invested in studying.", 
                   className="insight-item")
        ],
        'Teacher_Quality': [
            html.P("Teacher quality shows a strong positive correlation with student performance.", 
                   className="insight-item"),
            html.P("Students with access to high-quality teachers (rated 4-5) score on average 45 points higher than those with low-quality teachers (rated 1-2).", 
                   className="insight-item"),
            html.P("The impact of teacher quality is especially pronounced in subjects requiring specialized guidance, such as Mathematics and Sciences.", 
                   className="insight-item")
        ],
        'Distance_To_School': [
            html.P("There is a negative correlation between distance to school and JAMB scores.", 
                   className="insight-item"),
            html.P("Students traveling more than 10km to school score on average 25 points lower than those living within 5km.", 
                   className="insight-item"),
            html.P("The effect is likely due to increased commute time reducing available study hours and increased fatigue.", 
                   className="insight-item")
        ],
        'School_Type': [
            html.P("On average, students from private schools score 32 points higher than those from public schools.", 
                   className="insight-item"),
            html.P("However, high-performing public school students can achieve scores comparable to private school peers when other positive factors are present.", 
                   className="insight-item"),
            html.P("The gap is smaller when controlling for socioeconomic status and access to learning materials.", 
                   className="insight-item")
        ],
        'Parent_Involvement': [
            html.P("High parental involvement is associated with a 38-point average increase in JAMB scores compared to low involvement.", 
                   className="insight-item"),
            html.P("Students with high parental involvement are 42% more likely to score above 250 points.", 
                   className="insight-item"),
            html.P("The positive effect of parental involvement appears to be independent of family socioeconomic status.", 
                   className="insight-item")
        ],
        'Access_To_Learning_Materials': [
            html.P("Access to comprehensive learning materials results in an average score increase of 45 points.", 
                   className="insight-item"),
            html.P("This factor has one of the strongest correlations with JAMB performance.", 
                   className="insight-item"),
            html.P("The effect is particularly pronounced for students from lower socioeconomic backgrounds.", 
                   className="insight-item")
        ]
    }
    
    return html.Div([
        html.H4(f"Insights: {factor.replace('_', ' ')}", style={'color': '#1a3b66', 'marginTop': '20px'}),
        html.Div(insights.get(factor, [html.P("No specific insights available for this factor.")]),
                className="insights-box")
    ])

# Define callback for factor analysis
@app.callback(
    Output("factor-analysis", "figure"),
    Input("factor-dropdown", "value")
)
def update_factor_analysis(factor):
    if data.empty:
        return {}
    
    if factor in ['Study_Hours_Per_Week', 'Teacher_Quality', 'Distance_To_School']:
        # For numeric factors, create scatter plot
        fig = px.scatter(
            data,
            x=factor,
            y="JAMB_Score",
            trendline="ols",
            color_discrete_sequence=['#2563eb'],
            title=f"Relationship between {factor.replace('_', ' ')} and JAMB Score",
            opacity=0.7
        )
        
    else:
        # For categorical factors, create box plot
        fig = px.box(
            data,
            x=factor,
            y="JAMB_Score",
            color=factor,
            title=f"JAMB Score by {factor.replace('_', ' ')}",
            color_discrete_map={
                "Public": "#3b82f6", 
                "Private": "#10b981",
                "Yes": "#10b981",
                "No": "#ef4444",
                "Urban": "#8b5cf6",
                "Rural": "#f59e0b",
                "Low": "#ef4444",
                "Medium": "#f59e0b",
                "High": "#10b981"
            }
        )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#4b5563'),
        title_font=dict(color='#1a3b66', size=18)
    )
    
    return fig

# Define callback for correlation matrix
@app.callback(
    Output("correlation-matrix", "figure"),
    Input("correlation-matrix", "id")
)
def update_correlation_matrix(n):
    if data.empty:
        return {}
    
    # Select numeric columns for correlation
    numeric_cols = ['JAMB_Score', 'Study_Hours_Per_Week', 'Attendance_Rate', 
                   'Teacher_Quality', 'Distance_To_School']
    
    corr = data[numeric_cols].corr()
    
    fig = px.imshow(
        corr,
        text_auto='.2f',
        color_continuous_scale='RdBu_r',
        title="Correlation Matrix of Key Factors"
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#4b5563'),
        title_font=dict(color='#1a3b66', size=18)
    )
    
    return fig

# Define callback for prediction tool - FIXED VERSION
@app.callback(
    Output("prediction-output", "children"),
    Input("predict-button", "n_clicks"),
    State("study-hours-input", "value"),
    State("teacher-quality-input", "value"),
    State("attendance-input", "value"),
    State("distance-input", "value"),
    State("school-type-input", "value"),
    State("location-input", "value"),
    State("tutorials-input", "value"),
    State("materials-input", "value"),
    State("parent-input", "value"),
    State("it-input", "value"),
    prevent_initial_call=True  # Prevent callback execution on initial load
)
def update_prediction(n_clicks, study_hours, teacher_quality, attendance, distance,
                      school_type, location, tutorials, materials, parent, it):
    if not n_clicks:
        return html.Div([
            html.P("Fill in the student details and click 'Predict Score'")
        ])
    
    try:
        if not models or 'jamb_xgb_regressor' not in models:
            return html.Div([
                html.P("Prediction model not available", style={'color': 'red'})
            ])
        
        # Create input features dataframe with all required columns
        input_data = pd.DataFrame({
            'Study_Hours_Per_Week': [float(study_hours)],
            'Teacher_Quality': [float(teacher_quality)],
            'Attendance_Rate': [float(attendance)],
            'Distance_To_School': [float(distance)],
            'School_Type': [str(school_type)],
            'School_Location': [str(location)],
            'Extra_Tutorials': [str(tutorials)],
            'Access_To_Learning_Materials': [str(materials)],
            'Parent_Involvement': [str(parent)],
            'IT_Knowledge': [str(it)],
            # Adding the missing columns with default values
            'Parent_Education_Level': ['Secondary'],  # Default value
            'Gender': ['Male'],  # Default value
            'Student_ID': [1000],  # Default ID
            'Assignments_Completed': [80],  # Default percentage
            'Socioeconomic_Status': ['Middle'],  # Default value
            'Age': [18],  # Default value
            'Study_Efficiency': [0.7]  # Default value (0-1 scale)
        })
        
        # Add engineered features
        input_data['School_Quality_Index'] = float(teacher_quality) * 0.6
        if materials == 'Yes':
            input_data.loc[0, 'School_Quality_Index'] += 0.4
            
        input_data['Engagement_Level'] = float(attendance) / 20.0
        if tutorials == 'Yes':
            input_data.loc[0, 'Engagement_Level'] += 1.0
        if parent == 'High':
            input_data.loc[0, 'Engagement_Level'] += 1.0
            
        input_data['Distance_Barrier'] = 1.0 / (1.0 + float(distance))
        
        # Make predictions - handle as simple float values
        predicted_score = float(models['jamb_xgb_regressor'].predict(input_data)[0])
        pass_probability = float(models['jamb_pass_classifier'].predict_proba(input_data)[0][1]) * 100
        
        # Determine risk level
        if predicted_score >= 250:
            risk_level = "Low"
            risk_color = "green"
        elif predicted_score >= 200:
            risk_level = "Medium"
            risk_color = "orange"
        else:
            risk_level = "High"
            risk_color = "red"
        
        # Generate recommendations - simplified
        recommendations = []
        
        if study_hours < 20:
            recommendations.append("Increase study time to at least 20 hours per week")
        if attendance < 85:
            recommendations.append("Improve class attendance to at least 85%")
        if tutorials == 'No':
            recommendations.append("Consider enrolling in extra tutorial classes")
        if materials == 'No':
            recommendations.append("Ensure access to required learning materials")
        if distance > 10:
            recommendations.append("Consider finding accommodation closer to school")
        
        # Return styled HTML structure
        return html.Div([
            html.H4("Prediction Results", className="prediction-header"),
            html.Div([
                html.Div([
                    html.H2(f"{predicted_score:.1f}", style={'color': risk_color}),
                    html.P("Predicted JAMB Score")
                ], className="prediction-card"),
                html.Div([
                    html.H2(f"{pass_probability:.1f}%", style={'color': 'green' if pass_probability >= 70 else 'orange'}),
                    html.P("Chance of Scoring 200+")
                ], className="prediction-card"),
                html.Div([
                    html.H2(risk_level, style={'color': risk_color}),
                    html.P("Risk Level")
                ], className="prediction-card")
            ], className="prediction-results"),
            
            html.Div([
                html.H4("Recommendations:", className="recommendation-header"),
                html.Ul([html.Li(rec, className="recommendation-item") for rec in recommendations]) if recommendations else 
                    html.P("No specific recommendations at this time.")
            ], className="recommendations")
        ])
        
    except Exception as e:
        # Handle errors gracefully
        import traceback
        print(f"Prediction error: {e}")
        print(traceback.format_exc())
        return html.Div([
            html.P(f"Error making prediction: {str(e)}", style={'color': 'red'})
        ])

# Register callbacks for the resource library
register_callbacks(app)

# Register exit handler to save cache
atexit.register(on_exit)

# Run app
if __name__ == '__main__':
    try:
        # Print access instructions
        local_ip = "127.0.0.1"
        print("\n" + "="*60)
        print(f"Nigerian Educational Analytics Dashboard is running!")
        print(f"Access the dashboard at: http://localhost:8050 or http://127.0.0.1:8050")
        print("="*60 + "\n")
        
        # Run the app
        app.run(
            debug=True,
            host="localhost",  # Changed from 0.0.0.0 to localhost for better compatibility
            port=8050
        )
    except Exception as e:
        print(f"Error starting the dashboard: {e}")