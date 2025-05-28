"use client"

import { useState } from "react"
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
import { Sidebar, MobileSidebar } from "@/components/sidebar"

export default function BeritaPage() {
  const [searchQuery, setSearchQuery] = useState("")
  const [sortOrder, setSortOrder] = useState("terbaru")
  const [expandedNews, setExpandedNews] = useState<number | null>(null)

  const handleSearch = (query: string) => {
    console.log("Searching for:", query)
  }

  // Sample news data
  const newsData = [
    {
      id: 1,
      title: "BCA Catat Pertumbuhan Laba 7% di Q2 2023",
      summary:
        "Bank Central Asia (BBCA) mencatatkan pertumbuhan laba bersih sebesar 7% YoY pada kuartal kedua 2023. Pencapaian ini didorong oleh peningkatan pendapatan bunga bersih sebesar 5,8% dan pendapatan non-bunga yang tumbuh 11,9%. Direktur Keuangan BCA, Vera Eve Lim, menyatakan bahwa pertumbuhan kredit yang solid di segmen korporasi dan konsumer menjadi pendorong utama kinerja positif tersebut.",      
        fullContent:
        "IQPlus, (14/1) - Transparency International Indonesia (TII) bekerja sama dengan TEMPO Data Science menganugerahkan PT Astra Agro Lestari Tbk (AALI) sebagai emiten kelapa sawit dengan integritas tinggi. Astra Agro Lestari menerima penghargaan Indeks Integritas Bisnis Lestari dalam kategori Sapphire, pada Selasa (10/12) di Salihara Art Center. Kedua lembaga itu memberikan penghargaan tersebut sebagai bentuk pengakuan atas upaya nyata perusahaan dalam menerapkan praktik bisnis yang berintegritas dan berkelanjutan. Penghargaan itu pun menegaskan keberhasilan perusahaan dalam mengintegrasikan prinsip anti korupsi, penghormatan terhadap hak asasi manusia, dan keberlanjutan lingkungan ke dalam tata kelola perusahaan. Penilaian TII dan Tempo Data Science menjadi bukti bahwa perusahaan telah melaksanakan langkah-langkah strategis untuk mendukung prinsip-prinsip tersebut. Presiden Direktur Astra Agro Lestari Santosa menyatakan program keberlanjutan telah menjadi inti dari visi Perusahaan yakni Sejahtera Bersama Bangsa. Sekaligus menjawab tanggung jawab secara global yang berkaitan dengan Sustainable Development Goals (SDGs). Komitmen ini terus kami wujudkan melalui sustainability action plan yang sejalan dengan Sustainable Development Goals (SDGs). Kami juga telah memiliki kebijakan keberlanjutan yang berfokus pada prinsip- prinsip seperti tidak melakukan deforestasi, konservasi pada lahan gambut, serta penghormatan terhadap hak asasi manusia, jelas Santosa. Sementara itu, Direktur Astra Agro Lestari Widayanto menambahkan bahwa penghargaan ini menjadi bukti nyata dari komitmen perusahaan untuk memberikan kontribusi positif bagi setiap lapisan masyarakat dan lingkungan. Kami percaya bahwa keberlanjutan adalah pondasi utama untuk pertumbuhan jangka panjang. Pengakuan ini memotivasi kami untuk terus meningkatkan kualitas tata kelola dan memberikan dampak yang lebih besar bagi semua pemangku kepentingan, ujar Widayanto. Sejalan dengan itu, CEO Tempo Media Group, Arif Zulkifli mengungkapkan bahwa perusahaan yang mengutamakan integritas akan mampu mendorong keberlanjutan lingkungan dan membawa perubahan signifikan bagi masyarakat. Kata integritas bukanlah sesuatu yang main-main. Integritas mencerminkan kejujuran, kewibawaan, kemampuan dalam menjaga prinsip dan etika dalam berbisnis. Praktik bisnis yang berintegritas dan berkelanjutan kini menjadi aspek penting dalam dunia usaha, ungkap Arif. Keunggulan Astra Agro dalam tiga aspek utama menjadi alasan di balik pencapaian ini. Di bidang anti korupsi, perusahaan menerapkan kode etik yang tegas, memberikan pelatihan integritas kepada karyawan, dan selalu memberikan keterbukaan informasi baik kepada stakeholder maupun publik. Dalam aspek hak asasi manusia, Astra Agro menjalankan program pemberdayaan masyarakat, melindungi hak-hak pekerja, dan menciptakan lingkungan kerja yang aman dan nyaman bagi seluruh karyawan. Sementara itu, di bidang lingkungan hidup, perusahaan konsisten menerapkan praktik agribisnis ramah lingkungan, pengelolaan limbah yang baik, serta upaya pelestarian keanekaragaman hayati di seluruh area operasionalnya. Secretary General Transparacy International-Indonesia Danang Widoyoko mengatakan secara umum tujuan penghargaan ini digelar untuk mendorong integritas di sektor publik dan sektor swasta. Menurutnya isu-isu terkait keberlanjutan telah menjadi fokus seluruh lapisan, mulai dari pemerintah, pebisnis, hingga masyarakat. Hal ini yang mendorong TII yang merupakan NGO antikorupsi kemudian bersama dengan Tempo untuk melakukan pengukuran ESG. Kami secara independent dan objektif menilai langsung jadi mohon maaf, kami masuk ke semua website dan cek satu-satu perusahaan, mulai dari laporan tahunannya, Sustainability Report, dari Code of Conduct dan semua dokumen yang ada di situs, jelasnya. Dengan penghargaan ini, PT Astra Agro Lestari semakin mempertegas posisinya sebagai perusahaan yang tidak hanya berorientasi pada profit, tetapi juga memiliki tanggung jawab besar terhadap masyarakat dan kelestarian lingkungan. (end)",
      date: "15 Juli 2023",
      time: "14:30 WIB",
      source: "Investor Daily",
      category: "Keuangan",
      relatedStocks: ["BBCA", "BMRI", "BBRI"],
      imageUrl: "/placeholder.svg?height=200&width=400",
    },
    {
      id: 2,
      title: "OJK Perketat Aturan Margin Trading untuk Perlindungan Investor",
      summary:
        "Otoritas Jasa Keuangan (OJK) mengeluarkan aturan baru terkait margin trading untuk meningkatkan perlindungan investor. Regulasi ini mewajibkan perusahaan sekuritas untuk menerapkan sistem manajemen risiko yang lebih ketat dan transparansi yang lebih baik kepada nasabah. Ketua Dewan Komisioner OJK, Mahendra Siregar, menekankan pentingnya edukasi investor terkait risiko margin trading.",
      fullContent:
        'Otoritas Jasa Keuangan (OJK) mengeluarkan aturan baru terkait margin trading untuk meningkatkan perlindungan investor. Regulasi ini mewajibkan perusahaan sekuritas untuk menerapkan sistem manajemen risiko yang lebih ketat dan transparansi yang lebih baik kepada nasabah. Ketua Dewan Komisioner OJK, Mahendra Siregar, menekankan pentingnya edukasi investor terkait risiko margin trading.\n\nAturan baru tersebut mencakup beberapa poin utama, di antaranya penurunan rasio maksimum fasilitas pembiayaan dari 65% menjadi 60% dari nilai portofolio, peningkatan persyaratan margin call, serta kewajiban perusahaan sekuritas untuk memberikan simulasi risiko kepada nasabah sebelum membuka fasilitas margin.\n\n"Kami ingin memastikan bahwa investor memahami sepenuhnya risiko yang terkait dengan margin trading, terutama dalam kondisi pasar yang volatil," ujar Mahendra dalam konferensi pers virtual pada Rabu (12/7). Aturan baru ini akan mulai berlaku efektif pada 1 Oktober 2023, dengan masa transisi selama tiga bulan bagi perusahaan sekuritas untuk menyesuaikan sistem mereka.',
      date: "12 Juli 2023",
      time: "10:15 WIB",
      source: "CNBC Indonesia",
      category: "Regulasi",
      relatedStocks: ["PANS", "TRIM", "SRTG"],
      imageUrl: "/placeholder.svg?height=200&width=400",
    },
    // Additional news data...
  ]

  // Filter and sort news
  const sortedAndFilteredNews = [...newsData]
    .filter((news) => {
      if (!searchQuery.trim()) return true
      return news.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
             news.fullContent.toLowerCase().includes(searchQuery.toLowerCase())
    })
    .sort((a, b) => {
      const dateA = new Date(a.date.split(" ")[0].split("-").reverse().join("-"))
      const dateB = new Date(b.date.split(" ")[0].split("-").reverse().join("-"))
      return sortOrder === "terbaru" 
        ? dateB.getTime() - dateA.getTime() 
        : dateA.getTime() - dateB.getTime()
    })

  const toggleExpandNews = (id: number) => {
    setExpandedNews(expandedNews === id ? null : id)
  }

  return (
    <div className="flex min-h-screen bg-[#0f172a]">
      <Sidebar 
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        onSearch={handleSearch}
      />
      
      <div className="flex-1">
        <header className="sticky top-0 z-10 flex h-16 items-center justify-between border-b border-[#1e293b] bg-[#0f172a]/80 px-4 backdrop-blur-sm md:px-6">          <div className="flex items-center gap-4">
            <MobileSidebar 
              searchQuery={searchQuery}
              onSearchChange={setSearchQuery}
              onSearch={handleSearch}
            />
            <h1 className="text-xl font-semibold text-white">Berita</h1>
          </div>
        </header>        <div className="p-4 md:p-6">
          <div className="mb-6 flex items-center justify-between">
            <h2 className="text-xl font-semibold text-white">Semua Berita</h2>
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
            {sortedAndFilteredNews.length > 0 ? (
              sortedAndFilteredNews.map((news) => (
                <Card key={news.id} className="overflow-hidden border-[#1e293b] bg-[#0f172a] shadow-lg">
                  <CardHeader className="border-b border-[#1e293b] px-6 pb-4 pt-5">
                    <div className="flex flex-col gap-2">
                      <div className="flex items-center gap-2">
                        <div className="rounded-full bg-indigo-900/50 px-2 py-0.5 text-xs font-medium text-indigo-300">
                          {news.category}
                        </div>
                        <div className="flex items-center gap-1 text-xs text-slate-400">
                          <Calendar className="h-3 w-3" />
                          <span>{news.date}</span>
                        </div>
                        <div className="flex items-center gap-1 text-xs text-slate-400">
                          <Clock className="h-3 w-3" />
                          <span>{news.time}</span>
                        </div>
                      </div>
                      <CardTitle className="text-xl text-white">{news.title}</CardTitle>
                      <CardDescription className="text-slate-400">
                        Sumber: {news.source} | Terkait: {news.relatedStocks.join(", ")}
                      </CardDescription>
                    </div>
                  </CardHeader>
                  <CardContent className="p-6">                    <div className="mb-4">
                      {expandedNews === news.id ? (
                        <div className="space-y-4 leading-relaxed text-slate-300">
                          {news.fullContent.split('\n\n').map((paragraph, idx) => (
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
                            <p className="text-slate-300 leading-relaxed">{news.summary}</p>
                          </div>
                        </div>
                      )}
                    </div>
                    <div className="flex justify-between">                      <Button
                        variant="outline"
                        className="border-[#1e293b] bg-[#1e293b]/50 text-slate-300 hover:bg-[#1e293b] hover:text-white"
                        onClick={() => toggleExpandNews(news.id)}
                      >
                        {expandedNews === news.id ? (
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
                      >
                        <ExternalLink className="mr-2 h-4 w-4" /> Buka di Sumber
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))
            ) : (
              <div className="flex h-40 flex-col items-center justify-center rounded-lg border border-[#1e293b] bg-[#0f172a]/50 p-6 text-center">
                <p className="mb-2 text-lg font-medium text-slate-300">Tidak ada berita yang ditemukan</p>
                <p className="text-sm text-slate-400">Coba gunakan kata kunci pencarian yang berbeda</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
