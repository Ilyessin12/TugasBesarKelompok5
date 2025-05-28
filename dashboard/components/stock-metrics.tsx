import { ArrowDown, ArrowUp, DollarSign, LineChart, TrendingUp, Users } from "lucide-react"

export function StockMetrics({ darkMode = false }) {
  const metrics = [
    {
      name: "P/E Ratio",
      value: "22.5x",
      change: "+1.2",
      isPositive: true,
      icon: LineChart,
      color: darkMode ? "text-blue-300" : "text-blue-600",
      bgColor: darkMode ? "bg-blue-900/50" : "bg-blue-100",
    },
    {
      name: "EPS (TTM)",
      value: "Rp 425",
      change: "+6.8%",
      isPositive: true,
      icon: DollarSign,
      color: darkMode ? "text-emerald-300" : "text-emerald-600",
      bgColor: darkMode ? "bg-emerald-900/50" : "bg-emerald-100",
    },
    {
      name: "Dividend Yield",
      value: "1.8%",
      change: "-0.2%",
      isPositive: false,
      icon: TrendingUp,
      color: darkMode ? "text-amber-300" : "text-amber-600",
      bgColor: darkMode ? "bg-amber-900/50" : "bg-amber-100",
    },
    {
      name: "Market Cap",
      value: "Rp 1,200T",
      change: "+2.3%",
      isPositive: true,
      icon: Users,
      color: darkMode ? "text-purple-300" : "text-purple-600",
      bgColor: darkMode ? "bg-purple-900/50" : "bg-purple-100",
    },
  ]

  return (
    <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
      {metrics.map((metric) => (
        <div
          key={metric.name}
          className={`rounded-lg ${darkMode ? "border-[#1e293b] bg-[#0f172a]/50" : "border border-[#e2e8f0]"} p-4`}
        >
          <div className="mb-2 flex items-center gap-2">
            <div className={`rounded-md ${metric.bgColor} p-1.5`}>
              <metric.icon className={`h-4 w-4 ${metric.color}`} />
            </div>
            <span className={`text-sm ${darkMode ? "text-slate-400" : "text-muted-foreground"}`}>{metric.name}</span>
          </div>
          <div className={`text-lg font-bold ${darkMode ? "text-white" : ""}`}>{metric.value}</div>
          <div className="mt-1 flex items-center gap-1 text-xs font-medium">
            {metric.isPositive ? (
              <ArrowUp className={darkMode ? "h-3 w-3 text-emerald-300" : "h-3 w-3 text-emerald-600"} />
            ) : (
              <ArrowDown className={darkMode ? "h-3 w-3 text-red-300" : "h-3 w-3 text-red-600"} />
            )}
            <span
              className={
                metric.isPositive
                  ? darkMode
                    ? "text-emerald-300"
                    : "text-emerald-600"
                  : darkMode
                    ? "text-red-300"
                    : "text-red-600"
              }
            >
              {metric.change}
            </span>
          </div>
        </div>
      ))}
    </div>
  )
}
