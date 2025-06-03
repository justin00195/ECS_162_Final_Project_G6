<script lang="ts">
	import { favoriteMap, toggleFavorite } from '../stores/favorites';
  import '../assets/displayRecipes.scss';

  export let category: string;
  export let results: string[];

  function viewRecipe(title: string) {
    window.location.hash = `#/recipe/${encodeURIComponent(title)}`;
  }

</script>

<div class="container">
	<h2>{category}</h2>
	<ul class="results-list">
		{#each results as result}
			<li class="result">
				<button on:click={() => viewRecipe(result)}>
					{result}
				</button>
				<button on:click={() => {toggleFavorite(result)}} class="heart-btn">
					<img
						src={$favoriteMap[result] ? './solid-heart.png' : './empty-heart.png'}
						alt="heart icon"
						class="heart-icon"
					/>
				</button>
			</li>
		{/each}
	</ul>
</div>