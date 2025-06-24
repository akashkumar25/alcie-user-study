"""
Data Handler for ALCIE Study - Minimal Version
Handles CSV saving, Google Sheets, and email notifications
Keeps all the working functionality from old code
"""

import streamlit as st
import pandas as pd
import os
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import zipfile
import io

# ======================== CSV SAVING FUNCTIONS ========================

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
                'ranking_reason': response.get('ranking_reason', ''),  # NEW: Store reasoning
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
                'ranking_reason': response.get('ranking_reason', ''),  # NEW: Include reasoning
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
        
        return True, (final_file, category_final_file, summary_file)
        
    except Exception as e:
        st.error(f"Error saving final CSV: {e}")
        return False, None

# ======================== GOOGLE SHEETS FUNCTIONS ========================

def get_gsheet_connection():
    """Get Google Sheets connection with modern authentication"""
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        
        creds = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"], scopes=scope
        )
        client = gspread.authorize(creds)
        return client
    except KeyError as e:
        st.error(f"❌ Missing credentials in secrets: {e}")
        return None
    except Exception as e:
        st.error(f"❌ Failed to connect to Google Sheets: {e}")
        return None

def safe_ensure_headers(worksheet, expected_headers):
    """Safely ensure headers exist without clearing existing participant data"""
    try:
        # Check if worksheet has any content
        if worksheet.row_count == 0:
            worksheet.insert_row(expected_headers, 1)
            return True
        
        # Get first row to check for headers
        existing_first_row = worksheet.row_values(1)
        
        # If first row is empty, insert headers
        if not existing_first_row:
            worksheet.insert_row(expected_headers, 1)
            return True
        
        # Check if first row matches expected headers
        if existing_first_row == expected_headers:
            return True
        
        # If first row looks like data, insert headers above
        first_cell = existing_first_row[0] if existing_first_row else ""
        is_participant_data = (
            (first_cell.startswith('P') and any(c.isdigit() for c in first_cell)) or
            ('-' in first_cell and any(c.isdigit() for c in first_cell) and len(first_cell) > 10)
        )
        
        if is_participant_data:
            st.warning("⚠️ Detected data in first row - inserting headers above existing data")
            worksheet.insert_row(expected_headers, 1)
            return True
        
        return True
        
    except Exception as e:
        st.error(f"❌ Header management failed: {e}")
        return False

def get_detailed_responses_headers():
    """Generate headers for detailed per-response data"""
    base_headers = [
        'participant_id', 'sample_number', 'image_id', 'category', 'introduced_phase',
        'cf_risk', 'assigned_phase', 'model_checkpoint', 'diversity_score', 'is_diverse',
        'method_caption_a', 'method_caption_b', 'method_caption_c',
        'best_caption_method', 'ranking_reason', 'comment', 'timestamp'  # NEW: ranking_reason added
    ]
    
    # Add rating headers for each method
    actual_methods = ['random', 'diversity', 'uncertainty']
    rating_headers = []
    for method in actual_methods:
        rating_headers.extend([
            f'{method}_relevance',
            f'{method}_fluency', 
            f'{method}_descriptiveness',
            f'{method}_novelty'
        ])
    
    return base_headers + rating_headers

def get_participant_summary_headers():
    """Headers for participant summary"""
    return [
        'participant_id', 'fashion_interest', 'age_group', 'gender', 'total_samples',
        'completion_timestamp', 'quality_patterns_noticed', 'better_categories',
        'worse_categories', 'learning_hypothesis', 'summary_assessment_rating',
        'final_feedback'
    ]

def get_category_assessments_headers():
    """Headers for category assessments"""
    return [
        'participant_id', 'response_type', 'previous_category', 'current_category',
        'sample_idx_at_transition', 'quality_rating', 'quality_drop',
        'consistency_rating', 'expectations_rating', 'comments', 'timestamp'
    ]

def save_detailed_responses_to_sheets():
    """Save all detailed responses to Google Sheets"""
    try:
        client = get_gsheet_connection()
        if not client:
            return False
            
        # Get or create spreadsheet
        try:
            sheet = client.open("ALCIE User Study Responses")
        except gspread.SpreadsheetNotFound:
            sheet = client.create("ALCIE User Study Responses")
            sheet.share('akash.kumar@dfki.de', perm_type='user', role='writer')
        
        # Get or create worksheet
        try:
            worksheet = sheet.worksheet("DetailedResponses")
        except gspread.WorksheetNotFound:
            worksheet = sheet.add_worksheet(title="DetailedResponses", rows=2000, cols=30)
        
        # Safe header management
        headers = get_detailed_responses_headers()
        if not safe_ensure_headers(worksheet, headers):
            return False
        
        # Prepare data
        all_rows = []
        actual_methods = ['random', 'diversity', 'uncertainty']
        
        for response in st.session_state.responses:
            row = [
                # Base fields
                response['participant_id'],
                response['sample_number'],
                response['image_id'],
                response['category'],
                response['introduced_phase'],
                response['cf_risk'],
                response.get('assigned_phase', ''),
                response.get('model_checkpoint', ''),
                response.get('diversity_score', ''),
                response.get('is_diverse', ''),
                response['method_mapping'].get('Caption A', ''),
                response['method_mapping'].get('Caption B', ''),
                response['method_mapping'].get('Caption C', ''),
                response['best_caption_method'],
                response.get('ranking_reason', ''),  # NEW: Include reasoning
                response['comment'],
                response['timestamp'],
                
                # Rating fields
                response['ratings']['random']['relevance'],
                response['ratings']['random']['fluency'], 
                response['ratings']['random']['descriptiveness'],
                response['ratings']['random']['novelty'],
                response['ratings']['diversity']['relevance'],
                response['ratings']['diversity']['fluency'],
                response['ratings']['diversity']['descriptiveness'], 
                response['ratings']['diversity']['novelty'],
                response['ratings']['uncertainty']['relevance'],
                response['ratings']['uncertainty']['fluency'],
                response['ratings']['uncertainty']['descriptiveness'],
                response['ratings']['uncertainty']['novelty']
            ]
            
            all_rows.append(row)
        
        # Batch write
        if all_rows:
            worksheet.append_rows(all_rows)
        
        return True
        
    except Exception as e:
        st.error(f"❌ Error saving detailed responses: {e}")
        return False

def save_participant_summary_to_sheets(final_data):
    """Save participant summary to Google Sheets - FIXED VERSION"""
    try:
        client = get_gsheet_connection()
        if not client:
            return False
            
        # Get or create spreadsheet
        try:
            sheet = client.open("ALCIE User Study Responses")
        except gspread.SpreadsheetNotFound:
            sheet = client.create("ALCIE User Study Responses")
            sheet.share('akash.kumar@dfki.de', perm_type='user', role='writer')
        
        # Get or create worksheet
        try:
            worksheet = sheet.worksheet("ParticipantSummary")
        except gspread.WorksheetNotFound:
            worksheet = sheet.add_worksheet(title="ParticipantSummary", rows=1000, cols=25)
        
        # Safe header management
        headers = get_participant_summary_headers()
        if not safe_ensure_headers(worksheet, headers):
            return False
        
        # FIXED: Properly handle multiselect values
        better_cats = final_data.get('better_categories', '')
        worse_cats = final_data.get('worse_categories', '')
        
        # Ensure these are strings, not lists
        if isinstance(better_cats, list):
            better_cats = ", ".join(better_cats)
        if isinstance(worse_cats, list):
            worse_cats = ", ".join(worse_cats)
        
        # Single summary row with proper string conversion
        row = [
            str(st.session_state.participant_id),
            str(st.session_state.fashion_interest),
            str(final_data.get('age_group', '')),
            str(final_data.get('gender', '')),
            str(len(st.session_state.responses)),
            str(final_data.get('completion_timestamp', '')),
            str(final_data.get('quality_patterns_noticed', '')),
            str(better_cats),  # FIXED: Ensure string
            str(worse_cats),   # FIXED: Ensure string  
            str(final_data.get('learning_hypothesis', '')),
            str(final_data.get('summary_assessment_rating', '')),
            str(final_data.get('final_feedback', ''))
        ]
        
        worksheet.append_row(row)
        return True
        
    except Exception as e:
        st.error(f"❌ Error saving participant summary: {e}")
        return False

def save_category_assessments_to_sheets():
    """Save all category assessments to Google Sheets"""
    if not hasattr(st.session_state, 'category_assessments') or not st.session_state.category_assessments:
        return True
    
    try:
        client = get_gsheet_connection()
        if not client:
            return False
            
        # Get or create spreadsheet
        try:
            sheet = client.open("ALCIE User Study Responses")
        except gspread.SpreadsheetNotFound:
            sheet = client.create("ALCIE User Study Responses")
            sheet.share('akash.kumar@dfki.de', perm_type='user', role='writer')
        
        # Get or create worksheet
        try:
            worksheet = sheet.worksheet("CategoryAssessments")
        except gspread.WorksheetNotFound:
            worksheet = sheet.add_worksheet(title="CategoryAssessments", rows=1000, cols=15)
        
        # Safe header management
        headers = get_category_assessments_headers()
        if not safe_ensure_headers(worksheet, headers):
            return False
        
        # Prepare all assessment rows
        all_rows = []
        for assessment in st.session_state.category_assessments:
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
            all_rows.append(row_data)
        
        # Batch write
        if all_rows:
            worksheet.append_rows(all_rows)
        
        return True
        
    except Exception as e:
        st.error(f"❌ Error saving category assessments: {e}")
        return False

def save_all_to_google_sheets(final_data):
    """Save all data to Google Sheets - main function"""
    try:
        # Save all components
        detailed_success = save_detailed_responses_to_sheets()
        summary_success = save_participant_summary_to_sheets(final_data)
        category_success = save_category_assessments_to_sheets()
        
        return detailed_success and summary_success and category_success
        
    except Exception as e:
        st.error(f"❌ Error saving to Google Sheets: {e}")
        return False

# ======================== EMAIL FUNCTIONS ========================

def get_email_config():
    """Get email configuration from Streamlit secrets"""
    try:
        return {
            'smtp_server': st.secrets["email"]["smtp_server"],
            'smtp_port': st.secrets["email"]["smtp_port"],
            'sender_email': st.secrets["email"]["sender_email"],
            'sender_password': st.secrets["email"]["sender_password"],
            'researcher_email': st.secrets["email"]["researcher_email"]
        }
    except KeyError as e:
        st.warning(f"❗ Email configuration missing: {e}")
        return None

def create_zip_with_csv_files(participant_id):
    """Create a ZIP file containing all CSV files for the participant"""
    try:
        output_dir = "responses"
        zip_buffer = io.BytesIO()
        
        # Collect all CSV files for this participant
        csv_files = []
        for filename in os.listdir(output_dir):
            if filename.startswith(participant_id) and filename.endswith('.csv'):
                file_path = os.path.join(output_dir, filename)
                csv_files.append((filename, file_path))
        
        if not csv_files:
            return None, "No CSV files found"
        
        # Create ZIP file in memory
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for filename, file_path in csv_files:
                zip_file.write(file_path, filename)
        
        zip_buffer.seek(0)
        return zip_buffer.getvalue(), None
        
    except Exception as e:
        return None, str(e)

def send_csv_backup_email(participant_id):
    """Send CSV files as email attachment"""
    try:
        email_config = get_email_config()
        if not email_config:
            return False, "Email configuration not found"
        
        # Create ZIP file with all CSV files
        zip_data, zip_error = create_zip_with_csv_files(participant_id)
        if zip_error:
            return False, f"Failed to create ZIP: {zip_error}"
        
        # Create email message
        msg = MIMEMultipart()
        msg['From'] = email_config['sender_email']
        msg['To'] = email_config['researcher_email']
        msg['Subject'] = f"ALCIE Study Data Backup - Participant {participant_id}"
        
        # Email body
        body = f"""
ALCIE User Study - Data Backup

Participant ID: {participant_id}
Timestamp: {datetime.now().isoformat()}
Total Responses: {len(st.session_state.responses) if hasattr(st.session_state, 'responses') else 'Unknown'}
Category Assessments: {len(st.session_state.get('category_assessments', []))}

Data Files Included:
- Participant Summary (enhanced format)
- Detailed Responses (all ratings & methods)
- Category Assessments (transition evaluations)

This is an automated backup from the ALCIE continual learning study.

---
DFKI - German Research Center for Artificial Intelligence
Researcher: Akash Kumar
"""
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Attach ZIP file
        attachment = MIMEBase('application', 'zip')
        attachment.set_payload(zip_data)
        encoders.encode_base64(attachment)
        attachment.add_header(
            'Content-Disposition',
            f'attachment; filename=ALCIE_Study_{participant_id}_backup.zip'
        )
        msg.attach(attachment)
        
        # Send email
        server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
        server.starttls()
        server.login(email_config['sender_email'], email_config['sender_password'])
        text = msg.as_string()
        server.sendmail(email_config['sender_email'], email_config['researcher_email'], text)
        server.quit()
        
        return True, f"Backup sent to {email_config['researcher_email']}"
        
    except Exception as e:
        return False, f"Email sending failed: {str(e)}"

def send_completion_notification_email(participant_id, final_data):
    """Send completion notification to researcher"""
    try:
        email_config = get_email_config()
        if not email_config:
            return False, "Email configuration not found"
        
        # Create email message
        msg = MIMEMultipart()
        msg['From'] = email_config['sender_email']
        msg['To'] = email_config['researcher_email']
        msg['Subject'] = f"ALCIE Study Completed - Participant {participant_id}"
        
        # Calculate statistics
        category_assessments_count = len(st.session_state.get('category_assessments', []))
        total_ratings = len(st.session_state.responses) * 3 * 4  # 3 captions × 4 criteria
        
        # Email body with summary
        body = f"""
ALCIE User Study - Completion Notification

🎉 NEW PARTICIPANT COMPLETED THE STUDY!

PARTICIPANT DETAILS:
- Participant ID: {participant_id}
- Fashion Interest: {st.session_state.fashion_interest}
- Age Group: {final_data.get('age_group', 'Not provided')}
- Gender: {final_data.get('gender', 'Not provided')}
- Completion Time: {final_data['completion_timestamp']}

DATA COLLECTED:
- Images Evaluated: {len(st.session_state.responses)}
- Total Ratings: {total_ratings} (4 criteria × 3 methods × {len(st.session_state.responses)} images)
- Category Assessments: {category_assessments_count}
- Method Comparisons: Random vs Diversity vs Uncertainty sampling

RESEARCH INSIGHTS:
- Quality Patterns Noticed: {final_data.get('quality_patterns_noticed', 'Not provided')}
- Better Categories: {final_data.get('better_categories', 'None specified')}
- Worse Categories: {final_data.get('worse_categories', 'None specified')}
- Learning Hypothesis: {final_data.get('learning_hypothesis', 'Not provided')}

FEEDBACK:
{final_data.get('final_feedback', 'No additional feedback provided')}

Data has been saved to Google Sheets and CSV files.
A backup ZIP file has been sent to your email.

---
ALCIE Study System - DFKI
"""
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
        server.starttls()
        server.login(email_config['sender_email'], email_config['sender_password'])
        text = msg.as_string()
        server.sendmail(email_config['sender_email'], email_config['researcher_email'], text)
        server.quit()
        
        return True, "Completion notification sent"
        
    except Exception as e:
        return False, f"Notification email failed: {str(e)}"

def send_completion_emails(final_data):
    """Send completion emails - main function"""
    try:
        # Send backup email
        backup_success, backup_msg = send_csv_backup_email(st.session_state.participant_id)
        
        # Send notification email
        notification_success, notification_msg = send_completion_notification_email(
            st.session_state.participant_id, final_data
        )
        
        return backup_success and notification_success
        
    except Exception as e:
        st.warning(f"Email sending failed: {e}")
        return False