<script lang="ts">
    import { auth } from '$lib/stores/auth';
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import { gotoIfStudent } from '$lib/auth';

    type Course = {
        id: number;
        course_code: string;
        course_name: string;
        created_by: {
            username: string;
        };
        learning_outcome_count: number;
        assessment_count: number;
    };

    let courses: Course[] = [];
    let accessToken: string | null = null;
    let loading = true;

    onMount(async () => {
        auth.subscribe(($auth) => (accessToken = $auth.access))();
        if (!accessToken) goto('/login');

        const res = await fetch('http://localhost:8080/api/courses/', {
            headers: { Authorization: `Bearer ${accessToken}` },
        });

        gotoIfStudent(accessToken!, '/dashboard/');

        if (res.ok) {
            const data = await res.json();
            courses = data.courses;
        }
        loading = false;
    });

    function openCourse(course: Course) {
        goto(`/dashboard/courses/${course.id}/`);
    }

    function createNewCourse() {
        goto('/dashboard/courses/new');
    }
</script>

<div class="px-6 py-6 space-y-6">
    <div class="flex items-center justify-between">
        <div>
            <h1 class="text-2xl font-semibold text-gray-100 tracking-tight">
                Courses
            </h1>
            <p class="mt-1 text-sm text-gray-400">
                View and manage created courses
            </p>
        </div>

        <button
            on:click={createNewCourse}
            class="px-4 py-2 rounded-lg
                   bg-purple-500/20 text-purple-300 hover:bg-purple-500/30 text-sm font-medium
                   transition"
        >
            + New Course
        </button>
    </div>

    {#if loading}
        <p class="text-sm text-gray-400">Loading courses…</p>
    {:else if courses.length === 0}
        <div
            class="rounded-xl border border-white/10
                   bg-white/2 p-8 text-center text-gray-400"
        >
            No courses created yet
        </div>
    {:else}
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {#each courses as course}
                <button
                    on:click={() => openCourse(course)}
                    class="group text-left rounded-2xl border border-white/10
                           bg-[#0e0e15] p-5 transition
                           hover:border-purple-500/30 hover:bg-white/3"
                >
                    <div class="flex items-start justify-between">
                        <div>
                            <p
                                class="text-xs uppercase tracking-wide text-purple-400"
                            >
                                {course.course_code}
                            </p>
                            <h3
                                class="mt-1 font-semibold text-gray-100 group-hover:text-white"
                            >
                                {course.course_name}
                            </h3>
                        </div>
                    </div>

                    <div class="mt-4 space-y-2 text-sm text-gray-400">
                        <div class="flex items-center gap-2">
                            <span
                                class="inline-block w-2 h-2 rounded-full bg-purple-400/70"
                            ></span>
                            <span>
                                Created by <span class="text-gray-200"
                                    >{course.created_by.username}</span
                                >
                            </span>
                        </div>

                        <div class="flex gap-4 text-xs text-gray-500">
                            <span
                                >{course.learning_outcome_count} Learning Outcomes</span
                            >
                            <span>{course.assessment_count} Assessments</span>
                        </div>
                    </div>

                    <div
                        class="mt-4 pt-3 border-t border-white/5
                               text-xs text-purple-400
                               opacity-0 group-hover:opacity-100
                               transition"
                    >
                        Details →
                    </div>
                </button>
            {/each}
        </div>
    {/if}
</div>
