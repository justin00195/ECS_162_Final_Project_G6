<script lang="ts">
    import { onMount } from "svelte";

    let mealsContainer: HTMLElement;
    let meals: { id: number, name: string, ingredients: string[] }[] = [];
    let nextMealId = 0;
    let searchResults: { [key: number]: any[] } = {};
    let searchQuery: { [key: number]: string } = {};
    let isLoading: { [key: number]: boolean } = {};
    let showDropdown: { [key: number]: boolean } = {};

    async function loadMeals() {
        try {
            const response = await fetch('http://localhost:8000/api/meal', {
                credentials: 'include'
            });
            
            if (!response.ok) {
                throw new Error('Failed to load meals');
            }
            
            const data = await response.json();
            // Sort meals by ID to ensure ascending order
            meals = data.meals.sort((a: { id: number }, b: { id: number }) => a.id - b.id);
            
            // Update nextMealId to be greater than any existing meal ID
            const maxId = meals.length > 0 ? Math.max(...meals.map(m => m.id)) : 0;
            nextMealId = maxId + 1;
        } catch (error) {
            console.error('Error loading meals:', error);
        }
    }

    async function getCaloriesFromNinja(query: string): Promise<number | null> {
    try {
      const res = await fetch('http://localhost:8000/report', {
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
      console.error('Error to get receipt calories:', err);
      return null;
    }
  }

    async function searchIngredients(mealId: number, query: string) {
        if (!query.trim()) {
            searchResults[mealId] = [];
            showDropdown[mealId] = false;
            return;
        }

        isLoading[mealId] = true;
        showDropdown[mealId] = true;
        
        try {
            const response = await fetch(
                `http://localhost:8000/api/food/search?query=${encodeURIComponent(query)}&pageSize=3`,
                {
                    credentials: 'include'
                }
            );
            
            if (!response.ok) {
                throw new Error('Failed to fetch ingredients');
            }
            
            const data = await response.json();
            searchResults[mealId] = data.foods || [];
        } catch (error) {
            console.error('Error searching ingredients:', error);
            searchResults[mealId] = [];
        } finally {
            isLoading[mealId] = false;
        }
    }

    async function addMeal() {
        const newMealName = `Meal ${meals.length + 1}`;
        
        try {
            const response = await fetch('http://localhost:8000/api/meal', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'include',
                body: JSON.stringify({
                    name: newMealName
                })
            });

            if (!response.ok) {
                throw new Error('Failed to add meal to database');
            }

            const data = await response.json();
            // Only update UI if database operation was successful
            const newMeal = { 
                id: data.meal_id, 
                name: newMealName, 
                ingredients: [] 
            };
            meals = [...meals, newMeal];  // Add to end of array
            searchResults[data.meal_id] = [];
            searchQuery[data.meal_id] = '';
            isLoading[data.meal_id] = false;
            showDropdown[data.meal_id] = false;
            
            // Wait for DOM update before scrolling
            setTimeout(() => {
                mealsContainer?.scrollTo({
                    top: mealsContainer.scrollHeight,
                    behavior: 'smooth'
                });
            }, 0);
        } catch (error) {
            console.error('Error adding meal:', error);
        }
    }

    async function deleteMeal(mealId: number) {
        try {
            const response = await fetch(`http://localhost:8000/api/meal/${mealId}`, {
                method: 'DELETE',
                credentials: 'include'
            });

            if (!response.ok) {
                throw new Error('Failed to delete meal');
            }

            // Only update UI if delete was successful
            meals = meals.filter(meal => meal.id !== mealId);
            delete searchResults[mealId];
            delete searchQuery[mealId];
            delete isLoading[mealId];
            delete showDropdown[mealId];
        } catch (error) {
            console.error('Error deleting meal:', error);
        }
    }

    async function updateMeal(mealId: number, updateData: { name?: string, ingredients?: string[] }) {
        try {
            const response = await fetch(`http://localhost:8000/api/meal/${mealId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'include',
                body: JSON.stringify(updateData)
            });

            if (!response.ok) {
                throw new Error('Failed to update meal');
            }
        } catch (error) {
            console.error('Error updating meal:', error);
        }
    }

    function renameMeal(mealId: number, newName: string) {
        meals = meals.map(meal => {
            if (meal.id === mealId) {
                return { ...meal, name: newName };
            }
            return meal;
        });
        updateMeal(mealId, { name: newName });
    }

    function addIngredient(mealId: number, ingredientName: string) {
        if (!ingredientName.trim()) return;
        
        const updatedMeals = meals.map(meal => {
            if (meal.id === mealId) {
                const updatedMeal = {
                    ...meal,
                    ingredients: [...meal.ingredients, ingredientName.trim()]
                };
                // Update in database
                updateMeal(mealId, { ingredients: updatedMeal.ingredients });
                return updatedMeal;
            }
            return meal;
        });
        
        meals = updatedMeals;
        // Clear search after adding
        searchQuery[mealId] = '';
        searchResults[mealId] = [];
        showDropdown[mealId] = false;
    }

    function removeIngredient(mealId: number, index: number) {
        meals = meals.map(meal => {
            if (meal.id === mealId) {
                const newIngredients = [...meal.ingredients];
                newIngredients.splice(index, 1);
                // Update in database
                updateMeal(mealId, { ingredients: newIngredients });
                return {
                    ...meal,
                    ingredients: newIngredients
                };
            }
            return meal;
        });
    }

    function handleSearchInput(mealId: number, event: Event) {
        const input = event.target as HTMLInputElement;
        searchQuery[mealId] = input.value;
        searchIngredients(mealId, input.value);
    }

    function handleIngredientClick(mealId: number, ingredientName: string) {
        addIngredient(mealId, ingredientName);
    }

    function handleClickOutside(mealId: number) {
        setTimeout(() => {
            showDropdown[mealId] = false;
        }, 200);
    }

    function browseMealRecipes(mealId: number) {
        window.location.hash = `#/planner/browse?meal=${mealId}&from=planner`;
    }

    function handleRenameKeydown(mealId: number, event: KeyboardEvent & { currentTarget: HTMLInputElement }) {
        if (event.key === 'Enter') {
            const input = event.currentTarget;
            if (input.value.trim()) {
                renameMeal(mealId, input.value.trim());
            }
            input.blur();
        } else if (event.key === 'Escape') {
            event.currentTarget.blur();
        }
    }

    function handleRenameBlur(mealId: number, event: FocusEvent & { currentTarget: HTMLInputElement }) {
        const input = event.currentTarget;
        if (input.value.trim()) {
            renameMeal(mealId, input.value.trim());
        }
    }

    onMount(async () => {
        await loadMeals();
    });
</script>

<div class="planner-container">
    <h1>Meal Planner</h1>
    
    <div class="meals-section" bind:this={mealsContainer}>
        {#each meals as meal (meal.id)}
            <div class="meal-container">
                <div class="meal-header">
                    <div class="title-section">
                        <input 
                            type="text"
                            class="meal-title"
                            value={meal.name}
                            on:keydown={(e) => handleRenameKeydown(meal.id, e)}
                            on:blur={(e) => handleRenameBlur(meal.id, e)}
                        />
                    </div>
                    <button class="delete-btn" on:click={() => deleteMeal(meal.id)}>
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M3 6h18"></path>
                            <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"></path>
                            <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"></path>
                        </svg>
                    </button>
                </div>
                <div class="ingredients-section">
                    <div class="search-container">
                        <div class="search-input-container">
                            <svg class="search-icon" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <circle cx="11" cy="11" r="8"></circle>
                                <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                            </svg>
                            <input
                                type="text"
                                placeholder="Search ingredients..."
                                value={searchQuery[meal.id] || ''}
                                on:input={(e) => handleSearchInput(meal.id, e)}
                                on:blur={() => handleClickOutside(meal.id)}
                            />
                        </div>
                        {#if showDropdown[meal.id] && (searchResults[meal.id]?.length > 0 || isLoading[meal.id])}
                            <div class="search-results">
                                {#if isLoading[meal.id]}
                                    <div class="loading">Searching...</div>
                                {:else}
                                    {#each searchResults[meal.id] as result}
                                        <div 
                                            class="result-item"
                                            on:mousedown={() => handleIngredientClick(meal.id, result.name)}
                                        >
                                            <div class="result-name">{result.name}</div>
                                            {#if result.category}
                                                <div class="result-category">{result.category}</div>
                                            {/if}
                                        </div>
                                    {/each}
                                {/if}
                            </div>
                        {/if}
                    </div>
                    <button class="browse-btn" on:click={() => browseMealRecipes(meal.id)}>
                        Browse Recipes
                    </button>
                </div>
                {#if meal.ingredients.length > 0}
                    <ul class="ingredients-list">
                        {#each meal.ingredients as ingredient, i}
                            <li>
                                <span class="ingredient-text">{ingredient}</span>
                                <button class="remove-btn" on:click={() => removeIngredient(meal.id, i)}>×</button>
                            </li>
                        {/each}
                    </ul>
                {/if}
            </div>
        {/each}
    </div>

    <button class="add-meal-btn" on:click={addMeal}>
        <img src="../public/add-icon.svg" alt="plus sign" width="30px" height="30px">
        Add Meal
    </button>
</div>

<style lang="scss">
    .planner-container {
        max-width: 1000px;
        margin: 0 auto;
        padding: 0 2rem;
        height: 60vh;
        display: flex;
        flex-direction: column;
        align-items: center;

        h1 {
            color: #91593B;
            text-align: center;
            margin: 1rem 0 2rem 0;
            padding-top: 1rem;
            flex-shrink: 0;
        }
    }

    .meals-section {
        flex: 1;
        overflow-y: auto;
        width: 100%;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
    }

    .meal-container {
        background: #DFD3CC;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        position: relative;

        &:last-child {
            margin-bottom: 0;
        }
    }

    .meal-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }

    .title-section {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        input { 
            color: #91593B;
            font-weight: 400;
        }
    }

    .meal-title {
        color: #8B4513;
        font-size: 1.5rem;
        font-weight: bold;
        background: none;
        border: none;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        margin: 0;

        &:hover {
            background: rgba(139, 69, 19, 0.1);
        }

        &:focus {
            background: white;
            outline: 2px solid #8B4513;
        }
    }

    .ingredients-section {
        display: flex;
        align-items: flex-start;
        gap: 1rem;
        padding: 1rem;
        // border: 1px solid #ddd;
        border-radius: 15px;
        margin-bottom: 1rem;
    }

    .search-container {
        flex: 1;
        position: relative;
    }

    .search-input-container {
        width: 100%;
        margin-top: -10px;

        .search-icon {
            position: absolute;
            left: 10px;
            top: 50%;
            transform: translateY(-50%);
            color: #8B4513;
            pointer-events: none;
        }

        input {
            width: 94%;
            padding: 0.5rem 0.5rem 0.5rem 2rem;
            border: 1px solid #ddd;
            border-radius: 15px;
            font-size: 1rem;

            &:focus {
                outline: none;
                border-color: #8B4513;
            }
        }
    }

    .search-results {
        position: absolute;
        top: 100%;
        left: 0;
        right: 0;
        background: white;
        border-radius: 5px 5px 5px 5px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        z-index: 10;
        max-height: 200px;
        overflow-y: auto;

        .loading {
            padding: 0.5rem;
            text-align: center;
            color: #666;
        }

        .result-item {
            padding: 0.75rem;
            cursor: pointer;
            border-bottom: 1px solid #eee;

            &:last-child {
                border-bottom: none;
            }

            &:hover {
                background: #f5f5f5;
            }

            .result-name {
                font-weight: 500;
                margin-bottom: 0.25rem;
            }

            .result-category {
                font-size: 0.8rem;
                color: #666;
            }
        }
    }

    .delete-btn {
        background: none;
        border: none;
        padding: 0.5rem;
        cursor: pointer;
        color: #932b2b;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 5px;
        transition: background-color 0.2s;

        svg {
            width: 20px;
            height: 20px;
        }
    }

    .ingredients-list {
        list-style: disc;
        list-style-position: inside;
        padding: 8px;
        border-radius: 15px;
        background: #EDEAE8;
        position: relative;

        li {
            position: relative;
            padding-right: 2.5rem; //space for the remove button
            margin-bottom: 0.5rem;
            color: #91593B;
            line-height: 1.5;
        }

        .ingredient-text {
            display: inline-block;
            max-width: 90%; // prevents overlapping with the button
        }

        .remove-btn {
            position: absolute;
            right: 0.5rem;
            top: 50%;
            transform: translateY(-50%);
            background: none;
            border: none;
            color: #91593B;
            cursor: pointer;
            font-size: 1.2rem;
            padding: 0;

            &:hover {
                color: #5a3725;
            }
        }
    }


    .browse-btn {
        background-color: #8B4513;
        color: white;
        border: none;
        padding: 0.1rem 1rem;
        border-radius: 15px;
        cursor: pointer;
        font-size: 1rem;
        min-width: 150px;
        height: 33px;
        white-space: nowrap;

        &:hover {
            background-color: #6b3410;
        }
    }

    .add-meal-btn {
        background-color: #6479AF;
        color: white;
        border: none;
        padding: 1rem 1rem;
        border-radius: 30px;
        cursor: pointer;
        font-size: 1.5rem;
        width: 20%;
        margin-top: 1rem;
        transition: background-color 0.2s;
        flex-shrink: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;

        &:hover {
            background-color: #495880;
        }
    }
</style>