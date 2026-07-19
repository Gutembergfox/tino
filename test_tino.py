import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from main import SYSTEM_PROMPT


load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

TEXTO_1 = """In this essay I will talk about the importance of education. So, education is very important for the society. You know, without education the people cannot develop. For me to study is very difficult but I pretend to continue. Actually, the technology is changing everything. Like, the students have more access to information now. Thanks God we live in this era."""

USER_MESSAGE = f"""Target register: academic
Text to analyze:
\"\"\"
{TEXTO_1}
\"\"\"
"""

response = client.chat.completions.create(
    model="gpt-5.6",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": USER_MESSAGE},
    ],
)

raw = response.choices[0].message.content or ""
print("=== RAW RESPONSE ===")
print(raw)
print()
print("=== PARSED JSON ===")
try:
    parsed = json.loads(raw)
    print(json.dumps(parsed, indent=2, ensure_ascii=False))
except Exception as error:
    print(f"Não veio JSON válido: {error}")
