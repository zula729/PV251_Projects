export type CardType  = {
  id: string;
  author: string;
  keywords: string[];
  semestr: string,
  tags: string[]
  technology: string[];
  image?: string;
}

export type CardProps = {
    card: CardType;  // ← поле называется именно "card"
}