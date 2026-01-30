from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict
import json

class EmbeddingModel:
    """Generate and compare embeddings for skills and job descriptions"""
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize the embedding model
        Args:
            model_name: HuggingFace model name (default: lightweight sentence transformer)
        """
        print(f"Loading embedding model: {model_name}...")
        try:
            self.model = SentenceTransformer(model_name)
            print("Model loaded successfully!")
        except Exception as e:
            print(f"Error loading model: {e}")
            self.model = None
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for a single text"""
        if self.model is None:
            return np.array([])
        
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return np.array([])
    
    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for multiple texts"""
        if self.model is None:
            return np.array([])
        
        try:
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            return embeddings
        except Exception as e:
            print(f"Error generating embeddings: {e}")
            return np.array([])
    
    def calculate_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Calculate cosine similarity between two embeddings"""
        if len(embedding1) == 0 or len(embedding2) == 0:
            return 0.0
        
        # Reshape for sklearn
        emb1 = embedding1.reshape(1, -1)
        emb2 = embedding2.reshape(1, -1)
        
        similarity = cosine_similarity(emb1, emb2)[0][0]
        return float(similarity)
    
    def calculate_similarities(self, embedding: np.ndarray, embeddings_list: np.ndarray) -> np.ndarray:
        """Calculate similarities between one embedding and a list of embeddings"""
        if len(embedding) == 0 or len(embeddings_list) == 0:
            return np.array([])
        
        # Reshape for sklearn
        emb = embedding.reshape(1, -1)
        
        similarities = cosine_similarity(emb, embeddings_list)[0]
        return similarities
    
    def create_skill_profile_text(self, skills: List[str], experience_years: int = 0) -> str:
        """Create a text representation of skill profile for embedding"""
        skill_text = " ".join(skills)
        if experience_years > 0:
            return f"Professional with {experience_years} years of experience in {skill_text}"
        return f"Professional with skills in {skill_text}"
    
    def create_job_description_text(self, job: Dict) -> str:
        """Create a comprehensive text representation of a job for embedding"""
        required = " ".join(job.get('required_skills', []))
        nice_to_have = " ".join(job.get('nice_to_have', []))
        title = job.get('title', '')
        description = job.get('description', '')
        
        return f"{title}. {description}. Required skills: {required}. Nice to have: {nice_to_have}"
    
    def embed_job_roles(self, job_roles: List[Dict]) -> tuple:
        """
        Generate embeddings for all job roles
        Returns: (embeddings, job_roles)
        """
        job_texts = [self.create_job_description_text(job) for job in job_roles]
        embeddings = self.generate_embeddings(job_texts)
        return embeddings, job_roles
    
    def find_top_matches(self, resume_embedding: np.ndarray, job_embeddings: np.ndarray, 
                        job_roles: List[Dict], top_k: int = 5) -> List[Dict]:
        """
        Find top K matching jobs based on embeddings
        Returns: List of jobs with similarity scores
        """
        similarities = self.calculate_similarities(resume_embedding, job_embeddings)
        
        # Get top K indices
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            job = job_roles[idx].copy()
            job['similarity_score'] = float(similarities[idx])
            job['match_percentage'] = float(similarities[idx] * 100)
            results.append(job)
        
        return results