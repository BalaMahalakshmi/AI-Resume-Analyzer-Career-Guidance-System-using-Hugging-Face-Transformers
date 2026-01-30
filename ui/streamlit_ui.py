import streamlit as st
import sys
import os

# Add parent directory to path
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# current_dir = os.path.dirname(os.path.abspath(__file__))
# parent_dir = os.path.dirname(current_dir)
# if parent_dir not in sys.path:
#     sys.path.insert(0, parent_dir)


from backend.parser import ResumeParser
from backend.skills import SkillExtractor
from backend.matcher import JobMatcher
from backend.advisor import CareerAdvisor
from backend.chatbot import ResumeChat

# Page configuration
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

# Initialize session state
if 'resume_data' not in st.session_state:
    st.session_state.resume_data = None
if 'skills_data' not in st.session_state:
    st.session_state.skills_data = None
if 'job_matches' not in st.session_state:
    st.session_state.job_matches = None
if 'chatbot' not in st.session_state:
    st.session_state.chatbot = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #ff7f0e;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .skill-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        margin: 0.2rem;
        background-color: #e8f4f8;
        border-radius: 15px;
        font-size: 0.9rem;
    }
    .job-card {
        padding: 1rem;
        border-left: 4px solid #1f77b4;
        background-color: #f8f9fa;
        margin-bottom: 1rem;
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">📄 AI Resume Analyzer</div>', unsafe_allow_html=True)
st.markdown("### Upload your resume, discover job opportunities, and get personalized career advice!")

# Sidebar
with st.sidebar:
    st.markdown("## 🎯 Navigation")
    page = st.radio(
        "Choose a section:",
        ["📤 Upload Resume", "🎯 Job Matches", "💡 Career Advice", "💬 Ask Questions"]
    )
    
    st.markdown("---")
    st.markdown("### About")
    st.info("This AI-powered tool analyzes your resume, extracts skills, matches you with relevant jobs, and provides career guidance.")
    
    if st.session_state.resume_data:
        st.success("✅ Resume uploaded!")
        if st.button("Reset Application"):
            st.session_state.resume_data = None
            st.session_state.skills_data = None
            st.session_state.job_matches = None
            st.session_state.chatbot = None
            st.session_state.chat_history = []
            st.rerun()

# Page 1: Upload Resume
if page == "📤 Upload Resume":
    st.markdown('<div class="sub-header">Upload Your Resume</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Choose your resume (PDF format)",
            type=['pdf'],
            help="Upload your resume in PDF format for analysis"
        )
        
        if uploaded_file is not None:
            with st.spinner("🔍 Analyzing your resume..."):
                try:
                    # Parse resume
                    parser = ResumeParser()
                    resume_data = parser.get_resume_data(uploaded_file)
                    st.session_state.resume_data = resume_data
                    
                    # Extract skills
                    skill_extractor = SkillExtractor()
                    skills_data = skill_extractor.extract_all_skills(resume_data)
                    st.session_state.skills_data = skills_data
                    
                    # Match jobs
                    matcher = JobMatcher()
                    job_recommendations = matcher.get_job_recommendations(skills_data, top_k=5)
                    st.session_state.job_matches = job_recommendations.get('top_matches', [])
                    
                    # Initialize chatbot
                    st.session_state.chatbot = ResumeChat(
                        resume_data=resume_data,
                        skills_data=skills_data,
                        job_matches=st.session_state.job_matches
                    )
                    
                    st.success("✅ Resume analyzed successfully!")
                    
                except Exception as e:
                    st.error(f"❌ Error analyzing resume: {str(e)}")
    
    with col2:
        st.info("""
        **Tips for best results:**
        - Use a well-formatted PDF
        - Include clear sections (Skills, Experience, Education)
        - List your technical skills explicitly
        """)
    
    # Display extracted information
    if st.session_state.resume_data:
        st.markdown("---")
        st.markdown('<div class="sub-header">📋 Extracted Information</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Name", st.session_state.resume_data.get('name', 'Not found'))
        with col2:
            st.metric("Email", st.session_state.resume_data.get('email', 'Not found'))
        with col3:
            st.metric("Phone", st.session_state.resume_data.get('phone', 'Not found'))
        
        # Skills summary
        if st.session_state.skills_data:
            st.markdown('<div class="sub-header">🎯 Skills Summary</div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Skills", st.session_state.skills_data.get('skills_count', 0))
            with col2:
                st.metric("Experience", f"{st.session_state.skills_data.get('experience_years', 0)} years")
            
            # Categorized skills
            categorized = st.session_state.skills_data.get('categorized_skills', {})
            if categorized:
                st.markdown("#### Skills by Category")
                for category, skills in categorized.items():
                    if skills:
                        st.markdown(f"**{category}:**")
                        skills_html = "".join([f'<span class="skill-badge" style="color: #09637E;">{skill}</span>' for skill in skills])
                        st.markdown(skills_html, unsafe_allow_html=True)

# Page 2: Job Matches
elif page == "🎯 Job Matches":
    st.markdown('<div class="sub-header">Your Job Matches</div>', unsafe_allow_html=True)
    
    if not st.session_state.job_matches:
        st.warning("⚠️ Please upload a resume first to see job matches!")
    else:
        st.success(f"Found {len(st.session_state.job_matches)} matching job roles for you!")
        
        # Display job matches
        for i, job in enumerate(st.session_state.job_matches, 1):
            with st.container():
                st.markdown(f'<div class="job-card">', unsafe_allow_html=True)
                
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"### {i}. {job['title']}")
                    st.markdown(f"**Category:** {job.get('category', 'N/A')}")
                    st.markdown(f"**Description:** {job.get('description', 'N/A')}")
                
                with col2:
                    match_score = job.get('final_score', job.get('match_percentage', 0))
                    st.metric("Match Score", f"{match_score:.1f}%")
                
                # Expandable details
                with st.expander("View Details"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**✅ Your Matching Skills:**")
                        matching = job.get('matching_skills', [])
                        if matching:
                            for skill in matching:
                                st.markdown(f"- {skill}")
                        else:
                            st.info("No direct matches found")
                    
                    with col2:
                        st.markdown("**📚 Skills to Learn:**")
                        missing = job.get('missing_skills', [])
                        if missing:
                            for skill in missing:
                                st.markdown(f"- {skill}")
                        else:
                            st.success("You have all required skills!")
                
                st.markdown('</div>', unsafe_allow_html=True)

# Page 3: Career Advice
elif page == "💡 Career Advice":
    st.markdown('<div class="sub-header">Personalized Career Advice</div>', unsafe_allow_html=True)
    
    if not st.session_state.job_matches or not st.session_state.skills_data:
        st.warning("⚠️ Please upload a resume first to get career advice!")
    else:
        advisor = CareerAdvisor()
        advice = advisor.get_career_advice(
            st.session_state.skills_data,
            st.session_state.job_matches
        )
        
        # Target Role
        st.markdown(f"### 🎯 Target Role: {advice['target_role']}")
        st.progress(advice['match_score'] / 100)
        st.caption(f"Match Score: {advice['match_score']:.1f}%")
        
        # Learning Path
        st.markdown("---")
        st.markdown("### 📚 Your Learning Path")
        learning_path = advice.get('learning_path', {})
        
        if learning_path.get('priority_skills'):
            st.markdown("#### 🔥 Priority Skills to Learn")
            for skill_info in learning_path['priority_skills']:
                with st.expander(f"⭐ {skill_info['skill']} - {skill_info['estimated_time']}"):
                    st.markdown(f"**Priority:** {skill_info['priority']}")
                    st.markdown("**Learning Resources:**")
                    for resource in skill_info['resources']:
                        st.markdown(f"- {resource}")
                    st.markdown("**Action Items:**")
                    for item in skill_info['action_items']:
                        st.markdown(f"- {item}")
        
        # Timeline
        st.info(f"⏰ **Estimated Timeline:** {learning_path.get('estimated_timeline', 'N/A')}")
        
        # Skill Gap Analysis
        st.markdown("---")
        st.markdown("### 📊 Skill Gap Analysis")
        gap_analysis = advice.get('skill_gap_analysis', {})
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Current Skills", gap_analysis.get('current_skills_count', 0))
        with col2:
            st.metric("Missing Skills", gap_analysis.get('missing_required_count', 0))
        with col3:
            st.metric("Coverage", f"{gap_analysis.get('skill_coverage_percentage', 0):.1f}%")
        
        # Top missing skills
        if gap_analysis.get('top_missing_skills'):
            st.markdown("#### 🎯 Top Skills to Focus On:")
            for skill in gap_analysis['top_missing_skills'][:5]:
                st.markdown(f"- **{skill}**")
        
        # Action Plan
        st.markdown("---")
        st.markdown("### 🚀 Your 30-60-90 Day Action Plan")
        action_plan = advice.get('action_plan', {})
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### 📅 First 30 Days")
            for item in action_plan.get('30_days', []):
                st.markdown(f"- {item}")
        
        with col2:
            st.markdown("#### 📅 60 Days")
            for item in action_plan.get('60_days', []):
                st.markdown(f"- {item}")
        
        with col3:
            st.markdown("#### 📅 90 Days")
            for item in action_plan.get('90_days', []):
                st.markdown(f"- {item}")
        
        # General Advice
        st.markdown("---")
        st.markdown("### 💬 General Career Advice")
        for tip in advice.get('general_advice', []):
            st.info(f"💡 {tip}")

# Page 4: Ask Questions
elif page == "💬 Ask Questions":
    st.markdown('<div class="sub-header">Ask About Your Resume</div>', unsafe_allow_html=True)
    
    if not st.session_state.chatbot:
        st.warning("⚠️ Please upload a resume first to start chatting!")
    else:
        st.info("💬 Ask me anything about your resume, skills, career advice, or job recommendations!")
        
        # Display chat history
        for message in st.session_state.chat_history:
            if message['role'] == 'user':
                with st.chat_message("user"):
                    st.markdown(message['content'])
            else:
                with st.chat_message("assistant"):
                    st.markdown(message['content'])
        
        # Chat input
        user_input = st.chat_input("Type your question here...")
        
        if user_input:
            # Add user message to history
            st.session_state.chat_history.append({
                'role': 'user',
                'content': user_input
            })
            
            # Get bot response
            response = st.session_state.chatbot.chat(user_input)
            
            # Add bot response to history
            st.session_state.chat_history.append({
                'role': 'assistant',
                'content': response
            })
            
            # Rerun to display new messages
            st.rerun()
        
        # Suggested questions
        st.markdown("---")
        st.markdown("#### 💡 Suggested Questions:")
        suggestions = [
            "What skills do I have?",
            "Show job recommendations",
            "How can I improve my Python skills?",
            "What skills am I missing for Data Scientist role?",
            "Show my resume summary"
        ]
        
        cols = st.columns(len(suggestions))
        for col, suggestion in zip(cols, suggestions):
            if col.button(suggestion, key=suggestion):
                st.session_state.chat_history.append({
                    'role': 'user',
                    'content': suggestion
                })
                response = st.session_state.chatbot.chat(suggestion)
                st.session_state.chat_history.append({
                    'role': 'assistant',
                    'content': response
                })
                st.rerun()

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: gray;'>
        <p>Built with ❤️ using Streamlit & HuggingFace | AI Resume Analyzer v1.0</p>
    </div>
""", unsafe_allow_html=True)