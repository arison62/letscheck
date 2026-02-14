import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, LoaderCircle } from 'lucide-react';
import { Card } from '@/components/ui/card';

interface UploadZoneProps {
    onHashCalculated: (hash: string) => void;
    loading?: boolean;
}

// Utilitaire calcul hash
async function calculateHash(file: File): Promise<string> {
    const buffer = await file.arrayBuffer();
    const hashBuffer = await crypto.subtle.digest('SHA-256', buffer);
    return Array.from(new Uint8Array(hashBuffer))
        .map(b => b.toString(16).padStart(2, '0'))
        .join('');
}

export default function UploadZone({ onHashCalculated, loading }: UploadZoneProps) {
    const [isHashing, setIsHashing] = useState(false);

    const onDrop = useCallback(async (acceptedFiles: File[]) => {
        if (acceptedFiles.length > 0) {
            setIsHashing(true);
            try {
                const hash = await calculateHash(acceptedFiles[0]);
                onHashCalculated(hash);
            } catch (error) {
                console.error("Error calculating file hash:", error);
                // Handle hashing error, maybe show a toast
            } finally {
                setIsHashing(false);
            }
        }
    }, [onHashCalculated]);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: {
            'application/pdf': ['.pdf'],
            'image/jpeg': ['.jpg', '.jpeg'],
            'image/png': ['.png'],
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
        },
        maxFiles: 1,
        maxSize: 10 * 1024 * 1024 // 10MB
    });

    const isProcessing = loading || isHashing;

    return (
        <Card className="p-8">
            <div
                {...getRootProps()}
                className={`
                    border-2 border-dashed rounded-lg p-12
                    text-center cursor-pointer transition-colors
                    ${isDragActive ? 'border-primary bg-primary/5' : 'border-gray-300'}
                    ${isProcessing ? 'opacity-50 pointer-events-none' : ''}
                `}
            >
                <input {...getInputProps()} />

                {isProcessing ? (
                    <>
                        <LoaderCircle className="w-16 h-16 mx-auto mb-4 text-primary animate-spin" />
                        <p className="text-lg font-medium mb-2">
                            {isHashing ? "Calcul du hash en cours..." : "Vérification en cours..."}
                        </p>
                        {/* Shadcn progress doesn't have an indeterminate state, so a spinner is better */}
                    </>
                ) : (
                    <>
                        <Upload className="w-16 h-16 mx-auto mb-4 text-gray-400" />
                        <p className="text-lg font-medium mb-2">
                            {isDragActive
                                ? 'Déposez votre document ici'
                                : 'Glissez votre document ici ou cliquez pour parcourir'}
                        </p>
                        <p className="text-sm text-gray-500">
                            Formats acceptés : PDF, JPG, PNG, DOCX (max 10MB)
                        </p>
                    </>
                )}
            </div>
        </Card>
    );
}
