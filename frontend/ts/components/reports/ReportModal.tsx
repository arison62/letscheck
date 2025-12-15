import React, { useState } from 'react';
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
    DialogFooter,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import axios from 'axios';

interface ReportModalProps {
    documentHash: string;
}

export default function ReportModal({ documentHash }: ReportModalProps) {
    const [open, setOpen] = useState(false);
    const [reportType, setReportType] = useState('');
    const [reason, setReason] = useState('');
    const [reporterEmail, setReporterEmail] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async () => {
        setLoading(true);
        try {
            await axios.post('/api/v1/verifications/reports', {
                document_hash: documentHash,
                report_type: reportType,
                reason: reason,
                reporter_email: reporterEmail,
            });
            setOpen(false);
            // Optionally, show a success toast here
        } catch (error) {
            console.error('Failed to submit report:', error);
            // Optionally, show an error toast here
        } finally {
            setLoading(false);
        }
    };

    return (
        <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
                <Button variant="outline">Signaler un problème</Button>
            </DialogTrigger>
            <DialogContent>
                <DialogHeader>
                    <DialogTitle>Signaler un document suspect</DialogTitle>
                </DialogHeader>
                <div className="grid gap-4 py-4">
                    <Select onValueChange={setReportType} required>
                        <SelectTrigger>
                            <SelectValue placeholder="Type de signalement" />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="FAKE">Document Falsifié</SelectItem>
                            <SelectItem value="ALTERED">Document Altéré</SelectItem>
                            <SelectItem value="UNAUTHORIZED">Signature Non Autorisée</SelectItem>
                            <SelectItem value="OTHER">Autre</SelectItem>
                        </SelectContent>
                    </Select>
                    <Textarea
                        placeholder="Veuillez décrire le problème..."
                        value={reason}
                        onChange={(e) => setReason(e.target.value)}
                        required
                    />
                    <Input
                        type="email"
                        placeholder="Votre email (optionnel)"
                        value={reporterEmail}
                        onChange={(e) => setReporterEmail(e.target.value)}
                    />
                </div>
                <DialogFooter>
                    <Button onClick={handleSubmit} disabled={loading || !reportType || !reason}>
                        {loading ? 'Envoi...' : 'Envoyer le signalement'}
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
}
