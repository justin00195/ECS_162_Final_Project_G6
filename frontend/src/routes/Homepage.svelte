<script>
    import { link } from 'svelte-spa-router';
    import '/src/hp.scss'

    //https://developers.google.com/identity/protocols/oauth2/javascript-implicit-flow
function redirectToDexLogin() {
  const clientId = 'flask-app';
  const redirectUri = 'http://localhost:8000/auth/callback';
  const responseType = 'code';
  const scope = 'openid email';
  const dexUrl = `http://localhost:5556/auth?client_id=${clientId}&redirect_uri=${redirectUri}&response_type=${responseType}&scope=${scope}`;
  window.location.href = dexUrl; // Redirect user to Dex login page
}
  </script>

  
  <div class="container">
    <header>
      <h2>Food Tracker</h2>
      <div class="auth-buttons">
        <button class="loginButton" on:click={redirectToDexLogin}>Login</button>

      </div>
    </header>
  
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
  </div>