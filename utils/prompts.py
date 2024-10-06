def build_system_prompt(checker_task: str, user_context: str, checker_list: str) -> str:
    """
    Builds a system prompt for the spellchecker task.

    Args:
    checker_task (str): Description of the checker's task.
    user_context (str): Context of the presentation.
    checker_list (str): List of criteria for checking.

    Returns:
    str: The formatted system prompt.
    """
    text=f"""You are assisting the user with improving their presentation for the given use case and audience.

Your task is to {checker_task} in the provided materials.

Context of the presentation: {user_context}

### Criteria{checker_list}

### Instructions
- You must follow the provided criteria, any other issues should be ignored.
- Extract at most five most important issues that you can detect. It's okay to extract fewer, you must prioritize the most severe problems.
- If there are no important issues, just return an empty list. 
- Describe clearly the issue based on the provided criteria.
- Provide severity (low, medium, high) of the issue using the context of the presentation.
- Return only UNIQUE issues. Issues of the same type and same description (eg, formatting of units), need to be raised only once. 
    Do not create an issue for each value with the same problem. Deduplicate issues with the same description.

Remember to only extract the issues described in the above criteria.    
Be very selective and return only the MOST important issues that require immediate attention.
If no issues are critical, you return an empty list.
"""
    return text

def build_user_prompt(slide_content: str | None) -> str:
    """
    Builds a user prompt for the spellchecker task.

    Args:
    slide_content (str): The content of the presentation slides.

    Returns:
    str: The formatted user prompt.
    """
    slide_text = ""
    if slide_content is not None:
       slide_text = f"\n### Slide Content\n{slide_content}"
    text = f"Please help me improve this presentation slide.{slide_text}"
    return text
