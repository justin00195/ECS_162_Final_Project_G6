<script lang="ts">
  import { onMount } from 'svelte';
  import { selectedRecipe } from '../stores/recipe';
  import { selectedMeal } from '../stores/meal';
  import type { Meal } from '../stores/meal';

  interface Recipe {
    id?: number;
    title: string;
    calories: number;
    image: string;
    ingredients: string;
    instructions: string;
    servings: string;
  }

  let recipe: Recipe | null = null;
  let meal: Meal | null = null;

  onMount(async () => {
    // Get meal ID from URL
    const urlParams = new URLSearchParams(window.location.hash.split('?')[1] || '');
    const mealId = urlParams.get('meal');
    console.log('URL params:', { hash: window.location.hash, mealId }); // Debug log

    // Subscribe to recipe store
    selectedRecipe.subscribe(value => {
      recipe = value;
      console.log('Recipe updated:', recipe); // Debug log
    });

    // If we have a meal ID, fetch the meal data
    if (mealId) {
      try {
        const response = await fetch(`http://localhost:8000/api/meal/${mealId}`, {
          credentials: 'include'
        });
        if (!response.ok) {
          throw new Error('Failed to fetch meal');
        }
        const mealData = await response.json();
        console.log('Fetched meal:', mealData); // Debug log
        selectedMeal.set(mealData);
        meal = mealData;
      } catch (error) {
        console.error('Failed to fetch meal:', error);
        selectedMeal.set(null);
        meal = null;
      }
    }

    // Subscribe to meal store for any updates
    selectedMeal.subscribe(value => {
      meal = value;
      console.log('Meal updated:', meal); // Debug log
    });
  });

  async function addToMeal() {
    if (!recipe || !meal) {
      console.log('Missing recipe or meal:', { recipe, meal }); // Debug log
      return;
    }

    try {
      const response = await fetch('http://localhost:8000/api/meal/add', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify({
          mealId: meal.id,
          recipe: recipe.title
        })
      });

      if (!response.ok) {
        throw new Error('Failed to add recipe to meal');
      }

      // Navigate back to planner
      window.location.hash = '#/planner';
    } catch (error) {
      console.error('Failed to add recipe to meal:', error);
    }
  }
</script>

<div class="recipe-container">
  <div class="back-button-container">
    <button class="back-button" on:click={() => window.history.back()}>
      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M19 12H5"/>
        <path d="M12 19l-7-7 7-7"/>
      </svg>
      Back
    </button>
  </div>

  {#if recipe}
    <div class="recipe-content">
      <h1>{recipe.title}</h1>
      <div class="recipe-details">
        <img src={recipe.image} alt={recipe.title} class="recipe-image" />
        <div class="recipe-info">
          <p><strong>Calories:</strong> {recipe.calories}</p>
          <p><strong>Servings:</strong> {recipe.servings}</p>
        </div>
      </div>

      <div class="recipe-section">
        <h2>Ingredients</h2>
        <p>{recipe.ingredients}</p>
      </div>

      <div class="recipe-section">
        <h2>Instructions</h2>
        <p>{recipe.instructions}</p>
      </div>

      {#if meal}
        <button class="add-to-meal-button" on:click={addToMeal}>
          Add to {meal.name}
        </button>
      {/if}
    </div>
  {:else}
    <p>Recipe not found</p>
  {/if}
</div>

<style lang="scss">
  .recipe-container {
    max-width: 1000px;
    margin: 0 auto;
    padding: 2rem;
    position: relative;
  }

  .back-button-container {
    position: absolute;
    top: 2rem;
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

    &:hover {
      background-color: rgba(145, 89, 59, 0.1);
    }
  }

  .recipe-content {
    h1 {
      color: #91593B;
      text-align: center;
      margin-bottom: 2rem;
    }
  }

  .recipe-details {
    display: flex;
    gap: 2rem;
    margin-bottom: 2rem;
  }

  .recipe-image {
    width: 300px;
    height: 300px;
    object-fit: cover;
    border-radius: 15px;
  }

  .recipe-info {
    flex: 1;
    p {
      margin: 0.5rem 0;
      color: #60361F;
    }
  }

  .recipe-section {
    margin-bottom: 2rem;

    h2 {
      color: #91593B;
      margin-bottom: 1rem;
    }

    p {
      color: #60361F;
      line-height: 1.6;
      white-space: pre-wrap;
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