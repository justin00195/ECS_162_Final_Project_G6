<script lang="ts">
  import { onMount } from 'svelte';
  import location from 'svelte-spa-router';
  import '../assets/planner.scss'

  let plan: any = {};
  let search = '';
  let results: any[] = [];
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
      
      if (Array.isArray(data)) {
        results = data;
      } else if (data.items) {
        results = data.items;
      } else {
        results = [];
      }
    } catch (error) {
      console.error('Error:', error);
      results = [];
    } finally {
      loading = false;
    }
  }
  
  function viewRecipe(title: string) {
    window.location.hash = `#/recipe/${encodeURIComponent(title)}`;
  }
</script>

<div class="container">
  <h1>Planner Page</h1>

  <h2>Browse Recipes</h2>
  <input bind:value={search} placeholder="Search for a recipe" />
  <button on:click={recipeLookup} disabled={loading}>
  {loading ? 'Searching...' : 'Search'}
  </button>

  {#if loading}
  <p>Loading recipes...</p>
  {:else if results.length > 0}
  <h3>Search Results for "{search}"</h3>
  <ul>
    {#each results as recipe}
      <li>
        <button on:click={() => viewRecipe(recipe.title)}>
          {recipe.title}
        </button>
      </li>
    {/each}
  </ul>
  {/if}
</div>