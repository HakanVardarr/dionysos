<script lang="ts">
    import { auth } from '$lib/stores/auth';
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import Modal from '$lib/components/Modal.svelte';
    import Table from '$lib/components/Table.svelte';
    import type { Column, Action } from '$lib/components/Table.svelte';

    let teachers: any[] = [];

    let showModal = false;
    let modalTeacher: any = null;
    let modalMode: 'edit' | 'delete' | 'add' = 'add';
    let editUsername = '';
    let editEmail = '';
    let errorMessage = '';

    type Teacher = {
        id: number;
        username: string;
        email: string;
    };

    let accessToken: string | null = null;

    onMount(async () => {
        auth.subscribe(($auth) => (accessToken = $auth.access))();
        if (!accessToken) goto('/login');
        await fetchTeachers();
    });

    async function fetchTeachers() {
        const res = await fetch('http://localhost:8080/api/teachers/', {
            method: 'GET',
            headers: {
                Authorization: `Bearer ${accessToken}`,
                'Content-Type': 'application/json',
            },
        });
        if (res.ok) {
            const data = await res.json();
            teachers = data.teachers;
        }
    }

    function openModal(
        mode: 'edit' | 'delete' | 'add',
        teacher: Teacher | null = null,
    ) {
        modalMode = mode;
        modalTeacher = teacher;
        if (teacher) {
            editUsername = teacher.username;
            editEmail = teacher.email;
        } else {
            editUsername = '';
            editEmail = '';
        }
        errorMessage = '';
        showModal = true;
    }

    function closeModal() {
        showModal = false;
        modalTeacher = null;
        editUsername = '';
        editEmail = '';
        errorMessage = '';
    }

    async function addTeacher() {
        errorMessage = '';
        if (!editUsername || !editEmail) {
            errorMessage = 'Please fill in all fields';
            return;
        }

        const res = await fetch('http://localhost:8080/api/teachers/', {
            method: 'POST',
            headers: {
                Authorization: `Bearer ${accessToken}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: editUsername,
                email: editEmail,
            }),
        });
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
        await fetchTeachers();
    }

    async function saveEdit() {
        if (!modalTeacher) return;

        const res = await fetch(
            `http://localhost:8080/api/teachers/${modalTeacher.id}/`,
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
        await fetchTeachers();
    }

    async function confirmDelete() {
        if (!modalTeacher) return;

        const res = await fetch(
            `http://localhost:8080/api/teachers/${modalTeacher.id}/`,
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
        await fetchTeachers();
    }

    async function addTeachers(file: File) {
        const formData = new FormData();
        formData.append('file', file);

        const res = await fetch(`http://localhost:8080/api/teachers/bulk/`, {
            method: 'POST',
            headers: {
                Authorization: `Bearer ${accessToken}`,
            },
            body: formData,
        });

        if (!res.ok) {
            const error = await res.json();
            console.error('Upload failed:', error);
        } else {
            const data = await res.json();
            await fetchTeachers();
        }
    }

    const columns: Column[] = [
        { key: 'username', label: 'Username' },
        { key: 'email', label: 'Email' },
    ];

    const actions: Action<Teacher>[] = [
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
</script>

<h1 class="text-2xl font-bold px-6">Teacher Management</h1>
<p class="text-gray-400 mb-4 px-6">
    Manage teachers, edit details, and add new accounts.
</p>

<Table
    {columns}
    {actions}
    data={teachers}
    searchEnabled={true}
    addLabel="Add Teacher"
    onAdd={() => openModal('add')}
    onBulkAdd={addTeachers}
    onRowClick={(row) => {
        console.log(row);
    }}
/>

{#if showModal}
    <Modal
        show={showModal}
        data={modalTeacher}
        label="Teacher"
        {errorMessage}
        mode={modalMode}
        bind:editUsername
        bind:editEmail
        onSave={saveEdit}
        onDelete={confirmDelete}
        onAdd={addTeacher}
        onClose={closeModal}
    />
{/if}
