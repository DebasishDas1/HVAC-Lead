import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { User, Mail, Phone, ArrowRight, CheckCircle2 } from 'lucide-react';

interface LeadFormProps {
    onSubmit: (data: { name: string; email: string; phone: string }) => void;
}

export const LeadForm: React.FC<LeadFormProps> = ({ onSubmit }) => {
    const [formData, setFormData] = useState({ name: '', email: '', phone: '' });

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (formData.name && formData.email && formData.phone) {
            onSubmit(formData);
        }
    };

    return (
        <div className="flex animate-in fade-in slide-in-from-bottom-4 duration-700 items-center justify-center min-h-[60vh] px-4">
            <Card className="w-full max-w-md overflow-hidden border-none shadow-2xl ring-1 ring-primary/5">
                <CardHeader className="space-y-1 bg-gradient-to-br from-primary/5 to-transparent pb-8">
                    <div className="mb-2 flex h-12 w-12 items-center justify-center rounded-full bg-primary/10 text-primary">
                        <CheckCircle2 className="h-6 w-6" />
                    </div>
                    <CardTitle className="text-2xl font-bold">HVAC Connect</CardTitle>
                    <CardDescription className="text-base">
                        Get expert assistance with your heating & cooling needs.
                    </CardDescription>
                </CardHeader>
                <form onSubmit={handleSubmit}>
                    <CardContent className="space-y-5 pt-0">
                        <div className="space-y-2">
                            <Label htmlFor="name" className="text-sm font-semibold">Full Name</Label>
                            <div className="relative">
                                <User className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                                <Input
                                    id="name"
                                    placeholder="Enter your name"
                                    value={formData.name}
                                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                    required
                                    className="pl-10 h-11 transition-all focus-visible:ring-primary"
                                />
                            </div>
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="email" className="text-sm font-semibold">Email Address</Label>
                            <div className="relative">
                                <Mail className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                                <Input
                                    id="email"
                                    type="email"
                                    placeholder="name@example.com"
                                    value={formData.email}
                                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                                    required
                                    className="pl-10 h-11 transition-all focus-visible:ring-primary"
                                />
                            </div>
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="phone" className="text-sm font-semibold">Phone Number</Label>
                            <div className="relative">
                                <Phone className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                                <Input
                                    id="phone"
                                    type="tel"
                                    placeholder="(555) 000-0000"
                                    value={formData.phone}
                                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                                    required
                                    className="pl-10 h-11 transition-all focus-visible:ring-primary"
                                />
                            </div>
                        </div>
                    </CardContent>
                    <CardFooter className="pb-8">
                        <Button type="submit" className="w-full h-12 text-base font-bold shadow-lg shadow-primary/20 hover:scale-[1.02] transition-all">
                            Connect with an Expert <ArrowRight className="ml-2 h-4 w-4" />
                        </Button>
                    </CardFooter>
                </form>
            </Card>
        </div>
    );
};
