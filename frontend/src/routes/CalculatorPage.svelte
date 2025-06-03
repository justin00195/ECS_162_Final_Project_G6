<script lang="ts">
  import { onMount } from 'svelte';
  import '../assets/calculator.scss';
  import { allTDEE } from '../stores/tdee';


  let bmr = 0;
  let tdee = 0;
  let showResults = false;
  let error = '';

  let user = {
    gender: '',
    age: 0,
    height: 0,
    weight: 0,
    activity_level: 1.55
  };

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
        error = data.error || 'error to load profile';
      }
    } catch (err) {
      error = 'profile error';
    }
  });

  const calculate = async () => {
    try {
      const res = await fetch('http://localhost:8000/calculate', {
        method: 'GET',
        credentials: 'include'
      });

      const data = await res.json();
      if (!res.ok) {
        error = data.error || 'errror fetch data';
        return;
      }
      bmr = data.bmr;
      tdee = data.tdee;
      allTDEE.set(data.tdee);
      showResults = true;
      const results = document.querySelector('.results');
      if (results) {
        results.scrollIntoView({ behavior: 'smooth' });
      }
    } catch (err) {
      error = 'fetch error';
    }
  };
</script>

<div class="body">
  <h1 class="heading">Based on your profile to calculate your</h1>
  <div class="description">
    <p class="measurement-heading">Basal Metabolic Rate</p>
    <p class="acronym">(BMR)</p>
    <p class="plus">+</p>
    <p class="measurement-heading">Total Daily Energy Expenditure</p>
    <p class="acronym">(TDEE)</p>
  </div>

  <div class="form">
    <div class="input">
      <p><strong>Gender:</strong> {user.gender}</p>
      <p><strong>Age:</strong> {user.age}</p>
      <p><strong>Height:</strong> {user.height} cm</p>
      <p><strong>Weight:</strong> {user.weight} kg</p>
      <p><strong>Activity Level:</strong> {user.activity_level}</p>
    </div>

    {#if showResults}
      <div class="results">
        <h1 class="results-title">Results</h1>
        <div class="results-info">
          <div class="measurement">
            <p class="measurement-title">BMR:</p>
            <p>{bmr}</p>
            <p class="units">kcal/day</p>
          </div>
          <div class="measurement">
            <p class="measurement-title">TDEE:</p>
            <p>{tdee}</p>
            <p class="units">kcal/day</p>
          </div>
        </div>
      </div>
      <button on:click={calculate} class="calculate-btn">Recalculate!</button>
    {:else}
      <button on:click={calculate} class="calculate-btn">Calculate!</button>
    {/if}
  </div>
</div>


