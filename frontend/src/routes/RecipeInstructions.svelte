<script lang="ts">
    export let params;
    import {onMount} from 'svelte';
    import {selectedRecipe} from '../stores/recipe';
    import type { Recipe } from '../stores/recipe';
    import {get} from 'svelte/store';
    import { selectedMeal } from '../stores/meal';
    import type { Meal } from '../stores/meal';


    let recipeTitle = decodeURIComponent(params.title);
    let recipe = get(selectedRecipe);
    let loading = false;
    let errorMessage ='';
    let mealId: number | null = null;

    /*onMount(async () => {
    if (params.title) {
      await getRecipeInfo(decodeURIComponent(recipeTitle));
    }
  })*/
    onMount(()=>{
      if(!recipe){
        errorMessage = 'Recipe Not Found BUGGGGGG'
        return;
      }

      loading = false;

    });

    onMount(async () => {
      // Get meal ID from URL and convert to number
      const urlParams = new URLSearchParams(window.location.hash.split('?')[1] || '');
      const mealIdParam = urlParams.get('meal');
      mealId = mealIdParam ? parseInt(mealIdParam, 10) : null;
      console.log('URL params:', { hash: window.location.hash, mealId }); // Debug log

      // Subscribe to recipe store
      selectedRecipe.subscribe(value => {
        recipe = value;
        console.log('Recipe updated:', recipe); // Debug log
      });
    });

  function formatIngredients(meal: any): string[] {
    // if (typeof meal.ingredients === 'string') {
    //   // Split by pipe character and trim each ingredient
    //   return meal.ingredients.split('|').map((s: string) => s.trim()).filter(Boolean);
    // }
    // return meal.ingredients; // Return as is if it's already an array
    console.log(meal.ingredients.split("|"))
    return meal.ingredients.split("|");
  }

  function formatInstructions(meal: any): string[] {
    // if (typeof meal.instructions === 'string') {
    //   // Split by single period and trim each instruction
    //   return meal.instructions.split('.')
    //     .map((s: string) => s.trim())
    //     .filter(Boolean)
    //     .map((s: string) => s + '.');
    // }
    // return meal.instructions; // Return as is if it's already an array
    console.log(meal.instructions.split("."))
    return meal.instructions.split(".").map((s: string) => s.trim()).filter(Boolean);
  }


  function goBack() {
    selectedRecipe.set(null);
    // Keep the meal ID when going back
    const urlParams = new URLSearchParams(window.location.hash.split('?')[1] || '');
    const mealId = urlParams.get('meal');
    if (mealId) {
      window.location.hash = `#/planner/browse?meal=${mealId}`;
    } else {
      window.location.hash = "#/planner/browse";
    }
  }

  // If we somehow got here without a recipe (e.g., direct URL access),
  // redirect back to browse page
  if (!recipe) {
    window.location.hash = '/planner/browse';
  }

  // Ensure calories exists, default to 0 if not present
  if (recipe && !recipe.calories) {
    recipe = {
      ...recipe,
      calories: 0
    } as Recipe;
  }

  async function addToMeal() {
    if (!recipe || !mealId) {
      console.log('Missing recipe or mealId:', { recipe, mealId }); // Debug log
      return;
    }


    
    try {
      // First get current meal to append to ingredients
      const getResponse = await fetch(`http://localhost:8000/api/meal/${mealId}`, {
        credentials: 'include'
      });

      if (!getResponse.ok) {
        throw new Error('Failed to fetch meal');
      }

      const mealData = await getResponse.json();
      const currentIngredients = mealData.ingredients || [];
      console.log(mealData)
      
      // Now update with appended ingredient
      const response = await fetch(`http://localhost:8000/api/meal/${mealId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify({
          ingredients: [...currentIngredients, recipe.title]
        })
      });

      if (!response.ok) {
        throw new Error('Failed to add recipe to meal');
      }

      // Navigate back to planner on success
      window.location.hash = '#/planner';
    } catch (error) {
      console.error('Failed to add recipe to meal:', error);
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
