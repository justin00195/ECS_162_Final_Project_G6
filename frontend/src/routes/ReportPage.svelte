<script lang="ts">
    import { onMount } from 'svelte';
  
    let report: any = {};
  
    onMount(async () => {
      const res = await fetch('http://localhost:5000/report');
      report = await res.json();
    });
  </script>
  
  <h1>Report Page</h1>
  <pre>{JSON.stringify(report, null, 2)}</pre>
  