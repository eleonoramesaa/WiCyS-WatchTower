import { Activity, Shield, AlertTriangle, TrendingUp, TrendingDown, Monitor, Smartphone, Tv, Tablet, MoreVertical, CheckCircle } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

const networkTrafficData = [
  { name: 'Mon', incoming: 2.1, outgoing: 1.5 },
  { name: 'Tue', incoming: 2.4, outgoing: 1.8 },
  { name: 'Wed', incoming: 2.2, outgoing: 1.6 },
  { name: 'Thu', incoming: 2.5, outgoing: 1.9 },
  { name: 'Fri', incoming: 2.3, outgoing: 1.7 },
];

const threatDetectionData = [
  { name: 'High', value: 5, fill: '#ef4444' },
  { name: 'Medium', value: 12, fill: '#f59e0b' },
  { name: 'Low', value: 21, fill: '#10b981' },
];

const trustedDevices = [
  { name: 'MacBook Pro', ip: '192.168.1.180', icon: Monitor, status: 'Active now', statusColor: 'text-green-400' },
  { name: 'iPhone 14 Pro', ip: '192.168.1.142', icon: Smartphone, status: 'Active now', statusColor: 'text-green-400' },
  { name: 'Desktop PC', ip: '192.168.1.101', icon: Monitor, status: '5 min ago', statusColor: 'text-slate-400' },
  { name: 'iPad Air', ip: '192.168.1.139', icon: Tablet, status: '1 hour ago', statusColor: 'text-slate-400' },
  { name: 'Smart TV', ip: '192.168.1.145', icon: Tv, status: 'Active now', statusColor: 'text-green-400', badge: 'Medium Risk' },
  { name: 'Android Phone', ip: '192.168.1.132', icon: Smartphone, status: '1 day ago', statusColor: 'text-slate-400' },
];

interface DashboardOverviewProps {
  onDeviceClick: (deviceName: string) => void;
}

export function DashboardOverview({ onDeviceClick }: DashboardOverviewProps) {
  return (
    <div className="grid grid-cols-1 xl:grid-cols-[1fr_280px] gap-6">
      {/* Main Content */}
      <div className="space-y-6">
        {/* Top Stats Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card className="border-slate-700 bg-slate-900/50 backdrop-blur-sm">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <div>
                <p className="text-slate-400">Active Connections</p>
                <div className="flex items-baseline gap-2 mt-1">
                  <span className="text-white"></span>
                  <span className="text-green-400 flex items-center gap-1">
                    <TrendingUp className="w-3 h-3" />
                    
                  </span>
                </div>
              </div>
              <div className="p-2 bg-blue-500/10 rounded-lg">
                <Activity className="w-5 h-5 text-blue-400" />
              </div>
            </CardHeader>
          </Card>


          <Card className="border-slate-700 bg-slate-900/50 backdrop-blur-sm">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <div>
                <p className="text-slate-400">Active Alerts</p>
                <div className="flex items-baseline gap-2 mt-1">
                  <span className="text-white"></span>
                  <span className="text-green-400 flex items-center gap-1">
                    <TrendingUp className="w-3 h-3" />
                    
                  </span>
                </div>
              </div>
              <div className="p-2 bg-red-500/10 rounded-lg">
                <AlertTriangle className="w-5 h-5 text-red-400" />
              </div>
            </CardHeader>
          </Card>

        </div>
        
        {/* Security Alerts */}
        <Card className="border-slate-700 bg-slate-900/50 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="text-white">Security Alerts</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-start gap-3 p-3 rounded-lg bg-red-500/10 border border-red-500/20">
                <div className="p-2 bg-red-500/20 rounded">
                  <AlertTriangle className="w-4 h-4 text-red-400" />
                </div>
                <div className="flex-1">
                  <p className="text-white">Suspicious Activity</p>
                  <p className="text-slate-400">Multiple failed login attempts detected</p>
                  <p className="text-slate-500 mt-1">2 min ago</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      

      {/* Trusted Devices */}
      
        <Card className="border-slate-700 bg-slate-900/50 backdrop-blur-sm">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-white">Trusted Devices</CardTitle>
              <span className="text-slate-400">6 devices</span>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {trustedDevices.map((device, index) => {
                const DeviceIcon = device.icon;
                return (
                  <div 
                    key={index} 
                    onClick={() => onDeviceClick(device.name)}
                    className="flex items-start gap-3 p-2 rounded-lg hover:bg-slate-800/50 transition-colors cursor-pointer"
                  >
                    <div className="p-2 bg-slate-800 rounded">
                      <DeviceIcon className="w-4 h-4 text-blue-400" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between gap-2">
                        <p className="text-white truncate">{device.name}</p>
                        <button className="text-slate-400 hover:text-white">
                          <MoreVertical className="w-4 h-4" />
                        </button>
                      </div>
                      <p className="text-slate-400 font-mono">{device.ip}</p>
                      <div className="flex items-center gap-2 mt-1">
                        <p className={device.statusColor}>{device.status}</p>
                        {device.badge && (
                          <Badge className="bg-yellow-500/10 text-yellow-400 border-yellow-500/20">
                            {device.badge}
                          </Badge>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
