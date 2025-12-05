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
          "http://localhost:5000/api/get_data?sql_query=SELECT%20d.id%2C%20d.name%2C%20h.device_type%2C%20d.os%2C%20h.outgoing_ip%2C%20d.mac_address%2C%20h.connection_status%2C%20h.threat%2C%20h.datetime%20FROM%20DEVICES%20d%20INNER%20JOIN%20(%20SELECT%20device_id%2C%20outgoing_ip%2C%20connection_status%2C%20device_type%2C%20datetime%2C%20threat%2C%20ROW_NUMBER()%20OVER%20(PARTITION%20BY%20device_id%20ORDER%20BY%20datetime%20DESC)%20as%20rn%20FROM%20HISTORY%20)%20h%20ON%20d.id%20%3D%20h.device_id%20WHERE%20h.rn%20%3D%201"
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
          ipAddress: row[4] ?? "",
          macAddress: row[5] ?? "",
          // Placeholder values until you join with History/Users for richer info
          os: row[3],
          type: row[2],
          status: row[6],
          lastSeen: row[8],
          threat: row[7],
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

    const intervalId = setInterval(() => {
        loadDevices(); 
       
      }, 5000);

      return () => clearInterval(intervalId);

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
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6 ">
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