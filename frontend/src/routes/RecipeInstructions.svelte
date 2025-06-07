<script lang="ts">
    export let params;
    import {onMount} from 'svelte';
    import {selectedRecipe,selectedServings} from '../stores/recipe';
    import {get} from 'svelte/store';

    let recipeTitle = decodeURIComponent(params.title);
    let recipe: any = null;
    let loading = false;
    let errorMessage ='';

    /*onMount(async () => {
    if (params.title) {
      await getRecipeInfo(decodeURIComponent(recipeTitle));
    }
  })*/
    onMount(()=>{
      const meal = get(selectedRecipe);
      if(!meal){
        errorMessage = 'Recipe Not Found BUGGGGGG'
        return;
      }

      recipe = {
          title: meal.title,
          ingredients: formatIngredients(meal),
          instructions: formatInstructions(meal),
          servings: meal.servings,
          image: meal.image
        };
        loading = false;
        selectedServings.set(meal.servings)
    });

    
  function formatIngredients(meal: any): string[] {
    return meal.ingredients.split("|");
  }

  function formatInstructions(meal: any): string[] {
    return meal.instructions.split(".").map((s: string) => s.trim()).filter(Boolean);

  }

  async function getRecipeInfo(mealName: string) {
    try {
      loading = true;
      
    // Search for meal by name to get the meal ID
      //const dbLookup = `https://www.themealdb.com/api/json/v1/1/search.php?s=${encodeURIComponent(mealName)}`;
      //console.log('DEBUG - Search URL:', searchUrl);
      
      //const res = await fetch(dbLookup);
      //const searchData = await res.json();
      console.log(mealName)
      const res = await fetch(`http://localhost:8000/api/recipe?query=${encodeURIComponent(mealName)}`, {
          method: 'GET',
          credentials: 'include'
    
      });
      const searchData = await res.json();
      
      if (!searchData.items || searchData.items.length === 0) {
        errorMessage = 'Recipe not found';
        console.log(searchData.items)
        console.log(searchData.items.length)
        return;
      }
      
       const meal = searchData.items[0];
        
        recipe = {
          title: meal.title,
          ingredients: formatIngredients(meal),
          instructions: formatInstructions(meal),
          servings: meal.servings,
          image: meal.image
        };
      
    } catch (error) {
      errorMessage = 'Failed to load recipe details';
      console.error('Error fetching recipe:', error);
    } finally {
      loading = false;
    }
  }


  function goBack() {
    selectedRecipe.set(null)
    window.location.hash = "#/planner/browse";
  }

</script>

<div class="recipe-detail">
    <div class="container">
      <button on:click={goBack} class="back-button">
        ← Back to Search
      </button>
  
      {#if loading}
        <div class="loading">
          <h2>🍳</h2>
          <p>Loading your delicious recipe...</p>
        </div>
      {:else if errorMessage}
        <h2>{errorMessage}</h2>
      {:else if recipe}
        <article class="recipe">
          <h1>{recipe.title}</h1>

          {#if recipe.image}
            <img src={recipe.image} alt={recipe.title} loading="lazy" />
          {/if}

          {#if recipe.servings}
            <p>Makes {recipe.servings} servings</p>
            {/if}
  
          <div class="content">
            <section class="ingredients">
              <h2>
                Ingredients
              </h2>
              {#if recipe.ingredients}
                <ul class="ingredients-list">
                  {#each recipe.ingredients as ingredient}
                    <li class="ingredientList">{ingredient}</li>
                  {/each}
                </ul>
              {:else}
                <div class="no-data">
                  <p>No ingredients list available for this recipe</p>
                </div>
              {/if}
            </section>
  
            <section class="instructions">
              <h2>Instructions</h2>
              {#if recipe.instructions}
                {#each recipe.instructions as step}
                  <p>{step}.</p>
                {/each}
              {:else}
                <div class="no-data">
                  <p>No cooking instructions available for this recipe</p>
                </div>
              {/if}
            </section>
          </div>
        </article>
      {:else}
        <div class="error">
          <h2>🔍 Recipe Not Found</h2>
          <p>Sorry, we couldn't find this recipe. Try searching again!</p>
        </div>
      {/if}
    </div>
  </div>
