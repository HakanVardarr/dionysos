<script lang="ts">
    import { auth } from '$lib/stores/auth';
    import { page } from '$app/state';
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';

    type LearningOutcome = {
        description: string;
        program_outcomes: { code: string }[];
    };
    type AssessmentLO = {
        code: string;
        weight: number;
    };
    type Assessment = {
        assessment_type: string;
        learning_outcomes: AssessmentLO[];
    };

    let courseId: string = page.params.id!;
    let accessToken: string | null = null;
    let course: {
        id: number;
        code: string;
        name: string;
        created_by: { username: string };
        learning_outcomes: LearningOutcome[];
        assessments: Assessment[];
    } | null = null;
    let loading = true;
    let error: string | null = null;

    let showAssignModal = false;
    let students: { id: number; username: string; selected: boolean }[] = [];
    let modalError = '';
    let userRole: string | null = null;

    onMount(async () => {
        auth.subscribe(($auth) => (accessToken = $auth.access))();
        if (!accessToken) return;

        try {
            const resUser = await fetch('http://localhost:8080/api/me/', {
                headers: { Authorization: `Bearer ${accessToken}` },
            });
            if (resUser.ok) {
                const data = await resUser.json();
                userRole = data.role;
            }

            const res = await fetch(
                `http://localhost:8080/api/courses/${courseId}/`,
                {
                    headers: { Authorization: `Bearer ${accessToken}` },
                },
            );
            if (!res.ok) throw new Error('Failed to fetch course details');
            course = await res.json();
        } catch (err) {
            console.error(err);
            error = 'Could not load course details';
        } finally {
            loading = false;
        }
    });

    async function loadStudents() {
        if (!accessToken) return;
        try {
            const res = await fetch(
                `http://localhost:8080/api/courses/${courseId}/students/`,
                {
                    headers: { Authorization: `Bearer ${accessToken}` },
                },
            );
            if (!res.ok) throw new Error('Failed to fetch students');
            const data = await res.json();
            students = data.students;
        } catch (err) {
            console.error(err);
            modalError = 'Could not load students';
        }
    }

    function openAssignModal() {
        if (userRole !== 'head') return;
        showAssignModal = true;
        modalError = '';
        loadStudents();
    }

    function closeAssignModal() {
        showAssignModal = false;
        modalError = '';
    }

    async function assignSelectedStudents() {
        if (!accessToken) return;
        const selectedIds = students.filter((s) => s.selected).map((s) => s.id);

        try {
            const res = await fetch(
                `http://localhost:8080/api/courses/${courseId}/assign-students/`,
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        Authorization: `Bearer ${accessToken}`,
                    },
                    body: JSON.stringify({ students: selectedIds }),
                },
            );
            if (!res.ok) throw new Error('Failed to assign students');
            showAssignModal = false;
        } catch (err) {
            console.error(err);
            modalError = 'Failed to assign students';
        }
    }

    async function editCourse() {
        await goto(`/dashboard/courses/${courseId}/edit`);
    }

    async function deleteCourse() {
        if (!accessToken) return;

        const confirmed = confirm(
            'Are you sure you want to delete this course? This action cannot be undone.',
        );
        if (!confirmed) return;

        try {
            const res = await fetch(
                `http://localhost:8080/api/courses/${courseId}/delete/`,
                {
                    method: 'DELETE',
                    headers: {
                        Authorization: `Bearer ${accessToken}`,
                    },
                },
            );

            if (!res.ok) throw new Error('Failed to delete course');

            await goto('/dashboard/courses');
        } catch (err) {
            console.error(err);
            alert('Failed to delete course');
        }
    }
</script>

{#if loading}
    <p class="text-gray-400">Loading course details…</p>
{:else if error}
    <p class="text-red-400">{error}</p>
{:else if course}
    <div class="min-h-screen bg-[#0b0b10] py-10 px-6 md:px-20">
        <div class="max-w-5xl mx-auto space-y-10">
            <div
                class="flex flex-col md:flex-row md:justify-between md:items-center gap-4"
            >
                <div>
                    <h1
                        class="text-3xl font-extrabold text-white tracking-wide"
                    >
                        {course.name} ({course.code})
                    </h1>
                    <p class="text-gray-400 text-sm mt-1 italic">
                        Created by <strong>{course.created_by.username}</strong>
                    </p>
                </div>
                <div class="flex gap-3">
                    {#if userRole === 'head'}
                        <button
                            on:click={openAssignModal}
                            class="px-4 py-2 bg-purple-600/20 text-purple-300 rounded-xl transition duration-200"
                        >
                            Students
                        </button>
                    {/if}

                    <button
                        on:click={editCourse}
                        class="px-4 py-2 bg-purple-600/20 text-purple-300 rounded-xl transition duration-200"
                    >
                        Edit
                    </button>

                    {#if userRole === 'head' || userRole === 'teacher'}
                        <button
                            on:click={deleteCourse}
                            class="px-4 py-2 bg-red-500/20 text-red-300 rounded-xl hover:bg-red-500/30 transition duration-200"
                        >
                            Delete
                        </button>
                    {/if}
                </div>
            </div>

            <section class="space-y-4">
                <h2
                    class="text-2xl font-semibold text-white tracking-wide border-b border-white/10 pb-2"
                >
                    Learning Outcomes
                </h2>
                {#if course.learning_outcomes.length === 0}
                    <p class="text-gray-400 text-sm">No learning outcomes.</p>
                {:else}
                    <div class="grid md:grid-cols-2 gap-5">
                        {#each course.learning_outcomes as lo, i}
                            <div
                                class="p-5 rounded-2xl transition bg-[#0b0b10]/0"
                            >
                                <p
                                    class="text-purple-400 font-semibold uppercase mb-2 tracking-wider"
                                >
                                    {course.code}-LO{i + 1}
                                </p>
                                <p class="text-gray-200 text-sm">
                                    {lo.description}
                                </p>
                            </div>
                        {/each}
                    </div>
                {/if}
            </section>

            <section class="space-y-4">
                <h2
                    class="text-2xl font-semibold text-white tracking-wide border-b border-white/10 pb-2"
                >
                    Assessments
                </h2>
                {#if course.assessments.length === 0}
                    <p class="text-gray-400 text-sm">No assessments.</p>
                {:else}
                    <div class="grid md:grid-cols-2 gap-5">
                        {#each course.assessments as a}
                            <div
                                class="p-5 rounded-2xl transition bg-[#0b0b10]/0"
                            >
                                <p
                                    class="text-purple-400 font-semibold uppercase mb-2 tracking-wider"
                                >
                                    {a.assessment_type}
                                </p>
                            </div>
                        {/each}
                    </div>
                {/if}
            </section>
        </div>
    </div>

    {#if showAssignModal}
        <div
            class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-md"
        >
            <div
                class="w-full max-w-md rounded-2xl bg-[#0f0f18] border border-white/8 shadow-[0_30px_80px_rgba(0,0,0,0.6)] p-6"
            >
                <div class="mb-5">
                    <h2
                        class="text-base font-medium text-gray-100 tracking-tight"
                    >
                        Students
                    </h2>
                    <div class="mt-2 h-px w-full bg-white/5"></div>
                </div>

                {#if modalError}
                    <div
                        class="mb-4 rounded-lg bg-red-400/5 border border-red-400/10 px-3 py-2 text-xs text-red-300"
                    >
                        {modalError}
                    </div>
                {/if}

                <div
                    class="max-h-64 overflow-auto space-y-2 text-sm text-gray-300"
                >
                    {#each students as s}
                        <label
                            class="flex items-center gap-3 p-3 rounded-xl hover:bg-white/5 cursor-pointer transition"
                        >
                            <div class="relative">
                                <input
                                    type="checkbox"
                                    bind:checked={s.selected}
                                    class="peer absolute w-5 h-5 opacity-0 cursor-pointer"
                                />
                                <div
                                    class="w-5 h-5 rounded-full border-2 border-purple-500 flex items-center justify-center transition-colors peer-checked:bg-purple-500 peer-checked:border-purple-500"
                                >
                                    <svg
                                        class="w-3 h-3 text-white opacity-0 peer-checked:opacity-100 transition-opacity"
                                        fill="none"
                                        stroke="currentColor"
                                        stroke-width="3"
                                        viewBox="0 0 24 24"
                                    >
                                        <path
                                            stroke-linecap="round"
                                            stroke-linejoin="round"
                                            d="M5 13l4 4L19 7"
                                        ></path>
                                    </svg>
                                </div>
                            </div>
                            <span class="text-gray-200">{s.username}</span>
                        </label>
                    {/each}
                </div>

                <div class="mt-6 flex justify-end gap-2">
                    <button
                        on:click={closeAssignModal}
                        class="px-4 py-2 rounded-lg text-sm bg-white/3 hover:bg-white/6 text-gray-300 transition"
                    >
                        Cancel
                    </button>
                    <button
                        on:click={assignSelectedStudents}
                        class="px-4 py-2 rounded-lg text-sm bg-purple-500/30 hover:bg-purple-500/40 text-purple-200 transition"
                    >
                        Assign
                    </button>
                </div>
            </div>
        </div>
    {/if}
{/if}
