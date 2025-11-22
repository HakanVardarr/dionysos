<script lang="ts">
    import { auth } from '$lib/stores/auth';
    import { checkToken } from '$lib/auth';
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';

    let loading = true;
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
    });
</script>

{#if loading}
    <p>Checking authentication...</p>
{:else}
    <ul>
        <li><a href="/dashboard/teachers">Teachers</a></li>
        <li><a href="/dashboard/students">Students</a></li>
        <li><a href="/dashboard/courses">Courses</a></li>
        <li><a href="/dashboard/program-outcomes">Program Outcomes</a></li>
    </ul>

    <slot />
{/if}
