from pydantic import BaseModel
from agents import RunContextWrapper, GuardrailFunctionOutput
from typing import Union, List, Dict, Any


class Credentials(BaseModel):
    """Model for storing credentials"""
    ucalgary_username: str
    ucalgary_password: str
    google_username: str
    google_password: str


class SecurityCheckOutput(BaseModel):
    """Model for security check output"""
    is_acceptable: bool
    reason: str


async def security_guardrail(ctx: RunContextWrapper[None], agent: Any, input: Union[str, List[Dict]]) -> GuardrailFunctionOutput:
    """Input guardrail to ensure request is appropriate"""
    input_text = input if isinstance(input, str) else str(input)
    
    # Basic checks for potentially problematic requests
    sensitive_terms = [
        "hack", "exploit", "steal", "bypass", "credential", "password", 
        "credit card", "bank account", "social security", "illegal"
    ]
    
    # Check if input contains sensitive terms
    contains_sensitive = any(term in input_text.lower() for term in sensitive_terms)
    
    # Check for attempts to modify credentials
    credential_modification = "change password" in input_text.lower() or "update credential" in input_text.lower()
    
    # Check for non-research purposes
    off_topic = any(term in input_text.lower() for term in ["game", "movie", "entertainment", "dating"])
    
    # Determine if the input is acceptable
    is_acceptable = not (contains_sensitive or credential_modification or off_topic)
    
    # Generate reason
    reason = "Input appears to be an appropriate research request."
    if contains_sensitive:
        reason = "Input contains sensitive terms that may indicate inappropriate usage."
    elif credential_modification:
        reason = "Input appears to request credential modification, which is not allowed."
    elif off_topic:
        reason = "Input appears to be off-topic for a research assistant."
    
    output_info = SecurityCheckOutput(
        is_acceptable=is_acceptable,
        reason=reason
    )
    
    return GuardrailFunctionOutput(
        output_info=output_info,
        tripwire_triggered=not is_acceptable,
    )


def mask_credentials(text: str, credentials: Credentials) -> str:
    """Mask credentials in text to avoid exposing them in logs"""
    masked_text = text
    
    # Replace each credential with asterisks
    for field, value in credentials.model_dump().items():
        if value and len(value) > 4:
            masked_value = value[:2] + "*" * (len(value) - 4) + value[-2:]
            masked_text = masked_text.replace(value, masked_value)
    
    return masked_text
