<script lang="ts">
  import { onMount } from 'svelte';
  import { selectedRecipe } from '../stores/recipe';
  import type { Recipe } from '../stores/recipe';
  import { get } from 'svelte/store';

  export let params;
  let loading = true;
  let errorMessage = '';
  let mealId: number | null = null;
  let recipe: Recipe | null = null;

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

  onMount(async () => {
    const urlParams = new URLSearchParams(window.location.hash.split('?')[1] || '');
    const mealIdParam = urlParams.get('meal');
    mealId = mealIdParam ? parseInt(mealIdParam, 10) : null;

    // 從 store 拿當前選的食譜
    recipe = get(selectedRecipe);
    if (!recipe) {
      errorMessage = 'Recipe Not Found';
      window.location.hash = '/planner/browse';
      return;
    }

    // 若缺 calories，用 Ninja API 補
    if (!recipe.calories && recipe.title) {
      const cal = await getCaloriesFromNinja(recipe.title);
      recipe = {
        ...recipe,
        calories: cal ?? 0
      };
    }

    loading = false;
  });

  function goBack() {
    selectedRecipe.set(null);
    const urlParams = new URLSearchParams(window.location.hash.split('?')[1] || '');
    const mealId = urlParams.get('meal');
    window.location.hash = mealId
      ? `#/planner/browse?meal=${mealId}`
      : '#/planner/browse';
  }

  async function addToMeal() {
    if (!recipe || !mealId) return;
    try {
      const getResponse = await fetch(`http://localhost:8000/api/meal/${mealId}`, {
        credentials: 'include'
      });
      const mealData = await getResponse.json();
      const currentIngredients = mealData.ingredients || [];

      const response = await fetch(`http://localhost:8000/api/meal/${mealId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          ingredients: [...currentIngredients, recipe.title]
        })
      });

      if (!response.ok) throw new Error('Failed to add recipe');
      window.location.hash = '#/planner';
    } catch (error) {
      console.error('Add to meal failed:', error);
      alert('Failed to add recipe to meal. Please try again.');
    }
  }
</script>



<div class="recipe-detail">
    <div class="container">
      <div class="back-button-container">
        <button class="back-button" on:click={goBack}>
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M19 12H5"/>
              <path d="M12 19l-7-7 7-7"/>
          </svg>
          Back to Search
        </button>
      </div>
  
      {#if loading}
        <div class="loading">
          <h2>🍳</h2>
          <p>Loading your delicious recipe...</p>
        </div>
      {:else if errorMessage}
        <h2>{errorMessage}</h2>
      {:else if recipe}
        <div class="recipe-container">
          <h1>{recipe.title}</h1>
          
          {#if recipe.image}
            <img src={recipe.image} alt={recipe.title} class="recipe-image"/>
          {/if}

          <div class="recipe-info">
            <div class="info-item">
              <span class="label">Servings:</span>
              <span class="value">{recipe.servings}</span>
            </div>
            <div class="info-item">
              <span class="label">Calories:</span>
              <span class="value">{recipe.calories} kcal</span>
            </div>
          </div>

          <div class="recipe-section">
            <h2>Ingredients</h2>
            <ul class="ingredients">
              {#each recipe.ingredients.split("|") as ingredient}
                <li>{ingredient}</li>
              {/each}
            </ul>
          </div>

          <div class="recipe-section">
            <h2>Instructions</h2>
            <ol class="instructions">
              {#each recipe.instructions.split("..") as instruction}
                <li>{instruction}</li>
              {/each}
            </ol>
          </div>

          {#if mealId}
            <button class="add-to-meal-button" on:click={addToMeal}>
              Add to Meal
            </button>
          {/if}
        </div>
      {:else}
        <div class="error">
          <h2>🔍 Recipe Not Found</h2>
          <p>Sorry, we couldn't find this recipe. Try searching again!</p>
        </div>
      {/if}
    </div>
  </div>

<style lang="scss">
  .recipe-detail {
    width: 100%;
  }

  .container {
    max-width: 800px;
    margin: 0 auto;
    padding: 0 2rem;
  }

  .back-button-container {
    margin-top: 1rem;
    margin-bottom: 1rem;
    margin-right: auto;
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
    padding-left: 0;
    border-radius: 15px;
    transition: background-color 0.2s;

    &:hover {
      background-color: rgba(145, 89, 59, 0.1);
    }

    svg {
      transform: none;
    }
  }

  .recipe-container {
    max-width: 800px;
    margin-top: 0;
    h1 {
      color: #91593B;
      text-align: center;
      margin: 1rem 0 2rem 0;
    }
  }

  .recipe-image {
    width: 100%;
    max-height: 400px;
    object-fit: cover;
    border-radius: 15px;
    margin-bottom: 2rem;
  }

  .recipe-info {
    display: flex;
    gap: 2rem;
    margin-bottom: 2rem;
    justify-content: center;
    
    .info-item {
      display: flex;
      gap: 0.5rem;
      align-items: center;
      
      .label {
        color: #91593B;
        font-weight: 500;
      }
      
      .value {
        color: #60361F;
      }
    }
  }

  .recipe-section {
    margin-bottom: 2rem;
    
    h2 {
      color: #91593B;
      font-size: 1.2rem;
      margin-bottom: 1rem;
    }

    .ingredients, .instructions {
      background: #DFD3CC;
      padding: 1.5rem;
      border-radius: 15px;
      color: #60361F;

      
      li {
        margin-bottom: 0.5rem;
        padding-left: 0.5rem;
        text-align: left;
        
        &:last-child {
          margin-bottom: 0;
        }
      }
    }

    .ingredients {
      list-style-type: disc;
      padding-left: 2.5rem;
    }

    .instructions {
      list-style-type: decimal;
      padding-left: 2.5rem;
    }
  }

  .add-to-meal-button {
    display: block;
    width: 100%;
    max-width: 200px;
    margin: 2rem auto;
    padding: 1rem;
    background-color: #6479AF;
    color: white;
    border: none;
    border-radius: 30px;
    font-size: 1rem;
    cursor: pointer;
    transition: background-color 0.2s;

    &:hover {
      background-color: #495880;
    }
  }
</style>
