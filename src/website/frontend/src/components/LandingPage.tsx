import { Shield, Monitor, Lock, Activity, Bell, BarChart3, ChevronDown } from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';

interface LandingPageProps {
  onLoginClick: () => void;
}

export function LandingPage({ onLoginClick }: LandingPageProps) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
      {/* Background pattern */}
      <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGRlZnM+PHBhdHRlcm4gaWQ9ImdyaWQiIHdpZHRoPSI2MCIgaGVpZ2h0PSI2MCIgcGF0dGVyblVuaXRzPSJ1c2VyU3BhY2VPblVzZSI+PHBhdGggZD0iTSAxMCAwIEwgMCAwIDAgMTAiIGZpbGw9Im5vbmUiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS1vcGFjaXR5PSIwLjA1IiBzdHJva2Utd2lkdGg9IjEiLz48L3BhdHRlcm4+PC9kZWZzPjxyZWN0IHdpZHRoPSIxMDAlIiBoZWlnaHQ9IjEwMCUiIGZpbGw9InVybCgjZ3JpZCkiLz48L3N2Zz4=')] opacity-40"></div>

      <div className="relative z-10">
        {/* Header */}
        <header className="border-b border-slate-700/50 bg-slate-900/50 backdrop-blur-sm">
          <div className="container mx-auto px-4 py-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-500/10 rounded-lg">
                <Shield className="w-8 h-8 text-blue-400" />
              </div>
              <div>
                <h1 className="text-white">WiCyS WatchTower</h1>
                <p className="text-slate-400">Cybersecurity Monitoring Platform</p>
              </div>
            </div>
            <Button 
              onClick={onLoginClick}
              className="bg-blue-600 hover:bg-blue-700"
            >
              <Lock className="w-4 h-4 mr-2" />
              Log In
            </Button>
          </div>
        </header>
      <br></br>
        {/* Hero Section */}
        <section className="container mx-auto px-4 py-20 text-center">
          <div className="max-w-4xl mx-auto space-y-6">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-500/10 border border-blue-500/20">
              <Shield className="w-4 h-4 text-blue-400" />
              <span className="text-blue-300">Enterprise Security Solution</span>
            </div>
            
            <h1 className="landing-h1">
             <b>Comprehensive Network Security Monitoring</b>
            </h1>
            
            <p className="text-slate-300 max-w-2xl mx-auto">
              WiCyS WatchTower provides real-time device monitoring, threat detection, and comprehensive 
              security analytics to protect your network infrastructure. Stay informed, stay secure.
      
            </p>
            <br></br>
            <div className="flex flex-col sm:flex-row gap-4 justify-center pt-4">
              <Button 
                onClick={onLoginClick}
                className="bg-blue-600 hover:bg-blue-700"
              >
                Get Started
              </Button>
              <Button 
                variant="outline"
                className="border-slate-600 text-slate-300 hover:bg-slate-800 bg-[rgba(0,0,0,0.85)]"
                onClick={() => {
                  document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' });
                }}
              >
                Learn More
              </Button>
            </div>
<br></br>
<br></br>
            <div className="pt-12 animate-bounce">
              <ChevronDown className="w-6 h-6 text-slate-400 mx-auto" />
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section id="features" className="container mx-auto px-4 py-20">
          <div className="text-center mb-12">
            <h3 className="text-white mb-2">Powerful Features</h3>
            <p className="text-slate-400">
              Everything you need to monitor and secure your network
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
            <Card className="border-slate-700 bg-slate-900/50 backdrop-blur-sm hover:bg-slate-800/50 transition-colors">
              <CardHeader>
                <div className="p-3 bg-blue-500/10 rounded-lg w-fit mb-4">
                  <Monitor className="w-6 h-6 text-blue-400" />
                </div>
                <CardTitle className="text-white">Real-Time Monitoring</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-slate-400">
                  Monitor all connected devices in real-time with instant status updates and connectivity tracking.
                </p>
              </CardContent>
            </Card>

            <Card className="border-slate-700 bg-slate-900/50 backdrop-blur-sm hover:bg-slate-800/50 transition-colors">
              <CardHeader>
                <div className="p-3 bg-green-500/10 rounded-lg w-fit mb-4">
                  <Activity className="w-6 h-6 text-green-400" />
                </div>
                <CardTitle className="text-white">Device History</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-slate-400">
                  Track comprehensive device connection history with detailed logs and activity timelines.
                </p>
              </CardContent>
            </Card>

            <Card className="border-slate-700 bg-slate-900/50 backdrop-blur-sm hover:bg-slate-800/50 transition-colors">
              <CardHeader>
                <div className="p-3 bg-yellow-500/10 rounded-lg w-fit mb-4">
                  <Bell className="w-6 h-6 text-yellow-400" />
                </div>
                <CardTitle className="text-white">Threat Alerts</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-slate-400">
                  Receive instant notifications for suspicious activity and potential security threats.
                </p>
              </CardContent>
            </Card>

            <Card className="border-slate-700 bg-slate-900/50 backdrop-blur-sm hover:bg-slate-800/50 transition-colors">
              <CardHeader>
                <div className="p-3 bg-red-500/10 rounded-lg w-fit mb-4">
                  <Lock className="w-6 h-6 text-red-400" />
                </div>
                <CardTitle className="text-white">Access Control</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-slate-400">
                  Manage user permissions and device access with enterprise-grade security controls.
                </p>
              </CardContent>
            </Card>

            
          </div>
        </section>

        {/* CTA Section */}
        <section className="container mx-auto px-4 py-20">
          <Card className="border-2 border-slate-700 bg-gradient-to-r from-blue-900/50 to-purple-900/50 backdrop-blur-sm max-w-4xl mx-auto">
            <CardContent className="text-center py-12">
              <Shield className="w-16 h-16 text-blue-400 mx-auto mb-6" />
              <h3 className="text-white mb-4">
                Ready to secure your network?
              </h3>
              <p className="text-slate-300 mb-8 max-w-2xl mx-auto">
                Join organizations worldwide that trust WiCyS WatchTower to protect their network infrastructure.
              </p>
              <Button 
                onClick={onLoginClick}
                className="bg-blue-600 hover:bg-blue-700"
              >
                Access Dashboard
              </Button>
            </CardContent>
          </Card>
        </section>

        {/* Footer */}
        <footer className="border-t border-slate-700/50 py-8">
          <div className="container mx-auto px-4 text-center text-slate-400">
            <p>&copy; 2025 WiCyS WatchTower. All rights reserved.</p>
          </div>
        </footer>
      </div>
    </div>
  );
}
