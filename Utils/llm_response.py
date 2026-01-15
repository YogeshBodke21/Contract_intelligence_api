from openai import OpenAI
from decouple import config

OPENAI_API_KEY = config("OPENAI_API_KEY")

def llm_prompt(top_chunks, que):
    context = "\n\n".join(text for score , text in top_chunks)

    prompt = f"""
    Answer the question using ONLY the context below.
    If the answer is not in the context, say "I don't know".

    Context:
    {context}

    Question:
    {que}

    Answer:"""
    return prompt




def call_llm(top_chunks, question):
    client = OpenAI(api_key = OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You answer using provided context only."},
            {"role": "user", "content": llm_prompt(top_chunks, question)}
        ],
        temperature=0.2
    )
    return response.choices[0].message.content



# print(call_llm(top_chunks, que))