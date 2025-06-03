<script lang="ts">
    import { link } from 'svelte-spa-router';
    import '/src/assets/hp.scss'
    import CalculatorPage from './CalculatorPage.svelte';
    import GoalPage from './GoalPage.svelte';
    import PlannerPage from './PlannerPage.svelte';
    import ReportPage from './ReportPage.svelte';
    import RecipePage from './RecipePage.svelte';
    import { onMount } from 'svelte';
    import UserPortal from './UserPortal.svelte';

    let currentPage = 'home';
    let isLoggedIn = false;
    let userInfo = {};
    let loading = true;

onMount(async () => {
  try {
    const userRes = await fetch('http://localhost:8000/auth/user', {
      credentials: 'include'
    });
    const datap = await userRes.json();
    console.log(userRes.status, datap);

    if (userRes.status === 200) {
      console.log("User is logged in");
      isLoggedIn = true;
      userInfo = {...datap};
    } else {
      console.log("User is not logged in");
      isLoggedIn = false;
    }
  } catch (error) {
    console.error('Failed to fetch user info:', error);
  } finally {
    loading = false;
  }
});

    //https://developers.google.com/identity/protocols/oauth2/javascript-implicit-flow
function redirectToDexLogin() {
  const clientId = 'flask-app';
  const redirectUri = 'http://localhost:8000/auth/callback';
  const responseType = 'code';
  const scope = 'openid email';
  const dexUrl = `http://localhost:5556/auth?client_id=${clientId}&redirect_uri=${redirectUri}&response_type=${responseType}&scope=${scope}`;
  window.location.href = dexUrl; // Redirect user to Dex login page
}

function userLogout() {
  window.location.href = "http://localhost:8000/logout";
  isLoggedIn = false;
}

  </script>

  
  <div class="container">
    <header>
      <button on:click={() => currentPage = 'home'}>
        <img src="./logo.png" alt="Food Tracker logo" id="logo">
      </button>
      <nav>
        <button on:click={() => currentPage = 'calculator'}>Calculator</button>
        <button on:click={() => currentPage = 'goal'}>Goal</button>
        <button on:click={() => currentPage = 'planner'}>Meal Planner</button>
        <button on:click={() => currentPage = 'report'}>Report</button>
        <button on:click={() => currentPage = 'recipe'}>Recipe</button>
        <div>
          {#if !loading}
            {#if isLoggedIn}
              <div class="logged-in">
                <button on:click={() => currentPage = 'user-portal'}>
                  <img src="./profile.png" alt="profile icon" id="profile-icon">
                </button>
                <button class="logout-btn" on:click={userLogout} type="button" aria-label="User Account">
                  Logout
                </button>
              </div>
            {:else}
              <button class="login-btn" on:click={redirectToDexLogin}>Login</button>
            {/if}
          {/if}
        </div>
      </nav>
    </header>
    {#if currentPage === 'calculator'}
        <CalculatorPage />
      {:else if currentPage === 'goal'}
        <GoalPage />
      {:else if currentPage === 'planner'}
        <PlannerPage />
      {:else if currentPage === 'report'}
        <ReportPage />
      {:else if currentPage === 'recipe'}
        <RecipePage />
      {:else if currentPage === 'user-portal'}
        <UserPortal />
      {/if}
  {#if currentPage === 'home'} 
    <h1 class="Welcome">Welcome to Food Tracker</h1>
      <div class="grid">
        <div class="card">
          <h3>About Us</h3>
          <p>College students struggle with healthy eating. We make it easier.</p>
        </div>
        <div class="card">
          <h3>What to Expect</h3>
          <p>Get daily, personalized meal plans based on your goals and preferences.</p>
        </div>
        <div class="card" style="flex-basis: 100%;">
          <h3>Track Your Progress</h3>
          <p>Stay motivated by tracking weight, goals, and progress over time.</p>
        </div>
      </div>
  {/if}
</div>
