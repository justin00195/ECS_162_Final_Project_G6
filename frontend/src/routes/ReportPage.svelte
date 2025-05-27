<script lang="ts">
    import { onMount } from 'svelte';
    import {Tween} from 'svelte/motion'
    import { cubicOut } from 'svelte/easing';
  
    let report: any = {};

    // calorieBudget should be calcualted from the goalpage
    let calorieBudget = 1000;
    let breakFast = 0;
    let lunch = 0;
    let dinner = 0;
    let snacks = 0;
  
    onMount(async () => {
      const res = await fetch('http://localhost:8000/report');
      report = await res.json();
    });


    let progress = new Tween(0, {
      duration: 500,
      easing: cubicOut
    })
    $: calsAte = breakFast + lunch + dinner + snacks;
    $: calsLeft = Math.max(0, calorieBudget - calsAte)

    function updateProgress(){
      const totalCals = breakFast + lunch + dinner + snacks;
      progress.target = Math.min(calorieBudget, Math.max(0,totalCals))
    }
  </script>
  
  
<pre>{JSON.stringify(report, null, 2)}</pre>
  <header>
    <h1>Report Page</h1>
  </header>
    
<div class="progress-container">
  <div class ="progress-wrapper">
    <div class ="progress-label">Daily Calorie Budget</div>
    <progress max = {calorieBudget} value={progress.current}></progress>


  <div class ="progress-info">
    <div>Daily Budget:{calorieBudget} | Calories Eaten: {calsAte} | Budget Remaining:{calsLeft}</div> 
  </div>
  </div>
</div>

<div class = "input-box">
  <div>
    <label for = "breakFastLabel">Breakfast</label>
    <input
      id ="breakFastLabel"
      type ="number"
      bind:value={breakFast}
      on:change={updateProgress}
      />
  </div>
    
  <div>
    <label for = "lunchLabel">Lunch</label>
    <input
      id ="lunchLabel"
      type ="number"
      bind:value={lunch}
      on:change={updateProgress}
      />
  </div>

   <div>
    <label for = "dinnerLabel">Dinner</label>
    <input
      id ="dinnerLabel"
      type ="number"
      bind:value={dinner}
      on:change={updateProgress}
      />
  </div>
    
  <div>
    <label for = "snacksLabel">Snacks</label>
    <input
      id ="snacksLabel"
      type ="number"
      bind:value={snacks}
      on:change={updateProgress}
      />
  </div>
</div>
     
  
  
  <!---Subject to change-->
  <style>

    .input-box{
      display: grid;
      grid-template-columns: repeat(2,1fr);
      gap:1rem;
      max-width: 400px;
      margin: 1rem auto;
      background-color: #DFD3CC;
      border-radius: 10px;
      padding: 2rem;
    }
    .progress-wrapper{
      display: flex;
      flex-direction: column;
      align-items: center;
      width: 500px;
    }
    .progress-label{
      font-weight: bold;
      text-align: center;
      margin-bottom: 0.5rem;
    }
    .progress-container {
      display: flex;
      justify-content: center;
      margin: 1rem auto 0 auto;
    }
    progress{
      width: 100%;
      height: 30px;
      appearance: none;
      border-radius: 15px;
      overflow: hidden;
      
    }
  </style>