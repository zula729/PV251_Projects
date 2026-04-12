type LabelProps = {
    text: string;
    type?: "keyword" | "tag" | "technology";
}

const colorMap = {
    keyword:    "bg-gray-100 text-gray-600",
    tag:        "bg-amber-50 text-amber-600",
    technology: "bg-green-50 text-green-600",
}

function Label({ text, type = "keyword" }: LabelProps) {
    return (
        <span className={`rounded-xl flex items-center p-0.5 pl-2 pr-2 ${colorMap[type]}`}>
            {text.charAt(0).toUpperCase() + text.slice(1).toLowerCase().replace(/_/g, " ")}
        </span>
    );
}

export default Label;
