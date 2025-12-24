<script lang="ts">
    import { auth } from '$lib/stores/auth';
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import Modal from '$lib/components/Modal.svelte';
    import Table from '$lib/components/Table.svelte';
    import type { Column, Action } from '$lib/components/Table.svelte';

    type ModalMode = 'add' | 'edit' | 'delete';
    type ModalState = {
        open: boolean;
        mode: ModalMode;
        outcome: ProgramOutcome | null;
        form: {
            code: string;
            description: string;
        };
        error: string;
    };
    type ProgramOutcome = {
        id: number;
        code: string;
        description: string;
    };

    let outcomes: ProgramOutcome[] = [];
    let modal: ModalState = {
        open: false,
        mode: 'add',
        outcome: null,
        form: {
            code: '',
            description: '',
        },
        error: '',
    };

    const columns: Column[] = [
        { key: 'code', label: 'Code' },
        { key: 'description', label: 'Description' },
    ];

    const actions: Action<ProgramOutcome>[] = [
        {
            label: 'Edit',
            colorClass: 'text-blue-400',
            callback: (t) => openModal('edit', t),
        },
        {
            label: 'Delete',
            colorClass: 'text-red-400',
            callback: (t) => openModal('delete', t),
        },
    ];

    function openModal(mode: ModalMode, outcome: ProgramOutcome | null = null) {
        modal = {
            open: true,
            mode,
            outcome,
            form: outcome
                ? {
                      code: outcome.code,
                      description: outcome.description,
                  }
                : {
                      code: '',
                      description: '',
                  },
            error: '',
        };
    }

    function closeModal() {
        modal = {
            open: false,
            mode: 'add',
            outcome: null,
            form: {
                code: '',
                description: '',
            },
            error: '',
        };
    }

    async function addOutcome() {
        modal.error = '';
        const { code, description } = modal.form;
        if (!code || !description) {
            modal.error = 'Please fill in all fields';
            return;
        }

        const res = await fetch('http://localhost:8080/api/program-outcomes/', {
            method: 'POST',
            headers: {
                Authorization: `Bearer ${accessToken}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ code, description }),
        });

        const data = await res.json();
        if (!res.ok) {
            modal.error =
                data.code?.[0] ||
                data.description?.[0] ||
                data.detail ||
                'Unknown error';
            return;
        }

        closeModal();
        await fetchOutcomes();
    }

    async function saveEdit() {
        if (!modal.outcome) return;

        const res = await fetch(
            `http://localhost:8080/api/program-outcomes/${modal.outcome.id}/`,
            {
                method: 'PUT',
                headers: {
                    Authorization: `Bearer ${accessToken}`,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    code: modal.form.code,
                    description: modal.form.description,
                }),
            },
        );

        const data = await res.json();
        if (!res.ok) {
            modal.error =
                data.code?.[0] ||
                data.description?.[0] ||
                data.detail ||
                'Unknown error';
            return;
        }

        closeModal();
        await fetchOutcomes();
    }

    async function confirmDelete() {
        if (!modal.outcome) return;

        const res = await fetch(
            `http://localhost:8080/api/program-outcomes/${modal.outcome.id}/`,
            {
                method: 'DELETE',
                headers: { Authorization: `Bearer ${accessToken}` },
            },
        );

        if (!res.ok) {
            const data = await res.json();
            modal.error = data.detail || 'Failed to delete';
            return;
        }

        closeModal();
        await fetchOutcomes();
    }

    let accessToken: string | null = null;
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
            console.log(data);
            outcomes = data['program-outcomes'];
        }
    }
</script>

<h1 class="text-3xl font-semibold text-white tracking-tight">
    Program Outcomes
</h1>

<p class="text-sm text-gray-400 mt-1 mb-6 max-w-xl">
    Define, edit and manage program-level learning outcomes.
</p>

<div
    class="rounded-2xl
           bg-[#0e0e15]
           border border-white/10
           shadow-xl shadow-black/30
           p-4"
>
    <Table
        {columns}
        {actions}
        data={outcomes}
        searchEnabled={true}
        addLabel="New Outcome"
        onAdd={() => openModal('add')}
        onRowClick={(row) => {
            console.log(row);
        }}
    />
</div>

{#if modal.open}
    <Modal
        show={modal.open}
        title={modal.mode === 'add'
            ? 'Add Outcome'
            : modal.mode === 'edit'
              ? 'Edit Outcome'
              : 'Delete Outcome'}
        errorMessage={modal.error}
        confirmLabel={modal.mode === 'delete'
            ? 'Delete'
            : modal.mode === 'add'
              ? 'Add'
              : 'Save'}
        onConfirm={modal.mode === 'delete'
            ? confirmDelete
            : modal.mode === 'add'
              ? addOutcome
              : saveEdit}
        onClose={closeModal}
    >
        {#if modal.mode === 'delete'}
            <p class="text-sm text-gray-300">
                Are you sure you want to delete
                <span class="font-medium text-gray-100">
                    {modal.outcome?.code}
                </span>
                ?
            </p>
        {:else}
            <input
                bind:value={modal.form.code}
                placeholder="Outcome Code"
                class="w-full rounded-lg
                       bg-white/3
                       border border-white/10
                       px-3 py-2 text-sm
                       text-gray-200
                       placeholder-gray-500
                       outline-none
                       focus:border-purple-400/40
                       transition"
            />

            <textarea
                bind:value={modal.form.description}
                placeholder="Description"
                rows="3"
                class="w-full mt-3 rounded-lg
                       bg-white/3
                       border border-white/10
                       px-3 py-2 text-sm
                       text-gray-200
                       placeholder-gray-500
                       outline-none
                       resize-none
                       focus:border-purple-400/40
                       transition"
            ></textarea>
        {/if}
    </Modal>
{/if}
