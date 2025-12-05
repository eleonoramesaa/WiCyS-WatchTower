import { useState, useMemo, useEffect } from 'react';
import { Shield, LogOut } from 'lucide-react';
import { Button } from './ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { DeviceTable, Device } from './DeviceTable';
import { DeviceFilters } from './DeviceFilters';
import { DashboardOverview } from './DashboardOverview';

interface DashboardProps {
  onLogout: () => void;
}


export function Dashboard({ onLogout }: DashboardProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [deviceType, setDeviceType] = useState('all');
  const [status, setStatus] = useState('all');
  const [activeTab, setActiveTab] = useState('dashboard');

  const [devices, setDevices] = useState<Device[]>([]);
  const [loadingDevices, setLoadingDevices] = useState(true);
  const [devicesError, setDevicesError] = useState<string | null>(null);

  useEffect(() => {
    async function loadDevices() {
      try {
        const res = await fetch(
          "http://127.0.0.1:5000/api/get_data?select_str=*&from_str=history"
        );

        if (!res.ok) throw new Error(`HTTP ${res.status}`);

        const data = await res.json();

        if (!Array.isArray(data)) {
          console.error("Devices API returned unexpected:", data);
          return;
        }

        const mapped: Device[] = data.map((row: any[]): Device => ({
          // Devices table: id, name, os, mac_address, user_id
          id: row[0],
          name: row[1],
          // Using mac_address as both IP and MAC placeholder for now
          ipAddress: row[2] ?? "",
          macAddress: row[2] ?? "",
          // Placeholder values until you join with History/Users for richer info
          os: "Linux",
          type: "Desktop",
          status: row[4],
          lastSeen: row[1],
          threat: row[5],
        }));

        setDevices(mapped);
        setDevicesError(null);
      } catch (err) {
        console.error("Failed to load devices", err);
        setDevicesError("Failed to load devices");
      } finally {
        setLoadingDevices(false);
      }
    }

    loadDevices();
  }, []);

  const filteredDevices = useMemo(() => {
    return devices.filter((device) => {
      const matchesSearch = 
        device.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        device.ipAddress.includes(searchTerm) ||
        device.macAddress.toLowerCase().includes(searchTerm.toLowerCase()) ||
        device.os.toLowerCase().includes(searchTerm.toLowerCase());
      
      const matchesType = deviceType === 'all' || device.os === deviceType;
      const matchesStatus = status === 'all' || device.status === status;

      return matchesSearch && matchesType && matchesStatus;
    });
  }, [devices, searchTerm, deviceType, status]);

  const handleReset = () => {
    setSearchTerm('');
    setDeviceType('all');
    setStatus('all');
  };

  const handleDeviceClick = (deviceName: string) => {
    setSearchTerm(deviceName);
    setActiveTab('history');
  };

  const stats = {
    total: devices.length
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

          <TabsContent value="dashboard" className="space-y-6">
            <DashboardOverview onDeviceClick={handleDeviceClick} />
          </TabsContent>

          <TabsContent value="history" className="space-y-6">
            {/* Filters */}
            <DeviceFilters
              searchTerm={searchTerm}
              onSearchChange={setSearchTerm}
              deviceType={deviceType}
              onDeviceTypeChange={setDeviceType}
              status={status}
              onStatusChange={setStatus}
              onReset={handleReset}
            />

            {/* Device Table */}
            <Card className="border-slate-700 bg-slate-900/50 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-white">Device History</CardTitle>
                <p className="text-slate-400">
                  Showing {filteredDevices.length} of {stats.total} devices
                </p>
              </CardHeader>
              <CardContent>
                <DeviceTable devices={filteredDevices} />
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}