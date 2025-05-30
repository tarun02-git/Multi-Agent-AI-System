from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

from memory.shared_memory import SharedMemory, MemoryEntry

class BaseAgent(ABC):
    def __init__(self, memory: SharedMemory):
        self.memory = memory
        self.agent_id = str(uuid.uuid4())
        
    @abstractmethod
    async def process(self, content: Any, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process the input content and return the results."""
        pass
    
    def create_memory_entry(
        self,
        source: str,
        type: str,
        extracted_values: Dict[str, Any],
        thread_id: str,
        conversation_id: Optional[str] = None
    ) -> str:
        """Create a new memory entry for the current processing."""
        entry = MemoryEntry(
            source=source,
            type=type,
            timestamp=datetime.now(),
            extracted_values=extracted_values,
            thread_id=thread_id,
            conversation_id=conversation_id
        )
        return self.memory.store_entry(entry)
    
    def get_thread_history(self, thread_id: str) -> list[MemoryEntry]:
        """Retrieve the processing history for a specific thread."""
        return self.memory.get_thread_history(thread_id)
    
    def update_memory_entry(self, entry_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing memory entry."""
        return self.memory.update_entry(entry_id, updates)
    
    def log_processing(self, content: Any, metadata: Dict[str, Any], results: Dict[str, Any]) -> str:
        """Log the processing results to memory."""
        thread_id = metadata.get("thread_id", str(uuid.uuid4()))
        conversation_id = metadata.get("conversation_id")
        
        extracted_values = {
            "input_metadata": metadata,
            "processing_results": results,
            "agent_id": self.agent_id
        }
        
        return self.create_memory_entry(
            source=metadata.get("source", "unknown"),
            type=metadata.get("type", "unknown"),
            extracted_values=extracted_values,
            thread_id=thread_id,
            conversation_id=conversation_id
        ) 