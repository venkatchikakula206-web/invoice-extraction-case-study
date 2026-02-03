from ..config import Settings
from .openai_provider import OpenAIInvoiceExtractor
from .anthropic_provider import AnthropicInvoiceExtractor

def get_extractor(settings: Settings):
    provider = settings.llm_provider.lower()
    
    if provider == "openai":
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is not set")
        return OpenAIInvoiceExtractor(api_key=settings.openai_api_key, model=settings.openai_model)
    
    if provider == "anthropic":
        if not settings.anthropic_api_key:
            raise RuntimeError("ANTHROPIC_API_KEY is not set")
        return AnthropicInvoiceExtractor(api_key=settings.anthropic_api_key, model=settings.anthropic_model)
        
    raise RuntimeError(f"Unsupported LLM_PROVIDER: {settings.llm_provider}")
