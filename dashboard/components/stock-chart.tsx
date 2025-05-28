"use client"

import { useEffect, useState } from "react"
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"

// Ubah fungsi getMonthName menjadi getFormattedDate
const getFormattedDate = (dateStr: string) => {
  const [day, month, year] = dateStr.split("/")
  const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
  return `${monthNames[parseInt(month, 10) - 1]} ${year}`
}

type StockChartProps = {
  darkMode?: boolean
  emiten?: string
  onDataUpdate?: (data: any) => void  // Tambahkan prop ini

}

export function StockChart({ darkMode = false, emiten, onDataUpdate }: StockChartProps) {
  const [data, setData] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [windowWidth, setWindowWidth] = useState(0)

  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true)
        const apiUrl = 'https://1d11-54-88-52-186.ngrok-free.app'
        const res = await fetch(`${apiUrl}/api/stock/${emiten}?period=monthly`,{
          headers: {
            "ngrok-skip-browser-warning": "true",
          },
        })
        
        if (!res.ok) {
          throw new Error('Network response was not ok')
        }

        const jsonData = await res.json()
        
        // Transform the data for the chart - updated to match API format
        const transformedData = jsonData.map((item: any) => ({
          name: getFormattedDate(item.Date),
          price: item.Close,
          high: item.High,
          low: item.Low
        }))

        setData(transformedData)
        
        // Update parent component with latest data
        if (onDataUpdate) {
          const latestData = jsonData[jsonData.length - 1]
          onDataUpdate({
            symbol: emiten,
            price: latestData.Close,
            // Calculate change percentage
            change: ((latestData.Close - jsonData[jsonData.length - 2].Close) / jsonData[jsonData.length - 2].Close * 100).toFixed(2) + '%'
          })
        }

      } catch (error) {
        console.error("Error fetching stock data:", error)
        setError('Failed to load data')
        setData([])
        if (onDataUpdate) {
          onDataUpdate(null)
        }
      } finally {
        setIsLoading(false)
      }
    }

    if (emiten) {
      fetchData()
    }
  }, [emiten])

  useEffect(() => {
    setWindowWidth(window.innerWidth)

    const handleResize = () => {
      setWindowWidth(window.innerWidth)
    }

    window.addEventListener("resize", handleResize)
    return () => window.removeEventListener("resize", handleResize)
  }, [])

  const formatRupiah = (value: number) => {
    return `Rp ${value.toLocaleString("id-ID")}`
  }

  // Only show loading state initially
  if (isLoading && data.length === 0) {
    return (
      <div className="h-[300px] w-full flex items-center justify-center text-slate-400">
        <div className="flex flex-col items-center gap-2">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-slate-400"></div>
          <p>Loading data...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="h-[300px] w-full flex items-center justify-center text-slate-400">
        <p>Failed to load chart data</p>
      </div>
    )
  }

  if (data.length === 0) {
    return (
      <div className="h-[300px] w-full flex items-center justify-center text-slate-400">
        <div className="flex flex-col items-center gap-2">
          <p>No data available for {emiten}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="h-[300px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart
          data={data}
          margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
        >
          <defs>
            <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
              <stop
                offset="5%"
                stopColor={darkMode ? "#818cf8" : "#10b981"}
                stopOpacity={0.3}
              />
              <stop
                offset="95%"
                stopColor={darkMode ? "#818cf8" : "#10b981"}
                stopOpacity={0}
              />
            </linearGradient>
          </defs>
          <CartesianGrid
            strokeDasharray="3 3"
            vertical={false}
            stroke={darkMode ? "#1e293b" : "#e2e8f0"}
          />
          <XAxis
            dataKey="name"
            tickLine={false}
            axisLine={false}
            tick={{
              fontSize: windowWidth < 500 ? 10 : 12,
              fill: darkMode ? "#94a3b8" : "#64748b",
            }}
          />
          <YAxis
            tickFormatter={formatRupiah}
            tickLine={false}
            axisLine={false}
            tick={{
              fontSize: windowWidth < 500 ? 10 : 12,
              fill: darkMode ? "#94a3b8" : "#64748b",
            }}
            width={80}
          />
          <Tooltip
            formatter={(value, name) => {
              switch(name) {
                case 'price':
                  return [`${formatRupiah(Number(value))}`, "Close"]
                case 'high':
                  return [`${formatRupiah(Number(value))}`, "High"]
                case 'low':
                  return [`${formatRupiah(Number(value))}`, "Low"]
                default:
                  return [value, name]
              }
            }}
            labelFormatter={(label) => `Tanggal: ${label}`}
            contentStyle={{
              borderRadius: "8px",
              border: darkMode ? "1px solid #1e293b" : "1px solid #e2e8f0",
              backgroundColor: darkMode ? "#0f172a" : "#ffffff",
              color: darkMode ? "#e2e8f0" : "#1e293b",
              boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
            }}
          />
          <Area
            type="monotone"
            dataKey="price"
            stroke={darkMode ? "#818cf8" : "#10b981"}
            strokeWidth={2}
            fill="url(#colorPrice)"
            activeDot={{
              r: 6,
              strokeWidth: 0,
              fill: darkMode ? "#818cf8" : "#10b981",
            }}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}
