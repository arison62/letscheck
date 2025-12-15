import React from 'react';
import { Head } from '@inertiajs/react';
import Layout from '@/components/layout/Layout';
import { Button } from '@/components/ui/button';

export default function Home() {
    return (
        <Layout>
            <Head title="Let's Check - Accueil" />
            <div className="text-center">
                <h1 className="text-4xl font-bold">Bienvenue sur Let's Check</h1>
                <p className="mt-4 text-lg">La solution pour vérifier l'authenticité de vos documents.</p>
                <Button className="mt-6">Commencer</Button>
            </div>
        </Layout>
    );
}
