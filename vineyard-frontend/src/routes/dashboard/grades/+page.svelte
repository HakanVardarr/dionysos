<script lang="ts">
    import { auth } from '$lib/stores/auth';
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import { capitalize } from '$lib/utils';

    type Assessment = {
        id: number;
        name: string;
        score: number | null;
    };

    type Course = {
        id: number;
        code: string;
        name: string;
        assessments: Assessment[];
        assessmentLabels?: Record<number, string>;
    };

    let accessToken: string | null = null;
    let courses: Course[] = [];
    let loading = true;
    let error: string | null = null;

    onMount(async () => {
        // Auth kontrolü
        auth.subscribe(($auth) => (accessToken = $auth.access))();
        if (!accessToken) {
            goto('/login');
            return;
        }

        try {
            const res = await fetch('http://localhost:8080/api/me/courses/', {
                headers: { Authorization: `Bearer ${accessToken}` },
            });
            if (!res.ok) throw new Error('Failed to fetch courses');

            const data = await res.json();
            courses = data.courses;

            // Assessment label mapini oluştur
            courses.forEach((course) => {
                const typeCounters: Record<string, number> = {};
                course.assessmentLabels = {};

                course.assessments.forEach((a) => {
                    typeCounters[a.name] = (typeCounters[a.name] || 0) + 1;
                    course.assessmentLabels![a.id] =
                        `${capitalize(a.name)} ${typeCounters[a.name]}`;
                });
            });
        } catch (err) {
            console.error(err);
            error = 'Could not load courses';
        } finally {
            loading = false;
        }
    });

    function getAssessmentScore(course: Course, assessmentId: number) {
        const assessment = course.assessments.find(
            (a) => a.id === assessmentId,
        );
        return assessment?.score ?? '-';
    }
</script>

{#if loading}
    <p class="text-gray-400 text-center mt-10">Loading your courses…</p>
{:else if error}
    <p class="text-red-400 text-center mt-10">{error}</p>
{:else}
    <div class="min-h-screen bg-[#0b0b10] py-10 px-6 md:px-20">
        <div class="max-w-5xl mx-auto space-y-8">
            <h1 class="text-3xl font-extrabold text-white tracking-wide mb-6">
                My Courses & Grades
            </h1>

            {#if courses.length === 0}
                <p class="text-gray-400">
                    You are not enrolled in any courses yet.
                </p>
            {:else}
                <div class="grid gap-6">
                    {#each courses as course}
                        <div
                            class="p-5 rounded-2xl bg-[#0f0f16] border border-white/5"
                        >
                            <h2 class="text-xl text-white font-semibold mb-3">
                                {course.name} ({course.code})
                            </h2>

                            {#if course.assessments.length === 0}
                                <p class="text-gray-400 text-sm">
                                    No assessments yet.
                                </p>
                            {:else}
                                <div class="grid md:grid-cols-2 gap-4">
                                    {#each course.assessments as a}
                                        <div
                                            class="p-3 bg-[#0b0b10] rounded-xl border border-white/10"
                                        >
                                            <p
                                                class="text-purple-400 font-medium mb-1"
                                            >
                                                {course.assessmentLabels![a.id]}
                                            </p>
                                            <p class="text-gray-200 text-lg">
                                                {getAssessmentScore(
                                                    course,
                                                    a.id,
                                                )}
                                            </p>
                                        </div>
                                    {/each}
                                </div>
                            {/if}
                        </div>
                    {/each}
                </div>
            {/if}
        </div>
    </div>
{/if}
