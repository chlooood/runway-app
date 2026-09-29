import type { City } from '../api/types'
import { formatMoney } from '../utils/format'
import './CityToggle.css'

interface CityToggleProps {
  /** Cities with spending history, mapped to their average monthly spend. */
  rates: Record<City, number>
  value: City | null
  onChange: (city: City) => void
  disabled?: boolean
}

export function CityToggle({ rates, value, onChange, disabled = false }: CityToggleProps) {
  const cities = Object.keys(rates).sort()
  return (
    <div className="city-toggle" role="group" aria-label="Cost-of-living baseline">
      {cities.map((city) => (
        <button
          key={city}
          type="button"
          className="city-toggle__option"
          aria-pressed={city === value}
          disabled={disabled}
          onClick={() => onChange(city)}
        >
          <span className="city-toggle__name">{city}</span>
          <span className="city-toggle__rate">{formatMoney(rates[city])}/mo</span>
        </button>
      ))}
    </div>
  )
}
