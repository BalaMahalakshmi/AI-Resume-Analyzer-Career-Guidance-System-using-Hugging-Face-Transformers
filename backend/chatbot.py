from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import torch
from typing import Dict, List

class ResumeChat:
    """Interactive chatbot for resume and career questions"""
    
    def __init__(self, resume_data: Dict = None, skills_data: Dict = None, 
                 job_matches: List[Dict] = None):
        """Initialize chatbot with resume context"""
        self.resume_data = resume_data or {}
        self.skills_data = skills_data or {}
        self.job_matches = job_matches or []
        self.conversation_history = []
        
        # Try to load a conversational model (we'll use a simpler approach for reliability)
        print("Initializing chatbot...")
        self.use_simple_mode = True  # Use template-based responses for reliability
        
    def update_context(self, resume_data: Dict = None, skills_data: Dict = None, 
                      job_matches: List[Dict] = None):
        """Update chatbot context with new data"""
        if resume_data:
            self.resume_data = resume_data
        if skills_data:
            self.skills_data = skills_data
        if job_matches:
            self.job_matches = job_matches
    
    def get_skills_summary(self) -> str:
        """Get a summary of extracted skills"""
        skills = self.skills_data.get('skills', [])
        skills_count = len(skills)
        experience = self.skills_data.get('experience_years', 0)
        
        if not skills:
            return "No skills have been extracted from your resume yet."
        
        categorized = self.skills_data.get('categorized_skills', {})
        summary = f"I found {skills_count} skills in your resume"
        
        if experience > 0:
            summary += f" with {experience} years of experience"
        
        summary += ". Your skills include:\n\n"
        
        for category, skills_list in categorized.items():
            if skills_list:
                summary += f"**{category}**: {', '.join(skills_list[:5])}\n"
        
        return summary
    
    def get_job_recommendations_summary(self) -> str:
        """Get a summary of job recommendations"""
        if not self.job_matches:
            return "No job matches have been generated yet. Upload a resume first!"
        
        summary = f"Based on your skills, here are your top {len(self.job_matches)} job recommendations:\n\n"
        
        for i, job in enumerate(self.job_matches[:5], 1):
            match_score = job.get('final_score', job.get('match_percentage', 0))
            summary += f"{i}. **{job['title']}** - {match_score:.1f}% match\n"
            summary += f"   Matching skills: {len(job.get('matching_skills', []))}\n"
            summary += f"   Skills to learn: {len(job.get('missing_skills', []))}\n\n"
        
        return summary
    
    def get_skill_improvement_advice(self, skill: str = None) -> str:
        """Get advice on improving specific skills"""
        if not self.job_matches:
            return "Upload a resume and get job matches first to receive personalized advice."
        
        top_job = self.job_matches[0]
        missing_skills = top_job.get('missing_skills', [])
        
        if not missing_skills:
            return f"Great! You already have all the required skills for {top_job['title']}. Consider advancing to more senior roles or specializing further."
        
        if skill:
            # Specific skill advice
            skill_lower = skill.lower()
            if skill_lower in [s.lower() for s in missing_skills]:
                return f"""To improve your **{skill}** skills:

1. **Learn the Basics**: Start with online tutorials and courses
   - Recommended: Search for '{skill} tutorial' on YouTube or Udemy
   - Read official documentation

2. **Build Projects**: Create 2-3 projects using {skill}
   - Start small with simple implementations
   - Gradually increase complexity

3. **Practice Daily**: Consistency is key
   - Spend 30-60 minutes daily practicing {skill}
   - Join coding challenges and competitions

4. **Get Feedback**: Share your work
   - Post projects on GitHub
   - Join communities and get code reviews

5. **Apply Knowledge**: Use it in real scenarios
   - Freelance projects
   - Contribute to open source
   - Update your portfolio

Estimated timeline: 2-3 months for beginner to intermediate level"""
            else:
                return f"You already have {skill}! Consider advancing to intermediate or expert level."
        
        # General improvement advice
        advice = f"""To improve your chances for **{top_job['title']}**, focus on these skills:\n\n"""
        
        for i, skill in enumerate(missing_skills[:5], 1):
            advice += f"{i}. **{skill}** - Critical skill\n"
        
        advice += "\n**Action Plan:**\n"
        advice += "- Focus on learning 1-2 skills at a time\n"
        advice += "- Build projects to demonstrate proficiency\n"
        advice += "- Update your resume and portfolio regularly\n"
        advice += "- Network with professionals in your target field\n"
        
        return advice
    
    def get_missing_skills_for_job(self, job_title: str = None) -> str:
        """Get missing skills for a specific job"""
        if not self.job_matches:
            return "No job matches available. Upload a resume first."
        
        if job_title:
            # Find specific job
            for job in self.job_matches:
                if job_title.lower() in job['title'].lower():
                    missing = job.get('missing_skills', [])
                    if not missing:
                        return f"You have all required skills for {job['title']}!"
                    
                    return f"Missing skills for **{job['title']}**:\n" + "\n".join([f"- {skill}" for skill in missing])
            
            return f"Job '{job_title}' not found in your matches."
        
        # Show missing skills for top job
        top_job = self.job_matches[0]
        missing = top_job.get('missing_skills', [])
        
        if not missing:
            return f"You have all required skills for {top_job['title']}!"
        
        return f"Missing skills for **{top_job['title']}**:\n" + "\n".join([f"- {skill}" for skill in missing])
    
    def get_resume_summary(self) -> str:
        """Get a summary of the resume"""
        if not self.resume_data:
            return "No resume data available."
        
        name = self.resume_data.get('name', 'Unknown')
        email = self.resume_data.get('email', 'Not found')
        phone = self.resume_data.get('phone', 'Not found')
        
        summary = f"**Resume Summary**\n\n"
        summary += f"Name: {name}\n"
        summary += f"Email: {email}\n"
        summary += f"Phone: {phone}\n\n"
        
        sections = self.resume_data.get('sections', {})
        if sections:
            for section_name, content in sections.items():
                if content:
                    summary += f"**{section_name.title()}**: Available\n"
        
        return summary
    
    def generate_response(self, query: str) -> str:
        """Generate response to user query"""
        query_lower = query.lower()
        
        # Skills-related queries
        if any(word in query_lower for word in ['skill', 'skills', 'what skills']):
            return self.get_skills_summary()
        
        # Job recommendations
        if any(word in query_lower for word in ['job', 'jobs', 'role', 'roles', 'recommend', 'suggestion']):
            return self.get_job_recommendations_summary()
        
        # Improvement advice
        if any(word in query_lower for word in ['improve', 'learn', 'study', 'get better']):
            # Check if specific skill mentioned
            skills = self.skills_data.get('skills', [])
            for skill in skills:
                if skill.lower() in query_lower:
                    return self.get_skill_improvement_advice(skill)
            return self.get_skill_improvement_advice()
        
        # Missing skills
        if any(word in query_lower for word in ['missing', 'lack', 'need', 'require', 'gap']):
            return self.get_missing_skills_for_job()
        
        # Resume summary
        if any(word in query_lower for word in ['resume', 'cv', 'profile', 'about me']):
            return self.get_resume_summary()
        
        # Experience
        if 'experience' in query_lower:
            exp_years = self.skills_data.get('experience_years', 0)
            if exp_years > 0:
                return f"Based on your resume, you have approximately {exp_years} years of experience."
            return "I couldn't determine your years of experience from the resume."
        
        # Specific job query
        if 'for' in query_lower and any(word in query_lower for word in ['software', 'data', 'developer', 'engineer']):
            # Extract job title from query
            for job in self.job_matches:
                if job['title'].lower() in query_lower:
                    return self.get_missing_skills_for_job(job['title'])
        
        # Default response with suggestions
        return """I can help you with:

- **"What skills do I have?"** - View your extracted skills
- **"Show job recommendations"** - See matching job roles
- **"How to improve [skill]?"** - Get learning advice for specific skills
- **"What skills am I missing?"** - See skill gaps for your target jobs
- **"Show my resume summary"** - View parsed resume information
- **"How many years of experience do I have?"** - View your experience

Ask me anything about your resume, skills, or career development!"""
    
    def chat(self, message: str) -> str:
        """Main chat interface"""
        # Add to conversation history
        self.conversation_history.append({
            'role': 'user',
            'content': message
        })
        
        # Generate response
        response = self.generate_response(message)
        
        # Add to conversation history
        self.conversation_history.append({
            'role': 'assistant',
            'content': response
        })
        
        return response
    
    def get_conversation_history(self) -> List[Dict]:
        """Get full conversation history"""
        return self.conversation_history
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []