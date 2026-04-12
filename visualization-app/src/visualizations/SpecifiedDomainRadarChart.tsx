import { Radar, RadarChart, PolarGrid, Legend, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from 'recharts';
import { TAGS } from "../types/filterOptions";
import { useMemo } from 'react';
import { useCards } from "../hooks/useCards";

function SpecifiedDomainRadarChart() {
    const cards = useCards();
    const data = useMemo(() => {
      const freq: Record<string, number> = {};
      cards.forEach(card => {
        card.tags?.forEach(tech => {
          const match = TAGS.find(t => t.toLowerCase() === tech.trim().toLowerCase());
          if (match) {
            freq[match] = (freq[match] ?? 0) + 1;
          }
        });
      });
      return Object.entries(freq).map(([topic, count]) => ({ topic, count }));
    }, [cards]);

  return (
    <ResponsiveContainer width="60%" aspect={1}>
      <RadarChart outerRadius="80%" data={data}>
        <PolarGrid />
        <PolarAngleAxis dataKey="topic" /> 
        <PolarRadiusAxis />
        <Radar name="" dataKey="count" stroke="#6366f1" fill="#6366f1" fillOpacity={0.6} />
        <Legend />
      </RadarChart>
    </ResponsiveContainer>
  );
}

export default SpecifiedDomainRadarChart;