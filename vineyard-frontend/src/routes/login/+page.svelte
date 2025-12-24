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

<div class="min-h-screen flex items-center justify-center bg-[#0b0b10]">
    <div
        class="bg-[#0f0f16] p-10 rounded-2xl shadow-lg w-full max-w-md border border-white/5"
    >
        <h1
            class="text-3xl font-extrabold mb-6 text-center text-purple-400 tracking-wide"
        >
            Dionysos Login
        </h1>

        {#if errorMessage}
            <p class="text-red-500 text-sm mb-4 text-center font-medium">
                {errorMessage}
            </p>
        {/if}

        <form on:submit|preventDefault={login} class="space-y-6">
            <div>
                <label
                    for="username"
                    class="block text-sm font-medium mb-1 text-gray-400"
                >
                    Username
                </label>
                <input
                    id="username"
                    type="text"
                    placeholder="Username"
                    bind:value={username}
                    class="w-full px-4 py-2 bg-[#0b0b10] border border-white/10 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500 transition"
                    required
                />
            </div>

            <div>
                <label
                    for="password"
                    class="block text-sm font-medium mb-1 text-gray-400"
                >
                    Password
                </label>
                <input
                    id="password"
                    type="password"
                    placeholder="Password"
                    bind:value={password}
                    class="w-full px-4 py-2 bg-[#0b0b10] border border-white/10 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500 transition"
                    required
                />
            </div>

            <button
                type="submit"
                class="w-full py-2 px-4 bg-purple-600/20 text-purple-300 font-semibold rounded-lg hover:bg-purple-600/30 transition"
            >
                Login
            </button>
        </form>

        <p class="text-gray-400 text-sm mt-4 text-center">
            Welcome back! Please enter your credentials.
        </p>
    </div>
</div>
