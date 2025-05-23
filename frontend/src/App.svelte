<script lang="ts">
  import { onMount } from 'svelte';
  import Router from 'svelte-spa-router';
  import Home from './routes/Homepage.svelte';
  import LoginPage from './routes/LoginPage.svelte';
  import CalculatorPage from './routes/CalculatorPage.svelte';
  import GoalPage from './routes/GoalPage.svelte';
  import PlannerPage from './routes/PlannerPage.svelte';
  import ReportPage from './routes/ReportPage.svelte';
  import RecipePage from './routes/RecipePage.svelte';

  let currentPage = 'login';

  const routes = {
    '/': Home
  };
</script>

<Router {routes} />


<main>

<nav>
  <button on:click={() => currentPage = 'login'}>Login</button>
  <button on:click={() => currentPage = 'calculator'}>Calculator</button>
  <button on:click={() => currentPage = 'goal'}>Goal</button>
  <button on:click={() => currentPage = 'planner'}>Planner</button>
  <button on:click={() => currentPage = 'report'}>Report</button>
  <button on:click={() => currentPage = 'recipe'}>Recipe</button>
</nav>


{#if currentPage === 'login'}
  <LoginPage />
{:else if currentPage === 'calculator'}
  <CalculatorPage />
{:else if currentPage === 'goal'}
  <GoalPage />
{:else if currentPage === 'planner'}
  <PlannerPage />
{:else if currentPage === 'report'}
  <ReportPage />
{:else if currentPage === 'recipe'}
  <RecipePage />
{/if}
</main>
