<script lang="ts">
    import { onMount } from 'svelte';
    import {Tween} from 'svelte/motion'
    import { cubicOut } from 'svelte/easing';
  
    let report: any = {};
  
    onMount(async () => {
      const res = await fetch('http://localhost:8000/report');
      report = await res.json();
    });


    let progress = new Tween(0, {
      duration: 500,
      easing: cubicOut
    })
    let inputValue = 0;
    function updateProgress(){
      let val = Math.min(100, Math.max(0, Number(inputValue)))
      progress.target = val
    }
  </script>
  
  
<pre>{JSON.stringify(report, null, 2)}</pre>
  <header>
    <h1>Report Page</h1>
  </header>
    
    <div class="progress-container">
      <progress max = "100" value={progress.current}></progress>
      <input
        type ="number"
        bind:value={inputValue}
        min ="0"
        max ="100"
        on:change={updateProgress}
      />
    </div>
  
  
  <!---Subject to change-->
  <style>

    .progress-container {
      display: flex;
      justify-content: center;
      width: 500px;
      margin: 5rem auto 0 auto;
    }
    progress{
      width: 100%;
      height: 30px;
      appearance: none;
      border-radius: 15px;
      overflow: hidden;
      
    }
  </style>