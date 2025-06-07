<script lang="ts">
  import { onMount } from 'svelte';
  import { calAdjust } from '../stores/calAdjust';
  import '../assets/goal.scss';

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
  let showDurationTooltip = false;
  let showCalorieTooltip = false;

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
      // Load saved message and calorie adjustment from localStorage
      const savedMessage = localStorage.getItem('goalMessage');
      const savedCalorieAdjust = localStorage.getItem('calorieAdjust');
      if (savedMessage) message = savedMessage;
      if (savedCalorieAdjust) calorieAdjust = parseInt(savedCalorieAdjust);

      const profileRes = await fetch('http://localhost:8000/user/profile', {
        method: 'GET',
        credentials: 'include'
      });
      const profileData = await profileRes.json();
      if (!profileRes.ok) {
        throw new Error(profileData.error || 'error fetching profile');
      }
      currentWeight = profileData.weight;
      startingWeight = currentWeight;
      latestWeight = startingWeight;

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
    if (!startingWeight || !targetWeight || !duration) {
      error = 'Please fill in all fields before submitting.';
      return;
    }
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
      const wasFirstGoal = !hasExistingGoal;
      hasExistingGoal = true;
      calorieAdjust = data.calories_sug;
      calAdjust.set(data.calories_sug);
      message = data.message;

      // Save message and calorie adjustment to localStorage
      localStorage.setItem('goalMessage', message);
      localStorage.setItem('calorieAdjust', calorieAdjust.toString());

      // Update saved values after successful submission
      savedStartingWeight = startingWeight;
      savedLatestWeight = latestWeight;
      savedTargetWeight = targetWeight;
      savedDuration = duration;
      savedStartDate = goalStartDate;

      // Fetch the current user profile
      const userProfileRes = await fetch('http://localhost:8000/user/profile', {
        method: 'GET',
        credentials: 'include'
      });
      const userProfile = await userProfileRes.json();
      // Update the weight field
      userProfile.weight = wasFirstGoal ? startingWeight : latestWeight;
      // POST the full user profile back
      await fetch('http://localhost:8000/user/profile', {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userProfile)
      });
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
      startingWeight = currentWeight;
      latestWeight = currentWeight;
      calorieAdjust = 0;  // Reset calorie adjustment
      calAdjust.set(0);   // Reset the Svelte store as well
      message = '';       // Clear the message

      // Clear localStorage
      localStorage.removeItem('goalMessage');
      localStorage.removeItem('calorieAdjust');

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

  // Keep latestWeight in sync with startingWeight before first goal is submitted
  $: if (!hasExistingGoal) {
    latestWeight = startingWeight;
  }
</script>

<h1>Set Your Weight Goal</h1>
{#if error}
  <p class="error-message">{error}</p>
{/if}

<!-- FLEXBOX LAYOUT -->
<div class="flex-container">
  <!-- LEFT COLUMN -->
  <div class="card left-column">
    {#if !hasExistingGoal}
      <label>
        Starting Weight (kg):
        <input type="number" bind:value={startingWeight} />
      </label>
    {:else}
      <div class="saved-value">
        <span class="label">Starting Weight:</span>
        <span class="value">{startingWeight} kg</span>
      </div>
    {/if}

    {#if hasExistingGoal}
      <label>
        Latest Weight (kg):
        <input type="number" bind:value={latestWeight} />
      </label>
    {/if}

    <label>
      Target Weight (kg):
      <input type="number" bind:value={targetWeight} />
    </label>

    <div class="input-with-tooltip">
      <label>
        Duration (days):
        <input type="number" bind:value={duration} />
      </label>
      <button 
        class="info-button" 
        on:click={() => showDurationTooltip = !showDurationTooltip}
        on:blur={() => showDurationTooltip = false}
      >
        ℹ️
      </button>
      {#if showDurationTooltip}
        <div class="tooltip">
          How many days until you reach your target weight?
        </div>
      {/if}
    </div>

    {#if !hasExistingGoal}
      <label>
        Goal Start Date:
        <input type="date" bind:value={goalStartDate} />
      </label>
    {:else}
      <div class="saved-value">
        <span class="label">Start Date:</span>
        <span class="value">📅 {goalStartDate}</span>
      </div>
    {/if}

    <div class="button-group">
      <button class="primary-button" on:click={setGoal}>
        {hasExistingGoal ? 'Update' : 'Submit'}
      </button>
      {#if hasExistingGoal}
        <button class="delete-button" on:click={confirmDelete}>
          Delete
        </button>
      {/if}
    </div>

    {#if showDeleteConfirmation}
      <div class="confirmation-popup">
        <p>Are you sure you want to delete your goal?</p>
        <div class="confirmation-buttons">
          <button class="delete-button" on:click={deleteGoal}>Yes</button>
          <button class="cancel-button" on:click={cancelDelete}>Cancel</button>
        </div>
      </div>
    {/if}
  </div>

  <!-- RIGHT COLUMN -->
  <div class="card right-column">
    {#if message}
      <div class="notification">
        <span class="checkmark">✅</span>
        <span class="message">{message}</span>
        <div class="calorie-info">
          <span>Recommended daily calorie {goalType === 'lose' ? 'deficit' : goalType === 'gain' ? 'surplus' : 'adjustment'}:</span>
          <div class="input-with-tooltip">
            <strong>{calorieAdjust} kcal</strong>
            <button 
              class="info-button" 
              on:click={() => showCalorieTooltip = !showCalorieTooltip}
              on:blur={() => showCalorieTooltip = false}
            >
              ℹ️
            </button>
            {#if showCalorieTooltip}
              <div class="tooltip">
                This is calculated based on your weight difference and duration. 
                For every 7700 calories, you gain or lose 1 kg of weight. Your calorie adjustment will be applied to your daily calorie budget.
              </div>
            {/if}
          </div>
        </div>
      </div>
    {/if}

    {#if hasExistingGoal}
      <div class="goal-type">
        <h3>Goal Type</h3>
        <p>{goalLabel}</p>
      </div>
    {/if}

    <div class="progress-section">
      <h3>Weight Progress</h3>
      <progress max="1" value={weightProgress}></progress>
      <p>{Math.round(weightProgress * 100)}% toward your weight goal</p>
    </div>

    <div class="progress-section">
      <h3>Time Progress</h3>
      <progress max="1" value={timeProgress}></progress>
      <p>{Math.round(timeProgress * 100)}% of {savedDuration} days elapsed</p>
    </div>
  </div>
</div>
