import asyncio
from services.api_client import APIClient
from services.content_generator import ContentGenerator, ContentRequest

async def main():
    client = APIClient()
    generator = ContentGenerator(client)
    await generator.initialize()
    
    request = ContentRequest(
        topic=input('Enter topic: '),
        industry=input('Enter industry: '),
        expertise_areas=input('Enter expertise areas (optional): ') or None,
        personal_story=input('Enter personal story (optional): ') or None
    )
    
    result = await generator.generate_content(request)
    print(f'\nContent generated! View at: https://docs.google.com/document/d/{result["doc_id"]}/edit')

if __name__ == '__main__':
    asyncio.run(main())