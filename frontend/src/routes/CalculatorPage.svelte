<script lang="ts">
  import '../assets/calculator.scss'

  let bmr = 0;
  let tdee = 0;
  let showResults = false;

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
    const res = await fetch('http://localhost:8000/calculate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(input)
    });

    const data = await res.json();
    bmr = data.bmr;
    tdee = data.tdee;
    showResults = true;

    const results = document.querySelector('.results');
    if (results) {
      results.scrollIntoView({ behavior: 'smooth' });
    }
  };

</script>

<div class="body">
  <h1 class="heading">Input your information below to calculate your</h1>
  <div class="description">
    <p class="measurement-heading">Basal Metabolic Rate</p>
    <p class="acronym">(BMR)</p>
    <p class="plus">+</p>
    <p class="measurement-heading">Total Daily Energy Expenditure</p>
    <p class="acronym">(TDEE)</p>
  </div>

  <div class="form">
    <div class="inputs">
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
    </div>

    {#if showResults}
      <div class="results">
        <h1 class="results-title">Results</h1>
        <div class="results-info">
          <div class="measurement">
            <p class="measurement-title">BMR: </p>
            <p>{bmr} </p>
            <p class="units">kcal/day</p>
          </div>
          <div class="measurement">
            <p class="measurement-title">TDEE: </p>
            <p>{tdee} </p>
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
