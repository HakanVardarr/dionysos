<script lang="ts">
    import { goto } from '$app/navigation';
    import CreateHeadForm from '$lib/components/CreateHeadForm.svelte';
    import { onMount } from 'svelte';

    let canCreateHead = false;
    let loading = true;

    onMount(async () => {
        const res = await fetch('http://localhost:8080/api/check-head-user/');
        if (res.ok) {
            const data = await res.json();
            canCreateHead = data.can_create_head;
        }
        loading = false;

        if (!canCreateHead) {
            goto('/login');
        }
    });
</script>

{#if loading}
    <h1>Loading....</h1>
{:else if canCreateHead}
    <CreateHeadForm />
{/if}
