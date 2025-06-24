"""
UI Components for ALCIE Study - Addresses Sara-Jane's Feedback
- Split consent and instructions (main feedback point)
- Unbiased sliders (no default values)
- Required reasoning for caption choices
- Scale explanations next to sliders
"""

import streamlit as st
from datetime import datetime
import time
from streamlit_js_eval import streamlit_js_eval
from data_handler import save_progress_to_csv, save_all_to_google_sheets, save_final_complete_csv, send_completion_emails

# ======================== STEP 1: DFKI CONSENT PAGE (NEW - Sara-Jane's Feedback) ========================

def show_dfki_consent_page():
    """Show DFKI-compliant consent form - Enhanced with Sara-Jane's requirements"""
    
    st.markdown("""
    <div class="main-header">
        <h1>🔬 Research Study Consent</h1>
        <h3>Active Learning for Continual Image Captioning Enhancement</h3>
        <p style="color: #D1D5DB; margin-top: 0.5rem;">
            German Research Center for Artificial Intelligence (DFKI)
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Study Purpose
    st.markdown("""
    ### **🎯 Study Purpose**
    
    This study investigates how artificial intelligence systems learn to describe fashion items 
    and whether they maintain quality when learning new categories over time.
    
    **Your role:** Evaluate AI-generated fashion captions and provide feedback on their quality.
    """)
    
    # Procedures
    st.markdown("""
    ### **📋 What You'll Do**
    
    1. **View 24 fashion images** across 6 categories
    2. **Rate AI-generated captions** on 4 criteria  
    3. **Complete brief questionnaires** about your experience
    4. **Duration:** 15-20 minutes
    """)
    
    # Data Collection & Privacy
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### **📊 Data Collected**
        
        **What we collect:**
        - Fashion interest level (required)
        - Age group (required)
        - Gender (required)
        - Rating scores (1-5 scales)
        - Caption preferences 
        - Optional written feedback
        
        **What we DON'T collect:**
        - Name, email, or personal details
        - IP addresses or location data
        - Any identifying information
        """)
    
    with col2:
        st.markdown("""
        ### **🛡️ Privacy Protection**
        
        - **Complete anonymity** - randomly generated participant IDs only
        - **Secure data storage** - research-grade protection standards
        - **Academic use only** - results published in scientific papers
        - **Your rights** - can withdraw consent for future publications
        """)
    
    # Enhanced sections (Sara-Jane's requirements)
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        ### **🔒 How Anonymity is Ensured**
        
        **Anonymization Process:**
        - No personal data collected (no names, emails, IP addresses)
        - Random participant IDs generated (e.g., P1234567890123)  
        - Data stored separately from any identifying information
        - No way to link responses back to individual participants
        
        **Data Storage:**
        - Secure DFKI servers in Germany
        - Encrypted storage with researcher-only access
        - Regular security audits and backups
        """)

    with col2:
        st.markdown("""
        ### **📅 Data Retention & Rights**
        
        **Retention Period:**
        - Anonymized data retained for **5 years** for research validation
        - Raw data permanently deleted after anonymization
        - Participants may request deletion before anonymization
        
        **Your Rights (GDPR):**
        - Withdraw consent anytime: akash.kumar@dfki.de
        - Request data deletion before publication
        - File complaints with data protection authority
        """)

    # Legal compliance details
    st.markdown("""
    ### **⚖️ Legal Basis & Compliance**

    **GDPR Compliance:**
    - **Legal basis:** Consent for research purposes (Article 6.1.a)
    - **Data controller:** Deutsches Forschungszentrum für Künstliche Intelligenz GmbH
    - **Address:** Trippstadter Straße 122, 67663 Kaiserslautern, Germany
    - **Data Protection Officer:** datenschutz@dfki.de
    - **Supervisory Authority:** LfDI Baden-Württemberg

    **Study Information:**
    - **Study Reference:** ALCIE-CL-2025 (DFKI Internal)
    - **Ethics Review:** Approved by DFKI Internal Review Process  
    - **Duration:** Data collection January-March 2025
    """)

    # Enhanced contact information
    st.markdown("""
    ### **📞 Complete Contact Information**

    **Research Team:**
    - **Principal Investigator:** Akash Kumar, M.Sc. (akash.kumar@dfki.de)
    - **Academic Supervisor:** Aliki Anagnostopoulou (aliki.anagnostopoulou@dfki.de)

    **Institution:**
    - **Organization:** DFKI - German Research Center for Artificial Intelligence
    - **Address:** Trippstadter Straße 122, 67663 Kaiserslautern, Germany  
    - **Phone:** +49 631 205-3511
    - **Website:** www.dfki.de

    **Data Protection:**
    - **DFKI Data Protection Officer:** datenschutz@dfki.de
    - **External Authority:** LfDI Baden-Württemberg
    """)

    # Scientific publication details
    st.markdown("""
    ### **📚 Research Output & Publication**

    **Scientific Publications:**
    - Results published in peer-reviewed AI/ML conferences (ACL, EMNLP, CVPR)
    - Potential journal publication in computational linguistics
    - Only anonymized aggregate data and statistical summaries published

    **Data Sharing:**
    - Anonymized data may be shared with academic collaborators
    - Individual responses never published in identifiable form  
    - Research code and datasets made available for scientific replication

    **Research Impact:**
    - Advances continual learning in AI systems
    - Improves fashion e-commerce recommendation systems
    - Contributes to human-like AI language understanding
    """)
    
    st.markdown("---")
    
    # Required Information
    st.markdown("### **📝 Required Information**")
    
    fashion_interest = st.radio(
        "How interested are you in fashion? (Required for research context)",
        ["Very interested", "Somewhat interested", "Moderately interested", 
         "Slightly interested", "Not particularly interested"],
        index=None,
        help="This helps us understand participant background and interpret responses"
    )

    # Consent details above checkbox for clarity
    consent = st.checkbox(
        "I have read and understood the information above, and I voluntarily consent to participate in this research study conducted by DFKI.\n\n\n\n"
        "I confirm that:\n\n"
        "• I am over 18 years of age and legally able to provide consent\n\n"
        "• I understand my participation is voluntary and I may withdraw anytime\n\n"
        "• I understand how my data will be anonymized and used for research\n\n"
        "• I consent to publication of anonymized results in scientific journals",
        help="Required: Please confirm that you understand and agree to participate in this research",
        key="participant_consent"
    )
    
    # Success message when consent is given
    if consent:
        st.markdown("""
        <div style="background: rgba(5, 150, 105, 0.1); border: 1px solid #10B981; 
                    border-radius: 8px; padding: 1rem; margin: 1rem 0; text-align: center;">
            <p style="margin: 0; color: #A7F3D0; font-weight: 600;">
                ✅ <strong>Consent Recorded:</strong> Your agreement has been noted. You may proceed to the study instructions.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    if st.button("Continue to Study Instructions", type="primary", use_container_width=True):
        if not consent:
            st.error("❌ Please provide your consent to participate")
        elif not fashion_interest:
            st.error("❌ Please indicate your fashion interest level")
        else:
            # Store data
            st.session_state.consent_given = True
            st.session_state.fashion_interest = fashion_interest
            st.session_state.show_instructions = True
                        
            # USE WORKING TRANSITION SYSTEM FROM OLD CODE
            st.session_state.show_transition_banner = True
            st.rerun()


# ======================== STEP 2: TASK INSTRUCTIONS (NEW - Separated) ========================

def show_task_instructions():
    """Show detailed task instructions - Separated from consent"""
    
    st.markdown("""
    <style>
    /* Force page to start at top */
    html, body {
        scroll-behavior: smooth !important;
    }
    /* Ensure main container starts at top */
    .main .block-container {
        margin-top: 0 !important;
        padding-top: 1rem !important;
    }
    </style>
    <div id="instructions-top" style="height: 1px; margin-top: -1px;"></div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="main-header">
        <h1>📚 Study Instructions</h1>
        <h3>Task Overview & Rating Guidelines</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Task Overview
    st.markdown("## 🎯 Your Task")
    st.markdown("""
    You will evaluate **AI-generated fashion captions** by viewing images and rating different descriptions.
    
    **What you'll do:**
    1. View **24 fashion images** (4 per category)
    2. Read **3 different AI captions** for each image  
    3. **Rate each caption** on 4 criteria using 1-5 scales
    4. **Arrange the captions from best to worst** for each image and explain your ranking
    5. Complete **brief assessments** between categories
    """)
    
    # Rating Criteria (Sara-Jane: "put scale information next to scales, not overview")
    st.markdown("## 📊 Rating Criteria")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### **1. Relevance (1-5)**
        *How accurately does this caption describe what you see?*
        - **5 = Perfect** - Completely accurate
        - **3 = Okay** - Somewhat accurate  
        - **1 = Very poor** - Completely wrong
        
        ### **2. Fluency (1-5)**  
        *How natural and well-written is the English?*
        - **5 = Perfect** - Natural, grammatically correct
        - **3 = Okay** - Understandable but awkward
        - **1 = Very poor** - Hard to understand
        """)
    
    with col2:
        st.markdown("""
        ### **3. Descriptiveness (1-5)**
        *How much useful detail does this caption provide?*
        - **5 = Perfect** - Rich, comprehensive detail
        - **3 = Okay** - Some helpful details
        - **1 = Very poor** - Very vague, minimal detail
        
        ### **4. Novelty (1-5)**
        *How creative and engaging is this caption?*
        - **5 = Perfect** - Very creative, engaging
        - **3 = Okay** - Somewhat interesting
        - **1 = Very poor** - Very generic, dull
        """)
    
    # Example Task
    st.markdown("## 💡 Example")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.image("images/image.png", caption="Category: Shoes", width=250)
    
    with col2:
        st.markdown("""
        **Caption A:** "Red sneakers"  
        → Relevance: 4, Fluency: 5, Descriptiveness: 2, Novelty: 1

        **Caption B:** "Vibrant crimson athletic footwear with white rubber soles"  
        → Relevance: 5, Fluency: 5, Descriptiveness: 5, Novelty: 4

        **Caption C:** "Footwear for walking"  
        → Relevance: 2, Fluency: 4, Descriptiveness: 1, Novelty: 1

        **Arrange (best to worst):** Caption B > Caption A > Caption C  
        **Why:** "Caption B is most accurate and detailed while using engaging language"
        """)
    
    # Important Guidelines  
    st.markdown("## ⚠️ Important Guidelines")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Rating Requirements:**
        - **Select ALL ratings** – No default values; you must choose for each criterion
        - **Rate independently** – Judge each caption on its own merit
        - **Arrange captions from best to worst** – Required for each image
        - **Explain your ranking** – Why did you order them this way?
        """)
    
    with col2:
        st.markdown("""
        **Study Flow:**
        - **Progress tracking** shows your current position
        - **Category transitions** with brief quality assessments  
        - **Takes 25-30 minutes** total completion time
        """)
    
    # Background Confirmation
    st.markdown(f"""
    ## 👤 Your Information
    **Fashion Interest:** {st.session_state.fashion_interest}  
    **Participant ID:** {st.session_state.participant_id}  
    """)
    
    # Start Button
    if st.button("🚀 Start Fashion Caption Study", type="primary", use_container_width=True):
        st.session_state.study_started = True
        st.session_state.show_instructions = False
        
        # USE WORKING TRANSITION SYSTEM FROM OLD CODE
        st.session_state.show_transition_banner = "start_study"
        st.rerun()

# ======================== STEP 3: MAIN STUDY INTERFACE (Updated - Sara-Jane's Fixes) ========================


def show_study_interface(app):
    """Show main study interface with sequential caption presentation and randomization"""

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

    # Initialize randomization for this sample if not already done
    sample_key = f"sample_{st.session_state.current_sample_idx}"
    if f"{sample_key}_randomized_order" not in st.session_state:
        # Randomize caption order (A, B, C)
        import random
        caption_indices = [0, 1, 2]
        random.shuffle(caption_indices)
        st.session_state[f"{sample_key}_randomized_order"] = caption_indices
        st.session_state[f"{sample_key}_current_caption"] = 0  # Start with first caption
        st.session_state[f"{sample_key}_ratings_complete"] = False

    # Get randomized order and current position
    randomized_order = st.session_state[f"{sample_key}_randomized_order"]
    current_caption_idx = st.session_state[f"{sample_key}_current_caption"]
    
    # Check if we're in final comparison phase
    if current_caption_idx >= 3:
        show_final_comparison_phase(current, sample_key)
        return
    
    # Show sequential caption rating
    show_sequential_caption_rating(current, sample_key, randomized_order, current_caption_idx)

def show_sequential_caption_rating(current, sample_key, randomized_order, current_caption_idx):
    """Show one caption at a time for rating - RADIO BUTTON VERSION"""
    
    # Get current caption info
    actual_caption_idx = randomized_order[current_caption_idx]
    caption_letter = ["A", "B", "C"][actual_caption_idx]
    caption_text = current["captions"][actual_caption_idx]
    caption_method = current["methods"][actual_caption_idx]
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>📊 Fashion Caption Evaluation</h1>
    </div>
    """, unsafe_allow_html=True)

    # Progress info with caption progress
    st.markdown(f"""
    <div class="progress-box">
        <strong>{current['progress']} • Caption {current_caption_idx + 1} of 3</strong>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])

    with col1:
        if current['image']:
            st.image(current['image'], caption="Fashion Image", width=350)
        st.markdown(f'<div class="category-badge">{current["category"].upper()}</div>', unsafe_allow_html=True)
        
        # Show rating progress
        caption_progress = (current_caption_idx + 1) / 3
        st.progress(caption_progress, text=f"Caption Progress: {current_caption_idx + 1}/3")
        
        # Show which captions are already rated
        st.markdown("### 📊 Rating Progress")
        for i in range(3):
            if i < current_caption_idx:
                st.markdown(f"✅ Caption {i+1}: **Completed**")
            elif i == current_caption_idx:
                st.markdown(f"🔄 Caption {i+1}: **Current**")
            else:
                st.markdown(f"⏳ Caption {i+1}: Pending")

    with col2:
        st.markdown(f"### 📝 Caption {current_caption_idx + 1} Evaluation")
        
        # Show current caption
        st.markdown(f"""
        <div class="caption-box" style="background: rgba(37, 99, 235, 0.1); border: 2px solid #2563EB;">
            <h4 style="color: #2563EB; margin-bottom: 1rem;">Caption {current_caption_idx + 1}:</h4>
            <p style="font-size: 1.1rem; line-height: 1.6; margin: 0;">{caption_text}</p>
        </div>
        """, unsafe_allow_html=True)

        # Rating section with radio buttons
        st.markdown("### 🔢 Rate This Caption")
        
        rating_key_base = f"{sample_key}_caption_{current_caption_idx}"
        

        # RELEVANCE RATING
        relevance = st.radio(
            "**Relevance:** How accurately does this describe what you see?",
            options=[1, 2, 3, 4, 5],
            format_func=lambda x: {
                1: "1 - Very Poor",
                2: "2 - Poor", 
                3: "3 - Okay",
                4: "4 - Good",
                5: "5 - Excellent"
            }[x],
            key=f"{rating_key_base}_relevance",
            index=None,
            help="1 = Completely wrong → 5 = Perfect description",
            horizontal=True
        )

        # FLUENCY RATING
        fluency = st.radio(
            "**Fluency:** How natural and well-written is the English?",
            options=[1, 2, 3, 4, 5],
            format_func=lambda x: {
                1: "1 - Very Poor",
                2: "2 - Poor",
                3: "3 - Okay", 
                4: "4 - Good",
                5: "5 - Excellent"
            }[x],
            key=f"{rating_key_base}_fluency",
            index=None,
            help="1 = Hard to understand → 5 = Perfect grammar",
            horizontal=True
        )

        # DESCRIPTIVENESS RATING
        descriptiveness = st.radio(
            "**Descriptiveness:** How much useful detail does this provide?",
            options=[1, 2, 3, 4, 5],
            format_func=lambda x: {
                1: "1 - Very Poor",
                2: "2 - Poor",
                3: "3 - Okay",
                4: "4 - Good",
                5: "5 - Excellent"
            }[x],
            key=f"{rating_key_base}_descriptiveness",
            index=None,
            help="1 = Very vague → 5 = Rich detail",
            horizontal=True
        )

        # NOVELTY RATING
        novelty = st.radio(
            "**Novelty:** How creative and engaging is this caption?",
            options=[1, 2, 3, 4, 5],
            format_func=lambda x: {
                1: "1 - Very Boring",
                2: "2 - Boring",
                3: "3 - Okay",
                4: "4 - Creative",
                5: "5 - Very Creative"
            }[x],
            key=f"{rating_key_base}_novelty",
            index=None,
            help="1 = Very generic → 5 = Very engaging",
            horizontal=True
        )



        # Check if all ratings provided
        all_ratings_given = all([
            relevance is not None,
            fluency is not None, 
            descriptiveness is not None,
            novelty is not None
        ])
        
        # Show progress feedback
        if not all_ratings_given:
            missing_ratings = []
            if relevance is None:
                missing_ratings.append("**Relevance**")
            if fluency is None:
                missing_ratings.append("**Fluency**")
            if descriptiveness is None:
                missing_ratings.append("**Descriptiveness**")
            if novelty is None:
                missing_ratings.append("**Novelty**")
            
            st.warning(f"📍 Please provide ratings for: {', '.join(missing_ratings)}")
        else:
            st.success("✅ All ratings provided!")

        # Optional comment for this caption
        caption_comment = st.text_area(
            f"💭 Optional thoughts about Caption {current_caption_idx + 1}",
            placeholder="What did you think about this specific caption?",
            height=80,
            key=f"{rating_key_base}_comment"
        )

        # Navigation buttons
        col_nav1, col_nav2, col_nav3 = st.columns([1, 2, 1])
    
        with col_nav1:
            if current_caption_idx > 0:
                if st.button("⬅️ Previous", use_container_width=True):
                    st.session_state[f"{sample_key}_current_caption"] = current_caption_idx - 1
                    st.rerun()  # Previous doesn't need transition (going backward)
        
        with col_nav3:
            if current_caption_idx < 2:  # Not the last caption
                if st.button("Next ➡️", type="primary", use_container_width=True, disabled=not all_ratings_given):
                    if all_ratings_given:
                        # Store ratings for this caption
                        store_caption_rating(sample_key, current_caption_idx, actual_caption_idx, 
                                        caption_method, relevance, fluency, descriptiveness, 
                                        novelty, caption_comment)
                        
                        # Set next caption and trigger transition
                        st.session_state[f"{sample_key}_current_caption"] = current_caption_idx + 1
                        st.session_state.show_transition_banner = True
                        st.session_state.transition_acknowledged = False  # <-- Important!
                        st.session_state.caption_transition_type = "next_caption"
                        st.rerun()
                    else:
                        st.error("❌ Please provide all ratings to continue")
            else:  # Last caption
                if st.button("Complete Ratings ✅", type="primary", use_container_width=True, disabled=not all_ratings_given):
                    if all_ratings_given:
                        # Store final caption rating
                        store_caption_rating(sample_key, current_caption_idx, actual_caption_idx,
                                        caption_method, relevance, fluency, descriptiveness,
                                        novelty, caption_comment)
                        
                        # Move to final comparison with transition
                        st.session_state[f"{sample_key}_current_caption"] = 3
                        st.session_state[f"{sample_key}_ratings_complete"] = True
                        st.session_state.show_transition_banner = True
                        st.session_state.transition_acknowledged = False  # <-- Important!
                        st.session_state.caption_transition_type = "final_comparison"
                        st.rerun()
                    else:
                        st.error("❌ Please provide all ratings to continue")

def show_final_comparison_phase(current, sample_key):
    """Show final comparison phase after all captions are rated"""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🏆 Final Caption Comparison</h1>
    </div>
    """, unsafe_allow_html=True)

    # Progress info
    st.markdown(f"""
    <div class="progress-box">
        <strong>{current['progress']} • Final Comparison</strong>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])

    with col1:
        if current['image']:
            st.image(current['image'], caption="Fashion Image", width=350)
        st.markdown(f'<div class="category-badge">{current["category"].upper()}</div>', unsafe_allow_html=True)
        
        # Show completion status
        st.markdown("### ✅ Rating Status")
        st.markdown("✅ Caption 1: **Completed**")
        st.markdown("✅ Caption 2: **Completed**") 
        st.markdown("✅ Caption 3: **Completed**")
        st.markdown("🔄 **Final Comparison: In Progress**")

    with col2:
        st.markdown("### 📝 Compare All Three Captions")
        
        # Show all captions for comparison
        randomized_order = st.session_state[f"{sample_key}_randomized_order"]
        
        for i in range(3):
            actual_idx = randomized_order[i]
            caption_text = current["captions"][actual_idx]
            
            # Get stored ratings for display
            stored_ratings = st.session_state.get(f"{sample_key}_caption_{i}_stored_ratings", {})
            
            st.markdown(f"""
            <div class="caption-box">
                <strong>Caption {i+1}:</strong> {caption_text}
                <br><small style="color: #9CA3AF;">
                Your ratings: Relevance {stored_ratings.get('relevance', '?')}, 
                Fluency {stored_ratings.get('fluency', '?')}, 
                Descriptiveness {stored_ratings.get('descriptiveness', '?')}, 
                Novelty {stored_ratings.get('novelty', '?')}
                </small>
            </div>
            """, unsafe_allow_html=True)

        # Final comparison questions
        st.markdown("### 🏆 Final Ranking & Assessment")

        col1_final, col2_final = st.columns(2)

        with col1_final:
            caption_order = st.radio(
                "Arrange the captions from best to worst:",
                ["Caption 1 > Caption 2 > Caption 3", 
                 "Caption 1 > Caption 3 > Caption 2", 
                 "Caption 2 > Caption 1 > Caption 3", 
                 "Caption 2 > Caption 3 > Caption 1", 
                 "Caption 3 > Caption 1 > Caption 2", 
                 "Caption 3 > Caption 2 > Caption 1"],
                index=None,
                key=f"{sample_key}_final_ranking",
                help="Select the order from best to worst based on all criteria"
            )

        with col2_final:
            ranking_reason = st.text_area(
                "Why did you arrange the captions this way?",
                placeholder="Explain your reasoning for this ranking. This is optional but helps us understand your thought process",
                height=120,
                key=f"{sample_key}_ranking_reason",
                help="Your reasoning helps us understand what makes captions effective"
            )

        # Overall comment
        overall_comment = st.text_area(
            "💭 Overall thoughts about these three captions",
            placeholder="Any additional observations about the captions or image?",
            height=80,
            key=f"{sample_key}_overall_comment"
        )

        # Submit button
        if st.button("✅ Submit All Ratings & Continue", type="primary", use_container_width=True):
            if not caption_order:
                st.error("❌ Please select the ranking order")
            else:
                # Process and submit all data
                submit_sequential_ratings(current, sample_key, caption_order, ranking_reason, overall_comment)
                st.session_state.show_transition_banner = True
                st.rerun()

def store_caption_rating(sample_key, caption_idx, actual_caption_idx, method, 
                        relevance, fluency, descriptiveness, novelty, comment):
    """Store individual caption rating in session state"""
    rating_data = {
        'actual_caption_idx': actual_caption_idx,
        'method': method,
        'relevance': relevance,
        'fluency': fluency,
        'descriptiveness': descriptiveness,
        'novelty': novelty,
        'comment': comment
    }
    
    st.session_state[f"{sample_key}_caption_{caption_idx}_stored_ratings"] = rating_data

def submit_sequential_ratings(current, sample_key, caption_order, ranking_reason, overall_comment):
    """Submit all sequential ratings as final response"""
    
    # Get randomized order and stored ratings
    randomized_order = st.session_state[f"{sample_key}_randomized_order"]
    
    # Reconstruct ratings in original A, B, C order
    ratings_by_method = {}
    method_mapping = {}
    
    for i in range(3):
        stored_rating = st.session_state[f"{sample_key}_caption_{i}_stored_ratings"]
        actual_idx = stored_rating['actual_caption_idx']
        method = stored_rating['method']
        
        # Map back to original caption letters
        caption_letter = ["Caption A", "Caption B", "Caption C"][actual_idx]
        method_mapping[caption_letter] = method
        
        ratings_by_method[method] = {
            'relevance': stored_rating['relevance'],
            'fluency': stored_rating['fluency'],
            'descriptiveness': stored_rating['descriptiveness'],
            'novelty': stored_rating['novelty']
        }
    
    # Determine best caption method from ranking
    best_caption_position = caption_order.split(" > ")[0]  # e.g., "Caption 1"
    best_caption_idx = int(best_caption_position.split(" ")[1]) - 1  # Convert to 0-based
    best_actual_idx = randomized_order[best_caption_idx]
    best_caption_letter = ["Caption A", "Caption B", "Caption C"][best_actual_idx]
    best_method = method_mapping[best_caption_letter]

    # Create response data (same format as before)
    response_data = {
        'participant_id': st.session_state.participant_id,
        'fashion_interest': st.session_state.fashion_interest,
        'sample_number': st.session_state.current_sample_idx + 1,
        'image_id': current['sample_data']['image_id'],
        'category': current['sample_data']['category'],
        'introduced_phase': current['sample_data']['introduced_phase'],
        'cf_risk': current['sample_data']['cf_risk'],
        'assigned_phase': current['sample_data'].get('assigned_phase', ''),
        'model_checkpoint': current['sample_data'].get('model_checkpoint', ''),
        'diversity_score': current['sample_data'].get('diversity_score', ''),
        'is_diverse': current['sample_data'].get('is_diverse', ''),
        'method_mapping': method_mapping,
        'ratings': ratings_by_method,
        'best_caption_method': best_method,
        'caption_presentation_order': randomized_order,  # NEW: Store randomization
        'ranking_reason': ranking_reason,
        'comment': overall_comment,
        'timestamp': datetime.now().isoformat()
    }

    st.session_state.responses.append(response_data)
    st.session_state.current_sample_idx += 1
    
    # Clean up session state for this sample
    keys_to_remove = [k for k in st.session_state.keys() if k.startswith(sample_key)]
    for key in keys_to_remove:
        del st.session_state[key]
    
    # Save progress to CSV after each response
    save_progress_to_csv()

    # Check if we need to show category assessment
    should_assess, prev_cat, curr_cat = should_show_category_assessment()
    
    if should_assess:
        st.session_state.show_category_assessment = True
        st.session_state.assessment_previous_category = prev_cat
        st.session_state.assessment_current_category = curr_cat
    else:
        st.session_state.show_transition_banner = True
        st.session_state.caption_transition_type = "next_image"  # Different type for image transitions
        st.session_state.transition_acknowledged = False  # <-- Important!



# ======================== HELPER FUNCTIONS ========================

def get_current_sample():
    """Get current sample data - FIXED VERSION"""
    # Check if app data is properly initialized
    if 'app_study_data' not in st.session_state:
        st.error("❌ App data not initialized. Please refresh the page.")
        return None
        
    if 'app_instance' not in st.session_state:
        st.error("❌ App instance not found. Please refresh the page.")
        return None
        
    app_study_data = st.session_state.app_study_data
    app_instance = st.session_state.app_instance
    
    # Check if we've reached the end
    if st.session_state.current_sample_idx >= len(app_study_data):
        return None
    
    sample = app_study_data[st.session_state.current_sample_idx]
    
    # Get image using the app instance
    image_pil = app_instance.get_image_path(sample['image_id'])
    
    # Get captions in consistent order
    methods = sorted(sample['predictions'].keys())
    captions = [sample['predictions'][method] for method in methods]
    
    return {
        'image': image_pil,
        'captions': captions,
        'progress': f"Image {st.session_state.current_sample_idx + 1} of {len(app_study_data)}",
        'category': sample['category'],
        'sample_data': sample,
        'methods': methods
    }

def show_spaced_radio_buttons(question, options, format_func, key, help_text):
    """Create properly spaced radio buttons using columns"""
    
    st.markdown(f"#### {question}")
    
    # Create columns with gaps for spacing
    cols = st.columns([1, 0.2, 1, 0.2, 1, 0.2, 1, 0.2, 1])  # 5 columns with gaps
    
    # Store the selected value
    selected_key = f"{key}_selected"
    if selected_key not in st.session_state:
        st.session_state[selected_key] = None
    
    selected_value = None
    
    # Place each option in its own column
    for i, option in enumerate(options):
        col_idx = i * 2  # Skip gap columns (0, 2, 4, 6, 8)
        with cols[col_idx]:
            label = format_func(option)
            
            # Create a button-style radio option
            is_selected = st.session_state[selected_key] == option
            
            if st.button(
                label,
                key=f"{key}_option_{option}",
                use_container_width=True,
                type="primary" if is_selected else "secondary"
            ):
                st.session_state[selected_key] = option
                selected_value = option
                st.rerun()
    
    # Add help text
    if help_text:
        st.caption(help_text)
    
    return st.session_state[selected_key]

def submit_rating_with_csv_backup(current, ranking_reason, comment):
    """Submit current rating and advance - ENHANCED with reasoning"""

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

    best_caption = st.session_state[f"best_caption_{st.session_state.current_sample_idx}"]

    # Create method mapping
    caption_labels = ["Caption A", "Caption B", "Caption C"]
    method_mapping = {caption_labels[i]: current['methods'][i] for i in range(3)}
    best_method = method_mapping.get(best_caption, '')

    # ENHANCED: Store response with reasoning (Sara-Jane's feedback)
    response_data = {
        'participant_id': st.session_state.participant_id,
        'fashion_interest': st.session_state.fashion_interest,
        'sample_number': st.session_state.current_sample_idx + 1,
        'image_id': current['sample_data']['image_id'],
        'category': current['sample_data']['category'],
        'introduced_phase': current['sample_data']['introduced_phase'],
        'cf_risk': current['sample_data']['cf_risk'],
        'assigned_phase': current['sample_data'].get('assigned_phase', ''),
        'model_checkpoint': current['sample_data'].get('model_checkpoint', ''),
        'diversity_score': current['sample_data'].get('diversity_score', ''),
        'is_diverse': current['sample_data'].get('is_diverse', ''),
        'method_mapping': method_mapping,
        'ratings': {
            current['methods'][0]: {'relevance': rel_a, 'fluency': flu_a, 'descriptiveness': desc_a, 'novelty': nov_a},
            current['methods'][1]: {'relevance': rel_b, 'fluency': flu_b, 'descriptiveness': desc_b, 'novelty': nov_b},
            current['methods'][2]: {'relevance': rel_c, 'fluency': flu_c, 'descriptiveness': desc_c, 'novelty': nov_c}
        },
        'best_caption_method': best_method,
        'ranking_reason': ranking_reason,  # NEW: Required reasoning
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
        st.session_state.show_category_assessment = True
        st.session_state.assessment_previous_category = prev_cat
        st.session_state.assessment_current_category = curr_cat
    else:
        st.session_state.show_transition_banner = True
        st.session_state.transition_acknowledged = False  # <-- Important!


# ======================== CATEGORY ASSESSMENT (Minimal Changes) ========================

def should_show_category_assessment():
    """Determine if we should show category assessment"""
    if st.session_state.current_sample_idx == 0:
        return False, None, None
    
    # Get app data from session state to avoid circular import
    if 'app_study_data' not in st.session_state:
        return False, None, None
    
    app_study_data = st.session_state.app_study_data
    
    # Check if we've just finished the study
    if st.session_state.current_sample_idx >= len(app_study_data):
        last_sample = app_study_data[st.session_state.current_sample_idx - 1]
        last_category = last_sample['category']
        
        final_assessment_key = f"final_{last_category.lower()}_assessment"
        if not hasattr(st.session_state, 'assessed_transitions'):
            st.session_state.assessed_transitions = set()
        
        if final_assessment_key not in st.session_state.assessed_transitions:
            return True, last_category, "completion"
        else:
            return False, None, None
    
    # Check if we're transitioning to a new category
    current_sample = app_study_data[st.session_state.current_sample_idx]
    previous_sample = app_study_data[st.session_state.current_sample_idx - 1]
    
    current_category = current_sample['category']
    previous_category = previous_sample['category']
    
    if current_category != previous_category:
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
        <div class="info-card" style="background: #78350F; border-color: #D97706;">
            <h3>📊 Final Category Assessment</h3>
            <p><strong>You've just completed:</strong> {previous_category} items (Final Category)</p>
            <p><strong>Next:</strong> Final questionnaire</p>
        </div>
        """, unsafe_allow_html=True)
        
        continue_text = "Continue to Final Questionnaire →"
        transition_key = f"final_{previous_category.lower()}_assessment"
    else:
        st.markdown(f"""
        <div class="info-card" style="background: #78350F; border-color: #D97706;">
            <h3>📊 Quick Category Assessment</h3>
            <p><strong>You've just completed:</strong> {previous_category} items</p>
            <p><strong>Now starting:</strong> {current_category} items</p>
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
            key=f"quality_{previous_category.lower()}_assessment"
        )
        
        quality_drop = st.radio(
            f"Did you notice any quality decrease in {previous_category} captions?",
            ["No decrease", "Slight decrease", "Moderate decrease", "Significant decrease"],
            index=None,
            key=f"quality_drop_{previous_category.lower()}"
        )
    
    with col2:
        consistency = st.radio(
            f"How consistent were the {previous_category} captions?",
            ["Very consistent", "Mostly consistent", "Somewhat consistent", "Inconsistent"],
            index=None,
            key=f"consistency_{previous_category.lower()}"
        )
        
        expectations = st.radio(
            f"Did {previous_category} captions meet your expectations?",
            ["Exceeded expectations", "Met expectations", "Below expectations", "Well below expectations"],
            index=None,
            key=f"expectations_{previous_category.lower()}"
        )
    
    comments = st.text_area(
        f"Any specific observations about {previous_category} captions?",
        placeholder=f"Optional: What did you notice about {previous_category} descriptions?",
        height=80,
        key=f"comments_{previous_category.lower()}"
    )
    
    if st.button(continue_text, type="primary", use_container_width=True):
        if not all([quality_assessment, quality_drop, consistency, expectations]):
            st.error("❌ Please answer all assessment questions")
        else:
            # Store assessment data
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
            
            if 'category_assessments' not in st.session_state:
                st.session_state.category_assessments = []
            st.session_state.category_assessments.append(assessment_data)
            
            # Mark transition as assessed
            st.session_state.assessed_transitions.add(transition_key)
            
            if current_category == "completion":
                st.session_state.show_category_assessment = False
                st.session_state.show_transition_banner = "final_category_completed"
            else:
                st.session_state.show_transition_banner = f"category_transition_{current_category}"
                st.session_state.show_category_assessment = False
            
            st.rerun()

# ======================== COMPLETION PAGE (Minimal Changes) ========================

def show_completion_page():
    """Show completion questionnaire - keeping most of old structure"""
    
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
    
    # Demographics (keep simple)
    st.markdown("### 👤 Demographics")
    col1, col2 = st.columns(2)
    
    with col1:
        age = st.selectbox("Age group:", ["", "18-24", "25-34", "35-44", "45-54", "55-64", "65+"])
    
    with col2:
        gender = st.selectbox("Gender:", ["", "Female", "Male", "Non-binary/Third gender", "Prefer not to disclose"])
    
    st.markdown("---")
    
    # Quality Assessment (keep focused)
    st.markdown("### 📊 Caption Quality Assessment")
    
    col1, col2 = st.columns(2)
    
    with col1:
        quality_patterns = st.radio(
            "Did you notice quality differences between fashion categories?",
            ["Yes, clear differences", "Some differences", "No patterns", "Not sure"],
            index=None
        )
        
        if quality_patterns in ["Yes, clear differences", "Some differences"]:
            better_categories = st.multiselect(
                "Which categories had better captions?",
                ["Accessories", "Bottoms", "Dresses", "Outerwear", "Shoes", "Tops"]
            )
            
            worse_categories = st.multiselect(
                "Which categories had worse captions?",
                ["Accessories", "Bottoms", "Dresses", "Outerwear", "Shoes", "Tops"]
            )
        else:
            better_categories = []
            worse_categories = []
    
    with col2:
        learning_hypothesis = st.radio(
            "Do you think the AI learned some fashion categories better than others?",
            ["Yes, definitely", "Yes, somewhat", "No", "Not sure"],
            index=None
        )
        
        summary_assessment = st.radio(
            "How well do you think the AI learned to describe diverse fashion items?",
            ["Excellent", "Good", "Fair", "Poor", "Very poor"],
            index=None
        )
    
    # Final feedback
    final_feedback = st.text_area(
        "💭 Any final thoughts or suggestions?",
        placeholder="Your insights are valuable for our research...",
        height=120
    )
    
    # Submit button with processing
    if st.session_state.get('processing_completion', False):
        st.button("🔄 Processing... Please wait", disabled=True, type="primary", use_container_width=True)
        st.warning("⏳ **Please wait...** Your submission is being processed.")
    else:
        if st.button("💾 Complete Study & Save Results", type="primary", use_container_width=True):
            if not quality_patterns or not learning_hypothesis or not summary_assessment:
                st.error("❌ Please answer all required questions")
            else:
                complete_study_with_processing(age, gender, quality_patterns, better_categories, 
                                             worse_categories, learning_hypothesis, summary_assessment, 
                                             final_feedback)

def complete_study_with_processing(age, gender, quality_patterns, better_categories, worse_categories,
                                 learning_hypothesis, summary_assessment, final_feedback):
    """Complete study with processing indicators"""
    
    st.session_state.processing_completion = True
    
    try:
        status_placeholder = st.empty()
        progress_placeholder = st.empty()
        
        with status_placeholder:
            st.info("🔄 **Processing your submission...** Please don't close this window.")
        
        # Prepare final data
        with progress_placeholder:
            st.progress(1/3, text="Step 1/3: Preparing final data")
        
        final_data = {
            'participant_id': st.session_state.participant_id,
            'response_type': 'final_questionnaire',
            'age_group': age,
            'gender': gender,
            'quality_patterns_noticed': quality_patterns,
            'better_categories': ", ".join(better_categories) if better_categories else "",
            'worse_categories': ", ".join(worse_categories) if worse_categories else "",
            'learning_hypothesis': learning_hypothesis,
            'summary_assessment_rating': summary_assessment,
            'final_feedback': final_feedback,
            'completion_timestamp': datetime.now().isoformat()
        }
        
        # Save to Google Sheets
        with progress_placeholder:
            st.progress(2/3, text="Step 2/3: Saving to Google Sheets")
        
        sheets_success = save_all_to_google_sheets(final_data)
        
        # Save CSV and send emails
        with progress_placeholder:
            st.progress(3/3, text="Step 3/3: Creating backups")
        
        csv_success, files = save_final_complete_csv(final_data)
        email_success = send_completion_emails(final_data)
        
        # Clear processing indicators
        status_placeholder.empty()
        progress_placeholder.empty()

        # Show completion status
        if sheets_success:
            st.balloons()
            st.success("🎉 **Study completed successfully!**")
            
            st.markdown(f"""
            ## ✅ **Thank You!**
            
            **What you accomplished:**
            - Evaluated **{len(st.session_state.responses)} fashion images**
            - Provided **{len(st.session_state.responses) * 3}** caption evaluations  
            - Shared valuable insights about AI-generated descriptions
            
            **Your participant ID:** `{st.session_state.participant_id}`  
            **Thank you for advancing AI research!** 🙏
            """)
        else:
            st.error("❌ Some data saving failed - please contact researcher")
            st.info(f"**Participant ID:** {st.session_state.participant_id}")
            st.info("**Contact:** akash.kumar@dfki.de")
        
        st.session_state.study_complete = True
        st.session_state.processing_completion = False
        
    except Exception as e:
        st.session_state.processing_completion = False
        st.error(f"❌ **Critical Error:** {str(e)}")
        st.error(f"Please contact the researcher: akash.kumar@dfki.de")

# ======================== TRANSITION MESSAGE (Unchanged) ========================

def show_transition_message(message="Loading next..."):
    """Enhanced transition message with working scroll - FROM OLD CODE"""
    from streamlit_js_eval import streamlit_js_eval
    
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

    # WORKING JAVASCRIPT FROM OLD CODE
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

    # WORKING SCROLL DETECTION FROM OLD CODE
    trigger = streamlit_js_eval(js_expressions="window.scrollY", key="scroll_trigger_top")
    if isinstance(trigger, int) and trigger <= 10:
        time.sleep(0.5)
        st.session_state.show_transition_banner = False
        st.rerun()