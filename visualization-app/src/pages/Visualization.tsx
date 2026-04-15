import TagsStackedBarChart from '../visualizations/TagsBarChart';
import TechnologyStackedBarChart from '../visualizations/TechnologyBarChart';

export function Visualization() {
    return (
        <main className="flex-1 p-2 ml-4">
            <h2 className="text-4xl font-semibold ">Visualization</h2>
            <div className="pt-8">
                <div>
                    <TechnologyStackedBarChart />
                    <TagsStackedBarChart />
                </div>
            </div>
        </main>
    );
}
export default Visualization;
