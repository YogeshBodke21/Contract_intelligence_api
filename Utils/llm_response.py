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



def call_llm_audit(prompt):
    client = OpenAI(api_key = OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )
    return response.choices[0].message.content

# print(call_llm(top_chunks, que))


####################
# LLM for Stream

def call_llm_stream(top_chunks, que):
    context = "\n".join([c[0].text for c in top_chunks])

    prompt = f"""
    Answer the question ONLY using the context below.

    Context:
    {context}

    Question:
    {que}
    """
    client = OpenAI(api_key=OPENAI_API_KEY)

    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        stream=True
    )

    for chunk in stream:
        delta = chunk.choices[0].delta
        print("delta", delta)
         # delta is an object, not a dict
        if hasattr(delta, "content") and delta.content:
            yield delta.content
