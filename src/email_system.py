import asyncio
import json
import logging
from datetime import datetime, UTC
from typing import List, Dict, Any

# Import the 'Gatekeeper' we built in Step 1
from templates import TemplateManager

# Setup professional logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EmailWorkerSystem:
    def __init__(self, template_str: str, worker_count: int = 3):
        self.tm = TemplateManager(template_str)
        self.queue = asyncio.Queue() # The "Stand Out" Queue System
        self.worker_count = worker_count
        self.results_log = []

    async def email_sender_service(self, user: Dict[str, Any], content: str):
        """Requirement 2: The actual 'sending' logic."""
        await asyncio.sleep(0.5) # Simulate network call
        if "error" in user['email']:
            raise ConnectionError("Remote SMTP Server Refused Connection")
        return True

    async def worker(self, worker_id: int):
        """
        The Consumer: Pulls jobs from the queue.
        Includes Requirement 5 (Retries) and Rate Limiting (Stand Out).
        """
        while True:
            user = await self.queue.get()
            email_addr = user.get('email', 'Unknown')
            
            # Rate Limiting: Ensure we don't burst too fast (e.g., 2 per second)
            await asyncio.sleep(0.5) 
            
            success = False
            # Retry Mechanism: Attempt up to 3 times
            for attempt in range(1, 4): 
                try:
                    email_content = self.tm.render(user)
                    await self.email_sender_service(user, email_content)
                    
                    self.log_status(email_addr, "sent")
                    logger.info(f"Worker-{worker_id}: Success for {email_addr}")
                    success = True
                    break # Exit retry loop on success
                
                except Exception as e:
                    logger.warning(f"Worker-{worker_id}: Attempt {attempt} failed for {email_addr}: {e}")
                    # If it's the last attempt, log as permanent failure
                    if attempt == 3:
                        self.log_status(email_addr, "failed", str(e))
                    else:
                        # Exponential Backoff: Wait longer after each failure
                        await asyncio.sleep(attempt * 1) 

            self.queue.task_done()

    def log_status(self, email: str, status: str, error: str = None):
        """Requirement 4: Persistent Logging (Now with Disk Writing)."""
        entry = {
            "email": email,
            "status": status,
            "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "error_reason": error
        }
        self.results_log.append(entry)
        
        # Incremental Save: Write to file every time a status changes
        # This ensures you don't lose data if the script crashes mid-way
        try:
            with open("final_dispatch_log.json", "w") as f:
                json.dump(self.results_log, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to write log to disk: {e}")

    async def run(self, user_data_list: List[Dict[str, Any]]):
        """The Producer: Orchestrates the workers and the queue."""
        # Start the worker tasks (The assembly line)
        workers = [asyncio.create_task(self.worker(i)) for i in range(self.worker_count)]

        # Fill the queue (Drop the jobs onto the belt)
        for user in user_data_list:
            await self.queue.put(user)

        # Wait for all jobs to be processed
        await self.queue.join()

        # Stop the workers
        for w in workers:
            w.cancel()
            
        # Wait a microsecond to ensure cancellations are processed
        await asyncio.gather(*workers, return_exceptions=True)    

        # Save final logs (Requirement 4)
        with open("final_dispatch_log.json", "w") as f:
            json.dump(self.results_log, f, indent=4)

if __name__ == "__main__":
    # Test Data
    USERS = [
        { "name": "Alice", "email": "alice@example.com", "role": "Engineer" },
        { "name": "Bob", "email": "bob@example.com", "role": "Designer" },
        { "name": "Charlie", "email": "charlie-error@example.com", "role": "Manager" }, # Failure test
        { "name": "Diana", "email": "diana@example.com", "role": "Intern" }
    ]

    TEMPLATE = "Subject: Welcome!\nHi {{name}}, welcome as our new {{role}}!"

    # Initialize the system with 2 concurrent workers
    system = EmailWorkerSystem(TEMPLATE, worker_count=2)
    
    # Run the async loop
    asyncio.run(system.run(USERS))            