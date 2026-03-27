import { useState, useEffect, useCallback } from 'react'

const API_BASE = '/api'

/**
 * Fetch JSON and freeze it. Glass Wall: all data is immutable after fetch.
 */
async function fetchFrozen(url) {
  const res = await fetch(`${API_BASE}${url}`)
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
  const data = await res.json()
  return Object.freeze(data)
}

/**
 * Deep-freeze an object recursively.
 */
function deepFreeze(obj) {
  if (obj === null || typeof obj !== 'object') return obj
  Object.freeze(obj)
  Object.getOwnPropertyNames(obj).forEach((key) => {
    if (typeof obj[key] === 'object' && obj[key] !== null && !Object.isFrozen(obj[key])) {
      deepFreeze(obj[key])
    }
  })
  return obj
}

/**
 * Hook: load all observer data at mount. All state is frozen (Glass Wall).
 */
export function useObserver() {
  const [passes, setPasses] = useState(null)
  const [reports, setReports] = useState({})
  const [canonicalReport, setCanonicalReport] = useState(null)
  const [seal, setSeal] = useState(null)
  const [selectedPass, setSelectedPass] = useState('final')
  const [selectedParadox, setSelectedParadox] = useState(null)
  const [paradoxDetail, setParadoxDetail] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // Load all data on mount
  useEffect(() => {
    async function loadAll() {
      try {
        setLoading(true)
        const [passData, sealData, reportData] = await Promise.all([
          fetchFrozen('/passes'),
          fetchFrozen('/seal'),
          fetchFrozen('/report'),
        ])
        setPasses(deepFreeze(passData.passes))
        setSeal(deepFreeze(sealData))
        setCanonicalReport(deepFreeze(reportData))

        // Load observer reports for all passes
        const passIds = passData.passes.map((p) => p.pass_id)
        const reportEntries = await Promise.all(
          passIds.map(async (id) => {
            const r = await fetchFrozen(`/observe/${id}`)
            return [id, deepFreeze(r)]
          })
        )
        const reportsMap = Object.fromEntries(reportEntries)
        setReports(deepFreeze(reportsMap))
        setError(null)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }
    loadAll()
  }, [])

  // Load paradox detail on selection
  const selectParadox = useCallback(
    async (paradoxId) => {
      if (!paradoxId) {
        setSelectedParadox(null)
        setParadoxDetail(null)
        return
      }
      setSelectedParadox(paradoxId)
      try {
        const detail = await fetchFrozen(`/observe/${selectedPass}/paradox/${paradoxId}`)
        setParadoxDetail(deepFreeze(detail))
      } catch (err) {
        setParadoxDetail(null)
      }
    },
    [selectedPass]
  )

  return {
    passes,
    reports,
    canonicalReport,
    seal,
    selectedPass,
    setSelectedPass,
    selectedParadox,
    selectParadox,
    paradoxDetail,
    loading,
    error,
    currentReport: reports[selectedPass] || null,
  }
}
