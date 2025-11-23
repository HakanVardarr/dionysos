<script lang="ts">
    import { auth } from '$lib/stores/auth';
    import { checkToken } from '$lib/auth';
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import { page } from '$app/state';
    import { capitalize } from '$lib/utils';

    let username = '';
    let role = '';
    let loading = true;

    const links = [
        { name: 'Teachers', href: '/dashboard/teachers' },
        { name: 'Students', href: '/dashboard/students' },
        { name: 'Courses', href: '/dashboard/courses' },
        { name: 'Program Outcomes', href: '/dashboard/program-outcomes' },
    ];

    onMount(async () => {
        let accessToken: string | null = null;
        auth.subscribe(($auth) => (accessToken = $auth.access))();

        if (!accessToken) {
            goto('/login');
            return;
        }

        const valid = await checkToken(accessToken);
        if (!valid) {
            auth.set({ access: null, refresh: null });
            localStorage.removeItem('access');
            localStorage.removeItem('refresh');
            goto('/login');
        } else {
            loading = false;
        }

        const res = await fetch('http://localhost:8080/api/me/', {
            method: 'GET',
            headers: {
                Authorization: `Bearer ${accessToken}`,
                'Content-Type': 'application/json',
            },
        });

        if (!res.ok) return;

        const data = await res.json();
        username = data['username'];
        role = data['role'];
    });

    function logout() {
        auth.set({ access: null, refresh: null });
        localStorage.removeItem('access');
        localStorage.removeItem('refresh');
        goto('/login');
    }
</script>

{#if loading}
    <p class="text-center mt-20 text-purple-500 font-medium">
        Checking authentication...
    </p>
{:else}
    <div class="flex h-screen bg-gray-900">
        <aside
            class="w-64 bg-gray-950 text-gray-300 flex flex-col px-6 py-8 gap-6 shadow-lg"
        >
            <div class="mb-6">
                <div class="text-xl font-bold text-purple-500">{username}</div>
                <div class="text-gray-400 text-sm">{capitalize(role)}</div>
            </div>

            <nav class="flex flex-col gap-2 flex-1">
                {#each links as link}
                    <a
                        href={link.href}
                        class="px-3 py-2 rounded transition hover:bg-purple-700 hover:text-white
                            {page.url.pathname === link.href
                            ? 'bg-purple-700 text-white font-bold'
                            : ''}"
                    >
                        {link.name}
                    </a>
                {/each}
            </nav>

            <button
                on:click={logout}
                class="mt-auto bg-purple-600 hover:bg-purple-700 text-white px-3 py-2 rounded transition"
            >
                Logout
            </button>
        </aside>

        <div class="flex-1 flex flex-col">
            <header class="w-full bg-gray-900 px-6 py-4 shadow-md"></header>

            <main class="p-6 flex-1 overflow-auto text-gray-100">
                <slot />
            </main>
        </div>
    </div>
{/if}
