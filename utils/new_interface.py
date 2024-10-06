import gradio as gr
from pptx import Presentation
from typing import List
import json

# Assuming the DetectedIssue, ExtractedIssue, and IssueCategory models are defined properly
# Please make sure that you adjust the import according to your project structure
from models import ExtractedIssue, DetectedIssue, IssueCategory

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

# Placeholder sample image path
sample_image_path = "https://via.placeholder.com/150"

def extract_text_from_pptx(file):
    prs = Presentation(file.name)
    
    slides_content = {}
    
    for slide_index, slide in enumerate(prs.slides):
        slide_text = []
        for shape in slide.shapes:
            if shape.has_text_frame:
                slide_text.append(shape.text)
        # Join all text in the slide into a single string
        slide_content = "\n".join(slide_text)
        # print(f"Slide {slide_index + 1} Content:\n{slide_content}\n{'-'*40}")
        slides_content[slide_index + 1] = slide_content  # Slide index as key (1-based)
    
    return json.dumps(slides_content, indent=4)

def create_slide_html(issues_data):
    slides = {}

    # Group issues by slide number (page_id)
    for issue in issues_data:
        slide_number = issue.page_id
        if slide_number not in slides:
            slides[slide_number] = []
        slides[slide_number].append(issue)

    html_content = ""

    # Create the HTML structure for each slide
    for slide_number, issues in slides.items():
        html_content += f"<div style='border:1px solid #ddd; padding: 10px; margin: 10px 0;'><h3>Slide {slide_number}</h3>"
        html_content += f"<img src='{sample_image_path}' alt='Slide {slide_number} Preview' style='width:150px;'/>"
        for i, issue in enumerate(issues, 1):
            issue_description = issue.extracted_issue.issue_description
            severity = issue.extracted_issue.severity.capitalize()
            html_content += f"<p><strong>Issue {i}:</strong> {issue_description} (Severity: {severity})</p>"
        html_content += "</div>"

    return html_content

def process_ppt(context_info, ppt_upload):
    # Extract text from the uploaded PowerPoint file
    slides_content = extract_text_from_pptx(ppt_upload)

    print("slides_content: ", slides_content)
    
    # Generate mock issues data
    issues_data = generate_mock_detected_issues()
    
    # Create the HTML content for slide view
    slide_html = create_slide_html(issues_data)
    
    # Return both the summary and the HTML content
    return "Mock summary generated", slide_html

# Building the Gradio interface
with gr.Blocks() as demo:
    gr.Markdown("# Context Brief")

    context_input = gr.Textbox(label="Context Information", placeholder="Enter context for the presentation")
    ppt_upload = gr.File(label="Upload PPT", file_count="single", file_types=[".ppt", ".pptx"])

    generate_button = gr.Button("Generate Page View")

    gr.Markdown("### Summary")
    summary_output = gr.Textbox(label="Summary", lines=4, interactive=False)

    gr.Markdown("### Page View")
    slide_sections_container = gr.HTML("")  # Use HTML component to dynamically render slide sections

    # Generate Page View on button click
    generate_button.click(
        process_ppt,
        inputs=[context_input, ppt_upload],
        outputs=[summary_output, slide_sections_container]
    )

demo.launch()
