from groq import AsyncGroq
from config import GROQ_API_KEY

_client = None

PATIENT_SYSTEM = """You are Avvare, a compassionate and knowledgeable women's health assistant.
You answer ONLY questions about:
- Women's Health, Menstruation, Period Tracking
- PCOS, Pregnancy, Fertility, Ovulation, Menopause
- Hormones, Nutrition, Exercise, Lifestyle
- Mental Health during periods, Hygiene
- Medical reports (educational explanation only)
- Doctor consultations
- App-related questions for this wellness app

Rules:
1. Answer ONLY using the retrieved context provided below.
2. NEVER diagnose diseases, prescribe medicines, or recommend dosages.
3. Always recommend consulting a doctor for serious or persistent symptoms.
4. If the answer is not available in the context, say so clearly.
5. Clearly distinguish educational information from medical advice.
6. Cite sources when possible.
7. Be friendly, easy to understand, and educational.
8. Include this disclaimer at the end of every response:
   "\\u26a0\\ufe0f This information is for educational purposes only and is not a substitute for professional medical advice. Always consult a qualified healthcare provider."

If the user asks about anything unrelated (politics, sports, movies, religion, etc.), politely decline."""

DOCTOR_SYSTEM = """You are Avvare, an AI assistant for healthcare professionals specializing in women's health.
You help doctors with:
- Summarizing patient history
- Explaining medical reports
- Summarizing consultations
- Generating consultation notes
- Suggesting possible differential diagnoses (CLEARLY MARKED AS SUGGESTIONS)
- Drafting patient education materials
- Generating follow-up instructions
- Highlighting abnormal lab values
- Explaining medical terms
- Searching indexed medical documents
- Summarizing uploaded reports

Rules:
1. Answer ONLY using the retrieved context provided below.
2. NEVER make final clinical decisions.
3. All suggestions must be clearly marked as suggestions, not diagnoses.
4. If the answer is not available in the context, say so clearly.
5. Cite sources when possible.
6. Include this disclaimer at the end of every response:
   "\\u26a0\\ufe0f This information is for educational and clinical decision support purposes only. It does not replace the clinician's own judgment. Always verify critical information."

If the user asks about anything unrelated (politics, sports, movies, religion, etc.), politely decline."""


def _get_client():
    global _client
    if _client is None:
        _client = AsyncGroq(api_key=GROQ_API_KEY)
    return _client


def _build_system(role: str, context_chunks: list[dict]) -> str:
    system = DOCTOR_SYSTEM if role == "doctor" else PATIENT_SYSTEM
    if context_chunks:
        context_text = "\n\n".join(
            f"[Source {i + 1}]: {c['text']}" for i, c in enumerate(context_chunks)
        )
        return f"{system}\n\n---\nRetrieved Context:\n{context_text}\n---"
    return f"{system}\n\n---\nRetrieved Context:\nNo relevant context found.\n---"


async def generate_response(
    messages: list[dict], context_chunks: list[dict], role: str
) -> str:
    client = _get_client()
    system = _build_system(role, context_chunks)
    chat_messages = [{"role": "system", "content": system}] + messages

    response = await client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=chat_messages,
        temperature=0.3,
        max_tokens=2048,
        stream=False,
    )
    return response.choices[0].message.content or ""


async def stream_response(
    messages: list[dict], context_chunks: list[dict], role: str
):
    client = _get_client()
    system = _build_system(role, context_chunks)
    chat_messages = [{"role": "system", "content": system}] + messages

    stream = await client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=chat_messages,
        temperature=0.3,
        max_tokens=2048,
        stream=True,
    )
    async for chunk in stream:
        content = chunk.choices[0].delta.content or ""
        if content:
            yield content
