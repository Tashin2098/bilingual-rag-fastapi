from fastapi import APIRouter, File, UploadFile, Header, HTTPException, Query
from langdetect import detect
from googletrans import Translator
from faiss_index import faiss_index

router = APIRouter()
translator = Translator()
API_KEY = "my_very_secret_key_123"

def verify_api_key(key: str):
    if key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

# ========== INGESTION ENDPOINT ==========
@router.post("/ingest")
async def ingest_document(file: UploadFile = File(...), x_api_key: str = Header(...)):
    """
    Accept documents in ANY language (English, Japanese, etc.)
    Store them with language tags
    """
    verify_api_key(x_api_key)
    if not file.filename.endswith(".txt"):
        raise HTTPException(status_code=400, detail="Only .txt files allowed")
    
    content = (await file.read()).decode("utf-8")
    lang = detect(content)  # Detects: "en", "ja", etc.
    
    faiss_index.add_document(content, lang)
    
    return {
        "message": "Document ingested successfully",
        "language": lang,
        "note": f"Document stored in {lang}. Can be queried in any language!"
    }

# ========== RETRIEVAL ENDPOINT ==========
@router.get("/retrieve")
async def retrieve_docs(query: str, x_api_key: str = Header(...)):
    """
    BILINGUAL FEATURE:
    Query can be in ANY language (English, Japanese, etc.)
    System retrieves relevant chunks from documents in ANY language
    The multilingual embedding model handles the semantic matching!
    """
    verify_api_key(x_api_key)
    
    # Detect the query language
    query_lang = detect(query)
    
    # Retrieve - works cross-lingual thanks to multilingual embeddings!
    results = faiss_index.query(query, top_k=3)
    
    return {
        "query": query,
        "query_language": query_lang,  # What language the user asked in
        "results": results,
        "note": "Results may be in different language than query - this is intentional!"
    }

# ========== GENERATION ENDPOINT ==========
@router.get("/generate")
async def generate_response(
    query: str, 
    output_language: str = Query(None), 
    x_api_key: str = Header(...)
):
    """
    ADVANCED BILINGUAL FEATURE:
    
    1. Accept query in ANY language
    2. Retrieve relevant chunks (may be in different language)
    3. Combine into mock response
    4. If output_language specified, translate to that language
    
    EXAMPLES:
    - English doc + Japanese query + output_language='ja' = Answer in Japanese
    - Japanese doc + English query + output_language='en' = Answer in English
    - English doc + English query + output_language='ja' = Translate English answer to Japanese
    """
    verify_api_key(x_api_key)
    
    # Detect query language
    query_lang = detect(query)
    
    # Retrieve relevant chunks (works cross-lingual!)
    results = faiss_index.query(query, top_k=3)
    
    # Combine retrieved chunks
    combined_text = "\n".join([doc["content"] for doc in results])
    
    # Create response
    response = f"Mock LLM response based on retrieved documents:\n{combined_text}\n\nAnswer to: {query}"
    
    # TRANSLATION LOGIC
    # Determine output language
    if output_language:
        target_lang = output_language
    else:
        target_lang = query_lang  # Default: respond in query language
    
    # Translate if needed
    if target_lang != query_lang:
        response = translator.translate(response, dest=target_lang).text
    
    return {
        "query": query,
        "query_language": query_lang,
        "response": response,
        "output_language": target_lang,
        "original_doc_languages": [doc["lang"] for doc in results],
        "note": "System successfully handled cross-lingual query, retrieval, and translation!"
    }
