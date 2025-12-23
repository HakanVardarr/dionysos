<script lang="ts">
    import { auth } from '$lib/stores/auth';
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import Modal from '$lib/components/Modal.svelte';
    import Table from '$lib/components/Table.svelte';
    import type { Column, Action } from '$lib/components/Table.svelte';

    let outcomes: any[] = [];

    let showModal = false;
    let modalOutcome: any = null;
    let modalMode: 'edit' | 'edit-outcome' | 'delete' | 'add-outcome' | 'add' =
        'add-outcome';
    let editUsername = '';
    let editEmail = '';
    let errorMessage = '';

    type ProgramOutcome = {
        id: number;
        code: string;
        description: string;
    };

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

    function openModal(
        mode: 'edit' | 'delete' | 'add' | 'add-outcome' | 'edit-outcome',
        outcome: ProgramOutcome | null = null,
    ) {
        modalMode = mode;
        modalOutcome = outcome;
        if (outcome) {
            editUsername = outcome.code;
            editEmail = outcome.description;
        } else {
            editUsername = '';
            editEmail = '';
        }
        errorMessage = '';
        showModal = true;
    }

    function closeModal() {
        showModal = false;
        modalOutcome = null;
        editUsername = '';
        editEmail = '';
        errorMessage = '';
    }

    async function addOutcome() {
        errorMessage = '';
        if (!editUsername || !editEmail) {
            errorMessage = 'Please fill in all fields';
            return;
        }

        const res = await fetch('http://localhost:8080/api/program-outcomes/', {
            method: 'POST',
            headers: {
                Authorization: `Bearer ${accessToken}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                code: editUsername,
                description: editEmail,
            }),
        });
        const data = await res.json();
        if (!res.ok) {
            errorMessage =
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
        if (!modalOutcome) return;

        const res = await fetch(
            `http://localhost:8080/api/program-outcomes/${modalOutcome.id}/`,
            {
                method: 'PUT',
                headers: {
                    Authorization: `Bearer ${accessToken}`,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username: editUsername,
                    email: editEmail,
                }),
            },
        );

        const data = await res.json();
        if (!res.ok) {
            errorMessage =
                data.username?.[0] ||
                data.email?.[0] ||
                data.detail ||
                'Unknown error';
            return;
        }

        closeModal();
        await fetchOutcomes();
    }

    async function confirmDelete() {
        if (!modalOutcome) return;

        const res = await fetch(
            `http://localhost:8080/api/program-outcomes/${modalOutcome.id}/`,
            {
                method: 'DELETE',
                headers: { Authorization: `Bearer ${accessToken}` },
            },
        );

        if (!res.ok) {
            const data = await res.json();
            errorMessage = data.detail || 'Failed to delete';
            return;
        }

        closeModal();
        await fetchOutcomes();
    }

    const columns: Column[] = [
        { key: 'code', label: 'Code' },
        { key: 'description', label: 'Description' },
    ];

    const actions: Action<ProgramOutcome>[] = [
        {
            label: 'Edit',
            colorClass: 'text-blue-400',
            callback: (t) => openModal('edit-outcome', t),
        },
        {
            label: 'Delete',
            colorClass: 'text-red-400',
            callback: (t) => openModal('delete', t),
        },
    ];
</script>

<h1 class="text-2xl font-bold px-6">Program Outcomes</h1>
<p class="text-gray-400 mb-4 px-6">
    Manage teachers, edit details, and add new accounts.
</p>

<Table
    {columns}
    {actions}
    data={outcomes}
    searchEnabled={true}
    addLabel="New Outcome"
    onAdd={() => openModal('add-outcome')}
    onRowClick={(row) => {
        console.log(row);
    }}
/>

{#if showModal}
    <Modal
        show={showModal}
        data={modalOutcome}
        label="Teacher"
        {errorMessage}
        mode={modalMode}
        bind:editUsername
        bind:editEmail
        onSave={saveEdit}
        onDelete={confirmDelete}
        onAdd={addOutcome}
        onClose={closeModal}
    />
{/if}
