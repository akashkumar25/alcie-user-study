#!/usr/bin/env python3
"""
ALCIE User Study Interface - Streamlit App
Pure human evaluation of AI-generated fashion captions
"""

import streamlit as st
import json
import pandas as pd
import numpy as np
import random
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="ALCIE User Study",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for professional look
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: 600;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .caption-box {
        background-color: #f8f9fa;
        padding: 1.2rem;
        border-radius: 8px;
        margin: 0.8rem 0;
        border-left: 4px solid #1f77b4;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        font-size: 1.1rem;
        line-height: 1.4;
    }
    .category-tag {
        display: inline-block;
        background-color: #17a2b8;
        color: white;
        padding: 0.4rem 0.8rem;
        border-radius: 6px;
        font-size: 0.9rem;
        font-weight: 600;
        margin-right: 0.5rem;
    }
    .instruction-box {
        background-color: #e8f4f8;
        padding: 1.2rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid #17a2b8;
    }
    .progress-info {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        text-align: center;
    }
    .stSelectSlider > div > div > div {
        background-color: #e3f2fd;
    }
</style>
""", unsafe_allow_html=True)

class ALCIEStudyApp:
    def __init__(self):
        self.study_dataset_file = "alcie_study_dataset.json"
        self.initialize_session_state()
    
    def initialize_session_state(self):
        """Initialize all session state variables"""
        if 'study_data' not in st.session_state:
            st.session_state.study_data = self.load_study_data()
            st.session_state.current_sample = 0
            st.session_state.responses = []
            st.session_state.participant_id = f"P{random.randint(1000, 9999)}"
            st.session_state.study_started = False
            st.session_state.consent_given = False
    
    def load_study_data(self):
        """Load and randomize study dataset"""
        try:
            with open(self.study_dataset_file, 'r') as f:
                data = json.load(f)
            
            # Randomize sample order for each participant
            samples = data['samples'].copy()
            random.shuffle(samples)
            data['samples'] = samples
            
            return data
        except FileNotFoundError:
            st.error(f"❌ Study dataset not found: {self.study_dataset_file}")
            st.info("Please make sure you've run the data processor first!")
            st.stop()
        except Exception as e:
            st.error(f"❌ Error loading study data: {e}")
            st.stop()
    
    def show_welcome_page(self):
        """Welcome page with consent and instructions"""
        st.markdown('<h1 class="main-header">ALCIE User Study</h1>', unsafe_allow_html=True)
        st.markdown('<p class="sub-header">Active Learning for Continual Image Captioning Enhancement</p>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Study overview
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📋 Study Overview")
            st.markdown("""
            **Purpose:** Evaluate AI-generated fashion captions from different learning strategies
            
            **Duration:** 20-25 minutes
            
            **Your task:** 
            - View fashion images and their categories
            - Rate 3 AI-generated captions per image
            - Select which caption you think is best
            """)
        
        with col2:
            st.markdown("### 🏛️ Research Team")
            st.markdown("""
            **Institution:** DFKI (German Research Center for AI)
            
            **Researcher:** Akash Kumar
            
            **Supervisor:** Aliki Anagnostopoulou
            
            **Privacy:** All responses are completely anonymous
            """)
        
        # Detailed instructions
        st.markdown("### 📊 How to Rate Captions")
        
        instructions = """
        For each image, you'll see **3 different AI-generated captions** labeled A, B, and C.  
        Please rate each caption on **4 dimensions** using a 1-5 scale:
        
        - **Relevance** (1=Completely wrong → 5=Perfectly accurate)
        - **Fluency** (1=Very awkward English → 5=Very natural English) 
        - **Descriptiveness** (1=Too vague → 5=Very detailed and informative)
        - **Novelty** (1=Very boring → 5=Very creative and interesting)
        
        Then select which caption you think is **best overall**.
        """
        
        st.markdown('<div class="instruction-box">' + instructions + '</div>', unsafe_allow_html=True)
        
        # Fashion interest screening
        st.markdown("### 👗 Background Information")
        fashion_interest = st.selectbox(
            "How would you describe your interest in fashion?",
            ["", "Very interested", "Somewhat interested", "Moderately interested", 
             "Slightly interested", "Not particularly interested"],
            key="fashion_interest"
        )
        
        # Consent section
        st.markdown("### ✅ Informed Consent")
        st.markdown("""
        **By participating, I understand that:**
        - My participation is completely voluntary
        - I can stop at any time without any consequences
        - My responses will be analyzed anonymously for research purposes
        - Results may be published in academic papers and presentations
        - No personal identifying information will be collected
        - This research is conducted by DFKI for advancing AI technology
        """)
        
        consent_checkbox = st.checkbox(
            "I have read the above information and consent to participate in this research study", 
            key="consent"
        )
        
        # Start study button
        if consent_checkbox and fashion_interest:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🚀 Start Study", type="primary", use_container_width=True):
                    st.session_state.consent_given = True
                    st.session_state.study_started = True
                    st.session_state.fashion_interest = fashion_interest
                    st.rerun()
        elif fashion_interest:
            st.info("📝 Please check the consent box to continue")
        else:
            st.info("📝 Please select your fashion interest level to continue")
    
    def show_study_interface(self):
        """Main study interface for caption evaluation"""
        
        # Check if study is complete
        if st.session_state.current_sample >= len(st.session_state.study_data['samples']):
            self.show_completion_page()
            return
        
        current_sample = st.session_state.study_data['samples'][st.session_state.current_sample]
        
        # Header
        st.markdown('<h1 class="main-header">Fashion Caption Evaluation</h1>', unsafe_allow_html=True)
        
        # Progress tracking
        progress = (st.session_state.current_sample + 1) / len(st.session_state.study_data['samples'])
        current_num = st.session_state.current_sample + 1
        total_num = len(st.session_state.study_data['samples'])
        
        st.markdown(f'<div class="progress-info">', unsafe_allow_html=True)
        st.progress(progress)
        st.markdown(f"**Progress:** Image {current_num} of {total_num}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Category and phase information
        category = current_sample['category']
        cf_risk = current_sample['cf_risk']
        phase = current_sample['introduced_phase']
        
        st.markdown(
            f'<span class="category-tag">{category.upper()}</span>'
            f'<span style="color: #666; font-size: 0.9rem;">Learning Phase {phase} • '
            f'{cf_risk.replace("_", " ").title()} Forgetting Risk</span>', 
            unsafe_allow_html=True
        )
        
        st.markdown("---")
        
        # Image placeholder (since we're not using actual images)
        st.markdown("### 👗 Fashion Item")
        st.info(f"**Category:** {category.upper()} | **Image ID:** {current_sample['image_id']}")
        st.markdown("*Imagine a typical fashion item from this category while evaluating the captions below.*")
        
        # Caption evaluation section
        self.show_caption_evaluation(current_sample)
    
    def show_caption_evaluation(self, sample):
        """Display caption evaluation interface"""
        
        st.markdown("### 📝 Caption Evaluation")
        st.markdown("Please rate each caption on all four dimensions, then select your favorite:")
        
        # Get predictions and randomize their order
        predictions = sample['predictions']
        methods = list(predictions.keys())
        random.shuffle(methods)  # Different order for each participant
        
        # Store method mapping for this sample
        caption_labels = [f"Caption {chr(65 + i)}" for i in range(len(methods))]
        method_mapping = {caption_labels[i]: methods[i] for i in range(len(methods))}
        
        responses = {}
        
        # Evaluate each caption
        for i, method in enumerate(methods):
            label = caption_labels[i]
            caption_text = predictions[method]
            
            st.markdown(f"#### {label}")
            st.markdown(f'<div class="caption-box">"{caption_text}"</div>', unsafe_allow_html=True)
            
            # Rating scales in columns
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                relevance = st.select_slider(
                    "Relevance",
                    options=[1, 2, 3, 4, 5],
                    value=3,
                    key=f"relevance_{i}",
                    help="How accurately does it describe the fashion item?"
                )
            
            with col2:
                fluency = st.select_slider(
                    "Fluency",
                    options=[1, 2, 3, 4, 5],
                    value=3,
                    key=f"fluency_{i}",
                    help="How natural and well-written is the English?"
                )
            
            with col3:
                descriptiveness = st.select_slider(
                    "Descriptiveness",
                    options=[1, 2, 3, 4, 5],
                    value=3,
                    key=f"descriptiveness_{i}",
                    help="How detailed and informative is it?"
                )
            
            with col4:
                novelty = st.select_slider(
                    "Novelty",
                    options=[1, 2, 3, 4, 5],
                    value=3,
                    key=f"novelty_{i}",
                    help="How creative and interesting is the description?"
                )
            
            responses[method] = {
                'relevance': relevance,
                'fluency': fluency,
                'descriptiveness': descriptiveness,
                'novelty': novelty
            }
            
            st.markdown("---")
        
        # Overall preference selection
        st.markdown("### 🏆 Overall Preference")
        best_caption_label = st.radio(
            "Which caption do you think is **best overall**?",
            options=caption_labels,
            key="best_caption",
            horizontal=True
        )
        
        # Optional comments
        comment = st.text_area(
            "💭 Additional Comments (Optional)",
            placeholder="Any thoughts about these captions or the fashion item?",
            key="comment",
            max_chars=300,
            height=80
        )
        
        # Submit button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("✅ Submit & Continue", type="primary", use_container_width=True):
                best_method = method_mapping[best_caption_label]
                self.save_response(sample, responses, best_method, comment, method_mapping)
                st.session_state.current_sample += 1
                
                # Clear form state for next sample
                for key in list(st.session_state.keys()):
                    if key.startswith(('relevance_', 'fluency_', 'descriptiveness_', 'novelty_', 'best_caption', 'comment')):
                        del st.session_state[key]
                
                st.rerun()
    
    def save_response(self, sample, responses, best_method, comment, method_mapping):
        """Save participant response data"""
        
        response_data = {
            'participant_id': st.session_state.participant_id,
            'fashion_interest': st.session_state.fashion_interest,
            'sample_number': st.session_state.current_sample + 1,
            'image_id': sample['image_id'],
            'category': sample['category'],
            'introduced_phase': sample['introduced_phase'],
            'cf_risk': sample['cf_risk'],
            'method_mapping': method_mapping,  # Which caption letter corresponds to which method
            'ratings': responses,  # All ratings for all methods
            'best_caption_method': best_method,
            'comment': comment,
            'timestamp': pd.Timestamp.now().isoformat()
        }
        
        st.session_state.responses.append(response_data)
    
    def show_completion_page(self):
        """Study completion and final questionnaire"""
        
        st.markdown('<h1 class="main-header">🎉 Study Complete!</h1>', unsafe_allow_html=True)
        st.markdown('<p class="sub-header">Thank you for your valuable contribution to AI research!</p>', unsafe_allow_html=True)
        
        # Completion summary
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Images Evaluated", len(st.session_state.responses))
        with col2:
            st.metric("Captions Rated", len(st.session_state.responses) * 3)
        with col3:
            st.metric("Participant ID", st.session_state.participant_id)
        
        st.markdown("---")
        
        # Final questionnaire
        st.markdown("### 📋 Final Questions")
        
        # Overall observations
        quality_patterns = st.radio(
            "Did you notice any patterns in caption quality across different fashion categories?",
            ["Yes, clear differences between categories", 
             "Some differences", 
             "No clear patterns", 
             "Not sure"],
            key="quality_patterns"
        )
        
        if quality_patterns in ["Yes, clear differences between categories", "Some differences"]:
            better_categories = st.multiselect(
                "Which fashion categories seemed to have better captions overall?",
                ["Accessories", "Bottoms", "Dresses", "Outerwear", "Shoes", "Tops"],
                key="better_categories"
            )
        else:
            better_categories = []
        
        # Caption style preferences
        caption_preference = st.radio(
            "What type of fashion captions do you prefer?",
            ["More detailed and descriptive", 
             "More creative and interesting", 
             "More accurate and factual", 
             "Balanced across all aspects"],
            key="caption_preference"
        )
        
        # AI system evaluation
        ai_readiness = st.select_slider(
            "How ready do you think AI caption systems are for fashion e-commerce?",
            options=["Not ready", "Somewhat ready", "Moderately ready", "Very ready", "Completely ready"],
            value="Moderately ready",
            key="ai_readiness"
        )
        
        # Final feedback
        final_feedback = st.text_area(
            "Any final thoughts about AI-generated fashion captions or this study?",
            placeholder="Optional feedback...",
            key="final_feedback",
            height=100
        )
        
        # Complete study
        if st.button("💾 Complete Study", type="primary", use_container_width=True):
            self.save_final_data(quality_patterns, better_categories, caption_preference, ai_readiness, final_feedback)
            self.export_and_thank()
    
    def save_final_data(self, quality_patterns, better_categories, caption_preference, ai_readiness, final_feedback):
        """Save final questionnaire responses"""
        
        final_data = {
            'participant_id': st.session_state.participant_id,
            'response_type': 'final_questionnaire',
            'quality_patterns_noticed': quality_patterns,
            'better_categories': better_categories,
            'caption_preference': caption_preference,
            'ai_readiness_rating': ai_readiness,
            'final_feedback': final_feedback,
            'completion_timestamp': pd.Timestamp.now().isoformat(),
            'total_study_time_minutes': 'approximately_20_25'
        }
        
        st.session_state.responses.append(final_data)
    
    def export_and_thank(self):
        """Export data and show thank you message"""
        
        try:
            # Separate main responses from final questionnaire
            main_responses = [r for r in st.session_state.responses if r.get('response_type') != 'final_questionnaire']
            final_response = [r for r in st.session_state.responses if r.get('response_type') == 'final_questionnaire'][0]
            
            # Create comprehensive dataframe
            responses_df = pd.DataFrame(main_responses)
            
            # Flatten ratings into separate columns
            for idx, response in enumerate(main_responses):
                for method, ratings in response['ratings'].items():
                    for metric, score in ratings.items():
                        responses_df.loc[idx, f"{method}_{metric}"] = score
            
            # Add final questionnaire data to each row
            for col, value in final_response.items():
                if col not in ['participant_id', 'response_type']:
                    responses_df[col] = value
            
            # Generate filename
            filename = f"alcie_responses_{st.session_state.participant_id}.csv"
            csv_data = responses_df.to_csv(index=False)
            
            # Success message
            st.success("🎉 **Study completed successfully!**")
            
            # Download button
            st.download_button(
                label="📥 Download Your Responses (CSV)",
                data=csv_data,
                file_name=filename,
                mime="text/csv",
                use_container_width=True
            )
            
            # Thank you message
            st.markdown("---")
            st.markdown("### 🙏 Thank You!")
            
            st.markdown("""
            Your participation helps advance AI research in fashion and computer vision!
            
            **What happens next:**
            - Your anonymous responses will be analyzed with other participants
            - Results will contribute to research on continual learning and AI captioning
            - Findings may be published in academic conferences and journals
            
            **Questions or concerns?** Contact: akkumar@dfki.de
            
            ---
            
            **DFKI - German Research Center for Artificial Intelligence**  
            *Advancing AI for the benefit of society*
            """)
            
            # Reset button for new participant
            if st.button("🔄 Reset for New Participant"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
                
        except Exception as e:
            st.error(f"❌ Error saving responses: {e}")
            st.info("Your responses have been recorded in the session. Please contact the researcher.")
    
    def run(self):
        """Main application runner"""
        
        if not st.session_state.consent_given or not st.session_state.study_started:
            self.show_welcome_page()
        else:
            self.show_study_interface()

# Main application entry point
def main():
    """Initialize and run the ALCIE study app"""
    app = ALCIEStudyApp()
    app.run()

if __name__ == "__main__":
    main()