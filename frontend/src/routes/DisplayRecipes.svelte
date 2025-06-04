<script lang="ts">
	import { favoriteMap, toggleFavorite } from '../stores/favorites';
  import '../assets/displayRecipes.scss';
	import {selectedRecipe} from '../stores/recipe'
  export let category: string;
  export let results: any[];

  function viewRecipe(title: string) {
    window.location.hash = `#/recipe/${encodeURIComponent(recipe.title)}`;
  }
  function tempRecipeInfo(recipe: any){
    selectedRecipe.set(recipe);
	console.log(selectedRecipe)
    window.location.hash = `#/recipe/${encodeURIComponent(recipe.title)}`
  }

</script>

<div class="container">
	<h2>{category}</h2>
	<ul class="results-list">
		{#each results as result}
			<li class="result">
				<button on:click={() => tempRecipeInfo(result)}>
					{result.title}
				</button>
				<button on:click={() => {toggleFavorite(result.title)}} class="heart-btn">
					<img
						src={$favoriteMap[result.title] ? './solid-heart.png' : './empty-heart.png'}
						alt="heart icon"
						class="heart-icon"
					/>
				</button>
			</li>
		{/each}
	</ul>
</div>