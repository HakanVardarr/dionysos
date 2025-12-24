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

    const allLinks = [
        { name: 'Teachers', href: '/dashboard/teachers' },
        { name: 'Students', href: '/dashboard/students' },
        { name: 'Courses', href: '/dashboard/courses' },
        { name: 'Outcomes', href: '/dashboard/program-outcomes' },
        { name: 'Reports', href: '/dashboard/reports' },
    ];

    let links: any[] = [];
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
            return;
        }

        const res = await fetch('http://localhost:8080/api/me/', {
            headers: { Authorization: `Bearer ${accessToken}` },
        });

        if (res.ok) {
            const data = await res.json();
            username = data.username;
            role = data.role;

            if (role === 'head') links = allLinks;
            else if (role === 'teacher')
                links = allLinks.filter(
                    (l) => l.name === 'Courses' || l.name === 'Reports',
                );
            else links = [];
        }

        loading = false;
    });

    function logout() {
        auth.set({ access: null, refresh: null });
        localStorage.removeItem('access');
        localStorage.removeItem('refresh');
        goto('/login');
    }
</script>

{#if loading}
    <p class="text-center mt-24 text-purple-400 font-medium">
        Checking authentication…
    </p>
{:else}
    <div class="flex h-screen bg-[#0b0b10] text-gray-100">
        <aside
            class="w-64 bg-[#0f0f16] border-r border-white/5
                   flex flex-col px-5 py-6 gap-6"
        >
            <div class="flex items-center gap-3 pb-4 border-b border-white/5">
                <div
                    class="w-10 h-10 rounded-full bg-purple-600/20
                           flex items-center justify-center
                           text-purple-400 font-bold"
                >
                    {username.charAt(0).toUpperCase()}
                </div>

                <div>
                    <div class="font-semibold text-white">
                        {username}
                    </div>
                    <div class="text-xs text-gray-400">
                        {capitalize(role)}
                    </div>
                </div>
            </div>

            <nav class="flex flex-col gap-1 flex-1 pt-2">
                {#each links as link}
                    <a
                        href={link.href}
                        class="relative px-4 py-2 rounded-lg text-sm transition
                            hover:bg-purple-600/10 hover:text-purple-300
                            {page.url.pathname === link.href
                            ? 'bg-purple-600/15 text-purple-300 font-medium'
                            : 'text-gray-400'}"
                    >
                        {#if page.url.pathname === link.href}
                            <span
                                class="absolute left-0 top-1/2 -translate-y-1/2
                                       w-1 h-6 bg-purple-500 rounded-r"
                            ></span>
                        {/if}
                        {link.name}
                    </a>
                {/each}
            </nav>

            <button
                on:click={logout}
                class="mt-auto w-full flex items-center justify-center
                       gap-2 rounded-lg px-4 py-2 text-sm
                       bg-red-500/10 text-red-400
                       hover:bg-red-500/20 transition"
            >
                Logout
            </button>
        </aside>

        <div class="flex-1 flex flex-col overflow-hidden">
            <main class="flex-1 overflow-auto p-8">
                <slot />
            </main>
        </div>
    </div>
{/if}
