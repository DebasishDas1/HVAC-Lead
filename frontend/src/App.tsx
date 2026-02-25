import { useState, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { LeadForm } from './components/LeadForm';
import { ChatInterface } from './components/ChatInterface';

interface User {
  name: string;
  email: string;
  phone: string;
}

function App() {
  const [user, setUser] = useState<User | null>(null);
  const [sessionId, setSessionId] = useState<string>('');

  useEffect(() => {
    // Check for existing session and user in localStorage
    const savedUser = localStorage.getItem('hvac_user');
    const savedSessionId = localStorage.getItem('hvac_session_id');

    if (savedUser && savedSessionId) {
      setUser(JSON.parse(savedUser));
      setSessionId(savedSessionId);
    }
  }, []);

  const handleStartChat = (userData: User) => {
    const newSessionId = uuidv4();
    setUser(userData);
    setSessionId(newSessionId);

    // Persist to localStorage
    localStorage.setItem('hvac_user', JSON.stringify(userData));
    localStorage.setItem('hvac_session_id', newSessionId);
  };

  const resetSession = () => {
    localStorage.removeItem('hvac_user');
    localStorage.removeItem('hvac_session_id');
    setUser(null);
    setSessionId('');
  };

  return (
    <div className="min-h-screen bg-slate-100 font-sans text-slate-900">
      <header className="py-6 px-4 bg-white border-b shadow-sm sticky top-0 z-10">
        <div className="max-w-6xl mx-auto flex justify-between items-center">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-slate-900 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold">H</span>
            </div>
            <h1 className="text-xl font-bold tracking-tight">HVAC Specialist</h1>
          </div>
          {user && (
            <Button variant="ghost" onClick={resetSession} className="text-slate-500 hover:text-slate-900 text-xs">
              New Session
            </Button>
          )}
        </div>
      </header>

      <main className="max-w-6xl mx-auto pb-12">
        {!user ? (
          <LeadForm onSubmit={handleStartChat} />
        ) : (
          <ChatInterface user={user} sessionId={sessionId} />
        )}
      </main>

      <footer className="py-6 text-center text-slate-500 text-sm border-t bg-white">
        © 2026 HVAC Specialist Co. All rights reserved.
      </footer>
    </div>
  );
}

// Simple Button for the header since we don't want to import shadcn Button which might have complex deps here
const Button = ({ children, onClick, variant, className }: any) => (
  <button
    onClick={onClick}
    className={`${variant === 'ghost' ? 'hover:bg-slate-100' : 'bg-slate-900 text-white'} px-4 py-2 rounded-md transition-colors ${className}`}
  >
    {children}
  </button>
);

export default App;
