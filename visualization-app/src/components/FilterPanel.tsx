import { useMemo, useState } from "react";
import FilterGroup from "./FilterGroup";
import { TAGS, TECHNOLOGY, SEMESTR } from "../types/filterOptions";
import type { FilterPanelProps } from "../types/FilterPanel";
import { Trash2 } from "lucide-react";

function FilterPanel({ selected, onToggle, onClear, cards = [] }: FilterPanelProps) {
    const [isOpen, setIsOpen] = useState(false);
    const technologyFrequency = useMemo(() => {
        const freq: Record<string, number> = {};
        cards.forEach(card => {
            card.technology?.forEach(tech => {
                const match = TECHNOLOGY.find(t => t.toLowerCase() === tech.trim().toLowerCase());
                if (match) {
                    freq[match] = (freq[match] ?? 0) + 1;
                }
            });
        });
    return freq;
    }, [cards]);

const sortedTechnology = useMemo(() => {
    const sorted = [...TECHNOLOGY].sort((a, b) => {
        const freqA = technologyFrequency[a] ?? 0;
        const freqB = technologyFrequency[b] ?? 0;
        if (freqA === 0 && freqB !== 0) return 1;
        if (freqB === 0 && freqA !== 0) return -1;
        return freqB - freqA;
    });
    return sorted;
}, [technologyFrequency]);

    return (
        <div>
            <button onClick={() => setIsOpen(prev => !prev)}
                className="text-gray-600 hover:text-gray-900 mt-2 font-semibold">
                {isOpen ? "▲" : "▼"} Filters {selected.length > 0 && `(${selected.length})`}
            </button>

            <div className={`overflow-hidden transition-all duration-400 ease-in-out
                ${isOpen ? "max-h-screen opacity-100" : "max-h-0 opacity-0"}`}>
                <div className="pt-4 font-semibold"> Categories
                    <FilterGroup items={TAGS} selected={selected} onToggle={onToggle} />
                </div>
                <div className="pt-4 font-semibold"> Technology
                    <FilterGroup items={sortedTechnology} selected={selected} onToggle={onToggle} sorted={false} />
                </div>
                <div className="pt-4 font-semibold"> Semester
                    <FilterGroup items={SEMESTR} selected={selected} onToggle={onToggle} />
                </div>
                {selected.length > 0 && (
                    <button onClick={onClear} className="text-xs text-red-400 hover:text-red-600 mt-2">
                        <Trash2 size={16} />
                    </button>
                )}
            </div>
        </div>
    )
}

export default FilterPanel;
