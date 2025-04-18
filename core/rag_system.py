from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class RAGSystem:
    def __init__(self):
        self.embedder = SentenceTransformer('multi-qa-MiniLM-L6-cos-v1')
        self.documents = []
        self.summaries = []
        self.embeddings = None

    def add_document(self, text, summary):
        """Store document with automatic fallback handling"""
        display_summary = summary if len(summary.split()) > 10 else text[:200] + "..."
        self.documents.append(text)
        self.summaries.append(display_summary)
        
        embed_text = summary if len(summary.split()) > 10 else text[:200]
        new_embedding = self.embedder.encode([embed_text])
        
        if self.embeddings is None:
            self.embeddings = new_embedding
        else:
            self.embeddings = np.vstack([self.embeddings, new_embedding])

    def query(self, question, k=2):
        """Safe query with error handling"""
        concert_terms = {'concert', 'tour', 'venue', 'artist', 'date'}
        if not any(term in question.lower() for term in concert_terms):
            return ["Please ask about concert tours"]
        
        if not self.documents:
            return ["No documents available"]
            
        try:
            k = min(k, len(self.documents))
            q_embedding = self.embedder.encode([question])
            sim_scores = cosine_similarity(q_embedding, self.embeddings)[0]
            top_idx = np.argsort(sim_scores)[-k:][::-1]
            
            return [self._format_result(idx) for idx in top_idx]
        except Exception:
            return ["Error processing query"]

    def _format_result(self, idx):
        return "\n".join([
            f"=== Summary ===",
            self.summaries[idx],
            f"\n=== Relevant Excerpt ===",
            self.documents[idx][:1000] + ("..." if len(self.documents[idx]) > 1000 else "")
        ])