import { useState } from "react";
import FilterGroup from "./FilterGroup";
import { TAGS, TECHNOLOGY, SEMESTR } from "../types/filterOptions";
import type { FilterPanelProps } from "../types/FilterPanel";
import { Trash2 } from "lucide-react";

function FilterPanel({ selected, onToggle, onClear }: FilterPanelProps) {
    const [isOpen, setIsOpen] = useState(false);
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
                    <FilterGroup items={TECHNOLOGY} selected={selected} onToggle={onToggle} />
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
