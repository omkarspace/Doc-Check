import openai
from app.config import settings

openai.api_key = settings.OPENAI_API_KEY

def analyze_document(text: str, document_type: str = "general") -> dict:
    """
    Analyze a document using AI and extract relevant information
    """
    try:
        prompt = f"""
        Analyze the following {document_type} document and extract the following information:
        1. Document type and classification
        2. Key entities (names, dates, amounts, addresses)
        3. Summary of the document content
        4. Any potential risks or compliance issues

        Document text: {text}
        """

        response = openai.ChatCompletion.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a document analysis AI assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )

        analysis = response.choices[0].message.content
        return {
            "status": "success",
            "analysis": analysis
        }
    except Exception as e:
        raise Exception(f"Error analyzing document: {str(e)}")
