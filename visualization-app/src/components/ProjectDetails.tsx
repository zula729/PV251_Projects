import { useParams } from 'react-router';
import { useCards } from '../hooks/useCards';
import { useMemo, useState } from 'react';
import Label from './Label';

function ProjectDetails() {
    const [currentImageIndex, setCurrentImageIndex] = useState(0);
    const { id } = useParams<{ id: string }>();
    const cards = useCards();
    const card = useMemo(() => cards.find((c) => c.id === id), [cards, id]);

    if (!card) {
        return <div>No project</div>;
    }

    return (
        <main className="flex-1 p-8 ml-4">
            <h2 className="text-4xl font-semibold mb-8">Gallery/{card.name}</h2>
            <div className="w-full max-w-5xl">
                <div className="relative w-full bg-gray-300 rounded-lg overflow-hidden mb-6">
                    <img
                        src={card.images[currentImageIndex]}
                        alt={`carousel-image-${currentImageIndex}`}
                        className="w-full h-120 object-cover"
                    />
                </div>

                <div className="flex gap-3 overflow-x-auto pb-2">
                    {card.images.map((image, index) => (
                        <button
                            onClick={() => setCurrentImageIndex(index)}
                            className={`shrink-0 rounded-lg overflow-hidden border-3 cursor-pointer transition ${
                                currentImageIndex === index
                                    ? 'border-amber-200 opacity-100'
                                    : 'border-gray-300 opacity-60 hover:opacity-100'
                            }`}
                        >
                            <img
                                src={image}
                                alt={`thumbnail-${index}`}
                                className="w-32 h-24 object-cover"
                            />
                        </button>
                    ))}
                </div>
            </div>

            <div className="max-w-5xl">
                <div className="flex flex-col mb-6 ">
                    <p className="font-semibold text-gray-700 mb-2">Category:</p>
                    <div className="flex flex-nowrap gap-2 overflow-x-auto">
                        {card.tags.map((tags) => (
                            <Label key={tags} text={tags} type={'tag'}></Label>
                        ))}
                    </div>
                    <p className="font-semibold text-gray-700 mb-2">Technology:</p>
                    <div className="flex flex-wrap gap-2">
                        {card.technology.map((technology) => (
                            <Label key={technology} text={technology} type={'technology'}></Label>
                        ))}
                    </div>
                    <p className="font-semibold text-gray-700 mb-2">Semester:</p>
                    <div className="flex flex-wrap gap-2">
                        <Label key={card.semestr} text={card.semestr} type={'semestr'}></Label>
                    </div>
                    <p className="font-semibold text-gray-700 mb-2">Keywords:</p>
                    <div className="flex flex-wrap gap-2">
                        {card.keywords.map((keyword) => (
                            <Label key={keyword} text={keyword} type={'keyword'}></Label>
                        ))}
                    </div>
                </div>
                <h1 className="text-3xl font-bold mb-4">{card.name}</h1>
                <p className="text-lg text-gray-700 mb-2">
                    <strong>Author:</strong>{' '}
                    {card.author.map((author, index) => (
                        <span key={index}>
                            {author}
                            {index < card.author.length - 1 && ', '}
                        </span>
                    ))}
                </p>
                <p className="text-lg text-gray-700">
                    <strong>About:</strong>{' '}
                    {
                        'Lorem ipsum dolor sit amet consectetur adipiscing elit. Quisque faucibus ex sapien vitae pellentesque sem placerat. In id cursus mi pretium tellus duis convallis. Tempus leo eu aenean sed diam urna tempor. Pulvinar vivamus fringilla lacus nec metus bibendum egestas. Iaculis massa nisl malesuada lacinia integer nunc posuere. Ut hendrerit semper vel class aptent taciti sociosqu. Ad litora torquent per conubia nostra inceptos himenaeos.Lorem ipsum dolor sit amet consectetur adipiscing elit. Quisque faucibus ex sapien vitae pellentesque sem placerat. In id cursus mi pretium tellus duis convallis. Tempus leo eu aenean sed diam urna tempor. Pulvinar vivamus fringilla lacus nec metus bibendum egestas. Iaculis massa nisl malesuada lacinia integer nunc posuere. Ut hendrerit semper vel class aptent taciti sociosqu. Ad litora torquent per conubia nostra inceptos himenaeos.Lorem ipsum dolor sit amet consectetur adipiscing elit. Quisque faucibus ex sapien vitae pellentesque sem placerat. In id cursus mi pretium tellus duis convallis. Tempus leo eu aenean sed diam urna tempor. Pulvinar vivamus fringilla lacus nec metus bibendum egestas. Iaculis massa nisl malesuada lacinia integer nunc posuere. Ut hendrerit semper vel class aptent taciti sociosqu. Ad litora torquent per conubia nostra inceptos himenaeos.'
                    }
                </p>
                <p className="text-lg text-gray-700">
                    <strong>Link:</strong> {}
                </p>
            </div>
        </main>
    );
}

export default ProjectDetails;
