import { writable } from 'svelte/store';

export const calorieRange = writable<[number, number]>([0, 1500]);
export const selectedDiets = writable(<string[]>([]));
export const selectedMealTypes = writable(<string[]>([]));