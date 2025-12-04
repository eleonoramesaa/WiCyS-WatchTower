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
  },
  {
    id: '4',
    name: 'Database-Server',
    type: 'Server',
    ipAddress: '192.168.1.50',
    macAddress: '00:50:56:C0:00:08',
    status: 'Online',
    lastSeen: 'Just now',
    location: 'Data Center',
  },
  {
    id: '5',
    name: 'Legacy-PC',
    type: 'Desktop',
    ipAddress: '192.168.1.89',
    macAddress: '00:0C:29:4F:1E:B3',
    status: 'Offline',
    lastSeen: '3 hours ago',
    location: 'Office - Floor 2',
  },
  {
    id: '6',
    name: 'Smart-Thermostat',
    type: 'IoT',
    ipAddress: '192.168.1.205',
    macAddress: 'B8:27:EB:A4:5C:8F',
    status: 'Online',
    lastSeen: '10 minutes ago',
    location: 'Building HVAC',
  },
  {
    id: '7',
    name: 'Web-Server-01',
    type: 'Server',
    ipAddress: '192.168.1.51',
    macAddress: '00:50:56:C0:00:09',
    status: 'Online',
    lastSeen: 'Just now',
    location: 'Data Center',
  },
  {
    id: '8',
    name: 'Android-Tablet',
    type: 'Mobile',
    ipAddress: '192.168.1.178',
    macAddress: 'F0:25:B7:3E:9A:1C',
    status: 'Offline',
    lastSeen: '1 day ago',
    location: 'Conference Room',
  },
  {
    id: '9',
    name: 'Security-Camera-01',
    type: 'IoT',
    ipAddress: '192.168.1.210',
    macAddress: 'E0:23:71:B5:4F:2A',
    status: 'Warning',
    lastSeen: '15 minutes ago',
    location: 'Entrance',
  },
  {
    id: '10',
    name: 'MacBook-Pro',
    type: 'Desktop',
    ipAddress: '192.168.1.134',
    macAddress: '3C:22:FB:2B:7E:8D',
    status: 'Online',
    lastSeen: '1 minute ago',
    location: 'Office - Floor 3',
  },
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
