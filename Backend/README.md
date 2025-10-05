# LegalAI Backend

The backend service for LegalAI - a FastAPI-based REST API that powers the legal information retrieval system with AI integration, document search, and personalized recommendations.

## Features

- **AI-Powered Responses**: Integration with Google Gemini AI for intelligent legal query processing
- **Document Retrieval**: FAISS-based vector search for relevant legal documents
- **Intent Detection**: Smart query analysis and routing
- **Personalized Recommendations**: User-specific legal content suggestions
- **CORS Support**: Configured for cross-origin requests from the frontend
- **Async Processing**: High-performance async request handling

## Architecture

The backend follows a modular architecture with:

```
Backend/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── routers/               # API route handlers
│   ├── get_ai_response.py    # AI chat endpoints
│   ├── handle_search.py      # Document search endpoints
│   ├── get_recommendations.py # Recommendation endpoints
│   ├── auth.py              # Authentication endpoints
│   ├── chat_history.py      # Chat history management
│   └── generate_summary.py  # Document summary generation
├── services/              # Business logic layer
│   ├── llm_handler.py        # AI model integration
│   ├── query_processor.py    # Query processing and retrieval
│   ├── get_relevant_docs.py  # Document retrieval logic
│   ├── get_doc_chunks.py     # Document chunking utilities
│   └── translator.py         # Language translation services
├── database/              # Database layer
│   ├── connection.py         # Database connection management
│   ├── models.py            # Database models and schemas
│   ├── queries.sql          # SQL query templates
│   └── schema.sql           # Database schema definitions
├── schemas/               # Pydantic data models
│   └── auth.py             # Authentication schemas
├── utils/                 # Utility functions
│   └── auth.py            # Authentication utilities
└── docs/                  # API documentation
    └── bills.tsv          # Legal document metadata
```

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Google Gemini API key

### Installation

1. **Navigate to Backend directory**

   ```bash
   cd Backend
   ```

2. **Create a virtual environment (recommended)**

   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**

   Create a `.env` file in the `Backend` directory with the following content:

   ```env
   GEMINI_API_KEY=your_google_gemini_api_key # https://aistudio.google.com/apikey
   GROQ_API_KEY=your_groq_api_key # https://console.groq.com/keys
   ```

5. **Run the server**
   ```bash
   python main.py
   ```

The API will be available at `http://localhost:8000`

### API Documentation

Once running, visit:

- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## API Endpoints

### Chat Endpoints (`/chat`)

#### POST `/chat/get_ai_response`

Get AI-powered responses to legal queries.

**Request Body:**

```json
{
  "query": "What are the requirements for filing a patent?",
  "history": []
}
```

**Response:**

```json
{
  "response": "To file a patent, you need to meet the following requirements..."
}
```

### Document Search (`/get_docs`)

#### POST `/get_docs/search`

Search for relevant legal documents.

**Request Body:**

```json
{
  "query": "municipal council amendments"
}
```

**Response:**

```json
{
  "documents": ["document1.pdf", "document2.pdf"],
  "scores": [0.95, 0.87]
}
```

### Recommendations (`/recommendations`)

#### POST `/recommendations`

Get personalized legal content recommendations.

**Request Body:**

```json
{
  "username": "user_1"
}
```

**Response:**

```json
{
  "recommendations": [
    {
      "title": "Related Legal Topic",
      "description": "Brief description",
      "relevance_score": 0.92
    }
  ]
}
```

## Technology Stack

### Core Framework

- **FastAPI**: Modern, fast web framework for building APIs
- **Uvicorn**: ASGI server for running the application
- **Pydantic**: Data validation using Python type annotations

### AI & ML

- **Google Generative AI**: Gemini model integration
- **FAISS**: Vector similarity search for documents
- **Transformers**: NLP model handling

### Data Processing

- **Pandas**: Data manipulation and analysis
- **Beautiful Soup**: HTML/XML parsing
- **Requests**: HTTP library for external API calls

### Utilities

- **Python-dotenv**: Environment variable management
- **APScheduler**: Task scheduling
- **Authlib**: Authentication utilities

## Configuration

### Environment Variables

Create a `.env` file in the Backend directory:

```env
# Required
GEMINI_API_KEY=your_google_gemini_api_key # https://aistudio.google.com/apikey
GROQ_API_KEY=your_groq_api_key # https://console.groq.com/keys

# Optional
HOST=0.0.0.0
PORT=8000
RELOAD=True
```

### CORS Configuration

The application is configured to accept requests from any origin for development. For production, update the CORS settings in `main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Update for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## ‍Development

### Running in Development Mode

```bash
python main.py
```

The server will start with auto-reload enabled, automatically restarting when code changes are detected.

### Running with Custom Configuration

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Testing the API

You can test the API using:

1. **Interactive Docs**: Visit http://localhost:8000/docs
2. **curl**:
   ```bash
   curl -X POST "http://localhost:8000/chat/get_ai_response" \
        -H "Content-Type: application/json" \
        -d '{"query": "What is copyright law?", "history": []}'
   ```
3. **Python requests**:

   ```python
   import requests

   response = requests.post(
       "http://localhost:8000/chat/get_ai_response",
       json={"query": "What is copyright law?", "history": []}
   )
   print(response.json())
   ```

## Dependencies

Key dependencies include:

- **fastapi**: Web framework
- **uvicorn**: ASGI server
- **google-generativeai**: Google AI integration
- **faiss-cpu**: Vector similarity search
- **pandas**: Data processing
- **python-dotenv**: Environment management
- **pydantic**: Data validation
- **beautifulsoup4**: HTML parsing
- **requests**: HTTP client

For a complete list, see `requirements.txt`.

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed and virtual environment is activated
2. **API Key Issues**: Verify your Google Gemini API key is set correctly in `.env`
3. **Port Conflicts**: Change the port in `main.py` if 8000 is already in use
4. **CORS Errors**: Check CORS configuration for your frontend URL

### Logs

The application logs important information to the console. For debugging, check:

- Request/response details
- AI model responses
- Error messages and stack traces

## Contributing

1. Follow PEP 8 style guidelines
2. Add type hints to new functions
3. Update documentation for API changes
4. Test endpoints before submitting PRs

## License

This backend service is part of the LegalAI project and follows the same MIT License.
