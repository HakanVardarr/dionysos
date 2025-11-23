<script context="module" lang="ts">
    export type Column = { key: string; label: string };
    export type Action<T = any> = {
        label: string;
        colorClass?: string;
        callback: (item: T) => void;
    };
</script>

<script lang="ts">
    export let data: any[] = [];
    export let columns: Column[] = [];
    export let actions: Action[] = [];
    export let searchEnabled = true;
    export let addLabel: string | null = null;
    export let onAdd: (() => void) | null = null;

    let searchTerm = '';

    $: filteredData = data.filter((row) =>
        columns.some((col) =>
            String(row[col.key])
                .toLowerCase()
                .includes(searchTerm.toLowerCase()),
        ),
    );
</script>

<div class="flex flex-col p-6 gap-4">
    {#if searchEnabled || addLabel}
        <div class="flex justify-between items-center gap-2">
            {#if searchEnabled}
                <input
                    type="text"
                    placeholder="Search..."
                    bind:value={searchTerm}
                    class="flex-1 px-3 py-2 rounded-md bg-gray-800 border border-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
            {/if}

            {#if addLabel && onAdd}
                <button
                    type="button"
                    on:click={onAdd}
                    class="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 transition"
                >
                    {addLabel}
                </button>
            {/if}
        </div>
    {/if}

    <div class="overflow-x-auto rounded-lg border border-gray-700">
        <table
            class="min-w-full divide-y divide-gray-700 bg-gray-900 text-white"
        >
            <thead class="bg-purple-800">
                <tr>
                    {#each columns as col}
                        <th class="px-6 py-3 text-left text-sm font-semibold"
                            >{col.label}</th
                        >
                    {/each}
                    {#if actions.length > 0}
                        <th class="px-6 py-3 text-left text-sm font-semibold"
                        ></th>
                    {/if}
                </tr>
            </thead>
            <tbody class="divide-y divide-gray-700">
                {#each filteredData as row}
                    <tr>
                        {#each columns as col}
                            <td class="px-6 py-4">{row[col.key]}</td>
                        {/each}
                        {#if actions.length > 0}
                            <td class="px-6 py-4 flex gap-2">
                                {#each actions as action}
                                    <button
                                        type="button"
                                        class={`flex-1 text-sm ${action.colorClass ?? 'text-blue-400'}`}
                                        on:click={() => action.callback(row)}
                                    >
                                        <span
                                            class="hover:underline cursor-pointer"
                                            >{action.label}</span
                                        >
                                    </button>
                                {/each}
                            </td>
                        {/if}
                    </tr>
                {/each}
            </tbody>
        </table>
    </div>
</div>
