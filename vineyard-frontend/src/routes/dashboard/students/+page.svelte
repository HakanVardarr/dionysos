<script lang="ts">
    import { auth } from '$lib/stores/auth';
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import Modal from '$lib/components/Modal.svelte';
    import Table from '$lib/components/Table.svelte';
    import type { Column, Action } from '$lib/components/Table.svelte';

    type Student = {
        id: number;
        username: string;
        email: string;
    };

    type ModalMode = 'add' | 'edit' | 'delete';
    type ModalState = {
        open: boolean;
        mode: ModalMode;
        student: Student | null;
        form: {
            username: string;
            email: string;
        };
        error: string;
    };

    let students: Student[] = [];
    let accessToken: string | null = null;

    let modal: ModalState = {
        open: false,
        mode: 'add',
        student: null,
        form: {
            username: '',
            email: '',
        },
        error: '',
    };

    const columns: Column[] = [
        { key: 'username', label: 'Username' },
        { key: 'email', label: 'Email' },
    ];

    const actions: Action<Student>[] = [
        {
            label: 'Edit',
            colorClass: 'text-blue-400',
            callback: (s) => openModal('edit', s),
        },
        {
            label: 'Delete',
            colorClass: 'text-red-400',
            callback: (s) => openModal('delete', s),
        },
    ];

    onMount(async () => {
        auth.subscribe(($auth) => (accessToken = $auth.access))();
        if (!accessToken) goto('/login');
        await fetchStudents();
    });

    async function fetchStudents() {
        const res = await fetch('http://localhost:8080/api/students/', {
            headers: {
                Authorization: `Bearer ${accessToken}`,
            },
        });

        if (res.ok) {
            const data = await res.json();
            students = data.students;
        }
    }

    function openModal(mode: ModalMode, student: Student | null = null) {
        modal = {
            open: true,
            mode,
            student,
            form: student
                ? {
                      username: student.username,
                      email: student.email,
                  }
                : {
                      username: '',
                      email: '',
                  },
            error: '',
        };
    }

    function closeModal() {
        modal.open = false;
    }

    async function addStudent() {
        modal.error = '';

        const { username, email } = modal.form;
        if (!username || !email) {
            modal.error = 'Please fill in all fields';
            return;
        }

        const res = await fetch('http://localhost:8080/api/students/', {
            method: 'POST',
            headers: {
                Authorization: `Bearer ${accessToken}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, email }),
        });

        const data = await res.json();
        if (!res.ok) {
            modal.error =
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
        if (!modal.student) return;

        const res = await fetch(
            `http://localhost:8080/api/students/${modal.student.id}/`,
            {
                method: 'PUT',
                headers: {
                    Authorization: `Bearer ${accessToken}`,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(modal.form),
            },
        );

        const data = await res.json();
        if (!res.ok) {
            modal.error =
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
        if (!modal.student) return;

        const res = await fetch(
            `http://localhost:8080/api/students/${modal.student.id}/`,
            {
                method: 'DELETE',
                headers: {
                    Authorization: `Bearer ${accessToken}`,
                },
            },
        );

        if (!res.ok) {
            const data = await res.json();
            modal.error = data.detail || 'Failed to delete';
            return;
        }

        closeModal();
        await fetchStudents();
    }

    async function addStudents(file: File) {
        const formData = new FormData();
        formData.append('file', file);

        const res = await fetch('http://localhost:8080/api/students/bulk/', {
            method: 'POST',
            headers: {
                Authorization: `Bearer ${accessToken}`,
            },
            body: formData,
        });

        if (res.ok) {
            await fetchStudents();
        }
    }
</script>

<h1 class="text-3xl font-semibold text-white tracking-tight">
    Student Management
</h1>

<p class="text-sm text-gray-400 mt-1 mb-6 max-w-xl">
    Manage enrolled students, edit account details and bulk upload new users.
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
        data={students}
        searchEnabled={true}
        addLabel="Add Student"
        onAdd={() => openModal('add')}
        onBulkAdd={addStudents}
    />
</div>

{#if modal.open}
    <Modal
        show={modal.open}
        title={modal.mode === 'add'
            ? 'Add Student'
            : modal.mode === 'edit'
              ? 'Edit Student'
              : 'Delete Student'}
        errorMessage={modal.error}
        confirmLabel={modal.mode === 'delete'
            ? 'Delete'
            : modal.mode === 'add'
              ? 'Add'
              : 'Save'}
        onConfirm={modal.mode === 'delete'
            ? confirmDelete
            : modal.mode === 'add'
              ? addStudent
              : saveEdit}
        onClose={closeModal}
    >
        {#if modal.mode === 'delete'}
            <div
                class="rounded-lg
                       bg-red-500/10
                       border border-red-500/20
                       px-4 py-3
                       text-sm text-red-300"
            >
                Are you sure you want to permanently delete
                <span class="font-semibold text-red-200">
                    {modal.student?.username}
                </span>
                ?
            </div>
        {:else}
            <div class="space-y-3">
                <input
                    bind:value={modal.form.username}
                    placeholder="Username"
                    class="w-full rounded-lg
                           bg-[#0c0c12]
                           border border-white/10
                           px-3 py-2 text-sm text-gray-200
                           placeholder-gray-500
                           outline-none
                           focus:border-purple-500/40
                           transition"
                />

                <input
                    bind:value={modal.form.email}
                    type="email"
                    placeholder="Email address"
                    class="w-full rounded-lg
                           bg-[#0c0c12]
                           border border-white/10
                           px-3 py-2 text-sm text-gray-200
                           placeholder-gray-500
                           outline-none
                           focus:border-purple-500/40
                           transition"
                />
            </div>
        {/if}
    </Modal>
{/if}
