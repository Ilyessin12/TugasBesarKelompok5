"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import {
  Bell,
  Clock,
  Settings,
  TrendingUp,
  TrendingDown,
  ChevronDown
} from "lucide-react"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { MobileSidebar } from "@/components/sidebar" // Keep only the mobile sidebar
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"

import { StockChart } from "@/components/stock-chart"
import { NewsCard } from "@/components/news-card"
import { API } from "@/services/api"
import { StockData, NewsItem as APINewsItem, EmitenInfo } from "@/types/api"
import { RealtimeClock } from "@/components/realtime-clock"

// Definisikan tipe untuk data emiten
interface Emiten {
  symbol: string
  name: string
  sector: string
  marketCap: string
  price: string
  change: string
}

interface NewsItem {
  id: number;
  title: string;
  summary: string;
  date: string;
  source: string;
  relatedStock: string;
}

// Sample news data for different emitens
const newsDatabase: { [key: string]: NewsItem[] } = {
  "AALI.JK": [
    {
      id: 1,
      title: "AALI Raih Penghargaan Sustainability Business Integrity Index",
      summary: "PT Astra Agro Lestari Tbk (AALI) menerima penghargaan Indeks Integritas Bisnis Lestari dalam kategori Sapphire dari Transparency International Indonesia.",
      date: "2 jam yang lalu",
      source: "IQ Plus",
      relatedStock: "AALI.JK"
    },
    {
      id: 2,
      title: "Astra Agro Lestari Fokus pada Praktik Berkelanjutan",
      summary: "AALI menegaskan komitmennya dalam menerapkan praktik bisnis berkelanjutan dengan fokus pada konservasi lingkungan.",
      date: "5 jam yang lalu",
      source: "IQ Plus",
      relatedStock: "AALI.JK"
    },
    {
      id: 3,
      title: "Kinerja Q2: AALI Mencatat Peningkatan Produksi",
      summary: "PT Astra Agro Lestari Tbk melaporkan peningkatan produksi kelapa sawit sebesar 8% pada kuartal kedua 2023.",
      date: "8 jam yang lalu",
      source: "IQ Plus",
      relatedStock: "AALI.JK"
    }
  ],
  "BBCA.JK": [
    {
      id: 1,
      title: "BCA Catat Pertumbuhan Laba 7% di Q2 2023",
      summary: "Bank Central Asia (BBCA) mencatatkan pertumbuhan laba bersih sebesar 7% YoY pada kuartal kedua 2023.",
      date: "2 jam yang lalu",
      source: "IQ Plus",
      relatedStock: "BBCA.JK"
    },
    {
      id: 2,
      title: "BCA Digital Perluas Layanan WEALTH",
      summary: "BCA mengembangkan layanan wealth management digital untuk memperluas akses nasabah ke produk investasi.",
      date: "5 jam yang lalu",
      source: "IQ Plus",
      relatedStock: "BBCA.JK"
    },
    {
      id: 3,
      title: "BCA Tingkatkan Infrastruktur Digital Banking",
      summary: "Bank BCA terus memperkuat infrastruktur digital banking untuk mengantisipasi peningkatan transaksi digital.",
      date: "8 jam yang lalu",
      source: "IQ Plus",
      relatedStock: "BBCA.JK"
    }
  ]
}

// Add static financial data
const staticFinancialData = {
  ADRO: {
    EntityName: "Alamtri Resources Indonesia Tbk",
    EntityCode: "ADRO",
    Assets: 10472711000,
    ProfitLoss: 1854878000,
    EquityAttributableToEquityOwnersOfParentEntity: 6772664000,
    CashAndCashEquivalents: 3311232000,
    ShortTermBankLoans: 0,
    LongTermBankLoans: 404361000,
    SalesAndRevenue: 1084004000,
    GrossProfit: 867681000,
    ProfitFromOperation: 0,
    NetCashFlowOp: 1152758000,
    NetCashFlowInv: -582426000,
    NetCashFlowFin: -1333690000,
    CurrentAssets: 5000000000,
    NonCurrentAssets: 5472711000,
    CurrentLiabilities: 2000000000,
    NonCurrentLiabilities: 204361000,
    ShareCapital: 3000000000,
    RetainedEarnings: 3772664000,
    TotalEquity: 6772664000,

    // Derived calculations
    get TotalLiabilities() {
      return this.Assets - this.EquityAttributableToEquityOwnersOfParentEntity;
    },
    get ROE() {
      return ((this.ProfitLoss / this.EquityAttributableToEquityOwnersOfParentEntity) * 100).toFixed(2);
    },
    get DebtToEquity() {
      return (this.TotalLiabilities / this.EquityAttributableToEquityOwnersOfParentEntity).toFixed(2);
    },
    get OtherAssets() {
      return this.Assets - this.CashAndCashEquivalents;
    },
    get TotalCashFlow() {
      return this.NetCashFlowOp + this.NetCashFlowInv + this.NetCashFlowFin;
    },
    financial: {
      balance: [
        { metric: "Total Aset", value: 10472711000 },
        { metric: "Kas & Setara Kas", value: 3311232000 },
        { metric: "Pinjaman Jangka Pendek", value: 0 },
        { metric: "Pinjaman Jangka Panjang", value: 404361000 },
        { metric: "Ekuitas Pemilik", value: 6772664000 }
      ],
      cashflow: [
        { metric: "Arus Kas dari Operasi", value: 1152758000 },
        { metric: "Arus Kas dari Investasi", value: -582426000 },
        { metric: "Arus Kas dari Pendanaan", value: -1333690000 }
      ],
      ratios: [
        { 
          metric: "Net Profit Margin", 
          value: (1854878000 / 1084004000 * 100).toFixed(2),
          suffix: "%" 
        },
        { 
          metric: "Gross Profit Margin", 
          value: (867681000 / 1084004000 * 100).toFixed(2),
          suffix: "%" 
        },
        { 
          metric: "Return on Assets", 
          value: (1854878000 / 10472711000 * 100).toFixed(2),
          suffix: "%" 
        },
        { 
          metric: "Debt to Equity Ratio", 
          value: ((0 + 404361000) / 6772664000).toFixed(2),
          suffix: "x" 
        }
      ]
    }
  }
}

export default function DashboardPage() {
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedEmiten, setSelectedEmiten] = useState("AALI.JK")
  const [emitenList, setEmitenList] = useState<Emiten[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [timePeriod, setTimePeriod] = useState("3D") // Default to 3 days
  const [reportType, setReportType] = useState<"quarterly" | "annual">("quarterly") // Add for financial reports

  // Add this state:
  const [newsItems, setNewsItems] = useState<Array<any>>([])
  const [newsLoading, setNewsLoading] = useState(true)
  const [newsError, setNewsError] = useState<string | null>(null)

  // Add this state for tracking selected year
  const [selectedYear, setSelectedYear] = useState("2024") // Default to current year

  // Add these state variables to your DashboardPage component

  // Financial data state
  const [financialData, setFinancialData] = useState<any>(null);
  const [financialLoading, setFinancialLoading] = useState(true);
  const [financialError, setFinancialError] = useState<string | null>(null);

  // Add this function to convert UI period strings to API period values
  const mapPeriodToApiValue = (period: string): string => {
    switch(period) {
      case "3D": return "3days";
      case "1W": return "1week";
      case "1M": return "1month";
      case "3M": return "3month";
      case "6M": return "6m";
      case "1Y": return "1y";
      case "3Y": return "3y";
      case "5Y": return "5y";
      case "ALL": return "all";
      default: return "1month";
    }
  }

  // Add this function to handle search
  const handleSearch = (query: string) => {
    if (!query) return

    // Convert to uppercase and add .JK if not present
    let formattedQuery = query.toUpperCase()
    if (!formattedQuery.endsWith('.JK')) {
      formattedQuery += '.JK'
    }

    // Update selected emiten
    setSelectedEmiten(formattedQuery)
  }
  
  // Handler for chart data updates
  const handleChartDataUpdate = (data: StockData | null) => {
    setIsLoading(false)
    
    if (!data) {
      setEmitenList([{
        symbol: "No Data",
        name: "No Data",
        sector: "No Data",
        marketCap: "No Data",
        price: "No Data",
        change: "No Data"
      }])
      return
    }

    const updatedEmitenData = {
      symbol: data.symbol,
      name: data.symbol?.replace('.JK', ''),
      sector: "Loading...", 
      marketCap: "Loading...", 
      price: data.price ? `Rp ${data.price.toLocaleString("id-ID")}` : "No Data",
      change: data.change || "0%" // Menggunakan change dari API
    }

    setEmitenList([updatedEmitenData])
  }

  // Modified handler to do additional work if needed when period changes
  const handlePeriodChange = (period: string) => {
    setTimePeriod(period)
    // The StockChart will re-fetch data automatically due to the period dependency
  }

  // Default emiten data with loading/no data states
  const selectedEmitenData = emitenList.find(e => e.symbol === selectedEmiten) || {
    symbol: selectedEmiten,
    name: isLoading ? "Loading..." : "No Data",
    sector: isLoading ? "Loading..." : "No Data",
    marketCap: isLoading ? "Loading..." : "No Data",
    price: isLoading ? "Loading..." : "No Data",
    change: isLoading ? "Loading..." : "No Data"
  }

  // Add this useEffect to fetch news when emiten changes
  useEffect(() => {
    const fetchNews = async () => {
      setNewsLoading(true);
      setNewsError(null);
      
      try {
        const emitenCode = selectedEmiten.replace('.JK', '');
        const response = await API.getNewsData(emitenCode, 3, 0); // Limit to 3 news items
        
        // Check response format
        if (response && typeof response === 'object' && response.message && !Array.isArray(response)) {
          // This is a "no data" response with a message from the API
          console.log(`News API message: ${response.message}`);
          setNewsItems([]);
        } else if (Array.isArray(response)) {
          // Valid data array returned
          console.log(`Received ${response.length} news items`);
          setNewsItems(response);
        } else {
          // Unexpected response format
          console.error("Unexpected API response format:", response);
          setNewsItems([]);
        }
      } catch (error: any) {
        // This is a technical error (network, server down, etc.)
        console.error("Error fetching news:", error);
        setNewsError(error?.message || "Failed to load news");
      } finally {
        setNewsLoading(false);
      }
    };
    
    if (selectedEmiten) {
      fetchNews();
    }
  }, [selectedEmiten])

  // Add this useEffect to fetch financial data when emiten or year changes
  useEffect(() => {
    const fetchFinancialData = async () => {
      setFinancialLoading(true);
      setFinancialError(null);
      
      try {
        const emitenCode = selectedEmiten.replace('.JK', '');
        const response = await API.getFinancialData(emitenCode, selectedYear);
        
        console.log("Financial API response:", response);
        
        // Check if response is an error message but didn't throw an exception
        if (response && typeof response === 'object') {
          if (response.error || response.message) {
            // API returned an error message in a successful response
            console.log("No financial data available:", response.message || response.error);
            setFinancialData(null); // Treat as no data case
          } else if (!response.Assets && !response.SalesAndRevenue) {
            // Response doesn't have expected financial data fields
            console.log("Invalid financial data format");
            setFinancialData(null); // Treat as no data case
          } else {
            // Valid financial data
            setFinancialData(response);
          }
        } else {
          // Unexpected response format
          console.error("Unexpected API response format:", response);
          setFinancialData(null);
        }
      } catch (error: any) {
        // Technical API error (network issues, server down, etc)
        console.error("Error fetching financial data:", error);
        setFinancialError(error?.message || "Failed to load financial data");
      } finally {
        setFinancialLoading(false);
      }
    };
    
    fetchFinancialData();
  }, [selectedEmiten, selectedYear]);

  // Add this helper function to format large numbers as T (trillion), B (billion), or M (million)
  const formatCurrency = (value: number | null | undefined) => {
    if (value === null || value === undefined) return "N/A";
    
    // Convert to absolute value for formatting
    const absValue = Math.abs(value);
    
    if (absValue >= 1e12) {
      return `Rp ${(value / 1e12).toFixed(2)}T`;
    } else if (absValue >= 1e9) {
      return `Rp ${(value / 1e9).toFixed(2)}T`;
    } else if (absValue >= 1e6) {
      return `Rp ${(value / 1e6).toFixed(2)}M`;
    } else {
      return `Rp ${value.toLocaleString("id-ID")}`;
    }
  };

  // Add this helper function to format percentage values
  const formatPercentage = (value: number | null | undefined) => {
    if (value === null || value === undefined) return "N/A";
    return `${(value * 100).toFixed(2)}%`;
  };

  if (error) {
    return <div className="h-screen flex items-center justify-center text-red-400">Error: {error}</div>
  }

  return (
    // Changed the layout to remove sidebar
    <div className="min-h-screen bg-[#0f172a]">
      <div className="flex flex-col w-full">
        <header className="sticky top-0 z-10 flex h-16 items-center justify-between border-b border-[#1e293b] bg-[#0f172a]/80 px-4 backdrop-blur-sm md:px-6">
          <div className="flex items-center gap-4">
            <MobileSidebar 
              searchQuery={searchQuery}
              onSearchChange={setSearchQuery}
              onSearch={handleSearch}
            />
            <div className="flex items-center gap-2">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="h-6 w-6 text-indigo-500"
              >
                <path d="M3 3v18h18" />
                <path d="m19 9-5 5-4-4-3 3" />
              </svg>
              <h1 className="text-xl font-semibold text-white">SahamSederhana</h1>
            </div>
          </div>
          
          {/* New search box and clock container */}
          <div className="flex items-center gap-4">
            {/* Emiten search box */}
            <div className="relative hidden md:block">
              <div className="absolute inset-y-0 left-0 flex items-center pl-3">
                <svg 
                  xmlns="http://www.w3.org/2000/svg" 
                  className="h-4 w-4 text-slate-400" 
                  fill="none" 
                  viewBox="0 0 24 24" 
                  stroke="currentColor"
                >
                  <path 
                    strokeLinecap="round" 
                    strokeLinejoin="round" 
                    strokeWidth={2} 
                    d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" 
                  />
                </svg>
              </div>
              <form 
                onSubmit={(e) => {
                  e.preventDefault();
                  handleSearch(searchQuery);
                }}
              >
                <input 
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Cari emiten..."
                  className="h-9 w-64 rounded-md border border-[#1e293b] bg-[#1e293b]/50 py-2 pl-10 pr-4 text-sm text-white placeholder-slate-400 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                />
              </form>
            </div>
            
            {/* Clock stays on the right */}
            <RealtimeClock />
          </div>
        </header>

        <div className="p-4 md:p-6">
          <div className="mb-6 grid grid-cols-1 gap-6 lg:grid-cols-3">
            <Card className="overflow-hidden border-[#1e293b] bg-[#0f172a] shadow-lg lg:col-span-2">
              <CardHeader className="border-b border-[#1e293b] bg-[#0f172a] px-6">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="flex items-center gap-2">
                      <div className="text-lg font-semibold text-white">
                        {selectedEmitenData.symbol}
                      </div>
                      <div className="rounded-full bg-indigo-900/50 px-2 py-0.5 text-xs font-medium text-indigo-300">
                        {selectedEmitenData.sector}
                      </div>
                    </div>
                    <CardDescription className="text-slate-400">
                      IDX: {selectedEmitenData.symbol}
                    </CardDescription>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold text-white">
                      {selectedEmitenData.price}
                    </div>
                    <div className={`flex items-center justify-end gap-1 text-sm font-medium ${
                      selectedEmitenData.change.startsWith('+') ? 'text-emerald-400' : 'text-red-400'
                    }`}>
                      {selectedEmitenData.change.startsWith('+') ? (
                        <TrendingUp className="h-4 w-4" />
                      ) : (
                        <TrendingDown className="h-4 w-4" />
                      )}
                      {selectedEmitenData.change}
                    </div>
                  </div>
                </div>
              </CardHeader>
              <div className="border-b border-[#1e293b] px-6 py-3">
                <div className="flex items-center gap-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    className="text-slate-400 hover:bg-[#1e293b] hover:text-white data-[active=true]:bg-[#1e293b] data-[active=true]:text-white"
                    data-active={timePeriod === "3D"}
                    onClick={() => handlePeriodChange("3D")}
                  >
                    3D
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="text-slate-400 hover:bg-[#1e293b] hover:text-white data-[active=true]:bg-[#1e293b] data-[active=true]:text-white"
                    data-active={timePeriod === "1W"}
                    onClick={() => handlePeriodChange("1W")}
                  >
                    1W
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="text-slate-400 hover:bg-[#1e293b] hover:text-white data-[active=true]:bg-[#1e293b] data-[active=true]:text-white"
                    data-active={timePeriod === "1M"}
                    onClick={() => handlePeriodChange("1M")}
                  >
                    1M
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="text-slate-400 hover:bg-[#1e293b] hover:text-white data-[active=true]:bg-[#1e293b] data-[active=true]:text-white"
                    data-active={timePeriod === "3M"}
                    onClick={() => handlePeriodChange("3M")}
                  >
                    3M
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="text-slate-400 hover:bg-[#1e293b] hover:text-white data-[active=true]:bg-[#1e293b] data-[active=true]:text-white"
                    data-active={timePeriod === "1Y"}
                    onClick={() => handlePeriodChange("1Y")}
                  >
                    1Y
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="text-slate-400 hover:bg-[#1e293b] hover:text-white data-[active=true]:bg-[#1e293b] data-[active=true]:text-white"
                    data-active={timePeriod === "ALL"}
                    onClick={() => handlePeriodChange("ALL")}
                  >
                    ALL
                  </Button>
                </div>
              </div>
              <CardContent className="p-0">
                <div className="border-b border-[#1e293b] px-6 py-4">
                  <StockChart 
                    darkMode={true} 
                    emiten={selectedEmiten} 
                    period={mapPeriodToApiValue(timePeriod)}
                    onDataUpdate={handleChartDataUpdate}
                  />
                </div>
              </CardContent>
            </Card>

            <div className="grid gap-6">
              <Card className="border-[#1e293b] bg-[#0f172a] shadow-lg">
                <CardHeader className="border-b border-[#1e293b] px-6 pb-3 pt-4">
                  <CardTitle className="text-base text-white">Berita Terkini</CardTitle>
                </CardHeader>
                <CardContent className="p-0">
                  {/* Replace the news display section with this improved version */}
                  <div className="divide-y divide-[#1e293b]">
                    {newsLoading ? (
                      <div className="flex items-center justify-center p-6">
                        <div className="h-6 w-6 animate-spin rounded-full border-2 border-t-transparent border-indigo-500"></div>
                        <span className="ml-3 text-slate-300">Memuat berita...</span>
                      </div>
                    ) : newsError ? (
                      // Technical API error
                      <div className="flex items-center justify-center p-6">
                        <div className="flex flex-col items-center text-center">
                          <svg 
                            xmlns="http://www.w3.org/2000/svg" 
                            className="h-6 w-6 text-red-400 mb-2" 
                            fill="none" 
                            viewBox="0 0 24 24" 
                            stroke="currentColor"
                          >
                            <path 
                              strokeLinecap="round" 
                              strokeLinejoin="round" 
                              strokeWidth={2} 
                              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" 
                            />
                          </svg>
                          <p className="text-red-400 text-sm">{newsError}</p>
                        </div>
                      </div>
                    ) : newsItems.length > 0 ? (
                      newsItems.slice(0, 3).map((news, index) => (
                        <div key={news._id || index} className="p-4">
                          <div className="mb-2">
                            <h3 className="line-clamp-2 font-medium text-white">
                              {news.Title || "No Title"}
                            </h3>
                          </div>
                          <p className="line-clamp-3 mb-3 text-sm text-slate-400">
                            {news.Ringkasan || "No summary available"}
                          </p>
                          <div className="flex items-center justify-between">
                            <span className="text-xs text-slate-500">
                              {news.Date || "N/A"}
                            </span>
                            <a 
                              href={news.Link} 
                              target="_blank" 
                              rel="noopener noreferrer"
                              className="text-xs text-indigo-400 hover:text-indigo-300"
                            >
                              {news.Link ? "Baca di Sumber" : "Tidak ada link"}
                            </a>
                          </div>
                        </div>
                      ))
                    ) : (
                      // Empty data (API worked but no news found)
                      <div className="flex items-center justify-center p-6">
                        <div className="flex flex-col items-center text-center">
                          <svg 
                            xmlns="http://www.w3.org/2000/svg" 
                            className="h-6 w-6 text-slate-400 mb-2" 
                            fill="none" 
                            viewBox="0 0 24 24" 
                            stroke="currentColor"
                          >
                            <path 
                              strokeLinecap="round" 
                              strokeLinejoin="round" 
                              strokeWidth={2} 
                              d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" 
                            />
                          </svg>
                          <p className="text-slate-400 text-sm">Tidak ada berita terkini untuk emiten {selectedEmiten.replace('.JK', '')}</p>
                        </div>
                      </div>
                    )}
                  </div>
                  <div className="border-t border-[#1e293b] p-3">
                    <Link 
                      href={`/berita?emiten=${selectedEmiten.replace('.JK', '')}`}
                      className="block w-full"
                    >
                      <Button 
                        variant="ghost" 
                        className="w-full justify-between text-sm text-slate-400 hover:text-white"
                      >
                        Lihat semua berita {selectedEmiten.replace('.JK', '')}
                        <ChevronDown className="h-4 w-4" />
                      </Button>
                    </Link>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>

          {/* Financial report section - two-column layout */}
          <Card className="border-[#1e293b] bg-[#0f172a] shadow-lg mt-8">
            <CardHeader className="border-b border-[#1e293b] px-6">
              <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-3 md:space-y-0">
                <CardTitle className="text-white">Laporan Keuangan</CardTitle>
                <div className="flex items-center gap-2">
                  <span className="text-sm text-slate-400">Pilih tahun:</span>
                  <Select 
                    value={selectedYear} 
                    onValueChange={setSelectedYear}
                  >
                    <SelectTrigger className="h-8 w-[100px] border-[#1e293b] bg-[#1e293b] text-slate-300">
                      <SelectValue placeholder="Tahun" />
                    </SelectTrigger>
                    <SelectContent className="border-[#1e293b] bg-[#0f172a] text-slate-300">
                      <SelectItem value="2024">2024</SelectItem>
                      <SelectItem value="2023">2023</SelectItem>
                      <SelectItem value="2022">2022</SelectItem>
                      <SelectItem value="2021">2021</SelectItem>
                      <SelectItem value="2020">2020</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardHeader>
            <CardContent className="p-6">
              {financialLoading ? (
                <div className="flex items-center justify-center p-10">
                  <div className="h-8 w-8 animate-spin rounded-full border-2 border-t-transparent border-indigo-500"></div>
                  <span className="ml-3 text-slate-300">Memuat data keuangan...</span>
                </div>
              ) : financialError ? (
                <div className="flex flex-col items-center justify-center p-10 text-center">
                  <svg 
                    xmlns="http://www.w3.org/2000/svg" 
                    className="h-10 w-10 text-red-400 mb-4" 
                    fill="none" 
                    viewBox="0 0 24 24" 
                    stroke="currentColor"
                  >
                    <path 
                      strokeLinecap="round" 
                      strokeLinejoin="round" 
                      strokeWidth={2} 
                      d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" 
                    />
                  </svg>
                  <p className="text-red-400 mb-2">{financialError}</p>
                  <p className="text-sm text-slate-400">Coba pilih tahun yang berbeda</p>
                </div>
              ) : !financialData ? (
                <div className="flex flex-col items-center justify-center p-10 text-center">
                  <p className="text-slate-400">Tidak ada data keuangan tersedia untuk {selectedEmiten.replace('.JK', '')} tahun {selectedYear}</p>
                </div>
              ) : (
                <>
                  {/* Two-column table layout */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Left column table */}
                    <div>
                      <Table>
                        <TableHeader>
                          <TableRow className="border-[#1e293b] hover:bg-transparent">
                            <TableHead className="w-[180px] bg-[#1e293b] text-slate-300">Metrik</TableHead>
                            <TableHead className="bg-[#1e293b] text-slate-300">Nilai</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          <TableRow className="border-[#1e293b] hover:bg-[#1e293b]/50">
                            <TableCell className="font-medium text-white">Pendapatan</TableCell>
                            <TableCell className="text-slate-300">
                              {formatCurrency(financialData.SalesAndRevenue)}
                            </TableCell>
                          </TableRow>
                          <TableRow className="border-[#1e293b] hover:bg-[#1e293b]/50">
                            <TableCell className="font-medium text-white">Laba Kotor</TableCell>
                            <TableCell className="text-slate-300">
                              {formatCurrency(financialData.GrossProfit)}
                            </TableCell>
                          </TableRow>
                          <TableRow className="border-[#1e293b] hover:bg-[#1e293b]/50">
                            <TableCell className="font-medium text-white">Laba Operasi</TableCell>
                            <TableCell className="text-slate-300">
                              {formatCurrency(financialData.ProfitFromOperation)}
                            </TableCell>
                          </TableRow>
                          <TableRow className="border-[#1e293b] hover:bg-[#1e293b]/50">
                            <TableCell className="font-medium text-white">Laba Bersih</TableCell>
                            <TableCell className="text-slate-300">
                              {formatCurrency(financialData.ProfitLoss)}
                            </TableCell>
                          </TableRow>
                          <TableRow className="border-[#1e293b] hover:bg-[#1e293b]/50">
                            <TableCell className="font-medium text-white">Kas</TableCell>
                            <TableCell className="text-slate-300">
                              {formatCurrency(financialData.CashAndCashEquivalents)}
                            </TableCell>
                          </TableRow>
                          <TableRow className="border-[#1e293b] hover:bg-[#1e293b]/50">
                            <TableCell className="font-medium text-white">Total Aset</TableCell>
                            <TableCell className="text-slate-300">
                              {formatCurrency(financialData.Assets)}
                            </TableCell>
                          </TableRow>
                        </TableBody>
                      </Table>
                    </div>

                    {/* Right column table */}
                    <div>
                      <Table>
                        <TableHeader>
                          <TableRow className="border-[#1e293b] hover:bg-transparent">
                            <TableHead className="w-[180px] bg-[#1e293b] text-slate-300">Metrik</TableHead>
                            <TableHead className="bg-[#1e293b] text-slate-300">Nilai</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          <TableRow className="border-[#1e293b] hover:bg-[#1e293b]/50">
                            <TableCell className="font-medium text-white">Pinjaman Jangka Pendek</TableCell>
                            <TableCell className="text-slate-300">
                              {formatCurrency(financialData.ShortTermBankLoans)}
                            </TableCell>
                          </TableRow>
                          <TableRow className="border-[#1e293b] hover:bg-[#1e293b]/50">
                            <TableCell className="font-medium text-white">Pinjaman Jangka Panjang</TableCell>
                            <TableCell className="text-slate-300">
                              {formatCurrency(financialData.LongTermBankLoans)}
                            </TableCell>
                          </TableRow>
                          <TableRow className="border-[#1e293b] hover:bg-[#1e293b]/50">
                            <TableCell className="font-medium text-white">Total Ekuitas</TableCell>
                            <TableCell className="text-slate-300">
                              {formatCurrency(financialData.EquityAttributableToEquityOwnersOfParentEntity)}
                            </TableCell>
                          </TableRow>
                          <TableRow className="border-[#1e293b] hover:bg-[#1e293b]/50">
                            <TableCell className="font-medium text-white">Arus Kas Operasi</TableCell>
                            <TableCell className="text-slate-300">
                              {formatCurrency(financialData.NetCashFlowOp)}
                            </TableCell>
                          </TableRow>
                          <TableRow className="border-[#1e293b] hover:bg-[#1e293b]/50">
                            <TableCell className="font-medium text-white">Arus Kas Investasi</TableCell>
                            <TableCell className="text-slate-300">
                              {formatCurrency(financialData.NetCashFlowInv)}
                            </TableCell>
                          </TableRow>
                          <TableRow className="border-[#1e293b] hover:bg-[#1e293b]/50">
                            <TableCell className="font-medium text-white">Arus Kas Pendanaan</TableCell>
                            <TableCell className="text-slate-300">
                              {formatCurrency(financialData.NetCashFlowFin)}
                            </TableCell>
                          </TableRow>
                        </TableBody>
                      </Table>
                    </div>
                  </div>

                  {/* Period information */}
                  <div className="mt-4 text-sm text-slate-400 text-center">
                    <p>
                      Periode: {financialData.CurrentPeriodStartDate} - {financialData.CurrentPeriodEndDate} | 
                      Jenis Laporan: {financialData.PeriodOfFinancialStatementsSubmissions || "Annual"}
                    </p>
                  </div>
                </>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}