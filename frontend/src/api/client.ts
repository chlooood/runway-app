import axios from 'axios'
import type {
  ApiExpense,
  ApiForecast,
  ApiGoal,
  ApiIncomeEvent,
  City,
  Expense,
  Forecast,
  Goal,
  IncomeEvent,
} from './types'

const baseURL = import.meta.env.VITE_API_BASE_URL
if (!baseURL) {
  throw new Error('VITE_API_BASE_URL is not set (copy frontend/.env.example to frontend/.env)')
}

const http = axios.create({ baseURL })

// Money arrives as decimal strings; numbers are exact enough for display and charts.
const money = (value: string): number => Number(value)

const toIncomeEvent = (e: ApiIncomeEvent): IncomeEvent => ({ ...e, amount: money(e.amount) })

const toExpense = (e: ApiExpense): Expense => ({ ...e, amount: money(e.amount) })

const toGoal = (g: ApiGoal): Goal => ({
  id: g.id,
  name: g.name,
  targetAmount: money(g.target_amount),
  targetDate: g.target_date,
})

const moneyMap = (m: Record<string, string>): Record<string, number> =>
  Object.fromEntries(Object.entries(m).map(([key, value]) => [key, money(value)]))

const toForecast = (f: ApiForecast): Forecast => ({
  goalId: f.goal_id,
  asOf: f.as_of,
  city: f.city,
  currentBalance: money(f.current_balance),
  monthlySpendRate: money(f.monthly_spend_rate),
  cityMonthlyRates: moneyMap(f.city_monthly_rates),
  categoryMonthlyRates: moneyMap(f.category_monthly_rates),
  knownFutureIncome: money(f.known_future_income),
  projectedBalance: money(f.projected_balance),
  targetAmount: money(f.target_amount),
  targetDate: f.target_date,
  gap: money(f.gap),
  onTrack: f.on_track,
  monthlyCutNeeded: money(f.monthly_cut_needed),
  suggestedCuts: moneyMap(f.suggested_cuts),
  cutsCloseGap: f.cuts_close_gap,
  stays: f.stays.map((s) => ({
    label: s.label,
    city: s.city,
    startDate: s.start_date,
    endDate: s.end_date,
    monthlyBudget: money(s.monthly_budget),
    upfrontCost: money(s.upfront_cost),
  })),
  horizonEnd: f.horizon_end,
  projectedEndBalance: money(f.projected_end_balance),
  lowestBalance: money(f.lowest_balance),
  lowestBalanceDate: f.lowest_balance_date,
  runsOutOn: f.runs_out_on,
  points: f.points.map((p) => ({ ...p, balance: money(p.balance) })),
})

export async function getGoals(): Promise<Goal[]> {
  const { data } = await http.get<ApiGoal[]>('/goals')
  return data.map(toGoal)
}

export async function getIncomeEvents(): Promise<IncomeEvent[]> {
  const { data } = await http.get<ApiIncomeEvent[]>('/income-events')
  return data.map(toIncomeEvent)
}

export async function getExpenses(filters: { city?: City; category?: string } = {}): Promise<Expense[]> {
  const { data } = await http.get<ApiExpense[]>('/expenses', { params: filters })
  return data.map(toExpense)
}

export async function getForecast(goalId: number, city?: City): Promise<Forecast> {
  const { data } = await http.get<ApiForecast>(`/goals/${goalId}/forecast`, {
    params: city ? { city } : {},
  })
  return toForecast(data)
}
