import Label from './Label';

import type { CardType } from '../types/CardType';

import { useState, useRef, useEffect } from 'react';

type CardProps = {
    card: CardType;
};

type LabelWithType = {
    text: string;
    type: 'keyword' | 'tag' | 'technology';
};

function Card({ card }: CardProps) {
    const [expanded, setExpanded] = useState(false);
    const allLabels: LabelWithType[] = [
        ...(card.tags ?? [])
            .sort((a, b) => a.localeCompare(b))
            .map((tag) => ({ text: tag, type: 'tag' as const })),
        ...(card.technology ?? [])
            .sort((a, b) => a.localeCompare(b))
            .map((tech) => ({ text: tech, type: 'technology' as const })),
        ...(card.keywords ?? [])
            .sort((a, b) => a.localeCompare(b))
            .map((kw) => ({ text: kw, type: 'keyword' as const }))
    ].filter((label) => label !== undefined && label.text && label.text.trim() !== '');
    const [isOverflowing, setIsOverflowing] = useState(false);
    const labelsRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const el = labelsRef.current;
        if (!el) return;
        el.style.maxHeight = 'none';
        const fullHeight = el.scrollHeight;
        el.style.maxHeight = '';

        setIsOverflowing(fullHeight > 72);
    }, [allLabels]);

    return (
        <div className="rounded-2xl bg-white">
            <div className="flex flex-col">
                <div className={`border border-gray-400 shadow-lg/20 rounded-xl w-90 pb-3`}>
                    <img className="object-cover rounded-t-xl w-full h-40" src={card.images[0]} />
                    <div className="flex flex-col pl-2 pr-2 pt-2">
                        <div className="h-25">
                            <h2 className="text-xl font-semibold">{card.name}</h2>
                            <p className="text-sm text-gray-500">
                                {card.author.map((author, index) => (
                                    <span key={index}>
                                        {author}
                                        {index < card.author.length - 1 && ', '}
                                    </span>
                                ))}
                            </p>
                            <p className="text-m">{card.semestr}</p>
                        </div>
                        <hr className="mt-3 mb-2 border-gray-300"></hr>
                        <div>
                            <div
                                ref={labelsRef}
                                className={`flex flex-row pt-2 gap-1 flex-wrap overflow-hidden transition duration-300 
                            ${expanded ? 'max-h-screen' : 'max-h-15'}`}
                            >
                                {allLabels.map((label) => (
                                    <Label key={label.text} text={label.text} type={label.type} />
                                ))}
                            </div>
                            <div className="h-5 mt-1">
                                {(isOverflowing || expanded) && (
                                    <button
                                        onClick={() => setExpanded((prev) => !prev)}
                                        className="text-xs text-gray-500 hover:text-gray-800 cursor-pointer text-left"
                                    >
                                        {expanded ? '↑ less' : 'more ↓'}
                                    </button>
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Card;
