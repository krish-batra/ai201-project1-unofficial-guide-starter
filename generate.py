"""
Milestone 5: Grounded Response Generation
Uses retrieved chunks as context and Groq LLM to generate grounded answers.
Answers are based only on retrieved documents — no general knowledge.
"""

import os
from dotenv import load_dotenv
from groq import Groq
from retrieve import retrieve

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are a helpful assistant that answers questions about CS professors at the University of Pittsburgh.

IMPORTANT RULES:
1. Answer ONLY using the information provided in the documents below.
2. Do NOT use any outside knowledge or make assumptions beyond what the documents say.
3. Always cite which document(s) your answer comes from at the end of your response, under a "Sources:" heading.
4. If the provided documents do not contain enough information to answer the question, say exactly: "I don't have enough information in my documents to answer that question."
5. Be concise and direct. Quote specific student reviews when they support your answer.
"""


def format_context(chunks):
    """
    Formats retrieved chunks into a readable context block for the LLM prompt.
    """
    context_parts = []
    for i, chunk in enumerate(chunks):
        context_parts.append(
            f"[Document {i+1} — Source: {chunk['source']}]\n{chunk['text']}"
        )
    return "\n\n".join(context_parts)


def generate_answer(query, k=5):
    """
    Retrieves relevant chunks and generates a grounded answer using Groq.
    Returns a dict with keys: answer, sources, chunks.
    """
    # Step 1: Retrieve relevant chunks
    chunks = retrieve(query, k=k)

    # Step 2: Format context
    context = format_context(chunks)

    # Step 3: Build the user message
    user_message = f"""Here are the relevant student reviews from Rate My Professors:

{context}

Based ONLY on the documents above, please answer the following question:
{query}"""

    # Step 4: Call Groq LLM
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ],
        max_tokens=1000,
        temperature=0.2
    )

    answer = response.choices[0].message.content

    # Step 5: Collect unique sources
    sources = list(dict.fromkeys(chunk["source"] for chunk in chunks))

    return {
        "answer": answer,
        "sources": sources,
        "chunks": chunks
    }


def ask(question):
    """
    Public interface for the query system.
    Prints the answer and sources, and returns the result dict.
    """
    print(f"\nQuestion: {question}")
    print("-" * 60)

    result = generate_answer(question)

    print(result["answer"])
    print("\nRetrieved from:")
    for source in result["sources"]:
        print(f"  • {source}")

    return result


if __name__ == "__main__":
    # Test with evaluation plan questions
    test_questions = [
        "Does Jarrett Billingsley allow AI on assignments?",
        "Are Nick Farnan's exams open book?",
        "What is a class that has nothing to do with CS at Pitt?",  # out-of-scope test
    ]

    for question in test_questions:
        ask(question)
        print("\n" + "="*60)