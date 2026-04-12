import tagsYaml from '../../backend/tags.yaml';
import techYaml from '../../backend/tech_terms.yaml';

export const TAGS = Object.keys(tagsYaml) as string[];

export const TECHNOLOGY = Object.keys(techYaml) as string[];

export const SEMESTR = [
    "podzim2024", 
    "podzim2025"
]