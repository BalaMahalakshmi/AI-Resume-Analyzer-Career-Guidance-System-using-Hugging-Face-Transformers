# 📄 AI Resume Analyzer

An intelligent resume analysis tool powered by HuggingFace models that extracts skills, matches you with relevant job roles, and provides personalized career advice.

## 🌟 Features

- **Resume Parsing**: Extract text and information from PDF resumes
- **Skill Extraction**: Automatically identify technical and soft skills using NER and pattern matching
- **Job Matching**: Match your skills with relevant job roles using semantic embeddings
- **Career Advice**: Get personalized learning paths and skill improvement suggestions
- **Interactive Q&A**: Chat with an AI assistant about your resume and career

## 🏗️ Project Structure

```
resume-ai/
├── app.py                      # Main application entry point
├── backend/
│   ├── parser.py              # PDF parsing and text extraction
│   ├── skills.py              # Skill extraction using NER
│   ├── matcher.py             # Job matching algorithms
│   ├── advisor.py             # Career advice generation
│   └── chatbot.py             # Interactive Q&A chatbot
├── data/
│   └── job_roles.json         # Job roles database
├── models/
│   └── embeddings.py          # Sentence embeddings for semantic matching
├── ui/
│   └── streamlit_ui.py        # Streamlit web interface
└── requirements.txt           # Python dependencies
```

## 🚀 Installation

### 1. Clone the repository or download the files

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the application

```bash
python app.py
```

Or directly with Streamlit:

```bash
streamlit run ui/streamlit_ui.py
```

## 📖 Usage

### 1. Upload Resume
- Navigate to the "📤 Upload Resume" page
- Upload your resume in PDF format
- The system will automatically:
  - Extract text from your resume
  - Identify your skills
  - Find matching job roles

### 2. View Job Matches
- Go to "🎯 Job Matches" page
- See your top matching job roles
- View match scores and skill comparisons
- Expand each job to see:
  - Matching skills you already have
  - Skills you need to learn

### 3. Get Career Advice
- Visit "💡 Career Advice" page
- Get personalized learning paths
- See skill gap analysis
- View 30-60-90 day action plans
- Receive tailored recommendations

### 4. Ask Questions
- Use "💬 Ask Questions" page
- Chat with the AI assistant
- Ask about:
  - Your skills and experience
  - Job recommendations
  - How to improve specific skills
  - Missing skills for target roles

## 🤖 How It Works

### Resume Parsing
Uses `PyPDF2` and `pdfplumber` to extract text from PDF files, then applies regex patterns to identify key information like name, email, phone, and sections.

### Skill Extraction
Combines:
- Pattern matching against a comprehensive skill database
- Section-based extraction for better accuracy
- Skill categorization (Programming, Web, Cloud, Data Science, etc.)

### Job Matching
Uses hybrid approach:
1. **Skill-based matching**: Direct comparison of resume skills vs. job requirements
2. **Semantic matching**: Uses Sentence Transformers (`all-MiniLM-L6-v2`) to understand context
3. **Weighted scoring**: Combines both methods for accurate recommendations

### Career Advice
Analyzes:
- Skill gaps between your profile and target jobs
- Learning resources and timelines
- Prioritized action plans
- General career guidance based on experience level

### Interactive Chatbot
Template-based conversational AI that:
- Maintains context of your resume and job matches
- Answers questions about skills and career development
- Provides specific advice for skill improvement

## 🛠️ Technologies Used

- **Streamlit**: Web interface
- **HuggingFace Transformers**: NLP models
- **Sentence Transformers**: Semantic embeddings
- **PyPDF2 & pdfplumber**: PDF parsing
- **Scikit-learn**: Similarity calculations
- **Python 3.8+**: Core language

## 📝 Customization

### Adding More Job Roles
Edit `data/job_roles.json` to add new job roles:

```json
{
  "id": 11,
  "title": "Your Job Title",
  "category": "Category",
  "required_skills": ["Skill1", "Skill2"],
  "nice_to_have": ["Skill3", "Skill4"],
  "description": "Job description"
}
```

### Adding More Skills
Edit the `known_skills` set in `backend/skills.py` to add more recognizable skills.

### Changing the Embedding Model
In `models/embeddings.py`, change the model name:

```python
self.model = SentenceTransformer('your-preferred-model')
```

## 🎯 Example Queries for Chatbot

- "What skills do I have?"
- "Show me job recommendations"
- "How can I improve my Python skills?"
- "What am I missing for Data Scientist role?"
- "Show my resume summary"
- "How many years of experience do I have?"

## ⚠️ Limitations

- Only supports PDF format resumes
- Skills extraction depends on clear formatting
- Job database is limited (10 sample jobs included)
- NER model is lightweight (prioritizes speed over accuracy)
- Chatbot uses template-based responses (not generative AI)

## 🔮 Future Enhancements

- [ ] Support for DOCX format
- [ ] Integration with job boards (Indeed, LinkedIn)
- [ ] More sophisticated NER models
- [ ] Generative AI for chatbot (using LLMs)
- [ ] Resume improvement suggestions
- [ ] Cover letter generation
- [ ] Interview preparation tips
- [ ] Salary estimation

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Contact

For questions or feedback, please reach out or create an issue.

---

Built with using HuggingFace and Streamlit