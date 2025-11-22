<script lang="ts">
    import { goto } from '$app/navigation';
    import { auth } from '$lib/stores/auth';
    import { onMount } from 'svelte';

    let username = '';
    let password = '';
    let errorMessage = '';

    onMount(() => {
        const unsubscribe = auth.subscribe(($auth) => {
            if ($auth.access) {
                goto('/dashboard');
            }
        });
    });

    async function login() {
        errorMessage = '';
        const res = await fetch('http://localhost:8080/api/token/login/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password }),
        });

        if (!res.ok) {
            errorMessage = 'Invalid username or password';
            return;
        }

        const data = await res.json();
        auth.set({
            access: data.access,
            refresh: data.refresh,
        });
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
