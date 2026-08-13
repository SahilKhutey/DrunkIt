# FACCP TypeScript SDK

Official TypeScript / JavaScript SDK for integrating with FACCP platform services.

## Usage

```typescript
import { FACCPClient } from "@faccp/sdk-typescript";

const client = new FACCPClient("http://localhost:8000");
const products = await client.getProducts("beer");
console.log(products);
```
