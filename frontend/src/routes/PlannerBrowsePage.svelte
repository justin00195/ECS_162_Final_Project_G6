<script lang="ts">
  import { onMount } from 'svelte';
  import '../assets/planner.scss';
  import DisplayRecipes from './DisplayRecipes.svelte';
  import { get } from 'svelte/store';
  import { calorieRange, selectedDiets, selectedMealTypes } from '../stores/filters';

  let search = '';
  let results: any[] = [];
  let loading = false;
  let allRecipes: any[] = [];
  let filteredRecipes: any[] = [];
  let noSearch = true;

  async function getCaloriesFromNinja(query: string): Promise<number | null> {
    try {
      const res = await fetch('http://localhost:8000/api/quary_food', {
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
      console.error('Error fetching calories from Ninja API:', err);
      return null;
    }
  }

  async function recipeLookup() {
    if (!search.trim()) return;

    loading = true;
    results = [];
    noSearch = false;

    try {
      const range = get(calorieRange);
      const diets = get(selectedDiets);
      const mealTypes = get(selectedMealTypes);

      const params = new URLSearchParams({
        query: search,
        minCalories: range[0].toString(),
        maxCalories: range[1].toString(),
      });

      if (diets.length > 0) params.set('diet', diets.join(','));
      if (mealTypes.length > 0) params.set('mealType', mealTypes.join(','));

      const res = await fetch(`http://localhost:8000/api/recipe?${params.toString()}`, {
        credentials: 'include'
      });

      const data = await res.json();
      const rawResults = data.items || [];

      results = await Promise.all(
        rawResults.map(async (item: any) => {
          const cal = await getCaloriesFromNinja(item.title || item.name || search);
          return {
            ...item,
            calories: cal ?? 'N/A'
          };
        })
      );
    } catch (error) {
      console.error('Error during recipe lookup:', error);
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
      filteredRecipes = allRecipes;
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

      if (diets.length > 0) params.set('diet', diets.join(','));
      if (mealTypes.length > 0) params.set('mealType', mealTypes.join(','));

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
    await fetchAllRecipes();
  });

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
    <DisplayRecipes category="Search Results" results={results} />
  {/if}

  {#if results.length == 0}
    <DisplayRecipes category={noSearch ? "All Recipes" : "Search Results"} results={filteredRecipes} />
  {/if}
</div>
