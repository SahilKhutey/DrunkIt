# FACCP Python SDK

Official Python SDK for integration with FACCP platform services.

## Quickstart

```python
import asyncio
from faccp_sdk import FACCPClient

async def main():
    client = FACCPClient(base_url="http://localhost:8000")
    products = await client.get_products(category="beer")
    print(f"Retrieved {len(products)} products")
    await client.close()

asyncio.run(main())
```
