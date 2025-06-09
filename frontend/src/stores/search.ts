import { writable } from 'svelte/store';

interface Recipe {
  id?: number;
  title: string;
  calories: number;
  image: string;
  ingredients: string;
  instructions: string;
  servings: string;
}

interface SearchState {
  searchTerm: string;
  results: Recipe[];
  isSearching: boolean;
}

// Try to load cached search state from localStorage
const loadCachedState = (): SearchState => {
  try {
    const cached = localStorage.getItem('searchState');
    if (cached) {
      return JSON.parse(cached);
    }
  } catch (error) {
    console.error('Error loading cached search state:', error);
  }
  return {
    searchTerm: '',
    results: [],
    isSearching: false
  };
};

// Create the store with initial cached value
const searchState = writable<SearchState>(loadCachedState());

// Subscribe to changes and update localStorage
searchState.subscribe(value => {
  try {
    localStorage.setItem('searchState', JSON.stringify(value));
  } catch (error) {
    console.error('Error saving search state to cache:', error);
  }
});

export { searchState }; 