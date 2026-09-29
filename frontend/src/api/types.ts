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
  city: City | null // projected points: whose cost baseline applied that day
}

export interface ApiStayWindow {
  label: string
  city: City
  start_date: string
  end_date: string
  monthly_budget: string
  upfront_cost: string
}

export interface ApiForecast {
  goal_id: number
  as_of: string
  city: City | null
  current_balance: string
  monthly_spend_rate: string
  city_monthly_rates: Record<City, string>
  category_monthly_rates: Record<string, string>
  known_future_income: string
  projected_balance: string
  target_amount: string
  target_date: string
  gap: string
  on_track: boolean
  monthly_cut_needed: string
  suggested_cuts: Record<string, string>
  cuts_close_gap: boolean
  stays: ApiStayWindow[]
  horizon_end: string
  projected_end_balance: string
  lowest_balance: string
  lowest_balance_date: string
  runs_out_on: string | null
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
  city: City | null
}

export interface StayWindow {
  label: string
  city: City
  startDate: string
  endDate: string
  monthlyBudget: number
  upfrontCost: number
}

export interface Forecast {
  goalId: number
  asOf: string
  city: City | null
  currentBalance: number
  monthlySpendRate: number
  cityMonthlyRates: Record<City, number>
  categoryMonthlyRates: Record<string, number> // selected city, largest first
  knownFutureIncome: number
  projectedBalance: number
  targetAmount: number
  targetDate: string
  gap: number
  onTrack: boolean
  monthlyCutNeeded: number
  suggestedCuts: Record<string, number>
  cutsCloseGap: boolean
  stays: StayWindow[] // planned stays (e.g. the exchange), projected on their own budgets
  horizonEnd: string
  projectedEndBalance: number
  lowestBalance: number
  lowestBalanceDate: string
  runsOutOn: string | null
  points: ForecastPoint[]
}
