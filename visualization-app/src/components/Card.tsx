import image from "../assets/image.png"
import Label from "./Label";

import type { CardProps } from "../types/CardType";

function Card({ card } : CardProps) {
  return (
    <div className="rounded-2xl bg-white">
      <div className="flex flex-col">
        <div className="border border-gray-400 shadow-lg/20 rounded-xl w-80 pb-3">
          <img className="object-cover rounded-t-xl w-full h-30"src={image}/>
          <div className="flex flex-col pl-2 pr-2 pt-2">
            <h2 className="text-2xl font-semibold">{card.id}</h2>
            <p className="text-sm text-gray-500">{card.author}</p>
            <p className="text-m">{card.semestr}</p>
            <hr className="mt-3 mb-2 border-gray-300"></hr>
            <div className="flex flex-row pt-2 gap-1 flex-wrap">
                {card.keywords.map((kw) => (
                  <Label key={kw} text={kw}/>
                ))}
                {card.tags.map((tag) => (
                  <Label key={tag} text={tag}/>
                ))}
                {card.technology.map((tech) => (
                  <Label key={tech} text={tech}/>
                ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Card;