import { SidebarData } from "./SidebarData";

function Sidebar() {
  return (
    <div className="sidebar h-screen w-50 pt-4 pr-3 pl-3 shadow-lg"> 
    <p className="px-3 text-[12px] font-semibold uppercase tracking-widest text-gray-800 mb-2">
        Navigation
      </p>
      <hr className="border-gray-300 pb-2"></hr>
      <ul className="">
        {SidebarData.map((val, key) => {
          return <li
            key={key}
            className={`group flex items-center gap-3 px-3 py-2.5 rounded-xl cursor-pointer mb-2
                transition-all duration-150 ease-in-out
              ${window.location.pathname === val.link
                ? "bg-amber-50 text-amber-700"
                : "text-gray-500 hover:bg-gray-50 hover:text-gray-900"
              }`}
            onClick={() => { window.location.pathname = val.link }}
          >
        <div className="pr-2 ">{val.icon}</div> 
          <div className=""> {val.title}</div> 
          </li>})}
      </ul>
    </div>
  );
}

export default Sidebar;