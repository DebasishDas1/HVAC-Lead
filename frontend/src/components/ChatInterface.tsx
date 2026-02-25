import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Send, User, Bot, Loader2, Sparkles, AlertCircle } from 'lucide-react';
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
    const [error, setError] = useState<string | null>(null);
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
    }, [messages, isLoading]);

    const sendMessage = async () => {
        if (!input.trim() || isLoading || isQualified) return;

        const userMessage = input.trim();
        setInput('');
        setError(null);
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
            setError("Connection issue. Please ensure the backend server is running.");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex animate-in fade-in duration-1000 items-center justify-center min-h-[80vh] px-4 py-4">
            <Card className="w-full max-w-3xl h-[750px] flex flex-col shadow-2xl border-none ring-1 ring-primary/5 overflow-hidden">
                <CardHeader className="border-b bg-background/50 backdrop-blur-sm py-4">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <Avatar className="h-10 w-10 border-2 border-primary/10 shadow-sm">
                                <AvatarFallback className="bg-primary text-primary-foreground">
                                    <Bot size={20} />
                                </AvatarFallback>
                            </Avatar>
                            <div>
                                <CardTitle className="text-lg font-bold">HVAC Assistant</CardTitle>
                                <div className="flex items-center gap-1.5">
                                    <span className="relative flex h-2 w-2">
                                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                                        <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
                                    </span>
                                    <span className="text-xs font-medium text-muted-foreground">Expert Support Online</span>
                                </div>
                            </div>
                        </div>
                        {isQualified && (
                            <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200 gap-1 px-3 py-1">
                                <Sparkles size={12} /> Qualified
                            </Badge>
                        )}
                    </div>
                </CardHeader>

                <CardContent className="flex-1 overflow-hidden p-0 bg-gradient-to-b from-transparent to-primary/[0.02]">
                    <ScrollArea className="h-full px-6 py-8">
                        <div className="space-y-8 pb-4">
                            {messages.map((msg, i) => (
                                <div
                                    key={i}
                                    className={cn(
                                        "flex w-full items-start gap-3 animate-in slide-in-from-bottom-2 duration-300",
                                        msg.role === 'user' ? "flex-row-reverse" : "flex-row"
                                    )}
                                >
                                    <Avatar className={cn(
                                        "h-8 w-8 mt-1 border shadow-sm",
                                        msg.role === 'user' ? "bg-white" : "bg-primary"
                                    )}>
                                        {msg.role === 'user' ? (
                                            <AvatarFallback className="bg-white text-muted-foreground"><User size={14} /></AvatarFallback>
                                        ) : (
                                            <AvatarFallback className="bg-primary text-primary-foreground"><Bot size={14} /></AvatarFallback>
                                        )}
                                    </Avatar>
                                    <div className={cn(
                                        "relative group max-w-[85%] rounded-2xl p-4 text-sm transition-all duration-200",
                                        msg.role === 'user'
                                            ? "bg-primary text-primary-foreground shadow-md rounded-tr-none"
                                            : "bg-white text-foreground shadow-sm border border-border/50 rounded-tl-none hover:border-primary/20"
                                    )}>
                                        <p className="leading-relaxed">{msg.content}</p>
                                    </div>
                                </div>
                            ))}

                            {isLoading && (
                                <div className="flex w-full items-start gap-3 animate-pulse">
                                    <Avatar className="h-8 w-8 mt-1 border bg-primary shadow-sm">
                                        <AvatarFallback className="bg-primary text-primary-foreground"><Bot size={14} /></AvatarFallback>
                                    </Avatar>
                                    <div className="bg-white text-foreground max-w-[85%] rounded-2xl p-4 text-sm shadow-sm border border-border/50 rounded-tl-none flex items-center gap-2">
                                        <Loader2 size={14} className="animate-spin text-primary" />
                                        <span className="text-muted-foreground italic">Thinking...</span>
                                    </div>
                                </div>
                            )}

                            {error && (
                                <div className="flex justify-center animate-in zoom-in-95 duration-300">
                                    <div className="bg-destructive/10 text-destructive text-xs py-2 px-4 rounded-full border border-destructive/20 flex items-center gap-2">
                                        <AlertCircle size={14} />
                                        {error}
                                    </div>
                                </div>
                            )}

                            {isQualified && (
                                <div className="space-y-4 px-4 py-6 bg-green-50/50 border border-green-100 rounded-3xl text-center animate-in zoom-in-95 duration-500">
                                    <div className="inline-flex h-12 w-12 items-center justify-center rounded-full bg-green-100 text-green-600 mb-2">
                                        <Sparkles className="h-6 w-6" />
                                    </div>
                                    <h3 className="text-lg font-bold text-green-900">Great News!</h3>
                                    <p className="text-sm text-green-700 max-w-sm mx-auto">
                                        Your session is complete and you've been qualified. A team member will reach out to you within the next hour.
                                    </p>
                                </div>
                            )}
                            <div ref={scrollRef} />
                        </div>
                    </ScrollArea>
                </CardContent>

                <CardFooter className="p-4 bg-background border-t">
                    <div className="flex w-full gap-2 items-center bg-muted/50 p-1.5 rounded-2xl ring-1 ring-border/50 focus-within:ring-primary/30 transition-all duration-300">
                        <Input
                            placeholder={isQualified ? "Session complete" : "Describe your heating or cooling issue..."}
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                            disabled={isLoading || isQualified}
                            className="flex-1 border-none bg-transparent shadow-none focus-visible:ring-0 placeholder:text-muted-foreground/70"
                        />
                        <Button
                            onClick={sendMessage}
                            disabled={isLoading || isQualified || !input.trim()}
                            size="icon"
                            className={cn(
                                "h-11 w-11 rounded-xl shadow-lg transition-all duration-300",
                                !input.trim() ? "opacity-50 grayscale" : "bg-primary hover:scale-105"
                            )}
                        >
                            <Send size={18} />
                        </Button>
                    </div>
                </CardFooter>
            </Card>
        </div>
    );
};
