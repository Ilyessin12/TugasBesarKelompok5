import { CalendarIcon, ExternalLink } from "lucide-react"

interface NewsCardProps {
  title: string
  summary: string
  date: string
  source: string
  darkMode?: boolean
}

export function NewsCard({ title, summary, date, source, darkMode = false }: NewsCardProps) {
  return (
    <div className={`px-6 py-4 ${darkMode ? "hover:bg-[#1e293b]/50" : "hover:bg-slate-50/50"} transition-colors`}>
      <h3
        className={`font-medium ${darkMode ? "text-white hover:text-indigo-300" : "hover:text-teal-600"} cursor-pointer`}
      >
        {title}
      </h3>
      <p className={`mt-1 text-sm ${darkMode ? "text-slate-400" : "text-muted-foreground"} line-clamp-2`}>{summary}</p>
      <div
        className={`mt-2 flex items-center justify-between text-xs ${darkMode ? "text-slate-500" : "text-muted-foreground"}`}
      >
        <div className="flex items-center gap-1">
          <CalendarIcon className="h-3 w-3" />
          <span>{date}</span>
        </div>
        <div className="flex items-center gap-1">
          <span>{source}</span>
          <ExternalLink className="h-3 w-3" />
        </div>
      </div>
    </div>
  )
}
