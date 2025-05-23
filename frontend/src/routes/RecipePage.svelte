<script lang="ts">
    import { onMount } from 'svelte';
  
    let recipes: Array<{ name: string; calories: number }> = [];
  
    onMount(async () => {
      const res = await fetch('http://localhost:5000/recipes');
      const data = await res.json();
      recipes = data.recipes;
    });
  </script>
  
  <h1>Recipe Page</h1>
  <ul>

  </ul>
  