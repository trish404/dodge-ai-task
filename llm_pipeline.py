from groq import Groq

client = Groq(api_key=" ")


SYSTEM_PROMPT = """
You are a data assistant working with a structured business transaction graph.

STRICT RULES:
- ONLY return a single-line executable command.
- DO NOT explain anything.
- DO NOT include steps, reasoning, or markdown.
- DO NOT include punctuation except spaces.
- Output must be EXACTLY one of the formats below.

ALLOWED COMMANDS:
1. TRACE <ORDER_ID> [<ORDER_ID> ...]
2. TOP_PRODUCTS
3. INCOMPLETE_ORDERS
4. OUT_OF_SCOPE

RULES:
- If the query asks to trace one order → return: TRACE <ORDER_ID>
- If the query asks to trace multiple orders → return: TRACE <ORDER_ID1> <ORDER_ID2>
- Extract ONLY valid order IDs (format: SO_XXXXXX_XX)
- Convert lowercase to uppercase if needed
- If no valid order ID is present → return OUT_OF_SCOPE
- If query is unrelated → return OUT_OF_SCOPE
- If query is incomplete (e.g., "Trace") → return OUT_OF_SCOPE

EXAMPLES:

User: Trace SO_123
Output: TRACE SO_123

User: trace so_123
Output: TRACE SO_123

User: Show me full journey of SO_123
Output: TRACE SO_123

User: Trace SO_123 and SO_456
Output: TRACE SO_123 SO_456

User: Show top products
Output: TOP_PRODUCTS

User: Find incomplete orders
Output: INCOMPLETE_ORDERS

User: Trace
Output: OUT_OF_SCOPE

User: Who is the president?
Output: OUT_OF_SCOPE
"""

def is_out_of_scope(user_query):
    keywords = ["president", "poem", "weather", "who is", "write"]
    return any(k in user_query.lower() for k in keywords)

def is_incomplete_query(user_query):
    return user_query.strip().lower() in ["trace", "show", "get"]

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

STRICT RULES:
- Only use the provided result.
- Do NOT make assumptions.
- Do NOT add extra explanations.
- If result contains 'not found', say it clearly.

Answer:
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    return response.choices[0].message.content.strip()

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
