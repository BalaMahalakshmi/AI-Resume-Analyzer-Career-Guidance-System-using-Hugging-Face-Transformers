from typing import Dict, List

class CareerAdvisor:
    """Provide career advice and skill improvement suggestions"""
    
    def __init__(self):
        # Learning resources mapped to skills
        self.learning_resources = {
            'python': {
                'beginner': ['Codecademy Python', 'Python.org Tutorial', 'Automate the Boring Stuff'],
                'intermediate': ['Real Python', 'Python Tricks', 'Effective Python'],
                'advanced': ['Fluent Python', 'Python Cookbook', 'Advanced Python Programming']
            },
            'javascript': {
                'beginner': ['freeCodeCamp', 'JavaScript.info', 'Eloquent JavaScript'],
                'intermediate': ['You Don\'t Know JS', 'JavaScript: The Good Parts'],
                'advanced': ['JavaScript Patterns', 'High Performance JavaScript']
            },
            'react': {
                'beginner': ['React Official Docs', 'React for Beginners'],
                'intermediate': ['React Hooks', 'React Testing'],
                'advanced': ['React Performance', 'React Design Patterns']
            },
            'machine learning': {
                'beginner': ['Coursera ML by Andrew Ng', 'Fast.ai', 'Kaggle Learn'],
                'intermediate': ['Hands-On ML with Scikit-Learn', 'Deep Learning Specialization'],
                'advanced': ['Deep Learning by Ian Goodfellow', 'Advanced ML courses']
            },
            'docker': {
                'beginner': ['Docker Official Tutorial', 'Docker for Beginners'],
                'intermediate': ['Docker Deep Dive', 'Docker Compose'],
                'advanced': ['Docker in Production', 'Kubernetes']
            },
            'aws': {
                'beginner': ['AWS Free Tier', 'AWS Cloud Practitioner'],
                'intermediate': ['AWS Solutions Architect', 'AWS Certified Developer'],
                'advanced': ['AWS Advanced Networking', 'AWS Security']
            }
        }
        
        # Skill improvement timelines
        self.learning_timelines = {
            'beginner': '2-3 months with consistent practice',
            'intermediate': '3-6 months of hands-on projects',
            'advanced': '6-12 months of deep specialization'
        }
    
    def get_skill_level_recommendation(self, skill: str, has_skill: bool, 
                                      experience_years: int) -> Dict:
        """Recommend learning level based on current status"""
        if not has_skill:
            return {
                'skill': skill,
                'current_level': 'None',
                'recommended_level': 'beginner',
                'priority': 'high',
                'timeline': self.learning_timelines['beginner']
            }
        
        if experience_years < 2:
            return {
                'skill': skill,
                'current_level': 'beginner',
                'recommended_level': 'intermediate',
                'priority': 'medium',
                'timeline': self.learning_timelines['intermediate']
            }
        elif experience_years < 5:
            return {
                'skill': skill,
                'current_level': 'intermediate',
                'recommended_level': 'advanced',
                'priority': 'low',
                'timeline': self.learning_timelines['advanced']
            }
        else:
            return {
                'skill': skill,
                'current_level': 'advanced',
                'recommended_level': 'expert/specialized',
                'priority': 'low',
                'timeline': 'Continuous learning and specialization'
            }
    
    def get_learning_resources(self, skill: str, level: str = 'beginner') -> List[str]:
        """Get learning resources for a specific skill and level"""
        skill_lower = skill.lower()
        
        # Direct match
        if skill_lower in self.learning_resources:
            return self.learning_resources[skill_lower].get(level, [])
        
        # Partial match
        for key in self.learning_resources:
            if key in skill_lower or skill_lower in key:
                return self.learning_resources[key].get(level, [])
        
        # Generic resources
        return [
            f'Search for "{skill} tutorial" on YouTube',
            f'Check {skill} documentation',
            f'Practice on Codecademy or freeCodeCamp',
            'Build personal projects',
            'Join relevant online communities'
        ]
    
    def create_learning_path(self, missing_skills: List[str], 
                           current_skills: List[str], 
                           target_job: Dict) -> Dict:
        """Create a structured learning path for missing skills"""
        learning_path = {
            'target_role': target_job.get('title', 'Unknown'),
            'priority_skills': [],
            'nice_to_have_skills': [],
            'estimated_timeline': '',
            'learning_strategy': []
        }
        
        # Categorize missing skills by priority
        required = set(skill.lower() for skill in target_job.get('required_skills', []))
        nice_to_have = set(skill.lower() for skill in target_job.get('nice_to_have', []))
        
        priority_missing = []
        optional_missing = []
        
        for skill in missing_skills:
            if skill.lower() in required:
                priority_missing.append(skill)
            elif skill.lower() in nice_to_have:
                optional_missing.append(skill)
        
        # Create detailed plan for priority skills
        for skill in priority_missing[:5]:  # Top 5 priority
            resources = self.get_learning_resources(skill, 'beginner')
            learning_path['priority_skills'].append({
                'skill': skill,
                'priority': 'high',
                'resources': resources[:3],
                'estimated_time': '2-3 months',
                'action_items': [
                    f'Complete online course or tutorial for {skill}',
                    f'Build 2-3 projects using {skill}',
                    f'Add {skill} projects to portfolio',
                    'Practice daily for consistent improvement'
                ]
            })
        
        # Add nice-to-have skills
        for skill in optional_missing[:3]:  # Top 3 nice-to-have
            learning_path['nice_to_have_skills'].append({
                'skill': skill,
                'priority': 'medium',
                'resources': self.get_learning_resources(skill, 'beginner')[:2],
                'estimated_time': '1-2 months'
            })
        
        # Calculate total timeline
        total_months = len(priority_missing) * 2 + len(optional_missing) * 1
        learning_path['estimated_timeline'] = f'{total_months} months with focused learning'
        
        # General strategy
        learning_path['learning_strategy'] = [
            'Focus on one skill at a time to avoid overwhelm',
            'Build real projects to solidify understanding',
            'Contribute to open source projects',
            'Network with professionals in the field',
            'Document your learning journey on GitHub/LinkedIn',
            'Apply for relevant internships or junior positions',
            'Keep your resume and portfolio updated'
        ]
        
        return learning_path
    
    def analyze_skill_gaps(self, resume_skills: List[str], 
                          target_jobs: List[Dict], 
                          experience_years: int) -> Dict:
        """Comprehensive skill gap analysis across multiple jobs"""
        if not target_jobs:
            return {'error': 'No target jobs provided'}
        
        # Aggregate all required skills
        all_required = set()
        all_nice_to_have = set()
        
        for job in target_jobs:
            all_required.update(job.get('required_skills', []))
            all_nice_to_have.update(job.get('nice_to_have', []))
        
        resume_skills_lower = {skill.lower() for skill in resume_skills}
        
        # Calculate gaps
        missing_required = [skill for skill in all_required 
                          if skill.lower() not in resume_skills_lower]
        missing_nice = [skill for skill in all_nice_to_have 
                       if skill.lower() not in resume_skills_lower]
        
        # Sort by frequency across jobs
        skill_frequency = {}
        for job in target_jobs:
            for skill in job.get('required_skills', []):
                skill_frequency[skill] = skill_frequency.get(skill, 0) + 1
        
        # Sort missing skills by importance
        missing_required_sorted = sorted(missing_required, 
                                        key=lambda x: skill_frequency.get(x, 0), 
                                        reverse=True)
        
        return {
            'current_skills_count': len(resume_skills),
            'missing_required_count': len(missing_required),
            'missing_nice_to_have_count': len(missing_nice),
            'top_missing_skills': missing_required_sorted[:10],
            'skill_coverage_percentage': round(
                (len(resume_skills_lower.intersection({s.lower() for s in all_required})) / 
                 len(all_required) * 100) if all_required else 0, 2
            ),
            'recommendations': self.get_priority_recommendations(
                missing_required_sorted[:5], experience_years
            )
        }
    
    def get_priority_recommendations(self, missing_skills: List[str], 
                                    experience_years: int) -> List[Dict]:
        """Get prioritized recommendations for skill development"""
        recommendations = []
        
        for i, skill in enumerate(missing_skills[:5]):
            rec = {
                'skill': skill,
                'priority_rank': i + 1,
                'importance': 'Critical' if i < 2 else 'High',
                'learning_resources': self.get_learning_resources(skill, 'beginner'),
                'estimated_time': '2-3 months',
                'next_steps': [
                    f'Enroll in a {skill} course',
                    f'Build a project using {skill}',
                    f'Practice {skill} daily',
                    'Add to LinkedIn skills'
                ]
            }
            recommendations.append(rec)
        
        return recommendations
    
    def get_career_advice(self, skills_data: Dict, job_matches: List[Dict]) -> Dict:
        """Generate comprehensive career advice"""
        resume_skills = skills_data.get('skills', [])
        experience_years = skills_data.get('experience_years', 0)
        
        if not job_matches:
            return {
                'message': 'No job matches found',
                'advice': 'Consider broadening your skill set'
            }
        
        # Get top job match
        top_job = job_matches[0]
        
        # Create learning path
        learning_path = self.create_learning_path(
            top_job.get('missing_skills', []),
            resume_skills,
            top_job
        )
        
        # Analyze gaps across all matches
        skill_gap_analysis = self.analyze_skill_gaps(
            resume_skills, job_matches[:3], experience_years
        )
        
        return {
            'target_role': top_job.get('title'),
            'match_score': top_job.get('final_score', 0),
            'learning_path': learning_path,
            'skill_gap_analysis': skill_gap_analysis,
            'general_advice': self.get_general_advice(experience_years, skill_gap_analysis),
            'action_plan': self.create_action_plan(learning_path, experience_years)
        }
    
    def get_general_advice(self, experience_years: int, gap_analysis: Dict) -> List[str]:
        """Provide general career advice based on profile"""
        advice = []
        
        if experience_years < 2:
            advice.extend([
                'Focus on building a strong foundation in core technologies',
                'Contribute to open source projects to gain experience',
                'Build a portfolio of personal projects',
                'Network with professionals through LinkedIn and tech communities'
            ])
        elif experience_years < 5:
            advice.extend([
                'Specialize in 2-3 key technologies',
                'Take on leadership roles in projects',
                'Consider relevant certifications',
                'Mentor junior developers'
            ])
        else:
            advice.extend([
                'Consider senior or lead positions',
                'Develop system design and architecture skills',
                'Build your personal brand through blogging or speaking',
                'Explore management or technical leadership paths'
            ])
        
        coverage = gap_analysis.get('skill_coverage_percentage', 0)
        if coverage < 50:
            advice.append('Prioritize learning the most in-demand skills in your target field')
        
        return advice
    
    def create_action_plan(self, learning_path: Dict, experience_years: int) -> Dict:
        """Create a concrete 30/60/90 day action plan"""
        return {
            '30_days': [
                'Complete online course for your #1 priority skill',
                'Start building your first project using new skills',
                'Update your LinkedIn profile and resume',
                'Join relevant online communities and forums'
            ],
            '60_days': [
                'Complete 2-3 projects showcasing your skills',
                'Start applying to relevant positions',
                'Network with professionals in your target field',
                'Continue learning your priority skills'
            ],
            '90_days': [
                'Have a strong portfolio of projects',
                'Be actively interviewing for positions',
                'Have improved significantly in 2-3 key skills',
                'Continue expanding your network and learning'
            ]
        }