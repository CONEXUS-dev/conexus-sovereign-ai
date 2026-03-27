import { useMemo } from 'react'
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceArea,
  ResponsiveContainer,
  Cell,
} from 'recharts'

const ANOMALY_COLORS = {
  regulated: '#22c55e',
  oscillating: '#f59e0b',
  drifting: '#ef4444',
  stuck: '#6b7280',
  saturated: '#a855f7',
  unknown: '#374151',
}

function classifyParadox(digest, anomalyFlags) {
  const id = digest.paradox_id
  for (const flag of anomalyFlags) {
    if (flag.includes(id)) {
      if (flag.startsWith('regulated:')) return 'regulated'
      if (flag.startsWith('oscillating:')) return 'oscillating'
      if (flag.startsWith('drifting:')) return 'drifting'
      if (flag.startsWith('stuck:')) return 'stuck'
      if (flag.startsWith('saturated:')) return 'saturated'
    }
  }
  return 'unknown'
}

function CustomTooltip({ active, payload }) {
  if (!active || !payload?.length) return null
  const d = payload[0].payload
  return (
    <div className="bg-sovereign-surface border border-sovereign-border rounded-lg p-3 text-xs shadow-lg">
      <div className="font-mono font-semibold text-gray-200 mb-1">{d.paradox_id}</div>
      <div className="text-gray-400">
        Entropy: <span className="text-gray-200">{d.entropy.toFixed(4)}</span>
      </div>
      <div className="text-gray-400">
        Balance: <span className="text-gray-200">{d.balance.toFixed(4)}</span>
      </div>
      <div className="text-gray-400">
        Status: <span className="text-gray-200">{d.classification}</span>
      </div>
      <div className="text-gray-400">
        Poles: <span className="text-gray-200">{d.pole_a} / {d.pole_b}</span>
      </div>
    </div>
  )
}

export default function ParadoxField({ report, onSelectParadox, selectedParadoxId }) {
  const data = useMemo(() => {
    if (!report?.paradox_digests) return []
    return report.paradox_digests.map((d) => ({
      ...d,
      classification: classifyParadox(d, report.anomaly_flags || []),
    }))
  }, [report])

  if (!report) return null

  const counts = data.reduce((acc, d) => {
    acc[d.classification] = (acc[d.classification] || 0) + 1
    return acc
  }, {})

  return (
    <div className="bg-sovereign-surface border border-sovereign-border rounded-xl p-5">
      <div className="flex items-baseline justify-between mb-4">
        <h2 className="text-lg font-serif font-semibold text-gray-100">Paradox Field</h2>
        <div className="flex gap-3 text-[10px]">
          {Object.entries(counts).map(([type, count]) => (
            <span key={type} className="flex items-center gap-1">
              <span
                className="w-2 h-2 rounded-full inline-block"
                style={{ backgroundColor: ANOMALY_COLORS[type] || '#374151' }}
              />
              <span className="text-gray-400">
                {type}: <span className="text-gray-300">{count}</span>
              </span>
            </span>
          ))}
        </div>
      </div>

      <ResponsiveContainer width="100%" height={380}>
        <ScatterChart margin={{ top: 10, right: 20, bottom: 20, left: 10 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
          <XAxis
            type="number"
            dataKey="entropy"
            name="Entropy"
            domain={[0, 1]}
            tick={{ fontSize: 10, fill: '#9ca3af' }}
            label={{ value: 'Entropy', position: 'bottom', offset: 0, style: { fontSize: 11, fill: '#6b7280' } }}
          />
          <YAxis
            type="number"
            dataKey="balance"
            name="Balance"
            domain={[0, 1]}
            tick={{ fontSize: 10, fill: '#9ca3af' }}
            label={{ value: 'Balance', angle: -90, position: 'insideLeft', style: { fontSize: 11, fill: '#6b7280' } }}
          />
          <Tooltip content={<CustomTooltip />} />

          {/* Target entropy band [0.70, 0.90] */}
          <ReferenceArea
            x1={0.70}
            x2={0.90}
            y1={0}
            y2={1}
            fill="#6366f1"
            fillOpacity={0.06}
            stroke="#6366f1"
            strokeOpacity={0.15}
            strokeDasharray="4 4"
          />

          {/* Target balance window [0.35, 0.65] */}
          <ReferenceArea
            x1={0}
            x2={1}
            y1={0.35}
            y2={0.65}
            fill="#6366f1"
            fillOpacity={0.04}
            stroke="#6366f1"
            strokeOpacity={0.1}
            strokeDasharray="4 4"
          />

          <Scatter
            data={data}
            onClick={(entry) => onSelectParadox?.(entry.paradox_id)}
            cursor="pointer"
          >
            {data.map((entry, index) => (
              <Cell
                key={index}
                fill={ANOMALY_COLORS[entry.classification] || '#374151'}
                stroke={entry.paradox_id === selectedParadoxId ? '#ffffff' : 'transparent'}
                strokeWidth={entry.paradox_id === selectedParadoxId ? 2 : 0}
                r={entry.paradox_id === selectedParadoxId ? 7 : 5}
              />
            ))}
          </Scatter>
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  )
}
