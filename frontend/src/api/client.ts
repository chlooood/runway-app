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

const toForecast = (f: ApiForecast): Forecast => ({
  goalId: f.goal_id,
  asOf: f.as_of,
  city: f.city,
  currentBalance: money(f.current_balance),
  monthlySpendRate: money(f.monthly_spend_rate),
  cityMonthlyRates: Object.fromEntries(
    Object.entries(f.city_monthly_rates).map(([city, rate]) => [city, money(rate)]),
  ),
  knownFutureIncome: money(f.known_future_income),
  projectedBalance: money(f.projected_balance),
  targetAmount: money(f.target_amount),
  targetDate: f.target_date,
  gap: money(f.gap),
  onTrack: f.on_track,
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
