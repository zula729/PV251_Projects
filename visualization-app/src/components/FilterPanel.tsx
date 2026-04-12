import { useMemo, useState } from "react";
import FilterGroup from "./FilterGroup";
import { TAGS, TECHNOLOGY, SEMESTR } from "../types/filterOptions";
import type { FilterPanelProps } from "../types/FilterPanel";
import { Trash } from "lucide-react";

function FilterPanel({ selected, onToggle, onClear, cards = [], techMode, onTechModeChange }: FilterPanelProps) {
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
            <div className="flex items-center gap-2">
                <button onClick={() => setIsOpen(prev => !prev)}
                    className="text-gray-500 hover:text-gray-700 mt-2 font-semibold">
                    {isOpen ? "▲" : "▼"} Filters {selected.length > 0 && `(${selected.length})`}
                </button>
                {selected.length > 0 && (
                        <button onClick={onClear} className="text-xs text-red-400 hover:text-red-600 mt-2.5">
                            <Trash size={16} />
                        </button>
                    )}  
            </div>

            <div className={`overflow-hidden transition-all duration-400 ease-in-out
                ${isOpen ? "max-h-screen opacity-100" : "max-h-0 opacity-0"}`}>
                <div className="pt-4 font-semibold"> Categories
                    <FilterGroup items={TAGS} selected={selected} onToggle={onToggle} type={"tag"}/>
                </div>
                <div className="pt-4 font-semibold flex items-center gap-3 ">
                    Technology
                    <div className="flex text-xs font-medium bg-gray-100 rounded-full p-0.5 gap-0.5 ">
                        <button
                            onClick={() => onTechModeChange("OR")}
                            className={`px-3 py-0.5 rounded-full transition-all duration-200 ${
                                techMode === "OR"
                                    ? "bg-white text-gray-800 shadow-sm"
                                    : "text-gray-400 hover:text-gray-600 cursor-pointer"
                            }`}
                        >
                            OR
                        </button>
                        <button
                            onClick={() => onTechModeChange("AND")}
                            className={`px-3 py-0.5 rounded-full transition-all duration-200 ${
                                techMode === "AND"
                                    ? "bg-white text-gray-800 shadow-sm"
                                    : "text-gray-400 hover:text-gray-600 cursor-pointer"
                            }`}
                        >
                            AND
                        </button>
                    </div>
                </div>
                <FilterGroup items={sortedTechnology} selected={selected} onToggle={onToggle} sorted={false} type={"technology"} />
                <div className="pt-4 font-semibold"> Semester
                    <FilterGroup items={SEMESTR} selected={selected} onToggle={onToggle} type={"semestr"} />
                </div>
                
            </div>
        </div>
    )
}

export default FilterPanel;
