<script lang="ts">
    import { onMount } from 'svelte';
  
    let plan: any = {};
  
    onMount(async () => {
      const res = await fetch('http://localhost:5000/plan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ })
      });
  </script>
  
  <h1>Planner Page</h1>
  <pre>{JSON.stringify(plan, null, 2)}</pre>
  