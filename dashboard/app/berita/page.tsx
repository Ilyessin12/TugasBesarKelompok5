"use client"

import { useState, useEffect } from "react" 
import { useSearchParams } from "next/navigation"
import { RealtimeClock } from "@/components/realtime-clock"
import {
  Calendar,
  Clock,
  ChevronDown,
  ChevronUp,
  ExternalLink,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { MobileSidebar } from "@/components/sidebar"
import { API } from "@/services/api"

export default function BeritaPage() {
  // Get emiten from URL query parameters
  const searchParams = useSearchParams()
  
  const [searchQuery, setSearchQuery] = useState("")
  const [sortOrder, setSortOrder] = useState("terbaru")
  const [expandedNews, setExpandedNews] = useState<string | null>(null)
  
  // State for API data
  const [newsData, setNewsData] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedEmiten, setSelectedEmiten] = useState<string | null>(null)

  // Handle search query changes
  const handleSearch = (query: string) => {
    // Update the search query for filtering
    setSearchQuery(query)
    
    // If query is an emiten code, fetch its news
    if (query && query.length >= 2) {
      setSelectedEmiten(query.toUpperCase())
      fetchNewsData(query.toUpperCase())
    }
  }

  // Function to fetch news data
  const fetchNewsData = async (emiten: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const emitenCode = emiten.replace('.JK', '');
      const data = await API.getNewsData(emitenCode, 20, 0);
      
      // Check if the response is actually an error message
      if (data && typeof data === 'object' && data.message && !Array.isArray(data)) {
        console.log("API returned a message:", data.message);
        // This is not a technical error, just empty data
        setNewsData([]);
      } else if (Array.isArray(data)) {
        console.log(`Received ${data.length} news items`);
        setNewsData(data);
      } else {
        // Unexpected response format
        console.error("Unexpected API response format:", data);
        setNewsData([]);
      }
    } catch (err: any) {
      // This is a technical error (network issue, server down, etc.)
      console.error("Error fetching news:", err);
      setError(`${err.message || 'Unknown error'}`);
    } finally {
      setIsLoading(false);
    }
  }

  // Initial load - fetch emiten from URL or default to general news
  useEffect(() => {
    const emitenParam = searchParams?.get('emiten')
    
    if (emitenParam) {
      setSelectedEmiten(emitenParam.toUpperCase())
      fetchNewsData(emitenParam)
    } else {
      // Could fetch general news here
      setIsLoading(false)
    }
  }, [searchParams])

  // Toggle expanded news
  const toggleExpandNews = (id: string) => {
    setExpandedNews(expandedNews === id ? null : id)
  }

  // Filter and sort news
  const sortedAndFilteredNews = [...newsData]
    .filter((news) => {
      if (!searchQuery.trim()) return true
      
      // Search in title and content
      return (
        (news.Title?.toLowerCase().includes(searchQuery.toLowerCase()) || false) ||
        (news.Content?.toLowerCase().includes(searchQuery.toLowerCase()) || false) ||
        (news.Ringkasan?.toLowerCase().includes(searchQuery.toLowerCase()) || false)
      )
    })
    .sort((a, b) => {
      // Parse dates from API format "DD/MM/YY - HH:MM" or fallback to uploaded_at
      const getDate = (item: any) => {
        if (item.Date) {
          const dateParts = item.Date.split(' - ')[0].split('/')
          if (dateParts.length === 3) {
            return new Date(2000 + parseInt(dateParts[2]), parseInt(dateParts[1]) - 1, parseInt(dateParts[0]))
          }
        }
        return new Date(item.uploaded_at || 0)
      }
      
      const dateA = getDate(a)
      const dateB = getDate(b)
      
      return sortOrder === "terbaru" 
        ? dateB.getTime() - dateA.getTime() 
        : dateA.getTime() - dateB.getTime()
    })

  // Format date string from "DD/MM/YY - HH:MM" to separate date and time
  const formatDateParts = (dateString: string) => {
    if (!dateString) return { date: 'N/A', time: 'N/A' }
    
    const parts = dateString.split(' - ')
    if (parts.length !== 2) return { date: dateString, time: '' }
    
    const [day, month, year] = parts[0].split('/')
    const date = `${day}/${month}/20${year}`
    const time = `${parts[1]} WIB`
    
    return { date, time }
  }

  return (
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
          
          <div className="flex items-center gap-4">
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
            
            <RealtimeClock />
          </div>
        </header>
        
        <div className="p-4 md:p-6">
          <div className="mb-6 flex items-center justify-between">
            <h2 className="text-xl font-semibold text-white">
              {selectedEmiten ? `Berita ${selectedEmiten}` : "Semua Berita"}
            </h2>
            <Select defaultValue="terbaru" onValueChange={setSortOrder}>
              <SelectTrigger className="w-[150px] border-[#1e293b] bg-[#1e293b] text-slate-300">
                <SelectValue placeholder="Urutkan" />
              </SelectTrigger>
              <SelectContent className="border-[#1e293b] bg-[#0f172a] text-slate-300">
                <SelectItem value="terbaru">Terbaru</SelectItem>
                <SelectItem value="terlama">Terlama</SelectItem>
              </SelectContent>
            </Select>
          </div>
          
          <div className="grid gap-6">
            {isLoading ? (
              <div className="flex h-40 items-center justify-center">
                <div className="h-8 w-8 animate-spin rounded-full border-2 border-t-transparent border-indigo-500"></div>
                <span className="ml-3 text-slate-300">Loading news...</span>
              </div>
            ) : error ? (
              // Technical error case (API call failed)
              <div className="flex h-40 flex-col items-center justify-center rounded-lg border border-red-900/50 bg-red-900/10 p-6 text-center">
                <p className="mb-2 text-lg font-medium text-red-400">{error}</p>
                <p className="text-sm text-slate-400">Please try again later</p>
              </div>
            ) : sortedAndFilteredNews.length > 0 ? (
              // News found case
              sortedAndFilteredNews.map((news) => {
                const { date, time } = formatDateParts(news.Date);
                
                return (
                  <Card key={news._id} className="overflow-hidden border-[#1e293b] bg-[#0f172a] shadow-lg">
                    <CardHeader className="border-b border-[#1e293b] px-6 pb-4 pt-5">
                      <div className="flex flex-col gap-2">
                        <div className="flex items-center gap-2">
                          <div className="rounded-full bg-indigo-900/50 px-2 py-0.5 text-xs font-medium text-indigo-300">
                            {news.Emiten?.replace('.JK', '') || "Unknown"}
                          </div>
                          <div className="flex items-center gap-1 text-xs text-slate-400">
                            <Calendar className="h-3 w-3" />
                            <span>{date}</span>
                          </div>
                          <div className="flex items-center gap-1 text-xs text-slate-400">
                            <Clock className="h-3 w-3" />
                            <span>{time}</span>
                          </div>
                        </div>
                        <CardTitle className="text-xl text-white">{news.Title}</CardTitle>
                        <CardDescription className="text-slate-400">
                          Sumber: {news.Link?.split('/')[2] || "Unknown"}
                        </CardDescription>
                      </div>
                    </CardHeader>
                    <CardContent className="p-6">
                      <div className="mb-4">
                        {expandedNews === news._id ? (
                          <div className="space-y-4 leading-relaxed text-slate-300">
                            {news.Content.split('\n\n').map((paragraph: string, idx: number) => (
                              <p key={idx}>{paragraph}</p>
                            ))}
                          </div>
                        ) : (
                          <div className="relative">
                            <div className="mb-3 flex items-center">
                              <span className="flex items-center gap-2 rounded-lg bg-gradient-to-r from-emerald-900/60 to-blue-900/60 px-3 py-1 text-xs font-medium text-emerald-200">
                                <svg
                                  width="14"
                                  height="14"
                                  viewBox="0 0 24 24"
                                  fill="none"
                                  stroke="currentColor"
                                  strokeWidth="2"
                                  strokeLinecap="round"
                                  strokeLinejoin="round"
                                  className="animate-pulse"
                                >
                                  <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" />
                                  <path d="M12 22.08V12" />
                                  <path d="m3.5 7 8.5 4.87L20.5 7" />
                                </svg>
                                Ringkasan AI
                              </span>
                            </div>
                            <div className="rounded-lg bg-gradient-to-b from-slate-800/50 to-transparent p-4">
                              <p className="text-slate-300 leading-relaxed">{news.Ringkasan}</p>
                            </div>
                          </div>
                        )}
                      </div>
                      <div className="flex justify-between">
                        <Button
                          variant="outline"
                          className="border-[#1e293b] bg-[#1e293b]/50 text-slate-300 hover:bg-[#1e293b] hover:text-white"
                          onClick={() => toggleExpandNews(news._id)}
                        >
                          {expandedNews === news._id ? (
                            <>
                              <ChevronUp className="mr-2 h-4 w-4" /> Kembali ke Ringkasan AI
                            </>
                          ) : (
                            <>
                              <ChevronDown className="mr-2 h-4 w-4" /> Baca Berita Lengkap
                            </>
                          )}
                        </Button>
                        <Button
                          variant="outline"
                          className="border-[#1e293b] bg-[#1e293b]/50 text-slate-300 hover:bg-[#1e293b] hover:text-white"
                          onClick={() => window.open(news.Link, '_blank')}
                        >
                          <ExternalLink className="mr-2 h-4 w-4" /> Buka di Sumber
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                );
              })
            ) : (
              // Empty data case (API worked but no news found)
              <div className="flex h-40 flex-col items-center justify-center rounded-lg border border-[#1e293b] bg-[#0f172a]/50 p-6 text-center">
                <p className="mb-2 text-lg font-medium text-slate-300">Tidak ada berita yang ditemukan</p>
                <p className="text-sm text-slate-400">
                  {selectedEmiten 
                    ? `Tidak ada berita terkini untuk emiten ${selectedEmiten}` 
                    : "Coba gunakan kata kunci pencarian yang berbeda"}
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
