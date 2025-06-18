/**
 * Type definitions for API responses
 */

export interface StockData {
  symbol: string;
  price: number;
  change: string;
  data: StockDataPoint[];
}

export interface StockDataPoint {
  Date: string;
  Open: number;
  High: number;
  Low: number;
  Close: number;
  Volume: number;
}

export interface NewsItem {
  _id: string;
  Title: string;
  Content: string;
  Ringkasan: string;
  Date: string;
  Emiten: string;
  Link: string;
  uploaded_at: string;
}

export interface FinancialReport {
  _id?: string;
  emiten: string;
  year: number;
  quarter: string;
  reportType: string;
  total_assets?: number;
  total_liabilities?: number;
  total_equity?: number;
  revenue?: number;
  gross_profit?: number;
  operating_profit?: number;
  net_income?: number;
  eps?: number;
  ratios?: {
    roe?: number;
    roa?: number;
    der?: number;
    current_ratio?: number;
    quick_ratio?: number;
    gross_margin?: number;
    operating_margin?: number;
    net_margin?: number;
  };
}

export interface EmitenInfo {
  symbol: string;
  name: string;
  sector: string;
  marketCap: string;
  price: string;
  change: string;
}
