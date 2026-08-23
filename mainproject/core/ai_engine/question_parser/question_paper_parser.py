import re
import json
from typing import Dict, Any, List
from core.ai_engine.providers.factory import AIProviderFactory
from core.ai_engine.parser.academic_parser import AcademicParserService
from django.db import transaction
from core.models import Examination, Question, Rubric, QuestionFigure, QuestionTable, QuestionFormula

class QuestionPaperParser:
    """
    Production Question Paper Parser for IntelliGrade.
    Extracts complete IUBAT paper structure: University, Department, Semester, Course,
    Course Code, Instructor, Exam, Duration, Total Marks, Instructions, Questions, Sub-parts,
    Figures, Tables, Bloom Level, CO, PO, Command Verbs, and Rubric Criteria.
    """

    def __init__(self):
        self.doc_parser = AcademicParserService()

    def parse_and_store_paper(self, examination: Examination, document_text_or_bytes: Any) -> Dict[str, Any]:
        """
        Parses uploaded question paper document and automatically stores all questions & rubrics in DB.
        """
        doc_str = str(document_text_or_bytes) if isinstance(document_text_or_bytes, str) else "Question Paper Document"
        
        # Step 1: Pass through Academic Document Layout Parser
        parsed_doc = self.doc_parser.parse_document(doc_str)

        # Step 2: Extract & Validate Questions using LLM Provider Failover Chain
        provider = AIProviderFactory.get_provider()
        prompt = f"""
You are an expert Academic Question Paper Scanner.
Parse the examination paper content below into clean structured JSON:

{doc_str[:4000]}

Return ONLY a valid JSON object matching this schema:
{{
  "header": {{
    "university": "IUBAT",
    "department": "Computer Science & Engineering",
    "course_code": "CSE 411",
    "course_title": "Software Engineering",
    "duration": "3 Hours",
    "total_marks": 100.0,
    "instructions": "Answer all questions."
  }},
  "questions": [
    {{
      "question_number": "Q1 (a)",
      "prompt_text": "Exact statement of question...",
      "allocated_marks": 5.0,
      "question_type": ["Theory"],
      "command_verbs": ["Explain"],
      "bloom_level": "Understand",
      "co_mapping": "CO1",
      "po_mapping": ["PO1"],
      "criteria": "1. Explanation of core principles (5 marks)",
      "ideal_answer": "Model answer for the question..."
    }}
  ]
}}
"""
        try:
            raw_res = provider.generate_completion(prompt, system_instruction="Return ONLY raw JSON.")
            cleaned = re.sub(r'```json\s*', '', raw_res)
            cleaned = re.sub(r'```\s*', '', cleaned).strip()
            llm_parsed = json.loads(cleaned)
            if isinstance(llm_parsed, dict) and 'questions' in llm_parsed and llm_parsed['questions']:
                parsed_doc['questions'] = llm_parsed['questions']
        except Exception:
            pass

        # Step 3: Automatically Store Questions, Rubrics, Figures & Tables in Database
        questions_saved = []
        with transaction.atomic():
            for item in parsed_doc.get('questions', []):
                q_num = item.get('question_number') or 'Q1'
                q_marks = float(item.get('allocated_marks') or 10.0)
                q_prompt = item.get('prompt_text') or ''
                q_bloom = item.get('bloom_level') or 'Understand'
                q_co = item.get('co_mapping') or 'CO1'
                q_po = item.get('po_mapping') or ['PO1']
                q_criteria = item.get('criteria') or f"1. Accurate response ({q_marks} marks)"
                q_answer = item.get('ideal_answer') or ''

                q_obj, _ = Question.objects.update_or_create(
                    examination=examination,
                    question_number=q_num,
                    defaults={
                        'prompt_text': q_prompt,
                        'max_marks': q_marks,
                        'bloom_level': q_bloom,
                        'co_mapping': q_co,
                        'po_mapping': q_po if isinstance(q_po, list) else [q_po],
                        'question_type': item.get('question_type', ['Theory']),
                        'command_verbs': item.get('command_verbs', ['Explain'])
                    }
                )

                Rubric.objects.update_or_create(
                    question=q_obj,
                    defaults={
                        'criteria': q_criteria,
                        'expected_answer': q_answer,
                        'ideal_answer': q_answer
                    }
                )

                # Persist associated QuestionFigure relations
                figures = item.get('figures') or item.get('associated_figures') or []
                if figures:
                    QuestionFigure.objects.filter(question=q_obj).delete()
                    for idx, fig_data in enumerate(figures, start=1):
                        img_val = fig_data.get('crop_path') or fig_data.get('image_path') or fig_data.get('image') or ''
                        bbox_val = fig_data.get('bounding_box') or fig_data.get('bbox') or []
                        QuestionFigure.objects.create(
                            question=q_obj,
                            page_number=fig_data.get('page_number', fig_data.get('page', 1)),
                            caption=fig_data.get('caption', ''),
                            image=img_val,
                            bounding_box=bbox_val,
                            display_order=fig_data.get('display_order', idx)
                        )

                # Persist associated QuestionTable relations
                tables = item.get('tables') or item.get('associated_tables') or []
                if tables:
                    QuestionTable.objects.filter(question=q_obj).delete()
                    for idx, tbl_data in enumerate(tables, start=1):
                        img_val = tbl_data.get('crop_path') or tbl_data.get('image_path') or tbl_data.get('image') or ''
                        bbox_val = tbl_data.get('bounding_box') or tbl_data.get('bbox') or []
                        QuestionTable.objects.create(
                            question=q_obj,
                            page_number=tbl_data.get('page_number', tbl_data.get('page', 1)),
                            element_type=tbl_data.get('element_type', 'TABLE'),
                            caption=tbl_data.get('caption', ''),
                            image=img_val,
                            bounding_box=bbox_val,
                            rows=tbl_data.get('rows', 0),
                            columns=tbl_data.get('columns', 0),
                            cell_json=tbl_data.get('cell_json', []),
                            table_data=tbl_data.get('table_data', {}),
                            display_order=tbl_data.get('display_order', idx)
                        )

                # Persist associated QuestionFormula relations if available
                formulas = item.get('formulas') or item.get('associated_formulas') or []
                if formulas:
                    QuestionFormula.objects.filter(question=q_obj).delete()
                    for idx, form_data in enumerate(formulas, start=1):
                        bbox_val = form_data.get('bounding_box') or form_data.get('bbox') or []
                        QuestionFormula.objects.create(
                            question=q_obj,
                            page_number=form_data.get('page_number', form_data.get('page', 1)),
                            caption=form_data.get('caption', ''),
                            raw_latex=form_data.get('raw_latex', ''),
                            bounding_box=bbox_val,
                            display_order=form_data.get('display_order', idx)
                        )

                questions_saved.append(q_obj.question_number)

        return {
            "success": True,
            "examination_id": examination.id,
            "questions_saved": len(questions_saved),
            "data": parsed_doc
        }
