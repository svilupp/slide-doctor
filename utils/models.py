from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional

class IssueCategory(str, Enum):
    CHART = "chart"
    SPELL = "spell"
    ALIGNMENT = "alignment"

class ExtractedIssue(BaseModel):
    issue_category: IssueCategory = Field(
        description="The category of the issue, based on the type of checker that identified it."
    )
    issue_description: str = Field(
        description="A detailed description of the issue, including why it's problematic and how it affects the document."
    )
    element_identification_contains_text: Optional[str] = Field(
        description="If the element to fix is a text element, provide a phrase of words that it contains that would uniquely identify it. Provide nothing else. If the element to fix is not text element, return null."
    )
    element_identification_verbatim: Optional[str] = Field(
        description="Describe how to uniquely describe the element to fix if it's not a text box. If the element to fix is a text element, return null."
    )
    severity: str = Field(
        description="The severity level of the issue given the provided context: 'low', 'medium', or 'high'."
    )
    
class DetectedIssue(BaseModel):
    extracted_issue: ExtractedIssue = Field(
        description="The core issue information extracted from the document."
    )
    page_id: int = Field(
        description="The page number where the issue was detected."
    )
    file: str = Field(
        description="The name or path of the file where the issue was found."
    )
    
    
class ExtractedIssueList(BaseModel):
    issues: list[ExtractedIssue] = Field(
        description="A list of issues found in the provided inputs.",
        default_factory=list
    )
