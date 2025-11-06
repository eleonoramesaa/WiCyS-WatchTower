import { useState } from 'react';
import { LandingPage } from './components/LandingPage';
import { LoginPage } from './components/LoginPage';
import { RegisterPage } from './components/RegisterPage';
import { Dashboard } from './components/Dashboard';

type View = 'landing' | 'login' | 'register' | 'dashboard';

export default function App() {
  const [currentView, setCurrentView] = useState<View>('landing');

  const handleLoginClick = () => {
    setCurrentView('login');
  };

  const handleRegisterClick = () => {
    setCurrentView('register');
  };

  const handleBackToLanding = () => {
    setCurrentView('landing');
  };

  const handleBackToLogin = () => {
    setCurrentView('login');
  };

  const handleLogin = () => {
    setCurrentView('dashboard');
  };

  const handleRegister = () => {
    setCurrentView('dashboard');
  };

  const handleLogout = () => {
    setCurrentView('landing');
  };

  return (
    <>
      {currentView === 'landing' && (
        <LandingPage onLoginClick={handleLoginClick} />
      )}
      {currentView === 'login' && (
        <LoginPage 
          onLogin={handleLogin} 
          onBackClick={handleBackToLanding}
          onRegisterClick={handleRegisterClick}
        />
      )}
      {currentView === 'register' && (
        <RegisterPage 
          onRegister={handleRegister}
          onBackClick={handleBackToLogin}
        />
      )}
      {currentView === 'dashboard' && (
        <Dashboard onLogout={handleLogout} />
      )}
    </>
  );
}
