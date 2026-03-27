export default function ParadoxDetail({ detail, onClose }) {
  if (!detail) return null

  const ev = detail.emoji_vector

  return (
    <div className="bg-sovereign-surface border border-sovereign-border rounded-xl p-5">
      <div className="flex items-baseline justify-between mb-4">
        <h2 className="text-lg font-serif font-semibold text-gray-100">
          {detail.id}
        </h2>
        <button
          onClick={onClose}
          className="text-xs text-gray-500 hover:text-gray-300 transition-colors"
        >
          Close
        </button>
      </div>

      {/* Poles */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="bg-sovereign-bg rounded-lg p-3">
          <div className="text-[10px] text-gray-500 uppercase tracking-wider mb-1">Pole A</div>
          <div className="text-sm text-gray-200">{detail.pole_a?.id || 'unknown'}</div>
          {detail.pole_a?.emoji && (
            <div className="text-xl mt-1">{detail.pole_a.emoji}</div>
          )}
          <div className="text-[10px] text-gray-500 mt-1">
            Confidence: {detail.pole_a?.confidence?.toFixed(2) || 'n/a'}
          </div>
        </div>
        <div className="bg-sovereign-bg rounded-lg p-3">
          <div className="text-[10px] text-gray-500 uppercase tracking-wider mb-1">Pole B</div>
          <div className="text-sm text-gray-200">{detail.pole_b?.id || 'unknown'}</div>
          {detail.pole_b?.emoji && (
            <div className="text-xl mt-1">{detail.pole_b.emoji}</div>
          )}
          <div className="text-[10px] text-gray-500 mt-1">
            Confidence: {detail.pole_b?.confidence?.toFixed(2) || 'n/a'}
          </div>
        </div>
      </div>

      {/* Emoji Vector — rendered as actual glyphs */}
      {ev && (
        <div className="mb-4">
          <div className="text-[10px] text-gray-500 uppercase tracking-wider mb-2">
            Emoji Vector ({ev.length} elements)
          </div>
          <div className="bg-sovereign-bg rounded-lg p-3">
            <div className="text-2xl tracking-widest leading-relaxed break-all">
              {ev.sequence_display || ev.sequence?.join('') || ''}
            </div>
            <div className="grid grid-cols-4 gap-2 mt-3 text-[10px]">
              <div>
                <span className="text-gray-500">Entropy: </span>
                <span className="text-gray-300">{ev.metrics?.entropy?.toFixed(4)}</span>
              </div>
              <div>
                <span className="text-gray-500">Balance: </span>
                <span className="text-gray-300">{ev.metrics?.pole_balance?.toFixed(4)}</span>
              </div>
              <div>
                <span className="text-gray-500">Chaos: </span>
                <span className="text-gray-300">{ev.metrics?.chaos_index?.toFixed(4)}</span>
              </div>
              <div>
                <span className="text-gray-500">Stability: </span>
                <span className="text-gray-300">{ev.metrics?.stability_index?.toFixed(4)}</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Metrics */}
      <div className="mb-4">
        <div className="text-[10px] text-gray-500 uppercase tracking-wider mb-2">Paradox Metrics</div>
        <div className="grid grid-cols-4 gap-2 text-xs">
          <div className="bg-sovereign-bg rounded p-2">
            <div className="text-gray-500">Tension</div>
            <div className="text-gray-200 font-mono">{detail.metrics?.tension_strength?.toFixed(3)}</div>
          </div>
          <div className="bg-sovereign-bg rounded p-2">
            <div className="text-gray-500">Resolution Pressure</div>
            <div className="text-gray-200 font-mono">{detail.metrics?.resolution_pressure?.toFixed(3)}</div>
          </div>
          <div className="bg-sovereign-bg rounded p-2">
            <div className="text-gray-500">Stability</div>
            <div className="text-gray-200 font-mono">{detail.metrics?.paradox_stability?.toFixed(3)}</div>
          </div>
          <div className="bg-sovereign-bg rounded p-2">
            <div className="text-gray-500">Divergence</div>
            <div className="text-gray-200 font-mono">{detail.metrics?.agent_divergence?.toFixed(3)}</div>
          </div>
        </div>
      </div>

      {/* Constraints */}
      <div className="mb-4">
        <div className="text-[10px] text-gray-500 uppercase tracking-wider mb-2">Constraints</div>
        <div className="flex gap-3 text-xs">
          <span className={`px-2 py-1 rounded ${
            detail.constraints?.collapse_veto
              ? 'bg-green-900/30 text-green-400 border border-green-800/50'
              : 'bg-red-900/30 text-red-400 border border-red-800/50'
          }`}>
            Veto: {detail.constraints?.collapse_veto ? 'LOCKED' : 'UNLOCKED'}
          </span>
          {detail.constraints?.veto_reason && (
            <span className="text-gray-500">{detail.constraints.veto_reason}</span>
          )}
        </div>
      </div>

      {/* History timeline */}
      {detail.history?.length > 0 && (
        <div>
          <div className="text-[10px] text-gray-500 uppercase tracking-wider mb-2">
            History ({detail.history.length} events)
          </div>
          <div className="max-h-48 overflow-y-auto space-y-1">
            {detail.history.map((entry, i) => (
              <div
                key={i}
                className="flex items-center gap-2 text-[10px] font-mono bg-sovereign-bg rounded px-2 py-1"
              >
                <span className="text-gray-500 w-16 shrink-0">{entry.operator}</span>
                <span className="text-gray-300">{entry.event}</span>
                {entry.entropy != null && (
                  <span className="text-gray-500 ml-auto">H={entry.entropy.toFixed(4)}</span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
