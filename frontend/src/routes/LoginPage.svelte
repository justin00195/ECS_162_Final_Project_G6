<script lang="ts">


  const handleLogin = async () => {
    try {
      const res = await fetch('http://localhost:5000/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({})
      });

      const data = await res.json();

      if (res.ok) {
        console.log(data.token);
      } else {
        
      }
    } catch (error) {
      console.error("Login error:", error);
    }
  };
</script>

<h1>Login</h1>

<p></p>
