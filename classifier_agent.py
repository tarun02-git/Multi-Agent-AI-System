# Author: Tarun Agarwal
# Multi-Agent AI System

import json
from typing import Dict, Any, Tuple
from email.parser import Parser
from PyPDF2 import PdfReader
import io
import mimetypes

from agents.base_agent import BaseAgent
from memory.shared_memory import SharedMemory

class ClassifierAgent(BaseAgent):
    SUPPORTED_FORMATS = ["pdf", "json", "email"]
    SUPPORTED_INTENTS = ["invoice", "rfq", "complaint", "regulation"]
    
    def __init__(self, memory: SharedMemory):
        super().__init__(memory)
        mimetypes.init()
    
    async def process(self, content: Any, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process the input content and classify its format and intent."""
        format_type = self._detect_format(content)
        intent = self._detect_intent(content, format_type)
        
        results = {
            "format": format_type,
            "intent": intent,
            "confidence": self._calculate_confidence(format_type, intent)
        }
        
        # Log the classification results
        self.log_processing(content, metadata, results)
        
        return results
    
    def _detect_format(self, content: Any) -> str:
        """Detect the format of the input content."""
        if isinstance(content, str):
            # Check if it's JSON
            try:
                json.loads(content)
                return "json"
            except json.JSONDecodeError:
                # Check if it's email
                if self._is_email_format(content):
                    return "email"
        
        # Check if it's PDF
        if isinstance(content, (bytes, bytearray)):
            try:
                pdf_file = io.BytesIO(content)
                PdfReader(pdf_file)
                return "pdf"
            except:
                pass
        
        raise ValueError("Unsupported format")
    
    def _detect_intent(self, content: Any, format_type: str) -> str:
        """Detect the intent of the content based on its format."""
        if format_type == "json":
            return self._detect_json_intent(content)
        elif format_type == "email":
            return self._detect_email_intent(content)
        elif format_type == "pdf":
            return self._detect_pdf_intent(content)
        
        raise ValueError(f"Unsupported format: {format_type}")
    
    def _detect_json_intent(self, content: str) -> str:
        """Detect intent from JSON content."""
        try:
            data = json.loads(content)
            if "type" in data:
                return data["type"].lower()
            
            # Analyze content for intent
            content_str = json.dumps(data).lower()
            return self._analyze_content_for_intent(content_str)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON content")
    
    def _detect_email_intent(self, content: str) -> str:
        """Detect intent from email content."""
        email = Parser().parsestr(content)
        subject = email.get("subject", "").lower()
        body = email.get_payload()
        
        # Combine subject and body for analysis
        content_str = f"{subject} {body}".lower()
        return self._analyze_content_for_intent(content_str)
    
    def _detect_pdf_intent(self, content: bytes) -> str:
        """Detect intent from PDF content."""
        try:
            pdf_file = io.BytesIO(content)
            reader = PdfReader(pdf_file)
            text = ""
            
            for page in reader.pages:
                text += page.extract_text()
            
            return self._analyze_content_for_intent(text.lower())
        except Exception as e:
            raise ValueError(f"Error processing PDF: {str(e)}")
    
    def _analyze_content_for_intent(self, content: str) -> str:
        """Analyze content to determine intent based on keywords."""
        intent_keywords = {
            "invoice": ["invoice", "bill", "payment", "amount due"],
            "rfq": ["rfq", "request for quote", "quote request", "pricing"],
            "complaint": ["complaint", "issue", "problem", "concern"],
            "regulation": ["regulation", "compliance", "policy", "requirement"]
        }
        
        # Count keyword matches for each intent
        intent_scores = {
            intent: sum(1 for keyword in keywords if keyword in content)
            for intent, keywords in intent_keywords.items()
        }
        
        # Return the intent with the highest score
        if not any(intent_scores.values()):
            return "unknown"
        
        return max(intent_scores.items(), key=lambda x: x[1])[0]
    
    def _is_email_format(self, content: str) -> bool:
        """Check if the content is in email format."""
        email = Parser().parsestr(content)
        return bool(email.get("from") and email.get("subject"))
    
    def _calculate_confidence(self, format_type: str, intent: str) -> float:
        """Calculate confidence score for the classification."""
        # This is a simple implementation. In a real system, you might want to use
        # more sophisticated confidence scoring based on the analysis results.
        base_confidence = 0.8 if format_type in self.SUPPORTED_FORMATS else 0.5
        intent_confidence = 0.9 if intent in self.SUPPORTED_INTENTS else 0.6
        
        return (base_confidence + intent_confidence) / 2 