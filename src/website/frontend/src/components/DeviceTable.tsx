import { Monitor, Smartphone, Server, Router, Wifi, CheckCircle, XCircle, AlertTriangle } from 'lucide-react';
import { Badge } from './ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';

export interface Device {
  id: string;
  name: string;
  type: 'Desktop' | 'Mobile' | 'Server' | 'Router' | 'IoT';
  ipAddress: string;
  status: 'Online' | 'Offline' | 'Warning';
  lastSeen: string;
  location: string;
  macAddress: string;
}

interface DeviceTableProps {
  devices: Device[];
}

const deviceIcons = {
  Desktop: Monitor,
  Mobile: Smartphone,
  Server: Server,
  Router: Router,
  IoT: Wifi,
};

const statusIcons = {
  Online: CheckCircle,
  Offline: XCircle,
  Warning: AlertTriangle,
};

const statusColors = {
  Online: 'bg-green-500/10 text-green-400 border-green-500/20',
  Offline: 'bg-red-500/10 text-red-400 border-red-500/20',
  Warning: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20',
};

export function DeviceTable({ devices }: DeviceTableProps) {
  if (devices.length === 0) {
    return (
      <div className="text-center py-12 text-slate-400">
        <Monitor className="w-12 h-12 mx-auto mb-4 opacity-50" />
        <p>No devices found</p>
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-slate-700 overflow-hidden">
      <Table>
        <TableHeader>
          <TableRow className="border-slate-700 hover:bg-slate-800/50">
            <TableHead className="text-slate-300">Device</TableHead>
            <TableHead className="text-slate-300">Type</TableHead>
            <TableHead className="text-slate-300">IP Address</TableHead>
            <TableHead className="text-slate-300">MAC Address</TableHead>
            <TableHead className="text-slate-300">Status</TableHead>
            <TableHead className="text-slate-300">Last Seen</TableHead>
            <TableHead className="text-slate-300">Location</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {devices.map((device) => {
            const DeviceIcon = deviceIcons[device.type];
            const StatusIcon = statusIcons[device.status];
            
            return (
              <TableRow key={device.id} className="border-slate-700 hover:bg-slate-800/50">
                <TableCell className="text-white">
                  <div className="flex items-center gap-2">
                    <div className="p-2 bg-slate-800 rounded">
                      <DeviceIcon className="w-4 h-4 text-blue-400" />
                    </div>
                    <span>{device.name}</span>
                  </div>
                </TableCell>
                <TableCell className="text-slate-300">{device.type}</TableCell>
                <TableCell className="text-slate-300 font-mono">{device.ipAddress}</TableCell>
                <TableCell className="text-slate-300 font-mono">{device.macAddress}</TableCell>
                <TableCell>
                  <Badge className={statusColors[device.status]}>
                    <StatusIcon className="w-3 h-3 mr-1" />
                    {device.status}
                  </Badge>
                </TableCell>
                <TableCell className="text-slate-300">{device.lastSeen}</TableCell>
                <TableCell className="text-slate-300">{device.location}</TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </div>
  );
}
