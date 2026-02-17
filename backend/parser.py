import PyPDF2
import pdfplumber
import re
from typing import Dict, List


class ResumeParser:
    """Parse resume PDFs and extract text content"""

    def __init__(self):
        self.text = ""

    # ── PDF Text Extraction ──────────────────────────────────────────────────

    def extract_text_from_pdf(self, pdf_file) -> str:
        """Extract text from PDF using pdfplumber (more reliable)"""
        try:
            with pdfplumber.open(pdf_file) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                self.text = text
                return text
        except Exception as e:
            print(f"pdfplumber failed: {e}, trying PyPDF2...")
            return self._extract_with_pypdf2(pdf_file)

    def _extract_with_pypdf2(self, pdf_file) -> str:
        """Fallback method using PyPDF2"""
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += (page.extract_text() or "") + "\n"
            self.text = text
            return text
        except Exception as e:
            print(f"PyPDF2 failed: {e}")
            return ""

    # ── Field Extractors ─────────────────────────────────────────────────────

    def extract_email(self, text: str = None) -> str:
        """Extract email address from resume"""
        if text is None:
            text = self.text
        pattern = r'\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b'
        matches = re.findall(pattern, text)
        return matches[0] if matches else "Not found"

    def extract_phone(self, text: str = None) -> str:
        """
        Extract phone number from resume.
        Handles Indian (+91) and international formats, spaces/dots/dashes.
        """
        if text is None:
            text = self.text

        # ── Ordered patterns (most specific first) ──────────────────────────
        patterns = [
            # +91-XXXXX-XXXXX  or  +91 XXXXX XXXXX
            r'\+91[\s\-]?\d{5}[\s\-]?\d{5}',
            # 91-XXXXXXXXXX
            r'91[\s\-]?\d{10}',
            # 10-digit with separators: XXXXX-XXXXX or XXXXX XXXXX
            r'\b\d{5}[\s\-]\d{5}\b',
            # Plain 10-digit number
            r'\b[6-9]\d{9}\b',
            # International: +1 (123) 456-7890
            r'\+?1?[\s\-]?\(?\d{3}\)?[\s\-]\d{3}[\s\-]\d{4}',
            # Generic: any sequence of digits with common separators (10-15 digits)
            r'\b\d[\d\s\-\.\(\)]{8,}\d\b',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text)
            if matches:
                # Clean up whitespace and return first match
                phone = matches[0].strip()
                # Remove extra spaces but keep structure
                phone = re.sub(r'\s+', ' ', phone)
                return phone

        return "Not found"

    def extract_name(self, text: str = None) -> str:
        """Extract name from resume (first non-empty line heuristic)"""
        if text is None:
            text = self.text

        lines = [l.strip() for l in text.strip().split('\n') if l.strip()]

        for line in lines[:8]:
            # Skip lines that look like contact info, headers, or URLs
            if re.search(r'@|http|linkedin|github|resume|cv|\d{5,}', line, re.I):
                continue
            words = line.split()
            # Name: 2–5 words, each starting with capital letter
            if 2 <= len(words) <= 5 and all(w[0].isupper() for w in words if w.isalpha()):
                return line

        return lines[0] if lines else "Not found"

    def extract_linkedin(self, text: str = None) -> str:
        """Extract LinkedIn URL if present"""
        if text is None:
            text = self.text
        pattern = r'(https?://)?(?:www\.)?linkedin\.com/in/[\w\-]+'
        matches = re.findall(pattern, text, re.I)
        return matches[0] if matches else "Not found"

    def extract_github(self, text: str = None) -> str:
        """Extract GitHub URL if present"""
        if text is None:
            text = self.text
        pattern = r'(https?://)?(?:www\.)?github\.com/[\w\-]+'
        matches = re.findall(pattern, text, re.I)
        return matches[0] if matches else "Not found"

    def extract_sections(self, text: str = None) -> Dict[str, str]:
        """Extract different sections from resume text"""
        if text is None:
            text = self.text

        sections = {
            'experience': '',
            'education':  '',
            'skills':     '',
            'projects':   '',
            'summary':    '',
            'certifications': '',
            'achievements': '',
        }

        patterns = {
            'experience':     r'(work\s*experience|experience|employment|professional\s*experience|work\s*history)',
            'education':      r'(education|academic|qualification|degree)',
            'skills':         r'(skills|technical\s*skills|competencies|expertise|technologies)',
            'projects':       r'(projects|portfolio|personal\s*projects|academic\s*projects)',
            'summary':        r'(summary|objective|profile|about\s*me|career\s*objective)',
            'certifications': r'(certifications?|certificates?|courses?|training)',
            'achievements':   r'(achievements?|awards?|honors?|accomplishments?)',
        }

        text_lower = text.lower()

        # Find all section positions
        section_positions = {}
        for sec, pat in patterns.items():
            match = re.search(pat, text_lower)
            if match:
                section_positions[sec] = match.start()

        # Sort sections by their position in the document
        sorted_sections = sorted(section_positions.items(), key=lambda x: x[1])

        # Extract text between consecutive section headers
        for idx, (sec, start_pos) in enumerate(sorted_sections):
            if idx + 1 < len(sorted_sections):
                end_pos = sorted_sections[idx + 1][1]
            else:
                end_pos = len(text)
            sections[sec] = text[start_pos:end_pos].strip()

        return sections

    def get_resume_data(self, pdf_file) -> Dict:
        """Extract all relevant data from resume"""
        text = self.extract_text_from_pdf(pdf_file)

        return {
            'text':      text,
            'name':      self.extract_name(text),
            'email':     self.extract_email(text),
            'phone':     self.extract_phone(text),
            'linkedin':  self.extract_linkedin(text),
            'github':    self.extract_github(text),
            'sections':  self.extract_sections(text),
        }