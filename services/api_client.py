from typing import Optional, Dict, Any
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential
import openai
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle
import os

class APIClient:
    def __init__(self):
        self.openai_client = self._init_openai()
        self.google_creds = self._init_google_creds()
        self.docs_service = self._build_docs_service()
        self.drive_service = self._build_drive_service()

    def _init_openai(self) -> openai.OpenAI:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found")
        return openai.OpenAI(api_key=api_key)

    def _init_google_creds(self) -> Optional[Credentials]:
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        return creds

    def _build_docs_service(self):
        return build('docs', 'v1', credentials=self.google_creds)

    def _build_drive_service(self):
        return build('drive', 'v3', credentials=self.google_creds)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def openai_request(self, prompt: str, system_role: str) -> Dict[str, Any]:
        response = await asyncio.to_thread(
            self.openai_client.chat.completions.create,
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_role},
                {"role": "user", "content": prompt}
            ]
        )
        return {"content": response.choices[0].message.content}

    async def create_doc(self, title: str, content: str) -> str:
        doc = self.docs_service.documents().create(body={"title": title}).execute()
        doc_id = doc.get("documentId")
        requests = [{
            'insertText': {
                'location': {'index': 1},
                'text': content
            }
        }]
        self.docs_service.documents().batchUpdate(
            documentId=doc_id,
            body={'requests': requests}
        ).execute()
        return doc_id