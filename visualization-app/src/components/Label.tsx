
function Label({text} : {text: string}) {
    return (
        <div className="rounded-xl bg-gray-200 flex items-center p-0.5 pl-2 pr-2">
            {text}
        </div>
    );
}

export default Label;