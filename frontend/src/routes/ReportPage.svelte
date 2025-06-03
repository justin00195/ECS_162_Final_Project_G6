<script lang="ts">
  import { onMount } from 'svelte';
  import {Tween} from 'svelte/motion'
  import {get} from 'svelte/store';
  import { cubicOut } from 'svelte/easing';
  import { allTDEE } from '../stores/tdee';
  import '../assets/report.scss';
  
  

  let report: any = {};

  // calorieBudget should be calcualted from the goalpage
  // some how need to pull info from api about macros 
  //3 main marcos are protien, fats, carbs
  const tdee = get(allTDEE)
  if (tdee === null){
    throw new Error("Please LOGIN for TDEE value")
  }
  let calorieBudget = tdee - 1000;
  let breakFast = 0;
  let lunch = 0;
  let dinner = 0;
  let snacks = 0;

  let breakFastQ = '';
  let lunchQ = '';
  let dinnerQ = '';
  let snacksQ = '';

  
  let totalProtein = 0;
  let totalCarbs = 0;
  let totalFats = 0;
  


  type mealType = 'breakfast' | 'lunch' |'dinner'|'snacks';
  type foodItem = {
    name: string;
    grams: number;
  }

  let mealList: Record<mealType, foodItem[]>={
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
        let newFood: foodItem[] = []

        for (const q of queries){
          const res = await fetch('http://localhost:8000/report',{
          method: 'POST',
          headers:{'Content-Type': 'application/json'},
          credentials: 'include',
          body: JSON.stringify({query:q})
      })
          const data = await res.json();

         if (data.items){
          for(const item of data.items){
            totalProtein += item.protein_g || 0;
            totalCarbs += item.carbohydrates_total_g || 0;
            totalFats += item.fat_total_g || 0;
            totalCals += item.calories || 0;
            labels.push(item.name)
            
            newFood.push({
              name: item.name,
              grams: item.serving_size_g
            })
          }
         }
        }
      
        mealList = {...mealList, [meal]:newFood}
      
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


  
</script>


<!--
<pre>{JSON.stringify(report, null, 2)}</pre>
-->

<h1>Report Page</h1>
<div class="progress-container">
<div class ="progress-wrapper">
  <div class ="progress-label">Daily Calorie Budget</div>
  <progress class = "cals-prog" max = {calorieBudget} value={progress.current}></progress>


<div class ="progress-info">
  <div>Daily Budget:{calorieBudget} | Calories Eaten: {calsAte} | Budget Remaining:{calsLeft}</div> 
</div>
</div>
</div>


<div class = "report-layout">
<div class="left-side">
  <div class= "marco-input-wrapper">
    <div class = "input-box">
      <div>
        <label for = "breakFastLabel">Breakfast</label>
        <input
          id ="breakFastLabel"
          type ="text"
          bind:value={breakFastQ}
          />
          <button class ="add-button" on:click={()=> getFoodData('breakfast', breakFastQ)}>Add</button>
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
          <button class ="add-button" on:click={()=> getFoodData('lunch', lunchQ)}>Add</button>
      </div>
      <div>
        <label for = "dinnerLabel">Dinner</label>
        <input
          id ="dinnerLabel"
          type ="text"
          bind:value={dinnerQ}
          />
          <button class ="add-button" on:click={()=> getFoodData('dinner', dinnerQ)}>Add</button>
      </div>
      <div>
        <label for = "snacksLabel">Snacks</label>
        <input
          id ="snacksLabel"
          type ="text"
          bind:value={snacksQ}
          />
          <button class ="add-button" on:click={()=> getFoodData('snacks', snacksQ)}>Add</button>
      </div>
    </div>
   
    <div class="macro-progress-wrapper">

      <div class ="macro-progress">
        <label for ="protein"> Total protein ate today {totalProtein}</label>
        <progress class ="protein-prog" id ="protein" max = {170} value={totalProtein.toFixed(2)}></progress>
      </div>
      


      <div class ="macro-progress">
        <label for ="carbs">Total carbohydrates ate today {totalCarbs}</label>
        <progress class ="carbs-prog"  id ="carbs" max = {250} value={totalCarbs.toFixed(2)}></progress>
      </div>
        

      <div class ="macro-progress">
        <label for ="fats">Total fats ate today {totalFats}</label>
        <progress class="fats-prog" id ="fats" max = {75} value={totalFats.toFixed(2)}></progress>
      </div>
        
    </div>
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
              <li>{item.name} - {item.grams}g</li>
            {/each}
          </ul>
          {:else}
            <p>No Food Found! Please Add it!</p>
          {/if}
      </div>
    {/each}
  </div>
</div>


 




<!---Subject to change-->
<style>

  
 

</style>