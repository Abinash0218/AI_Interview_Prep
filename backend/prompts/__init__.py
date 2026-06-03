from backend.prompts.technical import TECHNICAL_INTERVIEW_PROMPT
from backend.prompts.coding import CODING_ASSESSMENT_PROMPT
from backend.prompts.hr import HR_INTERVIEW_PROMPT
from backend.prompts.non_technical import NON_TECHNICAL_SKILLS_PROMPT

CATEGORY_PROMPTS = {
    "technical_interview": TECHNICAL_INTERVIEW_PROMPT,
    "coding_assessment": CODING_ASSESSMENT_PROMPT,
    "hr_interview": HR_INTERVIEW_PROMPT,
    "non_technical_skills": NON_TECHNICAL_SKILLS_PROMPT,
}

CATEGORY_LABELS = {
    "technical_interview": "Technical Interview",
    "coding_assessment": "Coding Assessment",
    "hr_interview": "HR Interview",
    "non_technical_skills": "Non Technical Skills",
}
