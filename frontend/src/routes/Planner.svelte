  function browseMealRecipes(mealId: number) {
    window.location.hash = `#/browse?meal=${mealId}&from=planner`;
  } 