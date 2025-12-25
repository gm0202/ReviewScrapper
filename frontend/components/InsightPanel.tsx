import { Sparkles } from 'lucide-react';

interface InsightPanelProps {
    text: string;
}

export default function InsightPanel({ text }: InsightPanelProps) {
    if (!text) return null;

    // Formatting bullet points if simpler string comes back
    const formattedText = text.split('\n').map((line, i) => (
        <p key={i} className="mb-2 text-slate-700 leading-relaxed text-sm">
            {line.replace(/^- /, '• ')}
        </p>
    ));

    return (
        <div className="bg-gradient-to-br from-indigo-50 to-white p-6 rounded-xl border border-indigo-100 shadow-sm">
            <div className="flex items-center gap-2 mb-4">
                <Sparkles className="w-5 h-5 text-indigo-600" />
                <h3 className="font-bold text-indigo-900">AI Trends & Insights</h3>
            </div>
            <div className="prose prose-sm max-w-none text-slate-600">
                {formattedText}
            </div>
        </div>
    );
}
