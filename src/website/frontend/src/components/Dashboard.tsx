import { useState, useMemo } from 'react';
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

// Mock device data
const mockDevices: Device[] = [
  {
    id: '1',
    name: 'Workstation-01',
    type: 'Desktop',
    ipAddress: '192.168.1.101',
    macAddress: '00:1B:44:11:3A:B7',
    status: 'Online',
    lastSeen: '2 minutes ago',
    location: 'Office - Floor 3',
  },
  {
    id: '2',
    name: 'iPhone-Dev',
    type: 'Mobile',
    ipAddress: '192.168.1.142',
    macAddress: 'A4:5E:60:E8:9C:2D',
    status: 'Online',
    lastSeen: '5 minutes ago',
    location: 'Mobile Network',
  },
  {
    id: '3',
    name: 'MainRouter',
    type: 'Router',
    ipAddress: '192.168.1.1',
    macAddress: 'C8:3A:35:30:48:F0',
    status: 'Warning',
    lastSeen: '1 minute ago',
    location: 'Server Room',
  }
];

export function Dashboard({ onLogout }: DashboardProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [deviceType, setDeviceType] = useState('all');
  const [status, setStatus] = useState('all');
  const [activeTab, setActiveTab] = useState('dashboard');

  const filteredDevices = useMemo(() => {
    return mockDevices.filter((device) => {
      const matchesSearch = 
        device.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        device.ipAddress.includes(searchTerm) ||
        device.macAddress.toLowerCase().includes(searchTerm.toLowerCase()) ||
        device.location.toLowerCase().includes(searchTerm.toLowerCase());
      
      const matchesType = deviceType === 'all' || device.type === deviceType;
      const matchesStatus = status === 'all' || device.status === status;

      return matchesSearch && matchesType && matchesStatus;
    });
  }, [searchTerm, deviceType, status]);

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
    total: mockDevices.length,
    online: mockDevices.filter(d => d.status === 'Online').length,
    warnings: mockDevices.filter(d => d.status === 'Warning').length,
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
