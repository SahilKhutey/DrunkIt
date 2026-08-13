import axios, { AxiosInstance } from "axios";

export class FACCPClient {
  private http: AxiosInstance;

  constructor(baseUrl: string = "http://localhost:8000", apiKey?: string) {
    this.http = axios.create({
      baseURL: baseUrl,
      headers: apiKey ? { Authorization: `Bearer ${apiKey}` } : {},
    });
  }

  async getProducts(category?: string): Promise<any[]> {
    const res = await this.http.get("/api/v1/catalog/products", { params: { category } });
    return res.data?.data || [];
  }

  async evaluatePolicy(jurisdiction: string, context: Record<string, any>): Promise<any> {
    const res = await this.http.post("/api/v1/compliance/policies/evaluate", {
      jurisdiction_code: jurisdiction,
      context,
    });
    return res.data?.data || {};
  }
}
