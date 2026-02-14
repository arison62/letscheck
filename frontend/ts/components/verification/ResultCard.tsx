import React from 'react';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { AlertCircle, CheckCircle, XCircle, ShieldOff } from 'lucide-react';
import ReportModal from '@/components/reports/ReportModal';
import { cn } from '@/lib/utils';

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

interface ResultCardProps {
    result: VerificationResult;
    className?: string;
}

const resultConfig = {
    AUTHENTIC: {
        title: "Document Authentique",
        icon: <CheckCircle className="w-12 h-12 text-green-500" />,
        color: "border-green-500",
        badge: "AUTHENTIQUE",
    },
    INVALID_SIGNATURE: {
        title: "Signature Invalide",
        icon: <XCircle className="w-12 h-12 text-red-500" />,
        color: "border-red-500",
        badge: "INVALIDE",
    },
    NOT_FOUND: {
        title: "Document Non Trouvé",
        icon: <AlertCircle className="w-12 h-12 text-yellow-500" />,
        color: "border-yellow-500",
        badge: "NON TROUVÉ",
    },
    REVOKED: {
        title: "Document Révoqué",
        icon: <ShieldOff className="w-12 h-12 text-gray-700" />,
        color: "border-gray-700",
        badge: "RÉVOQUÉ",
    },
};

export default function ResultCard({ result, className }: ResultCardProps) {
    const config = resultConfig[result.result] || resultConfig.INVALID_SIGNATURE;

    return (
        <Card className={cn("text-center", config.color, className)}>
            <CardHeader>
                <div className="flex justify-center mb-4">{config.icon}</div>
                <CardTitle>{config.title}</CardTitle>
            </CardHeader>
            <CardContent>
                {result.document && (
                    <div className="text-left space-y-2">
                        <p><strong>Institution:</strong> {result.document.institution.name}</p>
                        <p><strong>Date de signature:</strong> {new Date(result.document.signed_at).toLocaleString()}</p>
                    </div>
                )}
            </CardContent>
            <CardFooter className="flex flex-col gap-4">
                {result.result === 'AUTHENTIC' && result.certificate_url && (
                    <a href={result.certificate_url} download className="text-blue-500 hover:underline">
                        Télécharger le certificat
                    </a>
                )}
                <ReportModal documentHash={result.document_hash} />
            </CardFooter>
        </Card>
    );
}
