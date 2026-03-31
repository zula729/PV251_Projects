import type { CardType } from "./CardType";

export type FilterPanelProps = {
    selected: string[];
    onToggle: (category: string) => void;
    onClear: () => void;
    cards: CardType[];
    techMode: "OR" | "AND";
    onTechModeChange: (mode: "OR" | "AND") => void;
}