const dollars = new Intl.NumberFormat('en-CA', {
  style: 'currency',
  currency: 'CAD',
  currencyDisplay: 'narrowSymbol',
  maximumFractionDigits: 0,
})

/** "$13,576" — whole dollars; cents are noise at this scale. */
export const formatMoney = (value: number): string => dollars.format(value)

// Dates from the API are plain YYYY-MM-DD; parse as local dates so they don't shift a day.
const parseDate = (iso: string): Date => {
  const [year, month, day] = iso.split('-').map(Number)
  return new Date(year, month - 1, day)
}

/** "Jan 4, 2027" */
export const formatDate = (iso: string): string =>
  parseDate(iso).toLocaleDateString('en-CA', { month: 'short', day: 'numeric', year: 'numeric' })

/** "Jan" — for chart axis ticks. */
export const formatMonth = (iso: string): string =>
  parseDate(iso).toLocaleDateString('en-CA', { month: 'short' })

export const capitalize = (text: string): string => text.charAt(0).toUpperCase() + text.slice(1)
