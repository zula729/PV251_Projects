
type SearchbarProps = {
  value: string;
  onChange: (value: string) => void;
}

function Searchbar({value, onChange} : SearchbarProps) {
    return (
    <input name="myInput" className="rounded-xl border-solid border-2 flex items-center mt-4 p-1 pl-2 w-80"  
        placeholder="Search"
        value={value}
        onChange={(e) => onChange(e.target.value)}
    />
    )
}

export default Searchbar;