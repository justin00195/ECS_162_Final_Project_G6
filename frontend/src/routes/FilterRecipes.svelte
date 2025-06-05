<script lang="ts">
  import { RangeSlider } from 'svelte-range-slider-pips';
  import '../assets/filter.scss';
  import { calorieRange, selectedDiets, selectedMealTypes } from '../stores/filters';
  import { get } from 'svelte/store';
  
  let range = get(calorieRange);
  let diets = get(selectedDiets);
  let mealTypes = get(selectedMealTypes);

  const mealOptions = ['breakfast', 'lunch', 'dinner', 'dessert'];
  const dietOptions = ['vegan', 'vegetarian', 'glutenFree', 'dairyFree'];

  // Update stores when local variables change
  $: calorieRange.set(range);
  $: selectedDiets.set(diets);
  $: selectedMealTypes.set(mealTypes);

  function applyFilters() {
    // Update the stores with current values
    calorieRange.set(range);
    selectedDiets.set(diets);
    selectedMealTypes.set(mealTypes);
    
    window.location.hash = '#/planner/browse';
  }

  function goBack() {
    window.location.hash = "#/planner/browse";
  }
</script>

<button on:click={goBack} class="back-button"> ← </button>

<!-- Meal Type -->
<h2>Meal Type</h2>
{#each mealOptions as meal}
  <label>
    <input type="checkbox" bind:group={mealTypes} value={meal} />
    {meal}
  </label>
{/each}

<!-- Dietary Preferences -->
<h2>Dietary Preferences</h2>
{#each dietOptions as tag}
  <label>
    <input type="checkbox" bind:group={diets} value={tag} />
    {tag}
  </label>
{/each}

<!-- Calories -->
<div class="container">
  <h2>Calories per Serving</h2>
  <RangeSlider
    bind:values={range}
    min={0}
    max={1500}
    pips
    hoverable
    float
    class="calories-slider"
  />
  <p class="selected-range">{range[0]} - {range[1]} Calories / Serving</p>
</div>

<!-- Submit -->
<button on:click={applyFilters}>Apply Filters</button>