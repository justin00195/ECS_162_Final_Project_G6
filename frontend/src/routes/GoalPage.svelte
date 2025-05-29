<script lang="ts">
  import { onMount } from 'svelte';

  let currentWeight = 0;
  let targetWeight = 65;
  let duration = 90;
  let calorieAdjust = 0;
  let message = '';
  let error = '';

  let goalType: 'lose' | 'maintain' | 'gain' = 'maintain';

  onMount(async () => {
    try {
      const profileRes = await fetch('http://localhost:8000/user/profile', {
        method: 'GET',
        credentials: 'include'
      });
      const profileData = await profileRes.json();
      if (profileRes.ok) {
        currentWeight = profileData.weight;
      } else {
        error = profileData.error || 'error to fetch user profile';
        return;
      }

      const goalRes = await fetch('http://localhost:8000/goal', {
        method: 'GET',
        credentials: 'include'
      });
      const goalData = await goalRes.json();
      if (goalRes.ok) {
        targetWeight = goalData.target_weight;
        duration = goalData.duration_days;
        updateGoalType();
      } else {
        console.log('No goal yet');
      }
    } catch (err) {
      error = 'error to get goal';
    }
  });

  const updateGoalType = () => {
    if (targetWeight < currentWeight) {
      goalType = 'lose';
    } else if (targetWeight > currentWeight) {
      goalType = 'gain';
    } else {
      goalType = 'maintain';
    }
  };

  const setGoal = async () => {
    error = '';
    try {
      const res = await fetch('http://localhost:8000/goal', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          target_weight: targetWeight,
          duration_days: duration
        })
      });

      const data = await res.json();
      if (res.ok) {
        calorieAdjust = data.calories_sug;
        message = data.message;
        updateGoalType(); 
  
      } else {
        error = data.error || 'error to set goal';
      }
    } catch (err) {
      error = 'set goal error';
    }
  };

  $: progress = Math.min(
    Math.abs(targetWeight - currentWeight) / Math.abs(currentWeight - targetWeight || 1),
    1
  );
</script>

<h2>Set Your Weight Goal</h2>

{#if error}
  <p style="color: red;">{error}</p>
{/if}

<label>Current Weight (kg):
  <input type="number" bind:value={currentWeight} disabled />
</label>

<label>Target Weight (kg):
  <input type="number" bind:value={targetWeight} on:change={updateGoalType} />
</label>

<label>Duration (days):
  <input type="number" bind:value={duration} />
</label>

<button on:click={setGoal}>Submit Goal</button>

{#if message}
  <p><strong>{message}</strong></p>
  <p>
    Recommended daily calorie
    {goalType === 'lose' ? 'deficit' : goalType === 'gain' ? 'surplus' : 'adjustment'}:
    <strong>{calorieAdjust}</strong> kcal
  </p>
{/if}

<h3>Goal Progress</h3>
<progress max="1" value={progress}></progress>
<p>{(progress * 100).toFixed(0)}% toward your goal</p>
