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
    let searchTerm = '';

    function triggerBulkUpload() {
        fileInput.click();
    }

    function handleFileChange(e: Event) {
        const target = e.target as HTMLInputElement;
        if (target.files?.length && onBulkAdd) {
            onBulkAdd(target.files[0]);
        }
    }

    $: filteredData = data.filter((row) =>
        columns.some((c) =>
            String(row[c.key] ?? '')
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
</script>

<div class="space-y-4">
    <!-- TOP BAR -->
    {#if searchEnabled || addLabel || onBulkAdd}
        <div class="flex items-center gap-3">
            <!-- SEARCH -->
            {#if searchEnabled}
                <div class="relative">
                    <input
                        bind:value={searchTerm}
                        placeholder="Search"
                        class="w-64 rounded-lg
                               bg-[#0e0e15]
                               border border-white/5
                               px-4 py-2 text-sm text-gray-300
                               placeholder-gray-500
                               outline-none
                               focus:border-purple-500/30
                               focus:bg-[#11111a]
                               transition"
                    />
                </div>
            {/if}

            <!-- ACTION BUTTONS -->
            <div class="flex gap-2 ml-auto">
                {#if onBulkAdd}
                    <button
                        on:click={triggerBulkUpload}
                        class="px-3 py-2 rounded-lg text-sm
                               bg-white/5
                               border border-white/10
                               text-gray-400
                               hover:bg-white/10
                               transition"
                    >
                        Bulk upload
                    </button>
                {/if}

                {#if addLabel}
                    <button
                        on:click={onAdd}
                        class="px-4 py-2 rounded-lg text-sm
                               bg-purple-500/15
                               border border-purple-500/20
                               text-purple-300
                               hover:bg-purple-500/25
                               transition"
                    >
                        {addLabel}
                    </button>
                {/if}
            </div>

            <input
                type="file"
                accept=".csv,.xlsx"
                bind:this={fileInput}
                class="hidden"
                on:change={handleFileChange}
            />
        </div>
    {/if}

    <!-- TABLE -->
    <div
        class="rounded-xl border border-white/10
               bg-[#0e0e15] overflow-hidden"
    >
        <table class="w-full text-sm text-gray-200">
            <thead class="border-b border-white/10 bg-[#0e0e15]">
                <tr>
                    {#each columns as col}
                        <th
                            class="px-5 py-3 text-left text-xs
                                   uppercase tracking-wide
                                   text-gray-400"
                        >
                            {col.label}
                        </th>
                    {/each}

                    {#if actions.length}
                        <th
                            class="px-5 py-3 text-right text-xs
                                   uppercase tracking-wide
                                   text-gray-400 w-32"
                        >
                        </th>
                    {/if}
                </tr>
            </thead>

            <tbody class="divide-y divide-white/5">
                {#each paginatedData as row}
                    <tr
                        class="hover:bg-white/5 transition cursor-pointer"
                        on:click={() => onRowClick?.(row)}
                    >
                        {#each columns as col}
                            <td class="px-5 py-3">
                                {row[col.key]}
                            </td>
                        {/each}

                        {#if actions.length}
                            <td class="px-5 py-3 text-right">
                                <div class="flex justify-end gap-3">
                                    {#each actions as action}
                                        <button
                                            class="text-xs font-medium
                                                   px-2 py-1 rounded-md
                                                   text-purple-300
                                                   bg-purple-500/5
                                                   border border-purple-500/10
                                                   hover:bg-purple-500/10
                                                   transition"
                                            on:click={(e) => {
                                                e.stopPropagation();
                                                action.callback(row);
                                            }}
                                        >
                                            {action.label}
                                        </button>
                                    {/each}
                                </div>
                            </td>
                        {/if}
                    </tr>
                {/each}

                {#if paginatedData.length === 0}
                    <tr>
                        <td
                            colspan={columns.length + (actions.length ? 1 : 0)}
                            class="px-6 py-10 text-center text-gray-500"
                        >
                            No results found
                        </td>
                    </tr>
                {/if}
            </tbody>
        </table>
    </div>

    <!-- PAGINATION -->
    {#if totalPages > 1}
        <div class="flex items-center justify-between text-sm text-gray-400">
            <span>
                Page {currentPage} of {totalPages}
            </span>

            <div class="flex gap-1">
                {#each Array(totalPages) as _, i}
                    <button
                        on:click={() => (currentPage = i + 1)}
                        class="px-3 py-1 rounded-md transition
                               {currentPage === i + 1
                            ? 'bg-purple-500/30 text-purple-200'
                            : 'hover:bg-white/10'}"
                    >
                        {i + 1}
                    </button>
                {/each}
            </div>
        </div>
    {/if}
</div>
