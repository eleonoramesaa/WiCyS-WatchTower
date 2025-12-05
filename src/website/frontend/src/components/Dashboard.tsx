import { useState, useEffect, useMemo } from "react";
import { Shield, LogOut, Activity, AlertTriangle, TrendingUp } from "lucide-react";
import { Button } from "./ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { DeviceFilters } from "./DeviceFilters";
import { DashboardOverview } from "./DashboardOverview";

// ----------------------------
// History Table Component
// ----------------------------
function HistoryTable({ rows }: { rows: any[] }) {
  return (
    <table className="w-full text-left text-white">
      <thead>
        <tr className="border-b border-slate-700">
          <th className="p-2">Device ID</th>
          <th className="p-2">Timestamp</th>
          <th className="p-2">IP</th>
          <th className="p-2">Status</th>
          <th className="p-2">Threat</th>
        </tr>
      </thead>
      <tbody>
        {rows.map((row, index) => (
          <tr key={index} className="border-b border-slate-800">
            <td className="p-2">{row.deviceId}</td>
            <td className="p-2">{row.timestamp}</td>
            <td className="p-2">{row.outgoingIp}</td>
            <td
              className={`p-2 ${
                row.connectionStatus === "Connected"
                  ? "text-green-400"
                  : "text-red-400"
              }`}
            >
              {row.connectionStatus}
            </td>
            <td
              className={`p-2 ${
                row.threat === "Suspicious"
                  ? "text-red-400"
                  : "text-slate-400"
              }`}
            >
              {row.threat}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

// ----------------------------
// Main Dashboard Component
// ----------------------------
interface DashboardProps {
  onLogout: () => void;
}

export function Dashboard({ onLogout }: DashboardProps) {
  const [searchTerm, setSearchTerm] = useState("");
  const [deviceType, setDeviceType] = useState("all"); // normal/suspicious
  const [status, setStatus] = useState("all"); // connected/offline
  const [activeTab, setActiveTab] = useState("dashboard");

  // REAL backend history
  const [historyRows, setHistoryRows] = useState<any[]>([]);
  const [loadingHistory, setLoadingHistory] = useState(true);

  // ------------------------------------
  // Load History from Backend (Polling)
  // ------------------------------------
  async function loadHistory() {
    try {
      const res = await fetch(
        "http://127.0.0.1:5000/api/get_data?select_str=*&from_str=history"
      );

      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      const data = await res.json();

      if (!Array.isArray(data)) {
        console.error("History API returned unexpected:", data);
        return;
      }

      // Format rows for UI
      setHistoryRows(
        data.map((row: any[]) => ({
          deviceId: row[0],
          timestamp: row[1],
          outgoingIp: row[2],
          connectionStatus: row[4],
          threat: row[5] === 1 ? "Suspicious" : "Normal",
        }))
      );
    } catch (err) {
      console.error("Failed to load history:", err);
    } finally {
      setLoadingHistory(false);
    }
  }

  // Poll every 2 seconds
  useEffect(() => {
    loadHistory();
    const interval = setInterval(loadHistory, 2000);
    return () => clearInterval(interval);
  }, []);

  // ----------------------------
  // Filtering logic for History
  // ----------------------------
  const filteredHistory = useMemo(() => {
    return historyRows.filter((row) => {
      const matchesSearch =
        row.deviceId.toString().includes(searchTerm.toLowerCase()) ||
        row.outgoingIp?.includes(searchTerm.toLowerCase());

      const matchesStatus =
        status === "all" || row.connectionStatus === status;

      const matchesThreat =
        deviceType === "all" ||
        (deviceType === "suspicious" && row.threat === "Suspicious") ||
        (deviceType === "normal" && row.threat === "Normal");

      return matchesSearch && matchesStatus && matchesThreat;
    });
  }, [searchTerm, deviceType, status, historyRows]);

  const handleReset = () => {
    setSearchTerm("");
    setDeviceType("all");
    setStatus("all");
  };

  const handleDeviceClick = (deviceName: string) => {
    setSearchTerm(deviceName);
    setActiveTab("history");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Header */}
      <header className="border-b border-slate-700 bg-slate-900/50 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-500/10 rounded-lg">
              <Shield className="w-6 h-6 text-blue-400" />
            </div>
            <div>
              <h1 className="text-white">WiCyS WatchTower</h1>
              <p className="text-slate-400">Device Management & Monitoring</p>
            </div>
          </div>

          <Button
            variant="outline"
            onClick={onLogout}
            className="border-slate-700 text-slate-300 hover:bg-slate-800 bg-[rgba(0,0,0,0.8)]"
          >
            <LogOut className="w-4 h-4 mr-2" />
            Logout
          </Button>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="bg-slate-900/50 border border-slate-700">
            <TabsTrigger value="dashboard" className="data-[state=active]:bg-slate-800">
              Dashboard
            </TabsTrigger>
            <TabsTrigger value="history" className="data-[state=active]:bg-slate-800">
              History
            </TabsTrigger>
          </TabsList>

          {/* Dashboard Tab */}
          <TabsContent value="dashboard" className="space-y-6">
            <DashboardOverview onDeviceClick={handleDeviceClick} />
          </TabsContent>

          {/* History Tab */}
          <TabsContent value="history" className="space-y-6">
            <DeviceFilters
              searchTerm={searchTerm}
              onSearchChange={setSearchTerm}
              deviceType={deviceType}            // normal/suspicious
              onDeviceTypeChange={setDeviceType}
              status={status}                   // connected/offline/all
              onStatusChange={setStatus}
              onReset={handleReset}
            />

            <Card className="border-slate-700 bg-slate-900/50 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-white">Device History</CardTitle>
                <p className="text-slate-400">
                  Showing {filteredHistory.length} entries
                </p>
              </CardHeader>
              <CardContent>
                {loadingHistory ? (
                  <p className="text-slate-400">Loading...</p>
                ) : (
                  <HistoryTable rows={filteredHistory} />
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}
