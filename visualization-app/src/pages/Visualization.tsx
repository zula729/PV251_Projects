import SpecifiedDomainRadarChart from "../visualizations/SpecifiedDomainRadarChart";
// import SimpleTreemap from "../visualizations/SimpleTreemap";


export function Visualization() {
    return (
        <main className="flex-1 p-2 ml-4">
            <h2 className="text-4xl font-semibold ">Visualization</h2>
            <SpecifiedDomainRadarChart />
            {/* <SimpleTreemap/> */}
        </main>
  );
}
export default Visualization;