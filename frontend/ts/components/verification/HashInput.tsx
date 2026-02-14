import React, { useState } from 'react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { LoaderCircle } from 'lucide-react';

interface HashInputProps {
    onSubmit: (hash: string) => void;
    loading?: boolean;
}

export default function HashInput({ onSubmit, loading }: HashInputProps) {
    const [hash, setHash] = useState('');

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (hash.trim()) {
            onSubmit(hash.trim());
        }
    };

    return (
        <Card className="p-8">
            <form onSubmit={handleSubmit} className="flex flex-col gap-4">
                <Input
                    type="text"
                    placeholder="Entrez le hash SHA-256 du document"
                    value={hash}
                    onChange={(e) => setHash(e.target.value)}
                    disabled={loading}
                    className="w-full"
                />
                <Button type="submit" disabled={loading || !hash.trim()} className="w-full">
                    {loading ? <LoaderCircle className="animate-spin" /> : 'Vérifier le Hash'}
                </Button>
            </form>
        </Card>
    );
}
