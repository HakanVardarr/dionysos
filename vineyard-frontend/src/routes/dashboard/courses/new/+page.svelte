<script lang="ts">
    import { auth } from '$lib/stores/auth';
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';

    type ProgramOutcome = {
        code: string;
        weight: number;
    };

    type LearningOutcome = {
        description: string;
        program_outcomes: ProgramOutcome[];
    };

    type AssessmentLearningOutcome = {
        loIndex: number;
        weight: number;
    };

    type Assessment = {
        assessment_type: 'midterm' | 'project' | 'final';
        learning_outcomes: AssessmentLearningOutcome[];
    };

    let accessToken: string | null = null;
    let courseCode = '';
    let courseName = '';

    let learningOutcomes: LearningOutcome[] = [];
    let assessments: Assessment[] = [];

    let programOutcomes: { code: string; description: string }[] = [];

    onMount(async () => {
        auth.subscribe((a) => (accessToken = a.access))();
        if (!accessToken) goto('/login');

        const res = await fetch('http://localhost:8080/api/program-outcomes/', {
            headers: { Authorization: `Bearer ${accessToken}` },
        });

        if (res.ok) {
            const data = await res.json();
            programOutcomes = data['program-outcomes'];
        }

        learningOutcomes = [
            {
                description: '',
                program_outcomes: [
                    { code: programOutcomes[0]?.code ?? '', weight: 1 },
                ],
            },
        ];

        assessments = [
            {
                assessment_type: 'midterm',
                learning_outcomes: [{ loIndex: 0, weight: 1 }],
            },
        ];
    });

    function addLearningOutcome() {
        learningOutcomes = [
            ...learningOutcomes,
            {
                description: '',
                program_outcomes: [
                    { code: programOutcomes[0]?.code ?? '', weight: 1 },
                ],
            },
        ];
    }

    function addProgramOutcome(loIndex: number) {
        learningOutcomes = learningOutcomes.map((lo, i) =>
            i === loIndex
                ? {
                      ...lo,
                      program_outcomes: [
                          ...lo.program_outcomes,
                          {
                              code: programOutcomes[0]?.code ?? '',
                              weight: 1,
                          },
                      ],
                  }
                : lo,
        );
    }

    function addAssessment() {
        assessments = [
            ...assessments,
            {
                assessment_type: 'midterm',
                learning_outcomes: [{ loIndex: 0, weight: 1 }],
            },
        ];
    }

    function addAssessmentLO(aIndex: number) {
        assessments = assessments.map((a, i) =>
            i === aIndex
                ? {
                      ...a,
                      learning_outcomes: [
                          ...a.learning_outcomes,
                          { loIndex: 0, weight: 1 },
                      ],
                  }
                : a,
        );
    }

    async function createCourse() {
        if (!courseCode || !courseName) {
            alert('Course code and name required');
            return;
        }

        const payload = {
            course_code: courseCode,
            course_name: courseName,
            learning_outcomes: learningOutcomes.map((lo, i) => ({
                code: `${courseCode}-LO${i + 1}`,
                description: lo.description,
                program_outcomes: lo.program_outcomes,
            })),
            assessments: assessments.map((a) => ({
                assessment_type: a.assessment_type,
                learning_outcomes: a.learning_outcomes.map((lo) => ({
                    code: `${courseCode}-LO${lo.loIndex + 1}`,
                    weight: lo.weight,
                })),
            })),
        };

        const res = await fetch('http://localhost:8080/api/courses/', {
            method: 'POST',
            headers: {
                Authorization: `Bearer ${accessToken}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),
        });

        if (res.ok) {
            goto('/dashboard/courses');
        } else {
            alert('Failed to create course');
        }
    }
</script>

<div class="min-h-screen bg-[#0b0b10]">
    <div class="max-w-6xl mx-auto px-8 py-10 space-y-12">
        <div class="space-y-1">
            <h1 class="text-3xl font-semibold text-white">Create Course</h1>
            <p class="text-sm text-gray-400">
                Configure learning outcomes and assessments
            </p>
        </div>

        <div
            class="grid grid-cols-1 md:grid-cols-2 gap-6
                   bg-[#0f0f16] border border-white/5 rounded-2xl p-6"
        >
            <div>
                <label class="text-xs text-gray-400" for="course-code"
                    >Course Code</label
                >
                <input
                    id="course-code"
                    bind:value={courseCode}
                    class="mt-2 w-full rounded-lg bg-[#0b0b10]
            border border-white/5 px-4 py-2.5
            text-white outline-none
            focus:border-purple-500/50"
                />
            </div>

            <div>
                <label class="text-xs text-gray-400" for="course-name"
                    >Course Name</label
                >
                <input
                    id="course-name"
                    bind:value={courseName}
                    class="mt-2 w-full rounded-lg bg-[#0b0b10]
                           border border-white/5 px-4 py-2.5
                           text-white outline-none
                           focus:border-purple-500/50"
                />
            </div>
        </div>

        <section class="space-y-6">
            <div class="flex items-center justify-between">
                <h2 class="text-lg font-medium text-white">
                    Learning Outcomes
                </h2>

                <button
                    on:click={addLearningOutcome}
                    class="px-3 py-2 rounded-lg
                           bg-purple-600/15 text-purple-400
                           hover:bg-purple-600/25 transition text-sm"
                >
                    + Add Outcome
                </button>
            </div>

            {#each learningOutcomes as lo, i}
                <div
                    class="rounded-xl p-5 space-y-4
                           bg-[#0f0f16] border border-white/5"
                >
                    <h3 class="text-sm font-medium text-purple-400">
                        {courseCode || 'COURSE'}-LO{i + 1}
                    </h3>

                    <input
                        bind:value={lo.description}
                        placeholder="Learning outcome description"
                        class="w-full rounded-lg bg-[#0b0b10]
                               border border-white/5 px-4 py-2.5
                               text-white outline-none
                               focus:border-purple-500/50"
                    />

                    <div class="space-y-2">
                        <p class="text-xs text-gray-400">Program Outcomes</p>

                        {#each lo.program_outcomes as po}
                            <div class="grid grid-cols-3 gap-3">
                                <select
                                    bind:value={po.code}
                                    class="col-span-2 rounded-lg
                                           bg-[#0b0b10] border border-white/5
                                           px-3 py-2 text-white"
                                >
                                    {#each programOutcomes as p}
                                        <option value={p.code}>
                                            {p.description}
                                        </option>
                                    {/each}
                                </select>

                                <select
                                    bind:value={po.weight}
                                    class="rounded-lg bg-[#0b0b10]
                                           border border-white/5 px-3 py-2 text-white"
                                >
                                    {#each [1, 2, 3, 4, 5] as w}
                                        <option value={w}>{w}</option>
                                    {/each}
                                </select>
                            </div>
                        {/each}

                        <button
                            on:click={() => addProgramOutcome(i)}
                            class="text-xs text-purple-400 hover:text-purple-300"
                        >
                            + Add Program Outcome
                        </button>
                    </div>
                </div>
            {/each}
        </section>

        <section class="space-y-6">
            <div class="flex items-center justify-between">
                <h2 class="text-lg font-medium text-white">Assessments</h2>

                <button
                    on:click={addAssessment}
                    class="px-3 py-2 rounded-lg
                           bg-purple-600/15 text-purple-400
                           hover:bg-purple-600/25 transition text-sm"
                >
                    + Add Assessment
                </button>
            </div>

            {#each assessments as a, aIndex}
                <div
                    class="rounded-xl p-5 space-y-4
                           bg-[#0f0f16] border border-white/5"
                >
                    <select
                        bind:value={a.assessment_type}
                        class="rounded-lg bg-[#0b0b10]
                               border border-white/5 px-3 py-2
                               text-white w-44"
                    >
                        <option value="midterm">Midterm</option>
                        <option value="project">Project</option>
                        <option value="final">Final</option>
                    </select>

                    {#each a.learning_outcomes as lo}
                        <div class="grid grid-cols-3 gap-3">
                            <select
                                bind:value={lo.loIndex}
                                class="col-span-2 rounded-lg
                                       bg-[#0b0b10] border border-white/5
                                       px-3 py-2 text-white"
                            >
                                {#each learningOutcomes as _, i}
                                    <option value={i}>
                                        {courseCode || 'COURSE'}-LO{i + 1}
                                    </option>
                                {/each}
                            </select>

                            <select
                                bind:value={lo.weight}
                                class="rounded-lg bg-[#0b0b10]
                                       border border-white/5 px-3 py-2 text-white"
                            >
                                {#each [1, 2, 3, 4, 5] as w}
                                    <option value={w}>{w}</option>
                                {/each}
                            </select>
                        </div>
                    {/each}

                    <button
                        on:click={() => addAssessmentLO(aIndex)}
                        class="text-xs text-purple-400 hover:text-purple-300"
                    >
                        + Add Learning Outcome
                    </button>
                </div>
            {/each}
        </section>

        <div class="flex justify-end pt-6 border-t border-white/5">
            <button
                on:click={createCourse}
                class="px-3 py-2 rounded-lg
                           bg-purple-600/15 text-purple-400
                           hover:bg-purple-600/25 transition text-sm"
            >
                Create Course
            </button>
        </div>
    </div>
</div>
