<script lang="ts">
  let currentWeight = 70;
  let targetWeight = 65;
  let duration = 90; // days
  let goalType: 'lose' | 'maintain' | 'gain' = 'lose';

  let calorieAdjust = 0;
  let message = '';

  const setGoal = async () => {
    const res = await fetch('http://localhost:5000/goal', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        goal_type: goalType,
        target_weight: targetWeight,
        duration_days: duration
      })
    });

    const data = await res.json();
    calorieAdjust = data.calorie_adjust;
    message = data.message;
  };

  $: progress = Math.min((goalType === 'lose'
    ? (currentWeight - targetWeight)
    : (targetWeight - currentWeight)) / Math.abs(currentWeight - targetWeight), 1);
</script>

<h2>Set Your Weight Goal</h2>

<label>Current Weight (kg):
  <input type="number" bind:value={currentWeight} />
</label>

<label>Target Weight (kg):
  <input type="number" bind:value={targetWeight} />
</label>

<label>Duration (days):
  <input type="number" bind:value={duration} />
</label>

<label>Goal Type:
  <select bind:value={goalType}>
    <option value="lose">Lose</option>
    <option value="maintain">Maintain</option>
    <option value="gain">Gain</option>
  </select>
</label>

<button on:click={setGoal}>Submit Goal</button>

{#if message}
  <p><strong>{message}</strong></p>
  <p>Recommended daily calorie {goalType === 'lose' ? 'deficit' : goalType === 'gain' ? 'surplus' : 'adjustment'}: <strong>{calorieAdjust}</strong> kcal</p>
{/if}

<h3>Goal Progress</h3>
<progress max="1" value={progress}></progress>
<p>{(progress * 100).toFixed(0)}% toward your goal</p>
