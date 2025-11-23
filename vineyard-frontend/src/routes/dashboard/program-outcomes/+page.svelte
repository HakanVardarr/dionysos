<script lang="ts">
    // import Table from '$lib/components/Table.svelte';
    import { auth } from '$lib/stores/auth';
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';

    let accessToken: string | null = null;
    let code = '';
    let description = '';

    let modalMode: 'edit' | 'delete' | 'add' = 'add';

    let outcomes: string[] = [];
    onMount(async () => {
        auth.subscribe(($auth) => (accessToken = $auth.access))();
        if (!accessToken) goto('/login');
        await fetchOutcomes();
    });

    async function fetchOutcomes() {
        const res = await fetch('http://localhost:8080/api/program-outcomes/', {
            method: 'GET',
            headers: {
                Authorization: `Bearer ${accessToken}`,
                'Content-Type': 'application/json',
            },
        });

        if (res.ok) {
            const data = await res.json();
        }
    }
</script>

<div class="flex flex-col gap-4 items-start text-gray-200">
    <div class="w-full">
        <label for="code" class="block mb-1 text-sm">Code:</label>
        <input
            type="text"
            id="code"
            bind:value={code}
            class="w-full bg-gray-800 text-gray-200 border border-gray-700
                   rounded p-2 placeholder:text-gray-500
                   focus:outline-none focus:ring-2 focus:ring-purple-600 focus:border-purple-600"
            placeholder="Program outcome code"
        />
    </div>
    <div class="w-full">
        <label for="description" class="block mb-1 text-sm">
            Description:
        </label>

        <textarea
            id="description"
            rows="4"
            bind:value={description}
            class="resize-none w-full bg-gray-800 border border-gray-700 text-gray-200 text-sm
                   rounded p-3 placeholder:text-gray-500 shadow
                   focus:outline-none focus:ring-2 focus:ring-purple-600
                   focus:border-purple-600"
            placeholder="Enter description..."
        ></textarea>
    </div>

    <!-- <Table searchEnabled={true} /> -->
</div>
