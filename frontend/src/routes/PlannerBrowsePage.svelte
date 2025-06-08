<script lang="ts">
  import { onMount } from 'svelte';
  import '../assets/planner.scss';
  import DisplayRecipes from './DisplayRecipes.svelte';
  import { get } from 'svelte/store';
  import { selectedRecipe} from '../stores/recipe'
  import { calorieRange, selectedDiets, selectedMealTypes } from '../stores/filters';
  import { searchState } from '../stores/search';  // We'll create this store
  import { selectedMeal } from '../stores/meal';
  import { writable } from 'svelte/store';

  interface Recipe {
    id?: number;  // Make id optional since some recipes might not have it yet
    title: string;
    calories: number;
    image: string;
    ingredients: string;
    instructions: string;
    servings: string;
  }

  interface FavoriteResponse {
    favorites: (Recipe | string)[];
  }

  let plan: any = {};
  let loading = false;
  let search = '';
  let results: Recipe[] = [];
  let noSearch = true;
  let favoriteRecipes: Recipe[] = [];
  let initialRecipes: Recipe[] = [];
  let isSearching = false;
  let isLoadingInitial = true;  // Separate loading state for initial recipes
  let isFavoriteActionInProgress = false;

  // Add stores for caching
  const cachedFavorites = writable<Recipe[]>([]);
  const cachedSuggestions = writable<Recipe[]>([]);
  const hasFetchedInitial = writable(false);

  // Load cached data from localStorage on initialization
  try {
    const savedFavorites = localStorage.getItem('cachedFavorites');
    const savedSuggestions = localStorage.getItem('cachedSuggestions');
    if (savedFavorites) {
      cachedFavorites.set(JSON.parse(savedFavorites));
    }
    if (savedSuggestions) {
      cachedSuggestions.set(JSON.parse(savedSuggestions));
    }
  } catch (error) {
    console.error('Error loading cached data:', error);
  }

  // Subscribe to store changes to update localStorage
  cachedFavorites.subscribe(value => {
    try {
      localStorage.setItem('cachedFavorites', JSON.stringify(value));
    } catch (error) {
      console.error('Error saving favorites to cache:', error);
    }
  });

  cachedSuggestions.subscribe(value => {
    try {
      localStorage.setItem('cachedSuggestions', JSON.stringify(value));
    } catch (error) {
      console.error('Error saving suggestions to cache:', error);
    }
  });

  // Get meal ID from URL search params
  const urlParams = new URLSearchParams(window.location.hash.split('?')[1] || '');
  const mealId = urlParams.get('meal');
  const fromPlanner = urlParams.get('from') === 'planner';
  
  async function fetchFavoriteRecipes() {
    if (isFavoriteActionInProgress) {
      return;
    }
    
    // Check if we have cached favorites
    const currentFavorites = get(cachedFavorites);
    if (currentFavorites.length > 0) {
      favoriteRecipes = currentFavorites;
      return;
    }
    
    isFavoriteActionInProgress = true;
    
    try {
      const response = await fetch('http://localhost:8000/api/favorites', {
        credentials: 'include'
      });
      if (!response.ok) {
        throw new Error('Failed to fetch favorites');
      }
      const data = await response.json() as FavoriteResponse;
      console.log('Raw favorites data:', data);

      if (!data.favorites || !Array.isArray(data.favorites)) {
        console.log('No favorites array in response:', data);
        favoriteRecipes = [];
        cachedFavorites.set([]);
        return;
      }

      const recipesPromises = data.favorites.map(async (favorite) => {
        const recipeTitle = typeof favorite === 'string' ? favorite : favorite.title;
        try {
          const recipeResponse = await fetch(`http://localhost:8000/api/recipe?query=${encodeURIComponent(recipeTitle)}&exact=true`, {
            credentials: 'include'
          });
          if (!recipeResponse.ok) {
            throw new Error(`Failed to fetch recipe for ${recipeTitle}`);
          }
          const recipeData = await recipeResponse.json();
          return recipeData.items?.[0] || null;
        } catch (error) {
          console.error(`Failed to fetch recipe details for ${recipeTitle}:`, error);
          return null;
        }
      });

      const recipes = await Promise.all(recipesPromises);
      const validRecipes = recipes.filter((recipe): recipe is Recipe => recipe !== null);
      favoriteRecipes = validRecipes;
      cachedFavorites.set(validRecipes); // Cache the favorites
      
    } catch (error) {
      console.error('Failed to fetch favorite recipes:', error);
      favoriteRecipes = [];
      cachedFavorites.set([]);
    } finally {
      setTimeout(() => {
        isFavoriteActionInProgress = false;
      }, 500);
    }
  }

  // Fetch favorites first, then initial recipes
  async function initialize() {
    try {
      console.log('Starting initialization...');
      await fetchFavoriteRecipes();
      await fetchInitialRecipes();
    } catch (error) {
      console.error('Initialization error:', error);
    }
  }

  onMount(async () => {
    // Get meal ID from URL search params
    const urlParams = new URLSearchParams(window.location.hash.split('?')[1] || '');
    const mealId = urlParams.get('meal');
    const fromPlanner = urlParams.get('from') === 'planner';
    
    // Only restore search state if not coming from planner
    if (!fromPlanner) {
      const savedState = get(searchState);
      if (savedState) {
        search = savedState.searchTerm;
        results = savedState.results;
        isSearching = savedState.isSearching;
        noSearch = !isSearching;
        
        // Also restore filters if they were used in the search
        try {
          const cacheKey = JSON.stringify({
            search: savedState.searchTerm,
            range: get(calorieRange),
            diets: get(selectedDiets),
            mealTypes: get(selectedMealTypes)
          });
          
          const cachedResults = localStorage.getItem(`searchResults_${cacheKey}`);
          if (cachedResults) {
            results = JSON.parse(cachedResults);
          }
        } catch (error) {
          console.error('Error restoring cached search results:', error);
        }
      }
    } else {
      // Clear search state if coming from planner
      search = '';
      results = [];
      isSearching = false;
      noSearch = true;
      searchState.set({
        searchTerm: '',
        results: [],
        isSearching: false
      });
    }
    
    // Initialize data
    await initialize();
    console.log('Initialization complete. Favorites:', favoriteRecipes);
  });

  async function removeFromFavorites(recipe: Recipe, event: MouseEvent) {
    event.preventDefault();
    event.stopPropagation();
    
    if (isFavoriteActionInProgress) {
      return;
    }
    
    isFavoriteActionInProgress = true;
    
    try {
      const response = await fetch('http://localhost:8000/api/favorites', {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify({ recipe: recipe.title })
      });

      if (!response.ok) {
        throw new Error(`Failed to remove from favorites: ${response.statusText}`);
      }

      favoriteRecipes = favoriteRecipes.filter(fav => fav.title !== recipe.title);
      cachedFavorites.set(favoriteRecipes); // Update cache
    } catch (error) {
      console.error('Failed to remove from favorites:', error);
      alert('Failed to remove recipe from favorites. Please try again.');
    } finally {
      setTimeout(() => {
        isFavoriteActionInProgress = false;
      }, 500);
    }
  }

  async function fetchInitialRecipes() {
    // Check if we have cached suggestions
    const currentSuggestions = get(cachedSuggestions);
    if (currentSuggestions.length > 0) {
      initialRecipes = currentSuggestions;
      isLoadingInitial = false;
      return;
    }

    try {
      const initialSearch = 'soup';
      const initialLimit = 5;
      const res = await fetch(`http://localhost:8000/api/recipe?query=${initialSearch}&limit=${initialLimit}`, {
        credentials: 'include'
      });
      const data = await res.json();
      initialRecipes = data.items || [];
      cachedSuggestions.set(data.items || []); // Cache the suggestions
    } catch (error) {
      console.error('Failed to fetch initial recipes:', error);
      initialRecipes = [];
      cachedSuggestions.set([]);
    } finally {
      isLoadingInitial = false;
    }
  }

  async function handleSearch(event?: KeyboardEvent | MouseEvent) {
    if (event && 'key' in event && event.key !== 'Enter') return;
    
    if (!search.trim()) return;
    
    // Check if we have cached results for this exact search with current filters
    const currentState = get(searchState);
    const range = get(calorieRange);
    const diets = get(selectedDiets);
    const mealTypes = get(selectedMealTypes);
    
    // Create a cache key that includes filters
    const cacheKey = JSON.stringify({
      search,
      range,
      diets,
      mealTypes
    });
    
    // Try to get results from localStorage
    try {
      const cachedResults = localStorage.getItem(`searchResults_${cacheKey}`);
      if (cachedResults) {
        const parsedResults = JSON.parse(cachedResults);
        results = parsedResults;
        isSearching = true;
        noSearch = false;
        
        // Update search state
        searchState.set({
          searchTerm: search,
          results,
          isSearching: true
        });
        return;
      }
    } catch (error) {
      console.error('Error reading from cache:', error);
    }
    
    isSearching = true;
    noSearch = false;
    loading = true;

    try {
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

      const res = await fetch(`http://localhost:8000/api/recipe?${params.toString()}`, {
        credentials: 'include'
      });
      const data = await res.json();
      results = data.items || [];
      
      // Cache the results with the filters
      try {
        localStorage.setItem(`searchResults_${cacheKey}`, JSON.stringify(results));
      } catch (error) {
        console.error('Error caching search results:', error);
      }
      
      // Save search state
      searchState.set({
        searchTerm: search,
        results,
        isSearching: true
      });
    } catch (error) {
      console.error('Error:', error);
      results = [];
    } finally {
      loading = false;
    }
  }

  function goToFilters() {
    // Preserve meal ID and from parameter when navigating to filters
    const urlParams = new URLSearchParams(window.location.hash.split('?')[1] || '');
    const mealId = urlParams.get('meal');
    const fromPlanner = urlParams.get('from');
    
    let filterUrl = '#/filter';
    const params = new URLSearchParams();
    
    if (mealId) params.append('meal', mealId);
    if (fromPlanner) params.append('from', fromPlanner);
    if (params.toString()) filterUrl += '?' + params.toString();
    
    window.location.hash = filterUrl;
  }

  // Update the goToRecipe function
  function goToRecipe(recipe: Recipe) {
    selectedRecipe.set(recipe);  // Store the full recipe data
    const encodedTitle = encodeURIComponent(recipe.title);
    // Keep the meal ID when navigating to recipe
    const urlParams = new URLSearchParams(window.location.hash.split('?')[1] || '');
    const mealId = urlParams.get('meal');
    const fromPlanner = urlParams.get('from');
    
    let recipeUrl = `/recipe/${encodedTitle}`;
    const params = new URLSearchParams();
    
    if (mealId) params.append('meal', mealId);
    if (fromPlanner) params.append('from', fromPlanner);
    if (params.toString()) recipeUrl += '?' + params.toString();
    
    window.location.hash = recipeUrl;
  }

  async function addToFavorites(recipe: Recipe, event: MouseEvent) {
    event.preventDefault();
    event.stopPropagation();
    
    if (isFavoriteActionInProgress) {
      return;
    }
    
    if (favoriteRecipes.some(fav => fav.title === recipe.title)) {
      return;
    }
    
    isFavoriteActionInProgress = true;
    
    try {
      const response = await fetch('http://localhost:8000/api/favorites', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify({ recipe: recipe.title })
      });

      if (!response.ok) {
        const data = await response.json();
        
        if (response.status === 409 || (data.error && data.error.includes('UNIQUE constraint failed'))) {
          if (!favoriteRecipes.some(fav => fav.title === recipe.title)) {
            favoriteRecipes = [...favoriteRecipes, recipe];
            cachedFavorites.set(favoriteRecipes); // Update cache
          }
          return;
        }
      }

      favoriteRecipes = [...favoriteRecipes, recipe];
      cachedFavorites.set(favoriteRecipes); // Update cache
    } catch (error) {
      console.error('Failed to add to favorites:', error);
    } finally {
      setTimeout(() => {
        isFavoriteActionInProgress = false;
      }, 500);
    }
  }

  function isRecipeFavorited(recipe: Recipe): boolean {
    return favoriteRecipes.some(fav => fav.title === recipe.title);
  }

  function handleRecipeClick(recipe: Recipe, event: MouseEvent) {
    // If the click was on the heart button, don't navigate
    if ((event.target as HTMLElement).closest('.heart-button')) {
      return;
    }
    goToRecipe(recipe);
  }

  // Subscribe to filter changes and reapply search if we have an active search
  $: if (($calorieRange || $selectedDiets || $selectedMealTypes) && isSearching) {
    handleSearch();
  }

  // Subscribe to changes in results to update favorites
  $: if (results.length > 0) {
    fetchFavoriteRecipes();
  }
</script>

<div class="browse-container">
    <div class="back-button-container">
        <button class="back-button" on:click={() => window.location.hash = '#/planner'}>
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M19 12H5"/>
                <path d="M12 19l-7-7 7-7"/>
            </svg>
            Back to Planner
        </button>
    </div>
    <h1>Browse Recipes</h1>

    <div class="search-bar">
        <div class="search-input-container">
            <svg class="search-icon" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="11" cy="11" r="8"></circle>
              <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
            </svg>
            <input 
                type="text" 
                placeholder="What do you want to eat?" 
                bind:value={search}
                on:keydown={handleSearch}
            >
            <button class="search-button" on:click={handleSearch}>
                Search
            </button>
        </div>
    </div>

    {#if isSearching}
        <div class="search-results-container">
            <h2>Search Results</h2>
            {#if loading}
                <div class="loading">Searching...</div>
            {:else if results.length > 0}
                <div class="results-grid">
                    {#each results as recipe, index (recipe.id ?? recipe.title ?? index)}
                        <div class="recipe-card">
                            <span class="recipe-title" on:click={() => goToRecipe(recipe)}>{recipe.title}</span>
                            <button 
                              class="heart-button"
                              on:click|stopPropagation={(e) => addToFavorites(recipe, e)}
                            >
                              {#if isRecipeFavorited(recipe)}
                                <img 
                                    src="../public/solid-heart.png" 
                                    alt="heart" 
                                    class="heart-icon" 
                                />
                              {:else}
                                <img 
                                    src="../public/empty-heart.png" 
                                    alt="heart" 
                                    class="heart-icon" 
                                />
                              {/if}
                            </button>
                        </div>
                    {/each}
                </div>
            {:else}
                <div class="no-results">No recipes found</div>
            {/if}
        </div>
    {:else}
        <div class="recipes-section">
            <div class="section-header">
                <h2>Favorites</h2>
                <button class="filters-btn" on:click={goToFilters}>
                    Filters
                </button>
            </div>
            <div class="favorites-section">
                <div class="recipe-tags">
                    {#if favoriteRecipes.length === 0}
                        <div class="no-favorites">No favorite recipes yet</div>
                    {:else}
                        {#each favoriteRecipes as recipe, index (recipe.id ?? recipe.title ?? index)}
                            <div class="recipe-tag" on:click={() => goToRecipe(recipe)} role="button" tabindex="0">
                                <div class="tag-content">
                                    <span class="tag-text">{recipe.title}</span>
                                    <button 
                                        class="remove-button"
                                        on:click|stopPropagation={(e) => removeFromFavorites(recipe, e)}
                                    >
                                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                            <line x1="18" y1="6" x2="6" y2="18"></line>
                                            <line x1="6" y1="6" x2="18" y2="18"></line>
                                        </svg>
                                    </button>
                                </div>
                            </div>
                        {/each}
                    {/if}
                </div>
            </div>

            <div class="all-recipes-section">
                <div class="section-header">
                    <h2>Suggested Recipes</h2>
                </div>
                <div class="recipe-tags">
                    {#if isLoadingInitial}
                        <div class="loading">Loading recipes...</div>
                    {:else}
                        {#each initialRecipes as recipe, index (recipe.id ?? recipe.title ?? index)}
                            <div class="recipe-tag" on:click={() => goToRecipe(recipe)} role="button" tabindex="0">
                                <div class="tag-content">
                                    <span class="tag-text">{recipe.title}</span>
                                    <button 
                                        class="heart-button"
                                        on:click|stopPropagation={(e) => addToFavorites(recipe, e)}
                                    >
                                        <img 
                                            src={isRecipeFavorited(recipe) ? '../public/solid-heart.png' : '../public/empty-heart.png'} 
                                            alt="heart" 
                                            class="heart-icon" 
                                        />
                                    </button>
                                </div>
                            </div>
                        {/each}
                    {/if}
                </div>
            </div>
        </div>
    {/if}
</div>

<style lang="scss">
    .browse-container {
        max-width: 1000px;
        margin: 0 auto;
        padding: 0 2rem;
        position: relative;

        h1 {
            color: #91593B;
            text-align: center;
            margin: 1rem 0 2rem 0;
            padding-top: 1rem;
        }
    }

    .back-button-container {
        position: absolute;
        top: 1rem;
        left: 2rem;
    }

    .back-button {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        background: none;
        border: none;
        color: #91593B;
        font-size: 1rem;
        cursor: pointer;
        padding: 0.5rem;
        border-radius: 15px;
        transition: background-color 0.2s;

        svg {
            transform: none;
        }

        &:hover {
            background-color: rgba(145, 89, 59, 0.1);
        }
    }

    .search-bar {
        position: relative;
        margin-bottom: 2rem;
    }

    .search-input-container {
        width: 100%;
        position: relative;
        display: flex;
        gap: 0.5rem;
        align-items: top;

        .search-icon {
          position: absolute;
          left: 10px;
          top: 45%;
          transform: translateY(-50%);
          color: #8B4513;
          pointer-events: none;
        }

        input {
            flex: 1;
            padding: 0.5rem 1rem;
            padding-left: 2rem;
            border: 1px solid #ddd;
            border-radius: 15px;
            font-size: 1rem;
            margin-top: -0.2rem;

            &:focus {
                outline: none;
                border-color: #8B4513;
            }
        }

        .search-button {
          display: flex;
          align-items: center;
          justify-content: center;
          background-color: #6479AF;
          color: white;
          border: none;
          padding: 1rem 1rem;
          border-radius: 30px;
          cursor: pointer;
          width: 100px;
          height: 30px;
          font-size: 1rem;
          transition: background-color 0.2s;

            &:hover {
                background: #495880;
            }
        }

        input::placeholder {
            color: #DFD3CC;
        }
    }

    .recipes-section {
        background: #DFD3CC;
        border-radius: 15px;
        padding: 2rem;
    }

    .section-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;

        h2 {
            color: #91593B;
            font-size: 1.2rem;
            font-weight: 400;
            margin: 0;  // Remove default margin
        }

        .filters-btn {
            display: flex;
            align-items: center;
            justify-content: center;
            background-color: #6479AF;
            color: white;
            border: none;
            padding: 1rem 1rem;
            border-radius: 30px;
            cursor: pointer;
            width: 100px;
            height: 30px;
            font-size: 0.9rem;
            transition: background-color 0.2s;

            &:hover {
                background: #495880;
            }
        }
    }

    .favorites-section, .all-recipes-section {
        margin-bottom: 2rem;
    }

    .filters-section {
        display: none;
    }

    .recipe-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 0.75rem;
    }

    .recipe-tag {
        background: #EDEAE8;
        color: #91593B;
        padding: 0.5rem 1rem;
        border-radius: 15px;
        font-size: 0.9rem;
        position: relative;
        border: 1px solid #91593B;
        cursor: pointer;
        transition: background-color 0.2s;
        user-select: none;  // Prevent text selection on click

        &:hover {
            background: #c9bdb5;
        }

        // Add keyboard focus styles
        &:focus {
            outline: 2px solid #91593B;
            outline-offset: 2px;
        }
    }

    .tag-content {
        display: flex;
        align-items: center;
        gap: 1rem;
    }

    .tag-text {
        flex: 1;
    }

    .heart-button {
        background: none;
        border: none;
        padding: 0.5rem;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        
        &:hover {
            transform: scale(1.1);
        }
    }

    .heart-icon {
        width: 30px;
        height: 30px;
        transition: transform 0.2s;
    }

    .remove-button {
        background: none;
        border: none;
        padding: 0.5rem;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #91593B;
        
        &:hover {
            transform: scale(1.1);
            color: #6b3410;
        }

        svg {
            width: 16px;
            height: 16px;
        }
    }

    .search-results-container {
        background: #DFD3CC;
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 2rem;

        h2 {
            color: #91593B;
            font-size: 1.2rem;
            margin-bottom: 1rem;
        }
    }

    .results-grid {
        display: flex;
        flex-wrap: wrap;
        gap: 1rem;
    }

    .recipe-card {
        background: #EDEAE8;
        border: 1px solid #91593B;
        border-radius: 20px;
        padding: 0.75rem 2.5rem 0.75rem 1rem;
        color: #60361F;
        font-size: 0.9rem;
        position: relative;
        transition: all 0.2s;
        display: flex;
        align-items: center;
        text-align: left;

        &:hover {
            background: #DFD3CC;
        }
    }

    .recipe-title {
        flex: 1;
        cursor: pointer;
        
        &:hover {
            text-decoration: underline;
        }
    }

    .loading, .no-results {
        color: #91593B;
        text-align: center;
        padding: 1rem;
        font-style: italic;
    }

    .no-favorites {
        color: #91593B;
        font-style: italic;
        padding: 1rem;
        text-align: center;
    }
</style>