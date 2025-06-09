<script lang="ts">
  import { onMount } from 'svelte';
  import Router from 'svelte-spa-router';
  import routes from './routes/routes';
  import './app.scss'
  import Homepage from './routes/Homepage.svelte'; // import homepage directly
  import { userRole, fetchUserRole } from './stores/userRole';

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

    async function userLogout() {
      try {
        await fetch('http://localhost:8000/logout', {
          method: 'GET',
          credentials: 'include'
        });

        isLoggedIn = false;
        userInfo = {};
        userRole.set(null); // Reset userRole on logout
        await fetchUserRole(); // Ensure store is up to date after logout
        window.location.hash = "#/"; // redirect to homepage
      } catch (error) {
        console.error('Logout failed:', error);
      }
    }

</script>

{#if !loading}
  {#if isLoggedIn}
    <div class="container">
      <header>
        <a href="#/" class="logo">
          <img src="./logo.png" alt="Food Tracker logo" id="logo">
        </a>
        <nav>
          <a href="#/calculator">Calculator</a>
          <a href="#/goal">Goal</a>
          <a href="#/planner">Meal Planner</a>
          <a href="#/report">Report</a>
          <div>
            <div class="logged-in">
              <a href="#/user-portal">
                <img src="./profile.png" alt="profile icon" id="profile-icon">
              </a>
              <button class="logout-btn" on:click={userLogout} type="button" aria-label="User Account">
                Logout
              </button>
            </div>
          </div>
        </nav>
      </header>
    </div>
    <Router {routes} />
  {:else}
    <div class="container">
      <header>
        <a href="#/" class="logo">
          <img src="./logo.png" alt="Food Tracker logo" id="logo">
        </a>
        <nav>
          <button class="login-btn" on:click={redirectToDexLogin}>Login</button>
        </nav>
      </header>
    </div>
    <Homepage />
  {/if}
{:else}
  <div class="loading-container">
    <p>Loading...</p>
  </div>
{/if}

<main>


</main>
