<script lang="ts">
    import { auth } from '$lib/stores/auth';
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import Modal from '$lib/components/Modal.svelte';
    import Table from '$lib/components/Table.svelte';
    import type { Column, Action } from '$lib/components/Table.svelte';

    let students: any[] = [];

    let showModal = false;
    let modalStudent: any = null;
    let modalMode: 'edit' | 'delete' | 'add' = 'add';
    let editUsername = '';
    let editEmail = '';
    let errorMessage = '';

    type Student = {
        id: number;
        username: string;
        email: string;
    };

    let accessToken: string | null = null;

    onMount(async () => {
        auth.subscribe(($auth) => (accessToken = $auth.access))();
        if (!accessToken) goto('/login');
        await fetchStudents();
    });

    async function fetchStudents() {
        const res = await fetch('http://localhost:8080/api/students/', {
            method: 'GET',
            headers: {
                Authorization: `Bearer ${accessToken}`,
                'Content-Type': 'application/json',
            },
        });
        if (res.ok) {
            const data = await res.json();
            students = data.students;
        }
    }

    function openModal(
        mode: 'edit' | 'delete' | 'add',
        student: Student | null = null,
    ) {
        modalMode = mode;
        modalStudent = student;
        if (student) {
            editUsername = student.username;
            editEmail = student.email;
        } else {
            editUsername = '';
            editEmail = '';
        }
        errorMessage = '';
        showModal = true;
    }

    function closeModal() {
        showModal = false;
        modalStudent = null;
        editUsername = '';
        editEmail = '';
        errorMessage = '';
    }

    async function addStudent() {
        errorMessage = '';
        if (!editUsername || !editEmail) {
            errorMessage = 'Please fill in all fields';
            return;
        }

        const res = await fetch('http://localhost:8080/api/students/', {
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
        await fetchStudents();
    }

    async function saveEdit() {
        if (!modalStudent) return;

        const res = await fetch(
            `http://localhost:8080/api/students/${modalStudent.id}/`,
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
        await fetchStudents();
    }

    async function confirmDelete() {
        if (!modalStudent) return;

        const res = await fetch(
            `http://localhost:8080/api/students/${modalStudent.id}/`,
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
        await fetchStudents();
    }

    async function addStudents(file: File) {
        const formData = new FormData();
        formData.append('file', file);

        const res = await fetch(`http://localhost:8080/api/students/bulk/`, {
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
            await fetchStudents();
        }
    }

    const columns: Column[] = [
        { key: 'username', label: 'Username' },
        { key: 'email', label: 'Email' },
    ];

    const actions: Action<Student>[] = [
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

<h1 class="text-2xl font-bold px-6">Student Management</h1>
<p class="text-gray-400 mb-4 px-6">
    Manage students, view their progress, and add new student accounts.
</p>

<Table
    {columns}
    {actions}
    data={students}
    searchEnabled={true}
    addLabel="Add Student"
    onAdd={() => openModal('add')}
    onBulkAdd={addStudents}
/>

{#if showModal}
    <Modal
        show={showModal}
        data={modalStudent}
        label="Student"
        mode={modalMode}
        {errorMessage}
        bind:editUsername
        bind:editEmail
        onSave={saveEdit}
        onDelete={confirmDelete}
        onAdd={addStudent}
        onClose={closeModal}
    />
{/if}
