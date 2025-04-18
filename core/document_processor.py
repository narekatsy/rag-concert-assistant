from transformers import pipeline
import re

class DocumentProcessor:
    def __init__(self):
        self.summarizer = pipeline(
            "summarization",
            model="facebook/bart-large-mnli",
            tokenizer="facebook/bart-large-mnli",
            min_length=20,
            max_length=400
        )
        
        self.qa_model = pipeline(
            "text2text-generation",
            model="google/flan-t5-base",
            tokenizer="google/flan-t5-base"
        )

    def process_document(self, text):
        """Generate summary with robust error handling"""
        try:
            # Clean and validate input
            text = self._clean_text(text)
            if len(text.split()) < 15:
                return "Document too short for summary"
            
            # Generate summary with dynamic length
            input_length = len(text.split())
            max_len = min(500, max(20, int(input_length * 0.3)))
            
            summary = self.summarizer(
                text,
                max_length=max_len,
                min_length=max(15, int(max_len * 0.5)),
                do_sample=False,
                truncation=True
            )[0]['summary_text']
            
            return summary if self._is_valid_summary(summary, text) else text[:200] + "..."
            
        except Exception as e:
            print(f"Summary error: {str(e)}")
            return text[:200] + "..."

    def generate_answer(self, question, context):
        try:
            prompt = f"""Answer ONLY using the context below. Be specific with dates and locations.
            If information is missing, say "No information found".
            
            Context: {context}
            
            Question: {question}
            Answer:"""
            
            response = self.qa_model(
                prompt,
                max_length=400,
                do_sample=True,
                temperature=0.3,
                num_beams=6
            )[0]['generated_text']
            
            # Post-process to remove hallucinations
            if "information found" not in response and not any(char.isdigit() for char in response):
                return "No specific tour details available in the documents"
                
            return response.split("Answer:")[-1].strip()
        except Exception:
            return "Could not generate answer"

    def _clean_text(self, text):
        """Basic text cleaning"""
        text = re.sub(r'\s+', ' ', text).strip()
        text = re.sub(r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})', r'\3-\1-\2', text)
        return text.encode('ascii', 'ignore').decode('ascii')

    def _is_valid_summary(self, summary, original_text):
        """Validate summary quality"""
        if len(summary.split()) < 10:
            return False
        if summary.lower() == original_text.lower()[:len(summary)]:
            return False
        if len(re.findall(r'[^\w\s.,!?-]', summary)) > 5:
            return False
        return True

    CONCERT_KEYWORDS = {
        'concert', 'tour', 'venue', 'artist', 'band', 
        'schedule', 'date', 'ticket', 'arena', 'performance'
    }

    def is_concert_related(self, text):
        text_lower = text.lower()
        found_keywords = sum(1 for kw in self.CONCERT_KEYWORDS if kw in text_lower)
        return found_keywords >= 1