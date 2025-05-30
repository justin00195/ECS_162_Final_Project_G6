<script lang="ts">
    import { onMount } from 'svelte';
    import {Tween} from 'svelte/motion'
    import { cubicOut } from 'svelte/easing';
    
    
  
    let report: any = {};

    // calorieBudget should be calcualted from the goalpage
    // some how need to pull info from api about macros 
    //3 main marcos are protien, fats, carbs

    let calorieBudget = 1000;
    let breakFast = 0;
    let lunch = 0;
    let dinner = 0;
    let snacks = 0;

    let breakFastQ = '';
    let lunchQ = '';
    let dinnerQ = '';
    let snacksQ = '';

    type mealType = 'breakfast' | 'lunch' |'dinner'|'snacks';

    let mealList: Record<mealType, String[]>={
      breakfast: [],
      lunch: [],
      dinner: [],
      snacks: [],
    }
    
    // when new food is added it replaces the old one in the list 
    async function getFoodData(meal:mealType, query: string) {
      try{

          const queries = query.split(',').map(q=>q.trim())
          let totalCals = 0
          let labels: string[] = []

          for (const q of queries){
            const res = await fetch('http://localhost:8000/report',{
            method: 'POST',
            headers:{'Content-Type': 'application/json'},
            credentials: 'include',
            body: JSON.stringify({query:q})
        })
            const data = await res.json();

            const item = data.items?.[0]
            if (!item){
              alert("No Food Found!")
              return
            }

            const calories = Math.round(item.calories)
            totalCals += calories
            labels.push(`${item.name}(${calories} cals)`)

          }
        
        
        mealList[meal] = labels;

        if(meal =='breakfast'){
          breakFast = totalCals
          breakFastQ = labels.join(',')
        }else if (meal =='lunch'){
          lunch = totalCals
          lunchQ = labels.join(',')
        }else if (meal =='dinner'){
          dinner = totalCals
          dinnerQ = labels.join(',')
        }else if (meal =='snacks'){
          snacks = totalCals
          snacksQ = labels.join(',')
        }
        
        updateProgress()
    }catch(err){
      console.error("Failed to get data")
    }
  }
    
 


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




    async function testing(){
      try {
        const tesRest = await fetch('http://localhost:8000/report',{
          method: 'POST',
          headers:{'Content-Type': 'application/json'},
          credentials: 'include',
          body: JSON.stringify({query: 'egg'})
        })
        const data = await tesRest.json();
        console.log('data', data)
        alert('Test pass')
      }catch (error){
        console.error('Failed', error)
         alert('Test Failed')
      }
    }
    
  </script>
  
  
<!--
 <pre>{JSON.stringify(report, null, 2)}</pre>
-->
 
  <header>
    <h1>Report Page</h1>
  </header>
<button on:click={testing}>tester</button>
<div class="progress-container">
  <div class ="progress-wrapper">
    <div class ="progress-label">Daily Calorie Budget</div>
    <progress max = {calorieBudget} value={progress.current}></progress>


  <div class ="progress-info">
    <div>Daily Budget:{calorieBudget} | Calories Eaten: {calsAte} | Budget Remaining:{calsLeft}</div> 
  </div>
  </div>
</div>




<div class= "marco-input-wrapper">
  <div class = "input-box">
    <div>
      <label for = "breakFastLabel">Breakfast</label>
      <input
        id ="breakFastLabel"
        type ="text"
        bind:value={breakFastQ}
        />
        <button on:click={()=> getFoodData('breakfast', breakFastQ)}>Add</button>
    </div>
    <!--User input block where they can log their calories-->
    <!-- It should be that they can search up their food and the food API puts the info into here-->
    <div>
      <label for = "lunchLabel">Lunch</label>
      <input
        id ="lunchLabel"
        type ="text"
        bind:value={lunchQ}
        />
        <button on:click={()=> getFoodData('lunch', lunchQ)}>Add</button>
    </div>
    <div>
      <label for = "dinnerLabel">Dinner</label>
      <input
        id ="dinnerLabel"
        type ="text"
        bind:value={dinnerQ}
        />
        <button on:click={()=> getFoodData('dinner', dinnerQ)}>Add</button>
    </div>
    <div>
      <label for = "snacksLabel">Snacks</label>
      <input
        id ="snacksLabel"
        type ="text"
        bind:value={snacksQ}
        />
        <button on:click={()=> getFoodData('snacks', snacksQ)}>Add</button>
    </div>
  </div>
      
  <div class="macro-progress-wrapper">
    <label for ="protein">Protein</label>
    <progress  id ="protein" max = {calorieBudget} value={progress.current}></progress>

    <label for ="carbs">Carbohydrates</label>
    <progress id ="carbs" max = {calorieBudget} value={progress.current}></progress>

    <label for ="fats">Fats</label>
    <progress id ="fats" max = {calorieBudget} value={progress.current}></progress>
  </div>
</div>


<div class="display-info-wrapper">
  <h2>Meals Eaten Today</h2>

  {#each Object.entries(mealList) as [mealName, items]}
    <div class="meal-stats">
      <h3>{mealName.charAt(0).toUpperCase() + mealName.slice(1)}</h3>
      {#if items.length > 0}
        <ul>
          {#each items as item }
            <li>{item}</li>
          {/each}
        </ul>
        {:else}
          <p>No Food Found! Please Add it!</p>
        {/if}
    </div>
  {/each}
</div>
  
  <!---Subject to change-->
  <style>
    .display-info-wrapper{
      margin-top: 2rem;
      padding: 1.5rem;
      background-color: #b0acaa;
      border-radius: 15px;
      margin-left: auto;
      margin-right: auto;
    }
  
    .meal-stats{
      margin-bottom: 2rem;
    }

    .marco-input-wrapper{
      display:grid;
      grid-template-columns: repeat(2,1fr);
      gap:2rem;
      margin-top:2rem;
    }
    
    .macro-progress-wrapper{
       gap:1rem;
       background-color:#b0acaa;
       border-radius: 10px;
       max-width: 450px;
       padding: 1rem;
    }
    
    .input-box{
      display: grid;
      grid-template-columns: repeat(2,1fr);
      gap:1rem;
      max-width: 450px;
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