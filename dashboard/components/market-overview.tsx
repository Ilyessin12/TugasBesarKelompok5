import { TrendingDown, TrendingUp } from "lucide-react"

import { Card, CardContent } from "@/components/ui/card"

export function MarketOverview({ darkMode = false }) {
  const marketData = [
    {
      name: "IHSG",
      value: "7,250.45",
      change: "+0.75%",
      isPositive: true,
      color: darkMode ? "bg-blue-900/50" : "bg-blue-100",
      textColor: darkMode ? "text-blue-300" : "text-blue-700",
    },
    {
      name: "LQ45",
      value: "980.32",
      change: "+0.82%",
      isPositive: true,
      color: darkMode ? "bg-indigo-900/50" : "bg-indigo-100",
      textColor: darkMode ? "text-indigo-300" : "text-indigo-700",
    },
    {
      name: "IDX30",
      value: "520.15",
      change: "+0.68%",
      isPositive: true,
      color: darkMode ? "bg-purple-900/50" : "bg-purple-100",
      textColor: darkMode ? "text-purple-300" : "text-purple-700",
    },
    {
      name: "JII",
      value: "610.25",
      change: "-0.12%",
      isPositive: false,
      color: darkMode ? "bg-amber-900/50" : "bg-amber-100",
      textColor: darkMode ? "text-amber-300" : "text-amber-700",
    },
  ]

  return (
    <>
      {marketData.map((item) => (
        <Card
          key={item.name}
          className={darkMode ? "border-[#1e293b] bg-[#0f172a] shadow-lg" : "border-none bg-white shadow-sm"}
        >
          <CardContent className="flex items-center justify-between p-4">
            <div className="flex items-center gap-3">
              <div className={`flex h-10 w-10 items-center justify-center rounded-md ${item.color} ${item.textColor}`}>
                {item.isPositive ? <TrendingUp className="h-5 w-5" /> : <TrendingDown className="h-5 w-5" />}
              </div>
              <div>
                <p className={`text-sm font-medium ${darkMode ? "text-slate-400" : "text-muted-foreground"}`}>
                  {item.name}
                </p>
                <p className={`text-xl font-bold ${darkMode ? "text-white" : ""}`}>{item.value}</p>
              </div>
            </div>
            <div
              className={`rounded-full px-2 py-1 text-sm font-medium ${
                item.isPositive
                  ? darkMode
                    ? "bg-emerald-900/50 text-emerald-300"
                    : "bg-emerald-50 text-emerald-600"
                  : darkMode
                    ? "bg-red-900/50 text-red-300"
                    : "bg-red-50 text-red-600"
              }`}
            >
              {item.change}
            </div>
          </CardContent>
        </Card>
      ))}
    </>
  )
}
