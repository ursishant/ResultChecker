import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
from parsers import detect_format, parse_response_sheet, parse_answer_key
from analyzer import analyze_answers
from exporter import generate_csv, generate_excel

st.set_page_config(page_title="ResultChecker by Pennion.com", page_icon="🎯", layout="wide")

# Analytics Injection (Replace with your actual tracking code)
components.html(
    """
    <!-- Paste your Google Analytics or other tracking code here -->
    <script>
        // Analytics code goes here
        console.log("Analytics active");
    </script>
    """,
    width=0, height=0
)

# Custom CSS for Sleek Interface
st.markdown("""
<style>
    /* Main Background & Fonts */
    .stApp {
        background-color: #f8f9fa;
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide Default Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Headers */
    h1, h2, h3 {
        color: #1f2937;
        font-weight: 700 !important;
    }
    
    /* Primary Button Styling */
    .stButton > button {
        background-color: #2563eb !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 0.6rem 1.2rem !important;
        font-weight: 600 !important;
        transition: all 0.2s ease-in-out !important;
    }
    .stButton > button:hover {
        background-color: #1d4ed8 !important;
        box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2), 0 2px 4px -1px rgba(37, 99, 235, 0.1) !important;
        transform: translateY(-1px) !important;
    }
    
    /* Upload Cards Styling */
    [data-testid="stFileUploader"] {
        background-color: white;
        border: 2px dashed #cbd5e1;
        border-radius: 12px;
        padding: 1.5rem;
        transition: border-color 0.2s ease;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: #2563eb;
    }
    
    /* Metric Cards */
    [data-testid="stMetric"] {
        background-color: white;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
    }
    [data-testid="stMetricValue"] {
        color: #2563eb !important;
        font-weight: 800 !important;
    }
    
    /* Expander / Accordion */
    .streamlit-expanderHeader {
        background-color: white;
        border-radius: 8px;
        border: 1px solid #e5e7eb;
        font-weight: 600;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e5e7eb;
    }
</style>
""", unsafe_allow_html=True)


# Navigation
st.sidebar.title("ResultChecker")
st.sidebar.caption("by Pennion.com")
page = st.sidebar.radio("Go to", ["Home", "Answer Checker", "About"])

if page == "Home":
    st.title("ResultChecker")
    st.subheader("by Pennion.com")
    st.markdown("**Analyze your UGC NET response sheet against the official answer key instantly.**")
    
    st.markdown("""
    Welcome to ResultChecker!
    
    Upload your response sheet and official answer key to get a detailed question-wise analysis, including:
    - ✅ Correct Answers
    - ❌ Incorrect Answers
    - 🤷 Unattempted Questions
    - 🎯 Accuracy
    - 📊 Estimated Marks
    
    Get started by navigating to the Answer Checker!
    """)
    st.info("👈 Please select **Answer Checker** from the sidebar menu to begin.")
        
    st.info("Your privacy matters. We do not permanently store your uploaded PDFs. All analysis is done temporarily in your session.")

elif page == "Answer Checker":
    st.title("Answer Checker")
    
    selected_course = None
        
    # 1. Upload Files
    st.subheader("1. Upload Documents")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Candidate Response Sheet")
        st.caption("Upload your UGC NET response sheet PDF.")
        response_file = st.file_uploader("Upload Response Sheet", type=['pdf'], key="response")
        
    with col2:
        st.markdown("### Official Answer Key")
        st.caption("Upload the official answer key PDF.")
        answer_key_file = st.file_uploader("Upload Answer Key", type=['pdf'], key="answer")
        
    st.caption("Your PDFs are processed temporarily to generate your analysis. They are not intended to be permanently stored.")
    
    # 3. Analyze Button
    if st.button("Analyze Answers", disabled=not (response_file and answer_key_file), type="primary"):
        with st.spinner("Analyzing your answers..."):
            try:
                # Read bytes
                response_bytes = response_file.read()
                answer_key_bytes = answer_key_file.read()
                
                # Check file size (20MB max)
                if len(response_bytes) > 20 * 1024 * 1024 or len(answer_key_bytes) > 20 * 1024 * 1024:
                    st.error("File size limit exceeded. Maximum allowed size is 20 MB per PDF.")
                    st.stop()
                
                # Detect formats
                resp_fmt = detect_format(response_bytes)
                key_fmt = detect_format(answer_key_bytes)
                
                if resp_fmt != 'response_sheet':
                    st.warning("The first file does not appear to be a supported response sheet format. Please verify your file.")
                if key_fmt != 'answer_key' and key_fmt != 'response_sheet':
                    # Sometimes detector is not perfect for answer key, but we warn
                    pass
                
                # Parse
                resp_data = parse_response_sheet(response_bytes)
                key_data = parse_answer_key(answer_key_bytes)
                
                # Marking scheme fallback
                marking_scheme = {"correct": 2, "incorrect": 0, "unattempted": 0}
                if selected_course and "marking_scheme" in selected_course:
                    marking_scheme = selected_course["marking_scheme"]
                    
                # Analyze
                df, stats = analyze_answers(resp_data, key_data, marking_scheme=marking_scheme)
                
                # Show results in session state so it persists if user interacts with the page
                st.session_state['analysis_done'] = True
                st.session_state['df'] = df
                st.session_state['stats'] = stats
                st.session_state['selected_course'] = selected_course
                
            except Exception as e:
                st.error(f"An error occurred during processing: {str(e)}")
                st.info("Please make sure you have uploaded valid, unmodified PDFs downloaded directly from the examination portal.")
                
    # 4. Display Results
    if st.session_state.get('analysis_done'):
        st.divider()
        df = st.session_state['df']
        stats = st.session_state['stats']
        
        st.success(f"Successfully processed! Match Percentage: {stats.get('matched_percentage', 0)}%")
        
        if stats.get('matched_percentage', 0) < 50:
            st.warning("**Warning: The uploaded response sheet and answer key may not belong to the same examination/session. Please verify your files.**")
            
        # Section 2: Answer Analysis
        st.header("Your Answer Analysis")
        st.caption("Important: The score shown here is calculated from the uploaded response sheet and answer key. It is not an official NTA score or result.")
        
        m1, m2, m3, m4, m5, m6 = st.columns(6)
        m1.metric("Total Questions", stats["total_key_questions"])
        m2.metric("Attempted", stats["attempted"])
        m3.metric("Correct", stats["correct"])
        m4.metric("Incorrect", stats["incorrect"])
        m5.metric("Unattempted", stats["unattempted"])
        m6.metric("Missing", stats["missing"])
        
        c1, c2 = st.columns(2)
        c1.metric("Accuracy", f"{stats['accuracy']}%")
        c2.metric("Estimated Score", stats['estimated_score'])
        
        # Actions
        st.subheader("Downloads")
        csv_data = generate_csv(df)
        course_name = "Unknown Course"
        status_text = "N/A"
        excel_data = generate_excel(df, stats, course_name, status_text)
        
        dl_col1, dl_col2 = st.columns(2)
        with dl_col1:
            st.download_button("Download CSV", data=csv_data, file_name="exam_answer_analysis.csv", mime="text/csv")
        with dl_col2:
            st.download_button("Download Excel Report", data=excel_data, file_name="exam_answer_analysis.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        
        # Question-wise Detail
        st.subheader("Question-wise Detail")
        
        for idx, row in df.iterrows():
            with st.expander(f"Q: {row['Question ID']} | Result: {row['Result']}"):
                st.write(f"**Question ID:** {row['Question ID']}")
                st.write(f"**Your selected option number:** {row['Chosen Option'] if row['Chosen Option'] else 'None'}")
                st.write(f"**Your selected Option ID:** {row['Chosen Option ID'] if row['Chosen Option ID'] else 'None'}")
                st.write(f"**Correct Option ID:** {row['Correct Option ID']}")
                
                if row['Result'] == "Correct":
                    st.success("Correct")
                elif row['Result'] == "Incorrect":
                    st.error("Incorrect")
                elif row['Result'] == "Unattempted":
                    st.warning("Unattempted")
                else:
                    st.info(row['Result'])

elif page == "About":
    st.title("About ResultChecker")
    st.caption("by Pennion.com")
    
    st.subheader("What is this?")
    st.write("A tool for instantly analyzing UGC NET response sheets against official answer keys.")
    
    st.subheader("How does it work?")
    st.code('''Upload Response Sheet
+
Upload Answer Key
↓
Extract Question IDs
↓
Match Question IDs
↓
Map Chosen Option to Option ID
↓
Compare with Correct Option ID
↓
Generate Analysis''')

    st.warning("**Important disclaimer**: The calculated score is an estimate and does not replace the official NTA result.")
