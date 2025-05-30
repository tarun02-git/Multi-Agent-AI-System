# Author: Tarun Agarwal
# Multi-Agent AI System

from typing import Dict, Any, List, Optional
from email.parser import Parser
from email.utils import parsedate_to_datetime
import re
from datetime import datetime

from agents.base_agent import BaseAgent
from memory.shared_memory import SharedMemory

class EmailAgent(BaseAgent):
    URGENCY_KEYWORDS = {
        "high": ["urgent", "asap", "immediately", "critical", "emergency"],
        "medium": ["soon", "shortly", "prompt", "timely"],
        "low": ["when possible", "at your convenience", "no rush"]
    }
    
    def __init__(self, memory: SharedMemory):
        super().__init__(memory)
    
    async def process(self, content: Any, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process email content and extract relevant information."""
        try:
            # Parse email content
            if isinstance(content, str):
                email = Parser().parsestr(content)
            else:
                raise ValueError("Invalid email content")
            
            # Extract basic email information
            sender = self._extract_sender(email)
            subject = email.get("subject", "")
            date = self._extract_date(email)
            body = self._extract_body(email)
            
            # Analyze content
            intent = self._analyze_intent(subject, body)
            urgency = self._analyze_urgency(subject, body)
            key_entities = self._extract_entities(body)
            
            # Format for CRM
            crm_data = self._format_for_crm({
                "sender": sender,
                "subject": subject,
                "date": date,
                "body": body,
                "intent": intent,
                "urgency": urgency,
                "entities": key_entities
            })
            
            results = {
                "crm_data": crm_data,
                "analysis": {
                    "intent": intent,
                    "urgency": urgency,
                    "entities": key_entities
                }
            }
            
            # Log the processing results
            self.log_processing(content, metadata, results)
            
            return results
            
        except Exception as e:
            raise ValueError(f"Error processing email: {str(e)}")
    
    def _extract_sender(self, email: Any) -> Dict[str, str]:
        """Extract sender information from email."""
        from_header = email.get("from", "")
        match = re.match(r'"?([^"<]+)"?\s*<?([^>]*)>?', from_header)
        
        if match:
            name, email_addr = match.groups()
            return {
                "name": name.strip(),
                "email": email_addr.strip()
            }
        return {
            "name": "",
            "email": from_header.strip()
        }
    
    def _extract_date(self, email: Any) -> datetime:
        """Extract and parse email date."""
        date_str = email.get("date")
        if date_str:
            try:
                return parsedate_to_datetime(date_str)
            except:
                pass
        return datetime.now()
    
    def _extract_body(self, email: Any) -> str:
        """Extract email body content."""
        if email.is_multipart():
            # Get the first text/plain part
            for part in email.walk():
                if part.get_content_type() == "text/plain":
                    return part.get_payload(decode=True).decode()
        return email.get_payload()
    
    def _analyze_intent(self, subject: str, body: str) -> str:
        """Analyze email content to determine intent."""
        content = f"{subject} {body}".lower()
        
        intent_patterns = {
            "invoice": r"invoice|bill|payment|amount due",
            "rfq": r"rfq|request for quote|quote request|pricing",
            "complaint": r"complaint|issue|problem|concern",
            "regulation": r"regulation|compliance|policy|requirement"
        }
        
        for intent, pattern in intent_patterns.items():
            if re.search(pattern, content):
                return intent
        
        return "general"
    
    def _analyze_urgency(self, subject: str, body: str) -> str:
        """Analyze email content to determine urgency level."""
        content = f"{subject} {body}".lower()
        
        for level, keywords in self.URGENCY_KEYWORDS.items():
            if any(keyword in content for keyword in keywords):
                return level
        
        return "low"
    
    def _extract_entities(self, body: str) -> Dict[str, List[str]]:
        """Extract key entities from email body."""
        entities = {
            "dates": [],
            "amounts": [],
            "references": [],
            "contacts": []
        }
        
        # Extract dates
        date_pattern = r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{4}[-/]\d{1,2}[-/]\d{1,2}'
        entities["dates"] = re.findall(date_pattern, body)
        
        # Extract amounts
        amount_pattern = r'\$?\d+(?:,\d{3})*(?:\.\d{2})?'
        entities["amounts"] = re.findall(amount_pattern, body)
        
        # Extract reference numbers
        ref_pattern = r'(?:ref|reference|id|number)[:\s]+([A-Z0-9-]+)'
        entities["references"] = re.findall(ref_pattern, body, re.IGNORECASE)
        
        # Extract contact information
        email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        entities["contacts"].extend(re.findall(email_pattern, body))
        entities["contacts"].extend(re.findall(phone_pattern, body))
        
        return entities
    
    def _format_for_crm(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format extracted data for CRM usage."""
        return {
            "contact": {
                "name": data["sender"]["name"],
                "email": data["sender"]["email"]
            },
            "communication": {
                "subject": data["subject"],
                "date": data["date"].isoformat(),
                "body": data["body"]
            },
            "classification": {
                "intent": data["intent"],
                "urgency": data["urgency"]
            },
            "entities": data["entities"],
            "metadata": {
                "processed_at": datetime.now().isoformat(),
                "agent_id": self.agent_id
            }
        } 