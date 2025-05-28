<script lang="ts">
    import { onMount } from 'svelte';
  
    let user = {
      name: '',
      gender: '',
      age: 0,
      height: 0,
      weight: 0,
      activity_level: ''
    };
  
    let loading = false;
    let error = '';
  
 
  </script>
  
  <style>
  
    .card {
      background: white;
      border-radius: 1rem;
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
      padding: 2rem;
      max-width: 500px;
      width: 100%;
      transition: all 0.3s ease-in-out;
    }
  
    h1 {
      font-size: 2rem;
      font-weight: 600;
      color: #333;
      margin-bottom: 2rem;
    }
  
    .userInfo {
      display: grid;
      grid-template-columns: 1fr;
      row-gap: 1rem;
    }
  
    .attr {
      display: flex;
      justify-content: space-between;
      padding: 0.75rem 1rem;
      background-color: #f0f4f8;
      border-radius: 0.5rem;
      font-size: 1rem;
      color: #444;
    }
  
    .label {
      font-weight: 500;
      color: #222;
    }
  </style>

  <div class="userPortal">
    <h1>Your Profile</h1>
  
    {#if loading}
      <p class="status">Loading your information...</p>
    {:else if error}
      <p class="status" style="color: red;">{error}</p>
    {:else}
      <div class="card">
        <div class="userInfo">
          <div class="attr"><span class="label">Name:</span><span class="value">{user.name}</span></div>
          <div class="attr"><span class="label">Gender:</span><span class="value">{user.gender}</span></div>
          <div class="attr"><span class="label">Age:</span><span class="value">{user.age}</span></div>
          <div class="attr"><span class="label">Height:</span><span class="value">{user.height} cm</span></div>
          <div class="attr"><span class="label">Weight:</span><span class="value">{user.weight} kg</span></div>
          <div class="attr"><span class="label">Activity Level:</span><span class="value">{user.activity_level}</span></div>
        </div>
      </div>
    {/if}
  </div>
  