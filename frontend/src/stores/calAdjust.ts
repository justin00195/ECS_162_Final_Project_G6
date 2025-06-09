import { writable } from 'svelte/store';

export const calAdjust = writable<number | null>(null);
export const recipeCals = writable<number | null>(null);