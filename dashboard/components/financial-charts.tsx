"use client"
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  Cell,
  Legend,
  RadialBarChart,
  RadialBar,
  Label
} from "recharts"

interface ChartData {
  name: string;
  value: number;
}

type FinancialChartProps = {
  data: {
    financial: {
      income: Array<{ metric: string, value: number }>
      balance: Array<{ metric: string, value: number }>
      cashflow: Array<{ metric: string, value: number }>
    }
  }
}

export function IncomeChart({ data }: FinancialChartProps) {
  const chartData = [
    { name: 'Revenue', value: data.financial.income[0].value },
    { name: 'Gross Profit', value: data.financial.income[1].value },
    { name: 'Operating Profit', value: data.financial.income[2].value },
    { name: 'Net Profit', value: data.financial.income[3].value }
  ]

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
        <XAxis dataKey="name" stroke="#94a3b8" />
        <YAxis stroke="#94a3b8" />
        <Tooltip
          contentStyle={{
            backgroundColor: "#0f172a",
            border: "1px solid #1e293b",
            borderRadius: "6px"
          }}
          labelStyle={{ color: "#e2e8f0" }}
        />
        <Bar dataKey="value" fill="#818cf8" />
      </BarChart>
    </ResponsiveContainer>
  )
}

export function BalanceChart({ data }: { data: any }) {
  const chartData = [
    { name: 'Assets', value: data.financial.balance[0].value },
    { name: 'Liabilities', value: data.financial.balance[2].value + data.financial.balance[3].value },
    { name: 'Equity', value: data.financial.balance[4].value }
  ]

  const COLORS = ['#818cf8', '#f43f5e', '#22c55e']

  return (
    <ResponsiveContainer width="100%" height={300}>
      <PieChart>
        <Pie
          data={chartData}
          dataKey="value"
          nameKey="name"
          cx="50%"
          cy="50%"
          outerRadius={100}
          fill="#8884d8"
          label
        >
          {chartData.map((entry: ChartData, index: number) => (
            <Cell key={`cell-${index}`} fill={COLORS[index]} />
          ))}
        </Pie>
        <Tooltip
          contentStyle={{
            backgroundColor: "#0f172a",
            border: "1px solid #1e293b",
            borderRadius: "6px"
          }}
          labelStyle={{ color: "#e2e8f0" }}
        />
      </PieChart>
    </ResponsiveContainer>
  )
}

export function CashFlowChart({ data }: { data: any }) {
  const chartData = data.financial.cashflow.map((item: any) => ({
    name: item.metric.replace('Arus Kas dari ', ''),
    value: item.value
  }))

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
        <XAxis dataKey="name" stroke="#94a3b8" />
        <YAxis stroke="#94a3b8" />
        <Tooltip
          contentStyle={{
            backgroundColor: "#0f172a",
            border: "1px solid #1e293b",
            borderRadius: "6px"
          }}
          labelStyle={{ color: "#e2e8f0" }}
        />
        <Bar dataKey="value" fill="#818cf8">
          {chartData.map((entry: ChartData, index: number) => (
            <Cell 
              key={`cell-${index}`}
              fill={entry.value >= 0 ? '#22c55e' : '#f43f5e'}
            />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}

export function AssetCompositionChart({ data }: { data: any }) {
  const chartData = [
    { name: 'Kas & Setara Kas', value: data.CashAndCashEquivalents },
    { name: 'Aset Lainnya', value: data.Assets - data.CashAndCashEquivalents }
  ]

  const COLORS = ['#22c55e', '#818cf8']

  return (
    <ResponsiveContainer width="100%" height={300}>
      <PieChart>
        <Pie
          data={chartData}
          dataKey="value"
          nameKey="name"
          cx="50%"
          cy="50%"
          outerRadius={100}
          fill="#8884d8"
          label={(entry) => `${entry.name}`}
          labelLine={true}
        >
          {chartData.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={COLORS[index]} />
          ))}
        </Pie>
        <Tooltip
          formatter={(value: any) => `Rp. ${new Intl.NumberFormat().format(value)}`}
          contentStyle={{
            backgroundColor: "#1e293b",
            border: "1px solid #334155",
            borderRadius: "6px",
            padding: "8px 12px",
            boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
            fontSize: "14px"
          }}
          labelStyle={{ 
            color: "#f8fafc", 
            fontWeight: "600", 
            marginBottom: "4px",
            fontSize: "14px"
          }}
          itemStyle={{ color: "#cbd5e1" }}
          wrapperStyle={{ outline: "none" }}
        />
        <Legend 
          verticalAlign="bottom" 
          height={36}
          wrapperStyle={{
            paddingTop: "20px"
          }}
        />
      </PieChart>
    </ResponsiveContainer>
  )
}

export function EquityLiabilitiesChart({ data }: { data: any }) {
  const totalLiabilities = data.Assets - data.EquityAttributableToEquityOwnersOfParentEntity
  const chartData = [
    { name: 'Ekuitas', value: data.EquityAttributableToEquityOwnersOfParentEntity },
    { name: 'Liabilitas', value: totalLiabilities }
  ]

  const COLORS = ['#22c55e', '#f43f5e']

  return (
    <ResponsiveContainer width="100%" height={300}>
      <PieChart>
        <Pie
          data={chartData}
          dataKey="value"
          nameKey="name"
          cx="50%"
          cy="50%"
          outerRadius={100}
          fill="#8884d8"
          label={(entry) => `${entry.name}`}
          labelLine={true}
        >
          {chartData.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={COLORS[index]} />
          ))}
        </Pie>
        <Tooltip
          formatter={(value: any) => `Rp. ${new Intl.NumberFormat().format(value)}`}
          contentStyle={{
            backgroundColor: "#1e293b",
            border: "1px solid #334155",
            borderRadius: "6px",
            padding: "8px 12px",
            boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
            fontSize: "14px"
          }}
          labelStyle={{ 
            color: "#f8fafc", 
            fontWeight: "600", 
            marginBottom: "4px",
            fontSize: "14px"
          }}
          itemStyle={{ color: "#cbd5e1" }}
          wrapperStyle={{ outline: "none" }}
        />
        <Legend 
          verticalAlign="bottom" 
          height={36}
          wrapperStyle={{
            paddingTop: "20px"
          }}
        />
      </PieChart>
    </ResponsiveContainer>
  )
}

export function ProfitLossFlowChart({ data }: { data: any }) {
  const chartData = [
    { name: 'Pendapatan', value: data.SalesAndRevenue },
    { name: 'Laba Kotor', value: data.GrossProfit },
    { name: 'Laba Operasi', value: data.ProfitFromOperation },
    { name: 'Laba Bersih', value: data.ProfitLoss }
  ]

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
        <XAxis dataKey="name" stroke="#94a3b8" />
        <YAxis stroke="#94a3b8" />
        <Tooltip
          formatter={(value: any) => `Rp. ${new Intl.NumberFormat().format(value)}`}
          contentStyle={{
            backgroundColor: "#0f172a",
            border: "1px solid #1e293b",
            borderRadius: "6px"
          }}
          labelStyle={{ color: "#e2e8f0" }}
        />
        <Bar dataKey="value" fill="#818cf8" />
      </BarChart>
    </ResponsiveContainer>
  )
}

export function ROEGaugeChart({ data }: { data: any }) {
  const roe = (data.ProfitLoss / data.EquityAttributableToEquityOwnersOfParentEntity) * 100
  const chartData = [
    {
      name: 'ROE',
      value: roe,
      fill: roe < 10 ? '#f43f5e' : roe < 15 ? '#eab308' : '#22c55e'
    }
  ]

  return (
    <ResponsiveContainer width="100%" height={300}>
      <RadialBarChart
        innerRadius={60}
        outerRadius={100}
        barSize={10}
        data={chartData}
        startAngle={180}
        endAngle={0}
      >
        <RadialBar
          dataKey="value"
          background={{ fill: '#1e293b' }}
        />
        <text
          x="50%"
          y="50%"
          textAnchor="middle"
          dominantBaseline="middle"
          fill="#e2e8f0"
          fontSize="32"
          fontWeight="bold"
        >
          {`${roe.toFixed(1)}%`}
        </text>
        <Tooltip
          formatter={(value: any) => `${value.toFixed(2)}%`}
          contentStyle={{
            backgroundColor: "#1e293b",
            border: "1px solid #334155",
            borderRadius: "6px",
            padding: "8px 12px",
            boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
            fontSize: "14px"
          }}
          labelStyle={{ 
            color: "#f8fafc", 
            fontWeight: "600", 
            marginBottom: "4px" 
          }}
          itemStyle={{ color: "#cbd5e1" }}
        />
      </RadialBarChart>
    </ResponsiveContainer>
  )
}