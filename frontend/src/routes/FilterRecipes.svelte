<script lang="ts">
  import { RangeSlider } from 'svelte-range-slider-pips';
  import '../assets/filter.scss';
  import { calorieRange, selectedDiets, selectedMealTypes } from '../stores/filters';
  import { get } from 'svelte/store';
  
  let range = get(calorieRange);
  let diets = get(selectedDiets);
  let mealTypes = get(selectedMealTypes);
  let activeTab = 'all'; // 'all' or 'favorites'

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
    
    // Preserve meal ID and from parameter when going back
    const urlParams = new URLSearchParams(window.location.hash.split('?')[1] || '');
    const mealId = urlParams.get('meal');
    const fromPlanner = urlParams.get('from');
    
    let browseUrl = '#/planner/browse';
    const params = new URLSearchParams();
    
    if (mealId) params.append('meal', mealId);
    if (fromPlanner) params.append('from', fromPlanner);
    if (params.toString()) browseUrl += '?' + params.toString();
    
    window.location.hash = browseUrl;
  }

  function goBack() {
    // Also preserve parameters when going back
    const urlParams = new URLSearchParams(window.location.hash.split('?')[1] || '');
    const mealId = urlParams.get('meal');
    const fromPlanner = urlParams.get('from');
    
    let browseUrl = '#/planner/browse';
    const params = new URLSearchParams();
    
    if (mealId) params.append('meal', mealId);
    if (fromPlanner) params.append('from', fromPlanner);
    if (params.toString()) browseUrl += '?' + params.toString();
    
    window.location.hash = browseUrl;
  }
</script>

<div class="filter-container">
  <div class="tabs">
    <button 
      class="tab-btn" 
      class:active={activeTab === 'all'} 
      on:click={() => activeTab = 'all'}
    >
      All Recipes
    </button>
    <button 
      class="tab-btn" 
      class:active={activeTab === 'favorites'} 
      on:click={() => activeTab = 'favorites'}
    >
      Favorites
    </button>
  </div>

  <div class="filter-section">
    <h2>Calories Per Serving</h2>
    <div class="slider-container">
      <RangeSlider
        bind:values={range}
        min={0}
        max={1500}
        pips
        hoverable
        float
        class="calories-slider"
      />
      <p class="range-values">{range[0]} - {range[1]} Calories</p>
    </div>

    <div class="options-grid">
      <div class="option-section">
        <h2>Meal Type</h2>
        <div class="checkbox-grid">
          {#each mealOptions as meal}
            <label class="checkbox-label">
              <input type="checkbox" bind:group={mealTypes} value={meal}>
              <span class="checkbox-text">{meal}</span>
            </label>
          {/each}
        </div>
      </div>

      <div class="option-section">
        <h2>Dietary Preferences</h2>
        <div class="checkbox-grid">
          {#each dietOptions as diet}
            <label class="checkbox-label">
              <input type="checkbox" bind:group={diets} value={diet}>
              <span class="checkbox-text">{diet}</span>
            </label>
          {/each}
        </div>
      </div>
    </div>
  </div>

  <button class="find-recipes-btn" on:click={applyFilters}>Apply Filters</button>
</div>

<style lang="scss">
  .filter-container {
    max-width: 800px;
    margin: 2rem auto;
    padding: 2rem;
    background: white;
    border-radius: 15px;
    display: flex;
    flex-direction: column;
    gap: 2rem;
  }

  .tabs {
    display: flex;
    gap: 1rem;
    margin-bottom: 1rem;
  }

  .tab-btn {
    padding: 0.5rem 1.5rem;
    border: none;
    border-radius: 20px;
    background: #EDEAE8;
    color: #6479AF;
    cursor: pointer;
    font-size: 1rem;
    transition: all 0.2s;

    &.active {
      background: #6479AF;
      color: white;
    }

    &:hover:not(.active) {
      background: #e1e7f6;
    }
  }

  .filter-section {
    h2 {
      color: #91593B;
      font-size: 1.2rem;
      margin-bottom: 1rem;
    }
  }

  .slider-container {
    margin-bottom: 2rem;

    :global(.calories-slider) {
      margin: 2rem 0;
    }

    .range-values {
      text-align: center;
      color: #91593B;
      font-weight: 500;
    }
  }

  .options-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2rem;
  }

  .checkbox-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.75rem;
  }

  .checkbox-label {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: #91593B;
    font-size: 0.9rem;

    input[type="checkbox"] {
      width: 16px;
      height: 16px;
      accent-color: #91593B;
    }

    .checkbox-text {
      text-transform: capitalize;
    }
  }

  .find-recipes-btn {
    background-color: #6479AF;
    color: white;
    border: none;
    padding: 0.75rem 2rem;
    border-radius: 30px;
    font-size: 1rem;
    cursor: pointer;
    align-self: center;
    transition: background-color 0.2s;

    &:hover {
      background-color: #495880;
    }
  }

  :global(.calories-slider) {
    --range-handle: #91593B;
    --range-handle-focus: #6b3410;
    --range-track: #DFD3CC;
    --range-track-active: #91593B;
    --range-value: #91593B;
    --range-value-text: white;
  }
</style>