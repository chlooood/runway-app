import { useEffect, useState } from 'react'
import { getForecast, getGoals } from '../api/client'
import type { City, Forecast, Goal } from '../api/types'

export type RunwayData =
  | { status: 'loading' }
  | { status: 'error'; message: string }
  | { status: 'empty' } // no goals yet
  | { status: 'ready'; goal: Goal; forecast: Forecast; refreshing: boolean }

/**
 * Loads the first goal and its forecast, refetching when `city` changes.
 * `city` null lets the backend pick the current city. While a new city is
 * loading, the previous forecast stays on screen (refreshing: true).
 */
export function useRunwayData(city: City | null): RunwayData {
  const [goal, setGoal] = useState<Goal | null | undefined>(undefined)
  const [forecast, setForecast] = useState<Forecast | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loadedCity, setLoadedCity] = useState<City | null | undefined>(undefined)

  useEffect(() => {
    let cancelled = false
    getGoals()
      .then((goals) => !cancelled && setGoal(goals[0] ?? null))
      .catch(() => !cancelled && setError("Can't reach the Runway API — is uvicorn running?"))
    return () => {
      cancelled = true
    }
  }, [])

  useEffect(() => {
    if (!goal) return
    let cancelled = false
    getForecast(goal.id, city ?? undefined)
      .then((result) => {
        if (cancelled) return
        setForecast(result)
        setLoadedCity(city)
      })
      .catch(() => !cancelled && setError("Couldn't load your forecast. Try refreshing?"))
    return () => {
      cancelled = true
    }
  }, [goal, city])

  if (error) return { status: 'error', message: error }
  if (goal === null) return { status: 'empty' }
  if (!goal || !forecast) return { status: 'loading' }
  return { status: 'ready', goal, forecast, refreshing: loadedCity !== city }
}
