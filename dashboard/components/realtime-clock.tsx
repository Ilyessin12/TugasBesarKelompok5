"use client"

import { useEffect, useState } from "react"
import { Clock, Calendar } from "lucide-react"

export function RealtimeClock() {
  const [time, setTime] = useState<string>("--:--:--")
  const [date, setDate] = useState<string>("-- --- ----")

  useEffect(() => {
    // Only update time on the client side
    const updateDateTime = () => {
      const now = new Date()
      setTime(now.toLocaleTimeString("id-ID"))
      
      // Format date as DD Month YYYY in Indonesian
      setDate(now.toLocaleDateString("id-ID", {
        day: "numeric",
        month: "long",
        year: "numeric"
      }))
    }
    
    // Update immediately
    updateDateTime()
    
    // Then update every second
    const interval = setInterval(updateDateTime, 1000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="hidden md:flex items-center gap-4">
      <div className="flex items-center gap-1.5 text-sm text-slate-400">
        <Calendar className="h-4 w-4" />
        <span>{date}</span>
      </div>
      <div className="flex items-center gap-1.5 text-sm text-slate-400">
        <Clock className="h-4 w-4" />
        <span>{time}</span>
      </div>
    </div>
  )
}