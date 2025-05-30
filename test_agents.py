import pytest
from datetime import datetime
from memory.shared_memory import SharedMemory, MemoryEntry
from agents.classifier_agent import ClassifierAgent
from agents.json_agent import JSONAgent
from agents.email_agent import EmailAgent

@pytest.fixture
def memory():
    return SharedMemory("redis://localhost:6379")

@pytest.fixture
def classifier_agent(memory):
    return ClassifierAgent(memory)

@pytest.fixture
def json_agent(memory):
    return JSONAgent(memory)

@pytest.fixture
def email_agent(memory):
    return EmailAgent(memory)

@pytest.mark.asyncio
async def test_classifier_agent_json(classifier_agent):
    content = '{"type": "invoice", "data": {"amount": 100}}'
    metadata = {"source": "test"}
    
    result = await classifier_agent.process(content, metadata)
    
    assert result["format"] == "json"
    assert result["intent"] == "invoice"
    assert "confidence" in result

@pytest.mark.asyncio
async def test_classifier_agent_email(classifier_agent):
    content = """From: test@example.com
Subject: Test Email
Date: 2024-03-20

This is a test email."""
    metadata = {"source": "test"}
    
    result = await classifier_agent.process(content, metadata)
    
    assert result["format"] == "email"
    assert "confidence" in result

@pytest.mark.asyncio
async def test_json_agent_invoice(json_agent):
    content = {
        "type": "invoice",
        "data": {
            "invoice_number": "INV-001",
            "amount": 100.00,
            "date": "2024-03-20",
            "items": [],
            "customer": {}
        }
    }
    metadata = {"intent": "invoice"}
    
    result = await json_agent.process(content, metadata)
    
    assert result["valid"]
    assert "formatted_data" in result
    assert "anomalies" in result

@pytest.mark.asyncio
async def test_email_agent_rfq(email_agent):
    content = """From: test@example.com
Subject: RFQ for Office Supplies
Date: 2024-03-20

Please provide a quote for office supplies."""
    metadata = {"intent": "rfq"}
    
    result = await email_agent.process(content, metadata)
    
    assert "crm_data" in result
    assert "analysis" in result
    assert result["analysis"]["intent"] == "rfq"

def test_memory_storage(memory):
    entry = MemoryEntry(
        source="test",
        type="test",
        timestamp=datetime.now(),
        extracted_values={"test": "value"},
        thread_id="test-thread"
    )
    
    entry_id = memory.store_entry(entry)
    retrieved_entry = memory.get_entry(entry_id)
    
    assert retrieved_entry is not None
    assert retrieved_entry.source == entry.source
    assert retrieved_entry.type == entry.type
    assert retrieved_entry.thread_id == entry.thread_id 