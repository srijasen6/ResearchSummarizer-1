import os
import logging
import re
from typing import List, Dict, Any
import hashlib
import random

# Try to import AI libraries, fall back to None if not available
try:
    from llama_cpp import Llama
except ImportError:
    Llama = None

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None

class AIService:
    """Service for AI-powered text analysis and question answering"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.llm = None
        self.embedding_model = None
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize the AI models"""
        try:
            # Initialize embedding model (CPU-friendly)
            if SentenceTransformer:
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                self.logger.info("Embedding model initialized successfully")
            else:
                self.logger.warning("sentence-transformers not available, using fallback embedding")
            
            # Initialize LLM (CPU-friendly)
            if Llama:
                model_path = self._get_model_path()
                if model_path and os.path.exists(model_path):
                    self.llm = Llama(
                        model_path=model_path,
                        n_ctx=4096,  # Context window
                        n_threads=4,  # Number of CPU threads
                        verbose=False
                    )
                    self.logger.info("LLM initialized successfully")
                else:
                    self.logger.warning("LLM model not found. Using fallback responses.")
            else:
                self.logger.warning("llama-cpp-python not available, using fallback responses")
        except Exception as e:
            self.logger.error(f"Error initializing models: {str(e)}")
            self.logger.info("Will use fallback responses")
    
    def _get_model_path(self) -> str:
        """Get the path to the LLM model file"""
        # Check common locations for the model
        possible_paths = [
            "models_cache/llama-2-7b-chat.ggmlv3.q4_0.bin",
            "models_cache/llama-2-7b-chat.q4_0.gguf",
            "models_cache/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",
            os.path.expanduser("~/.cache/huggingface/transformers/llama-2-7b-chat.ggmlv3.q4_0.bin")
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def generate_summary(self, text: str, max_words: int = 150) -> str:
        """Generate a concise summary of the document"""
        if not text:
            return "No content to summarize."
        
        # Truncate text if too long
        text_preview = text[:3000] if len(text) > 3000 else text
        
        prompt = f"""Please provide a concise summary of the following document in no more than {max_words} words. Focus on the main points, key findings, and essential information:

Document:
{text_preview}

Summary:"""
        
        if self.llm:
            try:
                response = self.llm(
                    prompt,
                    max_tokens=200,
                    temperature=0.1,
                    top_p=0.9,
                    stop=["Document:", "Summary:", "\n\n"]
                )
                summary = response['choices'][0]['text'].strip()
                return self._limit_words(summary, max_words)
            except Exception as e:
                self.logger.error(f"Error generating summary with LLM: {str(e)}")
        
        # Fallback: Extract key sentences
        return self._extractive_summary(text, max_words)
    
    def answer_question(self, question: str, relevant_chunks: List[str], full_text: str) -> Dict[str, str]:
        """Answer a question based on document content"""
        if not question:
            return {"answer": "No question provided.", "justification": "", "source_reference": ""}
        
        context = "\n\n".join(relevant_chunks) if relevant_chunks else full_text[:2000]
        
        prompt = f"""Based on the following document content, answer the question accurately and provide justification.

Document Content:
{context}

Question: {question}

Please provide:
1. A direct answer to the question
2. Justification explaining why this answer is correct
3. Reference to the specific part of the document that supports your answer

Answer:"""
        
        if self.llm:
            try:
                response = self.llm(
                    prompt,
                    max_tokens=300,
                    temperature=0.2,
                    top_p=0.9,
                    stop=["Question:", "Document Content:", "\n\n---"]
                )
                response_text = response['choices'][0]['text'].strip()
                return self._parse_answer_response(response_text, context)
            except Exception as e:
                self.logger.error(f"Error answering question with LLM: {str(e)}")
        
        # Fallback: Simple keyword matching
        return self._keyword_based_answer(question, context)
    
    def generate_challenge_questions(self, text: str) -> List[Dict[str, str]]:
        """Generate logic-based challenge questions from the document"""
        if not text:
            return []
        
        # Use first 2000 characters for question generation
        text_preview = text[:2000] if len(text) > 2000 else text
        
        prompt = f"""Based on the following document, generate exactly 3 challenging questions that test comprehension and logical reasoning. Each question should require understanding and inference from the document content.

Document:
{text_preview}

For each question, provide:
1. The question text
2. The expected answer
3. Justification explaining the correct answer
4. Reference to the document section that supports the answer

Format each question as:
Q1: [question text]
A1: [expected answer]
J1: [justification]
R1: [reference]

Questions:"""
        
        if self.llm:
            try:
                response = self.llm(
                    prompt,
                    max_tokens=500,
                    temperature=0.3,
                    top_p=0.9,
                    stop=["Document:", "Questions:", "\n\n---"]
                )
                response_text = response['choices'][0]['text'].strip()
                return self._parse_challenge_questions(response_text)
            except Exception as e:
                self.logger.error(f"Error generating challenge questions with LLM: {str(e)}")
        
        # Fallback: Generate basic questions
        return self._generate_basic_questions(text_preview)
    
    def evaluate_answer(self, question: str, user_answer: str, expected_answer: str, justification: str) -> Dict[str, Any]:
        """Evaluate user's answer to a challenge question"""
        if not user_answer:
            return {
                "score": 0,
                "feedback": "No answer provided.",
                "is_correct": False
            }
        
        prompt = f"""Evaluate the following answer to a question based on the expected answer and justification.

Question: {question}

User's Answer: {user_answer}

Expected Answer: {expected_answer}

Justification: {justification}

Please provide:
1. A score from 0-100 (where 100 is perfect)
2. Feedback explaining the evaluation
3. Whether the answer is essentially correct (true/false)

Evaluation:"""
        
        if self.llm:
            try:
                response = self.llm(
                    prompt,
                    max_tokens=200,
                    temperature=0.1,
                    top_p=0.9,
                    stop=["Question:", "Evaluation:", "\n\n---"]
                )
                response_text = response['choices'][0]['text'].strip()
                return self._parse_evaluation_response(response_text)
            except Exception as e:
                self.logger.error(f"Error evaluating answer with LLM: {str(e)}")
        
        # Fallback: Simple similarity check
        return self._simple_evaluation(user_answer, expected_answer)
    
    def _limit_words(self, text: str, max_words: int) -> str:
        """Limit text to maximum number of words"""
        words = text.split()
        if len(words) <= max_words:
            return text
        return ' '.join(words[:max_words]) + '...'
    
    def _extractive_summary(self, text: str, max_words: int) -> str:
        """Create summary by extracting key sentences"""
        sentences = re.split(r'[.!?]+', text)
        # Get first few sentences as summary
        summary_sentences = []
        word_count = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                sentence_words = len(sentence.split())
                if word_count + sentence_words <= max_words:
                    summary_sentences.append(sentence)
                    word_count += sentence_words
                else:
                    break
        
        return '. '.join(summary_sentences) + '.' if summary_sentences else "Document content available for analysis."
    
    def _parse_answer_response(self, response_text: str, context: str) -> Dict[str, str]:
        """Parse LLM response for answer, justification, and reference"""
        lines = response_text.split('\n')
        answer = ""
        justification = ""
        source_reference = ""
        
        current_section = "answer"
        for line in lines:
            line = line.strip()
            if line.lower().startswith('justification') or line.lower().startswith('2.'):
                current_section = "justification"
                line = re.sub(r'^(justification|2\.)\s*:?\s*', '', line, flags=re.IGNORECASE)
            elif line.lower().startswith('reference') or line.lower().startswith('3.'):
                current_section = "reference"
                line = re.sub(r'^(reference|3\.)\s*:?\s*', '', line, flags=re.IGNORECASE)
            
            if line:
                if current_section == "answer":
                    answer += line + " "
                elif current_section == "justification":
                    justification += line + " "
                elif current_section == "reference":
                    source_reference += line + " "
        
        return {
            "answer": answer.strip() or "Based on the document content provided.",
            "justification": justification.strip() or "This answer is derived from the document content.",
            "source_reference": source_reference.strip() or "Referenced from document content."
        }
    
    def _keyword_based_answer(self, question: str, context: str) -> Dict[str, str]:
        """Provide a fallback answer based on keyword matching"""
        # Extract keywords from question
        question_words = set(question.lower().split())
        context_lower = context.lower()
        
        # Find sentences containing question keywords
        sentences = re.split(r'[.!?]+', context)
        relevant_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and any(word in sentence.lower() for word in question_words):
                relevant_sentences.append(sentence)
        
        if relevant_sentences:
            answer = relevant_sentences[0]
            justification = "This answer is based on keyword matching within the document."
            source_reference = "Referenced from document content containing relevant keywords."
        else:
            answer = "The information needed to answer this question may not be clearly available in the document."
            justification = "Unable to find specific information addressing this question."
            source_reference = "No direct reference found in the document."
        
        return {
            "answer": answer,
            "justification": justification,
            "source_reference": source_reference
        }
    
    def _parse_challenge_questions(self, response_text: str) -> List[Dict[str, str]]:
        """Parse challenge questions from LLM response"""
        questions = []
        lines = response_text.split('\n')
        
        current_question = {}
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if line.startswith('Q'):
                if current_question:
                    questions.append(current_question)
                current_question = {"question": re.sub(r'^Q\d+:\s*', '', line)}
            elif line.startswith('A') and 'question' in current_question:
                current_question["expected_answer"] = re.sub(r'^A\d+:\s*', '', line)
            elif line.startswith('J') and 'expected_answer' in current_question:
                current_question["justification"] = re.sub(r'^J\d+:\s*', '', line)
            elif line.startswith('R') and 'justification' in current_question:
                current_question["source_reference"] = re.sub(r'^R\d+:\s*', '', line)
        
        if current_question:
            questions.append(current_question)
        
        return questions[:3]  # Return maximum 3 questions
    
    def _generate_basic_questions(self, text: str) -> List[Dict[str, str]]:
        """Generate basic fallback questions"""
        sentences = re.split(r'[.!?]+', text)
        meaningful_sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        questions = []
        question_templates = [
            "What is the main topic discussed in this document?",
            "What are the key findings or conclusions mentioned?",
            "What specific details are provided about the subject matter?"
        ]
        
        for i, template in enumerate(question_templates):
            answer = meaningful_sentences[i] if i < len(meaningful_sentences) else "Information available in document."
            questions.append({
                "question": template,
                "expected_answer": answer,
                "justification": "This answer is based on the document content analysis.",
                "source_reference": "Referenced from document content."
            })
        
        return questions
    
    def _parse_evaluation_response(self, response_text: str) -> Dict[str, Any]:
        """Parse evaluation response from LLM"""
        lines = response_text.split('\n')
        score = 0
        feedback = ""
        is_correct = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Extract score
            score_match = re.search(r'(\d+)', line)
            if score_match and ('score' in line.lower() or line.startswith('1.')):
                score = int(score_match.group(1))
            
            # Extract feedback
            if 'feedback' in line.lower() or line.startswith('2.'):
                feedback = re.sub(r'^(feedback|2\.)\s*:?\s*', '', line, flags=re.IGNORECASE)
            elif feedback and not line.startswith(('1.', '2.', '3.', 'score', 'feedback')):
                feedback += " " + line
            
            # Extract correctness
            if 'correct' in line.lower() or line.startswith('3.'):
                is_correct = 'true' in line.lower()
        
        return {
            "score": min(100, max(0, score)),
            "feedback": feedback.strip() or "Answer evaluated based on comparison with expected response.",
            "is_correct": is_correct or score >= 70
        }
    
    def _simple_evaluation(self, user_answer: str, expected_answer: str) -> Dict[str, Any]:
        """Simple fallback evaluation"""
        user_words = set(user_answer.lower().split())
        expected_words = set(expected_answer.lower().split())
        
        # Calculate simple similarity
        if not expected_words:
            return {"score": 0, "feedback": "No expected answer to compare against.", "is_correct": False}
        
        intersection = user_words.intersection(expected_words)
        similarity = len(intersection) / len(expected_words)
        score = int(similarity * 100)
        
        if score >= 70:
            feedback = "Your answer contains most of the key points from the expected answer."
            is_correct = True
        elif score >= 40:
            feedback = "Your answer has some correct elements but misses some key points."
            is_correct = False
        else:
            feedback = "Your answer differs significantly from the expected answer."
            is_correct = False
        
        return {
            "score": score,
            "feedback": feedback,
            "is_correct": is_correct
        }
