import re
from typing import Dict, List, Optional


class ResumeChat:
    """
    Intelligent chatbot that answers ANY question about the resume,
    skills, career advice, and job recommendations.
    """

    def __init__(self, resume_data: Dict = None,
                 skills_data: Dict = None,
                 job_matches: List[Dict] = None):
        self.resume_data       = resume_data  or {}
        self.skills_data       = skills_data  or {}
        self.job_matches       = job_matches  or []
        self.conversation_history: List[Dict] = []

    def update_context(self, resume_data=None, skills_data=None, job_matches=None):
        if resume_data:  self.resume_data  = resume_data
        if skills_data:  self.skills_data  = skills_data
        if job_matches:  self.job_matches  = job_matches

    # ═══════════════════════════════════════════════════════════════════════
    #  HELPER GETTERS
    # ═══════════════════════════════════════════════════════════════════════

    def _name(self)      -> str:       return self.resume_data.get('name',  'You')
    def _email(self)     -> str:       return self.resume_data.get('email', 'Not found')
    def _phone(self)     -> str:       return self.resume_data.get('phone', 'Not found')
    def _linkedin(self)  -> str:       return self.resume_data.get('linkedin', 'Not found')
    def _github(self)    -> str:       return self.resume_data.get('github',   'Not found')
    def _exp_years(self) -> int:       return self.skills_data.get('experience_years', 0)
    def _skills(self)    -> List[str]: return self.skills_data.get('skills', [])
    def _categorized(self) -> Dict:    return self.skills_data.get('categorized_skills', {})
    def _raw_text(self)  -> str:       return self.resume_data.get('text', '')
    def _sections(self)  -> Dict:      return self.resume_data.get('sections', {})

    # ═══════════════════════════════════════════════════════════════════════
    #  RESPONSE BUILDERS
    # ═══════════════════════════════════════════════════════════════════════

    def _resp_skills(self) -> str:
        skills = self._skills()
        if not skills:
            return "I couldn't find any recognizable skills in your resume. Please make sure your resume has a clear **Skills** section."

        categorized = self._categorized()
        exp         = self._exp_years()

        lines = [f"**{self._name()}**, I found **{len(skills)} skills** in your resume"]
        if exp:
            lines[0] += f" with **{exp} years** of experience"
        lines[0] += ":\n"

        for cat, cat_skills in categorized.items():
            if cat_skills:
                lines.append(f"**{cat}:** {', '.join(cat_skills)}")

        lines.append(f"\n📌 **Total: {len(skills)} skills detected**")
        return "\n\n".join(lines)

    def _resp_all_skills_list(self) -> str:
        skills = self._skills()
        if not skills:
            return "No skills found yet. Please upload your resume."
        skill_list = "\n".join([f"• {s}" for s in sorted(skills)])
        return f"**All {len(skills)} skills found in your resume:**\n\n{skill_list}"

    def _resp_jobs(self) -> str:
        if not self.job_matches:
            return "No job matches yet. Please upload your resume first."

        lines = [f"Based on your **{len(self._skills())} skills**, here are your **top job matches:**\n"]
        for i, job in enumerate(self.job_matches[:5], 1):
            score    = job.get('final_score', job.get('match_percentage', 0))
            title    = job.get('title', 'Unknown')
            matching = job.get('matching_skills', [])
            missing  = job.get('missing_skills',  [])
            lines.append(
                f"**{i}. {title}** — {score:.1f}% match\n"
                f"   ✅ You have: {len(matching)} required skills\n"
                f"   📚 Need to learn: {len(missing)} skills"
            )
        lines.append("\n👉 Go to **🎯 Job Matches** tab to see clickable job portal links!")
        return "\n\n".join(lines)

    def _resp_best_job(self) -> str:
        if not self.job_matches:
            return "Please upload your resume first to get job recommendations."
        top   = self.job_matches[0]
        score = top.get('final_score', top.get('match_percentage', 0))
        return (
            f"Your **best matching job** is **{top['title']}** "
            f"with a **{score:.1f}%** match score!\n\n"
            f"✅ Skills you already have: {', '.join(top.get('matching_skills', [])[:5]) or 'None detected'}\n\n"
            f"📚 Skills to learn: {', '.join(top.get('missing_skills', [])[:5]) or 'None — you have everything!'}\n\n"
            f"👉 Check the **🎯 Job Matches** tab to apply on portals like LinkedIn, Naukri, Indeed!"
        )

    def _resp_missing_skills(self, job_title: str = None) -> str:
        if not self.job_matches:
            return "Please upload your resume first."

        target = None
        if job_title:
            for j in self.job_matches:
                if job_title.lower() in j['title'].lower():
                    target = j
                    break

        target = target or self.job_matches[0]
        missing = target.get('missing_skills', [])

        if not missing:
            return f"🎉 Great news! You already have **all required skills** for **{target['title']}**!"

        lines = [f"**Skills you need for {target['title']}:**\n"]
        for s in missing:
            lines.append(f"❌ {s}")
        lines.append(f"\n💡 Focus on the top 2-3 skills first, build projects, and update your resume!")
        return "\n".join(lines)

    def _resp_improve_skill(self, skill: str) -> str:
        skill_clean = skill.strip().title()
        return (
            f"**How to improve your {skill_clean} skills:**\n\n"
            f"**1️⃣ Learn the Basics:**\n"
            f"• Search for '{skill_clean} tutorial' on YouTube, Udemy, or Coursera\n"
            f"• Read the official {skill_clean} documentation\n\n"
            f"**2️⃣ Practice Daily:**\n"
            f"• Spend 30–60 minutes daily on {skill_clean}\n"
            f"• Solve problems on LeetCode, HackerRank, or Kaggle\n\n"
            f"**3️⃣ Build Projects:**\n"
            f"• Create 2–3 real projects using {skill_clean}\n"
            f"• Push them to GitHub for your portfolio\n\n"
            f"**4️⃣ Get Certified:**\n"
            f"• Look for {skill_clean} certifications on Coursera, edX, or LinkedIn Learning\n\n"
            f"**5️⃣ Apply It:**\n"
            f"• Contribute to open source projects\n"
            f"• Try freelance tasks using {skill_clean}\n\n"
            f"⏱️ **Estimated time:** 2–3 months to reach intermediate level with daily practice!"
        )

    def _resp_experience(self) -> str:
        exp = self._exp_years()
        if exp > 0:
            level = "entry-level" if exp < 2 else ("mid-level" if exp < 5 else "senior-level")
            return (
                f"Based on your resume, you have approximately **{exp} years** of experience.\n\n"
                f"This places you at a **{level}** position.\n\n"
                + (
                    "💡 Focus on building projects and getting internships to boost your profile."
                    if exp < 2 else
                    "💡 You're ready for mid-level roles. Consider specializing in 2–3 key technologies."
                    if exp < 5 else
                    "💡 You qualify for senior/lead roles. Consider cloud certifications or architecture skills."
                )
            )
        return (
            "I couldn't detect explicit years of experience from your resume.\n\n"
            "💡 **Tip:** Add a line like *'2 years of experience in Python and Machine Learning'* "
            "to your resume summary or experience section for better matching."
        )

    def _resp_summary(self) -> str:
        sections  = self._sections()
        skills    = self._skills()
        exp       = self._exp_years()
        top_job   = self.job_matches[0]['title'] if self.job_matches else "N/A"
        top_score = self.job_matches[0].get('final_score', 0) if self.job_matches else 0

        lines = [
            f"## 📋 Resume Summary for **{self._name()}**\n",
            f"**📧 Email:** {self._email()}",
            f"**📞 Phone:** {self._phone()}",
        ]
        if self._linkedin() != 'Not found':
            lines.append(f"**🔗 LinkedIn:** {self._linkedin()}")
        if self._github() != 'Not found':
            lines.append(f"**🐙 GitHub:** {self._github()}")

        lines += [
            f"\n**🎯 Skills Found:** {len(skills)}",
            f"**📅 Experience:** {exp} years" if exp else "**📅 Experience:** Not detected",
            f"**🏆 Best Job Match:** {top_job} ({top_score:.1f}%)" if top_job != "N/A" else "",
        ]

        if sections.get('education'):
            edu_text = sections['education'][:200].strip().replace('\n', ' ')
            lines.append(f"\n**🎓 Education:** {edu_text}...")

        if sections.get('summary') or sections.get('experience'):
            sec = sections.get('summary') or sections.get('experience')
            preview = sec[:200].strip().replace('\n', ' ')
            lines.append(f"\n**💼 Profile Preview:** {preview}...")

        return "\n".join([l for l in lines if l])

    def _resp_education(self) -> str:
        sections = self._sections()
        edu = sections.get('education', '')
        if edu:
            return f"**🎓 Education Details from your resume:**\n\n{edu[:500]}"
        return "I couldn't find a clear Education section in your resume. Make sure it's labeled **'Education'**."

    def _resp_projects(self) -> str:
        sections = self._sections()
        proj = sections.get('projects', '')
        if proj:
            return f"**💻 Projects from your resume:**\n\n{proj[:600]}"
        return "I couldn't find a Projects section. Adding a projects section greatly improves job matching!"

    def _resp_certifications(self) -> str:
        sections = self._sections()
        certs = sections.get('certifications', '')
        if certs:
            return f"**📜 Certifications from your resume:**\n\n{certs[:400]}"
        return (
            "I couldn't find certifications in your resume.\n\n"
            "💡 **Recommended certifications:**\n"
            "• AWS Certified Solutions Architect\n"
            "• Google Data Analytics Certificate\n"
            "• Microsoft Azure Fundamentals\n"
            "• Coursera Machine Learning Specialization"
        )

    def _resp_salary(self, job_title: str = None) -> str:
        salary_data = {
            'software engineer':       ('₹5–12 LPA', 'entry → ₹20–40 LPA senior'),
            'data scientist':          ('₹6–14 LPA', 'entry → ₹25–50 LPA senior'),
            'machine learning engineer':('₹7–16 LPA','entry → ₹30–60 LPA senior'),
            'frontend developer':      ('₹4–10 LPA', 'entry → ₹15–30 LPA senior'),
            'backend developer':       ('₹5–12 LPA', 'entry → ₹18–35 LPA senior'),
            'devops engineer':         ('₹6–15 LPA', 'entry → ₹25–50 LPA senior'),
            'cybersecurity analyst':   ('₹5–12 LPA', 'entry → ₹20–40 LPA senior'),
            'data analyst':            ('₹4–10 LPA', 'entry → ₹15–25 LPA senior'),
            'full stack developer':    ('₹5–12 LPA', 'entry → ₹20–40 LPA senior'),
        }

        if job_title:
            for key, (entry, growth) in salary_data.items():
                if key in job_title.lower():
                    return (
                        f"**💰 Salary for {job_title.title()} in India:**\n\n"
                        f"• **Entry Level (0–2 yrs):** {entry}\n"
                        f"• **Growth:** {growth}\n\n"
                        "💡 Salaries vary by city — Bangalore, Mumbai, Hyderabad pay 20–30% more.\n"
                        "🔗 Check Glassdoor and LinkedIn Salary for accurate, up-to-date data."
                    )

        if self.job_matches:
            top = self.job_matches[0]['title'].lower()
            for key, (entry, growth) in salary_data.items():
                if key in top:
                    return (
                        f"**💰 Expected Salary for {self.job_matches[0]['title']}:**\n\n"
                        f"• **Entry Level:** {entry}\n"
                        f"• **Growth Path:** {growth}\n\n"
                        "🔗 Check Glassdoor, LinkedIn Salary, or AmbitionBox for latest data."
                    )

        return (
            "**💰 Average Tech Salaries in India:**\n\n"
            "• Software Engineer: ₹5–12 LPA (fresher) → ₹20–40 LPA (senior)\n"
            "• Data Scientist: ₹6–14 LPA → ₹25–50 LPA\n"
            "• ML Engineer: ₹7–16 LPA → ₹30–60 LPA\n"
            "• DevOps: ₹6–15 LPA → ₹25–50 LPA\n"
            "• Cybersecurity: ₹5–12 LPA → ₹20–40 LPA\n\n"
            "🔗 Use **Glassdoor**, **LinkedIn Salary**, or **AmbitionBox** for precise data."
        )

    def _resp_interview_tips(self, job_title: str = None) -> str:
        role = job_title or (self.job_matches[0]['title'] if self.job_matches else "software engineering")
        return (
            f"**🎯 Interview Tips for {role}:**\n\n"
            "**📚 Technical Preparation:**\n"
            "• Revise Data Structures & Algorithms (LeetCode Easy/Medium)\n"
            "• Practice 50+ coding problems before the interview\n"
            "• Study system design basics (for senior roles)\n"
            "• Review all skills listed on your resume\n\n"
            "**💬 Behavioral Preparation:**\n"
            "• Prepare STAR method answers (Situation, Task, Action, Result)\n"
            "• Practice explaining your projects clearly in 2 minutes\n"
            "• Research the company before the interview\n\n"
            "**🔧 On Interview Day:**\n"
            "• Arrive 10 minutes early (or test your video setup for online)\n"
            "• Think out loud when solving problems\n"
            "• Ask clarifying questions before coding\n"
            "• Always prepare 2–3 questions to ask the interviewer\n\n"
            "**📌 Resources:**\n"
            "• LeetCode, HackerRank for coding\n"
            "• Glassdoor for company-specific questions\n"
            "• GeeksforGeeks for CS fundamentals"
        )

    def _resp_resume_tips(self) -> str:
        tips = []
        skills = self._skills()
        sections = self._sections()
        phone = self._phone()

        tips.append("**📝 Resume Improvement Tips for You:**\n")

        if phone == 'Not found':
            tips.append("❗ **Add your phone number** — it's missing or not in a standard format")

        if len(skills) < 10:
            tips.append("❗ **Add more skills** — you only have a few detected skills; list all your tools and technologies")

        if not sections.get('projects'):
            tips.append("💡 **Add a Projects section** — showcasing real projects greatly helps with matching")

        if not sections.get('certifications'):
            tips.append("💡 **Add Certifications** — even free courses from Coursera/Udemy count")

        if not sections.get('summary'):
            tips.append("💡 **Add a Summary/Objective** — a 3-line professional summary at the top helps recruiters")

        if self._exp_years() == 0:
            tips.append("💡 **Mention experience years** — add '2 years of experience' in your summary")

        tips.append("\n✅ **General Best Practices:**")
        tips.append("• Keep resume to 1 page (freshers) or 2 pages max")
        tips.append("• Use bullet points, not paragraphs")
        tips.append("• Quantify achievements (e.g., 'Improved accuracy by 15%')")
        tips.append("• Use ATS-friendly formatting (no tables or text boxes)")
        tips.append("• Save as PDF before uploading to job portals")

        return "\n".join(tips)

    def _resp_action_plan(self) -> str:
        top_job = self.job_matches[0]['title'] if self.job_matches else "your target role"
        missing = self.job_matches[0].get('missing_skills', [])[:3] if self.job_matches else []
        skills_str = ", ".join(missing) if missing else "key required skills"

        return (
            f"**🚀 Your Personal Action Plan for {top_job}:**\n\n"
            f"**📅 Next 30 Days:**\n"
            f"• Start learning: {skills_str}\n"
            f"• Complete 1 online course in your weakest skill\n"
            f"• Update your resume with all skills\n"
            f"• Create/update your LinkedIn profile\n\n"
            f"**📅 Next 60 Days:**\n"
            f"• Build 2–3 projects using new skills\n"
            f"• Push projects to GitHub\n"
            f"• Start applying on LinkedIn, Naukri, Indeed\n"
            f"• Attend 1–2 networking events or webinars\n\n"
            f"**📅 Next 90 Days:**\n"
            f"• Apply to 5–10 companies weekly\n"
            f"• Get 1 freelance or internship project\n"
            f"• Prepare for technical interviews\n"
            f"• Target companies actively hiring for {top_job}"
        )

    def _resp_company_suggestions(self) -> str:
        top_job = self.job_matches[0]['title'].lower() if self.job_matches else ""
        companies = {
            'software':       ['TCS', 'Infosys', 'Wipro', 'HCL', 'Accenture', 'Cognizant', 'Capgemini'],
            'data':           ['Amazon', 'Google', 'Microsoft', 'Flipkart', 'Swiggy', 'Zomato', 'Meesho'],
            'machine learning':['Google DeepMind', 'NVIDIA', 'Intel', 'IBM', 'Amazon AWS', 'Fractal Analytics'],
            'devops':         ['Amazon AWS', 'Microsoft Azure', 'IBM', 'Red Hat', 'HashiCorp'],
            'cybersecurity':  ['Palo Alto', 'Cisco', 'IBM Security', 'Check Point', 'KPMG'],
            'frontend':       ['Razorpay', 'PhonePe', 'Groww', 'Zepto', 'Meesho', 'CRED'],
            'full stack':     ['Freshworks', 'Zoho', 'Chargebee', 'Postman', 'BrowserStack'],
        }

        matched = []
        for key, comps in companies.items():
            if key in top_job:
                matched = comps
                break

        if not matched:
            matched = ['TCS', 'Infosys', 'Wipro', 'Amazon', 'Microsoft', 'Google', 'Accenture']

        role = self.job_matches[0]['title'] if self.job_matches else "your target role"
        comp_list = "\n".join([f"• {c}" for c in matched])
        return (
            f"**🏢 Top Companies Hiring for {role}:**\n\n"
            f"{comp_list}\n\n"
            "💡 **How to apply:**\n"
            "• Visit their careers page directly\n"
            "• Apply via LinkedIn / Naukri (use the portals in Job Matches tab)\n"
            "• Referrals increase your chances by 5x — connect with employees on LinkedIn!"
        )

    def _resp_profile_score(self) -> str:
        skills_count = len(self._skills())
        has_sections = self._sections()
        exp          = self._exp_years()
        top_score    = self.job_matches[0].get('final_score', 0) if self.job_matches else 0

        score = 0
        feedback = []

        # Skills (30 pts)
        if skills_count >= 20: score += 30; feedback.append("✅ Great skill variety")
        elif skills_count >= 10: score += 20; feedback.append("⚠️ Add more skills (currently {})".format(skills_count))
        else: score += 10; feedback.append("❌ Very few skills detected — add more!")

        # Sections (30 pts)
        for sec in ['education', 'experience', 'skills', 'projects']:
            if has_sections.get(sec): score += 7

        # Experience (20 pts)
        if exp >= 3: score += 20
        elif exp >= 1: score += 12; feedback.append("💡 More experience needed")
        else: score += 5; feedback.append("💡 Build internship/project experience")

        # Job match (20 pts)
        if top_score >= 70: score += 20
        elif top_score >= 40: score += 12
        else: score += 5; feedback.append("💡 Add more relevant skills for better job matching")

        grade = "⭐⭐⭐⭐⭐ Excellent" if score >= 85 else \
                "⭐⭐⭐⭐ Good" if score >= 70 else \
                "⭐⭐⭐ Average" if score >= 55 else "⭐⭐ Needs Improvement"

        return (
            f"**📊 Your Resume Profile Score: {score}/100**\n\n"
            f"**Grade: {grade}**\n\n"
            "**Breakdown:**\n"
            + "\n".join(feedback) +
            "\n\n💡 Go to **💡 Career Advice** tab for a detailed improvement plan!"
        )

    def _resp_default(self, query: str) -> str:
        """Smart default handler that tries to find relevant info from resume text"""
        text_lower = self._raw_text().lower()
        query_lower = query.lower()

        # Search resume text for query keywords
        keywords = [w for w in query_lower.split() if len(w) > 3]
        found_context = []

        for kw in keywords:
            # Find sentence containing keyword in resume text
            sentences = re.split(r'[.\n]', self._raw_text())
            for sent in sentences:
                if kw in sent.lower() and len(sent.strip()) > 10:
                    found_context.append(sent.strip()[:150])
                    break

        if found_context:
            context_str = "\n".join([f"• {c}" for c in found_context[:3]])
            return (
                f"Based on your resume, here's what I found related to **'{query}'**:\n\n"
                f"{context_str}\n\n"
                "💡 For more specific answers, you can ask me:\n"
                "• 'What are my skills?'\n"
                "• 'What jobs match me?'\n"
                "• 'How do I improve [skill name]?'\n"
                "• 'What is my profile score?'"
            )

        return (
            f"I couldn't find specific information about **'{query}'** in your resume.\n\n"
            "Here's what I **can** answer for you:\n\n"
            "🔹 **Skills:** 'What skills do I have?' | 'Show all my skills'\n"
            "🔹 **Jobs:** 'Show job recommendations' | 'What is my best job match?'\n"
            "🔹 **Missing skills:** 'What am I missing for [job]?'\n"
            "🔹 **Improvement:** 'How to improve Python?' | 'How to improve my resume?'\n"
            "🔹 **Profile:** 'What is my profile score?' | 'Show resume summary'\n"
            "🔹 **Career:** 'Give me action plan' | 'Interview tips'\n"
            "🔹 **Salary:** 'What is the salary for [job]?'\n"
            "🔹 **Companies:** 'Which companies should I apply to?'"
        )

    # ═══════════════════════════════════════════════════════════════════════
    #  MAIN INTENT ROUTER
    # ═══════════════════════════════════════════════════════════════════════

    def generate_response(self, query: str) -> str:
        q = query.lower().strip()

        # ── 1. Skills queries ───────────────────────────────────────────────
        if re.search(r'\ball\s+skills?\b|\blist\s+skills?\b|\bshow\s+all', q):
            return self._resp_all_skills_list()

        if re.search(r'\bskills?\b|\bwhat\s+(?:skills|can|do)\b|\bmy\s+skills?\b'
                     r'|\btechnologies\b|\btools\b', q):
            return self._resp_skills()

        # ── 2. Job recommendations ──────────────────────────────────────────
        if re.search(r'\bbest\s+(?:job|match|role)\b|\btop\s+job\b', q):
            return self._resp_best_job()

        if re.search(r'\bjobs?\b|\bmatches?\b|\broles?\b|\brecommend\b'
                     r'|\bsuggestions?\b|\bopportunities\b', q):
            return self._resp_jobs()

        # ── 3. Missing skills ───────────────────────────────────────────────
        if re.search(r'\bmissing\b|\black\b|\bneed\b|\bgap\b|\brequire\b', q):
            # Check if a specific job title is mentioned
            for job in self.job_matches:
                if job['title'].lower() in q:
                    return self._resp_missing_skills(job['title'])
            return self._resp_missing_skills()

        # ── 4. Improve / learn a specific skill ─────────────────────────────
        improve_match = re.search(
            r'(?:improve|learn|study|get\s+better|how\s+to\s+(?:learn|improve))'
            r'[\s\w]*?([\w.+#]+(?:\s[\w.+#]+)?)',
            q
        )
        if improve_match:
            skill = improve_match.group(1).strip()
            # Ignore generic words
            ignore = {'my', 'the', 'a', 'an', 'in', 'for', 'at', 'to', 'how', 'skill'}
            if skill.lower() not in ignore and len(skill) > 1:
                return self._resp_improve_skill(skill)

        if re.search(r'\bimprove\b|\blearn\b|\bstudy\b|\bget\s+better\b', q):
            if self.job_matches:
                missing = self.job_matches[0].get('missing_skills', [])
                if missing:
                    return self._resp_improve_skill(missing[0])
            return self._resp_improve_skill("your top priority skill")

        # ── 5. Resume / profile queries ─────────────────────────────────────
        if re.search(r'\bsummary\b|\babout\s+me\b|\bprofile\b|\bresume\s+detail', q):
            return self._resp_summary()

        if re.search(r'\beducation\b|\bdegree\b|\bcollege\b|\buniversity\b|\bqualif', q):
            return self._resp_education()

        if re.search(r'\bprojects?\b|\bportfolio\b', q):
            return self._resp_projects()

        if re.search(r'\bcertif\b|\bcourses?\b|\btraining\b|\bcredential', q):
            return self._resp_certifications()

        if re.search(r'\bscore\b|\brating\b|\bgrade\b|\bhow\s+good\b|\brank\b', q):
            return self._resp_profile_score()

        if re.search(r'\bimprove\s+(?:my\s+)?resume\b|\bresume\s+tips?\b|\bbetter\s+resume\b', q):
            return self._resp_resume_tips()

        # ── 6. Experience ───────────────────────────────────────────────────
        if re.search(r'\bexperience\b|\byears?\b|\bwork\s+history\b', q):
            return self._resp_experience()

        # ── 7. Contact details ──────────────────────────────────────────────
        if re.search(r'\bphone\b|\bmobile\b|\bcontact\b|\bemail\b|\blinkedin\b|\bgithub\b', q):
            return (
                f"**📞 Contact Details:**\n\n"
                f"• Name: {self._name()}\n"
                f"• Email: {self._email()}\n"
                f"• Phone: {self._phone()}\n"
                f"• LinkedIn: {self._linkedin()}\n"
                f"• GitHub: {self._github()}"
            )

        # ── 8. Salary ───────────────────────────────────────────────────────
        if re.search(r'\bsalar\b|\bpay\b|\bctc\b|\bpackage\b|\blpa\b|\bincome\b', q):
            for job in self.job_matches:
                if job['title'].lower() in q:
                    return self._resp_salary(job['title'])
            return self._resp_salary()

        # ── 9. Interview tips ───────────────────────────────────────────────
        if re.search(r'\binterview\b|\bprepare\b|\bpreparation\b|\btips?\b', q):
            return self._resp_interview_tips()

        # ── 10. Companies ───────────────────────────────────────────────────
        if re.search(r'\bcompan\b|\borganiz\b|\bfirm\b|\bwhere\s+(?:to\s+)?apply\b'
                     r'|\bwhich\s+compan\b', q):
            return self._resp_company_suggestions()

        # ── 11. Action plan / roadmap ───────────────────────────────────────
        if re.search(r'\bplan\b|\broadmap\b|\bsteps?\b|\bwhat\s+(?:should|to)\s+do\b'
                     r'|\bnext\b|\bstart\b', q):
            return self._resp_action_plan()

        # ── 12. Resume tips ─────────────────────────────────────────────────
        if re.search(r'\btips?\b|\bsuggestions?\b|\bimprov\b|\bfix\b|\bbetter\b', q):
            return self._resp_resume_tips()

        # ── 13. Greetings ───────────────────────────────────────────────────
        if re.search(r'\b(?:hi|hello|hey|good\s+(?:morning|evening|afternoon))\b', q):
            return (
                f"Hello **{self._name()}**! 👋\n\n"
                "I'm your AI Career Assistant. I can help you with:\n\n"
                "🔹 Analyzing your skills from your resume\n"
                "🔹 Suggesting the best job roles for you\n"
                "🔹 Showing what skills you're missing\n"
                "🔹 Giving career tips and improvement advice\n"
                "🔹 Interview preparation tips\n"
                "🔹 Salary information\n\n"
                "**Ask me anything!** For example:\n"
                "• 'What are my strongest skills?'\n"
                "• 'Which job should I target?'\n"
                "• 'How do I improve my Python?'"
            )

        # ── 14. Thank you ───────────────────────────────────────────────────
        if re.search(r'\bthank\b|\bthanks\b|\bthank\s+you\b', q):
            return (
                f"You're welcome, **{self._name()}**! 😊\n\n"
                "Best of luck with your job search! 🚀\n"
                "Feel free to ask me anything anytime!"
            )

        # ── 15. Default: search resume text ─────────────────────────────────
        return self._resp_default(query)

    # ═══════════════════════════════════════════════════════════════════════
    #  PUBLIC API
    # ═══════════════════════════════════════════════════════════════════════

    def chat(self, message: str) -> str:
        """Main entry point — accepts any message and returns a response"""
        self.conversation_history.append({'role': 'user', 'content': message})
        response = self.generate_response(message)
        self.conversation_history.append({'role': 'assistant', 'content': response})
        return response

    def get_conversation_history(self) -> List[Dict]:
        return self.conversation_history

    def clear_history(self):
        self.conversation_history = []