<script lang="ts">
  import { onMount } from 'svelte';
  import '../assets/planner.scss';
  import DisplayRecipes from './DisplayRecipes.svelte';
  //import { fetchFavorites, favoriteMap } from '../stores/favorites';
  import { get } from 'svelte/store';
  import { selectedRecipe} from '../stores/recipe'
  import { calorieRange, selectedDiets, selectedMealTypes } from '../stores/filters';

  let plan: any = {};
  let search = '';
  let results: any[] = [];
  let loading = false;
  let allRecipes: any[] = [];
  let filteredRecipes: any[] = [];
  let noSearch = true;

  async function recipeLookup(){
    if (!search.trim()) return;
        
    loading = true;
    results = []; // Clear immediately
    noSearch = false;

        
    try {
      // search filters
      const range = get(calorieRange);
      const diets = get(selectedDiets);
      const mealTypes = get(selectedMealTypes);

      const params = new URLSearchParams({
        query: search,
        minCalories: range[0].toString(),
        maxCalories: range[1].toString(),
      });

      if (diets.length > 0) {
        params.set('diet', diets.join(','));
      }
      if (mealTypes.length > 0) {
        params.set('mealType', mealTypes.join(','));
      }

      console.log(`Searching for: "${search}"`);
      const res = await fetch(`http://localhost:8000/api/recipe?${params.toString()}`, {
        credentials: 'include'
      });
      const data = await res.json();
      console.log('API response:', data);
      results = data.items || [];
    } catch (error) {
      console.error('Error:', error);
      results = [];
    } finally {
      loading = false;
    }
  }

  async function fetchAllRecipes() {
    loading = true;
    allRecipes = [];

    try {
      const res = await fetch(`http://localhost:8000/api/recipe`, {
        credentials: 'include'
      });
      const data = await res.json();
      allRecipes = data.items || [];
      filteredRecipes = allRecipes; // Initialize filtered recipes
    } catch (error) {
      console.error('Failed to fetch all recipes:', error);
    } finally {
      loading = false;
    }
  }

  async function applyFilters() {
    loading = true;
    noSearch = false;
    
    try {
      const range = get(calorieRange);
      const diets = get(selectedDiets);
      const mealTypes = get(selectedMealTypes);

      const params = new URLSearchParams({
        minCalories: range[0].toString(),
        maxCalories: range[1].toString(),
      });

      if (diets.length > 0) {
        params.set('diet', diets.join(','));
      }
      if (mealTypes.length > 0) {
        params.set('mealType', mealTypes.join(','));
      }

      const res = await fetch(`http://localhost:8000/api/recipe?${params.toString()}`, {
        credentials: 'include'
      });
      const data = await res.json();
      filteredRecipes = data.items || [];
    } catch (error) {
      console.error('Failed to apply filters:', error);
      filteredRecipes = allRecipes;
    } finally {
      loading = false;
    }
  }

  onMount(async () => {
    //await fetchFavorites();
    await fetchAllRecipes();
  });

  // Subscribe to filter changes and reapply filters
  $: if ($calorieRange || $selectedDiets || $selectedMealTypes) {
    applyFilters();
  }
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

  {#if results.length == 0}
  <DisplayRecipes
    category={noSearch ? "All Recipes" : "Search Results"}
    results={filteredRecipes}
  />
  {/if}

</div>