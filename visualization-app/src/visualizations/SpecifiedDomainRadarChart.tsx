import {
    Radar,
    RadarChart,
    PolarGrid,
    Legend,
    PolarAngleAxis,
    PolarRadiusAxis,
    ResponsiveContainer
} from 'recharts';
import { TAGS, SEMESTR } from '../types/filterOptions';
import { useMemo, useState } from 'react';
import { useCards } from '../hooks/useCards';
function SpecifiedDomainRadarChart() {
    const cards = useCards();
    const [selectedTags, setSelectedTags] = useState<string[]>(TAGS);
    const [selectedSemesters, setSelectedSemesters] = useState<string[]>(SEMESTR);

    const data = useMemo(() => {
        const freq: Record<string, Record<string, number>> = {};
        cards.forEach((card) => {
            card.tags?.forEach((tag) => {
                const matchTag = TAGS.find((t) => t.toLowerCase() === tag.trim().toLowerCase());
                const semester = card.semestr ?? 'unknown';
                if (
                    matchTag &&
                    selectedTags.includes(matchTag) &&
                    selectedSemesters.includes(semester)
                ) {
                    if (!freq[matchTag]) freq[matchTag] = {};
                    freq[matchTag][semester] = (freq[matchTag][semester] ?? 0) + 1;
                }
            });
        });

        return Object.entries(freq)
            .map(([tag, semesters]) => ({ tag, ...semesters }))
            .sort((a, b) => a.tag.localeCompare(b.tag));
    }, [cards, selectedTags, selectedSemesters]);

    return (
        <ResponsiveContainer width="60%" height={600}>
            <RadarChart outerRadius="80%" data={data}>
                <PolarGrid />
                <PolarAngleAxis dataKey="tag" />
                <PolarRadiusAxis angle={30} domain={[0, 9]} />
                {SEMESTR.map((semester, i) => (
                    <Radar
                        key={semester}
                        name={semester}
                        dataKey={semester}
                        stroke={i === 0 ? '#6366f1' : '#10b981'}
                        fill={i === 0 ? '#6366f1' : '#10b981'}
                        fillOpacity={0.6}
                    />
                ))}
                <Legend />
            </RadarChart>
        </ResponsiveContainer>
    );
}
export default SpecifiedDomainRadarChart;
