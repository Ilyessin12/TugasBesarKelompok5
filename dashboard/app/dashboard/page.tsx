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
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Sidebar, MobileSidebar } from "@/components/sidebar"

import { StockChart } from "@/components/stock-chart"
import { NewsCard } from "@/components/news-card"

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

export default function DashboardPage() {
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedEmiten, setSelectedEmiten] = useState("AALI.JK")
  const [emitenList, setEmitenList] = useState<Emiten[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [timePeriod, setTimePeriod] = useState("1M")
  const [reportType, setReportType] = useState<"quarterly" | "annual">("quarterly")

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
  const handleChartDataUpdate = (data: any) => {
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

  const handlePeriodChange = (period: string) => {
    setTimePeriod(period)
    // You can add logic here to fetch new data based on the selected period
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

  if (error) {
    return <div className="h-screen flex items-center justify-center text-red-400">Error: {error}</div>
  }

  return (
    <div className="flex min-h-screen bg-[#0f172a]">
      <Sidebar 
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        onSearch={handleSearch}
      />
      
      <div className="flex-1">
        <header className="sticky top-0 z-10 flex h-16 items-center justify-between border-b border-[#1e293b] bg-[#0f172a]/80 px-4 backdrop-blur-sm md:px-6">
          <div className="flex items-center gap-4">
            <MobileSidebar 
              searchQuery={searchQuery}
              onSearchChange={setSearchQuery}
              onSearch={handleSearch}
            />
            <h1 className="text-xl font-semibold text-white">Dashboard</h1>
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
                      {/* | Market Cap: {selectedEmitenData.marketCap} */}
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
                    data-active={timePeriod === "1D"}
                    onClick={() => handlePeriodChange("1D")}
                  >
                    1D
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
                  <div className="divide-y divide-[#1e293b]">
                    {(newsDatabase[selectedEmiten] || []).slice(0, 3).map((news) => (
                      <NewsCard
                        key={news.id}
                        title={news.title}
                        summary={news.summary}
                        date={news.date}
                        source={news.source}
                        darkMode={true}
                      />
                    ))}
                    {!newsDatabase[selectedEmiten] && (
                      <div className="flex items-center justify-center p-6 text-slate-400">
                        Tidak ada berita terkini untuk emiten ini
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
                        Lihat semua berita {selectedEmitenData.symbol.replace('.JK', '')}
                        <ChevronDown className="h-4 w-4" />
                      </Button>
                    </Link>
                  </div>
                </CardContent>
              </Card>

            </div>
          </div>

          <Card className="border-[#1e293b] bg-[#0f172a] shadow-lg">
            <CardHeader className="border-b border-[#1e293b] px-6 pb-3 pt-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <CardTitle className="text-white">Laporan Keuangan</CardTitle>
                  <div className="flex items-center gap-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-8 text-slate-400 hover:bg-[#1e293b] hover:text-white data-[active=true]:bg-[#1e293b] data-[active=true]:text-white"
                      data-active={reportType === "quarterly"}
                      onClick={() => setReportType("quarterly")}
                    >
                      Quartal
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-8 text-slate-400 hover:bg-[#1e293b] hover:text-white data-[active=true]:bg-[#1e293b] data-[active=true]:text-white"
                      data-active={reportType === "annual"}
                      onClick={() => setReportType("annual")}
                    >
                      Tahunan
                    </Button>
                  </div>
                </div>
                {reportType === "quarterly" && (
                  <div className="flex items-center gap-2">
                    <Select defaultValue="2023">
                      <SelectTrigger className="h-8 w-[180px] border-[#1e293b] bg-[#1e293b] text-slate-300">
                        <SelectValue placeholder="Pilih Periode" />
                      </SelectTrigger>
                      <SelectContent className="border-[#1e293b] bg-[#0f172a] text-slate-300">
                        <SelectItem value="2023">2023</SelectItem>
                        <SelectItem value="2022">2022</SelectItem>
                        <SelectItem value="2021">2021</SelectItem>
                        <SelectItem value="2020">2020</SelectItem>
                        <SelectItem value="2019">2019</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                )}
              </div>
            </CardHeader>
            <CardContent className="p-0">
              <Tabs defaultValue="overview" className="w-full">
                <div className="border-b border-[#1e293b] px-6">
                  <TabsList className="h-12 w-full justify-start gap-6 bg-transparent p-0">
                    <TabsTrigger
                      value="overview"
                      className="h-12 border-b-2 border-transparent text-slate-400 data-[state=active]:border-indigo-500 data-[state=active]:bg-transparent data-[state=active]:text-white data-[state=active]:shadow-none"
                    >
                      Ikhtisar
                    </TabsTrigger>
                    <TabsTrigger
                      value="income"
                      className="h-12 border-b-2 border-transparent text-slate-400 data-[state=active]:border-indigo-500 data-[state=active]:bg-transparent data-[state=active]:text-white data-[state=active]:shadow-none"
                    >
                      Laba Rugi
                    </TabsTrigger>
                    <TabsTrigger
                      value="balance"
                      className="h-12 border-b-2 border-transparent text-slate-400 data-[state=active]:border-indigo-500 data-[state=active]:bg-transparent data-[state=active]:text-white data-[state=active]:shadow-none"
                    >
                      Neraca
                    </TabsTrigger>
                    <TabsTrigger
                      value="cashflow"
                      className="h-12 border-b-2 border-transparent text-slate-400 data-[state=active]:border-indigo-500 data-[state=active]:bg-transparent data-[state=active]:text-white data-[state=active]:shadow-none"
                    >
                      Arus Kas
                    </TabsTrigger>
                  </TabsList>
                </div>
                <TabsContent value="overview" className="m-0 p-6">
                  <Table>
                    <TableHeader>
                      <TableRow className="border-[#1e293b] hover:bg-transparent">
                        <TableHead className="w-[250px] bg-[#1e293b] text-slate-300">Metrik</TableHead>
                        {reportType === "quarterly" ? (
                          <>
                            <TableHead className="bg-[#1e293b] text-slate-300">Q4</TableHead>
                            <TableHead className="bg-[#1e293b] text-slate-300">Q3</TableHead>
                            <TableHead className="bg-[#1e293b] text-slate-300">Q2</TableHead>
                            <TableHead className="bg-[#1e293b] text-slate-300">Q1</TableHead>
                          </>
                        ) : (
                          <>
                            <TableHead className="bg-[#1e293b] text-slate-300">2023</TableHead>
                            <TableHead className="bg-[#1e293b] text-slate-300">2022</TableHead>
                            <TableHead className="bg-[#1e293b] text-slate-300">2021</TableHead>
                            <TableHead className="bg-[#1e293b] text-slate-300">2020</TableHead>
                            <TableHead className="bg-[#1e293b] text-slate-300">2019</TableHead>
                          </>
                        )}
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      <TableRow className="border-[#1e293b] hover:bg-[#1e293b]/50">
                        <TableCell className="font-medium text-white">Pendapatan</TableCell>
                        {reportType === "quarterly" ? (
                          <>
                            <TableCell className="text-slate-300">Rp 27.3T</TableCell>
                            <TableCell className="text-slate-300">Rp 26.1T</TableCell>
                            <TableCell className="text-slate-300">Rp 25.7T</TableCell>
                            <TableCell className="text-slate-300">Rp 24.2T</TableCell>
                          </>
                        ) : (
                          <>
                            <TableCell className="text-slate-300">Rp 103.3T</TableCell>
                            <TableCell className="text-slate-300">Rp 97.2T</TableCell>
                            <TableCell className="text-slate-300">Rp 92.5T</TableCell>
                            <TableCell className="text-slate-300">Rp 88.1T</TableCell>
                            <TableCell className="text-slate-300">Rp 84.2T</TableCell>
                          </>
                        )}
                      </TableRow>
                      <TableRow className="border-[#1e293b] hover:bg-[#1e293b]/50">
                        <TableCell className="font-medium text-white">Laba Kotor</TableCell>
                        {reportType === "quarterly" ? (
                          <>
                            <TableCell className="text-slate-300">Rp 19.5T</TableCell>
                            <TableCell className="text-slate-300">Rp 18.9T</TableCell>
                            <TableCell className="text-slate-300">Rp 18.3T</TableCell>
                            <TableCell className="text-slate-300">Rp 17.1T</TableCell>
                          </>
                        ) : (
                          <>
                            <TableCell className="text-slate-300">Rp 73.8T</TableCell>
                            <TableCell className="text-slate-300">Rp 69.0T</TableCell>
                            <TableCell className="text-slate-300">Rp 65.2T</TableCell>
                            <TableCell className="text-slate-300">Rp 61.8T</TableCell>
                            <TableCell className="text-slate-300">Rp 58.9T</TableCell>
                          </>
                        )}
                      </TableRow>
                      <TableRow className="border-[#1e293b] hover:bg-[#1e293b]/50">
                        <TableCell className="font-medium text-white">Laba Bersih</TableCell>
                        {reportType === "quarterly" ? (
                          <>
                            <TableCell className="text-slate-300">Rp 11.2T</TableCell>
                            <TableCell className="text-slate-300">Rp 10.8T</TableCell>
                            <TableCell className="text-slate-300">Rp 10.5T</TableCell>
                            <TableCell className="text-slate-300">Rp 9.8T</TableCell>
                          </>
                        ) : (
                          <>
                            <TableCell className="text-slate-300">Rp 42.3T</TableCell>
                            <TableCell className="text-slate-300">Rp 39.5T</TableCell>
                            <TableCell className="text-slate-300">Rp 37.2T</TableCell>
                            <TableCell className="text-slate-300">Rp 35.1T</TableCell>
                            <TableCell className="text-slate-300">Rp 33.4T</TableCell>
                          </>
                        )}
                      </TableRow>
                      <TableRow className="border-[#1e293b] hover:bg-[#1e293b]/50">
                        <TableCell className="font-medium text-white">EPS</TableCell>
                        {reportType === "quarterly" ? (
                          <>
                            <TableCell className="text-slate-300">Rp 455</TableCell>
                            <TableCell className="text-slate-300">Rp 440</TableCell>
                            <TableCell className="text-slate-300">Rp 425</TableCell>
                            <TableCell className="text-slate-300">Rp 398</TableCell>
                          </>
                        ) : (
                          <>
                            <TableCell className="text-slate-300">Rp 1,718</TableCell>
                            <TableCell className="text-slate-300">Rp 1,608</TableCell>
                            <TableCell className="text-slate-300">Rp 1,512</TableCell>
                            <TableCell className="text-slate-300">Rp 1,423</TableCell>
                            <TableCell className="text-slate-300">Rp 1,342</TableCell>
                          </>
                        )}
                      </TableRow>
                      <TableRow className="border-[#1e293b] hover:bg-[#1e293b]/50">
                        <TableCell className="font-medium text-white">ROE</TableCell>
                        {reportType === "quarterly" ? (
                          <>
                            <TableCell className="text-slate-300">20.5%</TableCell>
                            <TableCell className="text-slate-300">20.1%</TableCell>
                            <TableCell className="text-slate-300">19.8%</TableCell>
                            <TableCell className="text-slate-300">19.2%</TableCell>
                          </>
                        ) : (
                          <>
                            <TableCell className="text-slate-300">20.5%</TableCell>
                            <TableCell className="text-slate-300">19.2%</TableCell>
                            <TableCell className="text-slate-300">18.4%</TableCell>
                            <TableCell className="text-slate-300">17.8%</TableCell>
                            <TableCell className="text-slate-300">17.2%</TableCell>
                          </>
                        )}
                      </TableRow>
                    </TableBody>
                  </Table>
                </TabsContent>
                <TabsContent value="income" className="m-0 p-6">
                  <Table>
                    <TableHeader>
                      <TableRow className="border-[#1e293b] hover:bg-transparent">
                        <TableHead className="w-[250px] bg-[#1e293b] text-slate-300">Metrik</TableHead>
                        <TableHead className="bg-[#1e293b] text-slate-300">Q2 2023</TableHead>
                        <TableHead className="bg-[#1e293b] text-slate-300">Q1 2023</TableHead>
                        <TableHead className="bg-[#1e293b] text-slate-300">YoY %</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      <TableRow className="border-[#1e293b] hover:bg-[#1e293b]/50">
                        <TableCell className="font-medium text-white">Pendapatan Bunga</TableCell>
                        <TableCell className="text-slate-300">Rp 18.2T</TableCell>
                        <TableCell className="text-slate-300">Rp 17.5T</TableCell>
                        <TableCell className="text-emerald-400">+4.0%</TableCell>
                      </TableRow>
                      <TableRow className="border-[#1e293b] hover:bg-[#1e293b]/50">
                        <TableCell className="font-medium text-white">Pendapatan Non-Bunga</TableCell>
                        <TableCell className="text-slate-300">Rp 7.5T</TableCell>
                        <TableCell className="text-slate-300">Rp 6.7T</TableCell>
                        <TableCell className="text-emerald-400">+11.9%</TableCell>
                      </TableRow>
                      <TableRow className="border-[#1e293b] hover:bg-[#1e293b]/50">
                        <TableCell className="font-medium text-white">Beban Operasional</TableCell>
                        <TableCell className="text-slate-300">Rp 9.8T</TableCell>
                        <TableCell className="text-slate-300">Rp 9.5T</TableCell>
                        <TableCell className="text-red-400">+3.2%</TableCell>
                      </TableRow>
                      <TableRow className="border-[#1e293b] hover:bg-[#1e293b]/50">
                        <TableCell className="font-medium text-white">Laba Sebelum Pajak</TableCell>
                        <TableCell className="text-slate-300">Rp 13.2T</TableCell>
                        <TableCell className="text-slate-300">Rp 12.3T</TableCell>
                        <TableCell className="text-emerald-400">+7.3%</TableCell>
                      </TableRow>
                    </TableBody>
                  </Table>
                </TabsContent>
                <TabsContent value="balance" className="m-0 p-6">
                  <Table>
                    <TableHeader>
                      <TableRow className="border-[#1e293b] hover:bg-transparent">
                        <TableHead className="w-[250px] bg-[#1e293b] text-slate-300">Metrik</TableHead>
                        <TableHead className="bg-[#1e293b] text-slate-300">Q2 2023</TableHead>
                        <TableHead className="bg-[#1e293b] text-slate-300">Q1 2023</TableHead>
                        <TableHead className="bg-[#1e293b] text-slate-300">YoY %</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      <TableRow className="border-[#1e293b] hover:bg-[#1e293b]/50">
                        <TableCell className="font-medium text-white">Total Aset</TableCell>
                        <TableCell className="text-slate-300">Rp 1,350T</TableCell>
                        <TableCell className="text-slate-300">Rp 1,320T</TableCell>
                        <TableCell className="text-emerald-400">+2.3%</TableCell>
                      </TableRow>
                      <TableRow className="border-[#1e293b] hover:bg-[#1e293b]/50">
                        <TableCell className="font-medium text-white">Kredit</TableCell>
                        <TableCell className="text-slate-300">Rp 720T</TableCell>
                        <TableCell className="text-slate-300">Rp 705T</TableCell>
                        <TableCell className="text-emerald-400">+2.1%</TableCell>
                      </TableRow>
                      <TableRow className="border-[#1e293b] hover:bg-[#1e293b]/50">
                        <TableCell className="font-medium text-white">Dana Pihak Ketiga</TableCell>
                        <TableCell className="text-slate-300">Rp 980T</TableCell>
                        <TableCell className="text-slate-300">Rp 965T</TableCell>
                        <TableCell className="text-emerald-400">+1.6%</TableCell>
                      </TableRow>
                      <TableRow className="border-[#1e293b] hover:bg-[#1e293b]/50">
                        <TableCell className="font-medium text-white">Ekuitas</TableCell>
                        <TableCell className="text-slate-300">Rp 215T</TableCell>
                        <TableCell className="text-slate-300">Rp 208T</TableCell>
                        <TableCell className="text-emerald-400">+3.4%</TableCell>
                      </TableRow>
                    </TableBody>
                  </Table>
                </TabsContent>
                <TabsContent value="cashflow" className="m-0 p-6">
                  <Table>
                    <TableHeader>
                      <TableRow className="border-[#1e293b] hover:bg-transparent">
                        <TableHead className="w-[250px] bg-[#1e293b] text-slate-300">Metrik</TableHead>
                        <TableHead className="bg-[#1e293b] text-slate-300">Q2 2023</TableHead>
                        <TableHead className="bg-[#1e293b] text-slate-300">Q1 2023</TableHead>
                        <TableHead className="bg-[#1e293b] text-slate-300">YoY %</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      <TableRow className="border-[#1e293b] hover:bg-[#1e293b]/50">
                        <TableCell className="font-medium text-white">Arus Kas Operasi</TableCell>
                        <TableCell className="text-slate-300">Rp 15.2T</TableCell>
                        <TableCell className="text-slate-300">Rp 14.3T</TableCell>
                        <TableCell className="text-emerald-400">+6.3%</TableCell>
                      </TableRow>
                      <TableRow className="border-[#1e293b] hover:bg-[#1e293b]/50">
                        <TableCell className="font-medium text-white">Arus Kas Investasi</TableCell>
                        <TableCell className="text-slate-300">Rp -5.8T</TableCell>
                        <TableCell className="text-slate-300">Rp -4.9T</TableCell>
                        <TableCell className="text-red-400">+18.4%</TableCell>
                      </TableRow>
                      <TableRow className="border-[#1e293b] hover:bg-[#1e293b]/50">
                        <TableCell className="font-medium text-white">Arus Kas Pendanaan</TableCell>
                        <TableCell className="text-slate-300">Rp -3.2T</TableCell>
                        <TableCell className="text-slate-300">Rp -2.8T</TableCell>
                        <TableCell className="text-red-400">+14.3%</TableCell>
                      </TableRow>
                      <TableRow className="border-[#1e293b] hover:bg-[#1e293b]/50">
                        <TableCell className="font-medium text-white">Kas Bersih</TableCell>
                        <TableCell className="text-slate-300">Rp 6.2T</TableCell>
                        <TableCell className="text-slate-300">Rp 6.6T</TableCell>
                        <TableCell className="text-red-400">-6.1%</TableCell>
                      </TableRow>
                    </TableBody>
                  </Table>
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}