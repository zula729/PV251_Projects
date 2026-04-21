import { useEffect, useState } from 'react';
import { db } from './firebase';
import { ref, onValue } from 'firebase/database';
import type { CardType } from '../types/CardType';

export function useCards() {
    const [cards, setCard] = useState<CardType[]>([]);
    useEffect(() => {
        const cardsRef = ref(db, 'Keywords from projects');
        const unsubscribe = onValue(cardsRef, (snapshot) => {
            const data = snapshot.val();
            if (data) {
                const parsed: CardType[] = Object.entries(data).map(([id, entry]: any) => ({
                    id,
                    author: Array.isArray(entry.author) ? entry.author : [entry.author],
                    keywords: entry.keywords,
                    name: entry.name,
                    semestr: entry.semester,
                    tags: entry.tags,
                    technology: entry.technology?.map((t: string) => t.trim()),
                    images: entry.images ?? []
                }));
                setCard(parsed);
            } else {
                setCard([]);
            }
        });
        return () => unsubscribe();
    }, []);
    return cards;
}
