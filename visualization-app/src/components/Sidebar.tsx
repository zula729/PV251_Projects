
function Sidebar() {
  return (
    <div className="sidebar shadow-md">
        <nav>
          <ul className = "p-2 flex flex-col gap-2 text-xl w-50">
            <li><a href="#home"> <div className= "rounded-r-full border-solid border-2 border-l-0 flex items-center p-2 pl-4 pr-5 -ml-2">Home</div></a></li>
            <li><a href="#gallery"><div className= "rounded-r-full border-solid border-2 border-l-0 flex items-center p-2 pl-4 pr-5 -ml-2">Gallery</div></a></li>
            <li><a href="#visualization"><div className= "rounded-r-full border-solid border-2 border-l-0 flex items-center p-2 pl-4 pr-5 -ml-2">Visualization</div></a></li>
          </ul>
        </nav>
    </div>
  );
}

export default Sidebar;