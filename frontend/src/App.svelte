<script lang="ts">
  import { onMount } from 'svelte';
  import Router from 'svelte-spa-router';
  import Home from './routes/Homepage.svelte';




  const routes = {
    '/': Home
  };
</script>

<Router {routes} />


<main>


</main>
