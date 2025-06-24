#!/usr/bin/env python3
"""
ALCIE User Study - Minimal Changes Version (Addresses Sara-Jane's Feedback)
Fixed: Design, Consent Split, Slider Bias, Required Reasoning
Run with: streamlit run alcie_study_main.py
"""

import streamlit as st

# Page configuration - MUST BE FIRST
st.set_page_config(
    page_title="ALCIE User Study",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Import other modules
import json
import pandas as pd
import random
import os
from datetime import datetime
from PIL import Image
import time
from streamlit_js_eval import streamlit_js_eval

# Import our custom modules
from ui_components import show_dfki_consent_page, show_task_instructions, show_study_interface, show_completion_page, show_transition_message, should_show_category_assessment, show_category_transition_assessment
from data_handler import save_progress_to_csv, save_final_complete_csv, save_all_to_google_sheets, send_completion_emails

# ======================== IMPROVED CSS ========================
def load_css():
    """Load CSS from external file"""
    try:
        with open('src/style.css', 'r') as f:
            css_content = f.read()
        st.markdown(f'<style>{css_content}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.error("❌ style.css file not found. Please ensure it's in the same directory as this script.")
        # Fallback minimal CSS
        st.markdown("""
        <style>
        .stApp { background-color: #1F2937 !important; color: #FFFFFF !important; }
        body, p, li, span, div, label, h1, h2, h3, h4, h5, h6 { color: #FFFFFF !important; }
        </style>
        """, unsafe_allow_html=True)

# ======================== APP CLASS (Unchanged from old code) ========================

class ALCIEStreamlitApp:
    def __init__(self):
        self.study_dataset_file = "data/alcie_study_dataset.json"
        self.images_directory = "images/"
        self.load_data()
        
    def load_data(self):
        """Load and sort study data"""
        try:
            with open(self.study_dataset_file, 'r') as f:
                data = json.load(f)
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

# ======================== SESSION STATE (Minimal Changes) ========================

def init_session_state():
    if 'study_started' not in st.session_state:
        st.session_state.study_started = False
        st.session_state.show_instructions = False  # NEW: Track instructions page
        st.session_state.current_sample_idx = 0
        st.session_state.responses = []
        timestamp_ms = int(time.time() * 1000)
        random_suffix = random.randint(100, 999)
        st.session_state.participant_id = f"P{timestamp_ms}{random_suffix}"
        st.session_state.fashion_interest = None
        st.session_state.consent_given = False  # NEW: Track consent separately
        st.session_state.study_complete = False
        st.session_state.processing_completion = False
        st.session_state.caption_transition_type = None  # "next_caption", "final_comparison", "next_image"




# ======================== MAIN LOGIC (Updated for new flow) ========================

def main():
    """Main application logic - WITH WORKING SCROLL FROM OLD CODE"""
    init_session_state()
    load_css()
    
    # WORKING TRANSITION HANDLING FROM OLD CODE
    if st.session_state.get("show_transition_banner", False):
        if st.session_state.show_transition_banner == "start_study":
            show_transition_message("Starting study...")
        else:
            show_transition_message()
        return  # CRITICAL: Prevents other UI from rendering
    
    st.markdown('<a id="scroll-top"></a>', unsafe_allow_html=True)

    # Initialize app data when study starts
    if st.session_state.study_started and 'app_study_data' not in st.session_state:
        st.session_state.app_instance = app
        st.session_state.app_study_data = app.study_data
        st.session_state.total_samples = len(app.study_data)

    # MAIN FLOW (rest stays the same)
    if not st.session_state.consent_given:
        show_dfki_consent_page()
    elif st.session_state.show_instructions:
        show_task_instructions()
    elif st.session_state.get("study_complete", False):
        st.success("Study completed! Thank you for your participation.")
    elif st.session_state.get("show_category_assessment", False):
        show_category_transition_assessment(
            st.session_state.assessment_previous_category,
            st.session_state.assessment_current_category
        )
    elif st.session_state.study_started:
        show_study_interface(app)
    else:
        st.error("❌ Navigation error. Please refresh the page.")

if __name__ == "__main__":
    main()