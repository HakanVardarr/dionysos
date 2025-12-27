<script lang="ts">
    import { auth } from '$lib/stores/auth';
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';

    let accessToken: string | null = null;
    let userRole: string | null = null;

    let loading = false;
    let error = '';
    let report: any = null;

    onMount(async () => {
        auth.subscribe((a) => (accessToken = a.access))();

        if (!accessToken) return;

        const res = await fetch('http://localhost:8080/api/me/', {
            headers: { Authorization: `Bearer ${accessToken}` },
        });

        const data = await res.json();
        userRole = data.role;

        if (userRole !== 'head') {
            goto('/dashboard');
            return;
        }

        await generateReport();
    });

    async function generateReport() {
        if (!accessToken) return;

        loading = true;
        error = '';
        report = null;

        try {
            const res = await fetch(
                'http://localhost:8080/api/reports/generate/',
                {
                    method: 'POST',
                    headers: { Authorization: `Bearer ${accessToken}` },
                },
            );

            if (!res.ok) throw new Error();
            report = await res.json();
        } catch {
            error = 'Failed to generate report';
        } finally {
            loading = false;
        }
    }

    /* ---------- HEATMAP HELPERS ---------- */

    function getMaxContribution(po: string) {
        if (!report) return 0;
        return Math.max(
            ...report.reports.map(
                (c: any) => c.program_outcome_contribution?.[po] || 0,
            ),
        );
    }

    function normalize(value: number, max: number) {
        if (!max || max === 0) return 0;
        return Math.min(100, (value / max) * 100);
    }

    function heatColor(percent: number) {
        const p = Math.max(0, Math.min(100, percent));
        const hue = (p / 100) * 120;
        return `hsl(${hue}, 85%, 45%)`;
    }

    function barColor(v: number) {
        if (v < 50) return 'bg-red-500';
        if (v < 70) return 'bg-yellow-400';
        return 'bg-green-500';
    }
</script>

<div
    class="min-h-screen bg-gradient-to-br from-[#0b0b10] via-[#0d0d14] to-black p-10"
>
    <div class="max-w-7xl mx-auto space-y-14">
        {#if loading}
            <div class="text-gray-400 animate-pulse">Generating reports…</div>
        {/if}

        {#if error}
            <p class="text-red-400">{error}</p>
        {/if}

        {#if report}
            <!-- 🌍 GLOBAL PROGRAM OUTCOMES -->
            <section
                class="rounded-3xl bg-white/5 border border-white/10 p-8 backdrop-blur-xl"
            >
                <h2
                    class="text-xl font-semibold text-purple-300 mb-6 uppercase tracking-wider"
                >
                    Overall Program Outcomes
                </h2>

                <div class="grid md:grid-cols-2 gap-6">
                    {#each Object.entries(report.program_outcomes) as [code, value]}
                        {@const v = value as number}
                        <div>
                            <div
                                class="flex justify-between text-xs text-gray-300 mb-1"
                            >
                                <span class="tracking-widest font-semibold"
                                    >{code}</span
                                >
                                <span>{v.toFixed(1)}%</span>
                            </div>

                            <div
                                class="h-3 w-full rounded-full bg-white/10 overflow-hidden"
                            >
                                <div
                                    class={`h-3 ${barColor(v)} transition-all`}
                                    style="width:{v}%"
                                ></div>
                            </div>
                        </div>
                    {/each}
                </div>
            </section>

            <!-- 🔥 COURSE → PROGRAM OUTCOME HEATMAP -->
            <section
                class="rounded-3xl bg-white/5 border border-white/10 p-8 backdrop-blur-xl"
            >
                <h2
                    class="text-xl font-semibold text-purple-300 mb-6 uppercase tracking-wider"
                >
                    Course Contribution Heatmap
                </h2>

                <div class="overflow-x-auto">
                    <table class="w-full border-collapse text-sm">
                        <thead>
                            <tr>
                                <th class="text-left text-gray-400 pb-3"
                                    >Course</th
                                >
                                {#each Object.keys(report.program_outcomes) as po}
                                    <th class="text-center text-gray-400 pb-3">
                                        {po}
                                    </th>
                                {/each}
                            </tr>
                        </thead>

                        <tbody>
                            {#each report.reports as course}
                                <tr class="border-t border-white/10">
                                    <td
                                        class="py-3 pr-4 text-gray-200 font-semibold"
                                    >
                                        {course.course_code}
                                    </td>

                                    {#each Object.keys(report.program_outcomes) as po}
                                        {@const raw =
                                            course
                                                .program_outcome_contribution?.[
                                                po
                                            ] || 0}
                                        {@const max = getMaxContribution(po)}
                                        {@const normalized = normalize(
                                            raw,
                                            max,
                                        )}

                                        <td class="p-2">
                                            <div
                                                class="h-10 rounded-xl flex items-center justify-center
                                                       text-xs font-bold text-white shadow-md transition"
                                                style="background-color: {heatColor(
                                                    normalized,
                                                )}"
                                                title={`Raw: ${raw.toFixed(2)} / Max: ${max.toFixed(2)}`}
                                            >
                                                {normalized.toFixed(0)}%
                                            </div>
                                        </td>
                                    {/each}
                                </tr>
                            {/each}
                        </tbody>
                    </table>
                </div>
            </section>

            <!-- 📚 COURSES -->
            <div class="space-y-10">
                {#each report.reports as c}
                    <section
                        class="rounded-3xl bg-white/4 border border-white/10 p-8 backdrop-blur-xl"
                    >
                        <div class="mb-6">
                            <h2 class="text-2xl font-semibold text-purple-300">
                                {c.course_name}
                            </h2>
                            <p class="text-sm text-gray-400">{c.course_code}</p>
                        </div>

                        <div class="space-y-4">
                            <h3
                                class="text-xs uppercase text-gray-400 tracking-widest"
                            >
                                Assessment Averages
                            </h3>

                            {#each Object.values(c.assessments) as a}
                                {@const v = (a as any).average}

                                <div>
                                    <div
                                        class="flex justify-between text-xs text-gray-300 mb-1"
                                    >
                                        <span
                                            class="tracking-widest font-semibold text-gray-200"
                                        >
                                            {(a as any).label.toUpperCase()}
                                        </span>
                                        <span>{v.toFixed(1)}%</span>
                                    </div>

                                    <div
                                        class="h-2 w-full bg-white/10 rounded-full overflow-hidden"
                                    >
                                        <div
                                            class={`h-2 ${barColor(v)} transition-all`}
                                            style="width:{v}%"
                                        ></div>
                                    </div>
                                </div>
                            {/each}
                        </div>
                    </section>
                {/each}
            </div>
        {/if}
    </div>
</div>
