import StackedBarChart from '../visualizations/StackedBarChart';
import { TAGS, TECHNOLOGY } from '../types/filterOptions';

export function Visualization() {
    return (
        <main className="flex-1 p-8 ml-4">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-4xl font-semibold">Visualization</h2>
                    <p className="text-gray-500 mt-1 text-sm">
                        Overview of technology and tag distribution across projects
                    </p>
                </div>
            </div>
            <div className="space-y-6 pt-4">
                <div className="border border-gray-200 rounded-xl p-6 shadow-md">
                    <h3 className="text-lg font-semibold mb-1">Technology Distribution</h3>
                    <p className="text-sm text-gray-400 mb-4">
                        Frequency of tehcnologies used across projects
                    </p>
                    <StackedBarChart
                        options={TECHNOLOGY}
                        cardField="technology"
                        dataKey="tech"
                        minTotal={5}
                        height={500}
                    />
                </div>

                <div className="border border-gray-200 rounded-xl p-6 shadow-md">
                    <h3 className="text-lg font-semibold mb-1">Tag Distribution</h3>
                    <p className="text-sm text-gray-400 mb-4">Frequency of tags across projects</p>
                    <StackedBarChart
                        options={TAGS}
                        cardField="tags"
                        dataKey="tag"
                        height={500}
                        yAxisStep={5}
                    />
                </div>
            </div>
        </main>
    );
}
export default Visualization;
