import { useMemo } from "react";
import {
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
} from "recharts";

const PASS_LABELS = { pass1: "P1", pass2: "P2", pass3: "P3", final: "Final" };

export default function OperatorLedger({ canonicalReport, reports, passes }) {
  // Per-pass metrics from canonical report
  const perPassData = useMemo(() => {
    if (!canonicalReport?.per_pass) return [];
    return canonicalReport.per_pass.map((p) => ({
      name: `Pass ${p.pass}`,
      claims: p.claims_after,
      newClaims: p.new_claims,
      tensions: p.tensions_after,
      newTensions: p.new_tensions,
      paradoxes: p.paradoxes_after,
      newParadoxes: p.new_promotions,
      heldCount: p.held_count,
      vetoedCount: p.vetoed_count,
    }));
  }, [canonicalReport]);

  // Entropy distribution across passes
  const entropyData = useMemo(() => {
    if (!reports || !passes) return [];
    return passes
      .map((p) => {
        const report = reports[p.pass_id];
        if (!report) return null;
        const dist = report.entropy_band_distribution || {};
        return {
          name: PASS_LABELS[p.pass_id] || p.pass_id,
          below: dist.below_band || 0,
          within: dist.within_band || 0,
          above: dist.above_band || 0,
        };
      })
      .filter(Boolean);
  }, [reports, passes]);

  // Operator ledger summary from final report
  const ledgerData = useMemo(() => {
    const final = reports?.final;
    if (!final?.operator_ledgers) return [];
    return final.operator_ledgers;
  }, [reports]);

  if (!canonicalReport) return null;

  return (
    <div className="bg-sovereign-surface border border-sovereign-border rounded-xl p-5">
      <h2 className="text-lg font-serif font-semibold text-gray-100 mb-4">
        Operator Ledger
      </h2>

      {/* Per-pass growth */}
      <div className="mb-6">
        <div className="text-[10px] text-gray-500 uppercase tracking-wider mb-2">
          Growth Across Passes
        </div>
        <ResponsiveContainer width="100%" height={200}>
          <BarChart
            data={perPassData}
            margin={{ top: 5, right: 20, bottom: 5, left: 10 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
            <XAxis dataKey="name" tick={{ fontSize: 10, fill: "#9ca3af" }} />
            <YAxis tick={{ fontSize: 10, fill: "#9ca3af" }} />
            <Tooltip
              contentStyle={{
                backgroundColor: "#111827",
                border: "1px solid #1f2937",
                borderRadius: "8px",
                fontSize: "11px",
              }}
            />
            <Bar dataKey="newClaims" fill="#6366f1" name="New Claims" />
            <Bar dataKey="newTensions" fill="#8b5cf6" name="New Tensions" />
            <Bar dataKey="newParadoxes" fill="#a855f7" name="New Paradoxes" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Entropy distribution */}
      {entropyData.length > 0 && (
        <div className="mb-6">
          <div className="text-[10px] text-gray-500 uppercase tracking-wider mb-2">
            Entropy Band Distribution
          </div>
          <ResponsiveContainer width="100%" height={180}>
            <BarChart
              data={entropyData}
              margin={{ top: 5, right: 20, bottom: 5, left: 10 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
              <XAxis dataKey="name" tick={{ fontSize: 10, fill: "#9ca3af" }} />
              <YAxis tick={{ fontSize: 10, fill: "#9ca3af" }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#111827",
                  border: "1px solid #1f2937",
                  borderRadius: "8px",
                  fontSize: "11px",
                }}
              />
              <Bar
                dataKey="below"
                fill="#ef4444"
                name="Below Band"
                stackId="entropy"
              />
              <Bar
                dataKey="within"
                fill="#22c55e"
                name="Within Band"
                stackId="entropy"
              />
              <Bar
                dataKey="above"
                fill="#f59e0b"
                name="Above Band"
                stackId="entropy"
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Operator summary table */}
      {ledgerData.length > 0 && (
        <div>
          <div className="text-[10px] text-gray-500 uppercase tracking-wider mb-2">
            Operator Actions (Final State)
          </div>
          <div className="space-y-2">
            {ledgerData.map((ledger) => (
              <div
                key={ledger.operator_name}
                className="bg-sovereign-bg rounded-lg px-3 py-2 flex items-center justify-between"
              >
                <div>
                  <div className="text-xs font-mono text-gray-200">
                    {ledger.operator_name}
                  </div>
                  <div className="text-[10px] text-gray-500">
                    {ledger.affected_paradox_ids.length} paradoxes
                  </div>
                </div>
                <div className="flex gap-2">
                  {Object.entries(ledger.action_counts).map(
                    ([action, count]) => (
                      <span
                        key={action}
                        className="text-[10px] bg-sovereign-surface px-2 py-0.5 rounded text-gray-400"
                      >
                        {action}: <span className="text-gray-200">{count}</span>
                      </span>
                    ),
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Summary stats */}
      <div className="grid grid-cols-4 gap-3 mt-4">
        <div className="bg-sovereign-bg rounded-lg p-3 text-center">
          <div className="text-[10px] text-gray-500">Total Claims</div>
          <div className="text-xl font-mono text-gray-100">
            {canonicalReport.final_state?.claims || 0}
          </div>
        </div>
        <div className="bg-sovereign-bg rounded-lg p-3 text-center">
          <div className="text-[10px] text-gray-500">Total Tensions</div>
          <div className="text-xl font-mono text-gray-100">
            {canonicalReport.final_state?.tensions || 0}
          </div>
        </div>
        <div className="bg-sovereign-bg rounded-lg p-3 text-center">
          <div className="text-[10px] text-gray-500">Total Paradoxes</div>
          <div className="text-xl font-mono text-gray-100">
            {canonicalReport.final_state?.paradoxes || 0}
          </div>
        </div>
        <div className="bg-sovereign-bg rounded-lg p-3 text-center">
          <div className="text-[10px] text-gray-500">Duration</div>
          <div className="text-xl font-mono text-gray-100">
            {canonicalReport.total_duration_sec
              ? `${Math.round(canonicalReport.total_duration_sec / 60)}m`
              : "n/a"}
          </div>
        </div>
      </div>
    </div>
  );
}
