import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Send, User, Bot, Loader2 } from 'lucide-react';
import axios from 'axios';
import { cn } from '@/lib/utils';

interface Message {
    role: 'user' | 'assistant';
    content: string;
}

interface ChatInterfaceProps {
    user: { name: string; email: string; phone: string };
    sessionId: string;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({ user, sessionId }) => {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [isQualified, setIsQualified] = useState(false);
    const scrollRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        // Initial greeting
        setMessages([
            {
                role: 'assistant',
                content: `Hello ${user.name}! I'm your HVAC service assistant. How can I help you today? Are you looking for a repair, installation, or routine maintenance?`
            }
        ]);
    }, [user.name]);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollIntoView({ behavior: 'smooth' });
        }
    }, [messages]);

    const sendMessage = async () => {
        if (!input.trim() || isLoading || isQualified) return;

        const userMessage = input.trim();
        setInput('');
        setMessages((prev) => [...prev, { role: 'user', content: userMessage }]);
        setIsLoading(true);

        try {
            const response = await axios.post('http://localhost:8000/chat', {
                sessionId,
                user,
                message: userMessage
            });

            const { response: aiResponse, qualified } = response.data;

            setMessages((prev) => [...prev, { role: 'assistant', content: aiResponse }]);
            setIsQualified(qualified);
        } catch (error) {
            console.error('Error sending message:', error);
            setMessages((prev) => [
                ...prev,
                { role: 'assistant', content: "I'm sorry, I'm having trouble connecting to the server. Please check if the backend is running." }
            ]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex items-center justify-center min-h-[90vh] px-4 py-8">
            <Card className="w-full max-w-2xl h-[700px] flex flex-col shadow-2xl border-2 border-slate-200">
                <CardHeader className="bg-slate-900 text-white rounded-t-lg">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-slate-700 rounded-full flex items-center justify-center">
                            <Bot size={24} className="text-blue-400" />
                        </div>
                        <div>
                            <CardTitle className="text-xl">HVAC Specialist</CardTitle>
                            <p className="text-xs text-slate-400 flex items-center gap-1">
                                <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                                Online - Ready to help
                            </p>
                        </div>
                    </div>
                </CardHeader>

                <CardContent className="flex-1 overflow-hidden p-0 bg-slate-50">
                    <ScrollArea className="h-full p-6">
                        <div className="space-y-6">
                            {messages.map((msg, i) => (
                                <div
                                    key={i}
                                    className={cn(
                                        "flex w-full items-start gap-3",
                                        msg.role === 'user' ? "flex-row-reverse" : "flex-row"
                                    )}
                                >
                                    <div className={cn(
                                        "w-8 h-8 rounded-full flex items-center justify-center shrink-0 mt-1",
                                        msg.role === 'user' ? "bg-slate-200" : "bg-blue-100"
                                    )}>
                                        {msg.role === 'user' ? <User size={16} className="text-slate-600" /> : <Bot size={16} className="text-blue-600" />}
                                    </div>
                                    <div className={cn(
                                        "max-w-[80%] rounded-2xl p-4 text-sm shadow-sm",
                                        msg.role === 'user'
                                            ? "bg-slate-900 font-medium text-white rounded-tr-none"
                                            : "bg-white text-slate-800 rounded-tl-none border border-slate-200"
                                    )}>
                                        {msg.content}
                                    </div>
                                </div>
                            ))}
                            {isLoading && (
                                <div className="flex w-full items-start gap-3">
                                    <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center shrink-0 mt-1">
                                        <Bot size={16} className="text-blue-600" />
                                    </div>
                                    <div className="bg-white text-slate-800 max-w-[80%] rounded-2xl p-4 text-sm shadow-sm border border-slate-200 rounded-tl-none">
                                        <Loader2 size={16} className="animate-spin text-slate-400" />
                                    </div>
                                </div>
                            )}
                            {isQualified && (
                                <div className="p-4 bg-green-50 border border-green-200 rounded-xl text-green-800 text-center font-medium animate-in fade-in slide-in-from-bottom-2 duration-500">
                                    ✅ Your session is complete. Our team will contact you shortly!
                                </div>
                            )}
                            <div ref={scrollRef} />
                        </div>
                    </ScrollArea>
                </CardContent>

                <CardFooter className="p-4 bg-white border-t rounded-b-lg">
                    <div className="flex w-full gap-2 items-center">
                        <Input
                            placeholder={isQualified ? "Session complete" : "Describe your HVAC issue..."}
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                            disabled={isLoading || isQualified}
                            className="flex-1 py-6 border-slate-200 focus:ring-slate-400"
                        />
                        <Button
                            onClick={sendMessage}
                            disabled={isLoading || isQualified || !input.trim()}
                            className="bg-slate-900 hover:bg-slate-800 text-white rounded-xl p-6"
                        >
                            <Send size={20} />
                        </Button>
                    </div>
                </CardFooter>
            </Card>
        </div>
    );
};
