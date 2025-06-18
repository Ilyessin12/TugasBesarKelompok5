"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { useState, useEffect } from "react"
import {
  BarChart,
  Bell,
  Clock,
  ExternalLink,
  FileText,
  Home,
  Menu,
  Search,
  Settings,
  TrendingUp,
  Calendar,
} from "lucide-react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet"

interface SidebarProps {
  searchQuery?: string
  onSearchChange?: (value: string) => void
  onSearch?: (query: string) => void // Add this prop
}

// Clock component for displaying realtime clock and date
function RealtimeClock() {
  const [date, setDate] = useState(new Date());
  
  useEffect(() => {
    const timer = setInterval(() => {
      setDate(new Date());
    }, 1000);
    
    return () => {
      clearInterval(timer);
    };
  }, []);
  
  const formatTime = (date: Date) => {
    return new Intl.DateTimeFormat('id-ID', { 
      hour: '2-digit', 
      minute: '2-digit', 
      second: '2-digit',
      hour12: false 
    }).format(date);
  };
  
  const formatDate = (date: Date) => {
    return new Intl.DateTimeFormat('id-ID', { 
      day: 'numeric', 
      month: 'long', 
      year: 'numeric',
      weekday: 'long'
    }).format(date);
  };
  
  return (
    <div className="flex flex-col items-center text-slate-300 mt-auto p-4 border-t border-[#1e293b]">
      <div className="flex items-center mb-1">
        <Clock className="h-4 w-4 mr-2" />
        <span className="text-lg font-semibold">{formatTime(date)}</span>
      </div>
      <div className="text-sm text-slate-400 text-center">
        <span>{formatDate(date)}</span>
      </div>
    </div>
  );
}

export function Sidebar({ searchQuery = "", onSearchChange, onSearch }: SidebarProps) {
  const pathname = usePathname()

  // Add form submit handler
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (onSearch && searchQuery) {
      onSearch(searchQuery)
    }
  }
  return (
    <div className="hidden w-64 flex-col border-r border-[#1e293b] bg-[#0f172a] md:flex h-full">
      <div className="flex h-16 items-center border-b border-[#1e293b] px-6">
        <Link href="/dashboard" className="flex items-center gap-2 text-lg font-semibold text-white">
          <div className="flex h-8 w-8 items-center justify-center rounded-md bg-gradient-to-br from-indigo-500 to-purple-600 text-white">
            <TrendingUp className="h-5 w-5" />
          </div>
          <span className="font-bold">SahamSederhana</span>
        </Link>
      </div>
      <div className="flex-1 overflow-auto px-3 py-4">
        <div className="mb-6 px-3">
          <form onSubmit={handleSubmit}>
            <div className="relative">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-slate-400" />
              <Input
                type="search"
                placeholder="Cari saham..."
                className="w-full border-[#1e293b] bg-[#1e293b] pl-8 text-slate-300 shadow-none placeholder:text-slate-500 focus-visible:ring-1 focus-visible:ring-indigo-500"
                value={searchQuery}
                onChange={(e) => onSearchChange?.(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault()
                    if (onSearch && searchQuery) {
                      onSearch(searchQuery)
                    }
                  }
                }}
              />
            </div>
          </form>
        </div>
        <div className="space-y-1 px-3 py-2">
          <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-slate-500">Menu Utama</p>
          <Button 
            variant="ghost" 
            className={`w-full justify-start ${
              pathname === "/dashboard" 
                ? "bg-[#1e293b] text-white" 
                : "text-slate-400 hover:bg-[#1e293b] hover:text-white"
            }`}
          >
            <Home className="mr-2 h-4 w-4" />
            <Link href="/dashboard">Dashboard</Link>
          </Button>
          <Button 
            variant="ghost" 
            className={`w-full justify-start ${
              pathname === "/laporan-keuangan" 
                ? "bg-[#1e293b] text-white" 
                : "text-slate-400 hover:bg-[#1e293b] hover:text-white"
            }`}
          >
            <BarChart className="mr-2 h-4 w-4" />
            <Link href="/laporan-keuangan">Laporan Keuangan</Link>
          </Button>
          <Button 
            variant="ghost" 
            className={`w-full justify-start ${
              pathname === "/berita" 
                ? "bg-[#1e293b] text-white" 
                : "text-slate-400 hover:bg-[#1e293b] hover:text-white"
            }`}
          >
            <FileText className="mr-2 h-4 w-4" />
            <Link href="/berita">Berita</Link>
          </Button>
        </div>
      </div>
      
      {/* Realtime clock and date */}
      <RealtimeClock />
    </div>
  )
}

export function MobileSidebar({ searchQuery = "", onSearchChange, onSearch }: SidebarProps) {
  return (
    <Sheet>
      <SheetTrigger asChild>
        <Button variant="ghost" size="icon" className="md:hidden">
          <Menu className="h-5 w-5 text-slate-400" />
          <span className="sr-only">Toggle Menu</span>
        </Button>
      </SheetTrigger>
      <SheetContent side="left" className="w-72 border-r border-[#1e293b] bg-[#0f172a] p-0">
        <div className="flex flex-col h-full">
          <Sidebar 
            searchQuery={searchQuery} 
            onSearchChange={onSearchChange}
            onSearch={onSearch} 
          />
          <div className="md:hidden">
            <RealtimeClock />
          </div>
        </div>
      </SheetContent>
    </Sheet>
  )
}