import re
from typing import Any

class InputSanitizer:
    @staticmethod
    def sanitize_string(value: str) -> str:
        """
        Basic sanitization: trims whitespace and removes common SQL injection patterns.
        """
        if not isinstance(value, str):
            raise ValueError("Input must be a string")
        value = value.strip()
        # Remove common SQL injection patterns
        blacklist = [
            r"(--|;|/\*|\*/|@@|@|char\(|nchar\(|varchar\(|alter |begin |cast\(|create |cursor |declare |delete |drop |end |exec |execute |fetch |insert |kill |open |select |sys |sysobjects |syscolumns |table |update )",
        ]
        for pattern in blacklist:
            value = re.sub(pattern, "", value, flags=re.IGNORECASE)
        return value

    @staticmethod
    def sanitize_dict(data: dict) -> dict:
        """
        Recursively sanitize all string values in a dictionary.
        """
        sanitized = {}
        for k, v in data.items():
            if isinstance(v, str):
                sanitized[k] = InputSanitizer.sanitize_string(v)
            elif isinstance(v, dict):
                sanitized[k] = InputSanitizer.sanitize_dict(v)
            else:
                sanitized[k] = v
        return sanitized 