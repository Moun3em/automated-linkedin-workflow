from typing import Dict, Optional
import asyncio
from datetime import datetime
from pydantic import BaseModel, Field
from services.api_client import APIClient

class ContentRequest(BaseModel):
    topic: str = Field(..., min_length=3, max_length=200)
    industry: str = Field(..., min_length=2)
    expertise_areas: Optional[str] = None
    personal_story: Optional[str] = None

class ContentGenerator:
    def __init__(self, api_client: APIClient):
        self.api_client = api_client

    async def initialize(self):
        pass

    async def generate_content(self, request: ContentRequest) -> Dict:
        content = await self.api_client.openai_request(
            f"Create a LinkedIn post about {request.topic} for {request.industry} industry."
            f"\nExpertise: {request.expertise_areas or 'General'}"
            f"\nPersonal story: {request.personal_story or 'None'}",
            "You are a LinkedIn content expert"
        )

        doc_id = await self.api_client.create_doc(
            f"{request.topic}_{datetime.now().strftime('%Y%m%d')}",
            content["content"]
        )

        return {"doc_id": doc_id, "content": content["content"]}