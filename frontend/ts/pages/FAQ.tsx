import React from 'react';
import { Head } from '@inertiajs/react';
import Layout from '@/components/layout/Layout';

export default function FAQ() {
    return (
        <Layout>
            <Head title="Let's Check - FAQ" />
            <div className="text-center">
                <h1 className="text-4xl font-bold">Questions Fréquemment Posées (FAQ)</h1>
                <p className="mt-4 text-lg">Trouvez ici les réponses à vos questions.</p>
            </div>
        </Layout>
    );
}
