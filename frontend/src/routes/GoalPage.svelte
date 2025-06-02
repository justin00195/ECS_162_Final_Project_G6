<script lang="ts">
  import { onMount } from 'svelte';

  let currentWeight = 0;
  let startingWeight = 0;
  let latestWeight = 0;
  let targetWeight = 0;
  let duration = 0;
  let goalStartDate = new Date().toISOString().slice(0, 10);
  let calorieAdjust = 0;
  let message = '';
  let error = '';
  let hasExistingGoal = false;
  let showDeleteConfirmation = false;

  // Saved values for progress calculations
  let savedStartingWeight = 0;
  let savedLatestWeight = 0;
  let savedTargetWeight = 0;
  let savedDuration = 0;
  let savedStartDate = '';

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

      const goalRes = await fetch('http://localhost:8000/goal', {
        method: 'GET',
        credentials: 'include'
      });
      const goalData = await goalRes.json();
      if (goalRes.ok) {
        hasExistingGoal = true;
        goalType = goalData.goal_type;
        targetWeight = goalData.target_weight;
        duration = goalData.duration_days;
        goalStartDate = goalData.start_date;
        startingWeight = goalData.starting_weight;
        latestWeight = goalData.latest_weight;

        // Save the initial values
        savedStartingWeight = startingWeight;
        savedLatestWeight = latestWeight;
        savedTargetWeight = targetWeight;
        savedDuration = duration;
        savedStartDate = goalStartDate;
      }
    } catch (err: any) {
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
          goal_type: goalType,
          target_weight: targetWeight,
          duration_days: duration,
          start_date: goalStartDate,
          starting_weight: startingWeight,
          latest_weight: latestWeight
        })
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.error || 'error setting goal');
      }
      hasExistingGoal = true;
      calorieAdjust = data.calories_sug;
      message = data.message;

      // Update saved values after successful submission
      savedStartingWeight = startingWeight;
      savedLatestWeight = latestWeight;
      savedTargetWeight = targetWeight;
      savedDuration = duration;
      savedStartDate = goalStartDate;
    } catch (err: any) {
      error = err.message || 'network error';
    }
  };

  const confirmDelete = () => {
    showDeleteConfirmation = true;
  };

  const cancelDelete = () => {
    showDeleteConfirmation = false;
  };

  const deleteGoal = async () => {
    try {
      const res = await fetch('http://localhost:8000/goal', {
        method: 'DELETE',
        credentials: 'include'
      });
      if (!res.ok) {
        throw new Error('Failed to delete goal');
      }
      // Reset form
      hasExistingGoal = false;
      goalType = 'maintain';
      targetWeight = 0;
      duration = 0;
      goalStartDate = new Date().toISOString().slice(0, 10);
      startingWeight = 0;
      latestWeight = 0;
      calorieAdjust = 0;  // Reset calorie adjustment
      message = '';       // Clear the message

      // Reset saved values
      savedStartingWeight = 0;
      savedLatestWeight = 0;
      savedTargetWeight = 0;
      savedDuration = 0;
      savedStartDate = '';
      
      showDeleteConfirmation = false;
    } catch (err: any) {
      error = err.message || 'Failed to delete goal';
    }
  };

  // reactive: derive goalType whenever start/target change
  $: goalType =
    targetWeight < startingWeight
      ? 'lose'
      : targetWeight > startingWeight
      ? 'gain'
      : 'maintain';

  // calculate weight progress using saved values
  $: weightProgress = hasExistingGoal
    ? clamp(
        (savedStartingWeight - savedLatestWeight) /
        (savedStartingWeight - savedTargetWeight)
      )
    : 0;

  // calculate time progress using saved values
  $: timeProgress = hasExistingGoal
    ? clamp(
        (Date.now() - new Date(savedStartDate).getTime()) /
        (savedDuration * 24 * 60 * 60 * 1000)
      )
    : 0;
</script>

<h2>Set Your Weight Goal</h2>
{#if error}
  <p style="color: red;">{error}</p>
{/if}

<!-- FLEXBOX LAYOUT -->
<div class="flex-container">
  <!-- LEFT COLUMN -->
  <div class="left-column">
    <!-- Current Weight field commented out
    <label>
      Current Weight (kg):
      <input type="number" bind:value={currentWeight} disabled />
    </label>
    -->
    <label>
      Starting Weight (kg):
      <input
        type="number"
        bind:value={startingWeight}
        disabled={hasExistingGoal}
      />
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

    <button on:click={setGoal}>
      {hasExistingGoal ? 'Update Progress' : 'Submit Goal'}
    </button>
    <button on:click={confirmDelete} style="margin-left: 10px;">
      Delete Goal
    </button>

    {#if showDeleteConfirmation}
      <div class="confirmation-popup">
        <p>Are you sure you want to delete your goal?</p>
        <button on:click={deleteGoal}>Yes, Delete</button>
        <button on:click={cancelDelete}>Cancel</button>
      </div>
    {/if}
  </div>

  <!-- RIGHT COLUMN -->
  <div class="right-column">
    {#if message}
      <p><strong>{message}</strong></p>
      <p>
        Recommended daily calorie
        {goalType === 'lose'
          ? 'deficit'
          : goalType === 'gain'
          ? 'surplus'
          : 'adjustment'}
        : <strong>{calorieAdjust}</strong> kcal
      </p>
    {/if}

    {#if hasExistingGoal}
      <h3>Goal Type</h3>
      <p>{goalLabel}</p>
    {/if}

    <h3>Weight Progress</h3>
    <progress max="1" value={weightProgress}></progress>
    <p>{Math.round(weightProgress * 100)}% toward your weight goal</p>

    <h3>Time Progress</h3>
    <progress max="1" value={timeProgress}></progress>
    <p>{Math.round(timeProgress * 100)}% of {savedDuration} days elapsed</p>
  </div>
</div>

<style>
  /* Flex container for two columns */
  .flex-container {
    display: flex;
    column-gap: 2rem;   /* horizontal space between columns */
    align-items: flex-start;
  }

  /* Each column should take up roughly 50% */
  .left-column,
  .right-column {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;       /* vertical spacing between items */
  }

  /* On narrow screens, stack vertically */
  @media (max-width: 600px) {
    .flex-container {
      flex-direction: column;
    }
  }

  .confirmation-popup {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: white;
    padding: 20px;
    border-radius: 5px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    z-index: 1000;
  }

  .confirmation-popup button {
    margin: 10px;
  }
</style>
