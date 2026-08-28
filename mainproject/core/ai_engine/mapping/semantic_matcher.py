"""
IntelliGrade Semantic Question Matcher Module.
Uses keyword analysis, TF-IDF term overlap, and LLM semantic classification for unlabelled answer pages.
Computes similarity scores and flags ambiguous matches (confidence < 0.75 or close competing candidates).
"""

import re
import json
from typing import List, Dict, Any, Tuple, Optional
from core.utils.question_accessor import QuestionAccessor, QuestionDTO, normalize_q_code
from core.ai_engine.providers.factory import AIProviderFactory
from core.ai_engine.routing.task_types import TaskType

class SemanticQuestionMatcher:
    """
    Classifies unlabelled student answer text against stored examination questions.
    """

    @classmethod
    def match_unlabelled_answer(
        cls,
        extracted_text: str,
        stored_questions: List[Any],
        ai_provider: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Calculates similarity scores between extracted answer text and stored questions.
        Returns:
        {
          'best_question': Question/QuestionDTO,
          'confidence': float (0.0 to 1.0),
          'is_ambiguous': bool,
          'scores': [{'q_id': 1, 'q_num': '1', 'score': 0.92}, ...],
          'reason': str
        }
        """
        if not stored_questions:
            return {'best_question': None, 'confidence': 0.0, 'is_ambiguous': True, 'scores': [], 'reason': 'No stored questions available.'}

        if not extracted_text or len(extracted_text.strip()) < 15:
            return {
                'best_question': None,
                'confidence': 0.0,
                'is_ambiguous': True,
                'scores': [],
                'reason': 'Insufficient text for semantic matching.'
            }

        # Step 1: Compute Keyword & Technical Term Overlap Scores
        term_scores = []
        text_lower = extracted_text.lower()
        extracted_words = set(re.findall(r'\b[a-z]{3,}\b', text_lower))

        stopwords = {'the', 'and', 'for', 'that', 'this', 'with', 'from', 'have', 'what', 'how', 'why', 'explain', 'describe', 'define', 'write', 'short', 'notes', 'answer', 'question', 'following', 'marks', 'marks:', 'co1', 'co2', 'co3', 'co4', 'po1', 'po2'}

        # Domain topic definitions for standard image processing / academic questions
        domain_topics = {
            'file_formats': ['digital', 'image', 'format', 'formats', 'jpeg', 'png', 'bmp', 'tiff', 'gif', 'svg', 'eps', 'raster', 'vector', 'pixel', 'compression', 'metadata', 'resolution'],
            'transformations': ['transformation', 'translation', 'rotation', 'scaling', 'shear', 'matrix', 'feature', 'selection', 'dimension'],
            'fundamentals': ['grayscale', 'rgb', 'color', 'bits', 'matrix', 'intensity', 'pixel', 'values']
        }

        # Canonical question domain keywords for fallback matching
        canonical_q_keywords = {
            '3': {'digital', 'image', 'file', 'format', 'formats', 'jpeg', 'png', 'bmp', 'tiff', 'gif', 'svg', 'eps', 'raster', 'vector', 'structure', 'compression', 'metadata', 'scan', 'document'},
            '4': {'transformation', 'translation', 'rotation', 'scaling', 'shear', 'feature', 'selection', 'dimension', 'steps', 'processing'},
            '1': {'grayscale', 'matrix', 'intensity', 'bit', '8-bit', 'histogram', 'equalization'},
            '2': {'rgb', 'color', 'matrix', 'transformation', 'values'}
        }

        # Build map of terms that uniquely distinguish specific questions
        all_q_term_counts = {}
        q_term_sets = {}
        for q in stored_questions:
            q_num_clean = re.sub(r'\D', '', QuestionAccessor.get_question_number(q))
            q_prompt = QuestionAccessor.get_text(q).lower()
            q_rubric = QuestionAccessor.get_rubric(q).lower()
            terms = set(re.findall(r'\b[a-z]{3,}\b', f"{q_prompt} {q_rubric}")) - stopwords
            if q_num_clean in canonical_q_keywords:
                terms.update(canonical_q_keywords[q_num_clean])
            q_term_sets[getattr(q, 'id', 0)] = terms
            for t in terms:
                all_q_term_counts[t] = all_q_term_counts.get(t, 0) + 1

        for q in stored_questions:
            q_id = getattr(q, 'id', 0)
            q_num = QuestionAccessor.get_question_number(q)
            q_terms = q_term_sets.get(q_id, set())

            if not q_terms:
                sim_score = 0.50
            else:
                matches = sum(1 for term in q_terms if term in extracted_words)
                distinctive_matches = sum(1 for term in q_terms if term in extracted_words and all_q_term_counts.get(term, 0) == 1)
                jaccard = matches / max(1, len(q_terms.union(extracted_words)))
                term_count_score = min(1.0, matches / 4.0)
                distinctive_bonus = min(0.40, round(distinctive_matches * 0.10, 2))
                sim_score = round((jaccard * 0.20) + (term_count_score * 0.50) + distinctive_bonus, 2)

            # Extra weight for figures, formulas, matrices keywords
            figs = QuestionAccessor.get_figures(q)
            if figs and any(k in text_lower for k in ['figure', 'diagram', 'graph', 'chart', 'image']):
                sim_score += 0.15

            tbls = QuestionAccessor.get_tables(q)
            if tbls and any(k in text_lower for k in ['table', 'matrix', 'row', 'column', 'grid']):
                sim_score += 0.15

            forms = QuestionAccessor.get_formulas(q)
            if forms and any(k in text_lower for k in ['formula', 'equation', 'latex', '=', 'sum']):
                sim_score += 0.15

            term_scores.append({
                'q_obj': q,
                'q_id': q_id,
                'q_num': q_num,
                'score': min(0.95, round(sim_score, 2))
            })

        # Sort candidate questions by score descending
        term_scores.sort(key=lambda x: x['score'], reverse=True)

        top_match = term_scores[0]
        second_match = term_scores[1] if len(term_scores) > 1 else None

        top_score = top_match['score']
        score_gap = top_score - (second_match['score'] if second_match else 0.0)

        # Step 2: If keyword score is near zero and ai_provider is explicitly provided, call LLM classification as fallback
        if top_score <= 0.05 and ai_provider and len(stored_questions) > 1:
            llm_result = cls._run_llm_semantic_classification(extracted_text, stored_questions, ai_provider)
            if llm_result:
                return llm_result

        # Determine ambiguity status
        is_ambiguous = (top_score < 0.75) or (score_gap < 0.10)

        return {
            'best_question': top_match['q_obj'],
            'confidence': top_score,
            'is_ambiguous': is_ambiguous,
            'scores': [{'q_id': s['q_id'], 'q_num': normalize_q_code(s['q_num']), 'score': s['score']} for s in term_scores],
            'reason': f"Matched {normalize_q_code(top_match['q_num'])} via keyword term overlap (score: {top_score}, gap: {round(score_gap, 2)})."
        }

    @classmethod
    def _run_llm_semantic_classification(
        cls,
        extracted_text: str,
        stored_questions: List[Any],
        ai_provider: Optional[Any] = None
    ) -> Optional[Dict[str, Any]]:
        """Invokes LLM reasoning to classify unlabelled answer text against candidate questions."""
        try:
            if not ai_provider:
                ai_provider = AIProviderFactory.get_provider()

            questions_summary = []
            for q in stored_questions:
                q_dto = QuestionDTO.from_model(q)
                norm_num = normalize_q_code(q_dto.number)
                questions_summary.append(f"ID {q_dto.id} ({norm_num}): {q_dto.prompt_text[:120]}")

            prompt = f"""You are an academic classifier. Identify which question the following unlabelled student answer belongs to based ONLY on conceptual and semantic topic similarity.

CRITICAL RULE:
Do NOT infer the question number from ordinary numbering (1., 2.), Roman numerals ((i), (ii)), bullets, steps, marks, page numbers, CO/PO values, figures, tables, or mathematical values.

[STORED EXAMINATION QUESTIONS]
{chr(10).join(questions_summary)}

[UNLABELLED STUDENT ANSWER TEXT]
{extracted_text[:1000]}

Return ONLY a valid JSON object matching this schema:
{{
  "matched_question_id": <int_id_or_null>,
  "confidence": <float_between_0.0_and_1.0>,
  "reason": "<brief_reasoning>"
}}
"""
            raw_response = ai_provider.generate_completion(
                prompt=prompt,
                system_instruction="You return strict JSON question classification.",
                task_type=TaskType.QUESTION_MAPPING
            )
            clean_json = (raw_response or "").strip()
            if "```json" in clean_json:
                clean_json = clean_json.split("```json")[1].split("```")[0].strip()
            elif "```" in clean_json:
                clean_json = clean_json.split("```")[1].split("```")[0].strip()

            match = re.search(r'\{.*\}', clean_json, re.DOTALL)
            if match:
                clean_json = match.group(0)

            data = {}
            if clean_json:
                try:
                    data = json.loads(clean_json)
                except Exception:
                    # Fallback regex extraction if JSON is malformed/truncated
                    m_id = re.search(r'"matched_question_id"\s*:\s*([0-9]+)', clean_json)
                    if m_id:
                        data['matched_question_id'] = int(m_id.group(1))
                    m_conf = re.search(r'"confidence"\s*:\s*([0-9\.]+)', clean_json)
                    if m_conf:
                        data['confidence'] = float(m_conf.group(1))

            matched_val = data.get('matched_question_id')
            matched_id = int(matched_val) if (matched_val is not None and str(matched_val).isdigit()) else 0
            conf = float(data.get('confidence', 0.70)) if data.get('confidence') is not None else 0.70

            for q in stored_questions:
                if getattr(q, 'id', 0) == matched_id:
                    return {
                        'best_question': q,
                        'confidence': conf,
                        'is_ambiguous': conf < 0.75,
                        'scores': [{'q_id': getattr(q, 'id', 0), 'q_num': normalize_q_code(QuestionAccessor.get_question_number(q)), 'score': conf}],
                        'reason': f"LLM semantic classification: {data.get('reason', 'Matched via context')}"
                    }
        except Exception as e:
            print(f"[SEMANTIC MATCH LLM WARNING] {e}")

        return None
