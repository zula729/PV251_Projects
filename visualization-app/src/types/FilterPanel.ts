export type FilterPanelProps = {
    selected: string[];
    onToggle: (category: string) => void;
    onClear: () => void;
}