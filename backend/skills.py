from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification
import re
from typing import List, Set
import json

class SkillExtractor:
    """Extract skills from resume text using NER and keyword matching"""
    
    def __init__(self):
        # Common tech skills database (expandable)
        self.known_skills = {
            # Programming Languages
            'python', 'java', 'javascript', 'c++', 'c#', 'ruby', 'go', 'rust', 'php',
            'swift', 'kotlin', 'typescript', 'r', 'scala', 'perl', 'matlab',
            
            # Web Technologies
            'html', 'css', 'react', 'angular', 'vue.js', 'node.js', 'express',
            'django', 'flask', 'spring', 'asp.net', 'jquery', 'bootstrap',
            'webpack', 'babel', 'sass', 'less', 'redux', 'graphql', 'rest api',
            
            # Databases
            'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'cassandra',
            'oracle', 'sqlite', 'dynamodb', 'elasticsearch', 'neo4j',
            
            # Cloud & DevOps
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'gitlab',
            'terraform', 'ansible', 'chef', 'puppet', 'ci/cd', 'linux',
            'bash', 'shell scripting', 'nginx', 'apache',
            
            # Data Science & ML
            'machine learning', 'deep learning', 'nlp', 'computer vision',
            'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'pandas',
            'numpy', 'matplotlib', 'seaborn', 'jupyter', 'spark', 'hadoop',
            
            # Tools & Others
            'git', 'github', 'jira', 'agile', 'scrum', 'tableau', 'power bi',
            'excel', 'data visualization', 'microservices', 'restful',
            'api design', 'system design', 'algorithms', 'data structures',
            'oop', 'functional programming', 'testing', 'unit testing',
            'tdd', 'debugging', 'problem solving', 'communication',
            'teamwork', 'leadership', 'project management'
        }
        
        # Try to load NER model (lightweight option)
        try:
            print("Loading NER model...")
            # Using a lighter model for skill extraction
            self.ner_pipeline = None  # We'll use regex primarily for skills
        except Exception as e:
            print(f"Could not load NER model: {e}")
            self.ner_pipeline = None
    
    def extract_skills_regex(self, text: str) -> Set[str]:
        """Extract skills using regex pattern matching"""
        text_lower = text.lower()
        found_skills = set()
        
        for skill in self.known_skills:
            # Use word boundaries to match whole words/phrases
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.add(skill.title())
        
        return found_skills
    
    def extract_skills_from_section(self, skills_section: str) -> Set[str]:
        """Extract skills specifically from skills section"""
        if not skills_section:
            return set()
        
        skills = set()
        
        # Split by common delimiters
        delimiters = [',', '•', '·', '|', '\n', ';']
        items = [skills_section]
        
        for delimiter in delimiters:
            new_items = []
            for item in items:
                new_items.extend(item.split(delimiter))
            items = new_items
        
        # Clean and check each item
        for item in items:
            item_clean = item.strip().lower()
            # Check if it matches known skills
            if item_clean in self.known_skills:
                skills.add(item_clean.title())
            # Also check for partial matches
            for known_skill in self.known_skills:
                if known_skill in item_clean and len(known_skill) > 3:
                    skills.add(known_skill.title())
        
        return skills
    
    def extract_experience_years(self, text: str) -> int:
        """Extract years of experience from resume"""
        # Pattern for "X years of experience"
        patterns = [
            r'(\d+)\+?\s*years?\s*of\s*experience',
            r'experience\s*:?\s*(\d+)\+?\s*years?',
            r'(\d+)\+?\s*years?\s*experience'
        ]
        
        text_lower = text.lower()
        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                return int(match.group(1))
        
        return 0
    
    def categorize_skills(self, skills: Set[str]) -> dict:
        """Categorize skills into different types"""
        categories = {
            'Programming Languages': [],
            'Web Technologies': [],
            'Databases': [],
            'Cloud & DevOps': [],
            'Data Science & ML': [],
            'Tools & Others': []
        }
        
        # Define category keywords
        programming_langs = {'python', 'java', 'javascript', 'c++', 'c#', 'ruby', 'go', 'rust', 'php', 'swift', 'kotlin', 'typescript'}
        web_tech = {'html', 'css', 'react', 'angular', 'vue.js', 'node.js', 'express', 'django', 'flask', 'spring'}
        databases = {'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'cassandra', 'oracle', 'sqlite'}
        cloud_devops = {'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'terraform', 'ansible', 'ci/cd'}
        data_ml = {'machine learning', 'deep learning', 'nlp', 'tensorflow', 'pytorch', 'keras', 'pandas', 'numpy'}
        
        for skill in skills:
            skill_lower = skill.lower()
            if skill_lower in programming_langs:
                categories['Programming Languages'].append(skill)
            elif skill_lower in web_tech:
                categories['Web Technologies'].append(skill)
            elif skill_lower in databases:
                categories['Databases'].append(skill)
            elif skill_lower in cloud_devops:
                categories['Cloud & DevOps'].append(skill)
            elif skill_lower in data_ml:
                categories['Data Science & ML'].append(skill)
            else:
                categories['Tools & Others'].append(skill)
        
        # Remove empty categories
        return {k: v for k, v in categories.items() if v}
    
    def extract_all_skills(self, resume_data: dict) -> dict:
        """Extract all skills from resume"""
        text = resume_data.get('text', '')
        sections = resume_data.get('sections', {})
        
        # Extract from entire text
        skills_from_text = self.extract_skills_regex(text)
        
        # Extract from skills section specifically
        skills_section = sections.get('skills', '')
        skills_from_section = self.extract_skills_from_section(skills_section)
        
        # Combine all skills
        all_skills = skills_from_text.union(skills_from_section)
        
        # Get experience years
        experience_years = self.extract_experience_years(text)
        
        return {
            'skills': sorted(list(all_skills)),
            'skills_count': len(all_skills),
            'categorized_skills': self.categorize_skills(all_skills),
            'experience_years': experience_years
        }