from embeddings_manager import EmbeddingsManager

class ChapterRetriever:
    def __init__(self):
        self.embeddings_manager = EmbeddingsManager()
    
    def get_full_chapter(self, book_title: str, chapter_number: str) -> str:
        """
        Retrieves chapter content with PROPER spacing matching your Pinecone data
        """
        chapter_name = f"Chapter  {chapter_number.title()}"        
        chunks = self.embeddings_manager.index.query(
            vector=[0]*384,
            top_k=10000,
            filter={
                "book": {"$eq": book_title},
                "chapter": {"$eq": chapter_name}
            },
            include_metadata=True
        )['matches']
        
        if not chunks:
            available = self.list_available_chapters(book_title)
            raise ValueError(
                f"Chapter '{chapter_name}' not found. Available chapters:\n"
                f"{available}"
            )
        
        sorted_chunks = sorted(chunks, key=lambda x: x['metadata']['chunk_index'])
        return "\n\n".join([chunk['metadata']['text'] for chunk in sorted_chunks])

    def list_available_chapters(self, book_title: str) -> list:
        """Lists chapters in nice format (removes double space)"""
        results = self.embeddings_manager.index.query(
            vector=[0]*384,
            top_k=10000,
            filter={"book": {"$eq": book_title}},
            include_metadata=True
        )['matches']
        
        chapters = set()
        for match in results:
            chapter = match['metadata'].get('chapter', '')
            if chapter:
                chapters.add(chapter.split()[-1])
                
        number_words = ['One', 'Two', 'Three', 'Four', 'Five',
                       'Six', 'Seven', 'Eight', 'Nine', 'Ten',
                       'Eleven', 'Twelve']
        return [ch for ch in number_words if ch in chapters]
    
# retriever = ChapterRetriever()

# print("Available chapters:", retriever.list_available_chapters("chemistry9_10"))

# chapter_content = retriever.get_full_chapter("chemistry9_10", "Eight")
# print(chapter_content)  