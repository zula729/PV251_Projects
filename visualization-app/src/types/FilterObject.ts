export type sortOption = "asc" | "desc"

export type FilterObject = {
  searchTerm: string,
  keywords: string[],
  tags: string[],
  technology: string[],
  semester: string,
  sort: sortOption
}