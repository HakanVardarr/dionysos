<script lang="ts">
    export let errorMessage: string = '';
    export let show = false;
    export let mode: 'add' | 'edit' | 'delete' = 'edit';
    export let data: any = null;
    export let label: string | null = null;
    export let editUsername = '';
    export let editEmail = '';
    export let onSave: () => void;
    export let onDelete: () => void;
    export let onAdd: () => void;
    export let onClose: () => void;

    function handleKeyDown(e: KeyboardEvent) {
        if (e.key === 'Enter') {
            e.preventDefault();
            if (mode === 'add' && onAdd) onAdd();
            else if (mode === 'edit' && onSave) onSave();
            else if (mode === 'delete' && onDelete) onDelete();
        }
    }
</script>

{#if show}
    <div
        class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
        role="dialog"
        aria-modal="true"
    >
        <div class="bg-gray-950 p-6 rounded-xl shadow-xl w-full max-w-md">
            {#if errorMessage}
                <p class="text-red-500 text-sm mb-3">{errorMessage}</p>
            {/if}

            {#if mode === 'add'}
                <h2 class="text-2xl font-bold mb-4 text-purple-500">
                    Add {label}
                </h2>
                <form
                    class="flex flex-col gap-4"
                    on:submit|preventDefault={() => onAdd?.()}
                >
                    <input
                        type="text"
                        bind:value={editUsername}
                        placeholder="Username"
                        class="w-full px-3 py-2 bg-gray-800 border border-gray-700 text-white rounded-md"
                        on:keydown={handleKeyDown}
                    />
                    <input
                        type="email"
                        bind:value={editEmail}
                        placeholder="Email"
                        class="w-full px-3 py-2 bg-gray-800 border border-gray-700 text-white rounded-md"
                        on:keydown={handleKeyDown}
                    />
                    <div class="flex justify-end gap-2">
                        <button
                            type="button"
                            class="px-4 py-2 bg-gray-700 text-white rounded-md cursor-pointer hover:bg-gray-800 transition"
                            on:click={onClose}
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            class="px-4 py-2 bg-purple-600 text-white rounded-md cursor-pointer hover:bg-purple-700 transition"
                        >
                            Add
                        </button>
                    </div>
                </form>
            {:else if mode === 'edit'}
                <h2 class="text-2xl font-bold mb-4 text-purple-500">
                    Edit {label}
                </h2>
                <form
                    class="flex flex-col gap-4"
                    on:submit|preventDefault={() => onSave?.()}
                >
                    <input
                        type="text"
                        bind:value={editUsername}
                        class="w-full px-3 py-2 bg-gray-800 border border-gray-700 text-white rounded-md"
                        on:keydown={handleKeyDown}
                    />
                    <input
                        type="email"
                        bind:value={editEmail}
                        class="w-full px-3 py-2 bg-gray-800 border border-gray-700 text-white rounded-md"
                        on:keydown={handleKeyDown}
                    />
                    <div class="flex justify-end gap-2">
                        <button
                            type="button"
                            class="px-4 py-2 bg-gray-700 text-white rounded-md cursor-pointer hover:bg-gray-800 transition"
                            on:click={onClose}
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            class="px-4 py-2 bg-purple-600 text-white rounded-md cursor-pointer hover:bg-purple-700 transition"
                        >
                            Save
                        </button>
                    </div>
                </form>
            {:else if mode === 'delete'}
                <h2 class="text-2xl font-bold mb-4 text-red-500">
                    Delete {label}
                </h2>
                <p>
                    Are you sure you want to delete <strong
                        >{data.username}</strong
                    >?
                </p>
                <div class="flex justify-end gap-2 mt-4">
                    <button
                        class="px-4 py-2 bg-gray-700 text-white rounded-md cursor-pointer hover:bg-gray-800 transition"
                        on:click={onClose}
                    >
                        Cancel
                    </button>
                    <button
                        class="px-4 py-2 bg-red-600 text-white rounded-md cursor-pointer hover:bg-red-700 transition"
                        on:click={onDelete}
                    >
                        Delete
                    </button>
                </div>
            {/if}
        </div>
    </div>
{/if}
