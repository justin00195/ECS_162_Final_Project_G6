<script lang="ts">
  import { onMount } from 'svelte';
  import '../assets/planner.scss'
  import DisplayRecipes from './DisplayRecipes.svelte';
  import { fetchFavorites } from '../stores/favorites';
  import { get } from 'svelte/store';
  import { selectedRecipe} from '../stores/recipe'
  

  let plan: any = {};
  let search = '';
  let results: any[] = []; //instead of storing just the titles, fetch all info
  let loading = false; // Add loading state

  async function getCaloriesFromNinja(query: string): Promise<number | null> {
    try {
      const res = await fetch('http://localhost:8000/report', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ query })
      });

      const data = await res.json();
      if (res.ok && data.items && data.items.length > 0) {
        return data.items.reduce((sum: number, item: any) => sum + (item.calories || 0), 0);
      } else {
        return null;
      }
    } catch (err) {
      console.error('Error to get receipt calories:', err);
      return null;
    }
  }

  async function recipeLookup(){
    if (!search.trim()) return;
    
    loading = true;
    results = []; // Clear immediately
    
    try {
      console.log(`Searching for: "${search}"`);
      const res = await fetch(`http://localhost:8000/api/recipe?query=${encodeURIComponent(search)}`, {
        credentials: 'include'
      });
      const data = await res.json();
      console.log('API response:', data);

      /*for (let i = 0; i < data.items.length; i++){
        results.push(data.items[i].title);
      }*/
     results = data.items;
    } catch (error) {
      console.error('Error:', error);
      results = [];
    } finally {
      loading = false;
    }
  }

  /*function tempRecipeInfo(recipe: any){
    selectedRecipe.set(recipe);
    window.location.hash = `#/recipe/${encodeURIComponent(title)}`
  }*/

  onMount(async () => {
    await fetchFavorites();
  });

</script>

<div class="container">
  <h1>Browse Recipes</h1>
  <input bind:value={search} placeholder="Search for a recipe" />
  <button on:click={recipeLookup} disabled={loading}>
    {loading ? 'Searching...' : 'Search'}
  </button>

  {#if loading}
    <p>Loading recipes...</p>
  {:else if results.length > 0}
    <DisplayRecipes
      category="Search Results"
      results={results}
    />
  {/if}
</div>