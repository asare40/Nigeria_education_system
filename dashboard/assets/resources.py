"""
Resource Library Component for Nigerian Educational Analytics Dashboard
Created: May 9, 2025
Author: asare40
"""

import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import requests
import json
from datetime import datetime, UTC
import os
import pandas as pd

# Define JAMB Subjects and Resources
JAMB_SUBJECTS = {
    "English Language": {
        "code": "eng",
        "topics": ["Comprehension", "Lexis and Structure", "Oral English", "Literature"]
    },
    "Mathematics": {
        "code": "math",
        "topics": ["Algebra", "Geometry", "Statistics", "Calculus", "Trigonometry"]
    },
    "Physics": {
        "code": "phy",
        "topics": ["Mechanics", "Energy", "Waves", "Electricity", "Modern Physics"]
    },
    "Chemistry": {
        "code": "chem",
        "topics": ["Atomic Structure", "Chemical Reactions", "Organic Chemistry", "Electrolysis"]
    },
    "Biology": {
        "code": "bio",
        "topics": ["Cell Biology", "Genetics", "Ecology", "Physiology", "Evolution"]
    },
    "Government": {
        "code": "gov",
        "topics": ["Nigerian Constitution", "Political Systems", "Democracy", "International Relations"]
    },
    "Literature": {
        "code": "lit",
        "topics": ["Poetry", "Drama", "Prose", "Literary Devices"]
    },
    "Economics": {
        "code": "econ",
        "topics": ["Microeconomics", "Macroeconomics", "Development Economics", "Public Finance"]
    },
}

# Define Open Educational Resources
OER_SOURCES = {
    "OpenStax": {
        "base_url": "https://openstax.org/subjects/",
        "subjects": {
            "math": "math",
            "eng": "humanities",
            "bio": "science",
            "chem": "science",
            "phy": "science",
            "gov": "social-sciences",
            "econ": "business",
        }
    },
    "Khan Academy": {
        "base_url": "https://www.khanacademy.org/",
        "subjects": {
            "math": "math",
            "eng": "humanities/grammar",
            "bio": "science/biology",
            "chem": "science/chemistry",
            "phy": "science/physics",
            "gov": "humanities/world-history",
            "econ": "economics-finance-domain/microeconomics",
        }
    },
    "LibreTexts": {
        "base_url": "https://libretexts.org/",
        "subjects": {
            "math": "Mathematics",
            "eng": "Humanities",
            "bio": "Biology",
            "chem": "Chemistry",
            "phy": "Physics",
            "gov": "SocialSciences",
            "econ": "Business",
        }
    },
    "YouTube EDU": {
        "base_url": "https://www.youtube.com/results?search_query=",
        "subjects": {
            "math": "JAMB+Mathematics+tutorial",
            "eng": "JAMB+English+tutorial",
            "bio": "JAMB+Biology+tutorial",
            "chem": "JAMB+Chemistry+tutorial",
            "phy": "JAMB+Physics+tutorial",
            "gov": "JAMB+Government+tutorial",
            "lit": "JAMB+Literature+tutorial",
            "econ": "JAMB+Economics+tutorial",
        }
    },
    "JAMB eLearning": {
        "base_url": "https://www.jamb.gov.ng/elearning/",
        "subjects": {
            "math": "mathematics",
            "eng": "english",
            "bio": "biology",
            "chem": "chemistry",
            "phy": "physics",
            "gov": "government",
            "lit": "literature",
            "econ": "economics",
        }
    },
}

# Cache for resources
RESOURCES_CACHE = {}
CACHE_EXPIRY = 24*60*60  # 24 hours in seconds
CACHE_FILE = "resources_cache.json"

def load_cache():
    """Load cached resources if available"""
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'r') as f:
                cache_data = json.load(f)
                # Check if cache is still valid
                if datetime.now(UTC).timestamp() - cache_data.get("timestamp", 0) < CACHE_EXPIRY:
                    return cache_data.get("resources", {})
    except Exception as e:
        print(f"Error loading cache: {e}")
    return {}

def save_cache(resources):
    """Save resources to cache with timestamp"""
    try:
        with open(CACHE_FILE, 'w') as f:
            json.dump({
                "timestamp": datetime.now(UTC).timestamp(),
                "resources": resources
            }, f)
    except Exception as e:
        print(f"Error saving cache: {e}")

# Mock function to fetch resources from OER APIs
def fetch_resources(subject, topic=None):
    """Fetch educational resources for a specific subject and topic"""
    # In a real implementation, this would query various APIs
    # For now, we'll generate mock data based on the subject and topic
    
    resources = []
    subject_code = JAMB_SUBJECTS.get(subject, {}).get("code", "")
    
    if not subject_code:
        return []
    
    # Check cache first
    cache_key = f"{subject_code}_{topic if topic else 'all'}"
    if cache_key in RESOURCES_CACHE:
        return RESOURCES_CACHE[cache_key]
        
    # For each OER source
    for source_name, source_info in OER_SOURCES.items():
        if subject_code in source_info["subjects"]:
            subject_path = source_info["subjects"][subject_code]
            url = f"{source_info['base_url']}{subject_path}"
            
            # In a real implementation, we would make API calls here
            # For demonstration, we'll create sample resources
            if source_name == "OpenStax":
                resources.append({
                    "title": f"{subject} Textbook",
                    "type": "book",
                    "source": source_name,
                    "url": url,
                    "description": f"Comprehensive {subject} textbook covering all JAMB topics",
                    "rating": 4.7
                })
                
            elif source_name == "Khan Academy":
                if topic:
                    topic_url = f"{url}/{topic.lower().replace(' ', '-')}"
                    resources.append({
                        "title": f"{topic} - {subject} Tutorial",
                        "type": "video",
                        "source": source_name,
                        "url": topic_url,
                        "description": f"Interactive lessons on {topic} for {subject} JAMB preparation",
                        "rating": 4.8
                    })
                else:
                    resources.append({
                        "title": f"{subject} Course",
                        "type": "course",
                        "source": source_name,
                        "url": url,
                        "description": f"Full {subject} course with practice exercises",
                        "rating": 4.9
                    })
                    
            elif source_name == "LibreTexts":
                resources.append({
                    "title": f"{subject} LibreText",
                    "type": "book",
                    "source": source_name,
                    "url": url,
                    "description": f"Open educational resource for {subject} with examples and problems",
                    "rating": 4.5
                })
                
            elif source_name == "YouTube EDU":
                resources.append({
                    "title": f"JAMB {subject} Video Tutorials",
                    "type": "video",
                    "source": source_name,
                    "url": url,
                    "description": f"Curated video lessons for JAMB {subject} exam preparation",
                    "rating": 4.6
                })
                
            elif source_name == "JAMB eLearning":
                resources.append({
                    "title": f"Official JAMB {subject} Materials",
                    "type": "official",
                    "source": source_name,
                    "url": url,
                    "description": f"Official study materials and practice questions for JAMB {subject}",
                    "rating": 4.9
                })
    
    # Add topic specific resources
    if topic:
        resources.append({
            "title": f"{topic} in {subject} - Study Guide",
            "type": "notes",
            "source": "Nigerian Academia",
            "url": f"https://example.com/jamb/{subject_code}/{topic.lower().replace(' ', '-')}",
            "description": f"Comprehensive notes on {topic} for JAMB {subject} preparation",
            "rating": 4.7
        })
        
        resources.append({
            "title": f"{topic} Practice Questions",
            "type": "practice",
            "source": "JAMB Prep",
            "url": f"https://example.com/practice/{subject_code}/{topic.lower().replace(' ', '-')}",
            "description": f"Over 200 practice questions on {topic} for {subject} JAMB preparation",
            "rating": 4.8
        })
    
    # Cache the results
    RESOURCES_CACHE[cache_key] = resources
    
    return resources

# Create resource library layout
def create_resource_library():
    """Create the resource library layout"""
    
    # Initialize cache
    global RESOURCES_CACHE
    RESOURCES_CACHE = load_cache()
    
    return html.Div([
        html.Div([
            html.H3("JAMB Digital Resource Library", style={'color': '#1C4E80'}),
            html.P("Access free educational resources and learning materials for JAMB preparation", 
                   style={'color': '#64748b', 'marginBottom': '25px'}),
            
            # Loading spinner for resources
            dcc.Loading(
                id="resource-loading",
                type="circle",
                children=[
                    html.Div(id="resource-content")
                ]
            ),
            
            # Resource filters
            html.Div([
                html.Div([
                    html.Label("Select Subject:", style={'fontWeight': '500'}),
                    dcc.Dropdown(
                        id="subject-dropdown",
                        options=[{"label": subj, "value": subj} for subj in JAMB_SUBJECTS.keys()],
                        value="English Language",
                        clearable=False,
                        style={'width': '100%'}
                    )
                ], style={'flex': '1', 'minWidth': '200px', 'marginRight': '10px'}),
                
                html.Div([
                    html.Label("Select Topic:", style={'fontWeight': '500'}),
                    dcc.Dropdown(
                        id="topic-dropdown",
                        options=[],  # Will be populated based on subject selection
                        value=None,
                        style={'width': '100%'}
                    )
                ], style={'flex': '1', 'minWidth': '200px', 'marginRight': '10px'}),
                
                html.Div([
                    html.Label("Resource Type:", style={'fontWeight': '500'}),
                    dcc.Dropdown(
                        id="resource-type-dropdown",
                        options=[
                            {"label": "All Types", "value": "all"},
                            {"label": "Books", "value": "book"},
                            {"label": "Videos", "value": "video"},
                            {"label": "Practice Questions", "value": "practice"},
                            {"label": "Course Materials", "value": "course"},
                            {"label": "Official JAMB Materials", "value": "official"}
                        ],
                        value="all",
                        clearable=False,
                        style={'width': '100%'}
                    )
                ], style={'flex': '1', 'minWidth': '200px'}),
            ], style={'display': 'flex', 'flexWrap': 'wrap', 'marginBottom': '20px'}),
            
            # Resources display area
            html.Div(id="resources-container", className="resources-grid"),
            
            # Resource saving feature
            html.Div([
                html.H4("My Saved Resources", style={'color': '#1C4E80', 'marginTop': '40px'}),
                html.Div(id="saved-resources", className="saved-resources"),
                
                # Hidden storage for saved resources
                dcc.Store(id="saved-resources-store", storage_type="local")
            ])
        ], className="resource-section")
    ], id="resource-library")

# Create resource card
def create_resource_card(resource):
    """Create a card component for a resource"""
    resource_type = resource.get("type", "")
    
    # Choose icon based on resource type
    icon = "📖"  # Default book icon
    if resource_type == "video":
        icon = "🎬"
    elif resource_type == "practice":
        icon = "✍️"
    elif resource_type == "course":
        icon = "🏫"
    elif resource_type == "official":
        icon = "🏆"
    elif resource_type == "notes":
        icon = "📝"
    
    return html.Div([
        html.Div([
            html.Div([
                html.Span(icon, className="resource-icon"),
                html.H4(resource.get("title", "Unknown Resource"))
            ], style={'display': 'flex', 'alignItems': 'center', 'gap': '10px'}),
            html.P(resource.get("description", ""), className="resource-description"),
            html.Div([
                html.Span(f"Source: {resource.get('source', 'Unknown')}", className="resource-source"),
                html.Div([
                    html.Span("Rating: ", className="rating-label"),
                    html.Span("★" * int(resource.get("rating", 0)), className="rating-stars"),
                    html.Span(f"{resource.get('rating', 'N/A')}/5", className="rating-value")
                ], className="resource-rating")
            ], className="resource-meta"),
        ], className="resource-info"),
        html.Div([
            html.A("Access Resource", href=resource.get("url", "#"), target="_blank", className="access-btn"),
            html.Button("Save", id={"type": "save-resource-btn", "index": resource.get("title")}, className="save-btn")
        ], className="resource-actions")
    ], className=f"resource-card {resource_type}")

def register_callbacks(app):
    """Register callbacks for the resource library"""
    
    # Update topics based on subject selection
    @app.callback(
        Output("topic-dropdown", "options"),
        Input("subject-dropdown", "value")
    )
    def update_topics(subject):
        if not subject or subject not in JAMB_SUBJECTS:
            return []
        topics = JAMB_SUBJECTS[subject]["topics"]
        return [{"label": topic, "value": topic} for topic in topics]
    
    # Update resources based on filters
    @app.callback(
        Output("resources-container", "children"),
        [
            Input("subject-dropdown", "value"),
            Input("topic-dropdown", "value"),
            Input("resource-type-dropdown", "value")
        ]
    )
    def update_resources(subject, topic, resource_type):
        if not subject:
            return html.P("Please select a subject to view resources")
        
        # Fetch resources
        resources = fetch_resources(subject, topic)
        
        # Filter by resource type if needed
        if resource_type and resource_type != "all":
            resources = [r for r in resources if r.get("type", "") == resource_type]
        
        if not resources:
            return html.Div([
                html.P("No resources found for the selected criteria."),
                html.P("Try selecting a different subject, topic, or resource type.")
            ], style={'textAlign': 'center', 'padding': '40px', 'color': '#64748b'})
        
        # Create resource cards
        resource_cards = [create_resource_card(resource) for resource in resources]
        
        return resource_cards
    
    # Save and load resources to local storage
    @app.callback(
        Output("saved-resources", "children"),
        [Input({"type": "save-resource-btn", "index": dash.ALL}, "n_clicks")],
        [State("saved-resources-store", "data"),
         State("subject-dropdown", "value"),
         State("topic-dropdown", "value")]
    )
    def update_saved_resources(n_clicks, saved_data, current_subject, current_topic):
        ctx = dash.callback_context
        if not ctx.triggered:
            # Initial load, check if we have saved data
            if not saved_data:
                return html.P("No saved resources yet. Click 'Save' on any resource to add it here.")
            
            # Display saved resources
            saved_cards = []
            for resource in saved_data:
                saved_cards.append(
                    html.Div([
                        html.Div([
                            html.H5(resource.get("title")),
                            html.P(f"Subject: {resource.get('subject')}"),
                            html.P(f"Type: {resource.get('type', 'Unknown').capitalize()}")
                        ], style={'flex': '1'}),
                        html.A("View", href=resource.get("url", "#"), target="_blank", className="view-saved-btn")
                    ], className="saved-resource-item")
                )
            return saved_cards
        
        # A save button was clicked
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        button_data = json.loads(button_id)
        resource_index = button_data.get("index")
        
        # Get current resources
        resources = fetch_resources(current_subject, current_topic)
        resource_to_save = next((r for r in resources if r.get("title") == resource_index), None)
        
        if not resource_to_save:
            return dash.no_update
        
        # Add subject and topic info
        resource_to_save["subject"] = current_subject
        resource_to_save["topic"] = current_topic or "General"
        
        # Initialize or update saved resources
        if not saved_data:
            saved_data = []
        
        # Check if already saved
        if not any(r.get("title") == resource_index for r in saved_data):
            saved_data.append(resource_to_save)
        
        # Update display
        saved_cards = []
        for resource in saved_data:
            saved_cards.append(
                html.Div([
                    html.Div([
                        html.H5(resource.get("title")),
                        html.P(f"Subject: {resource.get('subject')}"),
                        html.P(f"Type: {resource.get('type', 'Unknown').capitalize()}")
                    ], style={'flex': '1'}),
                    html.A("View", href=resource.get("url", "#"), target="_blank", className="view-saved-btn")
                ], className="saved-resource-item")
            )
            
        return saved_cards

# Save cache on exit
def on_exit():
    """Save cache on exit"""
    if RESOURCES_CACHE:
        save_cache(RESOURCES_CACHE)