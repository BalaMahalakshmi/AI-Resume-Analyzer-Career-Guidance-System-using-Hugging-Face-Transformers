import streamlit as st
import sys
import os

#  Fix import path - MUST be at the top before any other imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir  = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from backend.parser  import ResumeParser
from backend.skills  import SkillExtractor
from backend.matcher import JobMatcher
from backend.advisor import CareerAdvisor
from backend.chatbot import ResumeChat

# ─── Page Configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title = "AI Resume Analyzer",
    page_icon  = "📄",
    layout     = "wide"
)

# ─── Session State ─────────────────────────────────────────────────────────────
for key in ['resume_data', 'skills_data', 'job_matches', 'chatbot', 'chat_history', 'location']:
    if key not in st.session_state:
        st.session_state[key] = None if key != 'chat_history' else []
if 'location' not in st.session_state or st.session_state.location is None:
    st.session_state.location = "India"

# ─── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Overall page ── */
.main-header {
    font-size: 2.8rem;
    font-weight: 800;
    color: #1f77b4;
    text-align: center;
    margin-bottom: .5rem;
}
.sub-header {
    font-size: 1.5rem;
    font-weight: 700;
    color: #ff7f0e;
    margin-top: 1.5rem;
    margin-bottom: .8rem;
}

/* ── Job card ── */
.job-card {
    padding: 1.2rem 1.5rem;
    border-left: 5px solid #1f77b4;
    background: #f8f9fa;
    margin-bottom: 1.5rem;
    border-radius: 8px;
    box-shadow: 0 2px 6px rgba(0,0,0,.08);
}

/* ── Portal button ── */
.portal-btn {
    display: inline-block;
    padding: 8px 14px;
    border-radius: 8px;
    color: #fff !important;
    text-decoration: none !important;
    font-size: .85rem;
    font-weight: 600;
    margin: 4px 4px 4px 0;
    transition: opacity .2s, transform .15s;
    cursor: pointer;
}
.portal-btn:hover {
    opacity: .85;
    transform: translateY(-2px);
}

/* ── Skill badges ── */
.skill-badge {
    display: inline-block;
    padding: 3px 10px;
    margin: 3px;
    background: #e8f4f8;
    border-radius: 12px;
    font-size: .85rem;
    border: 1px solid #b8d8e8;
}
</style>
""", unsafe_allow_html=True)

# ─── Helper: render portal buttons ─────────────────────────────────────────────
def render_portal_buttons(job_portal_links: dict):
    """Render all job portal links as styled clickable buttons."""

    # Color map for portals
    portal_colors = {
        "LinkedIn":         "#0077B5",
        "LinkedIn (Skills)":"#005E8B",
        "Indeed":           "#003A9B",
        "Naukri":           "#FF7555",
        "Glassdoor":        "#0CAA41",
        "Monster":          "#6E45A5",
        "Internshala":      "#0073E6",
        "Shine":            "#F6A623",
        "Foundit":          "#E84B3A",
        "Wellfound":        "#000000",
        "Freshersworld":    "#E91E63",
    }

    portal_emojis = {
        "LinkedIn":         "💼",
        "LinkedIn (Skills)":"🎯",
        "Indeed":           "🔍",
        "Naukri":           "🇮🇳",
        "Glassdoor":        "🚪",
        "Monster":          "👾",
        "Internshala":      "🎓",
        "Shine":            "⭐",
        "Foundit":          "🔎",
        "Wellfound":        "🚀",
        "Freshersworld":    "🌟",
    }

    st.markdown("#### 🔗 Apply Now — Click to Open Job Portal:")

    buttons_html = ""
    for portal_name, link_info in job_portal_links.items():
        url   = link_info.get("url", "#")
        color = portal_colors.get(portal_name, "#555555")
        emoji = portal_emojis.get(portal_name, "🔗")

        buttons_html += f"""
        <a href="{url}" target="_blank" class="portal-btn"
           style="background-color:{color};">
           {emoji} {portal_name}
        </a>"""

    st.markdown(
        f'<div style="margin-top:8px;">{buttons_html}</div>',
        unsafe_allow_html=True
    )


# ═══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🎯 Navigation")
    page = st.radio(
        "Choose a section:",
        ["📤 Upload Resume", "🎯 Job Matches", "💡 Career Advice", "💬 Ask Questions"]
    )

    st.markdown("---")

    # Location selector
    st.markdown("### 🌍 Job Location")
    location = st.selectbox(
        "Preferred location for job search:",
        ["India", "Bangalore", "Mumbai", "Delhi", "Hyderabad",
         "Pune", "Chennai", "Kolkata", "Remote", "USA", "UK"],
        index=0
    )
    st.session_state.location = location

    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.info(
        "AI-powered resume analyzer that extracts your skills, "
        "matches you with relevant jobs, and links directly to job portals."
    )

    if st.session_state.resume_data:
        st.success("✅ Resume uploaded & analyzed!")
        if st.button("🔄 Reset / Upload New Resume"):
            for key in ['resume_data', 'skills_data', 'job_matches', 'chatbot']:
                st.session_state[key] = None
            st.session_state.chat_history = []
            st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
#  HEADER
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="main-header">📄 AI Resume Analyzer</div>', unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center; color:#555; font-size:1.05rem;'>"
    "Upload your resume → Get skill analysis → Find matching jobs → Apply directly! 🚀"
    "</p>",
    unsafe_allow_html=True
)


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE 1 — UPLOAD RESUME
# ═══════════════════════════════════════════════════════════════════════════════
if page == "📤 Upload Resume":
    st.markdown('<div class="sub-header">📤 Upload Your Resume</div>', unsafe_allow_html=True)

    col_upload, col_tips = st.columns([2, 1])

    with col_upload:
        uploaded_file = st.file_uploader(
            "Choose your resume (PDF format)",
            type=['pdf'],
            help="Upload your resume in PDF format"
        )

        if uploaded_file is not None:
            with st.spinner("🔍 Analyzing your resume... please wait"):
                try:
                    # 1. Parse resume
                    parser      = ResumeParser()
                    resume_data = parser.get_resume_data(uploaded_file)
                    st.session_state.resume_data = resume_data

                    # 2. Extract skills
                    extractor   = SkillExtractor()
                    skills_data = extractor.extract_all_skills(resume_data)
                    st.session_state.skills_data = skills_data

                    # 3. Match jobs (with portal links)
                    matcher          = JobMatcher()
                    recommendations  = matcher.get_job_recommendations(
                        skills_data, top_k=5,
                        location=st.session_state.location
                    )
                    st.session_state.job_matches = recommendations.get('top_matches', [])

                    # 4. Init chatbot
                    st.session_state.chatbot = ResumeChat(
                        resume_data  = resume_data,
                        skills_data  = skills_data,
                        job_matches  = st.session_state.job_matches
                    )

                    st.success("✅ Resume analyzed successfully! Go to **🎯 Job Matches** to see results.")

                except Exception as e:
                    st.error(f"❌ Error analyzing resume: {str(e)}")
                    st.error("Make sure your PDF is text-based (not scanned image).")

    with col_tips:
        st.info("""
**💡 Tips for best results:**

✅ Use a text-based PDF
✅ Add a clear **Skills** section
✅ Mention years of experience
✅ Use standard section headers
        """)

    # ── Show extracted information ──
    if st.session_state.resume_data:
        st.markdown("---")
        st.markdown('<div class="sub-header">📋 Extracted Information</div>', unsafe_allow_html=True)

        r = st.session_state.resume_data
        c1, c2, c3 = st.columns(3)
        c1.metric("👤 Name",  r.get('name',  'Not found'))
        c2.metric("📧 Email", r.get('email', 'Not found'))
        c3.metric("📞 Phone", r.get('phone', 'Not found'))

        # ── Skills Summary ──
        if st.session_state.skills_data:
            sd = st.session_state.skills_data
            st.markdown('<div class="sub-header">🎯 Skills Extracted</div>', unsafe_allow_html=True)

            m1, m2 = st.columns(2)
            m1.metric("Total Skills Found",   sd.get('skills_count', 0))
            m2.metric("Years of Experience",  f"{sd.get('experience_years', 0)} yrs")

            categorized = sd.get('categorized_skills', {})
            if categorized:
                st.markdown("#### Skills by Category:")
                for category, skills_list in categorized.items():
                    if skills_list:
                        badges = "".join(
                            f'<span style="color:black;" class="skill-badge">{s}</span>'
                            for s in skills_list
                        )
                        st.markdown(f"**{category}:** {badges}", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE 2 — JOB MATCHES  ← THE MAIN PAGE WITH LINKS
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🎯 Job Matches":
    st.markdown('<div class="sub-header">🎯 Your Top Job Matches</div>', unsafe_allow_html=True)

    if not st.session_state.job_matches:
        st.warning("⚠️ Please upload your resume first to see job matches!")
        st.info("👈 Go to **📤 Upload Resume** in the sidebar.")
    else:
        # ── Location refresh button ──
        col_info, col_refresh = st.columns([3, 1])
        with col_info:
            st.success(
                f"✅ Found **{len(st.session_state.job_matches)} matching job roles** "
                f"— portal links set for **{st.session_state.location}**"
            )
        with col_refresh:
            if st.button("🔄 Refresh Links for New Location"):
                if st.session_state.skills_data:
                    matcher         = JobMatcher()
                    recommendations = matcher.get_job_recommendations(
                        st.session_state.skills_data,
                        top_k=5,
                        location=st.session_state.location
                    )
                    st.session_state.job_matches = recommendations.get('top_matches', [])
                    st.rerun()

        st.markdown("---")

        # ── Render each job card ──────────────────────────────────────────────
        for rank, job in enumerate(st.session_state.job_matches, start=1):

            match_score = job.get('final_score', job.get('match_percentage', 0))
            title       = job.get('title', 'Unknown Role')
            category    = job.get('category', 'N/A')
            department  = job.get('department', 'N/A')
            description = job.get('description', 'N/A')
            matching    = job.get('matching_skills', [])
            missing     = job.get('missing_skills',  [])
            portal_links = job.get('job_portal_links', {})

            with st.container():
                st.markdown('<div class="job-card">', unsafe_allow_html=True)

                # ── Card header ──
                hcol1, hcol2, hcol3 = st.columns([4, 1, 1])
                with hcol1:
                    st.markdown(f"### {rank}. {title}")
                    st.markdown(
                        f"🏷️ **Category:** {category} &nbsp;|&nbsp; "
                        f"🎓 **Dept:** {department}",
                        unsafe_allow_html=True
                    )
                    st.markdown(f"📝 {description}")
                with hcol2:
                    st.metric("Match Score", f"{match_score:.1f}%")
                with hcol3:
                    st.metric("Skills Match", f"{len(matching)}/{len(matching)+len(missing)}")

                # ── Progress bar ──
                st.progress(min(match_score / 100, 1.0))

                st.markdown("---")

                # ════════════════════════════════════════════════════════
                #  JOB PORTAL LINKS  — clickable buttons
                # ════════════════════════════════════════════════════════
                if portal_links:
                    render_portal_buttons(portal_links)
                else:
                    st.warning("No job portal links available. Please re-upload your resume.")

                st.markdown("---")

                # ── Skill details (expandable) ──
                with st.expander(f"📊 View Skill Details for {title}"):
                    dc1, dc2 = st.columns(2)

                    with dc1:
                        st.markdown("**✅ Skills You Already Have:**")
                        if matching:
                            for skill in matching:
                                st.markdown(f"- ✅ {skill}")
                        else:
                            st.info("No direct skill matches found")

                    with dc2:
                        st.markdown("**📚 Skills You Need to Learn:**")
                        if missing:
                            for skill in missing:
                                st.markdown(f"- ❌ {skill}")
                        else:
                            st.success("🎉 You have ALL required skills!")

                    # Required vs nice-to-have
                    st.markdown("---")
                    st.markdown("**🔑 All Required Skills:**")
                    req_badges = "".join(
                        f'<span style="color:black;" class="skill-badge">{s}</span>'
                        for s in job.get('required_skills', [])
                    )
                    st.markdown(req_badges or "N/A", unsafe_allow_html=True)

                    st.markdown("**💡 Nice-to-Have Skills:**")
                    nice_badges = "".join(
                        f'<span style="color:black;" class="skill-badge" >{s}</span>'
                        for s in job.get('nice_to_have', [])
                    )
                    st.markdown(nice_badges or "N/A", unsafe_allow_html=True)

                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE 3 — CAREER ADVICE
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "💡 Career Advice":
    st.markdown('<div class="sub-header">💡 Personalized Career Advice</div>', unsafe_allow_html=True)

    if not st.session_state.job_matches or not st.session_state.skills_data:
        st.warning("⚠️ Please upload a resume first to get career advice!")
    else:
        advisor = CareerAdvisor()
        advice  = advisor.get_career_advice(
            st.session_state.skills_data,
            st.session_state.job_matches
        )

        # Target Role
        st.markdown(f"### 🎯 Target Role: **{advice['target_role']}**")
        st.progress(advice['match_score'] / 100)
        st.caption(f"Current Match Score: {advice['match_score']:.1f}%")

        # ── Learning Path ──
        st.markdown("---")
        st.markdown("### 📚 Your Learning Path")
        lp = advice.get('learning_path', {})

        if lp.get('priority_skills'):
            st.markdown("#### 🔥 Priority Skills to Learn:")
            for skill_info in lp['priority_skills']:
                with st.expander(f"⭐ {skill_info['skill']} — {skill_info['estimated_time']}"):
                    st.markdown(f"**Priority:** {skill_info['priority']}")
                    st.markdown("**Learning Resources:**")
                    for r in skill_info['resources']:
                        st.markdown(f"- {r}")
                    st.markdown("**Action Items:**")
                    for a in skill_info['action_items']:
                        st.markdown(f"- {a}")

        st.info(f"⏰ **Estimated Timeline:** {lp.get('estimated_timeline', 'N/A')}")

        # ── Skill Gap ──
        st.markdown("---")
        st.markdown("### 📊 Skill Gap Analysis")
        gap = advice.get('skill_gap_analysis', {})
        g1, g2, g3 = st.columns(3)
        g1.metric("Current Skills",  gap.get('current_skills_count', 0))
        g2.metric("Missing Skills",  gap.get('missing_required_count', 0))
        g3.metric("Coverage",        f"{gap.get('skill_coverage_percentage', 0):.1f}%")

        if gap.get('top_missing_skills'):
            st.markdown("#### 🎯 Top Skills to Focus On:")
            for s in gap['top_missing_skills'][:5]:
                st.markdown(f"- **{s}**")

        # ── Action Plan ──
        st.markdown("---")
        st.markdown("### 🚀 30 / 60 / 90 Day Action Plan")
        ap    = advice.get('action_plan', {})
        p1, p2, p3 = st.columns(3)
        with p1:
            st.markdown("#### 📅 First 30 Days")
            for item in ap.get('30_days', []):
                st.markdown(f"- {item}")
        with p2:
            st.markdown("#### 📅 60 Days")
            for item in ap.get('60_days', []):
                st.markdown(f"- {item}")
        with p3:
            st.markdown("#### 📅 90 Days")
            for item in ap.get('90_days', []):
                st.markdown(f"- {item}")

        # ── General Advice ──
        st.markdown("---")
        st.markdown("### 💬 General Career Advice")
        for tip in advice.get('general_advice', []):
            st.info(f"💡 {tip}")


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE 4 — ASK QUESTIONS
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "💬 Ask Questions":
    st.markdown('<div class="sub-header">💬 Ask About Your Resume</div>', unsafe_allow_html=True)

    if not st.session_state.chatbot:
        st.warning("⚠️ Please upload a resume first to start chatting!")
    else:
        st.info("Ask me anything about your resume, skills, career advice, or job recommendations!")

        # Chat history display
        for msg in st.session_state.chat_history:
            role = msg['role']
            with st.chat_message(role):
                st.markdown(msg['content'])

        # Chat input
        user_input = st.chat_input("Type your question here...")
        if user_input:
            st.session_state.chat_history.append({'role': 'user',      'content': user_input})
            response = st.session_state.chatbot.chat(user_input)
            st.session_state.chat_history.append({'role': 'assistant', 'content': response})
            st.rerun()

        # Suggested questions
        st.markdown("---")
        st.markdown("#### 💡 Suggested Questions:")
        suggestions = [
            "What skills do I have?",
            "Show job recommendations",
            "How can I improve my Python skills?",
            "What skills am I missing?",
            "Show my resume summary",
        ]
        cols = st.columns(len(suggestions))
        for col, suggestion in zip(cols, suggestions):
            if col.button(suggestion, key=f"btn_{suggestion}"):
                st.session_state.chat_history.append({'role': 'user',      'content': suggestion})
                response = st.session_state.chatbot.chat(suggestion)
                st.session_state.chat_history.append({'role': 'assistant', 'content': response})
                st.rerun()


# ─── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style='text-align:center; color:#888; font-size:.9rem;'>
    Built with ❤️ using Streamlit &amp; HuggingFace &nbsp;|&nbsp;
    AI Resume Analyzer v2.0 &nbsp;|&nbsp;
    Click any job portal button to apply! 🚀
</div>
""", unsafe_allow_html=True)