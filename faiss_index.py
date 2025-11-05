from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

class FaissIndex:
    def __init__(self):
        # This model supports 100+ languages including English and Japanese!
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.documents = []
        self.embeddings = np.empty((0, 384), dtype='float32')
        self.index = faiss.IndexFlatL2(384)

    def chunk_text(self, text, chunk_size=500, overlap=50):
        """Split text into overlapping chunks"""
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if len(chunk.strip()) > 0:
                chunks.append(chunk)
        return chunks

    def add_document(self, content, lang):
        """Add document - language agnostic (works in any language)"""
        chunks = self.chunk_text(content, chunk_size=500, overlap=50)
        
        for chunk in chunks:
            # The embedding model handles ANY language automatically
            emb = self.model.encode([chunk])
            self.documents.append({
                "content": chunk, 
                "lang": lang,  # Store original language for reference
                "chunk_lang": lang
            })
            self.embeddings = np.vstack([self.embeddings, emb])
            self.index.add(emb)

    def query(self, text, top_k=3):
        """
        Query in ANY language - retrieves relevant chunks regardless of document language
        This is the MAGIC of multilingual embeddings!
        """
        # Encode query in whatever language it is (English, Japanese, etc.)
        query_vector = self.model.encode([text])
        
        # Search finds semantically similar chunks regardless of language mismatch
        distances, indices = self.index.search(query_vector, k=top_k)
        results = []
        
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.documents) and dist < 1e10:
                results.append({
                    "content": self.documents[idx]["content"],
                    "lang": self.documents[idx]["lang"],  # Original document language
                    "score": float(dist)
                })
        return results

faiss_index = FaissIndex()
