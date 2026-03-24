from groq import Groq

client = Groq(api_key="")


SYSTEM_PROMPT = """
You are a data assistant working with a structured business transaction graph.

Your job is to convert user queries into a SINGLE structured command.

====================
STRICT OUTPUT RULES
====================
- Output MUST be exactly ONE line.
- DO NOT explain anything.
- DO NOT include reasoning, steps, or markdown.
- DO NOT include punctuation except spaces.
- DO NOT include extra text.
- Output must match EXACTLY one of the allowed command formats.

====================
ALLOWED COMMANDS
====================
1. TRACE <ORDER_ID> [<ORDER_ID> ...]
2. TOP_PRODUCTS
3. INCOMPLETE_ORDERS
4. OUT_OF_SCOPE

====================
ORDER ID RULES
====================
- Valid format: SO_XXXXXX_XX
- Extract ALL valid order IDs from the query
- Convert lowercase → uppercase
- Ignore invalid IDs
- If multiple valid IDs → include all in TRACE command
- If no valid IDs → return OUT_OF_SCOPE

====================
INTENT MAPPING
====================
- Trace / journey / lifecycle / flow → TRACE
- Top products / highest sales → TOP_PRODUCTS
- Incomplete / missing billing → INCOMPLETE_ORDERS
- Anything unrelated → OUT_OF_SCOPE

====================
EDGE CASE HANDLING
====================
- "trace" (no ID) → OUT_OF_SCOPE
- random text / gibberish → OUT_OF_SCOPE
- mixed queries → prioritize valid dataset intent
- extra words (e.g., "please", "hey") → ignore

====================
EXAMPLES
====================

User: Trace SO_123456_10
Output: TRACE SO_123456_10

User: trace so_123456_10
Output: TRACE SO_123456_10

User: Show full journey of SO_123456_10
Output: TRACE SO_123456_10

User: Trace SO_123456_10 and SO_654321_20
Output: TRACE SO_123456_10 SO_654321_20

User: hey can you trace so_123456_10 pls
Output: TRACE SO_123456_10

User: Show top products
Output: TOP_PRODUCTS

User: Find incomplete orders
Output: INCOMPLETE_ORDERS

User: Trace
Output: OUT_OF_SCOPE

User: asdkjasd
Output: OUT_OF_SCOPE

User: Who is the president?
Output: OUT_OF_SCOPE
"""

def is_out_of_scope(user_query):
    keywords = ["president", "poem", "weather", "who is", "write"]
    return any(k in user_query.lower() for k in keywords)

def is_incomplete_query(user_query):
    text = user_query.lower().strip()
    return ("trace" in text or "show" in text or "get" in text) and "so_" not in text

def is_valid_command(query):
    valid = ["TRACE", "TOP_PRODUCTS", "INCOMPLETE_ORDERS", "OUT_OF_SCOPE"]
    return any(query.startswith(v) for v in valid)

def generate_query(user_query):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_query}
        ],
        temperature=0
    )

    return response.choices[0].message.content.strip().upper()

def generate_natural_answer(user_query, result):

    prompt = f"""
User Question: {user_query}
Data Result: {result}

You are a business data assistant.

STRICT RULES:
- Only use the provided data.
- Do NOT hallucinate or invent information.
- Do NOT assume missing values.
- Be concise and clear.

STYLE:
- Write in natural business language.
- Provide a short explanation of what the data represents.
- Avoid robotic formatting.

FORMAT:

If ONE order:
Start with a summary sentence.
Then describe the flow clearly.

Example:
"Order SO_123 has been fully processed.

It was delivered via DL_..., billed through BL_..., recorded in journal entries JE_..., and completed with payments PY_...."

If MULTIPLE orders:
Repeat the same structure for each.

If NOT FOUND:
"Order <ID> was not found in the dataset."

If INCOMPLETE:
Clearly mention missing stages (e.g., billing or payment not completed).

Answer:
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    return response.choices[0].message.content.strip().replace(". ", ".\n\n")


def full_pipeline(user_query, execute_query_func):

    if not user_query.strip():
        return "Please enter a valid query."

    if is_incomplete_query(user_query):
        return "Please provide a valid order ID."

    if is_out_of_scope(user_query):
        return "This system only answers questions related to the dataset."

    query = generate_query(user_query)

    print("Generated Query:", query)

    if query == "OUT_OF_SCOPE":
        return "This system only answers questions related to the dataset."

    if not is_valid_command(query):
        return "Invalid structured query."

    try:
        result = execute_query_func(query)
    except Exception as e:
        return f"Error executing query: {str(e)}"

    print("Execution Result:", result)

    return generate_natural_answer(user_query, result)
