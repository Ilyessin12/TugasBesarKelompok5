"use client"

import { useEffect, useState } from "react"
import { format, parseISO } from "date-fns" // Make sure you have date-fns installed
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"
import { API } from "@/services/api"
import { StockData, StockDataPoint } from "@/types/api"

type StockChartProps = {
  darkMode?: boolean
  emiten?: string
  period?: string
  onDataUpdate?: (data: StockData | null) => void
}

export function StockChart({ darkMode = false, emiten, period = 'monthly', onDataUpdate }: StockChartProps) {
  const [data, setData] = useState<Array<{name: string, price: number, high: number, low: number}>>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [windowWidth, setWindowWidth] = useState(0)

  useEffect(() => {
    const fetchData = async () => {
      if (!emiten) {
        setIsLoading(false);
        return;
      }

      try {
        setIsLoading(true);
        
        // Map UI period values to API period values
        let apiPeriod = period.toLowerCase();
        if (apiPeriod === '3d') apiPeriod = '3days';
        if (apiPeriod === '1w') apiPeriod = '1week';
        if (apiPeriod === '1m') apiPeriod = '1month'; 
        if (apiPeriod === '3m') apiPeriod = '3month';
        if (apiPeriod === '1y' || apiPeriod === '3y' || apiPeriod === '5y') {
          // These are already in the correct format
        }
        if (apiPeriod === 'all') apiPeriod = 'all';
        
        const stockData = await API.getStockData(emiten, apiPeriod);
        
        // Transform the data for the chart - updated to match API format
        const transformedData = stockData.map((item: StockDataPoint) => ({
          name: getFormattedDate(item.Date),
          price: item.Close,
          high: item.High,
          low: item.Low
        }));

        setData(transformedData);
        
        // Update parent component with latest data
        if (onDataUpdate && stockData.length >= 2) {
          const latestData = stockData[stockData.length - 1];
          const firstData = stockData[0]; // Changed to first data point in period
          
          // Calculate change over the entire period
          const changePercentValue = ((latestData.Close - firstData.Close) / firstData.Close * 100);
          const changePercent = changePercentValue.toFixed(2);
          const changePrefix = changePercentValue > 0 ? '+' : ''; // Add plus sign for positive values
          
          onDataUpdate({
            symbol: emiten,
            price: latestData.Close,
            change: `${changePrefix}${changePercent}%`,
            data: stockData
          });
        }

      } catch (error) {
        console.error("Error fetching stock data:", error);
        setError('Failed to load data');
        setData([]);
        if (onDataUpdate) {
          onDataUpdate(null);
        }
      } finally {
        setIsLoading(false);
      }
    };

    if (emiten) {
      fetchData();
    }
  }, [emiten, period]); // Add period as dependency to re-fetch when it changes

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

  // Updated date formatter function that returns shorter format for X-axis
  const getFormattedDate = (dateString: string) => {
    try {
      const date = parseISO(dateString);
      // For X-axis labels, use a shorter format
      return format(date, 'MMM yyyy');
    } catch (error) {
      return dateString;
    }
  }

  // New formatter function specifically for tooltip that includes day
  const getDetailedDate = (dateString: string) => {
    try {
      const date = parseISO(dateString);
      // For tooltip, use a more detailed format with day included
      return format(date, 'dd MMM yyyy');
    } catch (error) {
      return dateString;
    }
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
            // Add these properties to make price changes more visible
            padding={{ top: 10, bottom: 10 }}
            allowDataOverflow={true}
            scale="linear"
            // Custom domain calculation for better visualization
            domain={[
              (dataMin: number) => {
                // Set lower bound to be slightly below minimum value (e.g., 5% lower)
                return Math.floor(dataMin * 0.98);
              },
              (dataMax: number) => {
                // Set upper bound to be slightly above maximum value (e.g., 5% higher)
                return Math.ceil(dataMax * 1.02);
              }
            ]}
          />
          <Tooltip            formatter={(value: any, name: string) => {
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
            labelFormatter={(label: any) => `Tanggal: ${label}`}
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
