import { writable } from 'svelte/store';

export const selectedRecipe = writable<any>(null);
export const selectedServings = writable<number | null>(null);