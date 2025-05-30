<script lang="ts">
  import { onMount } from 'svelte';

  let currentWeight = 0;
  let startingWeight = 0;
  let latestWeight = 0;
  let targetWeight = 65;
  let duration = 90;
  let goalStartDate = new Date().toISOString().slice(0, 10);
  let calorieAdjust = 0;
  let message = '';
  let error = '';

  // track goal type
  let goalType: 'lose' | 'maintain' | 'gain' = 'maintain';

  // derive a friendly label
  $: goalLabel =
    goalType === 'lose'
      ? 'Lose Weight'
      : goalType === 'gain'
      ? 'Gain Weight'
      : 'Maintain Weight';

  // clamp between 0 and 1
  const clamp = (v: number) => Math.min(Math.max(v, 0), 1);

  onMount(async () => {
    try {
      const profileRes = await fetch('http://localhost:8000/user/profile', {
        method: 'GET',
        credentials: 'include'
      });
      const profileData = await profileRes.json();
      if (!profileRes.ok) {
        throw new Error(profileData.error || 'error fetching profile');
      }
      currentWeight = profileData.weight;
      startingWeight = profileData.weight;
      latestWeight = profileData.weight;

      const goalRes = await fetch('http://localhost:8000/goal', {
        method: 'GET',
        credentials: 'include'
      });
      const goalData = await goalRes.json();
      if (goalRes.ok) {
        targetWeight = goalData.target_weight;
        duration = goalData.duration_days;
        goalStartDate = goalData.start_date || goalStartDate;
        startingWeight = goalData.starting_weight || startingWeight;
        latestWeight = goalData.latest_weight || latestWeight;
      }
    } catch (err) {
      error = err.message || 'error loading goal';
    }
  });

  const setGoal = async () => {
    error = '';
    try {
      const res = await fetch('http://localhost:8000/goal', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          target_weight: targetWeight,
          duration_days: duration,
          start_date: goalStartDate,
          starting_weight: startingWeight
        })
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.error || 'error setting goal');
      }
      calorieAdjust = data.calories_sug;
      message = data.message;
    } catch (err) {
      error = err.message || 'network error';
    }
  };

  // reactive: derive goalType whenever start/target change
  $: goalType =
    targetWeight < startingWeight
      ? 'lose'
      : targetWeight > startingWeight
      ? 'gain'
      : 'maintain';

  // calculate weight progress
  $: weightProgress = clamp(
    (startingWeight - latestWeight) / (startingWeight - targetWeight)
  );

  // calculate time progress
  $: timeProgress = clamp(
    (Date.now() - new Date(goalStartDate).getTime()) /
      (duration * 24 * 60 * 60 * 1000)
  );
</script>

<h2>Set Your Weight Goal</h2>
{#if error}
  <p style="color: red;">{error}</p>
{/if}

<label>
  Current Weight (kg):
  <input type="number" bind:value={currentWeight} disabled />
</label>

<label>
  Starting Weight (kg):
  <input type="number" bind:value={startingWeight} />
</label>

<label>
  Latest Weight (kg):
  <input type="number" bind:value={latestWeight} />
</label>

<label>
  Target Weight (kg):
  <input type="number" bind:value={targetWeight} />
</label>

<label>
  Duration (days):
  <input type="number" bind:value={duration} />
</label>

<label>
  Goal Start Date:
  <input type="date" bind:value={goalStartDate} />
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

<h3>Goal Type</h3>
<p>{goalLabel}</p>

<h3>Weight Progress</h3>
<progress max="1" value={weightProgress}></progress>
<p>
  {Math.round(weightProgress * 100)}% toward your weight goal
</p>

<h3>Time Progress</h3>
<progress max="1" value={timeProgress}></progress>
<p>
  {Math.round(timeProgress * 100)}% of {duration} days elapsed
</p>


<!-- <script lang="ts">
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
<p>{(progress * 100).toFixed(0)}% toward your goal</p> -->
