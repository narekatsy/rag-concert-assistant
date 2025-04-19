import re
import os
from core.document_processor import DocumentProcessor
from core.rag_system import RAGSystem

class ConcertTourManager:
    def __init__(self):
        self.rag = RAGSystem()
        self.processor = DocumentProcessor()
        self.document_count = 0

    def handle_input(self, user_input):
        if not user_input.strip():
            return "Please enter a valid command or question."
            
        if user_input.lower().startswith("add file:"):
            return self.handle_file_ingestion(user_input)
        elif user_input.lower() in ['hi', 'hello', 'hey']:
            return self.handle_greeting()
        else:
            return self.handle_question(user_input)

    def handle_file_ingestion(self, text):
        """Process a concert tour document file with full validation"""
        try:
            filepath = text[len("add file:"):].strip()
            
            # Validate file
            if not os.path.exists(filepath):
                return "Error: File not found. Please check the path."
            if not filepath.lower().endswith('.txt'):
                return "Error: Only .txt files are supported."
            if os.path.getsize(filepath) > 1_000_000:  # 1MB limit
                return "Error: File too large (max 1MB)."
                
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                
            if len(content) < 50:
                return "Error: Document too short (min 50 characters)."
                
            if not self.processor.is_concert_related(content):
                return "Sorry, I cannot ingest documents with other themes. Please provide concert tour information."
                
            # Process document
            summary = self.processor.process_document(content)
            if summary.startswith("Could not"):
                summary = "Generated summary unavailable (document stored)"
                
            # Store in RAG system
            self.rag.add_document(content, summary)
            self.document_count += 1
            
            return (
                "Thank you for sharing! Your document has been successfully added to the database.\n"
                f"Stored documents: {self.document_count}\n"
                f"Document summary: {summary if len(summary.split()) > 5 else 'Summary too short'}"
            )
            
        except Exception as e:
            return f"Error processing document: {str(e)}"

    def clean_text(self, text):
        """Clean input text"""
        text = text.encode('ascii', 'ignore').decode('ascii')
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def handle_greeting(self):
        if self.document_count == 0:
            return ("👋 Hello! I'm your concert tour assistant.\n"
                   "Please add documents using: 'add file: <path>.txt'")
        else:
            return (f"👋 Hi! I have {self.document_count} tour documents loaded.\n"
                   "Ask me about venues, dates, or artists!")

    def handle_question(self, question):
        """Answer concert tour questions with strict grounding"""
        try:
            # Validate question
            if self.document_count == 0:
                return "Please add tour documents first using 'add file: <path>.txt'"
            if len(question.strip()) < 4:
                return "Please ask a more specific question."
                
            concert_terms = {'concert', 'tour', 'venue', 'artist', 'band', 'date', 'when', 'where', 'perform'}
            if not any(term in question.lower() for term in concert_terms):
                return "I can only answer questions about concert tours."
                
            # Retrieve relevant context
            contexts = self.rag.query(question)
            if not contexts or "error" in contexts[0].lower():
                return "No relevant tour information found in documents."
                
            # Generate and validate answer
            answer = self.processor.generate_answer(question, "\n".join(contexts))
            
            if not answer or "no information" in answer.lower():
                return "The documents don't contain specific information about this."
                
            return (
                "Here's the information from tour documents:\n"
                f"{answer}\n"
                "(Answer is strictly based on ingested documents)"
            )
            
        except Exception as e:
            return f"Error answering your question: {str(e)}"

def main():
    print("""\n
    🎵 Concert Tour Assistant
    ----------------------------------------------
    Commands:
    - add file: <path>.txt   Add a tour document
    - <question>             Ask about tours
    - exit                   Quit
    """)
    
    manager = ConcertTourManager()
    
    while True:
        try:
            user_input = input("\n> ").strip()
            
            if user_input.lower() == 'exit':
                print("Goodbye! 🎸")
                break
                
            response = manager.handle_input(user_input)
            print(f"\n{response}")
            
        except KeyboardInterrupt:
            print("\nGoodbye! 🎸")
            break
        except Exception as e:
            print(f"⚠ Error: {str(e)}")

if __name__ == "__main__":
    main()