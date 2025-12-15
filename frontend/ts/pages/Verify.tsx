import React, { useState } from 'react';
import { Head } from '@inertiajs/react';
import Layout from '@/components/layout/Layout';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import axios from 'axios';
import UploadZone from '@/components/verification/UploadZone';
import QRScanner from '@/components/verification/QRScanner';
import HashInput from '@/components/verification/HashInput';
import ResultCard from '@/components/verification/ResultCard';
import VerificationHistory from '@/components/verification/VerificationHistory';

interface VerificationHistoryItem {
    hash: string;
    result: string;
    date: string;
}

// This is a placeholder for the actual result schema from the backend
interface VerificationResult {
    result: 'AUTHENTIC' | 'INVALID_SIGNATURE' | 'NOT_FOUND' | 'REVOKED';
    document_hash: string;
    document?: {
        institution: {
            name: string;
            logo_url?: string;
        };
        signed_at: string;
    };
    certificate_url?: string;
}


export default function Verify() {
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<VerificationResult | null>(null);

    const handleHashSubmit = async (hash: string, method: string) => {
        setLoading(true);
        setResult(null);
        try {
            const response = await axios.post('/api/v1/verifications/verify/hash', {
                document_hash: hash,
                method: method
            });
            const newResult = { ...response.data, document_hash: hash };
            setResult(newResult);

            // Save to history
            const storedHistory = localStorage.getItem('verificationHistory') || '[]';
            const history: VerificationHistoryItem[] = JSON.parse(storedHistory);
            history.unshift({ hash, result: newResult.result, date: new Date().toISOString() });
            localStorage.setItem('verificationHistory', JSON.stringify(history.slice(0, 10))); // Keep last 10
        } catch (error) {
            console.error('Verification failed:', error);
            // Handle error, maybe show a toast
        } finally {
            setLoading(false);
        }
    };

    return (
        <Layout>
            <Head title="Let's Check - Vérifier un Document" />

            <div className="container mx-auto px-4 py-8 max-w-4xl">
                <h1 className="text-3xl font-bold text-center mb-8">
                    Vérifier l'Authenticité d'un Document
                </h1>

                <Tabs defaultValue="upload" className="w-full">
                    <TabsList className="grid w-full grid-cols-3">
                        <TabsTrigger value="upload">Upload Fichier</TabsTrigger>
                        <TabsTrigger value="qr">Scanner QR</TabsTrigger>
                        <TabsTrigger value="hash">Entrer Hash</TabsTrigger>
                    </TabsList>

                    <TabsContent value="upload">
                        <UploadZone onHashCalculated={(hash) => handleHashSubmit(hash, 'UPLOAD')} loading={loading} />
                    </TabsContent>

                    <TabsContent value="qr">
                        <QRScanner onScan={(hash) => handleHashSubmit(hash, 'QR_SCAN')} />
                    </TabsContent>

                    <TabsContent value="hash">
                        <HashInput onSubmit={(hash) => handleHashSubmit(hash, 'HASH_INPUT')} loading={loading} />
                    </TabsContent>
                </Tabs>

                {result && (
                    <div className="mt-8">
                        <ResultCard result={result} />
                    </div>
                )}

                <VerificationHistory />
            </div>
        </Layout>
    );
}
