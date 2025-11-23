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
        goto('/dashboard');
    }
</script>

<div class="min-h-screen flex items-center justify-center bg-gray-900">
    <div class="bg-gray-950 p-10 rounded-2xl shadow-xl w-full max-w-md">
        <h1 class="text-3xl font-bold mb-6 text-center text-purple-500">
            Login
        </h1>

        {#if errorMessage}
            <p class="text-red-500 text-sm mb-4 text-center">{errorMessage}</p>
        {/if}

        <form on:submit|preventDefault={login} class="space-y-6">
            <div>
                <label
                    for="username"
                    class="block text-sm font-medium mb-1 text-gray-300"
                >
                    Username
                </label>
                <input
                    id="username"
                    type="text"
                    placeholder="Username"
                    bind:value={username}
                    class="w-full px-4 py-2 bg-gray-800 border border-gray-700 text-white rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition"
                    required
                />
            </div>

            <div>
                <label
                    for="password"
                    class="block text-sm font-medium mb-1 text-gray-300"
                >
                    Password
                </label>
                <input
                    id="password"
                    type="password"
                    placeholder="Password"
                    bind:value={password}
                    class="w-full px-4 py-2 bg-gray-800 border border-gray-700 text-white rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition"
                    required
                />
            </div>

            <button
                type="submit"
                class="w-full py-2 px-4 bg-purple-600 text-white font-semibold rounded-md hover:bg-purple-700 transition-colors"
            >
                Login
            </button>
        </form>

        <p class="text-gray-400 text-sm mt-4 text-center">
            Welcome to Dionysos
        </p>
    </div>
</div>
