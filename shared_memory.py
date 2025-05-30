# Author: Tarun Agarwal
# Multi-Agent AI System

from typing import Dict, Any, Optional
from datetime import datetime
import json
from pydantic import BaseModel

class MemoryEntry(BaseModel):
    source: str
    type: str
    timestamp: datetime
    extracted_values: Dict[str, Any]
    thread_id: str
    conversation_id: Optional[str] = None

class SharedMemory:
    def __init__(self, redis_url: str = None):
        self._in_memory_store = {}

    def store_entry(self, entry: MemoryEntry) -> str:
        entry_id = f"entry:{datetime.now().timestamp()}"
        entry_dict = entry.model_dump()
        entry_dict["timestamp"] = entry_dict["timestamp"].isoformat()
        entry_dict["extracted_values"] = json.dumps(entry_dict["extracted_values"])
        self._in_memory_store[entry_id] = entry_dict
        return entry_id

    def get_entry(self, entry_id: str) -> Optional[MemoryEntry]:
        entry_data = self._in_memory_store.get(entry_id, {})
        if not entry_data:
            return None
        entry_data["timestamp"] = datetime.fromisoformat(entry_data["timestamp"])
        entry_data["extracted_values"] = json.loads(entry_data["extracted_values"])
        return MemoryEntry(**entry_data)

    def get_thread_history(self, thread_id: str) -> list[MemoryEntry]:
        entries = []
        for entry_data in self._in_memory_store.values():
            if entry_data.get("thread_id") == thread_id:
                entry_data["timestamp"] = datetime.fromisoformat(entry_data["timestamp"])
                entry_data["extracted_values"] = json.loads(entry_data["extracted_values"])
                entries.append(MemoryEntry(**entry_data))
        return sorted(entries, key=lambda x: x.timestamp)

    def update_entry(self, entry_id: str, updates: Dict[str, Any]) -> bool:
        if entry_id not in self._in_memory_store:
            return False
        self._in_memory_store[entry_id].update(updates)
        return True

    def delete_entry(self, entry_id: str) -> bool:
        return bool(self._in_memory_store.pop(entry_id, None))

    def clear_thread(self, thread_id: str) -> int:
        deleted = 0
        to_delete = [k for k, v in self._in_memory_store.items() if v.get("thread_id") == thread_id]
        for k in to_delete:
            del self._in_memory_store[k]
            deleted += 1
        return deleted 