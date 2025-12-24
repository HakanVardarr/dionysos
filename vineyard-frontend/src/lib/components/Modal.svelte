<script lang="ts">
    export let show = false;
    export let title = '';
    export let errorMessage = '';
    export let confirmLabel = 'Save';

    export let onConfirm: () => void;
    export let onClose: () => void;

    function handleKeyDown(e: KeyboardEvent) {
        if (e.key === 'Enter') {
            e.preventDefault();
            onConfirm?.();
        }
        if (e.key === 'Escape') {
            onClose?.();
        }
    }
</script>

{#if show}
    <!-- BACKDROP -->
    <div
        class="fixed inset-0 z-50 flex items-center justify-center
               bg-black/50 backdrop-blur-md"
        role="dialog"
        aria-modal="true"
        tabindex="-1"
        on:keydown={handleKeyDown}
    >
        <!-- MODAL -->
        <div
            class="w-full max-w-md
                   rounded-2xl
                   bg-[#0f0f18]
                   border border-white/8
                   shadow-[0_30px_80px_rgba(0,0,0,0.6)]
                   p-6"
        >
            <!-- HEADER -->
            <div class="mb-5">
                <h2 class="text-base font-medium text-gray-100 tracking-tight">
                    {title}
                </h2>
                <div class="mt-2 h-px w-full bg-white/5"></div>
            </div>

            <!-- ERROR -->
            {#if errorMessage}
                <div
                    class="mb-4 rounded-lg
                           bg-red-400/5
                           border border-red-400/10
                           px-3 py-2 text-xs
                           text-red-300"
                >
                    {errorMessage}
                </div>
            {/if}

            <!-- CONTENT -->
            <div class="text-sm text-gray-300 space-y-3">
                <slot />
            </div>

            <!-- ACTIONS -->
            <div class="mt-6 flex justify-end gap-2">
                <!-- CANCEL -->
                <button
                    on:click={onClose}
                    class="px-4 py-2 rounded-lg text-sm
                           bg-white/3
                           hover:bg-white/6
                           text-gray-300
                           transition"
                >
                    Cancel
                </button>

                <!-- CONFIRM -->
                <button
                    on:click={onConfirm}
                    class="px-4 py-2 rounded-lg text-sm
                           bg-purple-500/30
                           hover:bg-purple-500/40
                           text-purple-200
                           transition"
                >
                    {confirmLabel}
                </button>
            </div>
        </div>
    </div>
{/if}
