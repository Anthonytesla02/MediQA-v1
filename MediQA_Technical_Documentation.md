# MediQA Technical Documentation

## Table of Contents
1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [AI Integration for Case Study Generation](#ai-integration-for-case-study-generation)
4. [Case Study Evaluation System](#case-study-evaluation-system)
5. [AI Chat Implementation](#ai-chat-implementation)
6. [Document Processing and RAG Engine](#document-processing-and-rag-engine)
7. [Application Workflow](#application-workflow)
8. [Key Files and Components](#key-files-and-components)

## Overview

MediQA is a sophisticated web-based medical case simulation platform designed to enhance medical training and diagnostic skills for healthcare professionals, specifically tailored for Ghanaian pharmacy practice. The application leverages AI technology to generate realistic medical cases, evaluate user responses, and provide a knowledge base for medical inquiries.

## System Architecture

The MediQA application is built with the following technical stack:

- **Backend**: Python with Flask web framework
- **Database**: PostgreSQL for data persistence
- **AI Integration**: Mistral AI API for natural language processing
- **Frontend**: HTML, CSS, JavaScript for user interface
- **Authentication**: Flask-Login for user session management
- **ORM**: SQLAlchemy for database interactions

The application follows a Model-View-Controller (MVC) architecture with clear separation of concerns:
- **Models**: Database tables and relationships defined in `models.py`
- **Views**: HTML templates in the `templates` directory
- **Controllers**: Route handlers in `routes.py`

## AI Integration for Case Study Generation

### Case Generation Process

The case study generation system is primarily implemented in `ai_service.py` through several key functions:

1. **Topic Selection**:
   - The function `generate_case_simulation()` selects a random medical topic from a curated list of conditions relevant to Ghanaian pharmacy practice.
   - Current topics include various conditions like Diarrhoea, Malaria, Diabetes, etc.

2. **Knowledge Base Consultation**:
   - For the selected topic, the system retrieves relevant medical information using:
     ```python
     topic_info = generate_context_for_query(selected_topic)
     ```
   - This step leverages the RAG (Retrieval Augmented Generation) engine to pull relevant information from the attached document (`pharmacy_guide.docx`).

3. **Case Creation**:
   - The function `create_medical_case_from_topic(topic, topic_info)` constructs a realistic medical case.
   - It includes generating a differential diagnosis (another condition with similar symptoms) to make the case more challenging.

4. **AI Prompt Construction**:
   - The system crafts specialized prompts for the Mistral AI API:
   ```python
   messages = [
     {"role": "system", "content": "You are a medical case generator..."},
     {"role": "user", "content": f"Create a case about {topic}. The differential diagnosis to discuss is {differential_diagnosis}..."}
   ]
   ```
   - These prompts are designed to generate realistic medical cases with specific structures.

5. **Response Processing**:
   - The AI response is cleaned and parsed from JSON format.
   - Error handling is implemented to deal with malformed responses.
   - Fallback mechanisms exist for when the AI service is unavailable.

### Case Structure

The generated case contains the following information:
- Patient demographics (age, gender)
- Presenting complaint (symptoms)
- Medical history
- Diagnosis (correct answer)
- Treatment plan (correct answer)
- Differential diagnosis reasoning

This information is stored in the session but is partially hidden from the user during the simulation to test their diagnostic skills.

## Case Study Evaluation System

The evaluation of user responses occurs in the `api_submit_simulation` endpoint in `routes.py`:

1. **Diagnosis Evaluation**:
   - The system extracts key terms from the correct diagnosis.
   - It performs a term-matching algorithm to compare the user's diagnosis with the correct one.
   - Scoring is tiered:
     - Exact match: 100 points
     - Contains key terms: 80 points
     - Partial match: 60 points
     - Few matches: 40 points

   ```python
   # Example of diagnosis evaluation logic
   diagnosis_key_terms = re.findall(r'\b\w{4,}\b', current_case['diagnosis'].lower())
   user_diagnosis_lower = answers['diagnosis'].lower()
   matched_terms = sum(1 for term in diagnosis_key_terms if term in user_diagnosis_lower)
   
   if matched_terms == len(diagnosis_key_terms) or user_diagnosis_lower == current_case['diagnosis'].lower():
       # Exact match or all key terms present
       diagnosis_score = 100
   elif matched_terms >= len(diagnosis_key_terms) * 0.7:
       # Most key terms are present
       diagnosis_score = 80
   ```

2. **Treatment Evaluation**:
   - Similarly, the system evaluates the treatment plan by checking for key medications and management approaches.
   - Special handling is implemented for API errors:
   ```python
   if "Error connecting to AI service" in current_case['treatment']:
       # Handle the API error gracefully
       treatment_score = 80  # Give a decent score to avoid frustrating users
   ```

3. **Score Calculation**:
   - The overall score is calculated as an average of the diagnosis and treatment scores.
   - Points are awarded to the user based on their performance.
   - Achievements are awarded for milestones (first case solved, perfect score).

4. **Feedback Generation**:
   - Specific feedback is provided for each question, explaining what was correct or incorrect.
   - The correct answers are revealed after submission.

## AI Chat Implementation

The AI chat functionality is implemented through several components:

1. **Frontend Interface** (`static/js/chat.js` and `templates/chat.html`):
   - A clean chat interface with message input and display area.
   - Messages are formatted using Markdown for better readability.
   - Typing indicators provide user feedback during API calls.

2. **API Endpoint** (`routes.py`):
   - The `/api/chat` endpoint processes user queries:
   ```python
   @app.route('/api/chat', methods=['POST'])
   def api_chat():
       data = request.json
       query = data.get('query', '')
       # Get AI response
       response = get_diagnosis_response(query)
       # Save chat history if user is logged in
       if user_id:
           # Update user streak
           update_user_streak(user_id)
           # Add chat to history
           chat_history = ChatHistory(...)
       return jsonify({"response": response})
   ```

3. **AI Service** (`ai_service.py`):
   - The `get_diagnosis_response()` function processes medical queries.
   - It leverages the RAG engine to retrieve relevant context from the document.
   - The context is incorporated into the prompt sent to the AI:
   ```python
   def get_diagnosis_response(user_query):
       # Get relevant context from document
       context = generate_context_for_query(user_query)
       
       # Create message with context for AI
       messages = [
           {"role": "system", "content": "You are a medical assistant..."}, 
           {"role": "user", "content": f"Using this relevant medical information: {context}\n\nQuestion: {user_query}"}
       ]
       
       # Generate AI response
       response = generate_ai_response(messages)
       return response
   ```

4. **AI Integration** (via Mistral AI):
   - The `generate_ai_response()` function handles API calls to Mistral AI.
   - Error handling for API failures, rate limiting, and timeouts is implemented.
   - Configuration in `config.py` includes the API key and endpoint.

## Document Processing and RAG Engine

A key component of MediQA is its ability to retrieve and utilize information from a medical document:

1. **Document Loading** (`document_processor.py`):
   - On startup, the application loads a medical reference document: `attached_assets/pharmacy_guide.docx`
   - Content is extracted using the `python-docx` library:
   ```python
   def extract_text_from_docx(docx_path):
       document = Document(docx_path)
       lines = []
       for paragraph in document.paragraphs:
           lines.append(paragraph.text)
       return lines
   ```

2. **Document Structure Parsing**:
   - The document is parsed to identify chapters and sections:
   ```python
   def parse_document_structure(content):
       chapters = {}
       current_chapter = None
       current_section = None
       # Parsing logic...
       return chapters
   ```

3. **Chunking for RAG** (`rag_engine.py`):
   - The document is split into smaller chunks for efficient retrieval:
   ```python
   def initialize_rag_engine():
       document_content = get_document_content()
       full_text = "\n".join(document_content)
       # Split text into chunks
       chunks = []
       words = full_text.split()
       for i in range(0, len(words), CHUNK_SIZE // 5):
           chunk = " ".join(words[i:i + CHUNK_SIZE // 5])
           chunks.append(chunk)
       document_chunks = chunks
   ```

4. **Semantic Search**:
   - Simple keyword-based search is implemented to find relevant chunks:
   ```python
   def search_similar_chunks(query, k=5):
       # Search logic...
       return relevant_chunks
   ```

5. **Context Generation**:
   - Retrieved chunks are combined to create a context for AI prompts:
   ```python
   def generate_context_for_query(query):
       relevant_chunks = search_similar_chunks(query)
       context = "\n\n".join(relevant_chunks)
       return context
   ```

## Application Workflow

The overall flow of the application is managed by `main.py` and initialized components:

1. **Application Initialization**:
   - The process starts in `main.py` with `auto_initialize()`
   - Database tables are created if they don't exist
   - Default achievements are initialized

2. **Background Initialization**:
   - Document processing and RAG engine initialization occur in a background thread
   - This allows the web application to start quickly while processing continues
   ```python
   threading.Thread(target=background_initialization, daemon=True).start()
   ```

3. **User Interaction**:
   - Users interact with the system through various routes defined in `routes.py`
   - Main functionalities include:
     - Authentication (login/signup)
     - Chat with AI assistant
     - Case simulations
     - Flashcards for learning
     - Dashboard for progress tracking

4. **Data Persistence**:
   - User data, chat history, and simulation attempts are stored in PostgreSQL
   - The database schema is defined in `models.py`

## Key Files and Components

### Backend Core Files
- `main.py`: Application entry point
- `app.py`: Flask application setup and configuration
- `config.py`: Configuration variables and settings
- `models.py`: Database models and relationships
- `routes.py`: HTTP route handlers and API endpoints

### AI and Knowledge Components
- `ai_service.py`: AI interaction and case generation logic
- `document_processor.py`: DOCX parsing and document structure management
- `rag_engine.py`: Retrieval Augmented Generation functionality
- `api_validator.py`: AI API validation and error handling

### User Management
- `auth.py`: Authentication logic (login, signup, session management)
- `gamification.py`: Points, streaks, achievements system

### Frontend Assets
- `templates/`: HTML templates for all pages
- `static/js/`: JavaScript files for client-side functionality
  - `auth.js`: Authentication handling
  - `chat.js`: Chat interface logic
  - `simulation.js`: Case simulation logic
  - `flashcards.js`: Flashcard review system

### Knowledge Base
- `attached_assets/pharmacy_guide.docx`: Medical reference document for the RAG system

---

This document provides a comprehensive overview of the MediQA system's technical implementation. The application leverages modern AI capabilities along with traditional web technologies to create an engaging and educational experience for medical professionals.