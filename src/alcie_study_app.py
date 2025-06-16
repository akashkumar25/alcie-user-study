#!/usr/bin/env python3
"""
ALCIE User Study - Complete Streamlit Version with All Improvements
Enhanced UI with automatic data collection, between-category assessments, and robust CSV/Sheets saving
Run with: streamlit run alcie_study_streamlit.py
"""

import streamlit as st

# Page configuration - MUST BE FIRST AND ONLY ONCE
st.set_page_config(
    page_title="ALCIE User Study",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Now import everything else
import json
import pandas as pd
import random
import os
from datetime import datetime
from PIL import Image
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ======================== IMPROVED GOOGLE SHEETS FUNCTIONS ========================

def get_main_responses_headers():
    """Generate headers that match the actual data structure"""
    base_headers = [
        'participant_id', 'fashion_interest', 'total_samples', 'all_image_ids', 
        'all_categories', 'response_type', 'age_group', 'gender',
        'quality_patterns_noticed', 'better_categories', 'worse_categories',
        'learning_hypothesis', 'better_learned_categories', 'accessories_rank',
        'bottoms_rank', 'dresses_rank', 'outerwear_rank', 'shoes_rank', 
        'tops_rank', 'caption_preference', 'summary_assessment_rating',
        'forgetting_evidence', 'final_feedback', 'completion_timestamp'
    ]
    return base_headers

def get_detailed_responses_headers():
    """Generate headers for detailed per-response data with method ratings"""
    base_headers = [
        'participant_id', 'fashion_interest', 'sample_number', 'image_id', 
        'category', 'introduced_phase', 'cf_risk', 'best_caption_method', 
        'comment', 'timestamp'
    ]
    
    # Add method mapping headers
    method_headers = ['method_caption_a', 'method_caption_b', 'method_caption_c']
    
    # Add rating headers for each method (dynamically generated based on actual methods)
    rating_headers = []
    example_methods = ['method1', 'method2', 'method3']  # Will be replaced with actual method names
    for method in example_methods:
        rating_headers.extend([
            f'{method}_relevance',
            f'{method}_fluency', 
            f'{method}_descriptiveness',
            f'{method}_novelty'
        ])
    
    # Add final questionnaire headers
    final_headers = [
        'response_type', 'age_group', 'gender', 'quality_patterns_noticed', 
        'better_categories', 'worse_categories', 'learning_hypothesis', 
        'better_learned_categories', 'accessories_rank', 'bottoms_rank', 
        'dresses_rank', 'outerwear_rank', 'shoes_rank', 'tops_rank', 
        'caption_preference', 'summary_assessment_rating', 'forgetting_evidence', 
        'final_feedback', 'completion_timestamp'
    ]
    
    return base_headers + method_headers + rating_headers + final_headers

def get_category_assessments_headers():
    """Headers for category assessments"""
    return [
        'participant_id', 'response_type', 'previous_category', 'current_category',
        'sample_idx_at_transition', 'quality_rating', 'quality_drop',
        'consistency_rating', 'expectations_rating', 'comments', 'timestamp'
    ]

def ensure_headers_exist(worksheet, headers):
    """Ensure headers exist and match expected structure"""
    try:
        # Get existing headers (first row)
        existing_headers = worksheet.row_values(1) if worksheet.row_count > 0 else []
        
        # If no headers or headers don't match, update them
        if not existing_headers or existing_headers != headers:
            if existing_headers:
                # Clear first row and insert new headers
                worksheet.delete_rows(1, 1)
            worksheet.insert_row(headers, 1)
            return True
        return False
    except Exception as e:
        st.warning(f"Could not ensure headers: {e}")
        return False

def get_gsheet_connection():
    """Get Google Sheets connection with proper error handling"""
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        
        # Use the correct secret key that matches your secrets.toml
        creds = ServiceAccountCredentials.from_json_keyfile_dict(
            st.secrets["gcp_service_account"], scope
        )
        client = gspread.authorize(creds)
        return client
    except KeyError as e:
        st.error(f"❌ Missing credentials in secrets: {e}")
        return None
    except Exception as e:
        st.error(f"❌ Failed to connect to Google Sheets: {e}")
        return None

def save_response_to_sheet_with_proper_headers(row_data, worksheet_name="MainResponses"):
    """Save single row to Google Sheets with proper header management"""
    try:
        client = get_gsheet_connection()
        if not client:
            return False
            
        # Try to open existing spreadsheet, create if doesn't exist
        try:
            sheet = client.open("ALCIE User Study Responses")
        except gspread.SpreadsheetNotFound:
            sheet = client.create("ALCIE User Study Responses")
            sheet.share('akashkumar97251@gmail.com', perm_type='user', role='writer')
        
        # Get or create worksheet
        try:
            worksheet = sheet.worksheet(worksheet_name)
        except gspread.WorksheetNotFound:
            worksheet = sheet.add_worksheet(title=worksheet_name, rows=1000, cols=50)
        
        # Ensure proper headers based on worksheet type
        if worksheet_name == "MainResponses":
            headers = get_main_responses_headers()
        elif worksheet_name == "DetailedResponses":
            headers = get_detailed_responses_headers()
        elif worksheet_name == "CategoryAssessments":
            headers = get_category_assessments_headers()
        else:
            headers = []
        
        if headers:
            ensure_headers_exist(worksheet, headers)
        
        # Convert row_data to list of strings
        if isinstance(row_data, (list, tuple)):
            string_row = [str(item) for item in row_data]
        else:
            string_row = [str(row_data)]
            
        worksheet.append_row(string_row)
        return True
        
    except Exception as e:
        st.warning(f"❗ Could not save to Google Sheet ({worksheet_name}): {e}")
        return False

def save_category_assessments_to_sheets():
    """Save all category assessments to Google Sheets"""
    if not hasattr(st.session_state, 'category_assessments') or not st.session_state.category_assessments:
        return True
    
    try:
        success_count = 0
        for assessment in st.session_state.category_assessments:
            # Convert assessment dict to list in correct order
            row_data = [
                assessment['participant_id'],
                assessment['response_type'],
                assessment['previous_category'],
                assessment['current_category'],
                assessment['sample_idx_at_transition'],
                assessment['quality_rating'],
                assessment['quality_drop'],
                assessment['consistency_rating'],
                assessment['expectations_rating'],
                assessment['comments'],
                assessment['timestamp']
            ]
            
            if save_response_to_sheet_with_proper_headers(row_data, worksheet_name="CategoryAssessments"):
                success_count += 1
        
        return success_count > 0
        
    except Exception as e:
        st.error(f"❌ Error saving category assessments: {e}")
        return False

def save_main_responses_to_sheets_fixed(final_data):
    """Save summary participant data to Google Sheets with proper headers"""
    try:
        # Create summary row data (one row per participant)
        row_data = [
            st.session_state.participant_id,
            st.session_state.fashion_interest,
            len(st.session_state.responses),  # total samples
            ', '.join([str(r['image_id']) for r in st.session_state.responses]),
            ', '.join([str(r['category']) for r in st.session_state.responses]),
            final_data.get('response_type', ''),
            final_data.get('age_group', ''),
            final_data.get('gender', ''),
            final_data.get('quality_patterns_noticed', ''),
            final_data.get('better_categories', ''),
            final_data.get('worse_categories', ''),
            final_data.get('learning_hypothesis', ''),
            final_data.get('better_learned_categories', ''),
            final_data.get('accessories_rank', ''),
            final_data.get('bottoms_rank', ''),
            final_data.get('dresses_rank', ''),
            final_data.get('outerwear_rank', ''),
            final_data.get('shoes_rank', ''),
            final_data.get('tops_rank', ''),
            final_data.get('caption_preference', ''),
            final_data.get('summary_assessment_rating', ''),
            final_data.get('forgetting_evidence', ''),
            final_data.get('final_feedback', ''),
            final_data.get('completion_timestamp', '')
        ]
        
        return save_response_to_sheet_with_proper_headers(row_data, worksheet_name="MainResponses")
        
    except Exception as e:
        st.error(f"❌ Error saving main responses: {e}")
        return False

# ======================== ENHANCED CSV SAVING FUNCTIONS ========================

def save_progress_to_csv():
    """Save current progress to CSV (called after each response)"""
    try:
        if not st.session_state.responses:
            return
            
        output_dir = "responses"
        os.makedirs(output_dir, exist_ok=True)
        
        # Create progress file
        progress_file = os.path.join(output_dir, f"{st.session_state.participant_id}_progress.csv")
        
        # Convert responses to DataFrame with proper flattening
        rows = []
        for response in st.session_state.responses:
            # Base row data
            row = {
                'participant_id': response['participant_id'],
                'fashion_interest': response['fashion_interest'],
                'sample_number': response['sample_number'],
                'image_id': response['image_id'],
                'category': response['category'],
                'introduced_phase': response['introduced_phase'],
                'cf_risk': response['cf_risk'],
                'best_caption_method': response['best_caption_method'],
                'comment': response['comment'],
                'timestamp': response['timestamp']
            }
            
            # Flatten method mapping
            for caption_label, method in response['method_mapping'].items():
                row[f'method_{caption_label.lower().replace(" ", "_")}'] = method
            
            # Flatten ratings
            for method, ratings in response['ratings'].items():
                for metric, score in ratings.items():
                    row[f'{method}_{metric}'] = score
            
            rows.append(row)
        
        # Save to CSV
        df = pd.DataFrame(rows)
        df.to_csv(progress_file, index=False)
        
        # Also save category assessments if they exist
        if hasattr(st.session_state, 'category_assessments') and st.session_state.category_assessments:
            category_progress_file = os.path.join(output_dir, f"{st.session_state.participant_id}_category_progress.csv")
            category_df = pd.DataFrame(st.session_state.category_assessments)
            category_df.to_csv(category_progress_file, index=False)
            
        return True
        
    except Exception as e:
        st.warning(f"Could not save progress to CSV: {e}")
        return False

def save_final_complete_csv(final_data):
    """Save complete final CSV with all data properly structured"""
    try:
        output_dir = "responses"
        os.makedirs(output_dir, exist_ok=True)
        
        # Main responses with final questionnaire data
        main_rows = []
        for response in st.session_state.responses:
            row = {
                # Response data
                'participant_id': response['participant_id'],
                'fashion_interest': response['fashion_interest'],
                'sample_number': response['sample_number'],
                'image_id': response['image_id'],
                'category': response['category'],
                'introduced_phase': response['introduced_phase'],
                'cf_risk': response['cf_risk'],
                'best_caption_method': response['best_caption_method'],
                'comment': response['comment'],
                'timestamp': response['timestamp'],
                
                # Final questionnaire data (same for all rows)
                **final_data
            }
            
            # Flatten method mapping
            for caption_label, method in response['method_mapping'].items():
                row[f'method_{caption_label.lower().replace(" ", "_")}'] = method
            
            # Flatten ratings
            for method, ratings in response['ratings'].items():
                for metric, score in ratings.items():
                    row[f'{method}_{metric}'] = score
            
            main_rows.append(row)
        
        # Save main responses
        main_df = pd.DataFrame(main_rows)
        final_file = os.path.join(output_dir, f"{st.session_state.participant_id}_complete.csv")
        main_df.to_csv(final_file, index=False)
        
        # Save category assessments
        category_final_file = None
        if hasattr(st.session_state, 'category_assessments') and st.session_state.category_assessments:
            category_df = pd.DataFrame(st.session_state.category_assessments)
            category_final_file = os.path.join(output_dir, f"{st.session_state.participant_id}_category_assessments_final.csv")
            category_df.to_csv(category_final_file, index=False)
        
        # Create summary file with participant overview
        summary_data = {
            'participant_id': st.session_state.participant_id,
            'total_responses': len(st.session_state.responses),
            'total_category_assessments': len(st.session_state.get('category_assessments', [])),
            'completion_status': 'complete',
            'start_time': st.session_state.responses[0]['timestamp'] if st.session_state.responses else '',
            'end_time': final_data['completion_timestamp'],
            **{k: v for k, v in final_data.items() if k not in ['participant_id', 'response_type']}
        }
        
        summary_df = pd.DataFrame([summary_data])
        summary_file = os.path.join(output_dir, f"{st.session_state.participant_id}_summary.csv")
        summary_df.to_csv(summary_file, index=False)
        
        return True, final_file, category_final_file, summary_file
        
    except Exception as e:
        st.error(f"Error saving final CSV: {e}")
        return False, None, None, None

# ======================== PROCESSING INDICATORS ========================

def show_progress_bar(steps_total, current_step, step_description):
    """Show progress bar with step description"""
    progress = current_step / steps_total
    st.progress(progress, text=f"Step {current_step}/{steps_total}: {step_description}")

# ======================== EXISTING STREAMLIT UI CODE ========================

st.markdown("""
<style>
/* Root Variables */
:root {
    --primary-color: #4F46E5;
    --primary-dark: #3730A3;
    --success-color: #10B981;
    --radius: 8px;
    --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

@media (prefers-color-scheme: light) {
    :root {
        --text-primary: #1F2937;
        --text-secondary: #6B7280;
        --bg-primary: #FFFFFF;
        --bg-secondary: #F9FAFB;
        --border-color: #E5E7EB;
    }
}

@media (prefers-color-scheme: dark) {
    :root {
        --text-primary: #ECEFF4;
        --text-secondary: #D8DEE9;
        --bg-primary: #2E3440;
        --bg-secondary: #3B4252;
        --border-color: #4C566A;
    }
}

/* Force consistent light appearance */
body, .stApp {
    background-color: #FFFFFF !important;
    color: #212529 !important;
}

/* Global Text Styling */
body, p, li, span, div, label, h1, h2, h3, h4, h5, h6 {
    color: #212529 !important;
}

/* Header */
.main-header {
    background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
    color: white;
    text-align: center;
    padding: 2rem;
    margin: -1rem -1rem 2rem -1rem;
    border-radius: 0 0 var(--radius) var(--radius);
    box-shadow: var(--shadow);
}

.main-header h1, .main-header h3 {
    color: white !important;
}

/* Cards */
.info-card, .caption-box, .progress-box, .success-message {
    background: #F8F9FA !important;
    color: #212529 !important;
    border: 1px solid #DEE2E6 !important;
    border-radius: var(--radius);
    padding: 1rem;
    box-shadow: var(--shadow);
}

/* Category Badge */
.category-badge {
    background: var(--primary-color);
    color: white;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
}

/* Buttons */
.stButton > button {
    background: var(--primary-color) !important;
    color: white !important;
    border: none !important;
    border-radius: var(--radius) !important;
    font-weight: 600 !important;
    padding: 0.75rem 1.5rem !important;
    transition: all 0.2s !important;
}

.stButton > button:hover {
    background: var(--primary-dark) !important;
    transform: translateY(-1px);
    box-shadow: var(--shadow);
}

/* Dropdown / Selectbox / Multiselect */
.stSelectbox, .stMultiSelect {
    color: #212529 !important;
}

.stSelectbox > div > div, 
.stSelectbox [data-testid="stSelectbox"],
.stMultiSelect > div > div,
.stMultiSelect [data-testid="stMultiSelect"] {
    background-color: #F8F9FA !important;
    color: #212529 !important;
    border: 1px solid #DEE2E6 !important;
}

/* Fix inner input text visibility */
.stSelectbox input, .stMultiSelect input {
    background-color: #F8F9FA !important;
    color: #212529 !important;
}

/* Dropdown Options (Popover) */
[data-baseweb="popover"],
[data-baseweb="popover"] ul,
[data-baseweb="popover"] li,
[data-baseweb="popover"] li:hover,
[data-baseweb="option"],
[data-baseweb="option"]:hover {
    background-color: #F8F9FA !important;
    color: #212529 !important;
    border: none !important;
}

/* Tags (selected items) */
[data-baseweb="tag"] {
    background-color: #DEE2E6 !important;
    color: #212529 !important;
}

/* Hide Streamlit UI Elements */
#MainMenu, footer, header, .stDeployButton {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)

class ALCIEStreamlitApp:
    def __init__(self):
        self.study_dataset_file = "data/alcie_study_dataset.json"
        self.images_directory = "images/"
        self.load_data()
        
    def load_data(self):
        """Load and shuffle study data"""
        try:
            with open(self.study_dataset_file, 'r') as f:
                data = json.load(f)
            self.study_data = data['samples'].copy()
            # Sort by category and phase instead of random shuffle
            self.study_data = sorted(
                data["samples"],
                key=lambda x: (x["category"], x["assigned_phase"])
            )
            return True
        except Exception as e:
            st.error(f"❌ Error loading data: {e}")
            return False
    
    def get_image_path(self, image_id):
        """Get PIL Image object"""
        for ext in ['.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG']:
            image_path = os.path.join(self.images_directory, f"{image_id}{ext}")
            if os.path.exists(image_path):
                try:
                    return Image.open(image_path)
                except Exception as e:
                    st.error(f"Error loading image {image_path}: {e}")
                    continue
        return None

# Initialize app
@st.cache_resource
def get_app():
    return ALCIEStreamlitApp()

app = get_app()

# Session state initialization
def init_session_state():
    if 'study_started' not in st.session_state:
        st.session_state.study_started = False
        st.session_state.current_sample_idx = 0
        st.session_state.responses = []
        timestamp_ms = int(time.time() * 1000)
        random_suffix = random.randint(100, 999)
        st.session_state.participant_id = f"P{timestamp_ms}{random_suffix}"
        st.session_state.fashion_interest = None
        st.session_state.consent_given = False
        st.session_state.study_complete = False
        st.session_state.processing_completion = False

init_session_state()

# ======================== CATEGORY ASSESSMENT FUNCTIONS ========================

def should_show_category_assessment():
    """Determine if we should show category assessment"""
    if st.session_state.current_sample_idx == 0:
        return False, None, None
    
    # Check if we've just finished the study (last category assessment)
    if st.session_state.current_sample_idx >= len(app.study_data):
        # Get the last sample's category for final assessment
        last_sample = app.study_data[st.session_state.current_sample_idx - 1]
        last_category = last_sample['category']
        
        # Check if we haven't assessed the last category yet
        final_assessment_key = f"final_{last_category.lower()}_assessment"
        if not hasattr(st.session_state, 'assessed_transitions'):
            st.session_state.assessed_transitions = set()
        
        if final_assessment_key not in st.session_state.assessed_transitions:
            return True, last_category, "completion"
        else:
            return False, None, None
    
    # Check if we're transitioning to a new category (existing logic)
    current_sample = app.study_data[st.session_state.current_sample_idx]
    previous_sample = app.study_data[st.session_state.current_sample_idx - 1]
    
    current_category = current_sample['category']
    previous_category = previous_sample['category']
    
    # Show assessment when transitioning to a new category
    if current_category != previous_category:
        # Don't show if we've already assessed this transition
        transition_key = f"{previous_category}_to_{current_category}"
        if not hasattr(st.session_state, 'assessed_transitions'):
            st.session_state.assessed_transitions = set()
        
        if transition_key not in st.session_state.assessed_transitions:
            return True, previous_category, current_category
    
    return False, None, None

def show_category_transition_assessment(previous_category, current_category):
    """Show assessment when transitioning between categories"""
    
    st.markdown("---")
    
    # Handle final category assessment differently
    if current_category == "completion":
        st.markdown(f"""
        <div class="info-card" style="background: #FEF3C7; border-color: #F59E0B;">
            <h3>📊 Final Category Assessment</h3>
            <p><strong>You've just completed:</strong> {previous_category} items (Final Category)</p>
            <p><strong>Next:</strong> Final questionnaire</p>
            <p>This helps us understand quality patterns for the last fashion category.</p>
        </div>
        """, unsafe_allow_html=True)
        
        continue_text = "Continue to Final Questionnaire →"
        transition_key = f"final_{previous_category.lower()}_assessment"
    else:
        st.markdown(f"""
        <div class="info-card" style="background: #FEF3C7; border-color: #F59E0B;">
            <h3>📊 Quick Category Assessment</h3>
            <p><strong>You've just completed:</strong> {previous_category} items</p>
            <p><strong>Now starting:</strong> {current_category} items</p>
            <p>This helps us understand quality patterns across fashion categories.</p>
        </div>
        """, unsafe_allow_html=True)
        
        continue_text = f"Continue to {current_category} →"
        transition_key = f"{previous_category}_to_{current_category}"
    
    col1, col2 = st.columns(2)
    
    with col1:
        quality_assessment = st.radio(
            f"How would you rate the overall caption quality for {previous_category} items?",
            ["Excellent", "Good", "Average", "Below average", "Poor"],
            index=None,
            key=f"quality_{previous_category.lower()}_assessment",
            help="Think about the captions you just evaluated for this category"
        )
        
        quality_drop = st.radio(
            f"Did you notice any quality decrease in {previous_category} captions?",
            ["No decrease", "Slight decrease", "Moderate decrease", "Significant decrease", "Major decrease"],
            index=None,
            key=f"quality_drop_{previous_category.lower()}",
            help="Compare to your expectations or other categories you've seen"
        )
    
    with col2:
        consistency = st.radio(
            f"How consistent were the {previous_category} captions?",
            ["Very consistent", "Mostly consistent", "Somewhat consistent", "Inconsistent", "Very inconsistent"],
            index=None,
            key=f"consistency_{previous_category.lower()}",
            help="Did caption quality vary a lot within this category?"
        )
        
        expectations = st.radio(
            f"Did {previous_category} captions meet your expectations?",
            ["Exceeded expectations", "Met expectations", "Below expectations", "Well below expectations"],
            index=None,
            key=f"expectations_{previous_category.lower()}",
            help="Based on what you'd expect for AI-generated fashion descriptions"
        )
    
    comments = st.text_area(
        f"Any specific observations about {previous_category} captions?",
        placeholder=f"Optional: What did you notice about {previous_category} descriptions?",
        height=80,
        key=f"comments_{previous_category.lower()}"
    )
    
    if st.button(continue_text, type="primary", use_container_width=True):
        # Validate that all radio buttons are selected
        if not quality_assessment:
            st.error("❌ Please rate the overall caption quality")
        elif not quality_drop:
            st.error("❌ Please indicate if you noticed any quality decrease")
        elif not consistency:
            st.error("❌ Please rate the consistency of captions")
        elif not expectations:
            st.error("❌ Please indicate if captions met your expectations")
        else:
            # Store the assessment data
            assessment_data = {
                'participant_id': st.session_state.participant_id,
                'response_type': 'category_assessment',
                'previous_category': previous_category,
                'current_category': current_category,
                'sample_idx_at_transition': st.session_state.current_sample_idx,
                'quality_rating': quality_assessment,
                'quality_drop': quality_drop,
                'consistency_rating': consistency,
                'expectations_rating': expectations,
                'comments': comments,
                'timestamp': datetime.now().isoformat()
            }
            
            # Store in session state
            if 'category_assessments' not in st.session_state:
                st.session_state.category_assessments = []
            st.session_state.category_assessments.append(assessment_data)
            
            # Mark this transition as assessed
            st.session_state.assessed_transitions.add(transition_key)
            
            # Handle final category vs regular transition
            if current_category == "completion":
                # Go directly to completion page
                st.session_state.show_category_assessment = False
                st.session_state.show_transition_banner = "final_category_completed"
            else:
                # Regular category transition
                st.session_state.show_transition_banner = f"category_transition_{current_category}"
                st.session_state.show_category_assessment = False
            
            st.rerun()

# ======================== UI PAGES ========================

def show_welcome_page():
    """Show welcome and consent page"""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🎯 ALCIE Fashion Study</h1>
        <h3>Active Learning for Continual Image Captioning Enhancement</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick overview
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="info-card">
        <h3>👋 Welcome & Thank You!</h3>
        <p>We're excited to have you participate in our AI research! Your insights will help us build better AI systems for fashion e-commerce and visual understanding.</p>
        
        <p><strong>What you'll do:</strong> Evaluate AI-generated fashion captions and help us understand what makes descriptions effective.</p>
        
        <p><strong>Your impact:</strong> Your feedback directly contributes to advancing AI technology used by millions of online shoppers.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="info-card">
        <h3>📊 Study Quick Facts</h3>
        <ul>
        <li><strong>Duration:</strong> 15-20 minutes</li>
        <li><strong>Task:</strong> Rate AI fashion captions</li>
        <li><strong>Categories:</strong> 6 fashion types</li>
        <li><strong>Privacy:</strong> Completely anonymous</li>
        <li><strong>Institution:</strong> DFKI (German AI Research Center)</li>
        <li><strong>Researcher:</strong> Akash Kumar</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Research background
    st.markdown("""
    ## 🔬 What This Study Is About
    
    **Research Focus:** We're investigating how AI systems learn to describe fashion items and whether they maintain quality when learning new categories over time.
    
    **Your Role:** As someone interested in fashion, you'll evaluate AI-generated captions on four key aspects: relevance, fluency, descriptiveness, and novelty.
    
    **Scientific Impact:** Results will be published in academic conferences and help advance computer vision and natural language processing.
    """)
    
    # Study guide
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🎯 Your Task Overview

        **What You'll Evaluate:** AI-generated fashion descriptions

        **Sample Size:** 24 fashion images, grouped by fashion category

        **Your Role:** Rate 3 different AI captions per image

        **Categories Included:**
        - 👜 **Accessories** (bags, jewelry, belts)
        - 👖 **Bottoms** (jeans, skirts, pants) 
        - 👗 **Dresses** (casual, formal, work)
        - 🧥 **Outerwear** (jackets, coats, blazers)
        - 👠 **Shoes** (sneakers, heels, boots)
        - 👕 **Tops** (shirts, blouses, sweaters)

        Images will be shown **category by category**, and for each image, you'll see **three different AI-generated captions**.

        🧠 **As you go through the study, try to notice if the captions seem more or less accurate or descriptive across different categories.**
        """)

    
    with col2:
        st.markdown("""
        ### 📊 Rating Criteria Explained
        
        **Relevance (1-5):** Does it accurately describe what's in the image?
        - *5 = Perfect match, 1 = Completely wrong*
        
        **Fluency (1-5):** How natural does the English sound?
        - *5 = Perfect grammar, 1 = Hard to understand*
        
        **Descriptiveness (1-5):** How much useful detail does it provide?
        - *5 = Very detailed, 1 = Too vague*
        
        **Novelty (1-5):** How interesting or creative is the description?
        - *5 = Very engaging, 1 = Boring/generic*
        """)
    
    # Privacy section
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🛡️ Your Privacy & Rights
        
        **What We Guarantee:**
        - **Complete anonymity** - no personal information collected
        - **Voluntary participation** - stop anytime without consequences  
        - **Secure data handling** - research-grade privacy protection
        - **Academic use only** - helps science, not commercial interests
        
        **Your Rights:**
        - Ask questions about the research anytime
        - Withdraw participation without explanation
        - Request study results after completion
        """)
    
    with col2:
        st.markdown("""
        ### 📞 Contact & Institution
        
        **Researcher:** Akash Kumar (akash.kumar@dfki.de)  
        **Supervisor:** Aliki Anagnostopoulou  
        **Institution:** DFKI - German Research Center for Artificial Intelligence  
        **Website:** www.dfki.de
        
        Feel free to contact us with any questions about this research!
        
        ### 💡 Important Reminders
        
        - **No wrong answers** - we want YOUR honest opinions
        - **Trust your instincts** - your natural reactions are what we need  
        - **Take your time** - quality feedback is more valuable than speed
        """)
    
    # Required information
    st.markdown("---")
    st.markdown("## 📝 Required Information")
    
    fashion_interest = st.radio(
        "How interested are you in fashion? (Required for research context)",
        ["Very interested", "Somewhat interested", "Moderately interested", 
        "Slightly interested", "Not particularly interested"],
        index=None,
        help="This helps us understand participant background"
    )
    
    consent = st.checkbox(
        "I have read the study information above and consent to participate in this research (Required)",
        help="Required to proceed to the study"
    )
    
    if st.button("🚀 Start Study", type="primary", use_container_width=True):
        if not consent:
            st.error("❌ Please check the consent box to continue")
        elif not fashion_interest:
            st.error("❌ Please select your fashion interest level")
        else:
            st.session_state.consent_given = True
            st.session_state.fashion_interest = fashion_interest
            st.session_state.study_started = True
            st.session_state.show_transition_banner = "start_study"
            st.rerun()

def get_current_sample():
    """Get current sample data"""
    if st.session_state.current_sample_idx >= len(app.study_data):
        return None
    
    sample = app.study_data[st.session_state.current_sample_idx]
    image_pil = app.get_image_path(sample['image_id'])
    
    # Get captions in consistent order
    methods = sorted(sample['predictions'].keys())
    captions = [sample['predictions'][method] for method in methods]
    
    return {
        'image': image_pil,
        'captions': captions,
        'progress': f"Image {st.session_state.current_sample_idx + 1} of {len(app.study_data)}",
        'category': sample['category'],
        'sample_data': sample,
        'methods': methods
    }

def show_study_interface():
    """Show main study interface"""

    st.markdown('<div id="top-anchor"></div>', unsafe_allow_html=True)

    # Check if we should show category assessment
    if st.session_state.get("show_category_assessment", False):
        show_category_transition_assessment(
            st.session_state.assessment_previous_category,
            st.session_state.assessment_current_category
        )
        return

    current = get_current_sample()
    if not current:
        # Check if we need final category assessment before completion
        should_assess, prev_cat, curr_cat = should_show_category_assessment()
        if should_assess:
            st.session_state.show_category_assessment = True
            st.session_state.assessment_previous_category = prev_cat
            st.session_state.assessment_current_category = curr_cat
            st.rerun()
        else:
            show_completion_page()
            return

    # Reset sliders only if flagged and BEFORE widgets are rendered
    if st.session_state.get("slider_reset_needed", False):
        keys_to_reset = [k for k in st.session_state.keys() if any(k.startswith(p) for p in ("rel_", "flu_", "desc_", "nov_"))]
        for key in keys_to_reset:
            st.session_state[key] = 3
        st.session_state.slider_reset_needed = False

    # Header
    st.markdown("""
    <div class="main-header">
        <h1>📊 Fashion Caption Evaluation</h1>
    </div>
    """, unsafe_allow_html=True)

    # Progress info
    st.markdown(f"""
    <div class="progress-box">
        <strong>{current['progress']}</strong>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])

    with col1:
        if current['image']:
            st.image(current['image'], caption="Fashion Image", width=350)
        st.markdown(f'<div class="category-badge">{current["category"].upper()}</div>', unsafe_allow_html=True)
        st.markdown("### 📊 Rating Instructions")
        st.markdown("""
        **For each caption, rate on 1–5 scale:**

        - **Relevance**: How accurately does it describe what you see?
        - **Fluency**: How natural and well-written is the English?
        - **Descriptiveness**: How detailed and informative is it?
        - **Novelty**: How creative, interesting, or engaging is it?

        *1 = Very Poor, 5 = Excellent*

        **Then select your favorite caption overall.**
        """)

    with col2:
        st.markdown("### 📝 Caption + Ratings")

        caption_letters = ["A", "B", "C"]
        for i, cap in enumerate(current["captions"]):
            label = caption_letters[i]
            st.markdown(f"""
            <div class="caption-box" style="padding: 1.2rem; margin-bottom: 1rem;">
                <strong>Caption {label}:</strong> {cap}
            </div>
            """, unsafe_allow_html=True)

            with st.container():
                col1, col2 = st.columns(2)
                with col1:
                    st.slider("Relevance", 1, 5, 3, key=f"rel_{label.lower()}_{st.session_state.current_sample_idx}", help="How well it describes the image")
                    st.slider("Fluency", 1, 5, 3, key=f"flu_{label.lower()}_{st.session_state.current_sample_idx}", help="How natural the caption sounds")
                with col2:
                    st.slider("Descriptiveness", 1, 5, 3, key=f"desc_{label.lower()}_{st.session_state.current_sample_idx}", help="How detailed the caption is")
                    st.slider("Novelty", 1, 5, 3, key=f"nov_{label.lower()}_{st.session_state.current_sample_idx}", help="How creative or interesting it is")

            st.markdown("---")

        best_caption = st.radio(
            "🏆 Which caption is best overall?",
            ["Caption A", "Caption B", "Caption C"],
            index=None,
            key=f"best_caption_{st.session_state.current_sample_idx}"
        )

        comment = st.text_area(
            "💭 Optional comments",
            placeholder="Any thoughts about these captions or the image?",
            height=100,
            key=f"comment_{st.session_state.current_sample_idx}"
        )

        if st.button("✅ Submit Rating & Continue", type="primary", use_container_width=True):
            if not best_caption:
                st.error("❌ Please select which caption is best overall")
            else:
                # Gather ratings for all captions
                rel_a = st.session_state[f"rel_a_{st.session_state.current_sample_idx}"]
                flu_a = st.session_state[f"flu_a_{st.session_state.current_sample_idx}"]
                desc_a = st.session_state[f"desc_a_{st.session_state.current_sample_idx}"]
                nov_a = st.session_state[f"nov_a_{st.session_state.current_sample_idx}"]

                rel_b = st.session_state[f"rel_b_{st.session_state.current_sample_idx}"]
                flu_b = st.session_state[f"flu_b_{st.session_state.current_sample_idx}"]
                desc_b = st.session_state[f"desc_b_{st.session_state.current_sample_idx}"]
                nov_b = st.session_state[f"nov_b_{st.session_state.current_sample_idx}"]

                rel_c = st.session_state[f"rel_c_{st.session_state.current_sample_idx}"]
                flu_c = st.session_state[f"flu_c_{st.session_state.current_sample_idx}"]
                desc_c = st.session_state[f"desc_c_{st.session_state.current_sample_idx}"]
                nov_c = st.session_state[f"nov_c_{st.session_state.current_sample_idx}"]

                submit_rating_with_csv_backup(current, rel_a, flu_a, desc_a, nov_a,
                              rel_b, flu_b, desc_b, nov_b,
                              rel_c, flu_c, desc_c, nov_c,
                              best_caption, comment)
                st.rerun()

def submit_rating_with_csv_backup(current, rel_a, flu_a, desc_a, nov_a, rel_b, flu_b, desc_b, nov_b,
                  rel_c, flu_c, desc_c, nov_c, best_caption, comment):
    """Submit current rating and advance with CSV backup"""

    # Create method mapping
    caption_labels = ["Caption A", "Caption B", "Caption C"]
    method_mapping = {caption_labels[i]: current['methods'][i] for i in range(3)}
    best_method = method_mapping[best_caption]

    # Store response
    response_data = {
        'participant_id': st.session_state.participant_id,
        'fashion_interest': st.session_state.fashion_interest,
        'sample_number': st.session_state.current_sample_idx + 1,
        'image_id': current['sample_data']['image_id'],
        'category': current['sample_data']['category'],
        'introduced_phase': current['sample_data']['introduced_phase'],
        'cf_risk': current['sample_data']['cf_risk'],
        'method_mapping': method_mapping,
        'ratings': {
            current['methods'][0]: {'relevance': rel_a, 'fluency': flu_a, 'descriptiveness': desc_a, 'novelty': nov_a},
            current['methods'][1]: {'relevance': rel_b, 'fluency': flu_b, 'descriptiveness': desc_b, 'novelty': nov_b},
            current['methods'][2]: {'relevance': rel_c, 'fluency': flu_c, 'descriptiveness': desc_c, 'novelty': nov_c}
        },
        'best_caption_method': best_method,
        'comment': comment,
        'timestamp': datetime.now().isoformat()
    }

    st.session_state.responses.append(response_data)
    st.session_state.current_sample_idx += 1
    
    # Save progress to CSV after each response
    save_progress_to_csv()

    # Check if we need to show category assessment
    should_assess, prev_cat, curr_cat = should_show_category_assessment()
    
    if should_assess:
        # Set flag to show category assessment instead of normal transition
        st.session_state.show_category_assessment = True
        st.session_state.assessment_previous_category = prev_cat
        st.session_state.assessment_current_category = curr_cat
    else:
        # Set normal reset flag
        st.session_state.slider_reset_needed = True
        st.session_state.show_transition_banner = True

def show_completion_page():
    """Show completion questionnaire with processing indicators"""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>📋 Final Questionnaire</h1>
        <h3>Help us understand your experience</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Progress info
    st.markdown(f"""
    <div class="progress-box">
    <strong>Rating Phase Complete!</strong><br>
    Participant ID: {st.session_state.participant_id} | 
    Images Evaluated: {len(st.session_state.responses)} | 
    Total Ratings: {len(st.session_state.responses) * 3}
    </div>
    """, unsafe_allow_html=True)
    
    # Demographics Section
    st.markdown("### 👤 Demographics")
    col1, col2 = st.columns(2)
    
    with col1:
        age = st.selectbox(
            "How old are you?",
            ["", "18-24", "25-34", "35-44", "45-54", "55-64", "65+"],
            help="Optional demographic information"
        )
    
    with col2:
        gender = st.selectbox(
            "What is your gender identity?",
            ["", "Female", "Male", "Non-binary/Third gender", "Prefer not to disclose"],
            help="Optional demographic information"
        )
    
    st.markdown("---")
    
    # Quality Assessment Section
    st.markdown("### 📊 Caption Quality Assessment")
    
    col1, col2 = st.columns(2)
    
    with col1:
        quality_patterns = st.radio(
            "Did you notice quality differences between fashion categories?",
            ["Yes, clear differences", "Some differences", "No patterns", "Not sure"],
            index=None,
            help="Think about whether certain categories had consistently better or worse captions"
        )
        
        # Conditional follow-up questions
        if quality_patterns in ["Yes, clear differences", "Some differences"]:
            better_categories = st.multiselect(
                "Which categories had better captions? (select all that apply)",
                ["Accessories", "Bottoms", "Dresses", "Outerwear", "Shoes", "Tops"],
                help="Select categories with consistently good captions"
            )
            
            worse_categories = st.multiselect(
                "Which categories had worse captions? (select all that apply)",
                ["Accessories", "Bottoms", "Dresses", "Outerwear", "Shoes", "Tops"],
                help="Select categories with consistently poor captions"
            )
        else:
            better_categories = []
            worse_categories = []
    
    with col2:
        learning_hypothesis = st.radio(
            "Do you think the AI learned some fashion categories better than others?",
            ["Yes, definitely", "Yes, somewhat", "No", "Not sure"],
            index=None,
            help="Based on the caption quality you observed"
        )
        
        if learning_hypothesis in ["Yes, definitely", "Yes, somewhat"]:
            better_learned = st.multiselect(
                "Which categories do you think the AI learned best?",
                ["Accessories", "Bottoms", "Dresses", "Outerwear", "Shoes", "Tops"],
                help="Categories where AI seemed most competent"
            )
        else:
            better_learned = []
    
    # Category Ranking Section
    st.markdown("### 🏆 Category Quality Ranking")
    st.markdown("Rank fashion categories by overall caption quality (1 = best, 6 = worst):")
    
    categories = ["Accessories", "Bottoms", "Dresses", "Outerwear", "Shoes", "Tops"]
    rankings = {}
    
    col1, col2, col3 = st.columns(3)
    with col1:
        rankings["Accessories"] = st.selectbox("Accessories (bags, jewelry, belts)", [1,2,3,4,5,6], key="rank_accessories")
        rankings["Bottoms"] = st.selectbox("Bottoms (jeans, skirts, pants)", [1,2,3,4,5,6], key="rank_bottoms")
    
    with col2:
        rankings["Dresses"] = st.selectbox("Dresses (casual, formal, work)", [1,2,3,4,5,6], key="rank_dresses")
        rankings["Outerwear"] = st.selectbox("Outerwear (jackets, coats, blazers)", [1,2,3,4,5,6], key="rank_outerwear")
    
    with col3:
        rankings["Shoes"] = st.selectbox("Shoes (sneakers, heels, boots)", [1,2,3,4,5,6], key="rank_shoes")
        rankings["Tops"] = st.selectbox("Tops (shirts, blouses, sweaters)", [1,2,3,4,5,6], key="rank_tops")
    
    # Check for duplicate rankings
    ranking_values = list(rankings.values())
    if len(set(ranking_values)) != len(ranking_values):
        st.warning("⚠️ Please ensure each category has a unique ranking (1-6)")
    
    st.markdown("---")
    
    # User Preferences and AI Assessment
    st.markdown("### 🎯 Preferences & AI Assessment")
    
    col1, col2 = st.columns(2)
    
    with col1:
        caption_preference = st.radio(
            "What type of fashion caption do you prefer?",
            ["Detailed descriptions", "Creative/engaging language", "Accurate basic facts", "Balanced approach"],
            index=None,
            help="Your personal preference for fashion descriptions"
        )
        
    
    with col2:
        summary_assessment = st.radio(
            "How well do you think the AI learned to describe diverse fashion items?",
            ["Excellent - handled all types well", "Good - handled most types well", 
            "Fair - struggled with some types", "Poor - struggled with many types", 
            "Very poor - couldn't handle most types"],
            index=None,
            help="Your overall impression of the AI's learning across different fashion categories"
        )
        
        forgetting_evidence = st.radio(
            "Did you notice any decrease in quality for categories shown earlier?",
            ["Yes, clear decrease", "Slight decrease", "No decrease noticed", "Not sure"],
            index=None,
            help="Think about whether early categories (accessories, bottoms) seemed worse"
        )
    
    # Additional Comments
    st.markdown("### 💭 Additional Feedback")
    final_feedback = st.text_area(
        "Any final thoughts, observations, or suggestions?",
        placeholder="Comments about caption quality patterns, AI performance, study experience, or suggestions for improvement...",
        height=120,
        help="Your insights are valuable for our research"
    )
    
    # Modified submit button section with processing indicators
    if st.session_state.get('processing_completion', False):
        # Show disabled button while processing
        st.button(
            "🔄 Processing... Please wait", 
            disabled=True, 
            type="primary", 
            use_container_width=True
        )
        st.warning("⏳ **Please wait...** Your submission is being processed. Do not close this window.")
    else:
        # Show normal submit button
        if st.button("💾 Complete Study & Save Results", type="primary", use_container_width=True):
            # Validate all required fields first
            if len(set(ranking_values)) != len(ranking_values):
                st.error("❌ Please ensure each category has a unique ranking (1-6)")
            elif not quality_patterns:
                st.error("❌ Please indicate if you noticed quality differences between categories")
            elif not learning_hypothesis:
                st.error("❌ Please indicate if you think the AI learned some categories better than others")
            elif not caption_preference:
                st.error("❌ Please select your caption preference")
            elif not summary_assessment:
                st.error("❌ Please rate how well the AI learned to describe fashion items")
            elif not forgetting_evidence:
                st.error("❌ Please indicate if you noticed any quality decrease for earlier categories")
            else:
                # All validation passed, start processing
                complete_study_with_processing_indicators(
                    age, gender, quality_patterns, better_categories, worse_categories,
                    learning_hypothesis, better_learned, rankings, caption_preference,
                    summary_assessment, forgetting_evidence, final_feedback
                )

def complete_study_with_processing_indicators(age, gender, quality_patterns, better_categories, worse_categories,
                                            learning_hypothesis, better_learned, rankings, caption_preference,
                                            summary_assessment, forgetting_evidence, final_feedback):
    """Complete the study with proper processing indicators"""
    
    # Disable the button immediately to prevent double-submission
    st.session_state.processing_completion = True
    
    try:
        # Create placeholder for status updates
        status_placeholder = st.empty()
        progress_placeholder = st.empty()
        
        with status_placeholder:
            st.info("🔄 **Processing your submission...** Please don't close this window.")
        
        # Step 1: Prepare data
        with progress_placeholder:
            show_progress_bar(6, 1, "Preparing final questionnaire data")
        
        time.sleep(0.5)  # Brief pause for UI update
        
        final_data = {
            'participant_id': st.session_state.participant_id,
            'response_type': 'final_questionnaire',
            'age_group': age,
            'gender': gender,
            'quality_patterns_noticed': quality_patterns,
            'better_categories': ", ".join(better_categories) if better_categories else "",
            'worse_categories': ", ".join(worse_categories) if worse_categories else "",
            'learning_hypothesis': learning_hypothesis,
            'better_learned_categories': ", ".join(better_learned) if better_learned else "",
            'accessories_rank': rankings.get("Accessories", ""),
            'bottoms_rank': rankings.get("Bottoms", ""),
            'dresses_rank': rankings.get("Dresses", ""),
            'outerwear_rank': rankings.get("Outerwear", ""),
            'shoes_rank': rankings.get("Shoes", ""),
            'tops_rank': rankings.get("Tops", ""),
            'caption_preference': caption_preference,
            'summary_assessment_rating': summary_assessment,
            'forgetting_evidence': forgetting_evidence,
            'final_feedback': final_feedback,
            'completion_timestamp': datetime.now().isoformat()
        }
        
        # Step 2: Save to CSV
        with progress_placeholder:
            show_progress_bar(6, 2, "Saving backup CSV files")
        
        csv_success = False
        csv_files = {}
        
        try:
            csv_success, main_file, category_file, summary_file = save_final_complete_csv(final_data)
            csv_files = {
                'main': main_file,
                'category': category_file,
                'summary': summary_file
            }
        except Exception as e:
            st.error(f"❌ CSV save failed: {e}")
        
        # Step 3: Prepare Google Sheets data
        with progress_placeholder:
            show_progress_bar(6, 3, "Preparing data for Google Sheets")
        
        time.sleep(0.5)
        
        # Step 4: Save main responses to Google Sheets
        with progress_placeholder:
            show_progress_bar(6, 4, "Saving main responses to Google Sheets")
        
        main_sheets_success = False
        try:
            with st.spinner("Uploading main responses to Google Sheets..."):
                main_sheets_success = save_main_responses_to_sheets_fixed(final_data)
        except Exception as e:
            st.error(f"❌ Main responses Google Sheets save failed: {e}")
        
        # Step 5: Save category assessments to Google Sheets
        with progress_placeholder:
            show_progress_bar(6, 5, "Saving category assessments to Google Sheets")
        
        category_sheets_success = False
        try:
            with st.spinner("Uploading category assessments to Google Sheets..."):
                category_sheets_success = save_category_assessments_to_sheets()
        except Exception as e:
            st.error(f"❌ Category assessments Google Sheets save failed: {e}")
        
        # Step 6: Finalize and show results
        with progress_placeholder:
            show_progress_bar(6, 6, "Finalizing submission")
        
        time.sleep(0.5)
        
        # Clear processing indicators
        status_placeholder.empty()
        progress_placeholder.empty()
        
        # Determine overall success
        sheets_success = main_sheets_success and category_sheets_success
        
        # Show detailed success/failure status
        st.markdown("## 📊 **Submission Status**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 💾 **Local Backup (CSV)**")
            if csv_success:
                st.success("✅ **CSV files saved successfully!**")
                if csv_files['main']:
                    st.info(f"📄 Main responses: `{csv_files['main']}`")
                if csv_files['category']:
                    st.info(f"📄 Category assessments: `{csv_files['category']}`")
                if csv_files['summary']:
                    st.info(f"📄 Summary: `{csv_files['summary']}`")
            else:
                st.error("❌ **CSV backup failed**")
        
        with col2:
            st.markdown("### ☁️ **Cloud Storage (Google Sheets)**")
            if sheets_success:
                st.success("✅ **Google Sheets upload successful!**")
                st.info("📊 Main responses uploaded")
                st.info("📊 Category assessments uploaded")
            elif main_sheets_success or category_sheets_success:
                st.warning("⚠️ **Partial Google Sheets upload**")
                if main_sheets_success:
                    st.info("✅ Main responses uploaded")
                else:
                    st.error("❌ Main responses failed")
                if category_sheets_success:
                    st.info("✅ Category assessments uploaded")
                else:
                    st.error("❌ Category assessments failed")
            else:
                st.error("❌ **Google Sheets upload failed**")
        
        # Overall status message
        if csv_success and sheets_success:
            st.balloons()
            st.success("🎉 **All data saved successfully!** Your responses are securely stored in both local CSV files and Google Sheets.")
        elif csv_success:
            st.success("✅ **Data saved to CSV backup!** Google Sheets had issues, but your responses are safely stored locally.")
        elif sheets_success:
            st.success("✅ **Data saved to Google Sheets!** CSV backup had issues, but your responses are stored in the cloud.")
        else:
            st.error("❌ **Error saving data.** Please contact the researcher immediately.")
            st.error("**Researcher contact:** akash.kumar@dfki.de")
        
        # Success summary
        category_assessments_count = len(st.session_state.get('category_assessments', []))
        st.markdown(f"""
        ---
        ## 🎉 **Study Completed Successfully!**
        
        **Your Contribution:**
        - **Participant ID:** {st.session_state.participant_id}
        - **Images Evaluated:** {len(st.session_state.responses)}
        - **Captions Rated:** {len(st.session_state.responses) * 3}
        - **Category Assessments:** {category_assessments_count}
        - **Completion Time:** {final_data['completion_timestamp']}
        
        **Thank you for contributing to AI research!** 🙏
        
        ---
        
        **🔬 About Your Data:**
        - All responses are anonymous and secure
        - Data will be used for academic research only
        - Results may be published in scientific conferences/journals
        - No personal information is stored or shared
        """)
        
        st.session_state.study_complete = True
        st.session_state.processing_completion = False
        
    except Exception as e:
        # Clear processing state on error
        st.session_state.processing_completion = False
        st.error(f"❌ **Critical error during submission:** {str(e)}")
        st.error("**Please contact the researcher immediately:** akash.kumar@dfki.de")
        st.error(f"**Participant ID:** {st.session_state.participant_id}")

def show_transition_message(message="Loading next image..."):
    # Check if this is a category transition
    banner_value = st.session_state.get("show_transition_banner", "")
    if isinstance(banner_value, str) and banner_value.startswith("category_transition_"):
        category = banner_value.split("_")[-1]
        message = f"Starting {category} category..."
    elif banner_value == "final_category_completed":
        message = "All categories completed! Proceeding to final questionnaire..."
    
    st.markdown(f"""
    <div class="success-message">
        <h4>✅ Response Saved!</h4>
        <p>{message}</p>
    </div>

    <a id="scroll-top"></a>
    """, unsafe_allow_html=True)

    st.markdown("""
    <script>
    function scrollAndTriggerRerun() {
        document.querySelector('#scroll-top').scrollIntoView({ behavior: 'smooth' });
        setTimeout(() => {
            window.parent.postMessage({ type: 'SCROLL_DONE' }, '*');
        }, 500);
    }
    scrollAndTriggerRerun();
    </script>
    """, unsafe_allow_html=True)

    # Simple time-based transition instead of streamlit_js_eval
    time.sleep(1.5)
    st.session_state.show_transition_banner = False
    st.rerun()

# ======================== MAIN APP LOGIC ========================

def main():
    
    st.markdown("""
    <style>
    /* Force readable text colors */
    .stApp {
        color: #262730 !important;
        background: #FFFFFF !important;
    }
    
    /* All text elements */
    p, li, span, div, h1, h2, h3, h4, h5, h6 {
        color: #262730 !important;
    }
    
    /* Card backgrounds */
    .info-card {
        background: #F8F9FA !important;
        color: #262730 !important;
        border: 1px solid #DEE2E6 !important;
    }
    
    /* Make sure text is always visible */
    .element-container {
        color: #262730 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<a id="scroll-top"></a>', unsafe_allow_html=True)

    if not st.session_state.study_started:
        show_welcome_page()
    elif st.session_state.get("study_complete", False):
        st.success("Study completed! Thank you for your participation.")
    elif st.session_state.get("show_transition_banner", False):
        if st.session_state.show_transition_banner == "start_study":
            show_transition_message("Starting study...")
        else:
            show_transition_message()
    else:
        show_study_interface()

if __name__ == "__main__":
    main()