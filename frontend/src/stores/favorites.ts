import { writable } from 'svelte/store';

export const favoriteMap = writable<Record<string, boolean>>({});
export const favoriteCals = writable<Record<string, number>>({});

export async function fetchFavorites() {
  const res = await fetch('http://localhost:8000/api/favorites', { credentials: 'include' });
  const data = await res.json();
  favoriteMap.set(Object.fromEntries(data.favorites.map((title: string) => [title, true])));
}

export async function toggleFavorite(recipe: string, calories?: number) {
  favoriteMap.update((map) => {
    const updatedMap = { ...map };
    const isFav = updatedMap[recipe] === true;

    const apiCall = isFav
      ? fetch('http://localhost:8000/api/favorites', {
          method: 'DELETE',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ recipe }),
          credentials: 'include',
        })
      : fetch('http://localhost:8000/api/favorites', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ recipe, calories }),
          credentials: 'include',
        });

    apiCall.then((res) => {
      if (res.ok) {
        if (isFav){
          delete updatedMap[recipe];
          favoriteCals.update(cals=>{
            const newCals = {...cals};
            delete newCals[recipe]
            return newCals
          })
        }else{
          updatedMap[recipe] = true;
          if (calories !== undefined){
            favoriteCals.update(cals => ({...cals, [recipe]: calories}))
          }
        }
        favoriteMap.set(updatedMap); // re-trigger reactivity
      } else {
        res.text().then(text=>{
           console.error('Failed to toggle favorite', res.status, text);
        })
      }
    });

    return map;
  });
}
