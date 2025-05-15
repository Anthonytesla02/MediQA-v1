# MediQA Detailed Technical Documentation

## Table of Contents

1. [System Architecture Overview](#system-architecture-overview)
   - [Core Components](#core-components)
   - [Database Schema](#database-schema)
   - [Tech Stack](#tech-stack)

2. [Knowledge Base and Document Processing](#knowledge-base-and-document-processing)
   - [Document Loading and Parsing](#document-loading-and-parsing)
   - [Document Structure Analysis](#document-structure-analysis)
   - [Text Extraction Process](#text-extraction-process)

3. [Retrieval Augmented Generation (RAG) Engine](#retrieval-augmented-generation-rag-engine)
   - [Content Chunking](#content-chunking)
   - [Semantic Search Implementation](#semantic-search-implementation)
   - [Context Generation for AI Prompts](#context-generation-for-ai-prompts)

4. [AI Integration for Medical Diagnosis](#ai-integration-for-medical-diagnosis)
   - [Chat Query Processing](#chat-query-processing)
   - [Prompt Engineering for Medical Context](#prompt-engineering-for-medical-context)
   - [API Interaction with Mistral AI](#api-interaction-with-mistral-ai)

5. [Case Study Generation System](#case-study-generation-system)
   - [Topic Selection Algorithm](#topic-selection-algorithm)
   - [Differential Diagnosis Generation](#differential-diagnosis-generation)
   - [Medical Case Prompt Engineering](#medical-case-prompt-engineering)
   - [Response Processing and Error Handling](#response-processing-and-error-handling)

6. [Case Study Evaluation System](#case-study-evaluation-system)
   - [Diagnosis Evaluation Logic](#diagnosis-evaluation-logic)
   - [Treatment Evaluation Algorithm](#treatment-evaluation-algorithm)
   - [Scoring Methodology](#scoring-methodology)
   - [Feedback Generation](#feedback-generation)

7. [Application Workflow](#application-workflow)
   - [Initialization Process](#initialization-process)
   - [Session Management](#session-management)
   - [API Endpoints](#api-endpoints)

---

## System Architecture Overview

MediQA is a comprehensive medical training platform designed specifically for Ghanaian pharmacy practice. The system employs a sophisticated architecture that integrates AI services, document processing, and interactive user interfaces to deliver an engaging learning experience.

### Core Components

1. **Flask Web Application**:
   - Located in `app.py` and `main.py`
   - Handles HTTP requests, session management, and application state
   - Uses Werkzeug for WSGI interface and security features

2. **Document Processor**:
   - Located in `document_processor.py`
   - Extracts and structures content from medical reference documents
   - Parses chapters, sections, and content for retrieval

3. **RAG Engine**:
   - Located in `rag_engine.py`
   - Implements retrieval-augmented generation for context-aware AI responses
   - Chunks document content and provides semantic search capabilities

4. **AI Service**:
   - Located in `ai_service.py`
   - Manages API interactions with Mistral AI
   - Generates case studies, evaluations, and chat responses

5. **Database Layer**:
   - Uses SQLAlchemy ORM with PostgreSQL
   - Stores user data, case attempts, achievements, and more
   - Models defined in `models.py`

### Database Schema

The database schema is implemented in `models.py` with these key tables:

```python
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    points = db.Column(db.Integer, default=0)
    streak = db.Column(db.Integer, default=0)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    chat_histories = db.relationship('ChatHistory', backref='user', lazy=True)
    case_attempts = db.relationship('CaseAttempt', backref='user', lazy=True)
    challenge_attempts = db.relationship('ChallengeAttempt', backref='user', lazy=True)
    flashcard_progresses = db.relationship('FlashcardProgress', backref='user', lazy=True)
    achievements = db.relationship('UserAchievement', backref='user', lazy=True)

class Case(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    symptoms = db.Column(db.Text, nullable=False)  # Stored as JSON
    diagnosis = db.Column(db.String(120), nullable=False)
    difficulty = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    attempts = db.relationship('CaseAttempt', backref='case', lazy=True)
```

### Tech Stack

- **Backend**: Python 3.11 with Flask framework
- **Database**: PostgreSQL via SQLAlchemy ORM
- **AI Provider**: Mistral AI API
- **Document Processing**: python-docx for DOCX parsing
- **Frontend**: HTML, CSS, JavaScript
- **Authentication**: Flask-Login for session management
- **Containerization**: Deployed via Replit infrastructure

---

## Knowledge Base and Document Processing

The MediQA system uses a medical reference document as its knowledge base, implementing sophisticated parsing and retrieval mechanisms to extract relevant information.

### Document Loading and Parsing

The document processing system initializes in `document_processor.py` with the following steps:

```python
def initialize_document_processor():
    """Initialize the document processor by loading and parsing the document."""
    global document_content, document_sections
    
    if not os.path.exists(DOCUMENT_PATH):
        logger.error(f"Document not found at {DOCUMENT_PATH}")
        return False
    
    logger.info(f"Loading document from {DOCUMENT_PATH}")
    document_content = extract_text_from_docx(DOCUMENT_PATH)
    
    if not document_content:
        logger.error("Failed to extract content from document")
        return False
    
    logger.info(f"Successfully loaded document with {len(document_content)} lines")
    
    # Parse document structure
    document_sections = parse_document_structure(document_content)
    logger.info(f"Parsed document into {len(document_sections)} chapters")
    
    return True
```

The document path is configured in `config.py`:

```python
# Document configuration
DOCUMENT_PATH = "attached_assets/pharmacy_guide.docx"
```

### Document Structure Analysis

The system analyzes the document structure to identify chapters, sections, and content hierarchies:

```python
def parse_document_structure(content):
    """Parse the document to identify chapters and sections."""
    sections = {}
    current_chapter = None
    current_section = None
    
    for line in content:
        # Check for chapter headings
        if line.startswith("Chapter "):
            parts = line.split(".")
            if len(parts) >= 2:
                current_chapter = parts[1].strip()
                current_section = None
                sections[current_chapter] = {"sections": {}, "content": []}
        # Check for section headings
        elif current_chapter and len(line) < 100 and not line.startswith("Table of Contents") and not line.isdigit():
            current_section = line
            if current_section not in sections[current_chapter]["sections"]:
                sections[current_chapter]["sections"][current_section] = []
        # Add content to current section or chapter
        elif current_chapter:
            if current_section:
                sections[current_chapter]["sections"][current_section].append(line)
            else:
                sections[current_chapter]["content"].append(line)
    
    return sections
```

This parsing creates a nested dictionary structure that preserves the hierarchy of the document:

```
{
    "Chapter Title": {
        "content": ["Line 1", "Line 2", ...],
        "sections": {
            "Section 1": ["Line 1", "Line 2", ...],
            "Section 2": ["Line 1", "Line 2", ...]
        }
    }
}
```

### Text Extraction Process

The system extracts text from the DOCX file using the python-docx library:

```python
def extract_text_from_docx(docx_path):
    """Extract text from a .docx file."""
    try:
        doc = docx.Document(docx_path)
        text = []
        
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text.append(paragraph.text.strip())
        
        return text
    except Exception as e:
        logger.error(f"Error extracting text from document: {e}")
        return []
```

The extracted text is then made available through several accessor functions:

```python
def get_document_content():
    """Get the full document content."""
    return document_content

def get_document_sections():
    """Get the parsed document sections."""
    return document_sections

def get_section_content(chapter, section=None):
    """Get content for a specific chapter and section."""
    if chapter in document_sections:
        if section and section in document_sections[chapter]["sections"]:
            return document_sections[chapter]["sections"][section]
        else:
            return document_sections[chapter]["content"]
    return []
```

---

## Retrieval Augmented Generation (RAG) Engine

The RAG engine provides contextual information retrieval to enhance AI responses with domain-specific knowledge.

### Content Chunking

The RAG engine initializes by chunking the document content into manageable pieces for retrieval:

```python
def initialize_rag_engine():
    """Initialize the RAG engine with document content."""
    global document_chunks
    
    try:
        document_content = get_document_content()
        if not document_content:
            logger.error("Document content is empty, cannot create document chunks")
            return False
        
        # Combine content into a single text
        full_text = "\n".join(document_content)
        
        # Split text into simple chunks
        chunks = []
        words = full_text.split()
        
        # Create simple chunks based on word count (approximating character count)
        for i in range(0, len(words), CHUNK_SIZE // 5):  # Approximating 5 chars per word
            chunk = " ".join(words[i:i + CHUNK_SIZE // 5])
            chunks.append(chunk)
        
        document_chunks = chunks
        logger.info(f"Split document into {len(chunks)} chunks")
        
        return True
    except Exception as e:
        logger.error(f"Error initializing RAG engine: {e}")
        return False
```

The chunk size is configured in `config.py`:

```python
# RAG configuration
CHUNK_SIZE = 1500  # Increased for faster processing
CHUNK_OVERLAP = 100  # Decreased for faster processing
```

### Semantic Search Implementation

The system implements a sophisticated semantic search algorithm to find relevant document chunks:

```python
def search_similar_chunks(query, k=5):
    """Search for chunks similar to the query using enhanced keyword matching."""
    if not document_chunks:
        logger.error("Document chunks not initialized")
        return []
    
    try:
        # Preprocess query to extract important terms
        query_lower = query.lower()
        
        # Check for common patterns in medical queries
        treatment_phrases = ['treatment for', 'treatment of', 'how to treat', 'medicine for', 'drug for', 'therapy for', 'exact treatment']
        diagnosis_phrases = ['diagnosis of', 'symptoms of', 'signs of', 'diagnosing', 'diagnostic criteria', 'what is', 'what diagnosis']
        
        is_treatment_query = any(phrase in query_lower for phrase in treatment_phrases)
        is_diagnosis_query = any(phrase in query_lower for phrase in diagnosis_phrases)
        
        # Extract keywords - give more importance to multi-word phrases
        keywords = re.findall(r'\b\w+\b', query_lower)
        phrases = re.findall(r'\b\w+(?:\s+\w+){1,3}\b', query_lower)  # Match 2-4 word phrases
        
        # Score chunks based on keyword and phrase matches with enhanced weighting
        chunk_scores = []
        for chunk in document_chunks:
            chunk_lower = chunk.lower()
            score = 0
            
            # Score individual keywords
            for keyword in keywords:
                if keyword in chunk_lower:
                    # Skip common words that add noise
                    if len(keyword) <= 3 or keyword in ['and', 'the', 'for', 'with', 'what', 'this', 'that']:
                        continue
                    
                    # Higher score for exact matches (with word boundaries)
                    if re.search(r'\b' + re.escape(keyword) + r'\b', chunk_lower):
                        score += 2
                    else:
                        score += 1
            
            # Score multi-word phrases - these get higher weights
            for phrase in phrases:
                if phrase in chunk_lower:
                    # Higher score for longer phrases and key medical terms
                    phrase_len = len(phrase.split())
                    score += 3 * phrase_len
            
            # Boost score for chunks containing treatment info in treatment queries
            if is_treatment_query and any(word in chunk_lower for word in ['treatment', 'therapy', 'drug', 'medication', 'dose', 'regimen', 'management']):
                score *= 1.5
            
            # Boost score for chunks containing diagnosis info in diagnosis queries
            if is_diagnosis_query and any(word in chunk_lower for word in ['symptom', 'diagnosis', 'sign', 'diagnostic', 'indication', 'criterion', 'criteria']):
                score *= 1.5
            
            # Only include chunks with meaningful score
            if score > 2:  # Threshold to filter out weak matches
                chunk_scores.append({"content": chunk, "score": score})
        
        # Sort by score and return top k
        sorted_chunks = sorted(chunk_scores, key=lambda x: x["score"], reverse=True)
        return sorted_chunks[:k]
    except Exception as e:
        logger.error(f"Error searching document chunks: {e}")
        return []
```

This implementation uses several strategies for relevance scoring:

1. **Keyword matching** with higher scores for exact matches
2. **Phrase matching** with length-based scoring
3. **Query type detection** (treatment vs. diagnosis)
4. **Domain-specific boosting** for medical terminology

### Context Generation for AI Prompts

The RAG engine generates context for AI prompts by combining relevant chunks:

```python
def generate_context_for_query(query):
    """Generate a context for the given query by combining relevant chunks and structure the information."""
    # Increase result count to get more potentially relevant chunks
    chunks = search_similar_chunks(query, k=5)
    
    # Extract key medical terms that might be mentioned in document headers
    medical_terms = re.findall(r'\b[A-Z][a-z]{3,}(?:\s+[A-Z][a-z]{3,}){0,3}\b', query)
    disease_mentions = [term for term in medical_terms if len(term) > 5]  # Likely disease names are longer
    
    if not chunks or len(''.join([chunk["content"] for chunk in chunks])) < 200:  # If content is too short
        # Enhanced fallback to section-based search 
        try:
            sections = get_document_sections()
            relevant_sections = []
            
            # Check for disease/treatment terms in chapter and section names
            for chapter_name, chapter_data in sections.items():
                # More sophisticated chapter name matching
                chapter_match_score = 0
                
                # Check for whole query matches
                if query.lower() in chapter_name.lower():
                    chapter_match_score += 10
                
                # Check for disease name matches in chapter titles
                for term in disease_mentions:
                    if term.lower() in chapter_name.lower():
                        chapter_match_score += 5
                
                # Check for individual word matches
                for word in query.lower().split():
                    if len(word) > 3 and word in chapter_name.lower():
                        chapter_match_score += 1
                
                if chapter_match_score > 0:
                    relevant_sections.append(("\n".join(chapter_data["content"]), chapter_match_score))
                
                # Search section names similarly
                for section_name, section_content in chapter_data["sections"].items():
                    section_match_score = 0
                    
                    if query.lower() in section_name.lower():
                        section_match_score += 10
                    
                    for term in disease_mentions:
                        if term.lower() in section_name.lower():
                            section_match_score += 5
                    
                    for word in query.lower().split():
                        if len(word) > 3 and word in section_name.lower():
                            section_match_score += 1
                    
                    if section_match_score > 0:
                        relevant_sections.append(("\n".join(section_content), section_match_score))
            
            if relevant_sections:
                # Sort by relevance score
                relevant_sections.sort(key=lambda x: x[1], reverse=True)
                # Take top 3 most relevant sections
                top_sections = [section[0] for section in relevant_sections[:3]]
                return "\n\n".join(top_sections)
        except Exception as e:
            logger.error(f"Error in fallback section search: {e}")
        
        return "The guidelines do not appear to contain specific information about this query."
    
    # Structure the context with any section/chapter headings when available
    structured_context = []
    
    for chunk in chunks:
        content = chunk["content"]
        # Try to identify if this chunk has a heading/title line
        lines = content.split('\n')
        
        if len(lines) > 1 and len(lines[0]) < 100 and any(char.isupper() for char in lines[0]):
            # Likely a heading - format it more prominently
            heading = lines[0].strip()
            content_body = '\n'.join(lines[1:]).strip()
            
            structured_chunk = f"## {heading} ##\n{content_body}"
            structured_context.append(structured_chunk)
        else:
            structured_context.append(content)
    
    # Combine chunks into a well-structured context
    context = "\n\n".join(structured_context)
    return context
```

This function implements several fallback strategies:

1. Primary search using the chunk-based approach
2. Fallback to section-based search if chunk search yields insufficient results
3. Structural formatting to preserve headings and organization

---

## AI Integration for Medical Diagnosis

The AI integration in MediQA is handled primarily through the `ai_service.py` module, which interacts with the Mistral AI API.

### Chat Query Processing

User queries in the chat interface are processed through the `api_chat` endpoint in `routes.py`:

```python
@app.route('/api/chat', methods=['POST'])
def api_chat():
    """API endpoint for chat messages."""
    try:
        data = request.json
        query = data.get('query', '')
        user_id = session.get('user_id')
        
        if not query:
            return jsonify({"error": "Query is required"}), 400
        
        # Get AI response
        response = get_diagnosis_response(query)
        
        # Save chat history if user is logged in
        if user_id:
            # Update user streak
            update_user_streak(user_id)
            
            # Add chat to history
            chat_history = ChatHistory(
                user_id=user_id,
                messages=json.dumps([
                    {"role": "user", "content": query},
                    {"role": "assistant", "content": response}
                ])
            )
            db.session.add(chat_history)
            db.session.commit()
        
        return jsonify({"response": response})
    except Exception as e:
        logger.error(f"Error in chat API: {e}")
        return jsonify({"error": "An error occurred processing your request"}), 500
```

This endpoint calls the `get_diagnosis_response` function from `ai_service.py` to process the query.

### Prompt Engineering for Medical Context

The system employs sophisticated prompt engineering to generate medically accurate responses:

```python
def get_diagnosis_response(user_query):
    """Get an AI diagnosis response based on the user query."""
    # Generate context from document
    context = generate_context_for_query(user_query)
    
    # Check if it's a treatment or diagnosis query to customize prompt
    query_lower = user_query.lower()
    
    # Check for treatment-related queries
    treatment_phrases = ['treatment for', 'treatment of', 'how to treat', 'medicine for', 
                        'drug for', 'therapy for', 'exact treatment', 'management of']
    
    # Check for diagnosis-related queries
    diagnosis_phrases = ['diagnosis of', 'symptoms of', 'signs of', 'diagnosing', 
                        'diagnostic criteria', 'what is', 'what diagnosis']
    
    is_treatment_query = any(phrase in query_lower for phrase in treatment_phrases)
    is_diagnosis_query = any(phrase in query_lower for phrase in diagnosis_phrases)
    
    # Add special handling for potentially confused conditions
    contains_large_chronic_ulcers = 'large chronic ulcers' in query_lower or 'chronic skin ulcers' in query_lower
    contains_peptic_ulcer = 'peptic ulcer' in query_lower
    
    # Check for potential confusion between similar conditions
    requires_disambiguation = False
    
    # If both conditions are mentioned, no need for disambiguation as the query likely already specifies
    if not (contains_large_chronic_ulcers and contains_peptic_ulcer):
        # Check for "ulcer" by itself which might cause confusion
        if 'ulcer' in query_lower:
            if contains_large_chronic_ulcers:
                # Explicitly note this is about skin ulcers
                user_query = user_query.replace("Large Chronic Ulcers", "Large Chronic Skin Ulcers (a dermatological condition)") 
                requires_disambiguation = True
            elif contains_peptic_ulcer:
                # Explicitly note this is about gastrointestinal ulcers
                user_query = user_query.replace("Peptic Ulcer Disease", "Peptic Ulcer Disease (a gastrointestinal condition)")
                requires_disambiguation = True
    
    # Base system prompt - then customize based on query type
    system_content = f"""You are a precise medical assistant that references the Standard Treatment Guidelines.
    Base your responses ONLY on the following medical reference information:
    
    {context}
    
    IMPORTANT INSTRUCTIONS:
    1. Be extremely concise - only provide relevant information.
    2. Focus only on factual information from the reference material.
    3. Format key points with bullet points when appropriate.
    4. Do not include any personal opinions or information not found in the reference.
    5. If the reference doesn't contain relevant information, simply state "The guidelines do not contain specific information about this query."
    """
    
    # Add specific instructions for treatment queries
    if is_treatment_query:
        system_content += """
        Since this is a treatment query, your response should:
        - Begin with the standard/recommended treatment
        - List medications with dosages if specified in the reference
        - Note any alternative treatments or stepwise approaches
        - Include only treatment information, not general disease background
        - Format as a brief, structured treatment plan
        """
        
        # Add special instructions for specific conditions that might be confused
        if contains_large_chronic_ulcers:
            system_content += """
            IMPORTANT: The query is about LARGE CHRONIC SKIN ULCERS, which is a dermatological condition affecting the skin.
            DO NOT provide treatment for peptic ulcer disease (a gastrointestinal condition).
            Focus only on topical treatments, wound care, antibiotics for skin infections, etc. for chronic skin ulcers.
            """
        elif contains_peptic_ulcer:
            system_content += """
            IMPORTANT: The query is about PEPTIC ULCER DISEASE, which is a gastrointestinal condition affecting the stomach/duodenum.
            DO NOT provide treatment for skin ulcers or wounds.
            Focus only on acid-suppressing medications (e.g., proton pump inhibitors), H. pylori eradication if relevant, etc.
            """
    
    # Add specific instructions for diagnosis queries
    elif is_diagnosis_query:
        system_content += """
        Since this is a diagnosis query, your response should:
        - Begin with a clear definition or diagnostic criteria
        - List key symptoms and signs in bullet point format
        - Include any diagnostic tests mentioned in the reference
        - Focus on identification criteria only, not treatment options
        - Keep explanations minimal and fact-based
        """
        
        # Add special instructions for specific conditions that might be confused
        if contains_large_chronic_ulcers:
            system_content += """
            IMPORTANT: The query is about LARGE CHRONIC SKIN ULCERS, which is a dermatological condition affecting the skin.
            DO NOT provide information about peptic ulcer disease (a gastrointestinal condition).
            Focus only on criteria for diagnosing chronic skin wounds and ulcers affecting the skin's surface.
            """
        elif contains_peptic_ulcer:
            system_content += """
            IMPORTANT: The query is about PEPTIC ULCER DISEASE, which is a gastrointestinal condition affecting the stomach/duodenum.
            DO NOT provide information about skin ulcers or wounds.
            Focus only on diagnosing ulcers in the digestive tract, particularly in the stomach and/or duodenum.
            """
    
    # Create messages for AI with context and query-specific guidance
    messages = [
        {"role": "system", "content": system_content},
        {"role": "user", "content": user_query}
    ]
    
    # Generate response
    response = generate_ai_response(messages)
    return response
```

The prompt engineering includes several sophisticated elements:

1. **Query type detection** to customize the response format
2. **Condition disambiguation** to prevent confusion between similarly named conditions
3. **Context-specific instructions** for different medical query types
4. **Structured response formatting** guidelines

### API Interaction with Mistral AI

The system interacts with the Mistral AI API through the `generate_ai_response` function:

```python
def generate_ai_response(messages, temperature=0.7, max_tokens=1000):
    """Generate a response from Mistral AI."""
    # Check if API key is set to a valid value
    if MISTRAL_API_KEY in ["YOUR_MISTRAL_API_KEY", "", None]:
        logger.warning("Mistral API key not configured. Using fallback response.")
        return "API key not configured. Please provide a valid Mistral API key in the environment variables."
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {MISTRAL_API_KEY}"
    }
    
    payload = {
        "model": "mistral-medium",
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    
    # Log entire request for debugging (without API key)
    debug_payload = payload.copy()
    logger.debug(f"Payload: {json.dumps(debug_payload)}")
    
    try:
        # Log request for debugging
        logger.info(f"Making API request to Mistral AI with {len(messages)} messages")
        
        # Direct API call to Mistral AI with shorter timeout
        response = requests.post(MISTRAL_API_URL, headers=headers, json=payload, timeout=30)
        
        # Check for HTTP errors
        if response.status_code != 200:
            error_message = "Error connecting to AI service. Please try again later."
            
            # Add specific handling for rate limiting errors
            if response.status_code == 429:
                logger.error(f"Mistral API rate limit exceeded: {response.text}")
                error_message = "API rate limit exceeded. The system is currently handling too many requests. Please try again in a few minutes."
            else:
                logger.error(f"Mistral API error: Status {response.status_code}, Response: {response.text}")
            
            # Return a more specific fallback message
            return error_message
        
        # Parse the response
        try:
            response_json = response.json()
            
            # Log response for debugging (useful for understanding API structure)
            logger.debug(f"Mistral API raw response: {json.dumps(response_json)}")
            
            if not response_json.get("choices") or len(response_json["choices"]) == 0:
                logger.error(f"Mistral API returned no choices: {response_json}")
                # Return a fallback message instead of None
                return "AI service returned an incomplete response. Please try again later."
                
            return response_json["choices"][0]["message"]["content"]
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}. Raw response: {response.text}")
            # Return a fallback message instead of None
            return "Error processing AI response. Please try again later."
    except requests.exceptions.Timeout:
        logger.error("Mistral API request timed out after 30 seconds")
        # Return a fallback message instead of None
        return "AI service request timed out. Please try again later."
    except requests.exceptions.RequestException as e:
        logger.error(f"Error making request to Mistral API: {e}")
        # Return a fallback message instead of None
        return "Network error connecting to AI service. Please try again later."
    except Exception as e:
        logger.error(f"Error generating AI response: {e}")
        # Return a fallback message instead of None
        return "Unexpected error with AI service. Please try again later."
```

This function implements comprehensive error handling:

1. **API key validation** with fallback messaging
2. **HTTP error handling** with specific responses for rate limiting
3. **Timeout management** with appropriate user feedback
4. **Response validation** to ensure the API returned valid content
5. **Exception catching** at multiple levels

The API configuration is stored in `config.py`:

```python
MISTRAL_API_KEY = "j4h3leTe769ILXBLzwsMkrKEzWqZjOTj"
```

---

## Case Study Generation System

The case study generation system is a core component of MediQA, providing realistic medical scenarios for training.

### Topic Selection Algorithm

The system selects topics for case studies from a curated list in `ai_service.py`:

```python
def generate_case_simulation():
    """Generate a simulated patient case with sequential questions."""
    # Get a random topic from the curated list
    curated_topics = [
        "Diarrhoea", "Rotavirus Disease and Diarrhoea", "Constipation", "Peptic Ulcer Disease",
        "Gastro-oesophageal Reflux Disease", "Haemorrhoids", "Vomiting", "Anaemia", "Measles",
        "Pertussis", "Common cold", "Pneumonia", "Headache", "Boils", "Impetigo", "Buruli ulcer",
        "Yaws", "Superficial Fungal Skin infections", "Pityriasis Versicolor", "Herpes Simplex Infections",
        "Herpes Zoster Infections", "Chicken pox", "Large Chronic Ulcers", "Pruritus", "Urticaria",
        "Reactive Erythema and Bullous Reaction", "Acne Vulgaris", "Eczema", "Intertrigo", "Diabetes Mellitus",
        "Diabetic Ketoacidosis", "Diabetes in Pregnancy", "Treatment-Induced Hypoglycemia", "Dyslipidaemia",
        "Goitre", "Hypothyroidism", "Hyperthyroidism", "Overweight and Obesity", "Dysmenorrhoea",
        "Abortion", "Abnormal Vaginal Bleeding", "Abnormal Vaginal Discharge", "Acute Lower Abdominal Pain",
        "Menopause", "Erectile Dysfunction", "Urinary Tract Infection", "Sexually Transmitted Infections in Adults",
        "Fever", "Tuberculosis", "Typhoid fever", "Malaria", "Uncomplicated Malaria", "Severe Malaria",
        "Malaria in Pregnancy", "Worm Infestation", "Xerophthalmia", "Foreign body in the eye",
        "Neonatal conjunctivitis", "Red eye", "Stridor", "Acute Epiglottitis", "Retropharyngeal Abscess",
        "Pharyngitis and Tonsillitis", "Acute Sinusitis", "Acute otitis Media", "Chronic Otitis Media",
        "Epistaxis", "Dental Caries", "Oral Candidiasis", "Acute Necrotizing Ulcerative Gingivitis",
        "Acute Bacterial Sialoadenitis", "Chronic Periodontal Infections", "Mouth Ulcers", "Odontogenic Infections",
        "Osteoarthritis", "Rheumatoid arthritis", "Juvenile Idiopathic Arthritis", "Back pain", "Gout",
        "Dislocations", "Open Fractures", "Cellulitis", "Burns", "Wounds", "Bites and Stings",
        "Shock", "Acute Allergic Reaction"
    ]
    selected_topic = random.choice(curated_topics)
    logger.info(f"Selected topic for case simulation: {selected_topic}")
    
    # Get relevant document content for the selected topic
    from document_processor import search_document
    from rag_engine import generate_context_for_query
    topic_info = generate_context_for_query(selected_topic)
    
    # Create a medical case based on the selected topic
    case_data = create_medical_case_from_topic(selected_topic, topic_info)
    
    return case_data
```

This function performs several key steps:

1. **Topic selection** from a comprehensive list of medical conditions
2. **Information retrieval** using the RAG engine to get condition details
3. **Case generation** by calling the specialized case creation function

### Differential Diagnosis Generation

The system enhances case complexity by generating differential diagnoses:

```python
def create_medical_case_from_topic(topic, topic_info):
    """Create a medical case based on a specific topic and information."""
    # Generate a differential diagnosis for the case (another condition with similar symptoms)
    differential_topics = [
        "Common cold", "Pneumonia", "Influenza", "Bronchitis", "Sinusitis", "Pharyngitis",
        "Gastroenteritis", "Food poisoning", "Irritable Bowel Syndrome", "Peptic Ulcer Disease",
        "Migraine", "Tension headache", "Cluster headache", "Allergic rhinitis", "Asthma"
    ]
    differential_diagnosis = random.choice([d for d in differential_topics if d != topic])
```

This approach:

1. Maintains a list of potential differential diagnoses
2. Ensures the differential diagnosis is different from the main topic
3. Provides realistic clinical decision-making challenges

### Medical Case Prompt Engineering

The system uses sophisticated prompt engineering to generate realistic medical cases:

```python
# Generate the case via AI with specific instructions for the required format
messages = [
    {"role": "system", "content": """You are a medical case generator for healthcare student training.
    Create a realistic but concise medical case about the specified condition.
    Follow these specific guidelines to create challenging but realistic cases:
    
    1. BE SPECIFIC: If the condition has subtypes (e.g., complicated vs. uncomplicated malaria), select ONE specific subtype and make it clear in the diagnosis field. Don't create cases that require treating multiple subtypes.
    
    2. REALISTIC SYMPTOM PRESENTATION: Include only 3-5 key symptoms/signs in the presenting complaint. Real patients rarely present with all textbook symptoms.
    
    3. AVOID DIAGNOSTIC GIVEAWAYS: Don't include obvious diagnostic clues (like mentioning mosquito bites for malaria). The clinician should diagnose based on symptoms and history, not explicit hints.
    
    The format must follow this structure exactly:
    1. A short patient profile (age, gender, occupation if relevant)
    2. Presenting complaint (3-5 chief symptoms reported by patient, without obvious diagnostic clues)
    3. Patient history (relevant medical history, include only: blood pressure, blood sugar, allergies, current medications)
    4. Diagnosis (the SPECIFIC medical diagnosis including subtype if relevant)
    5. Treatment (the appropriate treatment plan for ONLY the specific diagnosis/subtype, limited to oral medications, topical treatments, and lifestyle modifications that can be provided by a pharmacy - NO injections, IV treatments, or surgical procedures)
    6. Differential reasoning (why this diagnosis instead of the given alternative)
    
    Format the output as a JSON object with these exact keys: 
    patient_info, presenting_complaint, patient_history, diagnosis, treatment, differential_reasoning."""}, 
    {"role": "user", "content": f"Create a case about {topic}. The differential diagnosis to discuss is {differential_diagnosis}. Use relevant medical information about {topic} symptoms, diagnosis and treatment. For specific conditions like malaria, select and specify ONE subtype (e.g., 'Uncomplicated Malaria' or 'Severe Malaria') and only include treatment for that specific subtype. Keep it concise but medically accurate."}
]
```

This prompt engineering includes several key elements:

1. **Explicit structure** for case generation with specific sections
2. **Clinical realism guidelines** to create authentic medical cases
3. **Specificity requirements** for subtypes and diagnosis clarity
4. **Format restrictions** for pharmacy-relevant treatments
5. **Clear differential reasoning** requirements

### Response Processing and Error Handling

The system implements comprehensive error handling and response processing:

```python
try:
    response = generate_ai_response(messages, temperature=0.7)
    # Try to parse the JSON from the response
    import json
    
    # Clean up the response in case it contains markdown formatting
    if '```json' in response and '```' in response:
        response = response.split('```json')[1].split('```')[0].strip()
    elif '```' in response:
        response = response.split('```')[1].split('```')[0].strip()
    
    # Additional cleanup to handle potential JSON issues
    response = response.replace('\n', ' ').replace('\r', ' ')
    response = response.replace('\\', '\\\\')  # Escape backslashes
    
    # Try to find and fix common JSON syntax errors
    response = response.replace('},}', '}}')   # Fix double closing
    response = response.replace(',}', '}')     # Fix trailing commas
    response = response.replace('{,', '{')     # Fix leading commas
    
    # Log the cleaned response for debugging
    logger.debug(f"Cleaned JSON response: {response}")
    
    try:
        case_data = json.loads(response)
        
        # Validate the case data has the required fields
        required_fields = ['patient_info', 'presenting_complaint', 'patient_history', 'diagnosis', 'treatment', 'differential_reasoning']
        if all(field in case_data for field in required_fields):
            logger.info(f"Successfully created case for {topic} with differential {differential_diagnosis}")
            # Add topic and differential topic to the case data
            case_data['topic'] = topic
            case_data['differential_topic'] = differential_diagnosis
            return case_data
        else:
            logger.warning(f"Generated case is missing required fields: {case_data.keys()}")
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON for case: {e}. Response: {response}")
        
except Exception as e:
    logger.error(f"Error generating case from topic: {e}")

# If we get here, something went wrong in the case generation
# Use fallback approach
return create_fallback_case_from_topic(topic, differential_diagnosis)
```

The error handling approach includes:

1. **Response cleaning** to handle markdown formatting
2. **JSON syntax correction** for common API response issues
3. **Field validation** to ensure complete case data
4. **Fallback mechanism** when case generation fails

---

## Case Study Evaluation System

The case study evaluation system analyzes user responses to diagnose and treat medical cases.

### Diagnosis Evaluation Logic

The system evaluates user diagnoses using sophisticated text matching in `routes.py`:

```python
# Handle compound diagnoses or subtypes (e.g., "Uncomplicated Malaria")
# Extract main diagnosis and subtypes
main_diagnosis = ''
subtype = ''

# Split the diagnosis to potentially identify subtype
diagnosis_parts = correct_diagnosis.split()

# Look for common subtype indicators like "uncomplicated", "severe", "chronic", etc.
subtype_indicators = ['uncomplicated', 'complicated', 'severe', 'mild', 'moderate', 'acute', 'chronic']

# Try to identify main diagnosis and subtype
if len(diagnosis_parts) > 1:
    # Check if the first word is a subtype indicator
    if diagnosis_parts[0].lower() in subtype_indicators:
        subtype = diagnosis_parts[0].lower()
        main_diagnosis = ' '.join(diagnosis_parts[1:]).lower()
    # Or if the last word is a subtype
    elif diagnosis_parts[-1].lower() in subtype_indicators:
        subtype = diagnosis_parts[-1].lower()
        main_diagnosis = ' '.join(diagnosis_parts[:-1]).lower()
    else:
        # Just use the whole thing as main diagnosis
        main_diagnosis = correct_diagnosis
else:
    main_diagnosis = correct_diagnosis
    
# Now we check if the user correctly identified both the main diagnosis and its subtype (if applicable)
if user_diagnosis.lower() == correct_diagnosis.lower():
    # Exact match gets full score
    diagnosis_score = 100
    diagnosis_feedback = "Perfect! Your diagnosis is correct."
elif main_diagnosis in user_diagnosis:
    if subtype and subtype not in user_diagnosis:
        # Got main diagnosis but missed the subtype
        diagnosis_score = 80
        diagnosis_feedback = f"Your diagnosis identifies the correct condition, but doesn't specify the exact subtype. The correct diagnosis is: {current_case['diagnosis']}."
    else:
        # Just get main diagnosis
        diagnosis_score = 90
        diagnosis_feedback = f"Your diagnosis is very close to the correct one. The precise diagnosis is: {current_case['diagnosis']}."
else:
    # Check if key terms from main diagnosis are present
    diagnosis_key_terms = main_diagnosis.split()
    matched_terms = 0
    
    for term in diagnosis_key_terms:
        if term.lower() in user_diagnosis and len(term) > 3:  # Only count meaningful terms
            matched_terms += 1
    
    # Calculate score based on term matches
    if matched_terms >= len(diagnosis_key_terms) // 2:
        # Partial match gets partial score
        diagnosis_score = 60
        diagnosis_feedback = f"Your diagnosis is close, but not quite the exact condition. The correct diagnosis is: {current_case['diagnosis']}."
    else:
        # Few matches gets low score
        diagnosis_score = 40
        diagnosis_feedback = f"Your diagnosis is different from the correct one. The correct diagnosis is: {current_case['diagnosis']}."
```

This algorithm implements several sophisticated evaluation techniques:

1. **Subtype extraction** to identify condition specificity
2. **Exact match detection** for complete correctness
3. **Partial match scoring** for approximately correct answers
4. **Term-based matching** for individual concept identification
5. **Tiered feedback** based on response quality

### Treatment Evaluation Algorithm

The system evaluates treatment plans with specialized logic for medical treatments:

```python
# Parse treatments into a structured format
# This is a simplified representation - the actual code is more complex
def treatment_match(treatment_text, user_meds):
    """Check if a specific treatment is mentioned in the user's response."""
    treatment_lower = treatment_text.lower()
    
    # Common abbreviations and synonyms
    medication_synonyms = {
        "ace inhibitor": ["acei", "angiotensin converting enzyme inhibitor"],
        "arb": ["angiotensin receptor blocker", "angiotensin ii receptor blocker"],
        "ppi": ["proton pump inhibitor"],
        "nsaid": ["non-steroidal anti-inflammatory", "non steroidal anti inflammatory"],
        "otc": ["over the counter", "over-the-counter"],
        # Many more synonyms...
    }
    
    # Check for direct mention
    if treatment_lower in user_meds:
        return True
    
    # Check for synonyms and variations
    for term, variations in medication_synonyms.items():
        if term in treatment_lower:
            # Check if any variation is in the user response
            for variation in variations:
                if variation in user_meds:
                    return True
        # Also check the reverse - if treatment contains a term that's in user_meds
        for variation in variations:
            if variation in treatment_lower and term in user_meds:
                return True
    
    # For certain drugs, we need to check partial matching (e.g., "amoxicillin" in "amoxicillin-clavulanate")
    # Extract potential drug names from the treatment text
    drug_names = re.findall(r'\b[a-z]+(?:cillin|mycin|floxacin|oxacin|azole|statin|sartan|pril|olol|dipine)\b', treatment_lower)
    
    for drug in drug_names:
        if drug in user_meds:
            return True
    
    return False
```

The treatment evaluation goes beyond simple text matching:

1. **Medication synonym recognition** for medical terminology variants
2. **Drug class identification** through suffix pattern matching
3. **Structured treatment parsing** for first-line vs. alternative treatments
4. **Clinical guideline alignment** checking

### Scoring Methodology

The system implements a weighted scoring methodology:

```python
# Set question weights (diagnosis is typically more important)
diagnosis_weight = 0.6
treatment_weight = 0.4

# Calculate overall score as weighted average
overall_score = int(
    (diagnosis_score * diagnosis_weight) + 
    (treatment_score * treatment_weight)
)
```

This approach:

1. Assigns more weight to diagnostic accuracy (60%)
2. Weights treatment appropriateness at 40%
3. Combines scores into a weighted average
4. Normalizes to an integer percentage

### Feedback Generation

The system generates appropriate feedback based on score ranges:

```python
# Generate feedback based on score
if overall_score >= 90:
    feedback = "Excellent work! Your answers demonstrate thorough understanding of the case."
elif overall_score >= 70:
    feedback = "Good job! You've demonstrated solid clinical reasoning, but there's still room for improvement."
elif overall_score >= 50:
    feedback = "You're on the right track, but need to improve your clinical analysis and medical knowledge."
else:
    feedback = "Your answers need significant improvement. Review the key clinical concepts for this condition."
```

The feedback system provides:

1. **Tiered encouragement** based on performance level
2. **Educational guidance** for improvement
3. **Specific diagnostic corrections** when needed
4. **Treatment recommendations** based on clinical guidelines

---

## Application Workflow

The MediQA application follows a well-defined workflow from initialization to user interaction.

### Initialization Process

The application initializes in `main.py` with the following sequence:

```python
if __name__ == "__main__":
    # Only run initialization if the flag file doesn't exist
    if not Path(INIT_FLAG_FILE).exists():
        success = auto_initialize()
        if not success:
            logger.error("Initialization failed. Check the logs for details.")
    
    # Start background initialization in a separate thread
    # This allows the app to start while document processing continues
    threading.Thread(target=background_initialization, daemon=True).start()
    
    # Start the application
    debug_mode = os.environ.get("FLASK_ENV") == "development"
    logger.info("Starting MediQA application on port 5000...")
    app.run(host="0.0.0.0", port=5000, debug=debug_mode)
```

The auto-initialization function sets up the database:

```python
def auto_initialize():
    """Performs initial database setup"""
    logger.info("Starting database initialization...")
    
    # Check if we have a PostgreSQL database
    if not DATABASE_URL:
        logger.error("PostgreSQL database not found. Please ensure DATABASE_URL is configured.")
        return False
    else:
        logger.info("PostgreSQL database found")
    
    # Initialize database tables and data
    try:
        from app import app, db
        with app.app_context():
            # Import models to ensure they're registered with SQLAlchemy
            import models
            
            # Create tables if they don't exist
            db.create_all()
            
            # Initialize achievements
            from gamification import initialize_achievements
            initialize_achievements()
            
            logger.info("Database tables created successfully")
            
            # Create flag file to indicate initialization is complete
            Path(INIT_FLAG_FILE).touch()
            logger.info("Database initialization complete")
            return True
    except Exception as e:
        logger.error(f"Error during database initialization: {e}")
        return False
```

The background initialization handles document loading in a non-blocking way:

```python
def background_initialization():
    """Initialize document processor and RAG engine in background thread"""
    from app import initialize_document_and_rag
    
    logger.info("Starting background initialization of document processor and RAG engine...")
    success = initialize_document_and_rag()
    
    if success:
        logger.info("Background initialization completed successfully")
    else:
        logger.warning("Background initialization completed with issues")
```

### Session Management

The application manages user sessions using Flask-Login:

```python
# Set up Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'index'  # Redirect to index page when login required
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = "error"  # For styling the flash message

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))
```

The authentication blueprint handles user login, signup, and session validation:

```python
@auth_bp.route('/api/user/validate', methods=['GET'])
def validate_session():
    """Validate if user session is still active."""
    if current_user.is_authenticated:
        return jsonify({
            "valid": True,
            "user": {
                "id": current_user.id,
                "username": current_user.username,
                "email": current_user.email
            }
        })
    else:
        return jsonify({"valid": False}), 401
```

### API Endpoints

The application exposes several key API endpoints:

1. **Chat API**:
   ```python
   @app.route('/api/chat', methods=['POST'])
   def api_chat():
       # Process chat queries and return AI responses
   ```

2. **Case Simulation API**:
   ```python
   @app.route('/api/simulation/new', methods=['GET'])
   def api_new_simulation():
       # Generate new case simulations
   
   @app.route('/api/simulation/submit', methods=['POST'])
   def api_submit_simulation():
       # Process user submissions for cases
   ```

3. **Flashcard API**:
   ```python
   @app.route('/api/flashcards/topic', methods=['POST'])
   def api_flashcards_topic():
       # Retrieve flashcards for a specific topic
   
   @app.route('/api/flashcard/review', methods=['POST'])
   def api_flashcard_review():
       # Process flashcard review results
   ```

4. **User Statistics API**:
   ```python
   @app.route('/api/user/stats', methods=['GET'])
   def api_user_stats():
       # Retrieve user statistics and progress
   ```

These endpoints form the core of the application's functionality, enabling users to interact with the AI, attempt case simulations, study with flashcards, and track their progress.

---

This comprehensive technical documentation provides an in-depth understanding of MediQA's architecture, AI integration, case generation, evaluation systems, and overall workflow. The system leverages modern AI capabilities and medical knowledge to create an engaging and educational platform for healthcare professionals in Ghana.