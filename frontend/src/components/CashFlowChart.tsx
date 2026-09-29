import {
  CartesianGrid,
  Line,
  LineChart,
  ReferenceArea,
  ReferenceDot,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import type { Forecast, StayWindow } from '../api/types'
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

interface ChartTooltipProps {
  active?: boolean
  label?: string | number
  rowsByDate: Map<string, ChartRow>
  stays: StayWindow[]
}

function ChartTooltip({ active, label, rowsByDate, stays }: ChartTooltipProps) {
  const row = typeof label === 'string' ? rowsByDate.get(label) : undefined
  if (!active || !row) return null
  const stay = stays.find((s) => s.startDate <= row.date && row.date <= s.endDate)
  const departure = stays.find((s) => s.startDate === row.date && s.upfrontCost > 0)
  const isProjected = row.actual === null

  return (
    <div className="cash-flow__tooltip">
      <p className="cash-flow__tooltip-date">{formatDate(row.date)}</p>
      <p className={isProjected ? 'is-projected' : 'is-actual'}>
        {isProjected ? 'Projected' : 'Balance'}: {formatMoney((isProjected ? row.projected : row.actual) ?? 0)}
      </p>
      {departure && <p className="is-cost">Flights + deposit −{formatMoney(departure.upfrontCost)}</p>}
      {stay && (
        <p className="cash-flow__tooltip-stay">
          In {stay.city} · {formatMoney(stay.monthlyBudget)}/mo budget
        </p>
      )}
    </div>
  )
}

export function CashFlowChart({ forecast }: CashFlowChartProps) {
  const rows = toRows(forecast)
  const rowsByDate = new Map(rows.map((r) => [r.date, r]))
  const monthTicks = rows.filter((r) => r.date.endsWith('-01')).map((r) => r.date)
  const departures = forecast.stays.filter((s) => s.upfrontCost > 0 && rowsByDate.has(s.startDate))

  return (
    <section className="card cash-flow" aria-labelledby="cash-flow-title">
      <div className="cash-flow__header">
        <h2 id="cash-flow-title">Cash flow runway</h2>
        <ul className="cash-flow__legend" aria-label="Legend">
          <li className="is-actual">Actual</li>
          <li className="is-projected">Projected</li>
          <li className="is-goal">Goal</li>
          {forecast.stays.length > 0 && <li className="is-stay">Exchange</li>}
        </ul>
      </div>

      <div className="cash-flow__chart">
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={rows} margin={{ top: 20, right: 16, bottom: 0, left: 0 }}>
            <CartesianGrid stroke="var(--border)" vertical={false} />
            {forecast.stays.map((s) => (
              <ReferenceArea
                key={`${s.city}-${s.startDate}`}
                x1={s.startDate}
                x2={s.endDate}
                fill="var(--stay)"
                fillOpacity={1}
                label={{ value: s.city, position: 'insideTop', fill: 'var(--stay-text)', fontSize: 12, fontWeight: 700 }}
              />
            ))}
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
            <Tooltip content={({ active, label }) => (
              <ChartTooltip active={active} label={label} rowsByDate={rowsByDate} stays={forecast.stays} />
            )} />
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
            {departures.map((s) => (
              <ReferenceDot
                key={`dep-${s.startDate}`}
                x={s.startDate}
                y={rowsByDate.get(s.startDate)?.projected ?? 0}
                r={5}
                fill="var(--card)"
                stroke="var(--projected)"
                strokeWidth={2}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </section>
  )
}
