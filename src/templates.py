import re
from typing import Dict, Any, Set

class TemplateManager:
    """
    Handles Requirement 1: Templating Engine.
    Ensures no 'template leakage' and validates data before sending.
    """
    def __init__(self, template_str: str):
        self.template_str = template_str
        # Automatically find placeholders like {{name}} using Regex
        self.required_fields = self._extract_placeholders()

    def _extract_placeholders(self) -> Set[str]:
        # Finds everything inside {{ }}
        return set(re.findall(r"\{\{\s*(\w+)\s*\}\}", self.template_str))

    def validate_user_data(self, user_data: Dict[str, Any]):
        """
        Requirement 1 & 5: Throws handled errors for missing data or 
        invalid email formats before the email is even queued.
        """
        # 1. Check for missing variables
        missing = [f for f in self.required_fields if f not in user_data or not user_data[f]]
        if missing:
            raise ValueError(f"Data missing for placeholders: {', '.join(missing)}")
        
        # 2. Check for basic email validity (Requirement 5)
        if "email" not in user_data or "@" not in user_data["email"]:
            raise ValueError(f"Invalid or missing email address: {user_data.get('email')}")

    def render(self, user_data: Dict[str, Any]) -> str:
        """Requirement 1: Variable Replacement."""
        # Run validation first
        self.validate_user_data(user_data)
        
        content = self.template_str
        for field in self.required_fields:
            # Replace {{field}} with the actual value (e.g., 'Alice')
            content = content.replace(f"{{{{{field}}}}}", str(user_data[field]))
        return content