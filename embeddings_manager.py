# embeddings_manager.py
import pinecone
from sentence_transformers import SentenceTransformer
from typing import Dict, List
from config import Config
import time

class EmbeddingsManager:
    def __init__(self):
        self.model = SentenceTransformer(Config.EMBEDDING_MODEL)
        self.pinecone = pinecone.Pinecone(api_key=Config.PINECONE_API_KEY)
        self.index = self._initialize_index()

    def _initialize_index(self):
        """Initialize or connect to Pinecone index"""
        if Config.PINECONE_INDEX_NAME not in self.pinecone.list_indexes().names():
            self.pinecone.create_index(
                name=Config.PINECONE_INDEX_NAME,
                dimension=384, 
                metric='cosine'
            )
            time.sleep(60)
            
        return self.pinecone.Index(Config.PINECONE_INDEX_NAME)

    def check_chunk_exists(self, book_title: str, chapter_name: str, chunk_hash: str) -> bool:
        """Check if a chunk already exists in the index using a content hash"""
        results = self.index.query(
            vector=[0]*384,  
            top_k=1,
            filter={
                "book": {"$eq": book_title},
                "chapter": {"$eq": chapter_name},
                "chunk_hash": {"$eq": chunk_hash}
            },
            include_metadata=True
        )
        return len(results['matches']) > 0

    def create_embeddings(self, chapters: Dict[str, List[str]], book_title: str):
        """
        Create embeddings for chunks, checking for duplicates
        """
        vectors = []
        existing_count = 0
        new_count = 0
        
        for chapter_name, chunks in chapters.items():
            for i, chunk in enumerate(chunks):
                chunk_hash = str(hash(chunk))  
                
                if self.check_chunk_exists(book_title, chapter_name, chunk_hash):
                    existing_count += 1
                    continue
                    
                embedding = self.model.encode(chunk)
                chunk_id = f"{book_title}-{chapter_name}-{i}-{chunk_hash[:8]}"
                
                vectors.append({
                    "id": chunk_id,
                    "values": embedding.tolist(),
                    "metadata": {
                        "book": book_title,
                        "chapter": chapter_name,
                        "text": chunk,
                        "chunk_hash": chunk_hash,
                        "chunk_index": i
                    }
                })
                new_count += 1
                
                if len(vectors) >= 100:
                    self.index.upsert(vectors=vectors)
                    vectors = []
        
        if vectors:
            self.index.upsert(vectors=vectors)
            
        print(f"Processed {existing_count} existing chunks, added {new_count} new chunks")

    def list_available_chapters(self, book_title: str = None) -> List[str]:
        """List all chapters available in Pinecone"""
        chapters = set()
        results = self.index.query(
            vector=[0]*384,
            top_k=10000,
            filter={"book": {"$eq": book_title}} if book_title else {},
            include_metadata=True
        )
        
        for match in results['matches']:
            chapters.add(match['metadata']['chapter'])
        
        return sorted(chapters)