import { writable } from 'svelte/store';

export interface Recipe {
    id?: number;
    title: string;
    calories: number;
    image: string;
    ingredients: string;
    instructions: string;
    servings: string;
}

export const selectedRecipe = writable<Recipe | null>(null);