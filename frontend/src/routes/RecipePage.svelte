<script lang="ts">
    import { onMount } from 'svelte';
    //https://www.npmjs.com/package/svelte-spa-router
    let recipes: Array<{ name: string; calories: number }> = [];
  
    onMount(async () => {
      const res = await fetch('http://localhost:8000/recipes');
      const data = await res.json();
      recipes = data.recipes;
    });
  </script>
  
  <h1>Recipe Page</h1>
  <ul>

  </ul>
  