import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

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
        <div className="flex items-center justify-center min-h-[80vh] px-4">
            <Card className="w-full max-w-md border-2 border-slate-200 shadow-xl">
                <CardHeader className="space-y-1 bg-slate-50 border-b">
                    <CardTitle className="text-2xl font-bold text-slate-900">HVAC Connect</CardTitle>
                    <CardDescription className="text-slate-600">
                        Expert heating & cooling solutions. Tell us a bit about yourself to get started.
                    </CardDescription>
                </CardHeader>
                <form onSubmit={handleSubmit}>
                    <CardContent className="space-y-4 pt-6">
                        <div className="space-y-2">
                            <label className="text-sm font-medium text-slate-700">Full Name</label>
                            <Input
                                placeholder="John Doe"
                                value={formData.name}
                                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                required
                                className="border-slate-300 focus:ring-slate-400"
                            />
                        </div>
                        <div className="space-y-2">
                            <label className="text-sm font-medium text-slate-700">Email Address</label>
                            <Input
                                type="email"
                                placeholder="john@example.com"
                                value={formData.email}
                                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                                required
                                className="border-slate-300 focus:ring-slate-400"
                            />
                        </div>
                        <div className="space-y-2">
                            <label className="text-sm font-medium text-slate-700">Phone Number</label>
                            <Input
                                type="tel"
                                placeholder="(555) 000-0000"
                                value={formData.phone}
                                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                                required
                                className="border-slate-300 focus:ring-slate-400"
                            />
                        </div>
                    </CardContent>
                    <CardFooter className="bg-slate-50 border-t pt-6">
                        <Button type="submit" className="w-full bg-slate-900 hover:bg-slate-800 text-white py-6 text-lg font-semibold">
                            Start Chat
                        </Button>
                    </CardFooter>
                </form>
            </Card>
        </div>
    );
};
