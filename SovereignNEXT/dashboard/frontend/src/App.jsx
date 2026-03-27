import { useObserver } from './hooks/useObserver'
import ParadoxField from './components/ParadoxField'
import OperatorLedger from './components/OperatorLedger'
import LineageExplorer from './components/LineageExplorer'
import AnomalyPanel from './components/AnomalyPanel'
import ParadoxDetail from './components/ParadoxDetail'

const PASS_LABELS = {
  pass1: 'Pass 1',
  pass2: 'Pass 2',
  pass3: 'Pass 3',
  final: 'Final',
}

export default function App() {
  const {
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
    currentReport,
  } = useObserver()

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="text-2xl font-serif text-gray-400 mb-2">Sovereign Observer</div>
          <div className="text-sm text-gray-500">Loading V5 Anchor snapshots...</div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="text-2xl font-serif text-red-400 mb-2">Observation Failed</div>
          <div className="text-sm text-gray-500">{error}</div>
          <div className="text-xs text-gray-600 mt-4">
            Ensure the backend is running: python -m SovereignNEXT.dashboard.server
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen p-6 max-w-[1600px] mx-auto">
      {/* Header */}
      <header className="mb-8">
        <div className="flex items-baseline justify-between">
          <div>
            <h1 className="text-3xl font-serif font-semibold text-gray-100">
              Sovereign Observer
            </h1>
            <p className="text-sm text-gray-500 mt-1">
              Phase 6 — Epistemic Visibility Layer — Read Only
            </p>
          </div>
          {seal && (
            <div className="text-right text-xs text-gray-500">
              <div className="font-mono">{seal.baseline_id}</div>
              <div>Sealed: {new Date(seal.sealed_at).toLocaleDateString()}</div>
              <div className="font-mono text-[10px] text-gray-600 mt-1">
                {seal.snapshot_hash?.slice(0, 16)}...
              </div>
            </div>
          )}
        </div>

        {/* Pass selector */}
        <div className="flex gap-2 mt-4">
          {passes?.map((p) => (
            <button
              key={p.pass_id}
              onClick={() => {
                setSelectedPass(p.pass_id)
                selectParadox(null)
              }}
              className={`px-4 py-2 rounded text-sm font-medium transition-colors ${
                selectedPass === p.pass_id
                  ? 'bg-sovereign-accent text-white'
                  : 'bg-sovereign-surface text-gray-400 hover:text-gray-200 border border-sovereign-border'
              }`}
            >
              {PASS_LABELS[p.pass_id] || p.pass_id}
            </button>
          ))}
        </div>

        {/* Current snapshot hash */}
        {currentReport && (
          <div className="mt-2 text-[10px] font-mono text-gray-600">
            Snapshot: {currentReport.state_hash}
          </div>
        )}
      </header>

      {/* Main grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left column: Paradox Field + Detail */}
        <div className="lg:col-span-2 space-y-6">
          <ParadoxField
            report={currentReport}
            onSelectParadox={selectParadox}
            selectedParadoxId={selectedParadox}
          />

          {paradoxDetail && (
            <ParadoxDetail
              detail={paradoxDetail}
              onClose={() => selectParadox(null)}
            />
          )}

          <OperatorLedger
            canonicalReport={canonicalReport}
            reports={reports}
            passes={passes}
          />
        </div>

        {/* Right column: Anomalies + Lineage */}
        <div className="space-y-6">
          <AnomalyPanel report={currentReport} />
          <LineageExplorer
            passes={passes}
            reports={reports}
            canonicalReport={canonicalReport}
            selectedPass={selectedPass}
          />
        </div>
      </div>
    </div>
  )
}
