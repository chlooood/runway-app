// Response shapes from the Runway API.
//
// `Api*` types mirror the JSON exactly: money arrives as a decimal string
// (e.g. "9000.00") so the backend never loses precision. The un-prefixed
// types are what components use, with money parsed into numbers.

export type City = string

// ---- Wire format (matches backend/app/schemas) ----

export interface ApiIncomeEvent {
  id: number
  date: string // YYYY-MM-DD
  amount: string
  label: string
}

export interface ApiExpense {
  id: number
  date: string
  amount: string
  category: string
  city: City
}

export interface ApiGoal {
  id: number
  name: string
  target_amount: string
  target_date: string
}

export interface ApiForecastPoint {
  date: string
  balance: string
  projected: boolean
}

export interface ApiForecast {
  goal_id: number
  as_of: string
  city: City | null
  current_balance: string
  monthly_spend_rate: string
  city_monthly_rates: Record<City, string>
  known_future_income: string
  projected_balance: string
  target_amount: string
  target_date: string
  gap: string
  on_track: boolean
  points: ApiForecastPoint[]
}

// ---- App types (money as numbers) ----

export interface IncomeEvent {
  id: number
  date: string
  amount: number
  label: string
}

export interface Expense {
  id: number
  date: string
  amount: number
  category: string
  city: City
}

export interface Goal {
  id: number
  name: string
  targetAmount: number
  targetDate: string
}

export interface ForecastPoint {
  date: string
  balance: number
  projected: boolean
}

export interface Forecast {
  goalId: number
  asOf: string
  city: City | null
  currentBalance: number
  monthlySpendRate: number
  cityMonthlyRates: Record<City, number>
  knownFutureIncome: number
  projectedBalance: number
  targetAmount: number
  targetDate: string
  gap: number
  onTrack: boolean
  points: ForecastPoint[]
}
