<script lang="ts">
    import { auth } from '$lib/stores/auth';
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';

    let accessToken: string | null = null;
    let userRole: any = null;

    onMount(async () => {
        auth.subscribe((a) => (accessToken = a.access))();

        if (!accessToken) {
            goto('/login');
        }

        const res = await fetch('http://localhost:8080/api/me/', {
            headers: { Authorization: `Bearer ${accessToken}` },
        });

        const data = await res.json();
        userRole = data.role;

        if (userRole === 'student') {
            goto('/dashboard/grades');
            return;
        } else if (userRole === 'teacher') {
            goto('/dashboard/courses');
        }
    });
</script>

<div
    class="min-h-screen
           bg-linear-to-br from-[#0b0b10] via-[#0d0d14] to-black
           p-10"
>
    <div class="max-w-7xl mx-auto space-y-12">
        <!-- HEADER -->
        <header class="flex justify-between items-center">
            <div>
                <h1 class="text-3xl font-semibold text-purple-300">
                    Dashboard
                </h1>
                <p class="text-sm text-gray-400 mt-1">
                    Program and course performance overview
                </p>
            </div>
        </header>

        <!-- QUICK STATS -->
        <section class="grid md:grid-cols-2 gap-6">
            <div
                class="rounded-3xl bg-white/5 border border-white/10
                       p-6 backdrop-blur-xl shadow-md"
            >
                <h3
                    class="text-xs uppercase tracking-widest text-gray-400 mb-2"
                >
                    Courses
                </h3>
                <p class="text-3xl font-semibold text-purple-200">4</p>
                <p class="text-xs text-gray-500 mt-1">
                    Courses evaluated this term
                </p>
            </div>

            <div
                class="rounded-3xl bg-white/5 border border-white/10
                       p-6 backdrop-blur-xl shadow-md"
            >
                <h3
                    class="text-xs uppercase tracking-widest text-gray-400 mb-2"
                >
                    Avg. PO Score
                </h3>
                <p class="text-3xl font-semibold text-purple-200">63%</p>
                <p class="text-xs text-gray-500 mt-1">
                    Overall program outcome achievement
                </p>
            </div>
        </section>

        <!-- MAIN ACTIONS -->
        <section class="grid md:grid-cols-2 gap-8">
            <!-- PROGRAM REPORT -->
            <div
                class="rounded-3xl bg-white/5 border border-white/10
                       p-8 backdrop-blur-xl hover:bg-white/8 transition"
            >
                <h2 class="text-xl font-semibold text-purple-300 mb-3">
                    Program Report
                </h2>
                <p class="text-sm text-gray-400 mb-6">
                    View detailed program outcomes, course contributions, and
                    assessment performance.
                </p>

                <button
                    on:click={() => goto('/dashboard/reports')}
                    class="px-6 py-3 rounded-xl
                           bg-purple-500/30
                           hover:bg-purple-500/40
                           text-purple-200
                           text-sm font-medium
                           transition"
                >
                    Open Program Report
                </button>
            </div>

            <!-- COURSE MANAGEMENT -->
            <div
                class="rounded-3xl bg-white/5 border border-white/10
                       p-8 backdrop-blur-xl hover:bg-white/8 transition"
            >
                <h2 class="text-xl font-semibold text-purple-300 mb-3">
                    Course Analysis
                </h2>
                <p class="text-sm text-gray-400 mb-6">
                    Analyze individual courses, assessments, and learning
                    outcome mappings.
                </p>

                <button
                    on:click={() => goto('/dashboard/courses')}
                    class="px-6 py-3 rounded-xl
                           bg-purple-500/30
                           hover:bg-purple-500/40
                           text-purple-200
                           text-sm font-medium
                           transition"
                >
                    View Courses
                </button>
            </div>
        </section>

        <!-- FOOTER NOTE -->
        <div class="text-xs text-gray-600 text-center pt-10">
            Outcome-based evaluation system for academic quality assurance
        </div>
    </div>
</div>
