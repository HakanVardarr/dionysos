<script lang="ts">
    import { auth } from '$lib/stores/auth';
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import Modal from '$lib/components/Modal.svelte';
    import Table from '$lib/components/Table.svelte';
    import type { Column, Action } from '$lib/components/Table.svelte';

    type Teacher = {
        id: number;
        username: string;
        email: string;
    };

    type ModalMode = 'add' | 'edit' | 'delete';
    type ModalState = {
        open: boolean;
        mode: ModalMode;
        teacher: Teacher | null;
        form: {
            username: string;
            email: string;
        };
        error: string;
    };

    let teachers: Teacher[] = [];
    let accessToken: string | null = null;

    let modal: ModalState = {
        open: false,
        mode: 'add',
        teacher: null,
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

    onMount(async () => {
        auth.subscribe(($auth) => (accessToken = $auth.access))();
        if (!accessToken) goto('/login');
        await fetchTeachers();
    });

    async function fetchTeachers() {
        const res = await fetch('http://localhost:8080/api/teachers/', {
            headers: {
                Authorization: `Bearer ${accessToken}`,
            },
        });

        if (res.ok) {
            const data = await res.json();
            teachers = data.teachers;
        }
    }

    function openModal(mode: ModalMode, teacher: Teacher | null = null) {
        modal = {
            open: true,
            mode,
            teacher,
            form: teacher
                ? {
                      username: teacher.username,
                      email: teacher.email,
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

    async function addTeacher() {
        modal.error = '';

        const { username, email } = modal.form;
        if (!username || !email) {
            modal.error = 'Please fill in all fields';
            return;
        }

        const res = await fetch('http://localhost:8080/api/teachers/', {
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
        await fetchTeachers();
    }

    async function saveEdit() {
        if (!modal.teacher) return;

        const res = await fetch(
            `http://localhost:8080/api/teachers/${modal.teacher.id}/`,
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
        await fetchTeachers();
    }

    async function confirmDelete() {
        if (!modal.teacher) return;

        const res = await fetch(
            `http://localhost:8080/api/teachers/${modal.teacher.id}/`,
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
        await fetchTeachers();
    }

    async function addTeachers(file: File) {
        const formData = new FormData();
        formData.append('file', file);

        const res = await fetch('http://localhost:8080/api/teachers/bulk/', {
            method: 'POST',
            headers: {
                Authorization: `Bearer ${accessToken}`,
            },
            body: formData,
        });

        if (res.ok) {
            await fetchTeachers();
        }
    }
</script>

<h1 class="text-3xl font-semibold text-white tracking-tight">
    Teacher Management
</h1>

<p class="text-sm text-gray-400 mt-1 mb-6 max-w-xl">
    Manage instructors, edit account details and add new teacher accounts to the
    system.
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
        data={teachers}
        searchEnabled={true}
        addLabel="Add Teacher"
        onAdd={() => openModal('add')}
        onBulkAdd={addTeachers}
    />
</div>

{#if modal.open}
    <Modal
        show={modal.open}
        title={modal.mode === 'add'
            ? 'Add Teacher'
            : modal.mode === 'edit'
              ? 'Edit Teacher'
              : 'Delete Teacher'}
        errorMessage={modal.error}
        confirmLabel={modal.mode === 'delete'
            ? 'Delete'
            : modal.mode === 'add'
              ? 'Add'
              : 'Save'}
        onConfirm={modal.mode === 'delete'
            ? confirmDelete
            : modal.mode === 'add'
              ? addTeacher
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
                    {modal.teacher?.username}
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
