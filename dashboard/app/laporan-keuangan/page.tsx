"use client"

import { useState } from "react"
import {
  BarChart,
  Bell,
  Calendar,
  ChevronDown,
  Clock,
  FileText,
  Home,
  Menu,
  Search,
  Settings,
  TrendingUp,
} from "lucide-react"
import Link from "next/link"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Sidebar, MobileSidebar } from "@/components/sidebar"
import { IncomeChart, BalanceChart, CashFlowChart } from "@/components/financial-charts"
import { AssetCompositionChart, EquityLiabilitiesChart, ProfitLossFlowChart } from "@/components/financial-charts"

// Define types for financial data structure
type FinancialMetric = {
  metric: string
  q2_2023: string
  q1_2023: string
  q4_2022: string
  q3_2022: string
  yoy: string
}

type EmitenFinancialData = {
  overview: FinancialMetric[]
  income: FinancialMetric[]
  balance: FinancialMetric[]
  cashflow: FinancialMetric[]
}

type FinancialDataType = {
  [key: string]: EmitenFinancialData
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

export default function LaporanKeuanganPage() {
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedEmiten, setSelectedEmiten] = useState("BBCA")
  const [selectedPeriod, setSelectedPeriod] = useState("q2_2023")
  const [reportType, setReportType] = useState<"quarterly" | "annual">("quarterly")

  // Replace the existing emitenList with simpler static data
  const emitenList = [
    { code: "BBCA", name: "Bank Central Asia Tbk", sector: "Keuangan" },
    { code: "BBRI", name: "Bank Rakyat Indonesia Tbk", sector: "Keuangan" },
    { code: "TLKM", name: "Telkom Indonesia Tbk", sector: "Telekomunikasi" }
  ]

  // Replace the existing financialData with simpler static data
  const financialData: FinancialDataType = {
    BBCA: {
      overview: [
        {
          metric: "Pendapatan",
          q2_2023: "Rp 25.7T",
          q1_2023: "Rp 24.2T",
          q4_2022: "Rp 23.8T",
          q3_2022: "Rp 23.1T",
          yoy: "+6.2%",
        },
        {
          metric: "Laba Bersih",
          q2_2023: "Rp 10.5T",
          q1_2023: "Rp 9.8T", 
          q4_2022: "Rp 9.5T",
          q3_2022: "Rp 9.2T",
          yoy: "+7.1%",
        },
        {
          metric: "ROE",
          q2_2023: "19.8%",
          q1_2023: "19.2%",
          q4_2022: "18.9%", 
          q3_2022: "18.5%",
          yoy: "+0.6%",
        }
      ],
      income: [
        {
          metric: "Pendapatan Bunga",
          q2_2023: "Rp 18.2T",
          q1_2023: "Rp 17.5T",
          q4_2022: "Rp 17.2T",
          q3_2022: "Rp 16.8T",
          yoy: "+4.0%",
        }
      ],
      balance: [
        {
          metric: "Total Aset",
          q2_2023: "Rp 1,350T",
          q1_2023: "Rp 1,320T",
          q4_2022: "Rp 1,300T",
          q3_2022: "Rp 1,280T",
          yoy: "+2.3%", 
        }
      ],
      cashflow: [
        {
          metric: "Arus Kas Operasi",
          q2_2023: "Rp 15.2T",
          q1_2023: "Rp 14.3T",
          q4_2022: "Rp 14.0T",
          q3_2022: "Rp 13.8T",
          yoy: "+6.3%",
        }
      ]
    }
  }

  const handleEmitenSelect = (code: string): void => {
    setSelectedEmiten(code)
  }

  const handlePeriodChange = (value: string): void => {
    setSelectedPeriod(value)
  }

  return (
    <div className="flex min-h-screen bg-[#0f172a]">
      <Sidebar 
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
      />
      
      <div className="flex-1">
        <header className="sticky top-0 z-10 flex h-16 items-center justify-between border-b border-[#1e293b] bg-[#0f172a]/80 px-4 backdrop-blur-sm md:px-6">
          <div className="flex items-center gap-4">
            <MobileSidebar 
              searchQuery={searchQuery}
              onSearchChange={setSearchQuery}
            />
            <h1 className="text-xl font-semibold text-white">Laporan Keuangan</h1>
          </div>
        </header>

        <div className="p-4 md:p-6">
          <Card className="border-[#1e293b] bg-[#0f172a] shadow-lg">
            <CardHeader className="border-b border-[#1e293b] px-6">
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

                {/* Overview Tab */}
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
                        <TableCell className="font-medium text-white">Pendapatan Bunga</TableCell>
                        {reportType === "quarterly" ? (
                          <>
                            <TableCell className="text-slate-300">Rp 18.8T</TableCell>
                            <TableCell className="text-slate-300">Rp 18.2T</TableCell>
                            <TableCell className="text-slate-300">Rp 17.5T</TableCell>
                            <TableCell className="text-slate-300">Rp 17.1T</TableCell>
                          </>
                        ) : (
                          <>
                            <TableCell className="text-slate-300">Rp 71.6T</TableCell>
                            <TableCell className="text-slate-300">Rp 68.2T</TableCell>
                            <TableCell className="text-slate-300">Rp 65.1T</TableCell>
                            <TableCell className="text-slate-300">Rp 62.3T</TableCell>
                            <TableCell className="text-slate-300">Rp 59.8T</TableCell>
                          </>
                        )}
                      </TableRow>
                      <TableRow className="border-[#1e293b] hover:bg-[#1e293b]/50">
                        <TableCell className="font-medium text-white">Pendapatan Non-Bunga</TableCell>
                        {reportType === "quarterly" ? (
                          <>
                            <TableCell className="text-slate-300">Rp 8.1T</TableCell>
                            <TableCell className="text-slate-300">Rp 7.5T</TableCell>
                            <TableCell className="text-slate-300">Rp 6.7T</TableCell>
                            <TableCell className="text-slate-300">Rp 6.2T</TableCell>
                          </>
                        ) : (
                          <>
                            <TableCell className="text-slate-300">Rp 28.5T</TableCell>
                            <TableCell className="text-slate-300">Rp 25.9T</TableCell>
                            <TableCell className="text-slate-300">Rp 23.8T</TableCell>
                            <TableCell className="text-slate-300">Rp 22.1T</TableCell>
                            <TableCell className="text-slate-300">Rp 20.7T</TableCell>
                          </>
                        )}
                      </TableRow>
                      <TableRow className="border-[#1e293b] hover:bg-[#1e293b]/50">
                        <TableCell className="font-medium text-white">Beban Operasional</TableCell>
                        {reportType === "quarterly" ? (
                          <>
                            <TableCell className="text-slate-300">Rp 10.2T</TableCell>
                            <TableCell className="text-slate-300">Rp 9.8T</TableCell>
                            <TableCell className="text-slate-300">Rp 9.5T</TableCell>
                            <TableCell className="text-slate-300">Rp 9.2T</TableCell>
                          </>
                        ) : (
                          <>
                            <TableCell className="text-slate-300">Rp 38.7T</TableCell>
                            <TableCell className="text-slate-300">Rp 36.5T</TableCell>
                            <TableCell className="text-slate-300">Rp 34.8T</TableCell>
                            <TableCell className="text-slate-300">Rp 33.2T</TableCell>
                            <TableCell className="text-slate-300">Rp 31.9T</TableCell>
                          </>
                        )}
                      </TableRow>
                      <TableRow className="border-[#1e293b] hover:bg-[#1e293b]/50">
                        <TableCell className="font-medium text-white">Laba Sebelum Pajak</TableCell>
                        {reportType === "quarterly" ? (
                          <>
                            <TableCell className="text-slate-300">Rp 14.1T</TableCell>
                            <TableCell className="text-slate-300">Rp 13.2T</TableCell>
                            <TableCell className="text-slate-300">Rp 12.3T</TableCell>
                            <TableCell className="text-slate-300">Rp 11.8T</TableCell>
                          </>
                        ) : (
                          <>
                            <TableCell className="text-slate-300">Rp 51.4T</TableCell>
                            <TableCell className="text-slate-300">Rp 48.2T</TableCell>
                            <TableCell className="text-slate-300">Rp 45.5T</TableCell>
                            <TableCell className="text-slate-300">Rp 43.1T</TableCell>
                            <TableCell className="text-slate-300">Rp 41.2T</TableCell>
                          </>
                        )}
                      </TableRow>
                    </TableBody>
                  </Table>
                </TabsContent>
                
                <TabsContent value="balance" className="m-0 p-6">
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
                        <TableCell className="font-medium text-white">Total Aset</TableCell>
                        {reportType === "quarterly" ? (
                          <>
                            <TableCell className="text-slate-300">Rp 1,380T</TableCell>
                            <TableCell className="text-slate-300">Rp 1,350T</TableCell>
                            <TableCell className="text-slate-300">Rp 1,320T</TableCell>
                            <TableCell className="text-slate-300">Rp 1,300T</TableCell>
                          </>
                        ) : (
                          <>
                            <TableCell className="text-slate-300">Rp 1,380T</TableCell>
                            <TableCell className="text-slate-300">Rp 1,300T</TableCell>
                            <TableCell className="text-slate-300">Rp 1,220T</TableCell>
                            <TableCell className="text-slate-300">Rp 1,150T</TableCell>
                            <TableCell className="text-slate-300">Rp 1,090T</TableCell>
                          </>
                        )}
                      </TableRow>
                      <TableRow className="border-[#1e293b] hover:bg-[#1e293b]/50">
                        <TableCell className="font-medium text-white">Kredit</TableCell>
                        {reportType === "quarterly" ? (
                          <>
                            <TableCell className="text-slate-300">Rp 735T</TableCell>
                            <TableCell className="text-slate-300">Rp 720T</TableCell>
                            <TableCell className="text-slate-300">Rp 705T</TableCell>
                            <TableCell className="text-slate-300">Rp 695T</TableCell>
                          </>
                        ) : (
                          <>
                            <TableCell className="text-slate-300">Rp 735T</TableCell>
                            <TableCell className="text-slate-300">Rp 695T</TableCell>
                            <TableCell className="text-slate-300">Rp 660T</TableCell>
                            <TableCell className="text-slate-300">Rp 630T</TableCell>
                            <TableCell className="text-slate-300">Rp 605T</TableCell>
                          </>
                        )}
                      </TableRow>
                      <TableRow className="border-[#1e293b] hover:bg-[#1e293b]/50">
                        <TableCell className="font-medium text-white">Dana Pihak Ketiga</TableCell>
                        {reportType === "quarterly" ? (
                          <>
                            <TableCell className="text-slate-300">Rp 995T</TableCell>
                            <TableCell className="text-slate-300">Rp 980T</TableCell>
                            <TableCell className="text-slate-300">Rp 965T</TableCell>
                            <TableCell className="text-slate-300">Rp 955T</TableCell>
                          </>
                        ) : (
                          <>
                            <TableCell className="text-slate-300">Rp 995T</TableCell>
                            <TableCell className="text-slate-300">Rp 955T</TableCell>
                            <TableCell className="text-slate-300">Rp 915T</TableCell>
                            <TableCell className="text-slate-300">Rp 880T</TableCell>
                            <TableCell className="text-slate-300">Rp 850T</TableCell>
                          </>
                        )}
                      </TableRow>
                      <TableRow className="border-[#1e293b] hover:bg-[#1e293b]/50">
                        <TableCell className="font-medium text-white">Ekuitas</TableCell>
                        {reportType === "quarterly" ? (
                          <>
                            <TableCell className="text-slate-300">Rp 222T</TableCell>
                            <TableCell className="text-slate-300">Rp 215T</TableCell>
                            <TableCell className="text-slate-300">Rp 208T</TableCell>
                            <TableCell className="text-slate-300">Rp 203T</TableCell>
                          </>
                        ) : (
                          <>
                            <TableCell className="text-slate-300">Rp 222T</TableCell>
                            <TableCell className="text-slate-300">Rp 203T</TableCell>
                            <TableCell className="text-slate-300">Rp 188T</TableCell>
                            <TableCell className="text-slate-300">Rp 175T</TableCell>
                            <TableCell className="text-slate-300">Rp 165T</TableCell>
                          </>
                        )}
                      </TableRow>
                    </TableBody>
                  </Table>
                </TabsContent>
                
                <TabsContent value="cashflow" className="m-0 p-6">
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
                        <TableCell className="font-medium text-white">Arus Kas Operasi</TableCell>
                        {reportType === "quarterly" ? (
                          <>
                            <TableCell className="text-slate-300">Rp 16.2T</TableCell>
                            <TableCell className="text-slate-300">Rp 15.2T</TableCell>
                            <TableCell className="text-slate-300">Rp 14.3T</TableCell>
                            <TableCell className="text-slate-300">Rp 13.8T</TableCell>
                          </>
                        ) : (
                          <>
                            <TableCell className="text-slate-300">Rp 59.5T</TableCell>
                            <TableCell className="text-slate-300">Rp 55.8T</TableCell>
                            <TableCell className="text-slate-300">Rp 52.6T</TableCell>
                            <TableCell className="text-slate-300">Rp 49.8T</TableCell>
                            <TableCell className="text-slate-300">Rp 47.4T</TableCell>
                          </>
                        )}
                      </TableRow>
                      <TableRow className="border-[#1e293b] hover:bg-[#1e293b]/50">
                        <TableCell className="font-medium text-white">Arus Kas Investasi</TableCell>
                        {reportType === "quarterly" ? (
                          <>
                            <TableCell className="text-slate-300">Rp -6.5T</TableCell>
                            <TableCell className="text-slate-300">Rp -5.8T</TableCell>
                            <TableCell className="text-slate-300">Rp -4.9T</TableCell>
                            <TableCell className="text-slate-300">Rp -4.2T</TableCell>
                          </>
                        ) : (
                          <>
                            <TableCell className="text-slate-300">Rp -21.4T</TableCell>
                            <TableCell className="text-slate-300">Rp -19.8T</TableCell>
                            <TableCell className="text-slate-300">Rp -18.5T</TableCell>
                            <TableCell className="text-slate-300">Rp -17.4T</TableCell>
                            <TableCell className="text-slate-300">Rp -16.6T</TableCell>
                          </>
                        )}
                      </TableRow>
                      <TableRow className="border-[#1e293b] hover:bg-[#1e293b]/50">
                        <TableCell className="font-medium text-white">Arus Kas Pendanaan</TableCell>
                        {reportType === "quarterly" ? (
                          <>
                            <TableCell className="text-slate-300">Rp -3.8T</TableCell>
                            <TableCell className="text-slate-300">Rp -3.2T</TableCell>
                            <TableCell className="text-slate-300">Rp -2.8T</TableCell>
                            <TableCell className="text-slate-300">Rp -2.5T</TableCell>
                          </>
                        ) : (
                          <>
                            <TableCell className="text-slate-300">Rp -12.3T</TableCell>
                            <TableCell className="text-slate-300">Rp -11.5T</TableCell>
                            <TableCell className="text-slate-300">Rp -10.8T</TableCell>
                            <TableCell className="text-slate-300">Rp -10.2T</TableCell>
                            <TableCell className="text-slate-300">Rp -9.7T</TableCell>
                          </>
                        )}
                      </TableRow>
                      <TableRow className="border-[#1e293b] hover:bg-[#1e293b]/50">
                        <TableCell className="font-medium text-white">Kas Bersih</TableCell>
                        {reportType === "quarterly" ? (
                          <>
                            <TableCell className="text-slate-300">Rp 5.9T</TableCell>
                            <TableCell className="text-slate-300">Rp 6.2T</TableCell>
                            <TableCell className="text-slate-300">Rp 6.6T</TableCell>
                            <TableCell className="text-slate-300">Rp 7.1T</TableCell>
                          </>
                        ) : (
                          <>
                            <TableCell className="text-slate-300">Rp 25.8T</TableCell>
                            <TableCell className="text-slate-300">Rp 24.5T</TableCell>
                            <TableCell className="text-slate-300">Rp 23.3T</TableCell>
                            <TableCell className="text-slate-300">Rp 22.2T</TableCell>
                            <TableCell className="text-slate-300">Rp 21.1T</TableCell>
                          </>
                        )}
                      </TableRow>
                    </TableBody>
                  </Table>
                </TabsContent>
              </Tabs>
              
              {/* Financial Charts Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 p-6">
                <Card className="border-[#1e293b] bg-[#0f172a]">
                  <CardHeader>
                    <CardTitle className="text-slate-300">Komposisi Aset</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <AssetCompositionChart data={staticFinancialData.ADRO} />
                  </CardContent>
                </Card>

                <Card className="border-[#1e293b] bg-[#0f172a]">
                  <CardHeader>
                    <CardTitle className="text-slate-300">Ekuitas vs. Liabilitas</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <EquityLiabilitiesChart data={staticFinancialData.ADRO} />
                  </CardContent>
                </Card>

                <Card className="border-[#1e293b] bg-[#0f172a]">
                  <CardHeader>
                    <CardTitle className="text-slate-300">Alur Laba Rugi</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ProfitLossFlowChart data={staticFinancialData.ADRO} />
                  </CardContent>
                </Card>

                <Card className="border-[#1e293b] bg-[#0f172a]">
                  <CardHeader>
                    <CardTitle className="text-slate-300">Arus Kas</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <CashFlowChart data={staticFinancialData.ADRO} />
                  </CardContent>
                </Card>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
