import {
  CartesianGrid,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import type { Forecast } from '../api/types'
import { formatDate, formatMoney, formatMonth } from '../utils/format'
import './CashFlowChart.css'

interface CashFlowChartProps {
  forecast: Forecast
}

interface ChartRow {
  date: string
  actual: number | null
  projected: number | null
}

const compactMoney = new Intl.NumberFormat('en-CA', {
  style: 'currency',
  currency: 'CAD',
  currencyDisplay: 'narrowSymbol',
  notation: 'compact',
  maximumFractionDigits: 1,
})

/** Split points into two series; the as-of day sits in both so the lines join up. */
function toRows(forecast: Forecast): ChartRow[] {
  return forecast.points.map((p) => {
    const isToday = p.date === forecast.asOf
    return {
      date: p.date,
      actual: !p.projected ? p.balance : null,
      projected: p.projected || isToday ? p.balance : null,
    }
  })
}

export function CashFlowChart({ forecast }: CashFlowChartProps) {
  const rows = toRows(forecast)
  const monthTicks = rows.filter((r) => r.date.endsWith('-01')).map((r) => r.date)

  return (
    <section className="card cash-flow" aria-labelledby="cash-flow-title">
      <div className="cash-flow__header">
        <h2 id="cash-flow-title">Cash flow runway</h2>
        <ul className="cash-flow__legend" aria-label="Legend">
          <li className="is-actual">Actual</li>
          <li className="is-projected">Projected</li>
          <li className="is-goal">Goal</li>
        </ul>
      </div>

      <div className="cash-flow__chart">
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={rows} margin={{ top: 20, right: 16, bottom: 0, left: 0 }}>
            <CartesianGrid stroke="var(--border)" vertical={false} />
            <XAxis
              dataKey="date"
              ticks={monthTicks}
              tickFormatter={formatMonth}
              tick={{ fill: 'var(--muted)', fontSize: 12 }}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              tickFormatter={(value: number) => compactMoney.format(value)}
              tick={{ fill: 'var(--muted)', fontSize: 12 }}
              axisLine={false}
              tickLine={false}
              width={56}
            />
            <Tooltip
              formatter={(value) => formatMoney(Number(value))}
              labelFormatter={(label) => formatDate(String(label))}
              contentStyle={{ borderRadius: 12, border: '1px solid var(--border)' }}
            />
            <ReferenceLine
              y={forecast.targetAmount}
              stroke="var(--goal)"
              strokeDasharray="4 4"
              label={{
                value: `Goal ${formatMoney(forecast.targetAmount)}`,
                position: 'insideBottomRight',
                fill: 'var(--goal)',
                fontSize: 12,
              }}
            />
            <ReferenceLine
              x={forecast.asOf}
              stroke="var(--muted)"
              strokeDasharray="2 4"
              label={{ value: 'Today', position: 'top', fill: 'var(--muted)', fontSize: 12 }}
            />
            <Line
              name="Actual"
              dataKey="actual"
              stroke="var(--actual)"
              strokeWidth={3}
              dot={false}
              isAnimationActive={false}
            />
            <Line
              name="Projected"
              dataKey="projected"
              stroke="var(--projected)"
              strokeWidth={3}
              strokeDasharray="6 5"
              dot={false}
              isAnimationActive={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </section>
  )
}
