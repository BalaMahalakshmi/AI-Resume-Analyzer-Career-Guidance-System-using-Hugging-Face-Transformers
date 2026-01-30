import PyPDF2
import pdfplumber
import re
from typing import Dict, List

class ResumeParser:
    """Parse resume PDFs and extract text content"""
    
    def __init__(self):
        self.text = ""
        
    def extract_text_from_pdf(self, pdf_file) -> str:
        """Extract text from PDF using pdfplumber (more reliable)"""
        try:
            with pdfplumber.open(pdf_file) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() or ""
                self.text = text
                return text
        except Exception as e:
            print(f"Error with pdfplumber: {e}")
            # Fallback to PyPDF2
            return self._extract_with_pypdf2(pdf_file)
    
    def _extract_with_pypdf2(self, pdf_file) -> str:
        """Fallback method using PyPDF2"""
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() or ""
            self.text = text
            return text
        except Exception as e:
            print(f"Error with PyPDF2: {e}")
            return ""
    
    def extract_email(self, text: str = None) -> str:
        """Extract email address from resume"""
        if text is None:
            text = self.text
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        return emails[0] if emails else "Not found"
    
    def extract_phone(self, text: str = None) -> str:
        """Extract phone number from resume"""
        if text is None:
            text = self.text
        # Match various phone formats
        phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phones = re.findall(phone_pattern, text)
        return phones[0] if phones else "Not found"
    
    def extract_name(self, text: str = None) -> str:
        """Extract name from resume (first line heuristic)"""
        if text is None:
            text = self.text
        lines = text.strip().split('\n')
        # Usually name is in the first few lines
        for line in lines[:5]:
            line = line.strip()
            # Simple heuristic: name is typically 2-4 words, capitalized
            if len(line.split()) >= 2 and len(line.split()) <= 4:
                if line[0].isupper():
                    return line
        return "Not found"
    
    def extract_sections(self, text: str = None) -> Dict[str, str]:
        """Extract different sections from resume"""
        if text is None:
            text = self.text
            
        sections = {
            'experience': '',
            'education': '',
            'skills': '',
            'projects': '',
            'summary': ''
        }
        
        # Common section headers
        patterns = {
            'experience': r'(experience|work history|employment|professional experience)',
            'education': r'(education|academic|qualification)',
            'skills': r'(skills|technical skills|competencies|expertise)',
            'projects': r'(projects|portfolio)',
            'summary': r'(summary|objective|profile|about)'
        }
        
        text_lower = text.lower()
        
        for section, pattern in patterns.items():
            match = re.search(pattern, text_lower)
            if match:
                start = match.start()
                # Find next section or end
                next_section = len(text)
                for other_pattern in patterns.values():
                    other_match = re.search(other_pattern, text_lower[start + 50:])
                    if other_match:
                        next_section = min(next_section, start + 50 + other_match.start())
                
                sections[section] = text[start:next_section].strip()
        
        return sections
    
    def get_resume_data(self, pdf_file) -> Dict:
        """Extract all relevant data from resume"""
        text = self.extract_text_from_pdf(pdf_file)
        
        return {
            'text': text,
            'name': self.extract_name(text),
            'email': self.extract_email(text),
            'phone': self.extract_phone(text),
            'sections': self.extract_sections(text)
        }