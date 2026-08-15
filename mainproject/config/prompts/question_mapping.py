"""
Question & Answer Mapping Prompts
=================================
"""

QUESTION_MAPPING_SYSTEM_PROMPT = """Analyze student answer script pages and map each page region to its corresponding examination question number.
Respect answer-heading boundaries ('Answer to Question No. X') and flag ambiguous unlabelled pages for teacher review.
Output strict, valid JSON.
"""
