import Searchbar from '../components/Searchbar';
import Card from '../components/Card';
import FilterPanel from '../components/FilterPanel';
import { useState } from 'react';
import { useCards } from '../hooks/useCards';
import { TECHNOLOGY } from '../types/filterOptions';
import { Link } from 'react-router';

export function Gallery() {
    const cards = useCards();
    const [search, setSearch] = useState('');
    const [selectedCategories, setSelectedCategories] = useState<string[]>([]);
    const [techMode, setTechMode] = useState<'OR' | 'AND'>('OR');
    const toggleCategory = (cat: string) => {
        setSelectedCategories((prev) =>
            prev.includes(cat) ? prev.filter((c) => c !== cat) : [...prev, cat]
        );
    };
    const filtered = cards.filter((c) => {
        const matchesSearch =
            c.author?.toLowerCase().includes(search.toLowerCase()) ||
            c.keywords?.some((kw: string) => kw.toLowerCase().includes(search.toLowerCase())) ||
            c.technology?.some((tech: string) =>
                tech.toLowerCase().includes(search.toLowerCase())
            ) ||
            c.tags?.some((tag: string) => tag.toLowerCase().includes(search.toLowerCase())) ||
            c.name?.toLowerCase().includes(search.toLowerCase());

        const selectedTech = selectedCategories.filter((cat) => TECHNOLOGY.includes(cat));
        const selectedTags = selectedCategories.filter(
            (cat) => !TECHNOLOGY.includes(cat) && !cat.startsWith('podzim')
        );
        const selectedSemesters = selectedCategories.filter((cat) => cat.startsWith('podzim'));

        const matchesTech =
            selectedTech.length === 0 ||
            (techMode === 'OR'
                ? selectedTech.some((cat) =>
                      c.technology?.some((t) => t.trim().toLowerCase() === cat.toLowerCase())
                  )
                : selectedTech.every((cat) =>
                      c.technology?.some((t) => t.trim().toLowerCase() === cat.toLowerCase())
                  ));

        const matchesTags =
            selectedTags.length === 0 || selectedTags.some((cat) => c.tags?.includes(cat));

        const matchesSemester =
            selectedSemesters.length === 0 ||
            selectedSemesters.some((cat) => c.semestr?.includes(cat));

        return matchesTech && matchesTags && matchesSemester && matchesSearch;
    });

    return (
        <main className="flex-1 p-2 ml-4">
            <h2 className="text-4xl font-semibold">Gallery</h2>
            <h3 className="text-lg font-semibold pt-4 mr-25">
                Search <Searchbar value={search} onChange={setSearch} />
            </h3>
            <div>
                <FilterPanel
                    selected={selectedCategories}
                    onToggle={toggleCategory}
                    onClear={() => setSelectedCategories([])}
                    cards={cards}
                    techMode={techMode}
                    onTechModeChange={setTechMode}
                />
            </div>
            <div className="flex flex-row pt-2 gap-8 flex-wrap mt-4">
                {filtered.map((c) => (
                    <Link
                        to={c.name}
                        className="block transition-transform hover:scale-[1.02]"
                        onClick={(e) => {
                            if ((e.target as HTMLElement).closest('button')) {
                                e.preventDefault();
                            }
                        }}
                    >
                        <Card key={c.id} card={c} />
                    </Link>
                ))}
            </div>
        </main>
    );
}

export default Gallery;
