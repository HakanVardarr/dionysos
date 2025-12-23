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
    export let onBulkAdd: ((file: File) => void) | null = null;
    export let onRowClick: ((row: any) => void) | null = null;

    let fileInput: HTMLInputElement;

    function triggerBulkUpload() {
        fileInput.click();
    }

    function handleFileChange(event: Event) {
        const target = event.target as HTMLInputElement;
        if (target.files && target.files.length > 0) {
            const file = target.files[0];
            if (onBulkAdd) onBulkAdd(file);
        }
    }

    let searchTerm = '';

    $: filteredData = data.filter((row) =>
        columns.some((col) =>
            String(row[col.key])
                .toLowerCase()
                .includes(searchTerm.toLowerCase()),
        ),
    );

    let currentPage = 1;
    let pageSize = 10;

    $: totalPages = Math.ceil(filteredData.length / pageSize);

    $: paginatedData = filteredData.slice(
        (currentPage - 1) * pageSize,
        currentPage * pageSize,
    );

    function goToPage(page: number) {
        if (page >= 1 && page <= totalPages) {
            currentPage = page;
        }
    }

    function nextPage() {
        if (currentPage < totalPages) currentPage += 1;
    }

    function prevPage() {
        if (currentPage > 1) currentPage -= 1;
    }
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

            <button
                type="button"
                on:click={onAdd}
                class="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 transition"
            >
                {addLabel}
            </button>

            {#if onBulkAdd}
                <button
                    type="button"
                    on:click={triggerBulkUpload}
                    class="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 transition"
                >
                    Bulk Upload
                </button>
            {/if}
            <input
                type="file"
                accept=".csv,.xlsx"
                bind:this={fileInput}
                class="hidden"
                on:change={handleFileChange}
            />
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
                {#each paginatedData as row}
                    <tr
                        class="hover:bg-gray-800 cursor-pointer"
                        on:click={() => onRowClick?.(row)}
                    >
                        {#each columns as col}
                            <td class="px-6 py-4">{row[col.key]}</td>
                        {/each}
                        {#if actions.length > 0}
                            <td class="px-6 py-4 flex gap-2">
                                {#each actions as action}
                                    <button
                                        type="button"
                                        class={`flex-1 text-sm ${action.colorClass ?? 'text-blue-400'}`}
                                        on:click={(e) => {
                                            e.stopPropagation();
                                            action.callback(row);
                                        }}
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

    {#if totalPages > 1}
        <div class="flex justify-center items-center gap-2 mt-4">
            <button
                on:click={prevPage}
                class="px-3 py-1 bg-gray-800 rounded hover:bg-gray-700 transition"
                disabled={currentPage === 1}
            >
                Prev
            </button>

            {#each Array(totalPages) as _, i}
                <button
                    on:click={() => goToPage(i + 1)}
                    class="px-3 py-1 rounded hover:bg-gray-700 transition
                           {currentPage === i + 1
                        ? 'bg-purple-600 text-white'
                        : 'bg-gray-800 text-gray-200'}"
                >
                    {i + 1}
                </button>
            {/each}

            <button
                on:click={nextPage}
                class="px-3 py-1 bg-gray-800 rounded hover:bg-gray-700 transition"
                disabled={currentPage === totalPages}
            >
                Next
            </button>
        </div>
    {/if}
</div>
