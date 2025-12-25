"use client"

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface TrendChartProps {
    data: any[];
    topics: string[];
}

const COLORS = ['#8884d8', '#82ca9d', '#ffc658', '#ff7300', '#0088fe', '#00C49F'];

export default function TrendChart({ data, topics }: TrendChartProps) {
    // data format: [{ date: '2025-01-01', 'Topic A': 10, 'Topic B': 5 }, ...]

    return (
        <div className="h-[300px] w-full min-w-0 bg-white p-4 rounded-xl shadow-sm border border-slate-100">
            <h3 className="text-sm font-semibold text-slate-500 mb-4 uppercase tracking-wider">Topic Volume Trend</h3>
            <ResponsiveContainer width="100%" height="100%">
                <LineChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                    <XAxis dataKey="date" stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
                    <YAxis stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
                    <Tooltip
                        contentStyle={{ backgroundColor: '#fff', borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                        itemStyle={{ fontSize: '12px' }}
                    />
                    <Legend />
                    {topics.slice(0, 5).map((topic, index) => (
                        <Line
                            key={topic}
                            type="monotone"
                            dataKey={topic}
                            stroke={COLORS[index % COLORS.length]}
                            strokeWidth={3}
                            dot={{ r: 4, strokeWidth: 2 }}
                            activeDot={{ r: 6 }}
                        />
                    ))}
                </LineChart>
            </ResponsiveContainer>
        </div>
    );
}
