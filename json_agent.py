# Author: Tarun Agarwal
# Multi-Agent AI System

import json
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, ValidationError

from agents.base_agent import BaseAgent
from memory.shared_memory import SharedMemory

class JSONSchema(BaseModel):
    """Base schema for JSON validation."""
    type: str
    data: Dict[str, Any]

class InvoiceSchema(JSONSchema):
    """Schema for invoice data."""
    data: Dict[str, Any] = {
        "invoice_number": str,
        "amount": float,
        "date": str,
        "items": List[Dict[str, Any]],
        "customer": Dict[str, Any]
    }

class RFQSchema(JSONSchema):
    """Schema for RFQ data."""
    data: Dict[str, Any] = {
        "rfq_number": str,
        "requested_items": List[Dict[str, Any]],
        "deadline": str,
        "contact": Dict[str, Any]
    }

class ComplaintSchema(JSONSchema):
    """Schema for complaint data."""
    data: Dict[str, Any] = {
        "complaint_id": str,
        "description": str,
        "severity": str,
        "contact": Dict[str, Any]
    }

class RegulationSchema(JSONSchema):
    """Schema for regulation data."""
    data: Dict[str, Any] = {
        "regulation_id": str,
        "title": str,
        "requirements": List[str],
        "effective_date": str
    }

class JSONAgent(BaseAgent):
    SCHEMAS = {
        "invoice": InvoiceSchema,
        "rfq": RFQSchema,
        "complaint": ComplaintSchema,
        "regulation": RegulationSchema
    }
    
    def __init__(self, memory: SharedMemory):
        super().__init__(memory)
    
    async def process(self, content: Any, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process JSON content and validate against appropriate schema."""
        try:
            # Parse JSON content
            if isinstance(content, str):
                data = json.loads(content)
            elif isinstance(content, dict):
                data = content
            else:
                raise ValueError("Invalid JSON content")
            
            # Get the intent from metadata or content
            intent = metadata.get("intent") or data.get("type", "unknown")
            
            # Validate against appropriate schema
            validation_result = self._validate_schema(data, intent)
            
            # Extract and format data
            formatted_data = self._format_data(data, intent)
            
            # Check for anomalies
            anomalies = self._check_anomalies(formatted_data, intent)
            
            results = {
                "valid": validation_result["valid"],
                "formatted_data": formatted_data,
                "anomalies": anomalies,
                "validation_errors": validation_result.get("errors", [])
            }
            
            # Log the processing results
            self.log_processing(content, metadata, results)
            
            return results
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error processing JSON: {str(e)}")
    
    def _validate_schema(self, data: Dict[str, Any], intent: str) -> Dict[str, Any]:
        """Validate data against the appropriate schema."""
        schema_class = self.SCHEMAS.get(intent)
        if not schema_class:
            return {"valid": False, "errors": [f"Unsupported intent: {intent}"]}
        
        try:
            schema_class(**data)
            return {"valid": True}
        except ValidationError as e:
            return {
                "valid": False,
                "errors": [str(error) for error in e.errors()]
            }
    
    def _format_data(self, data: Dict[str, Any], intent: str) -> Dict[str, Any]:
        """Format the data according to the intent."""
        formatted = {
            "type": intent,
            "timestamp": data.get("timestamp"),
            "source": data.get("source")
        }
        
        if intent == "invoice":
            formatted.update({
                "invoice_number": data.get("data", {}).get("invoice_number"),
                "amount": data.get("data", {}).get("amount"),
                "date": data.get("data", {}).get("date"),
                "items": data.get("data", {}).get("items", []),
                "customer": data.get("data", {}).get("customer", {})
            })
        elif intent == "rfq":
            formatted.update({
                "rfq_number": data.get("data", {}).get("rfq_number"),
                "requested_items": data.get("data", {}).get("requested_items", []),
                "deadline": data.get("data", {}).get("deadline"),
                "contact": data.get("data", {}).get("contact", {})
            })
        elif intent == "complaint":
            formatted.update({
                "complaint_id": data.get("data", {}).get("complaint_id"),
                "description": data.get("data", {}).get("description"),
                "severity": data.get("data", {}).get("severity"),
                "contact": data.get("data", {}).get("contact", {})
            })
        elif intent == "regulation":
            formatted.update({
                "regulation_id": data.get("data", {}).get("regulation_id"),
                "title": data.get("data", {}).get("title"),
                "requirements": data.get("data", {}).get("requirements", []),
                "effective_date": data.get("data", {}).get("effective_date")
            })
        
        return formatted
    
    def _check_anomalies(self, data: Dict[str, Any], intent: str) -> List[str]:
        """Check for anomalies in the formatted data."""
        anomalies = []
        
        if intent == "invoice":
            if not data.get("invoice_number"):
                anomalies.append("Missing invoice number")
            if not data.get("amount") or data.get("amount") <= 0:
                anomalies.append("Invalid or missing amount")
            if not data.get("items"):
                anomalies.append("No items in invoice")
                
        elif intent == "rfq":
            if not data.get("rfq_number"):
                anomalies.append("Missing RFQ number")
            if not data.get("requested_items"):
                anomalies.append("No requested items")
            if not data.get("deadline"):
                anomalies.append("Missing deadline")
                
        elif intent == "complaint":
            if not data.get("complaint_id"):
                anomalies.append("Missing complaint ID")
            if not data.get("description"):
                anomalies.append("Missing complaint description")
            if not data.get("severity"):
                anomalies.append("Missing severity level")
                
        elif intent == "regulation":
            if not data.get("regulation_id"):
                anomalies.append("Missing regulation ID")
            if not data.get("requirements"):
                anomalies.append("No requirements specified")
            if not data.get("effective_date"):
                anomalies.append("Missing effective date")
        
        return anomalies 