import re
from typing import List, Set, Dict


class SkillExtractor:
    """Extract and categorize skills from resume text"""

    def __init__(self):
        # ── Master skills database ──────────────────────────────────────────
        self.known_skills = {
            # Programming Languages
            'python', 'java', 'javascript', 'c', 'c++', 'c#', 'ruby', 'go',
            'rust', 'php', 'swift', 'kotlin', 'typescript', 'r', 'scala',
            'perl', 'matlab', 'dart', 'lua', 'groovy', 'haskell', 'elixir',

            # Web Frontend
            'html', 'css', 'react', 'angular', 'vue.js', 'vue', 'jquery',
            'bootstrap', 'tailwind', 'sass', 'less', 'webpack', 'babel',
            'redux', 'next.js', 'nuxt.js', 'gatsby', 'svelte', 'typescript',

            # Web Backend
            'node.js', 'express', 'django', 'flask', 'fastapi', 'spring',
            'spring boot', 'asp.net', 'laravel', 'rails', 'graphql',
            'rest api', 'restful api', 'microservices', 'websocket',

            # Databases
            'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'cassandra',
            'oracle', 'sqlite', 'dynamodb', 'elasticsearch', 'neo4j',
            'mariadb', 'couchdb', 'firebase', 'supabase',

            # Cloud & DevOps
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins',
            'gitlab', 'terraform', 'ansible', 'chef', 'puppet', 'ci/cd',
            'linux', 'bash', 'shell scripting', 'nginx', 'apache',
            'heroku', 'vercel', 'netlify', 'github actions',

            # Data Science & ML
            'machine learning', 'deep learning', 'nlp', 'computer vision',
            'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'pandas',
            'numpy', 'matplotlib', 'seaborn', 'jupyter', 'spark', 'hadoop',
            'tableau', 'power bi', 'data visualization', 'statistics',
            'data analysis', 'big data', 'etl', 'data mining',
            'reinforcement learning', 'neural networks', 'bert', 'gpt',
            'hugging face', 'transformers', 'opencv', 'nltk', 'spacy',

            # Mobile
            'android', 'ios', 'react native', 'flutter', 'swift',
            'kotlin', 'xamarin', 'ionic', 'cordova',

            # Tools & Soft Skills
            'git', 'github', 'jira', 'agile', 'scrum', 'kanban',
            'excel', 'word', 'powerpoint', 'ms office',
            'oop', 'functional programming', 'testing', 'unit testing',
            'tdd', 'debugging', 'problem solving', 'communication',
            'teamwork', 'leadership', 'project management', 'figma',
            'postman', 'swagger', 'linux', 'vs code', 'intellij',

            # Cybersecurity
            'cybersecurity', 'network security', 'ethical hacking',
            'penetration testing', 'kali linux', 'owasp', 'siem',
            'firewalls', 'cryptography', 'soc', 'vulnerability assessment',

            # Electronics / ECE / EEE
            'plc', 'scada', 'matlab', 'simulink', 'verilog', 'vhdl',
            'fpga', 'embedded systems', 'arduino', 'raspberry pi',
            'circuit design', 'pcb design', 'autocad', 'labview',
            'microcontrollers', 'arm', 'rtos', 'can protocol', 'iot',
            'power systems', 'control systems', 'signal processing',

            # Mechanical / Civil
            'solidworks', 'catia', 'ansys', 'autocad', 'revit',
            'staad pro', 'etabs', 'sap2000', 'cad', 'cam', 'cnc',
            'finite element analysis', 'fea', 'cfd', 'six sigma', 'lean',

            # Medical / Biomedical
            'emr', 'ehr', 'clinical research', 'medical imaging',
            'biostatistics', 'healthcare analytics', 'dicom', 'hl7',
        }

        # ── Category mapping ────────────────────────────────────────────────
        self.categories = {
            'Programming Languages': {
                'python', 'java', 'javascript', 'c', 'c++', 'c#', 'ruby',
                'go', 'rust', 'php', 'swift', 'kotlin', 'typescript', 'r',
                'scala', 'perl', 'matlab', 'dart', 'lua', 'groovy'
            },
            'Web Technologies': {
                'html', 'css', 'react', 'angular', 'vue.js', 'vue',
                'jquery', 'bootstrap', 'tailwind', 'sass', 'less',
                'webpack', 'babel', 'redux', 'next.js', 'nuxt.js',
                'gatsby', 'svelte', 'node.js', 'express', 'django',
                'flask', 'fastapi', 'spring', 'spring boot', 'laravel',
                'rails', 'graphql', 'rest api', 'restful api'
            },
            'Databases': {
                'sql', 'mysql', 'postgresql', 'mongodb', 'redis',
                'cassandra', 'oracle', 'sqlite', 'dynamodb',
                'elasticsearch', 'neo4j', 'mariadb', 'firebase', 'supabase'
            },
            'Cloud & DevOps': {
                'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins',
                'gitlab', 'terraform', 'ansible', 'ci/cd', 'linux',
                'bash', 'nginx', 'github actions', 'heroku', 'vercel'
            },
            'Data Science & ML': {
                'machine learning', 'deep learning', 'nlp', 'computer vision',
                'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'pandas',
                'numpy', 'matplotlib', 'seaborn', 'jupyter', 'spark',
                'tableau', 'power bi', 'data visualization', 'statistics',
                'data analysis', 'big data', 'transformers', 'bert', 'gpt',
                'opencv', 'nltk', 'spacy', 'hugging face'
            },
            'Mobile Development': {
                'android', 'ios', 'react native', 'flutter', 'xamarin', 'ionic'
            },
            'Cybersecurity': {
                'cybersecurity', 'network security', 'ethical hacking',
                'penetration testing', 'kali linux', 'owasp', 'siem',
                'firewalls', 'cryptography', 'vulnerability assessment'
            },
            'Electronics & Embedded': {
                'plc', 'scada', 'verilog', 'vhdl', 'fpga', 'embedded systems',
                'arduino', 'raspberry pi', 'circuit design', 'pcb design',
                'microcontrollers', 'arm', 'rtos', 'can protocol', 'iot',
                'signal processing'
            },
            'Tools & Others': set(),   # Catch-all; filled at runtime
        }

    # ── Extraction Methods ───────────────────────────────────────────────────

    def extract_skills_regex(self, text: str) -> Set[str]:
        """Match known skills in resume text using word boundaries"""
        text_lower   = text.lower()
        found_skills = set()

        for skill in self.known_skills:
            # Escape special regex chars in skill name
            escaped = re.escape(skill)
            # Use word-boundary where possible
            pattern = r'(?<![a-zA-Z0-9])' + escaped + r'(?![a-zA-Z0-9])'
            if re.search(pattern, text_lower):
                found_skills.add(skill)

        return found_skills

    def extract_skills_from_section(self, skills_section: str) -> Set[str]:
        """Extract skills from the dedicated skills section"""
        if not skills_section:
            return set()

        skills       = set()
        text_lower   = skills_section.lower()

        # Split by common delimiters
        items = re.split(r'[,•·|\n;/]', skills_section)

        for item in items:
            clean = item.strip().lower()
            # Direct match
            if clean in self.known_skills:
                skills.add(clean)
            else:
                # Substring match for multi-word skills
                for known in self.known_skills:
                    if known in clean and len(known) > 2:
                        skills.add(known)

        return skills

    def extract_experience_years(self, text: str) -> int:
        """Extract years of experience from resume text"""
        text_lower = text.lower()
        patterns   = [
            r'(\d+)\+?\s*years?\s*of\s*(?:work\s*)?experience',
            r'experience\s*[:\-]?\s*(\d+)\+?\s*years?',
            r'(\d+)\+?\s*years?\s*(?:work\s*)?experience',
            r'(\d+)\+?\s*yrs?\s*of\s*experience',
        ]
        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                return int(match.group(1))
        return 0

    def categorize_skills(self, skills: Set[str]) -> Dict[str, List[str]]:
        """
        Categorize skills and return dict with non-empty categories.
        Skills are displayed with proper Title Case.
        """
        result = {cat: [] for cat in self.categories}
        uncategorized = set()

        for skill in skills:
            skill_lower = skill.lower()
            placed      = False
            for cat, cat_skills in self.categories.items():
                if cat == 'Tools & Others':
                    continue
                if skill_lower in cat_skills:
                    # Use readable display name
                    display = self._display_name(skill_lower)
                    result[cat].append(display)
                    placed = True
                    break
            if not placed:
                uncategorized.add(skill_lower)

        # Sort each category alphabetically
        for cat in result:
            result[cat] = sorted(result[cat])

        # Add uncategorized to Tools & Others
        if uncategorized:
            result['Tools & Others'] = sorted(
                [self._display_name(s) for s in uncategorized]
            )

        # Remove empty categories
        return {k: v for k, v in result.items() if v}

    def _display_name(self, skill: str) -> str:
        """Convert skill to proper display name"""
        special_cases = {
            'aws':           'AWS',
            'gcp':           'GCP',
            'sql':           'SQL',
            'html':          'HTML',
            'css':           'CSS',
            'nlp':           'NLP',
            'api':           'API',
            'rest api':      'REST API',
            'restful api':   'RESTful API',
            'oop':           'OOP',
            'tdd':           'TDD',
            'ci/cd':         'CI/CD',
            'c++':           'C++',
            'c#':            'C#',
            'vue.js':        'Vue.js',
            'node.js':       'Node.js',
            'next.js':       'Next.js',
            'nuxt.js':       'Nuxt.js',
            'asp.net':       'ASP.NET',
            'ios':           'iOS',
            'plc':           'PLC',
            'scada':         'SCADA',
            'vhdl':          'VHDL',
            'fpga':          'FPGA',
            'rtos':          'RTOS',
            'iot':           'IoT',
            'siem':          'SIEM',
            'owasp':         'OWASP',
            'pcb design':    'PCB Design',
            'fea':           'FEA',
            'cfd':           'CFD',
            'emr':           'EMR',
            'ehr':           'EHR',
            'hl7':           'HL7',
            'dicom':         'DICOM',
            'ms office':     'MS Office',
            'vs code':       'VS Code',
            'power bi':      'Power BI',
            'hugging face':  'Hugging Face',
            'bert':          'BERT',
            'gpt':           'GPT',
            'opencv':        'OpenCV',
            'nltk':          'NLTK',
            'can protocol':  'CAN Protocol',
            'machine learning': 'Machine Learning',
            'deep learning':    'Deep Learning',
            'computer vision':  'Computer Vision',
            'data visualization': 'Data Visualization',
            'data analysis':    'Data Analysis',
            'big data':         'Big Data',
            'spring boot':      'Spring Boot',
            'react native':     'React Native',
            'github actions':   'GitHub Actions',
            'neural networks':  'Neural Networks',
            'signal processing':'Signal Processing',
            'embedded systems': 'Embedded Systems',
            'circuit design':   'Circuit Design',
            'control systems':  'Control Systems',
            'power systems':    'Power Systems',
            'reinforcement learning': 'Reinforcement Learning',
        }
        return special_cases.get(skill.lower(), skill.title())

    # ── Main Entry Point ─────────────────────────────────────────────────────

    def extract_all_skills(self, resume_data: Dict) -> Dict:
        """Extract all skills from the full resume"""
        text     = resume_data.get('text', '')
        sections = resume_data.get('sections', {})

        # Extract from full text
        skills_from_text    = self.extract_skills_regex(text)

        # Extract from skills section (usually more accurate)
        skills_section_text = sections.get('skills', '')
        skills_from_section = self.extract_skills_from_section(skills_section_text)

        # Also check projects and experience for implicit skills
        for sec in ['projects', 'experience']:
            skills_from_text |= self.extract_skills_regex(sections.get(sec, ''))

        # Merge all found skills
        all_skills = skills_from_text | skills_from_section

        # Get years of experience
        experience_years = self.extract_experience_years(text)

        # Categorize
        categorized = self.categorize_skills(all_skills)

        # Build flat display list with proper names
        display_skills = sorted([
            self._display_name(s) for s in all_skills
        ])

        return {
            'skills':             display_skills,
            'skills_raw':         list(all_skills),
            'skills_count':       len(all_skills),
            'categorized_skills': categorized,
            'experience_years':   experience_years,
        }