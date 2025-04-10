# pdf_processor.py
import PyPDF2
import re
from typing import Dict, List, Tuple
import os
from config import Config

class PDFProcessor:
    @staticmethod
    def extract_chapters_from_pdf(pdf_path: str) -> Dict[str, List[str]]:
        """
        Extract chapters from PDF where chapters start with "Chapter X" or similar
        Returns a dictionary with chapter names as keys and content as lists of paragraphs
        """
        chapters = {}
        current_chapter = None
        chapter_content = []
        
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            
            for page in reader.pages:
                text = page.extract_text()
                if not text:
                    continue
                    
                lines = text.split('\n')
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                        
                    if re.match(r'^(Chapter\s+\d+|Chapter\s+[A-Za-z]+)', line):
                        if current_chapter:
                            chapters[current_chapter] = chapter_content
                            chapter_content = []
                        current_chapter = line
                    elif current_chapter:
                        chapter_content.append(line)
            
            # Add the last chapter
            if current_chapter and chapter_content:
                chapters[current_chapter] = chapter_content
        
        return chapters

    @staticmethod
    def chunk_content(content: List[str], min_chunk_size: int = 100, max_chunk_size: int = 500) -> List[str]:
        """
        Combine small paragraphs and split large ones to create consistent chunks
        """
        chunks = []
        current_chunk = []
        current_size = 0
        
        for paragraph in content:
            para_size = len(paragraph.split())
            
            if para_size > max_chunk_size:
                words = paragraph.split()
                for i in range(0, len(words), max_chunk_size):
                    chunk = ' '.join(words[i:i+max_chunk_size])
                    chunks.append(chunk)
                continue
                
            if current_size + para_size > max_chunk_size:
                if current_chunk:
                    chunks.append(' '.join(current_chunk))
                    current_chunk = []
                    current_size = 0
                    
            current_chunk.append(paragraph)
            current_size += para_size
            
            if current_size >= min_chunk_size:
                chunks.append(' '.join(current_chunk))
                current_chunk = []
                current_size = 0
                
        if current_chunk:
            chunks.append(' '.join(current_chunk))
            
        return chunks

    @staticmethod
    def process_pdf_folder(data_folder: str = None) -> Dict[str, Dict[str, List[str]]]:
        """
        Process all PDFs in a folder and return their chapter contents with chunking
        """
        if data_folder is None:
            data_folder = Config.DATA_FOLDER
            
        all_chapters = {}
        
        for filename in os.listdir(data_folder):
            if filename.endswith('.pdf'):
                pdf_path = os.path.join(data_folder, filename)
                chapters = PDFProcessor.extract_chapters_from_pdf(pdf_path)
                
                chunked_chapters = {}
                for chapter_name, content in chapters.items():
                    chunked_content = PDFProcessor.chunk_content(content)
                    chunked_chapters[chapter_name] = chunked_content
                
                all_chapters[filename] = chunked_chapters
                
        return all_chapters