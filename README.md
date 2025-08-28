# LegalAI

An intelligent legal information retrieval system that provides user-friendly responses to legal queries, personalized recommendations, and comprehensive legal document search capabilities. Built with modern web technologies and powered by AI to make legal information more accessible.

## Features

- **AI-Powered Legal Assistant**: Get intelligent responses to legal questions using advanced language models
- **Document Search & Retrieval**: Search through legal documents, bills, and acts with semantic understanding
- **Personalized Recommendations**: Receive tailored legal content based on your query history
- **Interactive Chat Interface**: Modern, responsive chat interface for seamless user interaction
- **Document Discovery**: Explore and discover relevant legal documents
- **Query History**: Track and revisit your previous legal queries

## Architecture

<img src="docs/assets/Package%20Diagram.jpg" alt="Package Diagram" width="800"/>

The system follows a modern microservices architecture with:

- **Frontend**: Next.js React application with Tailwind CSS
- **Backend**: FastAPI Python server with AI integration
- **AI Services**: Google Gemini integration for intelligent responses
- **Document Processing**: FAISS vector database and BM25 for semantic and keyword-based search

## Quick Start

### Prerequisites

- Node.js 18+ and npm
- Python 3.8+
- Google Gemini API key

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/niduniDK/LegalAI.git
   cd LegalAI
   ```

2. **Set up the Backend**

    Create a virtual environment (recommended):

    ```bash
    cd backend
    python -m venv venv
    # On Windows
    venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    # Install dependencies
    pip install -r requirements.txt
    ```

    Set up environment variables by creating a `.env` file in the Backend directory:

    ```env
    GEMINI_API_KEY=your_google_gemini_api_key # https://aistudio.google.com/apikey
    GROQ_API_KEY=your_groq_api_key # https://console.groq.com/keys
    ```

    Run the server:

    ```bash
    python main.py
    ```

3. **Set up the Frontend**

   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. **Access the Application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000

## Usage

1. **Ask Legal Questions**: Type your legal question in the chat interface
2. **Search Documents**: Use the search functionality to find relevant legal documents
3. **Get Recommendations**: Receive personalized recommendations based on your query history
4. **Explore**: Discover new legal topics and documents through the discovery interface

## Technology Stack

### Frontend

- **Framework**: Next.js 15 with React 19
- **Styling**: Tailwind CSS
- **UI Components**: Radix UI
- **Icons**: Lucide React
- **Build Tool**: Turbopack

### Backend

- **Framework**: FastAPI
- **AI Integration**: Google Gemini AI
- **Vector Search**: FAISS
- **Document Processing**: Beautiful Soup, pandas
- **Environment**: Python 3.8+

## Project Structure

```
LegalAI/
├── Backend/                 # Python FastAPI backend
│   ├── main.py             # Application entry point
│   ├── requirements.txt    # Python dependencies
│   ├── routers/            # API route handlers
│   └── services/           # Business logic services
├── frontend/               # Next.js React frontend
│   ├── src/app/           # Application pages and components
│   ├── components/        # Reusable UI components
│   └── package.json       # Node.js dependencies
└── docs/                  # Project documentation
```

## API Endpoints

- `POST /chat/get_ai_response` - Get AI-powered responses to legal queries
- `POST /get_docs/search` - Search legal documents
- `POST /recommendations` - Get personalized recommendations

## Contributing

We welcome contributions! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Documentation

- [Software Architecture Document](docs/Software%20Architecture%20Document.pdf)
- [Software Requirements Specification](docs/Software%20Requirements%20Specification.pdf)
- [Feasibility Report](docs/Feasibility%20Report.pdf)

---

Built with for better access to legal information
