import type { Forecast, Goal } from '../api/types'
import { capitalize, formatDate, formatMoney, formatShortDate } from '../utils/format'
import './GoalProgressCard.css'

interface GoalProgressCardProps {
  goal: Goal
  forecast: Forecast
}

/** What happens after the goal date, through any planned stays (e.g. the exchange). */
function StayOutlook({ forecast }: { forecast: Forecast }) {
  const { stays, runsOutOn, projectedEndBalance } = forecast
  if (stays.length === 0) return null

  if (runsOutOn) {
    const where = forecast.points.find((p) => p.date === runsOutOn)?.city
    return (
      <p className="goal-card__outlook is-short">
        Heads up: you'd run out around <strong>{formatShortDate(runsOutOn)}</strong>
        {where && ` in ${where}`}.
      </p>
    )
  }

  const cities = [...new Set(stays.map((s) => s.city))].join(' & ')
  const range = `${formatShortDate(stays[0].startDate)}–${formatShortDate(stays[stays.length - 1].endDate)}`
  return (
    <p className="goal-card__outlook">
      Through {cities} ({range}): you'd finish with about{' '}
      <strong>{formatMoney(projectedEndBalance)}</strong>.
    </p>
  )
}

/** Projected balance at the target date vs the goal, with an on-pace badge and suggested cuts. */
export function GoalProgressCard({ goal, forecast }: GoalProgressCardProps) {
  const { projectedBalance, targetAmount, onTrack, gap, suggestedCuts, monthlyCutNeeded } = forecast
  const progress = Math.max(0, Math.min(projectedBalance / targetAmount, 1))
  const cuts = Object.entries(suggestedCuts)

  return (
    <section className="card goal-card" aria-labelledby="goal-title">
      <div className="goal-card__header">
        <div>
          <p className="goal-card__eyebrow">Your goal</p>
          <h2 id="goal-title">{goal.name}</h2>
        </div>
        <span className={`goal-card__badge ${onTrack ? 'is-good' : 'is-short'}`}>
          {onTrack ? '✓ On track' : `About ${formatMoney(-gap)} short`}
        </span>
      </div>

      <p className="goal-card__headline">
        By <strong>{formatDate(goal.targetDate)}</strong> you're projected to have{' '}
        <strong>{formatMoney(projectedBalance)}</strong> of your {formatMoney(targetAmount)} goal.
      </p>

      <div
        className="goal-card__bar"
        role="progressbar"
        aria-label="Projected progress toward goal"
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={Math.round(progress * 100)}
      >
        <div
          className={`goal-card__fill ${onTrack ? 'is-good' : 'is-short'}`}
          style={{ width: `${progress * 100}%` }}
        />
      </div>

      {onTrack ? (
        <p className="goal-card__note">
          Nice — that leaves about <strong>{formatMoney(gap)}</strong> to spare.
        </p>
      ) : (
        <div className="goal-card__cuts">
          <p>
            To close the gap, trim about <strong>{formatMoney(monthlyCutNeeded)}/month</strong>
            {cuts.length > 0 && ' from:'}
          </p>
          {cuts.length > 0 && (
            <ul>
              {cuts.map(([category, amount]) => (
                <li key={category}>
                  {capitalize(category)} <span>−{formatMoney(amount)}/mo</span>
                </li>
              ))}
            </ul>
          )}
          {!forecast.cutsCloseGap && (
            <p className="goal-card__warning">
              Even cutting all flexible spending won't quite get there — extra income or a later
              date might help.
            </p>
          )}
        </div>
      )}

      <StayOutlook forecast={forecast} />

      <p className="goal-card__meta">
        Right now: {formatMoney(forecast.currentBalance)} saved · spending about{' '}
        {formatMoney(forecast.monthlySpendRate)}/month
        {forecast.city && ` in ${forecast.city}`}
      </p>
    </section>
  )
}
