<script lang="ts">
    export let params;
    import {onMount} from 'svelte';


    let recipeTitle = decodeURIComponent(params.title);
    let recipe: any = null;
    let loading = true;
    let errorMessage ='';

    onMount(async () => {
    if (params.title) {
      await getRecipeInfo(decodeURIComponent(params.title));
    }
  });

  async function getRecipeInfo(mealName: string) {
    try {
      loading = true;
      
    // Search for meal by name to get the meal ID
      const dbLookup = `https://www.themealdb.com/api/json/v1/1/search.php?s=${encodeURIComponent(mealName)}`;
      //console.log('DEBUG - Search URL:', searchUrl);
      
      const res = await fetch(dbLookup);
      const searchData = await res.json();
      
      if (!searchData.meals || searchData.meals.length === 0) {
        errorMessage = 'Recipe not found';
        return;
      }
      
      // Get the first matching meal's ID
      const mealId = searchData.meals[0].idMeal;
      const infoUrl = `https://www.themealdb.com/api/json/v1/1/lookup.php?i=${mealId}`;
      
      const infoRes = await fetch(infoUrl);
      const detailsData = await infoRes.json();
      
      console.log('DEBUG - Details API Response:', detailsData);
      
      if (detailsData.meals && detailsData.meals.length > 0) {
        const meal = detailsData.meals[0];
        
        recipe = {
          title: meal.strMeal,
          ingredients: formatMealDbIngredients(meal),
          instructions: meal.strInstructions,
          image: meal.strMealThumb,
          category: meal.strCategory,
          area: meal.strArea,
          youtube: meal.strYoutube,
          mealId: meal.idMeal
        };
        
      } else {
        errorMessage = 'Failed to fetch recipe details';
        console.log('DEBUG - No details found for meal ID:', mealId);
      }
      
    } catch (err) {
      errorMessage = 'Failed to load recipe details';
      console.error('Error fetching recipe:', err);
    } finally {
      loading = false;
    }
  }

  function formatMealDbIngredients(meal: any): string[] {
    const ingredients: string[] = [];

    for (let i = 1; i <= 20; i++) {
      const ingredient = meal[`strIngredient${i}`];
      const measure = meal[`strMeasure${i}`];

      if (ingredient && ingredient.trim()) {
        const formatted = measure && measure.trim()
          ? `${measure.trim()} ${ingredient.trim()}`
          : ingredient.trim();
        ingredients.push(formatted);
      }
    }
    return ingredients;
  }

  function goBack() {
    window.location.hash = "#/planner";
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
        <h2>Error!</h2>
      {:else if recipe}
        <article class="recipe">
          <header>
            <h1>{recipe.title}</h1>
              
          {#if recipe.image}
            <div class="foodPic">
              <img src={recipe.image} alt={recipe.title} loading="lazy" />
            </div>
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
                <div class="textInfo">
                  {recipe.instructions}
                </div>
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
