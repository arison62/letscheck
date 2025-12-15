import React, { useEffect, useRef } from 'react';
import { Html5QrcodeScanner } from 'html5-qrcode';
import { Card } from '@/components/ui/card';

interface QRScannerProps {
    onScan: (scannedText: string) => void;
}

const QRScanner: React.FC<QRScannerProps> = ({ onScan }) => {
    const scannerRef = useRef<Html5QrcodeScanner | null>(null);

    useEffect(() => {
        const scanner = new Html5QrcodeScanner(
            'qr-reader',
            {
                fps: 10,
                qrbox: { width: 250, height: 250 },
            },
            /* verbose= */ false
        );

        scannerRef.current = scanner;

        const onScanSuccess = (decodedText: string) => {
            onScan(decodedText);
            scanner.clear();
        };

        const onScanFailure = (error: any) => {
            // handle scan failure, usually better to ignore and keep scanning.
        };

        scanner.render(onScanSuccess, onScanFailure);

        return () => {
            if (scannerRef.current) {
                scannerRef.current.clear();
            }
        };
    }, [onScan]);

    return (
        <Card className="p-8 flex justify-center items-center">
            <div id="qr-reader" style={{ width: '100%', maxWidth: '500px' }}></div>
        </Card>
    );
};

export default QRScanner;
