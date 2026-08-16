import streamlit as st
import pandas as pd
from course_database import CourseDatabase
from parsers import detect_format, parse_response_sheet, parse_answer_key
from analyzer import analyze_answers
from exporter import generate_csv, generate_excel
from result_status import get_status_display

st.set_page_config(page_title="UGC NET Answer Checker", page_icon="🎓", layout="wide")

# Initialize Database
@st.cache_resource
def get_db():
    return CourseDatabase()

db = get_db()

# Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Answer Checker", "Result Status", "About"])

if page == "Home":
    st.title("UGC NET Answer Checker")
    st.markdown("**Analyze your UGC NET response sheet against the official answer key and check the result status of your subject.**")
    
    st.markdown("""
    Welcome to the UGC NET Answer Checker!
    
    Upload your response sheet and official answer key to get a detailed question-wise analysis, including:
    - ✅ Correct Answers
    - ❌ Incorrect Answers
    - 🤷 Unattempted Questions
    - 🎯 Accuracy
    - 📊 Estimated Marks
    
    Get started by navigating to the Answer Checker!
    """)
    if st.button("Analyze My Answers", type="primary"):
        st.switch_page("Answer Checker") # Streamlit natively doesn't have a simple page redirect for radio buttons without using multi-page framework, but we can instruct users or use query params. Wait, let's just use st.session_state to handle navigation.
        
    st.info("Your privacy matters. We do not permanently store your uploaded PDFs. All analysis is done temporarily in your session.")

elif page == "Answer Checker":
    st.title("Answer Checker")
    
    # 1. Select Course
    st.subheader("1. Select Your Subject (Optional)")
    courses = db.get_all_courses()
    course_options = ["None"] + [f"{c['code']} - {c['name']}" for c in courses]
    selected_course_str = st.selectbox("Search subject/course", options=course_options)
    
    selected_course = None
    if selected_course_str != "None":
        code = selected_course_str.split(" - ")[0]
        selected_course = db.get_course_by_code(code)
        
    # 2. Upload Files
    st.subheader("2. Upload Documents")
    
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
        sel_course = st.session_state['selected_course']
        
        st.success(f"Successfully processed! Match Percentage: {stats.get('matched_percentage', 0)}%")
        
        if stats.get('matched_percentage', 0) < 50:
            st.warning("**Warning: The uploaded response sheet and answer key may not belong to the same examination/session. Please verify your files.**")
            
        # Section 1: Result Status
        st.header("Official Result Status")
        if sel_course:
            status_text, r_date, r_url = get_status_display(sel_course)
            if status_text == "Result Declared":
                st.success(f"**Result Declared**")
                if r_url:
                    st.markdown(f"[View Official Result]({r_url})")
                else:
                    st.write("Official result link not available in the current database.")
            else:
                st.info(f"**Result Not Declared**")
        else:
            st.write("No course selected. Official result status cannot be determined.")
            
        st.caption("Official Result Status is shown only when the corresponding course record has been marked as officially declared in the platform's verified result database.")
        
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
        course_name = sel_course["name"] if sel_course else "Unknown Course"
        status_text = get_status_display(sel_course)[0] if sel_course else "Unknown"
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

elif page == "Result Status":
    st.title("UGC NET Result Status")
    st.write("Check the official result declaration status of UGC NET subjects.")
    
    courses = db.get_all_courses()
    
    search_query = st.text_input("Search subject/course by name or code")
    filter_opt = st.radio("Filter", ["All", "Result Declared", "Result Not Declared"], horizontal=True)
    
    filtered_courses = db.search_courses(search_query)
    
    if filter_opt == "Result Declared":
        filtered_courses = [c for c in filtered_courses if c.get("result_declared", False)]
    elif filter_opt == "Result Not Declared":
        filtered_courses = [c for c in filtered_courses if not c.get("result_declared", False)]
        
    st.write(f"Showing {len(filtered_courses)} course(s)")
    
    for c in filtered_courses:
        with st.container(border=True):
            st.subheader(f"{c['code']} - {c['name']}")
            status, date, url = get_status_display(c)
            
            if status == "Result Declared":
                st.success(f"**Result Declared**")
                if date:
                    st.write(f"Result Date: {date}")
                if url:
                    st.markdown(f"[View Official Result]({url})")
            else:
                st.info(f"**Result Not Declared**")
                st.write("We will update this status when official information is available.")

elif page == "About":
    st.title("About UGC NET Answer Checker")
    
    st.subheader("What is this?")
    st.write("A tool for analyzing UGC NET response sheets against official answer keys.")
    
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
