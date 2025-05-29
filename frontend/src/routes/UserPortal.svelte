<script lang="ts">
  import { onMount } from 'svelte';

  let user = {
    name: '',
    gender: '',
    age: 0,
    height: 0,
    weight: 0,
    activity_level: 1.55
  };

  let loading = true;
  let error = '';

  onMount(async () => {
    try {
      const res = await fetch('http://localhost:8000/user/profile', {
        method: 'GET',
        credentials: 'include'
      });
      const data = await res.json();
      if (res.ok) {
        user = data;
      } else {
        error = data.error || 'Please fill your profile';
      }
    } catch (err) {
      error = 'Please fill your profile';
    } finally {
      loading = false;
    }
  });

  const saveProfile = async () => {
    const res = await fetch('http://localhost:8000/user/profile', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(user)
    });

    const result = await res.json();
    if (res.ok) {
      window.location.href = '/';
    } else {
      error = result.error || 'error to save profile';
    }
  };
</script>

<style>
  .form {
    display: grid;
    gap: 1rem;
    padding: 2rem;
    max-width: 500px;
    margin: auto;
    background-color: #f9fafb;
    border-radius: 1rem;
  }

  label {
    display: flex;
    flex-direction: column;
    font-weight: 500;
  }

  input, select {
    padding: 0.5rem;
    border-radius: 0.5rem;
    border: 1px solid #ccc;
  }

  .save-btn {
    background-color: #4caf50;
    color: white;
    padding: 0.75rem;
    border: none;
    border-radius: 0.5rem;
    cursor: pointer;
    font-weight: bold;
  }
</style>

<h1>Your Profile</h1>

{#if loading}
  <p>Loading...</p>
{:else}
  {#if error}
    <p style="color: red;">{error}</p>
  {/if}
  <div class="form">
    <label>Name:
      <input type="text" bind:value={user.name} />
    </label>
    <label>Gender:
      <select bind:value={user.gender}>
        <option value="male">Male</option>
        <option value="female">Female</option>
      </select>
    </label>
    <label>Age:
      <input type="number" bind:value={user.age} />
    </label>
    <label>Height (cm):
      <input type="number" bind:value={user.height} />
    </label>
    <label>Weight (kg):
      <input type="number" bind:value={user.weight} />
    </label>
    <label>Activity Level:
      <select bind:value={user.activity_level}>
        <option value={1.2}>Sedentary</option>
        <option value={1.375}>Lightly active</option>
        <option value={1.55}>Moderately active</option>
        <option value={1.725}>Very active</option>
        <option value={1.9}>Super active</option>
      </select>
    </label>
    <button class="save-btn" on:click={saveProfile}>Save & Go Home</button>
  </div>
{/if}
