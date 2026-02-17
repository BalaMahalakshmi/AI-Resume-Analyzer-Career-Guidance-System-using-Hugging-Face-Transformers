import json
import sys
import os

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from typing import List, Dict, Set
from model.embeddings import EmbeddingModel


def generate_job_portal_links(job_title: str, skills: List[str] = [], location: str = "India") -> Dict:
    """
    Generate clickable job portal links for a given job title and skills.
    These links redirect directly to search results on each job portal.
    """

    # URL-encode job title and location
    job_query      = job_title.strip().replace(" ", "+")
    location_query = location.strip().replace(" ", "+")
    job_slug       = job_title.strip().lower().replace(" ", "-")

    # Top 3 skills as search keywords
    top_skills        = skills[:3] if len(skills) >= 3 else skills
    skills_query      = "+".join([s.replace(" ", "+") for s in top_skills])

    job_portal_links = {
        "LinkedIn": {
            "url":   f"https://www.linkedin.com/jobs/search/?keywords={job_query}&location={location_query}",
            "color": "#0077B5",
            "emoji": "💼"
        },
        "Indeed": {
            "url":   f"https://www.indeed.co.in/jobs?q={job_query}&l={location_query}",
            "color": "#003A9B",
            "emoji": "🔍"
        },
        "Naukri": {
            "url":   f"https://www.naukri.com/{job_slug}-jobs",
            "color": "#FF7555",
            "emoji": "🇮🇳"
        },
        "Glassdoor": {
            "url":   f"https://www.glassdoor.co.in/Job/jobs.htm?sc.keyword={job_query}&locT=C&locId=115",
            "color": "#0CAA41",
            "emoji": "🚪"
        },
        "Monster": {
            "url":   f"https://www.monsterindia.com/search/{job_slug}-jobs",
            "color": "#6E45A5",
            "emoji": "👾"
        },
        "Internshala": {
            "url":   f"https://internshala.com/jobs/{job_slug}-jobs",
            "color": "#0073E6",
            "emoji": "🎓"
        },
        "Shine": {
            "url":   f"https://www.shine.com/job-search/{job_slug}-jobs",
            "color": "#F6A623",
            "emoji": "⭐"
        },
        "Foundit": {
            "url":   f"https://www.foundit.in/srp/results?query={job_query}&locations={location_query}",
            "color": "#E84B3A",
            "emoji": "🔎"
        },
        "Wellfound": {
            "url":   f"https://wellfound.com/jobs?q={job_query}",
            "color": "#000000",
            "emoji": "🚀"
        },
        "Freshersworld": {
            "url":   f"https://www.freshersworld.com/jobs/jobsearch/{job_slug}-jobs",
            "color": "#E91E63",
            "emoji": "🌟"
        },
    }

    # If skills are available, add a skills-based LinkedIn search as bonus
    if top_skills:
        job_portal_links["LinkedIn (Skills)"] = {
            "url":   f"https://www.linkedin.com/jobs/search/?keywords={skills_query}&location={location_query}",
            "color": "#005E8B",
            "emoji": "🎯"
        }

    return job_portal_links


class JobMatcher:
    """Match resume skills with suitable job roles"""

    def __init__(self, job_roles_path: str = None):
        """Initialize matcher with job roles data"""
        if job_roles_path is None:
            # Auto-detect path
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            job_roles_path = os.path.join(base_dir, 'data', 'job_roles.json')

        self.job_roles      = self.load_job_roles(job_roles_path)
        self.embedding_model = EmbeddingModel()

        # Pre-compute job embeddings
        print("Computing job role embeddings...")
        self.job_embeddings, self.job_roles_list = self.embedding_model.embed_job_roles(
            self.job_roles['job_roles']
        )

    def load_job_roles(self, path: str) -> dict:
        """Load job roles from JSON file"""
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Job roles file not found at {path}")
            return {"job_roles": []}

    def calculate_skill_match(self, resume_skills: List[str], job_skills: List[str]) -> float:
        """Calculate percentage of matching skills"""
        if not job_skills:
            return 0.0
        resume_lower = {s.lower() for s in resume_skills}
        job_lower    = {s.lower() for s in job_skills}
        matching     = resume_lower.intersection(job_lower)
        return (len(matching) / len(job_lower)) * 100

    def get_matching_skills(self, resume_skills: List[str], job_skills: List[str]) -> List[str]:
        """Get list of matching skills"""
        resume_lower = {s.lower(): s for s in resume_skills}
        job_lower    = {s.lower() for s in job_skills}
        return [resume_lower[s] for s in resume_lower if s in job_lower]

    def get_missing_skills(self, resume_skills: List[str], job_skills: List[str]) -> List[str]:
        """Get list of skills required but not in resume"""
        resume_lower = {s.lower() for s in resume_skills}
        return [s for s in job_skills if s.lower() not in resume_lower]

    def match_jobs_by_skills(self, resume_skills: List[str], top_k: int = 5) -> List[Dict]:
        """Match jobs based on skill overlap"""
        matches = []
        for job in self.job_roles['job_roles']:
            required      = job.get('required_skills', [])
            nice          = job.get('nice_to_have', [])
            all_skills    = required + nice
            req_match     = self.calculate_skill_match(resume_skills, required)
            overall_match = self.calculate_skill_match(resume_skills, all_skills)
            job_match = {
                **job,
                'required_skill_match': round(req_match, 2),
                'overall_skill_match':  round(overall_match, 2),
                'matching_skills':      self.get_matching_skills(resume_skills, all_skills),
                'missing_skills':       self.get_missing_skills(resume_skills, required),
            }
            matches.append(job_match)
        matches.sort(
            key=lambda x: (x['required_skill_match'], x['overall_skill_match']),
            reverse=True
        )
        return matches[:top_k]

    def match_jobs_by_embeddings(self, resume_skills: List[str],
                                  experience_years: int = 0, top_k: int = 5) -> List[Dict]:
        """Match jobs using semantic embeddings"""
        resume_text      = self.embedding_model.create_skill_profile_text(resume_skills, experience_years)
        resume_embedding = self.embedding_model.generate_embedding(resume_text)
        matches          = self.embedding_model.find_top_matches(
            resume_embedding, self.job_embeddings, self.job_roles_list, top_k
        )
        for match in matches:
            required = match.get('required_skills', [])
            all_sk   = required + match.get('nice_to_have', [])
            match['matching_skills']      = self.get_matching_skills(resume_skills, all_sk)
            match['missing_skills']       = self.get_missing_skills(resume_skills, required)
            match['required_skill_match'] = self.calculate_skill_match(resume_skills, required)
        return matches

    def get_hybrid_matches(self, resume_skills: List[str],
                            experience_years: int = 0, top_k: int = 5) -> List[Dict]:
        """Hybrid matching: skill-based + embedding-based"""
        skill_matches     = self.match_jobs_by_skills(resume_skills, top_k=10)
        embedding_matches = self.match_jobs_by_embeddings(resume_skills, experience_years, top_k=10)
        combined = {}

        for i, match in enumerate(skill_matches):
            jid = match['id']
            combined[jid] = match.copy()
            combined[jid]['skill_rank_score'] = (10 - i) / 10

        for i, match in enumerate(embedding_matches):
            jid = match['id']
            if jid in combined:
                combined[jid]['embedding_rank_score'] = (10 - i) / 10
                combined[jid]['embedding_similarity']  = match.get('match_percentage', 0)
            else:
                combined[jid] = match.copy()
                combined[jid]['skill_rank_score']      = 0
                combined[jid]['embedding_rank_score']  = (10 - i) / 10

        for jid in combined:
            sk  = combined[jid].get('skill_rank_score', 0)
            em  = combined[jid].get('embedding_rank_score', 0)
            combined[jid]['final_score'] = (sk * 0.6 + em * 0.4) * 100

        results = sorted(combined.values(), key=lambda x: x['final_score'], reverse=True)
        return results[:top_k]

    def get_job_recommendations(self, skills_data: dict,
                                 top_k: int = 5,
                                 location: str = "India") -> dict:
        """
        Get job recommendations with job portal links.
        """
        resume_skills    = skills_data.get('skills', [])
        experience_years = skills_data.get('experience_years', 0)

        if not resume_skills:
            return {'top_matches': [], 'message': 'No skills found in resume'}

        matches = self.get_hybrid_matches(resume_skills, experience_years, top_k)

        # ✅ Add job portal links to EVERY match
        for match in matches:
            job_title = match.get('title', '')
            matching  = match.get('matching_skills', [])
            match['job_portal_links'] = generate_job_portal_links(
                job_title, matching, location
            )

        return {
            'top_matches':      matches,
            'total_skills':     len(resume_skills),
            'experience_years': experience_years,
            'message':          f'Found {len(matches)} matching job roles'
        }