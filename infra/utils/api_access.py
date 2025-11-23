import aiohttp

class ApiAccess:
    @staticmethod
    async def execute_get_request_async(url: str) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise Exception(f"Error: Received status code {response.status} for GET request to {url}")
                return await response.json()
