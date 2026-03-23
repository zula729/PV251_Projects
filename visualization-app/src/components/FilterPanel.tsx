import { useState } from "react";
import FilterGroup from "./FilterGroup";
import { TAGS, TECHNOLOGY, SEMESTR } from "../types/filterOptions";
import type { FilterPanelProps } from "../types/FilterPanel";

function FilterPanel({ selected, onToggle, onClear }: FilterPanelProps) {
    const [isOpen, setIsOpen] = useState(false);
    return (
        <div>
            <button onClick={() => setIsOpen(prev => !prev)}
                className="text-sm text-gray-600 hover:text-gray-900 mt-2">
                {isOpen ? "↑" : "↓"} Filters {selected.length > 0 && `(${selected.length})`}
            </button>

            {isOpen && (
                <>
                    <FilterGroup items={TAGS} selected={selected} onToggle={onToggle} />
                    <FilterGroup items={TECHNOLOGY} selected={selected} onToggle={onToggle} />
                    <FilterGroup items={SEMESTR} selected={selected} onToggle={onToggle} />
                    {selected.length > 0 && (
                        <button onClick={onClear} className="text-xs text-red-400 hover:text-red-600 mt-2">
                            clear all
                        </button>
                    )}
                </>
            )}
        </div>
    )
}

export default FilterPanel;
