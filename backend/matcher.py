import sys
import os

# Add parent directory to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import json
from typing import List, Dict, Set
import model
from model.embeddings import EmbeddingModel

class JobMatcher:
    """Match resume skills with suitable job roles"""
    
    def __init__(self, job_roles_path: str = 'data/job_roles.json'):
        """Initialize matcher with job roles data"""
        self.job_roles = self.load_job_roles(job_roles_path)
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
        
        resume_skills_lower = {skill.lower() for skill in resume_skills}
        job_skills_lower = {skill.lower() for skill in job_skills}
        
        matching_skills = resume_skills_lower.intersection(job_skills_lower)
        match_percentage = (len(matching_skills) / len(job_skills_lower)) * 100
        
        return match_percentage
    
    def get_matching_skills(self, resume_skills: List[str], job_skills: List[str]) -> List[str]:
        """Get list of matching skills"""
        resume_skills_lower = {skill.lower(): skill for skill in resume_skills}
        job_skills_lower = {skill.lower() for skill in job_skills}
        
        matching = [resume_skills_lower[skill] for skill in resume_skills_lower 
                   if skill in job_skills_lower]
        return matching
    
    def get_missing_skills(self, resume_skills: List[str], job_skills: List[str]) -> List[str]:
        """Get list of skills required but not present in resume"""
        resume_skills_lower = {skill.lower() for skill in resume_skills}
        job_skills_lower = {skill.lower() for skill in job_skills}
        
        missing = [skill for skill in job_skills if skill.lower() not in resume_skills_lower]
        return missing
    
    def match_jobs_by_skills(self, resume_skills: List[str], top_k: int = 5) -> List[Dict]:
        """Match jobs based on skill overlap"""
        matches = []
        
        for job in self.job_roles['job_roles']:
            required_skills = job.get('required_skills', [])
            nice_to_have = job.get('nice_to_have', [])
            all_skills = required_skills + nice_to_have
            
            # Calculate matches
            required_match = self.calculate_skill_match(resume_skills, required_skills)
            overall_match = self.calculate_skill_match(resume_skills, all_skills)
            
            matching_skills = self.get_matching_skills(resume_skills, all_skills)
            missing_skills = self.get_missing_skills(resume_skills, required_skills)
            
            job_match = {
                **job,
                'required_skill_match': round(required_match, 2),
                'overall_skill_match': round(overall_match, 2),
                'matching_skills': matching_skills,
                'missing_skills': missing_skills,
                'matching_count': len(matching_skills),
                'missing_count': len(missing_skills)
            }
            matches.append(job_match)
        
        # Sort by required skill match first, then overall match
        matches.sort(key=lambda x: (x['required_skill_match'], x['overall_skill_match']), 
                    reverse=True)
        
        return matches[:top_k]
    
    def match_jobs_by_embeddings(self, resume_skills: List[str], 
                                experience_years: int = 0, top_k: int = 5) -> List[Dict]:
        """Match jobs using semantic embeddings"""
        # Create resume profile text
        resume_text = self.embedding_model.create_skill_profile_text(
            resume_skills, experience_years
        )
        
        # Generate resume embedding
        resume_embedding = self.embedding_model.generate_embedding(resume_text)
        
        # Find top matches
        matches = self.embedding_model.find_top_matches(
            resume_embedding, self.job_embeddings, self.job_roles_list, top_k
        )
        
        # Add skill analysis to each match
        for match in matches:
            required_skills = match.get('required_skills', [])
            all_skills = required_skills + match.get('nice_to_have', [])
            
            match['matching_skills'] = self.get_matching_skills(resume_skills, all_skills)
            match['missing_skills'] = self.get_missing_skills(resume_skills, required_skills)
            match['required_skill_match'] = self.calculate_skill_match(resume_skills, required_skills)
        
        return matches
    
    def get_hybrid_matches(self, resume_skills: List[str], 
                          experience_years: int = 0, top_k: int = 5) -> List[Dict]:
        """
        Hybrid matching combining skill-based and embedding-based approaches
        This gives more accurate results
        """
        # Get matches from both methods
        skill_matches = self.match_jobs_by_skills(resume_skills, top_k=10)
        embedding_matches = self.match_jobs_by_embeddings(resume_skills, experience_years, top_k=10)
        
        # Combine and score
        combined = {}
        
        # Add skill-based scores
        for i, match in enumerate(skill_matches):
            job_id = match['id']
            combined[job_id] = match.copy()
            combined[job_id]['skill_rank_score'] = (10 - i) / 10  # Higher rank = higher score
        
        # Add embedding-based scores
        for i, match in enumerate(embedding_matches):
            job_id = match['id']
            if job_id in combined:
                combined[job_id]['embedding_rank_score'] = (10 - i) / 10
                combined[job_id]['embedding_similarity'] = match.get('match_percentage', 0)
            else:
                combined[job_id] = match.copy()
                combined[job_id]['skill_rank_score'] = 0
                combined[job_id]['embedding_rank_score'] = (10 - i) / 10
        
        # Calculate final score (weighted average)
        for job_id in combined:
            skill_score = combined[job_id].get('skill_rank_score', 0)
            embedding_score = combined[job_id].get('embedding_rank_score', 0)
            combined[job_id]['final_score'] = (skill_score * 0.6 + embedding_score * 0.4) * 100
        
        # Sort by final score
        results = sorted(combined.values(), key=lambda x: x['final_score'], reverse=True)
        
        return results[:top_k]
    
    def get_job_recommendations(self, skills_data: dict, top_k: int = 5) -> dict:
        """
        Get job recommendations based on extracted skills
        Returns comprehensive matching results
        """
        resume_skills = skills_data.get('skills', [])
        experience_years = skills_data.get('experience_years', 0)
        
        if not resume_skills:
            return {
                'top_matches': [],
                'message': 'No skills found in resume'
            }
        
        # Get hybrid matches (most accurate)
        matches = self.get_hybrid_matches(resume_skills, experience_years, top_k)
        
        return {
            'top_matches': matches,
            'total_skills': len(resume_skills),
            'experience_years': experience_years,
            'message': f'Found {len(matches)} matching job roles'
        }