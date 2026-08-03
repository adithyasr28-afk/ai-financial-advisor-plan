"use client";

import { useState } from "react";
import { Plus, X, Bell } from "lucide-react";
import { Card } from "../components/ui/Card";
import { Button } from "../components/ui/Button";
import { Input, Select, Label } from "../components/ui/Input";
import { StatusBadge } from "../components/ui/Badge";
import { EmptyState } from "../components/ui/EmptyState";

interface Alert {
  id: string;
  symbol: string;
  condition: "above" | "below" | "change_pct_above" | "change_pct_below";
  threshold: number;
  enabled: boolean;
  created_at: string;
}

const conditionLabels: Record<Alert["condition"], string> = {
  above: "Price above",
  below: "Price below",
  change_pct_above: "Daily change above",
  change_pct_below: "Daily change below",
};

export default function Alerts() {
  const [alerts, setAlerts] = useState<Alert[]>([
    { id: "1", symbol: "AAPL", condition: "above", threshold: 180, enabled: true, created_at: new Date().toISOString() },
    { id: "2", symbol: "TSLA", condition: "change_pct_below", threshold: -5, enabled: true, created_at: new Date().toISOString() },
  ]);
  const [showForm, setShowForm] = useState(false);
  const [newAlert, setNewAlert] = useState<Omit<Alert, "id" | "created_at">>({
    symbol: "",
    condition: "above",
    threshold: 0,
    enabled: true,
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newAlert.symbol || newAlert.threshold === 0) return;
    setAlerts((prev) => [...prev, { ...newAlert, id: Date.now().toString(), created_at: new Date().toISOString() }]);
    setNewAlert({ symbol: "", condition: "above", threshold: 0, enabled: true });
    setShowForm(false);
  };

  const toggleAlert = (id: string) =>
    setAlerts((prev) => prev.map((a) => (a.id === id ? { ...a, enabled: !a.enabled } : a)));
  const deleteAlert = (id: string) => setAlerts((prev) => prev.filter((a) => a.id !== id));

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <h1 className="font-display text-2xl font-semibold text-ink">Alerts</h1>
          <p className="text-sm text-ink-muted mt-1">Get notified when a symbol crosses a threshold.</p>
        </div>
        <Button variant={showForm ? "secondary" : "primary"} onClick={() => setShowForm(!showForm)}>
          {showForm ? "Cancel" : (<><Plus className="w-4 h-4" /> New alert</>)}
        </Button>
      </div>

      {showForm && (
        <Card>
          <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <Label>Symbol</Label>
              <Input
                mono
                value={newAlert.symbol}
                onChange={(e) => setNewAlert({ ...newAlert, symbol: e.target.value.toUpperCase() })}
                placeholder="AAPL"
                className="w-full"
              />
            </div>
            <div>
              <Label>Condition</Label>
              <Select
                value={newAlert.condition}
                onChange={(e) => setNewAlert({ ...newAlert, condition: e.target.value as Alert["condition"] })}
                className="w-full"
              >
                {Object.entries(conditionLabels).map(([value, label]) => (
                  <option key={value} value={value}>{label}</option>
                ))}
              </Select>
            </div>
            <div>
              <Label>Threshold</Label>
              <Input
                type="number"
                mono
                value={newAlert.threshold}
                onChange={(e) => setNewAlert({ ...newAlert, threshold: Number(e.target.value) })}
                step="0.01"
                className="w-full"
              />
            </div>
            <div className="flex items-end">
              <Button type="submit" className="w-full">Create alert</Button>
            </div>
          </form>
        </Card>
      )}

      <Card padded={false}>
        {alerts.length === 0 ? (
          <EmptyState icon={Bell} title="No alerts yet" description='Click "New alert" to get notified when a symbol crosses a threshold.' />
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-xs font-medium uppercase tracking-wide text-ink-faint">
                <th className="px-4 py-3 font-medium">Symbol</th>
                <th className="px-4 py-3 font-medium">Condition</th>
                <th className="px-4 py-3 font-medium">Threshold</th>
                <th className="px-4 py-3 font-medium">Status</th>
                <th className="px-4 py-3 font-medium">Created</th>
                <th className="px-4 py-3 font-medium"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-line">
              {alerts.map((alert) => (
                <tr key={alert.id} className="hover:bg-paper transition-colors">
                  <td className="px-4 py-2.5 font-mono font-medium text-ink">{alert.symbol}</td>
                  <td className="px-4 py-2.5 text-ink-muted">{conditionLabels[alert.condition]}</td>
                  <td className="px-4 py-2.5 font-mono text-ink tabular-nums">
                    {alert.condition.startsWith("change_pct") ? `${alert.threshold}%` : `$${alert.threshold}`}
                  </td>
                  <td className="px-4 py-2.5">
                    <button onClick={() => toggleAlert(alert.id)}>
                      <StatusBadge active={alert.enabled} />
                    </button>
                  </td>
                  <td className="px-4 py-2.5 text-xs text-ink-faint">
                    {new Date(alert.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-4 py-2.5 text-right">
                    <button
                      onClick={() => deleteAlert(alert.id)}
                      className="text-ink-faint hover:text-loss transition-colors"
                      aria-label={`Delete alert for ${alert.symbol}`}
                    >
                      <X className="w-3.5 h-3.5" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Card>

      <Card className="bg-warn-soft border-warn/20 text-sm text-warn">
        Alert evaluation needs a background worker — in production this would run on a scheduler
        (e.g. Celery beat) checking conditions against live market data.
      </Card>
    </div>
  );
}
