import { writable } from 'svelte/store';

export interface Meal {
  id: number;
  name: string;
  date: string;
  recipes: string[];
}

export const selectedMeal = writable<Meal | null>(null); 