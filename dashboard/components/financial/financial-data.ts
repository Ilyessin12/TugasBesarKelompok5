export const staticFinancialData = {
  EntityName: "Adaro Energy Tbk",
  EntityCode: "ADRO",
  // Income Statement
  SalesAndRevenue: 1084004000,
  GrossProfit: 867681000,
  ProfitFromOperation: 754320000,
  ProfitLoss: 1854878000,
  // Balance Sheet
  Assets: 10472711000,
  CashAndCashEquivalents: 3311232000,
  ShortTermBankLoans: 0,
  LongTermBankLoans: 404361000,
  EquityAttributableToEquityOwnersOfParentEntity: 6772664000,
  // Cash Flow
  NetCashFlowOp: 1152758000,
  NetCashFlowInv: -582426000,
  NetCashFlowFin: -1333690000
}

export const calculateFinancialRatios = (data: typeof staticFinancialData) => {
  return {
    netProfitMargin: (data.ProfitLoss / data.SalesAndRevenue) * 100,
    grossProfitMargin: (data.GrossProfit / data.SalesAndRevenue) * 100,
    debtToEquityRatio: ((data.ShortTermBankLoans + data.LongTermBankLoans) / data.EquityAttributableToEquityOwnersOfParentEntity) * 100,
    returnOnAssets: (data.ProfitLoss / data.Assets) * 100,
    returnOnEquity: (data.ProfitLoss / data.EquityAttributableToEquityOwnersOfParentEntity) * 100
  }
}