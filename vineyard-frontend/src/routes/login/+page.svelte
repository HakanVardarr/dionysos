<script lang="ts">
    let username = '';
    let password = '';
    let errorMessage = '';

    async function login() {
        errorMessage = '';
        const res = await fetch('http://localhost:8080/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password }),
        });

        if (!res.ok) {
            errorMessage = 'Invalid username or password';
            return;
        }

        const data = await res.json();
        localStorage.setItem('access', data.access);
        localStorage.setItem('refresh', data.refresh);
    }
</script>

<h1>Login</h1>
<form on:submit|preventDefault={login}>
    <input type="text" placeholder="Username" bind:value={username} required />
    <input
        type="password"
        placeholder="Password"
        bind:value={password}
        required
    />
    <button type="submit">Login</button>
</form>

{#if errorMessage}
    <p style="color:red">{errorMessage}</p>
{/if}
