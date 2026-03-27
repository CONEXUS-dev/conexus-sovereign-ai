import { useMemo } from 'react'

export default function LineageExplorer({ passes, reports, canonicalReport, selectedPass }) {
  // Compute deltas between passes
  const lineage = useMemo(() => {
    if (!passes || passes.length === 0) return []
    return passes.map((p, i) => {
      const prev = i > 0 ? passes[i - 1] : null
      return {
        pass_id: p.pass_id,
        claims: p.claims,
        tensions: p.tensions,
        paradoxes: p.paradoxes,
        emoji_vectors: p.emoji_vectors,
        state_hash: p.state_hash,
        delta_claims: prev ? p.claims - prev.claims : p.claims,
        delta_tensions: prev ? p.tensions - prev.tensions : p.tensions,
        delta_paradoxes: prev ? p.paradoxes - prev.paradoxes : p.paradoxes,
      }
    })
  }, [passes])

  // Belief stratification from current report
  const belief = useMemo(() => {
    const r = reports?.[selectedPass]
    if (!r?.belief_stratification) return null
    return r.belief_stratification
  }, [reports, selectedPass])

  if (!passes) return null

  const PASS_LABELS = { pass1: 'Pass 1', pass2: 'Pass 2', pass3: 'Pass 3', final: 'Final' }

  return (
    <div className="bg-sovereign-surface border border-sovereign-border rounded-xl p-5">
      <h2 className="text-lg font-serif font-semibold text-gray-100 mb-4">Lineage Explorer</h2>

      {/* Pass timeline */}
      <div className="space-y-2 mb-4">
        {lineage.map((p) => {
          const isSelected = p.pass_id === selectedPass
          return (
            <div
              key={p.pass_id}
              className={`rounded-lg px-3 py-2 transition-colors ${
                isSelected
                  ? 'bg-sovereign-accent/10 border border-sovereign-accent/30'
                  : 'bg-sovereign-bg border border-transparent'
              }`}
            >
              <div className="flex items-center justify-between mb-1">
                <span className={`text-xs font-semibold ${isSelected ? 'text-sovereign-accent' : 'text-gray-400'}`}>
                  {PASS_LABELS[p.pass_id] || p.pass_id}
                </span>
                {isSelected && (
                  <span className="text-[9px] bg-sovereign-accent/20 text-sovereign-accent px-1.5 py-0.5 rounded">
                    VIEWING
                  </span>
                )}
              </div>

              <div className="grid grid-cols-3 gap-2 text-[10px]">
                <div>
                  <span className="text-gray-500">Claims: </span>
                  <span className="text-gray-300 font-mono">{p.claims}</span>
                  <span className="text-gray-600 ml-1">(+{p.delta_claims})</span>
                </div>
                <div>
                  <span className="text-gray-500">Tensions: </span>
                  <span className="text-gray-300 font-mono">{p.tensions}</span>
                  <span className="text-gray-600 ml-1">(+{p.delta_tensions})</span>
                </div>
                <div>
                  <span className="text-gray-500">Paradoxes: </span>
                  <span className="text-gray-300 font-mono">{p.paradoxes}</span>
                  <span className="text-gray-600 ml-1">(+{p.delta_paradoxes})</span>
                </div>
              </div>

              <div className="text-[9px] font-mono text-gray-600 mt-1 truncate">
                {p.state_hash}
              </div>
            </div>
          )
        })}
      </div>

      {/* Belief stratification */}
      {belief && (
        <div className="mb-4">
          <div className="text-[10px] text-gray-500 uppercase tracking-wider mb-2">
            Belief Stratification
          </div>
          <div className="grid grid-cols-2 gap-2">
            <div className="bg-sovereign-bg rounded-lg p-2">
              <div className="text-[10px] text-green-500">Committed</div>
              <div className="text-sm font-mono text-gray-200">{belief.committed?.length || 0}</div>
            </div>
            <div className="bg-sovereign-bg rounded-lg p-2">
              <div className="text-[10px] text-amber-500">Held</div>
              <div className="text-sm font-mono text-gray-200">{belief.held?.length || 0}</div>
            </div>
            <div className="bg-sovereign-bg rounded-lg p-2">
              <div className="text-[10px] text-blue-500">Open</div>
              <div className="text-sm font-mono text-gray-200">{belief.open?.length || 0}</div>
            </div>
            <div className="bg-sovereign-bg rounded-lg p-2">
              <div className="text-[10px] text-gray-500">Deferred</div>
              <div className="text-sm font-mono text-gray-200">{belief.deferred?.length || 0}</div>
            </div>
          </div>
        </div>
      )}

      {/* Canonical run metadata */}
      {canonicalReport && (
        <div>
          <div className="text-[10px] text-gray-500 uppercase tracking-wider mb-2">
            Canonical Run
          </div>
          <div className="bg-sovereign-bg rounded-lg p-3 space-y-1 text-[10px] font-mono">
            <div>
              <span className="text-gray-500">Experiment: </span>
              <span className="text-gray-300">{canonicalReport.experiment}</span>
            </div>
            <div>
              <span className="text-gray-500">Phase: </span>
              <span className="text-gray-300">{canonicalReport.phase}</span>
            </div>
            <div>
              <span className="text-gray-500">Passes: </span>
              <span className="text-gray-300">{canonicalReport.passes}</span>
            </div>
            <div>
              <span className="text-gray-500">Seed: </span>
              <span className="text-gray-300">{canonicalReport.seed}</span>
            </div>
            <div>
              <span className="text-gray-500">Timestamp: </span>
              <span className="text-gray-300">
                {canonicalReport.timestamp
                  ? new Date(canonicalReport.timestamp).toLocaleString()
                  : 'n/a'}
              </span>
            </div>
            <div className="pt-1 border-t border-sovereign-border">
              <span className="text-gray-500">Input hash: </span>
              <span className="text-gray-400 break-all">{canonicalReport.input_content_hash}</span>
            </div>
            <div>
              <span className="text-gray-500">Final hash: </span>
              <span className="text-gray-400 break-all">{canonicalReport.final_state_hash}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
