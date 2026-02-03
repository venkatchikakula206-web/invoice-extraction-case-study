import base64
import json
from anthropic import Anthropic
from ..schemas import ExtractedInvoice

SYSTEM_PROMPT = """You are an expert data extraction assistant.
Your task is to extract structured data from sales invoices.
You must extract the data exactly according to the provided schema.
If a field is not present in the document, return null for that field.
Do not guess or hallucinate values.
"""

class AnthropicInvoiceExtractor:
    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20240620"):
        self.client = Anthropic(api_key=api_key)
        self.model = model

    def extract(self, image_bytes: bytes) -> ExtractedInvoice:
        b64 = base64.b64encode(image_bytes).decode("utf-8")
        
        # Generate the JSON schema from the Pydantic model
        # This ensures the schema is always in sync with the code
        schema = ExtractedInvoice.model_json_schema()
        
        # Define the tool for Anthropic
        tool_name = "extract_invoice"
        tools = [
            {
                "name": tool_name,
                "description": "Extracts structured data from an invoice image.",
                "input_schema": schema
            }
        ]

        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": b64,
                            },
                        },
                        {
                            "type": "text",
                            "text": "Please extract the invoice data."
                        }
                    ],
                }
            ],
            tools=tools,
            tool_choice={"type": "tool", "name": tool_name}
        )

        # Parse the tool use response
        for content in response.content:
            if content.type == "tool_use" and content.name == tool_name:
                return ExtractedInvoice.model_validate(content.input)
        
        raise RuntimeError("Anthropic model did not call the extraction tool")
