import type { StayWindow } from '../api/types'
import { capitalize, formatMoney } from '../utils/format'
import './CategoryBreakdown.css'

interface CategoryBreakdownProps {
  city: string | null
  /** Average monthly spend per category, largest first. */
  rates: Record<string, number>
  /** Suggested monthly cut per category, if the goal is off pace. */
  cuts: Record<string, number>
  /** Planned stays: budgeted, so shown as a note rather than as bars. */
  stays: StayWindow[]
}

export function CategoryBreakdown({ city, rates, cuts, stays }: CategoryBreakdownProps) {
  const rows = Object.entries(rates)
  const max = Math.max(...rows.map(([, amount]) => amount), 1)

  return (
    <section className="card breakdown" aria-labelledby="breakdown-title">
      <h2 id="breakdown-title">Where it goes{city && ` in ${city}`}</h2>
      <p className="breakdown__sub">Average per month</p>

      {rows.length === 0 ? (
        <p className="breakdown__empty">No spending recorded yet.</p>
      ) : (
        <ul className="breakdown__list">
          {rows.map(([category, amount]) => (
            <li key={category} className="breakdown__row">
              <span className="breakdown__label">{capitalize(category)}</span>
              <span className="breakdown__track" aria-hidden="true">
                <span className="breakdown__bar" style={{ width: `${(amount / max) * 100}%` }} />
              </span>
              <span className="breakdown__amount">
                {formatMoney(amount)}
                {cuts[category] !== undefined && (
                  <span className="breakdown__cut"> −{formatMoney(cuts[category])}</span>
                )}
              </span>
            </li>
          ))}
        </ul>
      )}

      {stays.map((s) => (
        <p key={`${s.city}-${s.startDate}`} className="breakdown__stay">
          {s.city} budget: <strong>{formatMoney(s.monthlyBudget)}/mo</strong> (planned)
        </p>
      ))}
    </section>
  )
}
