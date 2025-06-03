<script lang="ts">
  import { onMount } from 'svelte';
  import '../assets/planner.scss'
  import DisplayRecipes from './DisplayRecipes.svelte';
  import { fetchFavorites } from '../stores/favorites';
  import { get } from 'svelte/store';

  let plan: any = {};
  let search = '';
  let results: string[] = []; // Recipe titles
  let loading = false; // Add loading state

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

      for (let i = 0; i < data.items.length; i++){
        results.push(data.items[i].title);
      }
    } catch (error) {
      console.error('Error:', error);
      results = [];
    } finally {
      loading = false;
    }
  }

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