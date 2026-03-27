import { useMemo, useState } from 'react'

const SEVERITY_COLORS = {
  regulated: { bg: 'bg-green-900/20', border: 'border-green-800/30', text: 'text-green-400', label: 'info' },
  oscillating: { bg: 'bg-amber-900/20', border: 'border-amber-800/30', text: 'text-amber-400', label: 'warning' },
  drifting: { bg: 'bg-red-900/20', border: 'border-red-800/30', text: 'text-red-400', label: 'warning' },
  stuck: { bg: 'bg-gray-800/40', border: 'border-gray-700/30', text: 'text-gray-400', label: 'warning' },
  saturated: { bg: 'bg-purple-900/20', border: 'border-purple-800/30', text: 'text-purple-400', label: 'warning' },
}

function parseAnomaly(flag) {
  const colonIdx = flag.indexOf(':')
  if (colonIdx === -1) return { type: 'unknown', message: flag }
  const type = flag.substring(0, colonIdx).trim()
  const message = flag.substring(colonIdx + 1).trim()
  return { type, message }
}

export default function AnomalyPanel({ report }) {
  const [filter, setFilter] = useState('all')

  const anomalies = useMemo(() => {
    if (!report?.anomaly_flags) return []
    return report.anomaly_flags.map(parseAnomaly)
  }, [report])

  const counts = useMemo(() => {
    const c = { all: anomalies.length }
    anomalies.forEach((a) => {
      c[a.type] = (c[a.type] || 0) + 1
    })
    return c
  }, [anomalies])

  const filtered = filter === 'all' ? anomalies : anomalies.filter((a) => a.type === filter)

  // Health statement per governance contract
  const warnings = anomalies.filter((a) => a.type !== 'regulated')
  const healthStatement = warnings.length === 0
    ? 'healthy: no warnings'
    : 'warnings present: review anomalies'

  if (!report) return null

  return (
    <div className="bg-sovereign-surface border border-sovereign-border rounded-xl p-5">
      <h2 className="text-lg font-serif font-semibold text-gray-100 mb-3">Health & Anomalies</h2>

      {/* Health statement */}
      <div className={`rounded-lg px-3 py-2 mb-4 text-sm font-mono ${
        warnings.length === 0
          ? 'bg-green-900/20 text-green-400 border border-green-800/30'
          : 'bg-amber-900/20 text-amber-400 border border-amber-800/30'
      }`}>
        {healthStatement}
      </div>

      {/* Summary stats */}
      <div className="grid grid-cols-3 gap-2 mb-4">
        <div className="bg-sovereign-bg rounded-lg p-2 text-center">
          <div className="text-[10px] text-gray-500">Total</div>
          <div className="text-lg font-mono text-gray-200">{anomalies.length}</div>
        </div>
        <div className="bg-sovereign-bg rounded-lg p-2 text-center">
          <div className="text-[10px] text-gray-500">Regulated</div>
          <div className="text-lg font-mono text-green-400">{counts.regulated || 0}</div>
        </div>
        <div className="bg-sovereign-bg rounded-lg p-2 text-center">
          <div className="text-[10px] text-gray-500">Warnings</div>
          <div className="text-lg font-mono text-amber-400">{warnings.length}</div>
        </div>
      </div>

      {/* Integrity attestations */}
      {report.integrity_attestations?.length > 0 && (
        <div className="mb-4">
          <div className="text-[10px] text-gray-500 uppercase tracking-wider mb-2">
            Integrity Attestations
          </div>
          <div className="space-y-1">
            {report.integrity_attestations.map((a, i) => (
              <div
                key={i}
                className={`text-[11px] font-mono px-2 py-1 rounded ${
                  a.includes('VIOLATION')
                    ? 'bg-red-900/20 text-red-400'
                    : 'bg-green-900/10 text-green-500'
                }`}
              >
                {a}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Veto summary */}
      {report.veto_summary && (
        <div className="mb-4">
          <div className="text-[10px] text-gray-500 uppercase tracking-wider mb-2">Veto State</div>
          <div className="flex gap-3 text-xs">
            <span className="bg-green-900/20 text-green-400 px-2 py-1 rounded border border-green-800/30">
              Locked: {report.veto_summary.veto_locked}
            </span>
            <span className="bg-sovereign-bg text-gray-400 px-2 py-1 rounded">
              Unlocked: {report.veto_summary.veto_unlocked}
            </span>
          </div>
        </div>
      )}

      {/* Filter tabs */}
      <div className="flex gap-1 mb-3 flex-wrap">
        {Object.entries(counts).map(([type, count]) => (
          <button
            key={type}
            onClick={() => setFilter(type)}
            className={`text-[10px] px-2 py-1 rounded transition-colors ${
              filter === type
                ? 'bg-sovereign-accent text-white'
                : 'bg-sovereign-bg text-gray-500 hover:text-gray-300'
            }`}
          >
            {type} ({count})
          </button>
        ))}
      </div>

      {/* Anomaly list */}
      <div className="max-h-64 overflow-y-auto space-y-1">
        {filtered.map((a, i) => {
          const style = SEVERITY_COLORS[a.type] || SEVERITY_COLORS.stuck
          return (
            <div
              key={i}
              className={`${style.bg} ${style.border} border rounded px-2 py-1.5 text-[10px]`}
            >
              <span className={`${style.text} font-mono font-semibold`}>
                [{style.label}] {a.type}
              </span>
              <span className="text-gray-400 ml-2">{a.message}</span>
            </div>
          )
        })}
        {filtered.length === 0 && (
          <div className="text-[10px] text-gray-600 text-center py-4">
            No anomalies matching filter.
          </div>
        )}
      </div>
    </div>
  )
}
