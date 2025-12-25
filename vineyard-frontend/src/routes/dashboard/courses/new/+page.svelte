<script lang="ts">
    import { auth } from '$lib/stores/auth';
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';

    type ProgramOutcome = { code: string; weight: number };
    type LearningOutcome = {
        description: string;
        program_outcomes: ProgramOutcome[];
    };
    type AssessmentLearningOutcome = { loIndex: number; weight: number };
    type Assessment = {
        assessment_type: 'midterm' | 'project' | 'final' | 'assignment';
        learning_outcomes: AssessmentLearningOutcome[];
    };

    let accessToken: string | null = null;
    let courseCode = '';
    let courseName = '';
    let learningOutcomes: LearningOutcome[] = [];
    let assessments: Assessment[] = [];
    let programOutcomes: { code: string; description: string }[] = [];

    // Task state
    let taskStatus = '';

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

    async function sendWordAndPO(file: File) {
        if (!accessToken) return;

        taskStatus = 'Uploading Word file and program outcomes...';

        const formData = new FormData();
        formData.append('file', file);
        formData.append('course_code', courseCode);
        formData.append('program_outcomes', JSON.stringify(programOutcomes));

        console.log(formData);

        const res = await fetch('http://localhost:8080/api/tasks/generate/', {
            method: 'POST',
            headers: { Authorization: `Bearer ${accessToken}` },
            body: formData,
        });

        if (!res.ok) {
            taskStatus = 'Upload failed';
            return;
        }

        const data = await res.json();
        const taskId = data.task_id;
        taskStatus = 'Task started...';

        const interval = setInterval(async () => {
            const resultRes = await fetch(
                `http://localhost:8080/api/tasks/generate/${taskId}/`,
                {
                    headers: { Authorization: `Bearer ${accessToken}` },
                },
            );

            const resultData = await resultRes.json();
            taskStatus = resultData.status;

            if (
                resultData.status === 'SUCCESS' ||
                resultData.status === 'FAILURE'
            ) {
                clearInterval(interval);

                if (resultData.status === 'SUCCESS') {
                    taskStatus = 'Task completed successfully';
                    console.log(resultData.result);

                    const aiResult = resultData.result as {
                        LOs: Array<{
                            LO: string;
                            description: string;
                            POs: Record<string, number>;
                        }>;
                        Assessments: Record<string, Record<string, number>>;
                    };

                    learningOutcomes = aiResult.LOs.map((lo) => ({
                        description: lo.description,
                        program_outcomes: Object.entries(lo.POs).map(
                            ([code, weight]) => ({
                                code,
                                weight,
                            }),
                        ),
                    }));

                    assessments = Object.entries(aiResult.Assessments).map(
                        ([assessment_type, loDict]) => ({
                            assessment_type: assessment_type.toLowerCase() as
                                | 'midterm'
                                | 'project'
                                | 'final'
                                | 'assignment',
                            learning_outcomes: Object.entries(loDict).map(
                                ([loCode, weight]) => {
                                    const loIndex = learningOutcomes.findIndex(
                                        (lo, i) =>
                                            `${courseCode}-LO${i + 1}` ===
                                                loCode ||
                                            loCode === `LO${i + 1}`,
                                    );
                                    return {
                                        loIndex: loIndex >= 0 ? loIndex : 0,
                                        weight,
                                    };
                                },
                            ),
                        }),
                    );

                    taskStatus = '';
                } else {
                    taskStatus = 'Task failed';
                }
            }
        }, 1000);
    }

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
                          { code: programOutcomes[0]?.code ?? '', weight: 1 },
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

        console.log(payload);

        const res = await fetch('http://localhost:8080/api/courses/', {
            method: 'POST',
            headers: {
                Authorization: `Bearer ${accessToken}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),
        });

        if (res.ok) goto('/dashboard/courses');
        else alert('Failed to create course');
    }
</script>

<!-- Loading overlay -->
{#if taskStatus && taskStatus !== 'Upload failed'}
    <div
        class="fixed inset-0 bg-black/50 flex flex-col items-center justify-center z-50"
    >
        <div
            class="w-14 h-14 border-4 border-purple-500 border-t-transparent rounded-full animate-spin"
        ></div>
        <p class="mt-4 text-white text-sm">
            {#if taskStatus === 'Uploading Word file and program outcomes...'}
                Uploading your syllabus to the cloud...
            {:else if taskStatus === 'Task started...' || taskStatus === 'PENDING'}
                Coffee break?
            {:else if taskStatus === 'Task completed successfully'}
                Ta-da!
            {:else if taskStatus === 'Task failed'}
                Oops!
            {/if}
        </p>
    </div>
{/if}

<div class="min-h-screen bg-[#0b0b10]">
    <div class="max-w-6xl mx-auto px-8 py-10 space-y-12 relative">
        <div class="absolute top-6 right-6 flex items-center justify-end">
            <label
                class="relative px-6 py-3 rounded-2xl bg-linear-to-r from-purple-500 to-pink-500
               text-white font-semibold shadow-lg hover:from-pink-500 hover:to-purple-500
               transition-all duration-300 overflow-hidden flex items-center justify-center cursor-pointer"
            >
                <span class="relative z-10">✨ Generate AI Outcome</span>
                <input
                    type="file"
                    accept=".doc,.docx,.docm,.pdf"
                    class="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                    on:change={(e: Event) => {
                        const input = e.target as HTMLInputElement | null;
                        const file = input?.files?.[0];
                        if (file) sendWordAndPO(file);
                    }}
                />
                <div
                    class="absolute w-0 h-0 rounded-full bg-white/10 top-0 left-0 animate-ping"
                ></div>
            </label>
        </div>

        <div class="space-y-1 flex items-center">
            <h1 class="text-3xl font-semibold text-white">Create Course</h1>
            <span
                class="ml-3 px-2 py-1 text-xs bg-linear-to-r from-purple-500 to-pink-500 text-white rounded-full font-semibold shadow-sm"
            >
                ✨ AI Powered
            </span>
        </div>

        <div
            class="grid grid-cols-1 md:grid-cols-2 gap-6 bg-[#0f0f16] border border-white/5 rounded-2xl p-6"
        >
            <div>
                <label class="text-xs text-gray-400" for="course-code"
                    >Course Code</label
                >
                <input
                    id="course-code"
                    bind:value={courseCode}
                    class="mt-2 w-full rounded-lg bg-[#0b0b10] border border-white/5 px-4 py-2.5 text-white outline-none focus:border-purple-500/50"
                />
            </div>
            <div>
                <label class="text-xs text-gray-400" for="course-name"
                    >Course Name</label
                >
                <input
                    id="course-name"
                    bind:value={courseName}
                    class="mt-2 w-full rounded-lg bg-[#0b0b10] border border-white/5 px-4 py-2.5 text-white outline-none focus:border-purple-500/50"
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
                    class="px-3 py-2 rounded-lg bg-purple-600/15 text-purple-400 hover:bg-purple-600/25 transition text-sm"
                    >+ Add Outcome</button
                >
            </div>
            {#each learningOutcomes as lo, i}
                <div
                    class="rounded-xl p-5 space-y-4 bg-[#0f0f16] border border-white/5"
                >
                    <h3 class="text-sm font-medium text-purple-400">
                        {courseCode || 'COURSE'}-LO{i + 1}
                    </h3>
                    <input
                        bind:value={lo.description}
                        placeholder="Learning outcome description"
                        class="w-full rounded-lg bg-[#0b0b10] border border-white/5 px-4 py-2.5 text-white outline-none focus:border-purple-500/50"
                    />
                    <div class="space-y-2">
                        <p class="text-xs text-gray-400">Program Outcomes</p>
                        {#each lo.program_outcomes as po}
                            <div class="grid grid-cols-3 gap-3">
                                <select
                                    bind:value={po.code}
                                    class="col-span-2 rounded-lg bg-[#0b0b10] border border-white/5 px-3 py-2 text-white"
                                >
                                    {#each programOutcomes as p}
                                        <option value={p.code}
                                            >{p.description}</option
                                        >
                                    {/each}
                                </select>
                                <select
                                    bind:value={po.weight}
                                    class="rounded-lg bg-[#0b0b10] border border-white/5 px-3 py-2 text-white"
                                >
                                    {#each [1, 2, 3, 4, 5] as w}<option
                                            value={w}>{w}</option
                                        >{/each}
                                </select>
                            </div>
                        {/each}
                        <button
                            on:click={() => addProgramOutcome(i)}
                            class="text-xs text-purple-400 hover:text-purple-300"
                            >+ Add Program Outcome</button
                        >
                    </div>
                </div>
            {/each}
        </section>

        <section class="space-y-6">
            <div class="flex items-center justify-between">
                <h2 class="text-lg font-medium text-white">Assessments</h2>
                <button
                    on:click={addAssessment}
                    class="px-3 py-2 rounded-lg bg-purple-600/15 text-purple-400 hover:bg-purple-600/25 transition text-sm"
                    >+ Add Assessment</button
                >
            </div>
            {#each assessments as a, aIndex}
                <div
                    class="rounded-xl p-5 space-y-4 bg-[#0f0f16] border border-white/5"
                >
                    <select
                        bind:value={a.assessment_type}
                        class="rounded-lg bg-[#0b0b10] border border-white/5 px-3 py-2 text-white w-44"
                    >
                        <option value="midterm">Midterm</option>
                        <option value="project">Project</option>
                        <option value="assignment">Assignment</option>
                        <option value="final">Final</option>
                    </select>
                    {#each a.learning_outcomes as lo}
                        <div class="grid grid-cols-3 gap-3">
                            <select
                                bind:value={lo.loIndex}
                                class="col-span-2 rounded-lg bg-[#0b0b10] border border-white/5 px-3 py-2 text-white"
                            >
                                {#each learningOutcomes as _, i}
                                    <option value={i}
                                        >{courseCode || 'COURSE'}-LO{i +
                                            1}</option
                                    >
                                {/each}
                            </select>
                            <select
                                bind:value={lo.weight}
                                class="rounded-lg bg-[#0b0b10] border border-white/5 px-3 py-2 text-white"
                            >
                                {#each [1, 2, 3, 4, 5] as w}<option value={w}
                                        >{w}</option
                                    >{/each}
                            </select>
                        </div>
                    {/each}
                    <button
                        on:click={() => addAssessmentLO(aIndex)}
                        class="text-xs text-purple-400 hover:text-purple-300"
                        >+ Add Learning Outcome</button
                    >
                </div>
            {/each}
        </section>

        <div class="flex justify-end pt-6 border-t border-white/5">
            <button
                on:click={createCourse}
                class="px-3 py-2 rounded-lg bg-purple-600/15 text-purple-400 hover:bg-purple-600/25 transition text-sm"
            >
                Create Course
            </button>
        </div>
    </div>
</div>
