type FilterGroupProps = {
    items: string[];
    selected: string[];
    onToggle: (item: string) => void;
}

function FilterGroup({ items, selected, onToggle }: FilterGroupProps) {
    return (
        <div className="flex flex-wrap gap-2 mt-3 items-center">
            {items.map(item => (
                <button
                    key={item}
                    onClick={() => onToggle(item)}
                    className={`rounded-xl p-0.5 pl-2 pr-2 font-medium transition-colors cursor-pointer
                        ${selected.includes(item)
                            ? "bg-amber-200 text-black"
                            : "bg-gray-200 text-black hover:bg-gray-300"
                        }`}
                >
                    {item}
                </button>
            ))}
        </div>
    );
}

export default FilterGroup;