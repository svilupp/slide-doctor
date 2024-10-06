from typing import List
from .models import ExtractedIssue, DetectedIssue, IssueLocation


def generate_mock_detected_issues() -> List[DetectedIssue]:
    mock_issues = [
        DetectedIssue(
            extracted_issue=ExtractedIssue(
                issue_description="The pie chart on slide 2 lacks clear labels, making it difficult for the audience to interpret the data accurately.",
                element_location=IssueLocation.BODY_VISUAL,
                element_identification_contains_text=None,
                element_identification_verbatim="Pie chart without labels on slide 2",
                severity="medium"
            ),
            category="Chart",
            page_id=2,
            file="presentation.pptx"
        ),
        DetectedIssue(
            extracted_issue=ExtractedIssue(
                issue_description="There's a spelling error in the title of slide 2. 'Anual' should be 'Annual'.",
                element_location=IssueLocation.TITLE,
                element_identification_contains_text="Anual Report",
                element_identification_verbatim=None,
                severity="high"
            ),
            category="Spelling",
            page_id=2,
            file="presentation.pptx"
        ),
        DetectedIssue(
            extracted_issue=ExtractedIssue(
                issue_description="The bullet points on slide 3 are not aligned consistently, creating a visually disorganized appearance.",
                element_location=IssueLocation.BODY_TEXT,
                element_identification_contains_text=None,
                element_identification_verbatim="Misaligned bullet points on slide 3",
                severity="low"
            ),
            category="Alignment",
            page_id=3,
            file="presentation.pptx"
        ),
        DetectedIssue(
            extracted_issue=ExtractedIssue(
                issue_description="The bar graph on slide 3 uses colors that are too similar, making it challenging to distinguish between different data sets.",
                element_location=IssueLocation.BODY_VISUAL,
                element_identification_contains_text=None,
                element_identification_verbatim="Bar graph with similar colors on slide 3",
                severity="medium"
            ),
            category="Chart",
            page_id=3,
            file="presentation.pptx"
        ),
        DetectedIssue(
            extracted_issue=ExtractedIssue(
                issue_description="There's a typo in the footer of slide 3. 'Confidental' should be 'Confidential'.",
                element_location=IssueLocation.FOOTER,
                element_identification_contains_text="Confidental",
                element_identification_verbatim=None,
                severity="high"
            ),
            category="Spelling",
            page_id=3,
            file="presentation.pptx"
        )
    ]
    
    return mock_issues
