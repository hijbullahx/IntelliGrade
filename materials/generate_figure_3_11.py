"""
Figure 3.11 Generator: Teacher Override, Immutable Audit Trail & Certified PDF Generation
Generated directly according to the provided PDF:
  "F:\\Hijbullah\\IntelliGrade\\materials\\Evaluated_Script_Hijbullah_Roll_22303142 (2).pdf"
Output dimensions: 1800 x 1050 px (6.0 in x 3.5 in @ 300 DPI)
Pure light mode, publication-grade academic aesthetic.
"""

import os
import fitz  # PyMuPDF
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUTPUT_PNG = r"F:\Hijbullah\IntelliGrade\materials\Figure-3.11.png"
PDF_PATH = r"F:\Hijbullah\IntelliGrade\materials\Evaluated_Script_Hijbullah_Roll_22303142 (2).pdf"

def create_figure_3_11():
    # 1. Base SVG layout (1800 x 1050 px)
    svg_content = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1800 1050" width="1800" height="1050">
    <defs>
        <style>
            .figure-title { font-family: 'Segoe UI', Arial, sans-serif; font-size: 21px; font-weight: 800; fill: #0F172A; }
            .figure-sub { font-family: 'Segoe UI', Arial, sans-serif; font-size: 13px; font-weight: 500; fill: #475569; }
            .stage-header-title { font-family: 'Segoe UI', Arial, sans-serif; font-size: 14.5px; font-weight: 800; fill: #FFFFFF; }
            .stage-header-sub { font-family: 'Segoe UI', Arial, sans-serif; font-size: 11px; font-weight: 600; fill: #E2E8F0; }
            .card-title { font-family: 'Segoe UI', Arial, sans-serif; font-size: 12px; font-weight: 800; letter-spacing: 0.4px; }
            .body-text { font-family: 'Segoe UI', Arial, sans-serif; font-size: 11px; fill: #1E293B; line-height: 1.45; }
            .meta-label { font-family: 'Segoe UI', Arial, sans-serif; font-size: 10.5px; font-weight: 700; fill: #334155; }
            .code-text { font-family: 'Consolas', 'Courier New', monospace; font-size: 10px; fill: #0F172A; }
            .pill-text { font-family: 'Segoe UI', Arial, sans-serif; font-size: 9.5px; font-weight: 700; }
        </style>
        <marker id="arrBlue" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#2563EB" />
        </marker>
        <filter id="shadow" x="-3%" y="-2%" width="106%" height="106%">
            <feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#000000" flood-opacity="0.06" />
        </filter>
        <filter id="pageShadow" x="-4%" y="-2%" width="108%" height="108%">
            <feDropShadow dx="0" dy="3" stdDeviation="4" flood-color="#0F172A" flood-opacity="0.14" />
        </filter>
    </defs>

    <!-- Canvas Background -->
    <rect width="1800" height="1050" fill="#FFFFFF" />

    <!-- Top Figure Header -->
    <g transform="translate(30, 18)">
        <rect x="0" y="4" width="4" height="40" rx="2" fill="#2563EB" />
        <text x="16" y="24" class="figure-title">Figure 3.11: Teacher Override, Immutable Audit Trail &amp; Certified PDF Generation</text>
        <text x="16" y="42" class="figure-sub">End-to-End Finalization Architecture: Examiner Mark Adjustments, Immutable Audit Trail, Certified Watermarked PDF Script, and Draft Storage Purge</text>
    </g>

    <!-- ============================================================== -->
    <!-- STAGE 1: EXAMINER OVERRIDE WORKBENCH                          -->
    <!-- Coordinates: x: 30, y: 72, w: 320, h: 940                       -->
    <!-- ============================================================== -->
    <g transform="translate(30, 72)" filter="url(#shadow)">
        <rect width="320" height="940" rx="8" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1.3" />
        
        <!-- Header Bar -->
        <rect width="320" height="38" rx="8" fill="#1E40AF" />
        <rect y="30" width="320" height="8" fill="#1E40AF" />
        <text x="12" y="24" class="stage-header-title">1. Examiner Override</text>
        <text x="308" y="24" text-anchor="end" class="stage-header-sub">Workbench</text>

        <!-- CARD 1A: STUDENT & SCRIPT CONTEXT -->
        <g transform="translate(14, 50)">
            <rect width="292" height="120" rx="6" fill="#FFFFFF" stroke="#93C5FD" stroke-width="1.2" />
            <rect width="292" height="24" rx="6" fill="#EFF6FF" />
            <rect y="18" width="292" height="6" fill="#EFF6FF" />
            <text x="10" y="16" class="card-title" fill="#1E40AF">STUDENT &amp; EVALUATION CONTEXT</text>

            <g transform="translate(10, 34)">
                <text x="0" y="12" class="body-text"><tspan font-weight="700" fill="#1E40AF">Student: </tspan>Hijbullah (Roll: 22303142)</text>
                <text x="0" y="30" class="body-text"><tspan font-weight="700">Course / Exam: </tspan>CSE 4383 Examination</text>
                <text x="0" y="48" class="body-text"><tspan font-weight="700">Examiner: </tspan>Dr. Ferdaus Anam Jibon (Fac #408)</text>
                <text x="0" y="66" class="body-text"><tspan font-weight="700">Script ID: </tspan>#1042  |  <tspan font-weight="700">Pages: </tspan>14 Scanned Pages</text>
                <text x="0" y="80" class="meta-label" fill="#166534">● Active Grading Session: Ready for Review</text>
            </g>
        </g>

        <!-- CARD 1B: SOVEREIGN MARK ADJUSTMENT -->
        <g transform="translate(14, 182)">
            <rect width="292" height="235" rx="6" fill="#FFFFFF" stroke="#3B82F6" stroke-width="1.4" />
            <rect width="292" height="24" rx="6" fill="#DBEAFE" />
            <rect y="18" width="292" height="6" fill="#DBEAFE" />
            <text x="10" y="16" class="card-title" fill="#1D4ED8">SOVEREIGN MARK OVERRIDE SLIDER</text>

            <g transform="translate(10, 32)">
                <text x="0" y="14" class="body-text"><tspan font-weight="700">Target Question: </tspan><tspan font-weight="800" fill="#1E40AF">Q1</tspan> (Histogram Equalization)</text>
                <text x="0" y="29" class="body-text"><tspan font-weight="700">Initial AI Mark: </tspan><tspan font-weight="800" fill="#DC2626">16.5 / 25.0</tspan> (Conf: 0.88)</text>

                <!-- Interactive Slider UI Box -->
                <g transform="translate(0, 37)">
                    <rect width="272" height="72" rx="5" fill="#F8FAFC" stroke="#93C5FD" stroke-width="1" />
                    <text x="10" y="18" font-family="'Segoe UI', Arial, sans-serif" font-size="10.5px" font-weight="700" fill="#1E293B">Examiner Adjusted Mark Input:</text>
                    
                    <!-- Slider Bar -->
                    <rect x="10" y="28" width="252" height="6" rx="3" fill="#E2E8F0" />
                    <rect x="10" y="28" width="192" height="6" rx="3" fill="#2563EB" />
                    <circle cx="202" cy="31" r="7" fill="#1E40AF" stroke="#FFFFFF" stroke-width="2" />
                    
                    <!-- Score Badges -->
                    <rect x="10" y="44" width="112" height="22" rx="3" fill="#FFFFFF" stroke="#3B82F6" stroke-width="1.2" />
                    <text x="18" y="59" font-family="'Segoe UI', Arial, sans-serif" font-size="11.5px" font-weight="800" fill="#1D4ED8">Marks: 19.0 / 25.0</text>

                    <rect x="132" y="44" width="130" height="22" rx="3" fill="#ECFDF5" stroke="#10B981" stroke-width="1" />
                    <text x="140" y="59" font-family="'Segoe UI', Arial, sans-serif" font-size="10px" font-weight="800" fill="#047857">DELTA: +2.50 MARKS</text>
                </g>

                <g transform="translate(0, 120)">
                    <text x="0" y="12" font-family="'Segoe UI', Arial, sans-serif" font-size="10px" font-weight="700" fill="#475569">Rubric Step-Mark Re-allocation:</text>
                    <text x="0" y="26" class="code-text">• PDF &amp; CDF Table: <tspan font-weight="700" fill="#15803D">7.0 / 10.0</tspan> [CO2, PO1]</text>
                    <text x="0" y="40" class="code-text">• Formula Derivation: <tspan font-weight="700" fill="#15803D">4.5 / 5.0</tspan> [CO2, PO1]</text>
                    <text x="0" y="54" class="code-text">• Integer Transform: <tspan font-weight="700" fill="#2563EB">7.5 / 10.0</tspan> (+2.5 restored)</text>
                    <text x="0" y="68" class="code-text" fill="#059669">✔ Full teacher grading sovereignty preserved</text>
                </g>
            </g>
        </g>

        <!-- CARD 1C: EXAMINER JUSTIFICATION & OBE FEEDBACK -->
        <g transform="translate(14, 428)">
            <rect width="292" height="200" rx="6" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.2" />
            <rect width="292" height="24" rx="6" fill="#F1F5F9" />
            <rect y="18" width="292" height="6" fill="#F1F5F9" />
            <text x="10" y="16" class="card-title" fill="#334155">EXAMINER JUSTIFICATION &amp; OBE LOG</text>

            <g transform="translate(10, 32)">
                <text x="0" y="12" class="body-text"><tspan font-weight="700">• Mandatory Audit Justification (Δ &gt; 1.0):</tspan></text>
                
                <g transform="translate(0, 20)">
                    <rect width="272" height="78" rx="4" fill="#F8FAFC" stroke="#E2E8F0" stroke-width="1" />
                    <text x="8" y="16" font-family="'Segoe UI', Arial, sans-serif" font-size="10px" font-weight="600" fill="#475569">Examiner Notes:</text>
                    <text x="8" y="32" font-family="'Segoe UI', Arial, sans-serif" font-size="9.5px" font-style="italic" fill="#0F172A">"Student correctly formulated transformation table</text>
                    <text x="8" y="46" font-family="'Segoe UI', Arial, sans-serif" font-size="9.5px" font-style="italic" fill="#0F172A">and recovered step 3 integer mapping for pixel s(76).</text>
                    <text x="8" y="60" font-family="'Segoe UI', Arial, sans-serif" font-size="9.5px" font-style="italic" fill="#0F172A">Restored 2.5 marks for mathematical accuracy."</text>
                    <text x="8" y="72" font-family="'Segoe UI', Arial, sans-serif" font-size="8.5px" font-weight="700" fill="#2563EB">Target Competency: CO2 (Apply), PO1</text>
                </g>

                <g transform="translate(0, 108)">
                    <text x="0" y="12" class="body-text"><tspan font-weight="700">• Single-Click Re-evaluation Option:</tspan></text>
                    <text x="8" y="26" class="body-text" fill="#64748B">Allows optional re-querying of LLM evaluator</text>
                    <text x="8" y="40" class="body-text" fill="#64748B">with teacher guidance prompts before lock.</text>
                </g>
            </g>
        </g>

        <!-- CARD 1D: FINALIZATION ACTION TRIGGER -->
        <g transform="translate(14, 640)">
            <rect width="292" height="280" rx="6" fill="#FFFFFF" stroke="#16A34A" stroke-width="1.5" />
            <rect width="292" height="24" rx="6" fill="#DCFCE7" />
            <rect y="18" width="292" height="6" fill="#DCFCE7" />
            <text x="10" y="16" class="card-title" fill="#15803D">FINALIZATION ACTION TRIGGER</text>

            <g transform="translate(10, 32)">
                <text x="0" y="14" class="body-text"><tspan font-weight="700">• Total Final Score: </tspan><tspan font-weight="800" fill="#15803D">83.50 / 100.00 (83.5%)</tspan></text>
                <text x="0" y="29" class="body-text"><tspan font-weight="700">• Letter Grade: </tspan><tspan font-weight="800" fill="#15803D">A</tspan>  |  <tspan font-weight="700">Status: </tspan><tspan font-weight="800" fill="#2563EB">FINALIZED</tspan></text>

                <!-- Finalize Button UI -->
                <g transform="translate(0, 40)">
                    <rect width="272" height="38" rx="5" fill="#047857" stroke="#065F46" stroke-width="1" />
                    <text x="136" y="24" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif" font-size="12px" font-weight="800" fill="#FFFFFF">✔ Finalize Evaluation &amp; Stamp PDF →</text>
                </g>

                <g transform="translate(0, 92)">
                    <text x="0" y="12" font-family="'Segoe UI', Arial, sans-serif" font-size="10px" font-weight="700" fill="#334155">Workflow Execution Sequence:</text>
                    <text x="0" y="26" class="code-text">1. FinalizationService.finalize_submission()</text>
                    <text x="0" y="40" class="code-text">2. Saves immutable TeacherReview record</text>
                    <text x="0" y="54" class="code-text">3. Compiles certified PDF with IUBAT stamps</text>
                    <text x="0" y="68" class="code-text">4. Deletes 14 temporary working images</text>
                    <text x="0" y="82" class="code-text">5. Syncs 8-Sheet OBE Course Tabulation</text>
                    <text x="0" y="96" class="code-text">6. Dispatches notification email to student</text>
                </g>

                <g transform="translate(0, 202)">
                    <rect width="272" height="36" rx="4" fill="#F0FDF4" stroke="#BBF7D0" stroke-width="0.8" />
                    <text x="6" y="15" class="code-text" fill="#166534">SubmissionWorkflow.advance(submission,</text>
                    <text x="6" y="28" class="code-text" fill="#15803D">    StudentSubmission.Status.FINALIZED)</text>
                </g>
            </g>
        </g>
    </g>

    <!-- HORIZONTAL FLOW CHEVRON 1 -> 2 -->
    <g transform="translate(355, 520)">
        <circle cx="0" cy="0" r="12" fill="#EFF6FF" stroke="#3B82F6" stroke-width="1.5" />
        <text x="0" y="4.5" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif" font-size="13px" font-weight="900" fill="#2563EB">→</text>
    </g>

    <!-- ============================================================== -->
    <!-- STAGE 2: IMMUTABLE AUDIT LOGGING CORE                          -->
    <!-- Coordinates: x: 370, y: 72, w: 320, h: 940                       -->
    <!-- ============================================================== -->
    <g transform="translate(370, 72)" filter="url(#shadow)">
        <rect width="320" height="940" rx="8" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1.3" />
        
        <!-- Header Bar -->
        <rect width="320" height="38" rx="8" fill="#4338CA" />
        <rect y="30" width="320" height="8" fill="#4338CA" />
        <text x="12" y="24" class="stage-header-title">2. Immutable Audit Trail</text>
        <text x="308" y="24" text-anchor="end" class="stage-header-sub">TeacherReview</text>

        <!-- CARD 2A: APPEND-ONLY INTERCEPTOR -->
        <g transform="translate(14, 50)">
            <rect width="292" height="225" rx="6" fill="#FFFFFF" stroke="#6366F1" stroke-width="1.4" />
            <rect width="292" height="24" rx="6" fill="#E0E7FF" />
            <rect y="18" width="292" height="6" fill="#E0E7FF" />
            <text x="10" y="16" class="card-title" fill="#3730A3">APPEND-ONLY EVENT INTERCEPTOR</text>

            <g transform="translate(10, 32)">
                <text x="0" y="12" class="body-text">• Intercepts all mark revisions &amp; comments</text>
                <text x="0" y="26" class="body-text">• Zero UPDATE/DELETE permissions</text>
                <text x="0" y="40" class="body-text">• Guarantees non-repudiation for BAETE</text>

                <g transform="translate(0, 50)">
                    <rect width="272" height="132" rx="4" fill="#F5F3FF" stroke="#DDD6FE" stroke-width="1" />
                    <text x="8" y="16" font-family="'Segoe UI', Arial, sans-serif" font-size="10.5px" font-weight="700" fill="#4C1D95">Audit Security Context Vector:</text>
                    <text x="8" y="34" class="body-text"><tspan font-weight="700">Examiner: </tspan>Dr. Ferdaus Anam Jibon (408)</text>
                    <text x="8" y="50" class="body-text"><tspan font-weight="700">Client IP: </tspan>192.168.10.45 (Campus LAN)</text>
                    <text x="8" y="66" class="body-text"><tspan font-weight="700">Timestamp: </tspan>2026-09-06 14:22:18 UTC</text>
                    <text x="8" y="82" class="body-text"><tspan font-weight="700">Payload Hash: </tspan>SHA-256 (submission state)</text>
                    <text x="8" y="98" class="body-text"><tspan font-weight="700">BAETE Compliance: </tspan>Traceable lineages</text>
                    <text x="8" y="116" class="body-text" fill="#15803D"><tspan font-weight="700">State Lock: </tspan>is_finalized = True (Frozen)</text>
                </g>
            </g>
        </g>

        <!-- CARD 2B: DATABASE RELATIONAL MODELS -->
        <g transform="translate(14, 287)">
            <rect width="292" height="420" rx="6" fill="#FFFFFF" stroke="#818CF8" stroke-width="1.2" />
            <rect width="292" height="24" rx="6" fill="#EEF2FF" />
            <rect y="18" width="292" height="6" fill="#EEF2FF" />
            <text x="10" y="16" class="card-title" fill="#3730A3">DATABASE STORE: RELATIONAL MODELS</text>

            <g transform="translate(10, 32)">
                <!-- Model 1: TeacherReview -->
                <rect width="272" height="180" rx="4" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="0.8" />
                <rect width="272" height="20" rx="4" fill="#E2E8F0" />
                <text x="8" y="14" font-family="'Segoe UI', Arial, sans-serif" font-size="9.5px" font-weight="700" fill="#1E293B">MODEL: core.models.TeacherReview</text>
                
                <g transform="translate(8, 26)">
                    <text x="0" y="12" class="code-text"><tspan font-weight="700">id: </tspan>5082 (PK)  |  <tspan font-weight="700">submission_id: </tspan>1042</text>
                    <text x="0" y="26" class="code-text"><tspan font-weight="700">student_roll: </tspan>"22303142" (Hijbullah)</text>
                    <text x="0" y="40" class="code-text"><tspan font-weight="700">question_id: </tspan>1 (Q1)  |  <tspan font-weight="700" fill="#15803D">status: APPROVED</tspan></text>
                    <text x="0" y="54" class="code-text"><tspan font-weight="700" fill="#DC2626">original_ai_score: </tspan>16.50</text>
                    <text x="0" y="68" class="code-text"><tspan font-weight="700" fill="#16A34A">reviewed_score: </tspan>19.00 (+2.50 delta)</text>
                    <text x="0" y="82" class="code-text"><tspan font-weight="700">remarks: </tspan>"Step 3 integer mapping restored"</text>
                    <text x="0" y="96" class="code-text"><tspan font-weight="700">examiner_id: </tspan>408 (Dr. Ferdaus Anam Jibon)</text>
                    <text x="0" y="110" class="code-text"><tspan font-weight="700">created_at: </tspan>2026-09-06 14:22:18 UTC</text>
                    <text x="0" y="124" class="code-text" fill="#4338CA"><tspan font-weight="700">sha256: </tspan>7f9b2c8a1e4d0f6b3a27c...</text>
                    <text x="0" y="138" class="code-text" fill="#047857">✔ Permanent forensic evaluation audit record</text>
                </g>

                <!-- Model 2: EvaluationAuditLog -->
                <g transform="translate(0, 190)">
                    <rect width="272" height="186" rx="4" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="0.8" />
                    <rect width="272" height="20" rx="4" fill="#E2E8F0" />
                    <text x="8" y="14" font-family="'Segoe UI', Arial, sans-serif" font-size="9.5px" font-weight="700" fill="#1E293B">MODEL: core.models.EvaluationAuditLog</text>
                    
                    <g transform="translate(8, 26)">
                        <text x="0" y="12" class="code-text"><tspan font-weight="700">audit_id: </tspan>9144 (PK)  |  <tspan font-weight="700">action: FINALIZED</tspan></text>
                        <text x="0" y="26" class="code-text"><tspan font-weight="700">user_id: </tspan>408  |  <tspan font-weight="700">ip: </tspan>192.168.10.45</text>
                        <text x="0" y="40" class="code-text"><tspan font-weight="700">total_max_marks: </tspan>100.0</text>
                        <text x="0" y="54" class="code-text"><tspan font-weight="700" fill="#15803D">obtained_score: </tspan>83.50 (83.5%)</text>
                        <text x="0" y="68" class="code-text"><tspan font-weight="700">grade: </tspan>"A"  |  <tspan font-weight="700">is_finalized: </tspan>True</text>
                        <text x="0" y="82" class="code-text"><tspan font-weight="700">archived_pdf: </tspan>"evaluated_final_sub_1042.pdf"</text>
                        <text x="0" y="96" class="code-text"><tspan font-weight="700">timestamp: </tspan>2026-09-06 14:22:19 UTC</text>
                        <text x="0" y="110" class="code-text" fill="#7C3AED"><tspan font-weight="700">lock_token: </tspan>"LOCKED_BAETE_ACC_408_1042"</text>
                        <text x="0" y="126" class="code-text" fill="#166534">✔ Written with 0444 read-only permissions</text>
                    </g>
                </g>
            </g>
        </g>

        <!-- CARD 2C: ACCREDITATION AUDIT ASSURANCE -->
        <g transform="translate(14, 720)">
            <rect width="292" height="200" rx="6" fill="#FFFFFF" stroke="#A5B4FC" stroke-width="1.2" />
            <rect width="292" height="24" rx="6" fill="#EEF2FF" />
            <rect y="18" width="292" height="6" fill="#EEF2FF" />
            <text x="10" y="16" class="card-title" fill="#312E81">ACCREDITATION AUDIT ASSURANCE</text>

            <g transform="translate(10, 32)">
                <text x="0" y="12" class="body-text">• <tspan font-weight="700">BAETE Review Ready:</tspan> Complete paper trail</text>
                <text x="0" y="26" class="body-text">• <tspan font-weight="700">Department Head:</tspan> Read-only audit access</text>
                <text x="0" y="40" class="body-text">• <tspan font-weight="700">External Examiner:</tspan> Transparent delta log</text>

                <g transform="translate(0, 52)">
                    <rect width="272" height="104" rx="4" fill="#F8FAFC" stroke="#E2E8F0" stroke-width="0.8" />
                    <text x="6" y="14" class="code-text" fill="#475569"># Audit Query Verification</text>
                    <text x="6" y="28" class="code-text" fill="#2563EB">audits = EvaluationAuditLog.objects.filter(</text>
                    <text x="6" y="42" class="code-text" fill="#2563EB">    submission_id=1042</text>
                    <text x="6" y="56" class="code-text" fill="#2563EB">).select_related('teacher_user')</text>
                    <text x="6" y="70" class="code-text" fill="#15803D">assert submission.is_finalized == True</text>
                    <text x="6" y="84" class="code-text" fill="#166534"># State permanently locked against edits</text>
                </g>
            </g>
        </g>
    </g>

    <!-- HORIZONTAL FLOW CHEVRON 2 -> 3 -->
    <g transform="translate(695, 520)">
        <circle cx="0" cy="0" r="12" fill="#EFF6FF" stroke="#3B82F6" stroke-width="1.5" />
        <text x="0" y="4.5" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif" font-size="13px" font-weight="900" fill="#2563EB">→</text>
    </g>

    <!-- ============================================================== -->
    <!-- STAGE 3: DRAFT STORAGE PURGE & OBE TABULATION SYNC             -->
    <!-- Coordinates: x: 710, y: 72, w: 320, h: 940                       -->
    <!-- ============================================================== -->
    <g transform="translate(710, 72)" filter="url(#shadow)">
        <rect width="320" height="940" rx="8" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1.3" />
        
        <!-- Header Bar -->
        <rect width="320" height="38" rx="8" fill="#B91C1C" />
        <rect y="30" width="320" height="8" fill="#B91C1C" />
        <text x="12" y="24" class="stage-header-title">3. Storage Purge &amp; Sync</text>
        <text x="308" y="24" text-anchor="end" class="stage-header-sub">FinalizationService</text>

        <!-- CARD 3A: AUTOMATED DRAFT ARTIFACT PURGE -->
        <g transform="translate(14, 50)">
            <rect width="292" height="340" rx="6" fill="#FFFFFF" stroke="#EF4444" stroke-width="1.4" />
            <rect width="292" height="24" rx="6" fill="#FEE2E2" />
            <rect y="18" width="292" height="6" fill="#FEE2E2" />
            <text x="10" y="16" class="card-title" fill="#991B1B">AUTOMATED DRAFT ARTIFACT PURGE</text>

            <g transform="translate(10, 32)">
                <text x="0" y="12" class="body-text"><tspan font-weight="700">Method: </tspan><tspan font-weight="800">_purge_temporary_artifacts(1042)</tspan></text>
                <text x="0" y="26" class="body-text">• Executed immediately after PDF compilation</text>
                <text x="0" y="40" class="body-text">• Prevents server disk saturation during exams</text>

                <!-- Deleted Artifacts Box -->
                <g transform="translate(0, 48)">
                    <rect width="272" height="124" rx="4" fill="#FEF2F2" stroke="#FECACA" stroke-width="1" />
                    <text x="8" y="16" font-family="'Segoe UI', Arial, sans-serif" font-size="10px" font-weight="700" fill="#991B1B">Deleted Working Artifacts (Script #1042):</text>
                    
                    <g transform="translate(8, 26)">
                        <rect x="0" y="0" width="12" height="12" rx="2" fill="#EF4444" />
                        <text x="6" y="9.5" text-anchor="middle" font-size="9px" font-weight="900" fill="#FFFFFF">✕</text>
                        <text x="18" y="9" class="code-text" fill="#7F1D1D">media/submission_working/sub_1042_p*.jpg</text>
                        <text x="18" y="21" font-size="8.5px" fill="#991B1B">Deleted 14 obsolete high-res 300 DPI raster slices</text>

                        <rect x="0" y="28" width="12" height="12" rx="2" fill="#EF4444" />
                        <text x="6" y="37.5" text-anchor="middle" font-size="9px" font-weight="900" fill="#FFFFFF">✕</text>
                        <text x="18" y="37" class="code-text" fill="#7F1D1D">media/submission_preview/submission_1042_*</text>
                        <text x="18" y="49" font-size="8.5px" fill="#991B1B">Deleted uncertified preview PDF composites</text>

                        <rect x="0" y="56" width="12" height="12" rx="2" fill="#EF4444" />
                        <text x="6" y="65.5" text-anchor="middle" font-size="9px" font-weight="900" fill="#FFFFFF">✕</text>
                        <text x="18" y="65" class="code-text" fill="#7F1D1D">media/request_trace/eval_1042/</text>
                        <text x="18" y="77" font-size="8.5px" fill="#991B1B">Purged OCR bounding box traces &amp; JSON cache</text>
                    </g>
                </g>

                <!-- Storage Reclamation Statistics -->
                <g transform="translate(0, 180)">
                    <rect width="272" height="114" rx="4" fill="#F0FDF4" stroke="#BBF7D0" stroke-width="1" />
                    <text x="8" y="16" font-family="'Segoe UI', Arial, sans-serif" font-size="10.5px" font-weight="800" fill="#166534">Storage Recovery Statistics:</text>
                    <text x="8" y="34" class="body-text">• Pre-Purge Working Disk: <tspan font-weight="800" fill="#DC2626">~44.8 MB</tspan> (14 pages)</text>
                    <text x="8" y="50" class="body-text">• Post-Purge Certified PDF: <tspan font-weight="800" fill="#15803D">~2.8 MB</tspan></text>
                    <text x="8" y="68" class="body-text" fill="#166534"><tspan font-weight="800">✔ 93.8% Storage Reclamation (42.0 MB saved)</tspan></text>
                    <text x="8" y="86" class="body-text" fill="#15803D"><tspan font-weight="800">• 5,000 Scripts / Sem: </tspan><tspan font-weight="800" fill="#047857">&gt; 210 GB Disk Saved</tspan></text>
                    <text x="8" y="102" font-size="8.5px" fill="#4B5563">Automatic sweeper cleans unfinalized drafts &gt;24h</text>
                </g>
            </g>
        </g>

        <!-- CARD 3B: LIVE 8-SHEET OBE TABULATION SYNC -->
        <g transform="translate(14, 402)">
            <rect width="292" height="280" rx="6" fill="#FFFFFF" stroke="#059669" stroke-width="1.3" />
            <rect width="292" height="24" rx="6" fill="#D1FAE5" />
            <rect y="18" width="292" height="6" fill="#D1FAE5" />
            <text x="10" y="16" class="card-title" fill="#065F46">LIVE 8-SHEET OBE TABULATION SYNC</text>

            <g transform="translate(10, 32)">
                <text x="0" y="12" class="body-text"><tspan font-weight="700">Service: </tspan><tspan font-weight="800">sync_submission_to_tabulation()</tspan></text>
                <text x="0" y="26" class="body-text">• Propagates verified marks to official register</text>

                <g transform="translate(0, 36)">
                    <rect width="272" height="116" rx="4" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="0.8" />
                    <text x="8" y="16" font-family="'Segoe UI', Arial, sans-serif" font-size="10px" font-weight="700" fill="#1E293B">Synchronized Tabulation Metrics:</text>
                    <text x="8" y="32" class="body-text"><tspan font-weight="700">Course: </tspan>CSE 4383 (Computer Vision)</text>
                    <text x="8" y="48" class="body-text"><tspan font-weight="700">Student: </tspan>Hijbullah (ID: 22303142, Sec: E)</text>
                    <text x="8" y="64" class="body-text"><tspan font-weight="700">Midterm Score: </tspan><tspan font-weight="800" fill="#15803D">20.88 / 25.00</tspan> (83.5%)</text>
                    <text x="8" y="80" class="body-text"><tspan font-weight="700">OBE Mapping: </tspan>CO1: 85%, CO2: 82%, PO1: 84%</text>
                    <text x="8" y="98" class="body-text" fill="#047857"><tspan font-weight="700">Excel Sync: </tspan>8-Sheet Official Workbook updated</text>
                </g>

                <g transform="translate(0, 160)">
                    <rect width="272" height="74" rx="4" fill="#F0FDF4" stroke="#86EFAC" stroke-width="0.8" />
                    <text x="6" y="16" class="code-text" fill="#166534">StudentGradeRecord.objects.update_or_create(</text>
                    <text x="6" y="30" class="code-text" fill="#166534">    student=student, course=course,</text>
                    <text x="6" y="44" class="code-text" fill="#166534">    defaults={'mid_score': 20.88, 'status': 'FINAL'}</text>
                    <text x="6" y="58" class="code-text" fill="#15803D">)</text>
                </g>
            </g>
        </g>

        <!-- CARD 3C: STUDENT PORTAL & EMAIL DISPATCH -->
        <g transform="translate(14, 694)">
            <rect width="292" height="226" rx="6" fill="#FFFFFF" stroke="#0284C7" stroke-width="1.2" />
            <rect width="292" height="24" rx="6" fill="#E0F2FE" />
            <rect y="18" width="292" height="6" fill="#E0F2FE" />
            <text x="10" y="16" class="card-title" fill="#0369A1">STUDENT PORTAL &amp; EMAIL DISPATCH</text>

            <g transform="translate(10, 32)">
                <text x="0" y="12" class="body-text"><tspan font-weight="700">• Email Service: </tspan>EmailService.send_evaluated()</text>
                <text x="0" y="26" class="body-text">• Asynchronous thread dispatches certified PDF</text>
                <text x="0" y="40" class="body-text">• Student portal instantly updates with score card</text>

                <g transform="translate(0, 52)">
                    <rect width="272" height="124" rx="4" fill="#F0F9FF" stroke="#BAE6FD" stroke-width="1" />
                    <text x="8" y="16" font-family="'Segoe UI', Arial, sans-serif" font-size="10px" font-weight="700" fill="#0369A1">Dissemination Lifecycle Summary:</text>
                    <text x="8" y="34" class="body-text">1. Email dispatched with encrypted attachment</text>
                    <text x="8" y="50" class="body-text">2. File: <tspan font-weight="700">evaluated_final_submission_1042.pdf</tspan></text>
                    <text x="8" y="66" class="body-text">3. Student logs into portal to view itemized marks</text>
                    <text x="8" y="82" class="body-text">4. Dept Head dashboard receives pass-rate data</text>
                    <text x="8" y="102" class="body-text" fill="#047857"><tspan font-weight="800">✔ Evaluation Lifecycle Completed &amp; Sealed</tspan></text>
                </g>
            </g>
        </g>
    </g>

    <!-- HORIZONTAL FLOW CHEVRON 3 -> 4 -->
    <g transform="translate(1040, 520)">
        <circle cx="0" cy="0" r="12" fill="#EFF6FF" stroke="#3B82F6" stroke-width="1.5" />
        <text x="0" y="4.5" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif" font-size="13px" font-weight="900" fill="#2563EB">→</text>
    </g>

    <!-- ============================================================== -->
    <!-- STAGE 4: SAMPLE CERTIFIED WATERMARKED PDF SCRIPT               -->
    <!-- Coordinates: x: 1055, y: 72, w: 715, h: 940                      -->
    <!-- ============================================================== -->
    <g transform="translate(1055, 72)" filter="url(#shadow)">
        <rect width="715" height="940" rx="8" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1.3" />
        
        <!-- Header Bar -->
        <rect width="715" height="38" rx="8" fill="#047857" />
        <rect y="30" width="715" height="8" fill="#047857" />
        <text x="14" y="24" class="stage-header-title">4. Sample Certified PDF Script</text>
        <text x="700" y="24" text-anchor="end" class="stage-header-sub">Evaluated_Script_Hijbullah_Roll_22303142.pdf</text>

        <!-- SUB-HEADER SECURITY METRICS BAR -->
        <g transform="translate(16, 46)">
            <rect width="683" height="34" rx="4" fill="#ECFDF5" stroke="#A7F3D0" stroke-width="1" />
            <g transform="translate(10, 21)">
                <text x="0" y="0" font-family="'Segoe UI', Arial, sans-serif" font-size="10.5px" font-weight="700" fill="#065F46">Official Security Stamps:</text>
                <text x="140" y="0" font-family="'Segoe UI', Arial, sans-serif" font-size="10px" font-weight="600" fill="#047857">🛡️ IUBAT Anti-Tamper Watermark</text>
                <text x="330" y="0" font-family="'Segoe UI', Arial, sans-serif" font-size="10px" font-weight="600" fill="#047857">📊 Question Marks Summary Box</text>
                <text x="510" y="0" font-family="'Segoe UI', Arial, sans-serif" font-size="10px" font-weight="600" fill="#047857">✍️ Examiner Digital Signature</text>
            </g>
        </g>

        <!-- DUAL DOCUMENT SCRIPT PAGE PLACEHOLDERS (Will be composited by Pillow) -->
        <!-- Left Page Container: Page 1 (x: 20, y: 90, w: 326, h: 462) -->
        <g transform="translate(20, 90)">
            <rect width="326" height="462" rx="4" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1" />
            <!-- Caption below Page 1 -->
            <g transform="translate(0, 468)">
                <rect width="326" height="24" rx="3" fill="#F1F5F9" stroke="#E2E8F0" stroke-width="1" />
                <text x="163" y="16" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif" font-size="10px" font-weight="700" fill="#334155">Page 1: Script Cover, IUBAT Crest &amp; Feedback Overlay</text>
            </g>
        </g>

        <!-- Right Page Container: Page 14 (x: 368, y: 90, w: 326, h: 462) -->
        <g transform="translate(368, 90)">
            <rect width="326" height="462" rx="4" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1" />
            <!-- Caption below Page 14 -->
            <g transform="translate(0, 468)">
                <rect width="326" height="24" rx="3" fill="#F1F5F9" stroke="#E2E8F0" stroke-width="1" />
                <text x="163" y="16" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif" font-size="10px" font-weight="700" fill="#334155">Page 14: Scorecard, Rubric Matrix &amp; Teacher Signature</text>
            </g>
        </g>

        <!-- CARD 4B: CERTIFIED DOCUMENT ELEMENTS INSPECTION BOX -->
        <g transform="translate(16, 592)">
            <rect width="683" height="332" rx="6" fill="#FFFFFF" stroke="#10B981" stroke-width="1.3" />
            <rect width="683" height="24" rx="6" fill="#D1FAE5" />
            <rect y="18" width="683" height="6" fill="#D1FAE5" />
            <text x="12" y="16" class="card-title" fill="#065F46">CERTIFIED PDF STAMP &amp; AUDIT VERIFICATION METRICS</text>

            <g transform="translate(14, 34)">
                <!-- Feature 1: IUBAT Anti-Tamper Watermark -->
                <g transform="translate(0, 0)">
                    <rect width="324" height="66" rx="4" fill="#F0FDF4" stroke="#BBF7D0" stroke-width="0.8" />
                    <text x="8" y="15" font-family="'Segoe UI', Arial, sans-serif" font-size="10.5px" font-weight="800" fill="#15803D">❶ Official IUBAT Anti-Tamper Watermark</text>
                    <text x="8" y="30" font-family="'Segoe UI', Arial, sans-serif" font-size="9.5px" fill="#1E293B">• Multi-layer 45° watermark across all 14 pages</text>
                    <text x="8" y="44" font-family="'Segoe UI', Arial, sans-serif" font-size="9.5px" fill="#1E293B">• Translucent institutional seal prevents illicit modification</text>
                    <text x="8" y="58" font-family="'Segoe UI', Arial, sans-serif" font-size="9px" font-weight="700" fill="#047857">Protection: Vector background layer rendered by ReportLab</text>
                </g>

                <!-- Feature 2: Question Marks Summary Box -->
                <g transform="translate(338, 0)">
                    <rect width="320" height="66" rx="4" fill="#F0FDF4" stroke="#BBF7D0" stroke-width="0.8" />
                    <text x="8" y="15" font-family="'Segoe UI', Arial, sans-serif" font-size="10.5px" font-weight="800" fill="#15803D">❷ Question Marks Summary Table</text>
                    <text x="8" y="30" font-family="'Segoe UI', Arial, sans-serif" font-size="9.5px" fill="#1E293B">• Q1: 19.0/25 | Q2: 22.0/25 | Q3: 23.0/25 | Q4: 19.5/25</text>
                    <text x="8" y="44" font-family="'Segoe UI', Arial, sans-serif" font-size="9.5px" font-weight="700" fill="#166534">• Total Script Score: 83.50 / 100.00 (83.5%)</text>
                    <text x="8" y="58" font-family="'Segoe UI', Arial, sans-serif" font-size="9px" font-weight="700" fill="#047857">Status: FINALIZED | Confidence: 0.85 – 0.92</text>
                </g>

                <!-- Feature 3: Examiner Digital Signature Line -->
                <g transform="translate(0, 74)">
                    <rect width="324" height="66" rx="4" fill="#F0FDF4" stroke="#BBF7D0" stroke-width="0.8" />
                    <text x="8" y="15" font-family="'Segoe UI', Arial, sans-serif" font-size="10.5px" font-weight="800" fill="#15803D">❸ Examiner Digital Signature Block</text>
                    <text x="8" y="30" font-family="'Segoe UI', Arial, sans-serif" font-size="9.5px" fill="#1E293B">• Examiner: Dr. Ferdaus Anam Jibon (Faculty ID: 408)</text>
                    <text x="8" y="44" font-family="'Segoe UI', Arial, sans-serif" font-size="9.5px" fill="#1E293B">• Department of Computer Science &amp; Engineering, IUBAT</text>
                    <text x="8" y="58" font-family="'Segoe UI', Arial, sans-serif" font-size="9px" font-weight="700" fill="#047857">Digital Stamp: Cryptographically bound to SHA-256 state</text>
                </g>

                <!-- Feature 4: Automated Storage Purging -->
                <g transform="translate(338, 74)">
                    <rect width="320" height="66" rx="4" fill="#FEF2F2" stroke="#FECACA" stroke-width="0.8" />
                    <text x="8" y="15" font-family="'Segoe UI', Arial, sans-serif" font-size="10.5px" font-weight="800" fill="#B91C1C">❹ Automated Draft Storage Purging</text>
                    <text x="8" y="30" font-family="'Segoe UI', Arial, sans-serif" font-size="9.5px" fill="#1E293B">• FinalizationService._purge_temporary_artifacts()</text>
                    <text x="8" y="44" font-family="'Segoe UI', Arial, sans-serif" font-size="9.5px" fill="#1E293B">• 14 page working slices &amp; OCR bounding boxes purged</text>
                    <text x="8" y="58" font-family="'Segoe UI', Arial, sans-serif" font-size="9px" font-weight="700" fill="#B91C1C">Storage Reclaimed: 42.0 MB (93.8% server space saved)</text>
                </g>

                <!-- Bottom Official Certification Seal Bar -->
                <g transform="translate(0, 148)">
                    <rect width="658" height="136" rx="5" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1" />
                    <rect width="658" height="22" rx="5" fill="#F1F5F9" />
                    <text x="10" y="15" font-family="'Segoe UI', Arial, sans-serif" font-size="10px" font-weight="800" fill="#1E293B">LEGAL &amp; ACCREDITATION COMPLIANCE STAMP (IUBAT EXAM CONTROLLER OFFICE)</text>

                    <g transform="translate(10, 30)">
                        <!-- Seal Box -->
                        <rect x="0" y="0" width="130" height="92" rx="4" fill="#FFFFFF" stroke="#047857" stroke-width="1.2" stroke-dasharray="3,2" />
                        <text x="65" y="20" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif" font-size="9px" font-weight="800" fill="#065F46">IUBAT ACCREDITATION</text>
                        <circle cx="65" cy="46" r="16" fill="#ECFDF5" stroke="#10B981" stroke-width="1" />
                        <text x="65" y="50" text-anchor="middle" font-size="14px">✔</text>
                        <text x="65" y="74" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif" font-size="8.5px" font-weight="800" fill="#047857">CERTIFIED OFFICIAL</text>
                        <text x="65" y="85" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif" font-size="7.5px" fill="#475569">BAETE ACCREDITED</text>

                        <!-- Text Details -->
                        <g transform="translate(142, 4)">
                            <text x="0" y="12" font-family="'Segoe UI', Arial, sans-serif" font-size="10px" font-weight="700" fill="#0F172A">Archived File: <tspan font-family="'Consolas', monospace" font-size="9.5px" fill="#2563EB">media/submission_final/evaluated_final_submission_1042.pdf</tspan></text>
                            <text x="0" y="28" font-family="'Segoe UI', Arial, sans-serif" font-size="10px" fill="#334155"><tspan font-weight="700">Digital Fingerprint: </tspan><tspan font-family="'Consolas', monospace" font-size="9px" fill="#4338CA">SHA-256: 7f9b2c8a1e4d0f6b3a27c18... (Immutable)</tspan></text>
                            <text x="0" y="44" font-family="'Segoe UI', Arial, sans-serif" font-size="10px" fill="#334155"><tspan font-weight="700">QR Verification Endpoint: </tspan><tspan font-family="'Consolas', monospace" font-size="9px" fill="#0D9488">https://intelligrade.iubat.edu/verify/submission/22303142/</tspan></text>
                            <text x="0" y="60" font-family="'Segoe UI', Arial, sans-serif" font-size="9.5px" fill="#475569">Permissions: 0444 Read-Only | Institutional Archival Retention: 10 Years</text>
                            <text x="0" y="78" font-family="'Segoe UI', Arial, sans-serif" font-size="10px" font-weight="800" fill="#15803D">✔ Verified and Signed by Examiner Dr. Ferdaus Anam Jibon &amp; Academic Controller</text>
                        </g>
                    </g>
                </g>
            </g>
        </g>
    </g>

    <!-- Bottom Footer Meta Banner -->
    <g transform="translate(30, 1022)">
        <text x="0" y="14" font-family="'Segoe UI', Arial, sans-serif" font-size="10.5px" font-weight="600" fill="#64748B">IntelliGrade Finalization Core — Figure 3.11: Teacher Override, Immutable Audit Trail &amp; Certified PDF Generation</text>
        <text x="1740" y="14" text-anchor="end" font-family="'Segoe UI', Arial, sans-serif" font-size="10.5px" font-weight="600" fill="#64748B">Dimensions: 6.0" × 3.5" (300 DPI, 1800 × 1050 px) | Pure Light Mode | Publication-Ready</text>
    </g>
</svg>
"""

    # 2. Render SVG background using PyMuPDF (1:1 1800x1050 scale)
    doc_svg = fitz.open(stream=svg_content.encode('utf-8'), filetype='svg')
    pix_svg = doc_svg[0].get_pixmap()
    base_img = Image.frombytes('RGB', [pix_svg.width, pix_svg.height], pix_svg.samples)
    doc_svg.close()

    # 3. Load PDF Pages from the user's PDF
    pdf_doc = fitz.open(PDF_PATH)
    
    # Render Page 1 (Script Cover + Banner) at high quality
    p1_pix = pdf_doc[0].get_pixmap(dpi=220)
    p1_img = Image.frombytes('RGB', [p1_pix.width, p1_pix.height], p1_pix.samples)

    # Render Page 14 (Summary Scorecard Table) at high quality
    p14_pix = pdf_doc[13].get_pixmap(dpi=220)
    p14_img = Image.frombytes('RGB', [p14_pix.width, p14_pix.height], p14_pix.samples)
    pdf_doc.close()

    # Dimensions for embedded page thumbnails:
    target_w, target_h = 324, 460
    p1_thumb = p1_img.resize((target_w, target_h), Image.Resampling.LANCZOS)
    p14_thumb = p14_img.resize((target_w, target_h), Image.Resampling.LANCZOS)

    # Add anti-tamper watermark and signature stamp to Page 14 thumbnail
    p14_thumb = p14_thumb.convert('RGBA')
    watermark_layer = Image.new('RGBA', (target_w, target_h), (255, 255, 255, 0))
    w_draw = ImageDraw.Draw(watermark_layer)
    
    # Try default or standard fonts
    try:
        font_wm = ImageFont.truetype("arialbd.ttf", 20)
        font_wm_sub = ImageFont.truetype("arial.ttf", 12)
        font_sig = ImageFont.truetype("segoesc.ttf", 15) # Cursive font if available
        font_seal = ImageFont.truetype("arialbd.ttf", 9)
    except:
        font_wm = ImageFont.load_default()
        font_wm_sub = ImageFont.load_default()
        font_sig = ImageFont.load_default()
        font_seal = ImageFont.load_default()

    # 1. Diagonal Watermark on Page 14
    # Create a rotated watermark badge
    wm_img = Image.new('RGBA', (320, 80), (255, 255, 255, 0))
    wm_draw = ImageDraw.Draw(wm_img)
    wm_draw.rectangle([10, 10, 310, 70], outline=(16, 185, 129, 90), width=2)
    wm_draw.text((25, 20), "IUBAT OFFICIAL WATERMARK", fill=(16, 185, 129, 90), font=font_wm)
    wm_draw.text((65, 46), "ANTI-TAMPER CERTIFIED SCRIPT", fill=(16, 185, 129, 85), font=font_wm_sub)
    wm_rotated = wm_img.rotate(32, expand=True, resample=Image.Resampling.BICUBIC)
    
    # Paste rotated watermark onto Page 14
    watermark_layer.paste(wm_rotated, (0, 120), wm_rotated)

    # 2. Examiner Digital Signature on Teacher Signature line (bottom right)
    w_draw.text((160, 417), "Dr. Ferdaus A. Jibon", fill=(30, 64, 175, 230), font=font_sig)
    # Digital Stamp Box
    w_draw.rectangle([185, 388, 305, 412], outline=(4, 120, 87, 200), fill=(236, 253, 245, 180), width=1)
    w_draw.text((192, 391), "DIGITALLY VERIFIED", fill=(4, 120, 87, 240), font=font_seal)
    w_draw.text((192, 401), "FACULTY ID: #408", fill=(6, 95, 70, 240), font=font_seal)

    # QR Code placeholder on bottom left of Page 14
    w_draw.rectangle([15, 380, 55, 420], outline=(15, 23, 42, 220), fill=(255, 255, 255, 240), width=1)
    # Draw simple QR pixel pattern
    for qx in range(18, 52, 6):
        for qy in range(383, 417, 6):
            if (qx + qy) % 12 == 0 or (qx < 30 and qy < 395):
                w_draw.rectangle([qx, qy, qx+4, qy+4], fill=(15, 23, 42, 220))

    # Composite watermark layer onto Page 14
    p14_thumb = Image.alpha_composite(p14_thumb, watermark_layer).convert('RGB')

    # Watermark layer on Page 1 as well
    p1_thumb = p1_thumb.convert('RGBA')
    p1_wm_layer = Image.new('RGBA', (target_w, target_h), (255, 255, 255, 0))
    p1_wm_draw = ImageDraw.Draw(p1_wm_layer)
    wm_img1 = Image.new('RGBA', (320, 70), (255, 255, 255, 0))
    wm_draw1 = ImageDraw.Draw(wm_img1)
    wm_draw1.rectangle([10, 10, 310, 60], outline=(4, 120, 87, 75), width=2)
    wm_draw1.text((30, 20), "IUBAT CERTIFIED SCRIPT", fill=(4, 120, 87, 85), font=font_wm)
    wm_rot1 = wm_img1.rotate(35, expand=True, resample=Image.Resampling.BICUBIC)
    p1_wm_layer.paste(wm_rot1, (0, 150), wm_rot1)
    p1_thumb = Image.alpha_composite(p1_thumb, p1_wm_layer).convert('RGB')

    # Paste Page 1 and Page 14 into the base image at exact coordinates:
    # Column 4 start x = 1055, y = 72
    # Page 1 coords: x = 1055 + 21 = 1076, y = 72 + 91 = 163
    # Page 14 coords: x = 1055 + 369 = 1424, y = 72 + 91 = 163
    base_img.paste(p1_thumb, (1076, 163))
    base_img.paste(p14_thumb, (1424, 163))

    # Draw crisp outer borders around pasted thumbnails
    draw = ImageDraw.Draw(base_img)
    draw.rectangle([1075, 162, 1075 + target_w + 1, 162 + target_h + 1], outline=(203, 213, 225), width=1)
    draw.rectangle([1423, 162, 1423 + target_w + 1, 162 + target_h + 1], outline=(203, 213, 225), width=1)

    # Save to Figure-3.11.png
    base_img.save(OUTPUT_PNG, format="PNG", dpi=(300, 300))
    print(f"Successfully generated Figure 3.11 at: {OUTPUT_PNG}")

if __name__ == "__main__":
    create_figure_3_11()
