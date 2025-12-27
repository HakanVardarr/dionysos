from django.db.models import Avg

from .models import (
    AssessmentLearningOutcome,
    Course,
    ProgramLearningOutcome,
    ProgramOutcome,
    StudentAssessmentScore,
)


def calculate_course_report(course: Course):
    """
    Returns:
    {
        "assessments": {assesment_id: avg_score},
        "learning_outcomes": {learning_outcome_id: score},
        "program_outcomes": {program_outcome_code: score},
    }
    """

    # ===============================
    # 1️⃣ ASSESSMENT AVERAGES
    # ===============================
    assessment_averages = {}

    for assesment in course.assesments.all():
        avg_score = (
            StudentAssessmentScore.objects.filter(assesment=assesment).aggregate(
                avg=Avg("score")
            )["avg"]
            or 0
        )

        assessment_averages[assesment.id] = round(avg_score, 2)

    # ===============================
    # 2️⃣ LEARNING OUTCOME SCORES
    # ===============================
    learning_outcome_scores = {}

    for lo in course.learning_outcomes.all():
        weighted_sum = 0
        total_weight = 0

        alo_links = AssessmentLearningOutcome.objects.filter(
            learning_outcome=lo,
            assesment__course=course,
        )

        for link in alo_links:
            assesment_avg = assessment_averages.get(link.assesment_id, 0)
            weighted_sum += assesment_avg * link.weight
            total_weight += link.weight

        learning_outcome_scores[lo.id] = (
            round(weighted_sum / total_weight, 2) if total_weight > 0 else 0
        )

    # ===============================
    # 3️⃣ PROGRAM OUTCOME SCORES
    # ===============================
    program_outcome_scores = {}

    for po in ProgramOutcome.objects.all():
        weighted_sum = 0
        total_weight = 0

        plo_links = ProgramLearningOutcome.objects.filter(
            program_outcome=po,
            learning_outcome__course=course,
        )

        for link in plo_links:
            lo_score = learning_outcome_scores.get(link.learning_outcome_id, 0)
            weighted_sum += lo_score * link.weight
            total_weight += link.weight

        program_outcome_scores[po.code] = (
            round(weighted_sum / total_weight, 2) if total_weight > 0 else 0
        )

    return {
        "assessments": assessment_averages,
        "learning_outcomes": learning_outcome_scores,
        "program_outcomes": program_outcome_scores,
    }
