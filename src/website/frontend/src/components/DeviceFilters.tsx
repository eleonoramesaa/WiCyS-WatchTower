import { Search, Filter } from 'lucide-react';
import { Input } from './ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Button } from './ui/button';

interface DeviceFiltersProps {
  searchTerm: string;
  onSearchChange: (value: string) => void;
  deviceType: string;
  onDeviceTypeChange: (value: string) => void;
  status: string;
  onStatusChange: (value: string) => void;
  onReset: () => void;
}

export function DeviceFilters({
  searchTerm,
  onSearchChange,
  deviceType,
  onDeviceTypeChange,
  status,
  onStatusChange,
  onReset
}: DeviceFiltersProps) {
  return (
    <div className="flex flex-col sm:flex-row gap-4 mb-6">
      <div className="relative flex-1">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-400" />
        <Input
          placeholder="Search devices, IP addresses..."
          value={searchTerm}
          onChange={(e) => onSearchChange(e.target.value)}
          className="pl-10 bg-slate-800 border-slate-700 text-white placeholder:text-slate-500"
        />
      </div>
      
      <Select value={deviceType} onValueChange={onDeviceTypeChange}>
        <SelectTrigger className="w-full sm:w-[180px] bg-slate-800 border-slate-700 text-white">
          <SelectValue placeholder="Device Type" />
        </SelectTrigger>
        <SelectContent className="bg-slate-800 border-slate-700">
          <SelectItem value="all" className="text-white">All Types</SelectItem>
          <SelectItem value="Desktop" className="text-white">Desktop</SelectItem>
          <SelectItem value="Mobile" className="text-white">Mobile</SelectItem>
          <SelectItem value="Server" className="text-white">Server</SelectItem>
          <SelectItem value="Router" className="text-white">Router</SelectItem>
          <SelectItem value="IoT" className="text-white">IoT Device</SelectItem>
        </SelectContent>
      </Select>

      <Select value={status} onValueChange={onStatusChange}>
        <SelectTrigger className="w-full sm:w-[180px] bg-slate-800 border-slate-700 text-white">
          <SelectValue placeholder="Status" />
        </SelectTrigger>
        <SelectContent className="bg-slate-800 border-slate-700">
          <SelectItem value="all" className="text-white">All Status</SelectItem>
          <SelectItem value="Online" className="text-white">Online</SelectItem>
          <SelectItem value="Offline" className="text-white">Offline</SelectItem>
          <SelectItem value="Warning" className="text-white">Warning</SelectItem>
        </SelectContent>
      </Select>

      <Button 
        variant="outline" 
        onClick={onReset}
        className="border-slate-700 text-slate-300 hover:bg-slate-800 bg-[rgba(0,0,0,0.8)]"
      >
        <Filter className="w-4 h-4 mr-2" />
        Reset
      </Button>
    </div>
  );
}
