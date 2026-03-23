import Header from "./components/Header";
import Footer from "./components/Footer";
import Sidebar from "./components/Sidebar";
import Searchbar from "./components/Searchbar"
import Card from "./components/Card"; 
import FilterPanel from "./components/FilterPanel";
import { useState } from "react";
import { useCards } from "./hooks/useCards";


function App() {
    const cards = useCards();
    const [search, setSearch] = useState("");
    const [selectedCategories, setSelectedCategories] = useState<string[]>([]);
    const toggleCategory = (cat: string) => {
        setSelectedCategories(prev =>
            prev.includes(cat) ? prev.filter(c => c !== cat) : [...prev, cat]
        );
    };
    const filtered = cards.filter(c =>{
        const matchesSearch = 
            c.author?.toLowerCase().includes(search.toLowerCase()) ||
            c.keywords?.some((kw: string) => kw.toLowerCase().includes(search.toLowerCase())) ||
            c.technology?.some((tech: string) => tech.toLowerCase().includes(search.toLowerCase())) ||
            c.tags?.some((tag: string) => tag.toLowerCase().includes(search.toLowerCase()));
            
        const matchesCategories = selectedCategories.length === 0 ||
            selectedCategories.some(cat => c.tags?.includes(cat)) || 
            selectedCategories.some(cat => c.technology?.includes(cat)) ||
            selectedCategories.some(cat => c.semestr?.includes(cat));

        return matchesCategories && matchesSearch;
    });

    return (
    <div className="flex flex-col min-h-screen">
        <Header />
            <div className="flex flex-1"> 
                <div className="sticky top-0 self-start h-screen">
                    <Sidebar />
                </div>
                <main className="flex-1 p-2 ml-4">
                    <h2 className="text-4xl font-semibold ">Gallery</h2>
                    <div> <Searchbar value={search} onChange={setSearch} /> </div>
                    <div>
                        <FilterPanel
                        selected={selectedCategories}
                        onToggle={toggleCategory}
                        onClear={() => setSelectedCategories([])}
                        />
                    </div>
                    <div className="flex flex-row pt-2 gap-8 flex-wrap mt-4">
                        {filtered.map(c => (
                            <Card key={c.id} card={c} />
                        ))}
                        </div>
                </main>
            </div>
        <Footer />
    </div>
  );
}

export default App;