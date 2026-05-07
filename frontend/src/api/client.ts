const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

interface StockData {
  symbol: string;
  name: string;
  market: string;
}

interface ChipData {
  date: string;
  close_price: number;
  volume: number;
  foreign_investors_change?: number;
  investment_trust_change?: number;
  margin_change?: number;
}

class ChipAnalysisClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async fetch<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      headers: {
        "Content-Type": "application/json",
      },
      ...options,
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }

    return response.json();
  }

  async getStocks(): Promise<StockData[]> {
    const data = await this.fetch<{ data: StockData[] }>("/api/stocks");
    return data.data;
  }

  async searchStocks(q: string): Promise<StockData[]> {
    const data = await this.fetch<{ data: StockData[] }>(`/api/stocks/search?q=${q}`);
    return data.data;
  }

  async getStockDetail(symbol: string): Promise<StockData> {
    return this.fetch(`/api/stocks/${symbol}`);
  }

  async getChipAnalysis(symbol: string, days: number = 30): Promise<ChipData[]> {
    const data = await this.fetch<{
      symbol: string;
      days: number;
      data: ChipData[];
    }>(`/api/stocks/${symbol}/chip?days=${days}`);
    return data.data;
  }
}

export const chipClient = new ChipAnalysisClient();
