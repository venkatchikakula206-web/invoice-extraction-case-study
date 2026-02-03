import base64
from openai import OpenAI

from ..schemas import ExtractedInvoice

SYSTEM_PROMPT = """You extract structured data from sales invoices.
Return ONLY valid JSON matching the schema. Do not include markdown or explanations.
If a field is missing, use null. Do not guess values that are not present."""

class OpenAIInvoiceExtractor:
    def __init__(self, api_key: str, model: str):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def extract(self, image_bytes: bytes) -> ExtractedInvoice:
        b64 = base64.b64encode(image_bytes).decode("utf-8")
        
        completion = self.client.beta.chat.completions.parse(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": [
                    {"type": "text", "text": "Extract the invoice fields."},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}}
                ]}
            ],
            response_format=ExtractedInvoice,
        )
        
        message = completion.choices[0].message
        if message.parsed:
            return message.parsed
        elif message.refusal:
             raise RuntimeError(f"Model refused to extract: {message.refusal}")
        else:
             raise RuntimeError("Model returned no parsed data")
