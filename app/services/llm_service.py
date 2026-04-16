"""
LLM Service — Handles communication with Google Gemini to convert
natural language questions into SQL queries.
"""

import re
import google.generativeai as genai
from pathlib import Path
from app.config import settings


class LLMService:
    """Converts natural language to SQL using Google Gemini."""

    def __init__(self):
        if not settings.GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY is not set. Please add it to your .env file."
            )
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)

        # Load system prompt from config folder
        prompt_path = Path(__file__).resolve().parent.parent / "prompts" / "system_prompt.txt"
        with open(prompt_path, "r", encoding="utf-8") as f:
            self.system_prompt_template = f.read()

    def generate_sql(self, question: str, schema: str) -> str:
        """
        Send the question + schema to Gemini and extract the SQL query.
        
        Args:
            question: The natural language question from the user.
            schema: The database schema string from SchemaService.
            
        Returns:
            A clean SQL SELECT query string.
            
        Raises:
            ValueError: If the LLM returns a non-SELECT or dangerous query.
        """
        # Build the prompt with the current schema from the loaded template
        system_prompt = self.system_prompt_template.format(schema=schema)

        # Call Gemini
        response = self.model.generate_content(
            contents=[
                {"role": "user", "parts": [{"text": system_prompt}]},
                {"role": "model", "parts": [{"text": "Understood. I will only output raw SQL SELECT queries based on the provided schema. Ready for your question."}]},
                {"role": "user", "parts": [{"text": question}]},
            ]
        )

        raw_sql = response.text.strip()

        # Clean up the response — remove markdown code fences if present
        sql = self._clean_sql(raw_sql)

        # Validate safety
        self._validate_sql(sql)

        return sql

    def _clean_sql(self, raw: str) -> str:
        """Remove markdown code fences and extra whitespace from LLM output."""
        # Remove ```sql ... ``` blocks
        cleaned = re.sub(r"```sql\s*", "", raw, flags=re.IGNORECASE)
        cleaned = re.sub(r"```\s*", "", cleaned)

        # Remove leading/trailing whitespace and semicolons
        cleaned = cleaned.strip().rstrip(";").strip()

        # Add back a single semicolon
        cleaned = cleaned + ";"

        return cleaned

    def _validate_sql(self, sql: str) -> None:
        """
        Validate that the generated SQL is safe to execute.
        
        Raises:
            ValueError: If dangerous SQL keywords are detected.
        """
        sql_upper = sql.upper()

        # List of forbidden keywords (destructive operations)
        forbidden = [
            "INSERT ", "UPDATE ", "DELETE ", "DROP ",
            "ALTER ", "CREATE ", "TRUNCATE ", "REPLACE ",
            "EXEC ", "EXECUTE ", "GRANT ", "REVOKE ",
            "ATTACH ", "DETACH ",
        ]

        for keyword in forbidden:
            if keyword in sql_upper:
                raise ValueError(
                    f"Unsafe SQL detected: '{keyword.strip()}' statements are not allowed. "
                    f"Only SELECT queries are permitted."
                )

        # Must start with SELECT (after optional whitespace)
        if not sql_upper.strip().startswith("SELECT"):
            raise ValueError(
                "Generated SQL must be a SELECT statement. "
                f"Got: {sql[:50]}..."
            )
