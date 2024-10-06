# Import specific functions from each module
from .utils import load_config, extract_slide_number
from .models import IssueLocation, ExtractedIssue, DetectedIssue, ExtractedIssueList, IsValidIssue
from .mocks import generate_mock_detected_issues
from .image_utils import encode_image, get_image_data_url
from .pptx_utils import extract_text_from_pptx
from .client import MistralClientWrapper
from .screenshots import convert_pptx_to_images
from .deduplication import dedupe_by_similarity