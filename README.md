# Multi-Agent AI System

A sophisticated multi-agent AI system built by **Tarun Agarwal** that processes and routes different types of input (PDF, JSON, Email) to specialized agents for intelligent processing and analysis.

## Features

- **Classifier Agent**: Intelligent format and intent detection
- **JSON Agent**: Structured data processing and validation
- **Email Agent**: Email content analysis and extraction
- **Shared Memory Module**: Context preservation across agents (in-memory, no Redis required)
- **Multiple Input Format Support**: PDF, JSON, Email
- **Intent Classification**: Invoice, RFQ, Complaint, Regulation, etc.

## Project Structure

```
multi-agent-ai/
├── agents/
│   ├── classifier_agent.py
│   ├── json_agent.py
│   └── email_agent.py
├── memory/
│   └── shared_memory.py
├── utils/
│   ├── file_handlers.py
│   └── validators.py
├── config/
│   └── settings.py
├── tests/
│   └── test_agents.py
├── samples/
│   ├── sample.pdf
│   ├── sample.json
│   └── sample_email.txt
├── requirements.txt
├── main.py
├── templates/
│   └── index.html
├── static/
│   └── styles.css
```

## Setup and Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/multi-agent-ai.git
cd multi-agent-ai
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the main application:
```bash
python main.py
```

The app will be available at [http://localhost:8000](http://localhost:8000)

- Main UI: [http://localhost:8000](http://localhost:8000)
- API Docs: [http://localhost:8000/api/docs](http://localhost:8000/api/docs)

## Input Formats

### JSON (as string in `content` field)
**Important:** The `/process` endpoint expects a JSON object with a `content` field containing your actual data as a string.

Example request body for `/process`:
```json
{
  "content": "{\"type\": \"invoice\", \"data\": {\"invoice_number\": \"INV-001\", \"amount\": 1000, \"date\": \"2024-03-20\"}}"
}
```

### Email (as string in `content` field)
```json
{
  "content": "From: sender@example.com\nSubject: RFQ for Office Supplies\nDate: 2024-03-20\n\nDear Supplier,\nWe are interested in purchasing office supplies..."
}
```

### PDF
- Use the `/process/file` endpoint and upload a PDF file directly.
- The system will auto-detect and process the PDF.

## Memory Module

The system uses a lightweight in-memory memory module to maintain context across agents:
- Source tracking
- Type classification
- Timestamp logging
- Extracted values storage
- Thread/conversation tracking

## Testing

Run the test suite:
```bash
pytest tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License

## Author

- Tarun Agarwal

## Acknowledgments

- OpenAI for LLM capabilities
- Python community for excellent libraries 