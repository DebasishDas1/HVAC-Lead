import { useState, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { LeadForm } from './components/LeadForm';
import { ChatInterface } from './components/ChatInterface';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { Thermometer, RefreshCw, Phone, Mail, MapPin, Facebook, Twitter, Instagram, Linkedin, ArrowRight } from 'lucide-react';

interface User {
  name: string;
  email: string;
  phone: string;
}

function App() {
  const [user, setUser] = useState<User | null>(null);
  const [sessionId, setSessionId] = useState<string>('');

  useEffect(() => {
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
    <div className="min-h-screen bg-background font-sans text-foreground selection:bg-primary/20">
      <div className="hidden border-b bg-primary py-2 text-center text-xs font-medium text-primary-foreground md:block">
        Special Offer: Get 15% off your first routine maintenance service! Call us now.
      </div>
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container mx-auto px-4 flex h-20 items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="group relative">
              <div className="absolute -inset-1 rounded-xl bg-gradient-to-r from-primary to-blue-600 opacity-25 blur transition duration-1000 group-hover:opacity-100 group-hover:duration-200"></div>
              <div className="relative flex h-12 w-12 items-center justify-center rounded-xl bg-primary text-primary-foreground shadow-xl">
                <Thermometer className="h-7 w-7 transition-transform group-hover:scale-110" />
              </div>
            </div>
            <div className="flex flex-col">
              <span className="text-2xl font-black tracking-tighter bg-gradient-to-r from-primary via-blue-600 to-primary/80 bg-clip-text text-transparent uppercase">
                HVAC Specialist
              </span>
              <span className="text-[10px] font-bold uppercase tracking-[0.2em] text-muted-foreground/80 -mt-1">
                Premium Climate Control
              </span>
            </div>
          </div>

          <div className="flex items-center gap-6">
            <div className="hidden lg:flex items-center gap-4 border-r pr-6 mr-2">
              <div className="flex flex-col items-end">
                <span className="text-xs font-medium text-muted-foreground">Emergency Support</span>
                <span className="text-sm font-bold">(555) 123-4567</span>
              </div>
              <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center text-primary">
                <Phone className="h-5 w-5" />
              </div>
            </div>

            {user && (
              <Button
                variant="outline"
                size="sm"
                onClick={resetSession}
                className="hidden sm:flex gap-2 border-primary/20 hover:bg-primary/5 hover:text-primary transition-all duration-300 rounded-full px-5"
              >
                <RefreshCw className="h-4 w-4" />
                New Session
              </Button>
            )}
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 relative py-12 md:py-20 min-h-[calc(100vh-80px-300px)]">
        <div className="mx-auto max-w-5xl">
          {!user ? (
            <LeadForm onSubmit={handleStartChat} />
          ) : (
            <ChatInterface user={user} sessionId={sessionId} />
          )}
        </div>
      </main>

      <footer className="border-t bg-slate-950 text-slate-200">
        <div className="container mx-auto px-4 py-16">
          <div className="grid grid-cols-1 gap-12 md:grid-cols-2 lg:grid-cols-4">
            <div className="space-y-6">
              <div className="flex items-center gap-2">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-white">
                  <Thermometer className="h-5 w-5" />
                </div>
                <span className="text-xl font-bold tracking-tight text-white uppercase">HVAC Specialist</span>
              </div>
              <p className="text-sm text-slate-400 leading-relaxed max-w-xs">
                Providing premium heating, cooling, and air quality solutions for residential and commercial spaces since 1998.
              </p>
              <div className="flex items-center gap-4">
                <a href="#" className="h-9 w-9 rounded-full bg-slate-900 flex items-center justify-center hover:bg-primary hover:text-white transition-all"><Facebook size={16} /></a>
                <a href="#" className="h-9 w-9 rounded-full bg-slate-900 flex items-center justify-center hover:bg-primary hover:text-white transition-all"><Twitter size={16} /></a>
                <a href="#" className="h-9 w-9 rounded-full bg-slate-900 flex items-center justify-center hover:bg-primary hover:text-white transition-all"><Instagram size={16} /></a>
                <a href="#" className="h-9 w-9 rounded-full bg-slate-900 flex items-center justify-center hover:bg-primary hover:text-white transition-all"><Linkedin size={16} /></a>
              </div>
            </div>

            <div className="space-y-6">
              <h4 className="text-sm font-bold uppercase tracking-widest text-white underline underline-offset-8 decoration-primary/40">Our Services</h4>
              <ul className="space-y-3 text-sm text-slate-400">
                <li><a href="#" className="hover:text-primary transition-colors">Emergency Repair</a></li>
                <li><a href="#" className="hover:text-primary transition-colors">AC Installation</a></li>
                <li><a href="#" className="hover:text-primary transition-colors">Heating Systems</a></li>
                <li><a href="#" className="hover:text-primary transition-colors">Routine Maintenance</a></li>
                <li><a href="#" className="hover:text-primary transition-colors">Air Quality Testing</a></li>
              </ul>
            </div>

            <div className="space-y-6">
              <h4 className="text-sm font-bold uppercase tracking-widest text-white underline underline-offset-8 decoration-primary/40">Contact Info</h4>
              <ul className="space-y-4 text-sm text-slate-400">
                <li className="flex items-start gap-3">
                  <MapPin className="h-5 w-5 text-primary shrink-0" />
                  <span>123 service lane, Suite 400<br />Modern City, MC 12345</span>
                </li>
                <li className="flex items-center gap-3">
                  <Phone className="h-5 w-5 text-primary shrink-0" />
                  <span>(555) 123-4567</span>
                </li>
                <li className="flex items-center gap-3">
                  <Mail className="h-5 w-5 text-primary shrink-0" />
                  <span>support@hvacspecialist.com</span>
                </li>
              </ul>
            </div>

            <div className="space-y-6">
              <h4 className="text-sm font-bold uppercase tracking-widest text-white underline underline-offset-8 decoration-primary/40">Newsletter</h4>
              <p className="text-sm text-slate-400">Subscribe for maintenance tips and seasonal discounts.</p>
              <div className="relative">
                <input
                  type="email"
                  placeholder="Your email"
                  className="w-full bg-slate-900 border-none rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all text-white"
                />
                <button className="absolute right-2 top-2 h-8 w-8 bg-primary rounded-lg flex items-center justify-center text-white hover:bg-primary/80 transition-all focus:outline-none focus:ring-2 focus:ring-primary/20">
                  <ArrowRight size={16} />
                </button>
              </div>
            </div>
          </div>

          <Separator className="my-12 bg-slate-900" />

          <div className="flex flex-col items-center justify-between gap-6 md:flex-row text-xs text-slate-500 font-medium">
            <p>© 2026 HVAC Specialist Co. All rights reserved.</p>
            <div className="flex items-center gap-8">
              <a href="#" className="hover:text-slate-300 transition-colors uppercase tracking-widest">Privacy Policy</a>
              <a href="#" className="hover:text-slate-300 transition-colors uppercase tracking-widest">Terms</a>
              <a href="#" className="hover:text-slate-300 transition-colors uppercase tracking-widest">Sitemap</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
