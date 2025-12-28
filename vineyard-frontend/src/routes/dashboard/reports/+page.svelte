<script lang="ts">
    import { auth } from '$lib/stores/auth';
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';

    let accessToken: string | null = null;
    let userRole: string | null = null;

    let loading = false;
    let error = '';
    let report: any = null;
    let outcomes: any = null;
    let suggestionPayload: any = null;
    let suggestions: any = null;
    let suggestionLoading = false;
    let showModal = false;

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
        await buildProgramSuggestionJSON();
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

    async function fetchOutcomes() {
        const res = await fetch('http://localhost:8080/api/program-outcomes/', {
            method: 'GET',
            headers: {
                Authorization: `Bearer ${accessToken}`,
                'Content-Type': 'application/json',
            },
        });
        if (res.ok) {
            const data = await res.json();
            outcomes = data['program-outcomes'];
        }
    }

    async function buildProgramSuggestionJSON() {
        await fetchOutcomes();
        if (!report || !outcomes) return;

        const program_outcomes: Record<
            string,
            { score: number; description: string }
        > = {};
        Object.entries(report.program_outcomes).forEach(([po, score]) => {
            const descObj = outcomes.find((o: any) => o.code === po);
            const description = descObj ? descObj.description : '';
            program_outcomes[po] = { score: score as number, description };
        });

        const courses = report.reports.map((c: any) => {
            const assessments: Record<string, number> = {};
            Object.values(c.assessments).forEach((a: any) => {
                assessments[a.label] = a.average;
            });

            return {
                code: c.course_code,
                name: c.course_name,
                assessments,
            };
        });

        suggestionPayload = {
            program_name: 'Computer Science Engineering',
            program_outcomes,
            courses,
        };
    }

    async function generateSuggestions() {
        if (!suggestionPayload) return;

        suggestionLoading = true;
        suggestions = null;

        try {
            const startRes = await fetch(
                'http://localhost:8080/api/tasks/report/',
                {
                    method: 'POST',
                    headers: {
                        Authorization: `Bearer ${accessToken}`,
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(suggestionPayload),
                },
            );

            if (!startRes.ok)
                throw new Error('Failed to start suggestion task');

            const startData = await startRes.json();
            const taskId = startData.task_id;
            suggestionLoading = true;

            const interval = setInterval(async () => {
                const statusRes = await fetch(
                    `http://localhost:8080/api/tasks/report/${taskId}/`,
                    {
                        headers: { Authorization: `Bearer ${accessToken}` },
                    },
                );

                if (!statusRes.ok) return;

                const statusData = await statusRes.json();
                const state = statusData.status;

                if (state === 'SUCCESS' || state === 'FAILURE') {
                    clearInterval(interval);
                    suggestionLoading = false;

                    if (state === 'SUCCESS') {
                        suggestions = statusData.result;
                        showModal = true;
                    } else {
                        alert('Suggestion generation failed');
                    }
                }
            }, 1000);
        } catch (err) {
            console.error(err);
            alert('Error generating suggestions');
            suggestionLoading = false;
        }
    }

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

    function handleClose() {
        showModal = false;
    }
</script>

<div
    class="min-h-screen bg-linear-to-br from-[#0b0b10] via-[#0d0d14] to-black p-10"
>
    <div class="max-w-7xl mx-auto space-y-14">
        <div class="flex justify-between items-center mb-6">
            <h1 class="text-2xl font-semibold text-purple-300">
                Program Report
            </h1>

            <button
                class="px-6 py-3 bg-white/5 text-white rounded-2xl shadow-md flex items-center gap-2 hover:bg-white/10 transition"
                on:click={generateSuggestions}
                disabled={suggestionLoading}
            >
                {#if suggestionLoading}
                    <svg
                        class="animate-spin h-5 w-5 text-white"
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                    >
                        <circle
                            class="opacity-25"
                            cx="12"
                            cy="12"
                            r="10"
                            stroke="currentColor"
                            stroke-width="4"
                        ></circle>
                        <path
                            class="opacity-75"
                            fill="currentColor"
                            d="M4 12a8 8 0 018-8v8H4z"
                        ></path>
                    </svg>
                    Loading…
                {:else}
                    Generate Suggestions
                {/if}
            </button>
        </div>

        {#if loading}
            <div class="text-gray-400 animate-pulse">Generating reports…</div>
        {/if}

        {#if error}
            <p class="text-red-400">{error}</p>
        {/if}

        {#if report}
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
                                    <th class="text-center text-gray-400 pb-3"
                                        >{po}</th
                                    >
                                {/each}
                            </tr>
                        </thead>

                        <tbody>
                            {#each report.reports as course}
                                <tr class="border-t border-white/10">
                                    <td
                                        class="py-3 pr-4 text-gray-200 font-semibold"
                                        >{course.course_code}</td
                                    >

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
                                                class="h-10 rounded-xl flex items-center justify-center text-xs font-bold text-white shadow-md transition"
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

            <div class="space-y-10">
                {#each report.reports as c}
                    <section
                        class="rounded-3xl bg-white/5 border border-white/10 p-8 backdrop-blur-xl shadow-md"
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
                                <div
                                    class="bg-white/5 rounded-3xl p-4 shadow-md backdrop-blur-xl"
                                >
                                    <div
                                        class="flex justify-between text-xs text-gray-300 mb-1"
                                    >
                                        <span
                                            class="tracking-widest font-semibold text-gray-200"
                                            >{(
                                                a as any
                                            ).label.toUpperCase()}</span
                                        >
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

{#if showModal && suggestions}
    <div
        class="fixed inset-0 z-50 flex items-center justify-center
               bg-black/50 backdrop-blur-md"
        role="dialog"
        aria-modal="true"
    >
        <div
            class="w-full max-w-3xl
                   rounded-2xl
                   bg-[#0f0f18]
                   border border-white/8
                   shadow-[0_30px_80px_rgba(0,0,0,0.6)]
                   p-6"
        >
            <div class="mb-5 flex justify-between items-center">
                <h2 class="text-base font-medium text-gray-100 tracking-tight">
                    Program Suggestions
                </h2>
            </div>
            <div class="mt-2 h-px w-full bg-white/5"></div>

            <div class="mt-4 space-y-4 max-h-[60vh] overflow-y-auto">
                {#each suggestions.Suggestions as s}
                    <div
                        class="p-4 rounded-xl bg-[#2a2a40] border border-white/10 shadow-md"
                    >
                        <p><strong>PO:</strong> {s.PO}</p>
                        <p><strong>Course:</strong> {s.course}</p>
                        <p><strong>Issue:</strong> {s.issue}</p>
                        <p>
                            <strong>Recommendation:</strong>
                            {s.recommendation}
                        </p>
                    </div>
                {/each}
            </div>

            <div class="mt-6 flex justify-end gap-2">
                <button
                    class="px-4 py-2 rounded-lg text-sm
                           bg-white/3 hover:bg-white/6
                           text-gray-300
                           transition"
                    on:click={handleClose}
                >
                    Close
                </button>
            </div>
        </div>
    </div>
{/if}
