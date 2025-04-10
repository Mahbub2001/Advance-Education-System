# ingest.py
import os
from pdf_processor import PDFProcessor
from embeddings_manager import EmbeddingsManager
from config import Config

def main():
    print("PDF Ingestion Process with Chunking")
    print("----------------------------------")
    
    pdf_processor = PDFProcessor()
    embeddings_manager = EmbeddingsManager()
    
    all_chapters = pdf_processor.process_pdf_folder()
    
    if not all_chapters:
        print(f"No PDFs found in {Config.DATA_FOLDER}")
        return
    
    for filename, chapters in all_chapters.items():
        book_title = os.path.splitext(filename)[0]
        print(f"\nProcessing book: {book_title}")
        print(f"Found {len(chapters)} chapters")
        
        total_chunks = sum(len(chunks) for chunks in chapters.values())
        print(f"Created {total_chunks} chunks from content")
        
        embeddings_manager.create_embeddings(chapters, book_title)
    
    print("\nAvailable chapters in Pinecone:")
    for book in all_chapters.keys():
        book_title = os.path.splitext(book)[0]
        chapters = embeddings_manager.list_available_chapters(book_title)
        print(f"\nBook: {book_title}")
        for chap in chapters:
            print(f"- {chap}")

if __name__ == "__main__":
    main()