import { useEffect, useState } from "react";
import { db } from "./firebase";
import { ref, onValue } from "firebase/database";
import type { CardProps } from "../types/CardType";

export function useCards(){
    const [cards, setCard] = useState<CardProps []>([]);
    useEffect(() => {
        const cardsRef = ref(db, "Keywords from projects"); 
        const unsubscribe = onValue(cardsRef, (snapshot) => {
            const data = snapshot.val();
            if (data) {
                const parsed: CardProps [] = Object.entries(data).map(([id, entry]: any) => ({
                    id,
                    author: entry.author,
                    keywords: entry.keywords,
                    semestr: entry.semester,
                    tags: entry.tags,
                    technology: entry.technology,
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