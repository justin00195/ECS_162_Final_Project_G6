<script lang="ts">
  import { onMount } from 'svelte';

  let bmr = 0;
  let tdee = 0;

  interface BodyInput {
    sex: 'male' | 'female';
    age: number;
    height: number;
    weight: number;
    activity: number;
  }

  let input: BodyInput = {
    sex: 'male',
    age: 25,
    height: 175,
    weight: 70,
    activity: 1.55
  };

  const calculate = async () => {
    const res = await fetch('http://localhost:5000/calculate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(input)
    });

    const data = await res.json();
    bmr = data.bmr;
    tdee = data.tdee;
  };

  onMount(calculate);
</script>

<h1>Calculator Page</h1>

<label>Sex:
  <select bind:value={input.sex}>
    <option value="male">Male</option>
    <option value="female">Female</option>
  </select>
</label>

<label>Age:
  <input type="number" bind:value={input.age} />
</label>

<label>Height (cm):
  <input type="number" bind:value={input.height} />
</label>

<label>Weight (kg):
  <input type="number" bind:value={input.weight} />
</label>

<label>Activity Level:
  <select bind:value={input.activity}>
    <option value={1.2}>Sedentary</option>
    <option value={1.375}>Lightly active</option>
    <option value={1.55}>Moderately active</option>
    <option value={1.725}>Very active</option>
    <option value={1.9}>Super active</option>
  </select>
</label>

<button on:click={calculate}>Recalculate</button>

<p><strong>BMR:</strong> {bmr} kcal/day</p>
<p><strong>TDEE:</strong> {tdee} kcal/day</p>
