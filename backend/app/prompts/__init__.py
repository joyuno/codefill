"""
CodeFill Agent System Prompts
"""

from .chat_agent import (
    CHAT_AGENT_SYSTEM_PROMPT,
    TOPIC_ALIASES,
    DIFFICULTY_MAP,
    LEVEL_RECOMMENDATIONS
)

from .blank_problem_agent import (
    BLANK_PROBLEM_SYSTEM_PROMPT,
    BLANK_DIFFICULTY_CONFIG
)

from .puzzle_problem_agent import (
    PUZZLE_PROBLEM_SYSTEM_PROMPT,
    PUZZLE_DIFFICULTY_CONFIG
)

from .guided_problem_agent import (
    GUIDED_PROBLEM_SYSTEM_PROMPT,
    GUIDED_DIFFICULTY_CONFIG,
    GUIDED_TUTOR_CHAT_PROMPT,
    GUIDED_FEEDBACK_PROMPT
)

from .code_gen_agent import (
    CODE_GEN_SYSTEM_PROMPT,
    LEVEL_TOPIC_RECOMMENDATIONS,
    TOPIC_REQUIRED_CONCEPTS
)


from .free_chat_agent import (
    FREE_CHAT_SYSTEM_PROMPT,
    INTENT_ACTION_MAP,
    CONTEXT_REQUIRED_INTENTS
)

from .analysis_agent import (
    ANALYSIS_SYSTEM_PROMPT
)

from .feedback_agent import (
    FEEDBACK_SYSTEM_PROMPT,
    PROBLEM_TYPE_METRICS,
    GUIDED_SPECIAL_FEEDBACK,
    DIFFICULTY_CONFIG,
    calculate_grade,
    calculate_scores,
    calculate_xp,
    format_solve_time,
    get_difficulty_config,
    get_problem_type_stats,
    calculate_type_specific_grade,
)

from .guided_tutor_agent import (
    GUIDED_INITIAL_PROMPT,
    GUIDED_TUTOR_SYSTEM_PROMPT,
    STUDENT_STATUS,
    GUIDANCE_LEVEL,
    DIFFICULTY_GUIDANCE
)

__all__ = [
    # Chat Agent
    "CHAT_AGENT_SYSTEM_PROMPT",
    "TOPIC_ALIASES",
    "DIFFICULTY_MAP",
    "LEVEL_RECOMMENDATIONS",
    # Blank Problem Agent
    "BLANK_PROBLEM_SYSTEM_PROMPT",
    "BLANK_DIFFICULTY_CONFIG",
    # Puzzle Problem Agent
    "PUZZLE_PROBLEM_SYSTEM_PROMPT",
    "PUZZLE_DIFFICULTY_CONFIG",
    # Guided Problem Agent
    "GUIDED_PROBLEM_SYSTEM_PROMPT",
    "GUIDED_DIFFICULTY_CONFIG",
    "GUIDED_TUTOR_CHAT_PROMPT",
    "GUIDED_FEEDBACK_PROMPT",
    # Code Generation Agent
    "CODE_GEN_SYSTEM_PROMPT",
    "LEVEL_TOPIC_RECOMMENDATIONS",
    "TOPIC_REQUIRED_CONCEPTS",
    # Free Chat Agent
    "FREE_CHAT_SYSTEM_PROMPT",
    "INTENT_ACTION_MAP",
    "CONTEXT_REQUIRED_INTENTS",
    # Analysis Agent
    "ANALYSIS_SYSTEM_PROMPT",
    # Feedback Agent (4가지 문제 유형 통합)
    "FEEDBACK_SYSTEM_PROMPT",
    "PROBLEM_TYPE_METRICS",
    "GUIDED_SPECIAL_FEEDBACK",
    "DIFFICULTY_CONFIG",
    "calculate_grade",
    "calculate_scores",
    "calculate_xp",
    "format_solve_time",
    "get_difficulty_config",
    "get_problem_type_stats",
    "calculate_type_specific_grade",
    # Guided Tutor Agent (1대1 대화형 전용)
    "GUIDED_INITIAL_PROMPT",
    "GUIDED_TUTOR_SYSTEM_PROMPT",
    "STUDENT_STATUS",
    "GUIDANCE_LEVEL",
    "DIFFICULTY_GUIDANCE",
]
