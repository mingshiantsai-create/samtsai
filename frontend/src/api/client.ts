// Docker 環境下自動使用相對 URL，本地開發使用顯式配置
const API_BASE_URL = import.meta.env.VITE_API_URL ||
  (typeof window !== 'undefined' && window.location.hostname === 'localhost'
    ? "http://localhost:8000"
    : "");

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

interface BloodPressureCreateRequest {
  systolic: number;
  diastolic: number;
  pulse?: number;
  measurement_time: string;
  notes?: string;
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

  async createBloodPressure(data: BloodPressureCreateRequest): Promise<Response> {
    return fetch(`${this.baseUrl}/api/blood-pressure`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
  }

  async getBloodPressureRecords(limit: number = 50, offset: number = 0): Promise<any> {
    return this.fetch(`/api/blood-pressure?limit=${limit}&offset=${offset}`);
  }

  async getBloodPressureRecord(id: number): Promise<any> {
    return this.fetch(`/api/blood-pressure/${id}`);
  }

  async deleteBloodPressureRecord(id: number): Promise<any> {
    return this.fetch(`/api/blood-pressure/${id}`, {
      method: 'DELETE',
    });
  }
}

export const api = new ChipAnalysisClient();
export const chipClient = api;
