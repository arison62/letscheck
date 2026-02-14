import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

interface VerificationHistoryItem {
    hash: string;
    result: string;
    date: string;
}

const STORAGE_KEY = 'verificationHistory';

export default function VerificationHistory() {
    const [history, setHistory] = useState<VerificationHistoryItem[]>([]);

    useEffect(() => {
        const storedHistory = localStorage.getItem(STORAGE_KEY);
        if (storedHistory) {
            setHistory(JSON.parse(storedHistory));
        }
    }, []);

    const clearHistory = () => {
        localStorage.removeItem(STORAGE_KEY);
        setHistory([]);
    };

    if (history.length === 0) {
        return null;
    }

    return (
        <Card className="mt-8">
            <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle>Historique de Vérification</CardTitle>
                <Button variant="outline" size="sm" onClick={clearHistory}>
                    Effacer l'historique
                </Button>
            </CardHeader>
            <CardContent>
                <ul className="space-y-2">
                    {history.map((item, index) => (
                        <li key={index} className="flex justify-between items-center p-2 rounded bg-gray-50">
                            <span className="font-mono text-sm truncate" title={item.hash}>{item.hash}</span>
                            <span className="text-sm">{item.result}</span>
                            <span className="text-xs text-gray-500">{new Date(item.date).toLocaleString()}</span>
                        </li>
                    ))}
                </ul>
            </CardContent>
        </Card>
    );
}
