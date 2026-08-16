import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import plotly.graph_objects as go
from parsers import detect_format, parse_response_sheet, parse_answer_key
from analyzer import analyze_answers
from exporter import generate_csv, generate_excel
st.set_page_config(page_title="ResultChecker by Pennion.com", page_icon="🎯", layout="wide")

# Premium Custom CSS for Website UI
st.markdown("""
<style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    /* Main Background & Fonts */
    .stApp {
        background-color: #fcfcfd;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Hide Default Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Global Typography */
    h1, h2, h3, p, span {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }
    
    h1 {
        font-weight: 800 !important;
        font-size: 2.5rem !important;
        color: #0f172a !important;
        letter-spacing: -0.05em !important;
    }
    
    h2 {
        font-weight: 700 !important;
        color: #1e293b !important;
        letter-spacing: -0.03em !important;
    }
    
    /* Primary Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
        color: white !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 14px 0 rgba(37, 99, 235, 0.39) !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(37, 99, 235, 0.4) !important;
    }
    
    /* Upload Cards Styling */
    [data-testid="stFileUploader"] {
        background-color: #ffffff;
        border: 2px dashed #cbd5e1;
        border-radius: 16px;
        padding: 2rem;
        transition: all 0.2s ease;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
    }
    [data-testid="stFileUploader"]:hover {
        border-color: #3b82f6;
        background-color: #f8fafc;
    }
    
    /* Metric Cards */
    [data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #f1f5f9;
        border-radius: 16px;
        padding: 1.25rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-2px);
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.9rem !important;
        color: #64748b !important;
        font-weight: 500 !important;
    }
    [data-testid="stMetricValue"] {
        color: #0f172a !important;
        font-weight: 800 !important;
        font-size: 2rem !important;
        letter-spacing: -0.05em !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #f1f5f9;
    }
    [data-testid="stSidebar"] .stRadio label {
        font-weight: 600 !important;
        padding: 10px 0;
    }
    
    /* Info/Warning Boxes */
    .stAlert {
        border-radius: 12px !important;
        border: none !important;
    }
    
    /* Mobile Responsiveness */
    @media (max-width: 768px) {
        h1 { font-size: 2rem !important; }
        h2 { font-size: 1.5rem !important; }
        [data-testid="stMetricValue"], h2[style*="font-size:2.5rem"] { font-size: 1.5rem !important; }
        [data-testid="stFileUploader"] { padding: 1rem; }
        /* Force columns to stack gracefully on smaller screens */
        [data-testid="column"] { min-width: 100% !important; }
    }
</style>
""", unsafe_allow_html=True)


# Navigation
st.sidebar.title("ResultChecker")
st.sidebar.markdown("by [Pennion.com](https://pennion.com/)")
page = st.sidebar.radio("Go to", ["Home", "Answer Checker", "About"])

if page == "Home":
    st.title("ResultChecker")
    st.markdown("##### by [Pennion.com](https://pennion.com/)")
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
            
        # Section 2: Answer Analysis Dashboard
        st.header("Answer Analysis Dashboard")
        st.caption("Important: The score shown here is calculated directly from the uploaded response sheet and answer key. It is not an official NTA result.")
        
        dash_col1, dash_col2 = st.columns([1, 1.8])
        
        with dash_col1:
            with st.container(border=True):
                st.markdown("<h4 style='color:#475569;'>Accuracy / Health</h4>", unsafe_allow_html=True)
                fig = go.Figure(go.Pie(
                    values=[stats["correct"], stats["total_key_questions"] - stats["correct"]],
                    labels=["Correct", "Other"],
                    hole=0.75,
                    marker_colors=["#3b82f6", "#e2e8f0"],
                    textinfo='none',
                    hoverinfo='none'
                ))
                fig.update_layout(
                    showlegend=False,
                    margin=dict(t=10, b=10, l=10, r=10),
                    height=220,
                    annotations=[dict(text=f"<b>{stats['accuracy']}%</b><br><span style='font-size:12px;color:#94a3b8'>Accuracy</span>", x=0.5, y=0.5, font_size=32, showarrow=False)]
                )
                st.plotly_chart(fig, use_container_width=True)
                
            with st.container(border=True):
                st.markdown("<h4 style='color:#475569;'>Questions Breakdown</h4>", unsafe_allow_html=True)
                st.markdown(f"**{stats['total_key_questions']}** Total Questions")
                fig_bar = go.Figure(go.Bar(
                    x=[stats["correct"], stats["incorrect"], stats["unattempted"], stats["missing"]],
                    y=[""],
                    orientation='h',
                    marker=dict(color=["#10b981", "#ef4444", "#cbd5e1", "#f59e0b"])
                ))
                fig_bar.update_layout(barmode='stack', showlegend=False, height=50, margin=dict(t=0, b=0, l=0, r=0), xaxis=dict(showgrid=False, showticklabels=False), yaxis=dict(showgrid=False, showticklabels=False))
                st.plotly_chart(fig_bar, use_container_width=True)
                st.caption("🟢 Correct &nbsp; 🔴 Incorrect &nbsp; ⚪ Unattempted &nbsp; 🟠 Missing")
                
        with dash_col2:
            m1, m2, m3 = st.columns(3)
            with m1:
                with st.container(border=True):
                    st.markdown("<p style='color:#10b981; font-weight:600; margin-bottom:0;'>Correct Answers {</p>", unsafe_allow_html=True)
                    st.markdown(f"<h2 style='color:#10b981; margin-top:0;'>{stats['correct']}</h2>", unsafe_allow_html=True)
            with m2:
                with st.container(border=True):
                    st.markdown("<p style='color:#ef4444; font-weight:600; margin-bottom:0;'>Incorrect Answers {</p>", unsafe_allow_html=True)
                    st.markdown(f"<h2 style='color:#ef4444; margin-top:0;'>{stats['incorrect']}</h2>", unsafe_allow_html=True)
            with m3:
                with st.container(border=True):
                    st.markdown("<p style='color:#f59e0b; font-weight:600; margin-bottom:0;'>Unattempted {</p>", unsafe_allow_html=True)
                    st.markdown(f"<h2 style='color:#f59e0b; margin-top:0;'>{stats['unattempted']}</h2>", unsafe_allow_html=True)
                    
            st.markdown("<h4 style='margin-top:20px; color:#1e293b;'>Thematic Reports</h4>", unsafe_allow_html=True)
            r1, r2 = st.columns(2)
            with r1:
                with st.container(border=True):
                    st.markdown("<p style='color:#475569; font-size:0.9rem; font-weight:600; margin-bottom:0;'>Estimated Score</p>", unsafe_allow_html=True)
                    st.markdown(f"<h2 style='color:#2563eb; margin-top:0; font-size:2.5rem;'>◯ {stats['estimated_score']}</h2>", unsafe_allow_html=True)
                    if st.button("View details", key="vd1"): pass
            with r2:
                with st.container(border=True):
                    st.markdown("<p style='color:#475569; font-size:0.9rem; font-weight:600; margin-bottom:0;'>Attempt Ratio</p>", unsafe_allow_html=True)
                    attempt_pct = int((stats['attempted']/stats['total_key_questions'])*100) if stats['total_key_questions'] > 0 else 0
                    st.markdown(f"<h2 style='color:#2563eb; margin-top:0; font-size:2.5rem;'>◯ {attempt_pct}%</h2>", unsafe_allow_html=True)
                    if st.button("View details", key="vd2"): pass
            r3, r4 = st.columns(2)
            with r3:
                with st.container(border=True):
                    st.markdown("<p style='color:#475569; font-size:0.9rem; font-weight:600; margin-bottom:0;'>Match Confidence</p>", unsafe_allow_html=True)
                    st.markdown(f"<h2 style='color:#2563eb; margin-top:0; font-size:2.5rem;'>◯ {stats.get('matched_percentage', 0)}%</h2>", unsafe_allow_html=True)
                    if st.button("View details", key="vd3"): pass
            with r4:
                with st.container(border=True):
                    st.markdown("<p style='color:#475569; font-size:0.9rem; font-weight:600; margin-bottom:0;'>Missing Questions</p>", unsafe_allow_html=True)
                    st.markdown(f"<h2 style='color:#2563eb; margin-top:0; font-size:2.5rem;'>◯ {stats['missing']}</h2>", unsafe_allow_html=True)
                    if st.button("View details", key="vd4"): pass
        
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
        
        filter_options = st.multiselect(
            "Filter questions by result:",
            options=["Correct", "Incorrect", "Unattempted", "Missing"],
            default=["Correct", "Incorrect", "Unattempted", "Missing"]
        )
        
        filtered_df = df[df['Result'].isin(filter_options)]
        st.caption(f"Showing {len(filtered_df)} questions")
        
        for idx, row in filtered_df.iterrows():
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
    st.markdown("##### by [Pennion.com](https://pennion.com/)")
    
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

# Global Footer
st.markdown("---")
st.markdown("<div style='text-align: center; color: #64748b; padding-bottom: 20px;'>Built with ❤️ in India by <a href='https://pennion.com/' target='_blank' style='color: #2563eb; text-decoration: none; font-weight: 600;'>Pennion</a></div>", unsafe_allow_html=True)
