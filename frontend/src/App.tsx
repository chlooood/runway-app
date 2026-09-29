import { useState } from 'react'
import type { City } from './api/types'
import { CashFlowChart } from './components/CashFlowChart'
import { CategoryBreakdown } from './components/CategoryBreakdown'
import { CityToggle } from './components/CityToggle'
import { GoalProgressCard } from './components/GoalProgressCard'
import { useRunwayData } from './hooks/useRunwayData'
import './App.css'

function App() {
  const [city, setCity] = useState<City | null>(null)
  const data = useRunwayData(city)

  return (
    <main className="app">
      <header className="app__header">
        <div>
          <h1>Runway</h1>
          <p className="app__tagline">Hi! Here's how your savings are shaping up.</p>
        </div>
        {data.status === 'ready' && (
          <CityToggle
            rates={data.forecast.cityMonthlyRates}
            value={city ?? data.forecast.city}
            onChange={setCity}
            disabled={data.refreshing}
          />
        )}
      </header>

      {data.status === 'loading' && <p className="app__message">Loading your runway…</p>}
      {data.status === 'error' && <p className="app__message is-error">{data.message}</p>}
      {data.status === 'empty' && (
        <p className="app__message">No savings goal yet — run the seed script or add one to get started.</p>
      )}

      {data.status === 'ready' && (
        <div className={`app__content ${data.refreshing ? 'is-refreshing' : ''}`}>
          <GoalProgressCard goal={data.goal} forecast={data.forecast} />
          <CashFlowChart forecast={data.forecast} />
          <CategoryBreakdown
            city={data.forecast.city}
            rates={data.forecast.categoryMonthlyRates}
            cuts={data.forecast.suggestedCuts}
          />
        </div>
      )}
    </main>
  )
}

export default App
