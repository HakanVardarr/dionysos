<script lang="ts">
    import { goto } from '$app/navigation';

    let username = '';
    let email = '';
    let password = '';
    let confirmPassword = '';

    let errorMessage = '';
    async function createHead() {
        errorMessage = '';
        if (password != confirmPassword) {
            errorMessage = 'Passwords do not match';
            return;
        }

        const res = await fetch(
            'http://localhost:8080/api/register-head-user/',
            {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, email, password }),
            },
        );

        if (!res.ok) {
            const data = await res.json();
            errorMessage = data.error;
            return;
        }

        goto('/login');
    }
</script>

<h1>Create Department Head</h1>
<form on:submit|preventDefault={createHead}>
    <input type="text" placeholder="Username" bind:value={username} required />
    <input type="email" placeholder="Email" bind:value={email} required />
    <input
        type="password"
        placeholder="Password"
        bind:value={password}
        required
    />
    <input
        type="password"
        placeholder="Confirm Password"
        bind:value={confirmPassword}
        required
    />
    <button type="submit">Create</button>
</form>

{#if errorMessage}
    <p style="color:red">{errorMessage}</p>
{/if}
