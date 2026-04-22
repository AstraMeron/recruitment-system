import asyncio
import json
import logging
from datetime import datetime, UTC
from typing import List, Dict, Any
from jinja2 import Template

# Setup Logging for Reliability tracking
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EmailEngine:
    def __init__(self, template_str: str, max_retries: int = 3, concurrency: int = 5):
        self.template = Template(template_str)
        self.max_retries = max_retries
        self.concurrency_limit = asyncio.Semaphore(concurrency)
        self.logs = []

    def render(self, user_data: Dict[str, Any]) -> str:
        """Requirement 1: Templating Engine with Variable Validation"""
        required_vars = ['name', 'role']
        for var in required_vars:
            if var not in user_data or not user_data[var]:
                raise ValueError(f"Missing required attribute: {var}")
        
        # Injects user data into {{name}} and {{role}} placeholders
        return self.template.render(**user_data)

    async def send_email_mock(self, user: Dict[str, Any], content: str):
        """Requirement 2: Sending Mechanism (Mocked Service)"""
        await asyncio.sleep(0.5)  # Simulate network latency
        if "@error.com" in user['email']:
            raise ConnectionError("SMTP Server Timeout")
        return True

    async def process_user(self, user: Dict[str, Any]):
        """Requirement 3 & 5: Controlled Concurrency and Resilient Error Handling"""
        async with self.concurrency_limit:
            status = "pending"
            error_reason = None
            
            for attempt in range(self.max_retries):
                try:
                    email_body = self.render(user)
                    await self.send_email_mock(user, email_body)
                    status = "sent"
                    error_reason = None
                    break
                except Exception as e:
                    status = "failed"
                    error_reason = str(e)
                    if attempt < self.max_retries - 1:
                        logger.warning(f"Attempt {attempt + 1} failed for {user['email']}. Retrying...")
                        await asyncio.sleep(1) # Simple retry delay
                    else:
                        logger.error(f"Final attempt failed for {user['email']}: {e}")

            # Requirement 4: Persistent Log Entry (using modern UTC format)
            log_entry = {
                "email": user.get("email"),
                "status": status,
                "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
                "error_reason": error_reason
            }
            self.logs.append(log_entry)
            return log_entry

    async def run_batch(self, user_list: List[Dict[str, Any]]):
        """Requirement 3: Batch Processing & Concurrency Implementation"""
        tasks = [self.process_user(user) for user in user_list]
        await asyncio.gather(*tasks)
        
        # Persistence: Save logs to JSON file
        with open("email_dispatch_log.json", "w") as f:
            json.dump(self.logs, f, indent=4)
        print(f"\n--- Batch Complete. Logged {len(self.logs)} attempts to email_dispatch_log.json ---")

# --- Execution Block ---
if __name__ == "__main__":
    USER_DATA = [
        { "name": "Alice", "email": "alice@example.com", "role": "Engineer" },
        { "name": "Bob", "email": "bob@example.com", "role": "Designer" },
        { "name": "Charlie", "email": "charlie@error.com", "role": "Manager" }, # Failure test
        { "name": "Mary", "email": "merontilahunn@gmail.com", "role": "Lead Dev" }
    ]

    TEMPLATE_STR = """
    Subject: Welcome to the company!
    Hi {{name}}, we are excited to have you join as a {{role}}.
    """

    engine = EmailEngine(TEMPLATE_STR)
    asyncio.run(engine.run_batch(USER_DATA))