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

    onMount(async () => {
        auth.subscribe(($auth) => (accessToken = $auth.access))();
        if (!accessToken) goto('/login');

        try {
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

    function goToEdit() {
        goto(`/dashboard/courses/${courseId}/edit`);
    }

    function assignStudents() {
        goto(`/dashboard/courses/${courseId}/assign-students`);
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
                    <button
                        on:click={assignStudents}
                        class="px-4 py-2 bg-purple-600/20 text-purple-300 rounded-xl transition duration-200"
                    >
                        Assign Students
                    </button>
                    <button
                        on:click={goToEdit}
                        class="px-4 py-2 bg-purple-600/20 text-purple-300 rounded-xl transition duration-200"
                    >
                        Edit
                    </button>
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
{/if}
