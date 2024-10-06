from typing import List
from .models import ExtractedIssue, DetectedIssue, IssueCategory


def generate_mock_detected_issues() -> List[DetectedIssue]:
    mock_issues = [
        DetectedIssue(
            extracted_issue=ExtractedIssue(
                issue_category=IssueCategory.CHART,
                issue_description="The pie chart on slide 2 lacks clear labels, making it difficult for the audience to interpret the data accurately.",
                element_identification_verbatim="Pie chart without labels on slide 2",
                element_identification_contains_text=None,
                severity="medium"
            ),
            page_id=2,
            file="presentation.pptx"
        ),
        DetectedIssue(
            extracted_issue=ExtractedIssue(
                issue_category=IssueCategory.SPELL,
                issue_description="There's a spelling error in the title of slide 2. 'Anual' should be 'Annual'.",
                element_identification_contains_text="Anual Report",
                element_identification_verbatim=None,
                severity="high"
            ),
            page_id=2,
            file="presentation.pptx"
        ),
        DetectedIssue(
            extracted_issue=ExtractedIssue(
                issue_category=IssueCategory.ALIGNMENT,
                issue_description="The bullet points on slide 3 are not aligned consistently, creating a visually disorganized appearance.",
                element_identification_verbatim="Misaligned bullet points on slide 3",
                element_identification_contains_text=None,
                severity="low"
            ),
            page_id=3,
            file="presentation.pptx"
        ),
        DetectedIssue(
            extracted_issue=ExtractedIssue(
                issue_category=IssueCategory.CHART,
                issue_description="The bar graph on slide 3 uses colors that are too similar, making it challenging to distinguish between different data sets.",
                element_identification_verbatim="Bar graph with similar colors on slide 3",
                element_identification_contains_text=None,
                severity="medium"
            ),
            page_id=3,
            file="presentation.pptx"
        ),
        DetectedIssue(
            extracted_issue=ExtractedIssue(
                issue_category=IssueCategory.SPELL,
                issue_description="There's a typo in the footer of slide 3. 'Confidental' should be 'Confidential'.",
                element_identification_contains_text="Confidental",
                element_identification_verbatim=None,
                severity="high"
            ),
            page_id=3,
            file="presentation.pptx"
        )
    ]
    
    return mock_issues
