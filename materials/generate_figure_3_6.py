"""
Generates Figure 3.6: Question Boundary Discovery State Machine & Spatial Mapping
Dimensions: Width: 6.0 in, Height: 3.8 in @ 300 DPI (1800 x 1140 px)
Strict Light Mode, crisp high-contrast academic publication styling:
- Left: Start-of-Line Regex State Machine (LineReconstructor -> Fast-Reject -> Regex States)
- Center: Multi-Page Script Spatial Slicing (Page 1 & 2 continuous bounding box chaining)
- Right: Teacher Visual Crop Confirmation Modal UI (Thumbnails, boundary sliders, one-click confirm)
Outputs ONLY a single image: materials/Figure-3.6.png
"""
import os
import fitz  # PyMuPDF
from PIL import Image

def generate_svg():
    width = 1800
    height = 1140

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
    <defs>
        <!-- Arrowhead Markers -->
        <marker id="arrSlate" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <polygon points="0,1 10,5 0,9" fill="#475569" />
        </marker>
        <marker id="arrBlue" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <polygon points="0,1 10,5 0,9" fill="#2563EB" />
        </marker>
        <marker id="arrGreen" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <polygon points="0,1 10,5 0,9" fill="#16A34A" />
        </marker>
        <marker id="arrAmber" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <polygon points="0,1 10,5 0,9" fill="#D97706" />
        </marker>
        <marker id="arrPurple" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <polygon points="0,1 10,5 0,9" fill="#7C3AED" />
        </marker>
        <marker id="arrRed" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <polygon points="0,1 10,5 0,9" fill="#DC2626" />
        </marker>

        <style>
            .main-title {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 20px; font-weight: 800; fill: #0F172A; }}
            .main-subtitle {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 12px; font-weight: 600; fill: #475569; }}
            
            .panel-header-title {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 13.5px; font-weight: 700; fill: #FFFFFF; }}
            .panel-header-sub {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 10px; font-weight: 500; fill: #E2E8F0; }}
            
            .state-title {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 11.5px; font-weight: 800; }}
            .state-desc {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 10px; font-weight: 500; fill: #475569; }}
            .state-code {{ font-family: 'Consolas', monospace; font-size: 8.5px; font-weight: 700; }}
            
            .badge-text {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 9px; font-weight: 700; }}
            .label-text {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 10px; font-weight: 600; fill: #1E293B; }}
            
            .doc-title {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 11px; font-weight: 700; fill: #0F172A; }}
            .doc-text {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 9.5px; font-weight: 500; fill: #334155; }}
            
            .footer-info {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 10px; font-weight: 500; fill: #64748B; }}
        </style>
    </defs>

    <!-- Canvas Background -->
    <rect width="{width}" height="{height}" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.5" />

    <!-- Top Diagram Header Block -->
    <g transform="translate(45, 18)">
        <rect x="0" y="0" width="5" height="42" rx="2" fill="#2563EB" />
        <text x="16" y="21" class="main-title">Figure 3.6: Question Boundary Discovery State Machine &amp; Spatial Mapping</text>
        <text x="16" y="39" class="main-subtitle">Deterministic Regex State Machine, Multi-Page Bounding Box Slicing, and Teacher Visual Confirmation (CSE 4385 Exam Evaluation)</text>
    </g>

    <!-- ============================================================== -->
    <!-- PANEL 1 (LEFT): REGEX STATE MACHINE TRANSITION DIAGRAM         -->
    <!-- Coordinates: x: 45, y: 75, w: 535, h: 1025                      -->
    <!-- ============================================================== -->
    <g transform="translate(45, 75)">
        <rect width="535" height="1025" rx="8" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1.3" />
        
        <!-- Header Bar -->
        <rect width="535" height="38" rx="8" fill="#1E293B" />
        <rect y="30" width="535" height="8" fill="#1E293B" />
        <text x="16" y="24" class="panel-header-title">1. Start-of-Line Regex State Machine</text>
        <text x="520" y="24" text-anchor="end" class="panel-header-sub">question_number_detector.py</text>

        <!-- STATE 0: SCANNING_SCRIPT -->
        <g transform="translate(120, 55)">
            <rect width="250" height="74" rx="6" fill="#FFFFFF" stroke="#3B82F6" stroke-width="1.5" />
            <rect width="250" height="24" rx="6" fill="#DBEAFE" />
            <rect y="18" width="250" height="6" fill="#DBEAFE" />
            <text x="12" y="16" class="state-title" fill="#1E40AF">STATE 0: SCANNING_SCRIPT</text>
            <text x="12" y="42" class="state-desc">• Ingests reconstructed visual lines from OCR</text>
            <text x="12" y="56" class="state-desc">• Tracks baseline height &amp; proximity ymin</text>
            <text x="12" y="68" class="state-code" fill="#2563EB">LineReconstructor.reconstruct_lines()</text>
        </g>

        <!-- DOWN ARROW 0 -> FAST REJECT -->
        <path d="M 245 129 L 245 165" fill="none" stroke="#64748B" stroke-width="2" marker-end="url(#arrSlate)" />

        <!-- FAST-REJECTION FILTER -->
        <g transform="translate(30, 170)">
            <rect width="415" height="98" rx="6" fill="#FFF7ED" stroke="#FDBA74" stroke-width="1.3" />
            <rect width="415" height="22" rx="6" fill="#FFEDD5" />
            <rect y="16" width="415" height="6" fill="#FFEDD5" />
            <text x="12" y="15" class="state-title" fill="#9A3412">FILTER: FAST-REJECTION &amp; NOISE SUPPRESSION</text>
            <g transform="translate(12, 35)">
                <text x="0" y="0" class="state-desc">• <tspan font-weight="700" fill="#DC2626">Suppresses Matrix &amp; Pixel Tuples:</tspan> 50 56 60, (120, 150, 180), 3x3 matrix</text>
                <text x="0" y="15" class="state-desc">• <tspan font-weight="700" fill="#DC2626">Suppresses Rubric Tags &amp; Marks:</tspan> [CO2, C3, PO1 — 25 marks], 15+10=25</text>
                <text x="0" y="30" class="state-desc">• <tspan font-weight="700" fill="#DC2626">Suppresses Subpoints &amp; Figures:</tspan> (i), (ii), (iii), Figure 1: Football Ground</text>
                <text x="0" y="45" class="state-desc">• <tspan font-weight="700" fill="#DC2626">Suppresses Metadata &amp; Headers:</tspan> CSE 4385, Ferdaus Anam Jibon, IUBAT</text>
            </g>
        </g>

        <!-- REJECTION RECYCLING LOOP (With explicit gap for pill) -->
        <path d="M 445 217 L 485 217 L 485 160" fill="none" stroke="#DC2626" stroke-width="1.5" stroke-dasharray="4 2" />
        <g transform="translate(440, 138)">
            <rect width="90" height="22" rx="4" fill="#FEE2E2" stroke="#FCA5A5" stroke-width="1" />
            <text x="45" y="15" text-anchor="middle" class="badge-text" fill="#B91C1C">REJECT NOISE</text>
        </g>
        <path d="M 485 138 L 485 92 L 372 92" fill="none" stroke="#DC2626" stroke-width="1.5" stroke-dasharray="4 2" marker-end="url(#arrRed)" />

        <!-- DOWN ARROW FAST REJECT -> STATE 1 -->
        <path d="M 237 268 L 237 298" fill="none" stroke="#16A34A" stroke-width="2" marker-end="url(#arrGreen)" />
        <g transform="translate(182, 273)">
            <rect width="110" height="20" rx="4" fill="#DCFCE7" stroke="#86EFAC" stroke-width="0.8" />
            <text x="55" y="14" text-anchor="middle" class="badge-text" fill="#15803D">PASS CANDIDATE</text>
        </g>

        <!-- STATE 1: HEADER_DISCOVERED -->
        <g transform="translate(30, 303)">
            <rect width="415" height="152" rx="6" fill="#F0FDF4" stroke="#86EFAC" stroke-width="1.5" />
            <rect width="415" height="24" rx="6" fill="#DCFCE7" />
            <rect y="18" width="415" height="6" fill="#DCFCE7" />
            <text x="12" y="16" class="state-title" fill="#15803D">STATE 1: HEADER_DISCOVERED (Anchor Regex Match)</text>
            
            <g transform="translate(12, 36)">
                <text x="0" y="0" class="state-desc">• <tspan font-weight="700">Strict Start-of-Line Subcontinental Patterns:</tspan></text>
                
                <rect x="0" y="8" width="391" height="20" rx="3" fill="#FFFFFF" stroke="#BBF7D0" stroke-width="0.8" />
                <text x="8" y="22" class="state-code" fill="#166534">r'(?i)^\\s*Ans(wer)?\\s+to\\s+the\\s+Q(ues)?\\.\\s*No\\.?\\s*(\\d+[a-z]?)'</text>

                <rect x="0" y="32" width="391" height="20" rx="3" fill="#FFFFFF" stroke="#BBF7D0" stroke-width="0.8" />
                <text x="8" y="46" class="state-code" fill="#166534">r'(?i)^\\s*(Q(ues)?|Question)\\s*[\\:\\-\\s]*([0-9]{{1,2}}[a-z]?)\\b'</text>

                <text x="0" y="72" class="state-desc">• Extracts normalized identifier: <tspan font-family="Consolas" font-weight="700" fill="#15803D">norm_num = normalize_question_number(raw)</tspan></text>
                <text x="0" y="88" class="state-desc">• Matches exam questions: <tspan font-weight="700">Q1</tspan> (Hist Eq), <tspan font-weight="700">Q2</tspan> (HSI/CMY), <tspan font-weight="700">Q3</tspan> (Image Types), <tspan font-weight="700">Q4</tspan> (DIP Steps)</text>
                <text x="0" y="104" class="state-desc">• Best-score-wins deduplication resolves conflicting OCR variations</text>
            </g>
        </g>

        <!-- DOWN ARROW STATE 1 -> STATE 2 -->
        <path d="M 237 455 L 237 493" fill="none" stroke="#2563EB" stroke-width="2" marker-end="url(#arrBlue)" />

        <!-- STATE 2: ACTIVE_ANSWER_BODY -->
        <g transform="translate(30, 498)">
            <rect width="415" height="135" rx="6" fill="#EFF6FF" stroke="#93C5FD" stroke-width="1.5" />
            <rect width="415" height="24" rx="6" fill="#DBEAFE" />
            <rect y="18" width="415" height="6" fill="#DBEAFE" />
            <text x="12" y="16" class="state-title" fill="#1E40AF">STATE 2: ACTIVE_ANSWER_BODY (Spatial Segment Accumulator)</text>
            
            <g transform="translate(12, 38)">
                <text x="0" y="0" class="state-desc">• Sets active question pointer: <tspan font-family="Consolas" font-weight="700" fill="#1D4ED8">active_q = 'Q1'</tspan>, start coordinate <tspan font-family="Consolas" font-weight="700">ymin = 0.15</tspan></text>
                <text x="0" y="16" class="state-desc">• Consumes subsequent body lines: PDF/CDF tables, formulas, transformed matrices</text>
                <text x="0" y="32" class="state-desc">• Expands bounding box union: <tspan font-family="Consolas" font-weight="700">[ymin, min(xmin), max(ymax), max(xmax)]</tspan></text>
                <text x="0" y="48" class="state-desc">• Detects page boundary overflow when answer extends to Page 2</text>
                <rect x="0" y="58" width="391" height="26" rx="3" fill="#FFFFFF" stroke="#BFDBFE" stroke-width="0.8" />
                <text x="8" y="75" class="state-code" fill="#1E40AF">segment_slice = {{'page': curr_page, 'ymin': ymin, 'ymax': ymax_line}}</text>
            </g>
        </g>

        <!-- BRANCH 1: PAGE OVERFLOW (Clean gap, zero overlap) -->
        <path d="M 445 540 L 490 540 L 490 580" fill="none" stroke="#7C3AED" stroke-width="2" />
        <g transform="translate(456, 580)">
            <rect width="68" height="20" rx="4" fill="#F5F3FF" stroke="#DDD6FE" stroke-width="1" />
            <text x="34" y="14" text-anchor="middle" class="badge-text" font-size="8px" fill="#6D28D9">OVERFLOW</text>
        </g>
        <path d="M 490 600 L 490 700 L 448 700" fill="none" stroke="#7C3AED" stroke-width="2" marker-end="url(#arrPurple)" />

        <!-- DOWN ARROW STATE 2 -> STATE 3 -->
        <path d="M 237 633 L 237 673" fill="none" stroke="#2563EB" stroke-width="2" marker-end="url(#arrBlue)" />
        <g transform="translate(172, 643)">
            <rect width="130" height="20" rx="4" fill="#EFF6FF" stroke="#BFDBFE" stroke-width="0.8" />
            <text x="65" y="14" text-anchor="middle" class="badge-text" fill="#1D4ED8">NEW HEADER / EOF</text>
        </g>

        <!-- STATE 3: TERMINAL_SEGMENT_CLOSURE -->
        <g transform="translate(30, 678)">
            <rect width="415" height="142" rx="6" fill="#F5F3FF" stroke="#C4B5FD" stroke-width="1.5" />
            <rect width="415" height="24" rx="6" fill="#EDE9FE" />
            <rect y="18" width="415" height="6" fill="#EDE9FE" />
            <text x="12" y="16" class="state-title" fill="#6D28D9">STATE 3: TERMINAL_SEGMENT_CLOSURE &amp; PAYLOAD SLICING</text>
            
            <g transform="translate(12, 38)">
                <text x="0" y="0" class="state-desc">• Detected boundary cut: Q1 ends at <tspan font-family="Consolas" font-weight="700">ymax = Q2_header.ymin - 0.02 (y = 0.42)</tspan></text>
                <text x="0" y="16" class="state-desc">• Chains multi-page slices into unified entity: <tspan font-family="Consolas" font-weight="700">Q1.pages = [1, 2]</tspan></text>
                <text x="0" y="32" class="state-desc">• Generates high-res image crops via OpenCV &amp; downsamples to 1200px</text>
                <text x="0" y="48" class="state-desc">• Dispatches structured question mapping to interactive confirmation modal</text>
                <rect x="0" y="62" width="391" height="26" rx="3" fill="#FFFFFF" stroke="#DDD6FE" stroke-width="0.8" />
                <text x="8" y="79" class="state-code" fill="#6D28D9">QuestionMapping(question_id=1, page_numbers_json=[1, 2])</text>
            </g>
        </g>

        <!-- BOTTOM RECAP BOX IN LEFT PANEL -->
        <g transform="translate(20, 840)">
            <rect width="495" height="165" rx="6" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="1.2" />
            <rect width="495" height="24" rx="6" fill="#F1F5F9" />
            <rect y="18" width="495" height="6" fill="#F1F5F9" />
            <text x="12" y="16" font-family="'Segoe UI', Arial, sans-serif" font-size="11px" font-weight="700" fill="#334155">CLASSIFIER ARCHITECTURE SPECIFICATION</text>
            
            <g transform="translate(12, 38)">
                <text x="0" y="0" class="state-desc">• <tspan font-weight="700">Token Dictionaries:</tspan> ANSWER_TOKENS (ans, answer, soln, উত্তর, সমাধান)</text>
                <text x="0" y="16" class="state-desc">• <tspan font-weight="700">Candidate Scoring:</tspan> Subcontinental regex (+90), context boost (+5), top 25% (+4)</text>
                <text x="0" y="32" class="state-desc">• <tspan font-weight="700">Vision Fallback:</tspan> Top 35% crop sent to Vision Provider if OCR confidence &lt; 70%</text>
                <text x="0" y="48" class="state-desc">• <tspan font-weight="700">Ambiguity Guard:</tspan> Pages with no explicit heading NEVER default to Q1</text>
                <rect x="0" y="62" width="471" height="52" rx="4" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="0.8" />
                <text x="8" y="79" class="state-code" fill="#0F172A">def detect_explicit_question_heading(text, ymin_pct):</text>
                <text x="24" y="95" class="state-code" fill="#16A34A">return {{'is_heading': True, 'q_num': '1', 'conf': 0.99, 'course': 'CSE 4385'}}</text>
            </g>
        </g>
    </g>

    <!-- ============================================================== -->
    <!-- PANEL 2 (CENTER): SPATIAL PAGE SLICING & MULTI-PAGE SCRIPT     -->
    <!-- Coordinates: x: 600, y: 75, w: 565, h: 1025                     -->
    <!-- ============================================================== -->
    <g transform="translate(600, 75)">
        <rect width="565" height="1025" rx="8" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1.3" />
        
        <!-- Header Bar -->
        <rect width="565" height="38" rx="8" fill="#1E40AF" />
        <rect y="30" width="565" height="8" fill="#1E40AF" />
        <text x="16" y="24" class="panel-header-title">2. Spatial Page Slicing &amp; Multi-Page Linkage</text>
        <text x="550" y="24" text-anchor="end" class="panel-header-sub">Script Bounding Box Segmentation</text>

        <!-- SCRIPT PAGE 1 -->
        <g transform="translate(25, 55)">
            <!-- Page Sheet Background -->
            <rect width="515" height="425" rx="6" fill="#FFFFFF" stroke="#94A3B8" stroke-width="1.5" />
            <!-- Paper Header -->
            <rect width="515" height="28" rx="6" fill="#F1F5F9" />
            <rect y="22" width="515" height="6" fill="#F1F5F9" />
            <text x="14" y="18" class="doc-title" fill="#475569">STUDENT ANSWER SCRIPT — PAGE 1 OF 4</text>
            <text x="500" y="18" text-anchor="end" font-family="'Segoe UI', Arial, sans-serif" font-size="9.5px" font-weight="700" fill="#64748B">300 DPI Working Copy</text>

            <!-- Student Metadata Box (Non-Header, Filtered) -->
            <g transform="translate(14, 38)">
                <rect width="487" height="38" rx="4" fill="#F8FAFC" stroke="#E2E8F0" stroke-width="1" />
                <text x="10" y="16" font-family="'Segoe UI', Arial, sans-serif" font-size="9px" font-weight="600" fill="#64748B">Course: CSE 4385 (Computer Vision &amp; Image Processing) | Mid Term 2026</text>
                <text x="10" y="30" font-family="'Segoe UI', Arial, sans-serif" font-size="9px" font-weight="700" fill="#334155">Student Name: Tanvir Hasan   |   ID: 22103045   |   Section: E (IUBAT)</text>
                <rect x="350" y="8" width="128" height="20" rx="3" fill="#FEE2E2" stroke="#FCA5A5" stroke-width="0.8" />
                <text x="414" y="22" text-anchor="middle" class="badge-text" fill="#B91C1C">METADATA (FILTERED)</text>
            </g>

            <!-- DETECTED HEADER 1 OVERLAY (GREEN BOUNDING BOX) -->
            <g transform="translate(14, 88)">
                <rect width="487" height="36" rx="4" fill="#DCFCE7" stroke="#16A34A" stroke-width="2" stroke-dasharray="4 2" />
                <text x="12" y="22" font-family="'Courier New', monospace" font-size="14px" font-weight="800" fill="#14532D">Answer to the Question No. 1</text>
                <rect x="375" y="8" width="102" height="20" rx="3" fill="#16A34A" />
                <text x="426" y="22" text-anchor="middle" class="badge-text" fill="#FFFFFF">HEADER: Q1</text>
                <text x="12" y="32" font-family="Consolas" font-size="8px" font-weight="600" fill="#15803D">Spatial Box: [ymin: 0.15, xmin: 0.05, ymax: 0.21, xmax: 0.95] | Conf: 99%</text>
            </g>

            <!-- ANSWER 1 BODY (PAGE 1 SEGMENT) -->
            <g transform="translate(14, 132)">
                <rect width="487" height="255" rx="4" fill="#F0FDF4" stroke="#86EFAC" stroke-width="1.2" />
                
                <!-- Bounding Box Callout Tag -->
                <rect x="0" y="0" width="240" height="18" rx="2" fill="#16A34A" />
                <text x="8" y="13" class="badge-text" fill="#FFFFFF">Q1 SLICE PART 1 (PAGE 1 / y: 0.22 - 1.00)</text>

                <!-- Simulated Student Answer Script Lines for Q1 -->
                <g transform="translate(16, 28)">
                    <text x="0" y="14" class="doc-text" font-weight="700">Histogram Equalization Shifting on 8-bit Image (6×6 Matrix, N = 36):</text>
                    <text x="0" y="30" class="doc-text" font-style="italic">Let gray levels be r_k in [0, 255]. The probability density function is p_r(r_k) = n_k / 36.</text>
                    
                    <text x="0" y="52" class="doc-text" font-weight="700">Histogram Frequency Table &amp; Cumulative Distribution Function (CDF):</text>
                    <text x="0" y="68" class="doc-text" font-style="italic">• Total pixels N = 6 × 6 = 36. Gray scale range L = 256 (0 to 255).</text>
                    <text x="0" y="84" class="doc-text" font-style="italic">• Mapping function: s_k = T(r_k) = round[(L - 1) × CDF(r_k)] = round[255 × Σ p_r(r_j)]</text>
                    
                    <text x="0" y="108" class="doc-text" font-weight="700">3rd Row Pixels to Transform: [54, 78, 136, 96, 150, 76]</text>
                    <text x="0" y="124" class="doc-text" font-style="italic">• Frequency count for 3rd row gray levels across full 36-pixel matrix:</text>
                    <text x="0" y="140" class="doc-text" font-style="italic">  r = 54 (n=1, CDF=0.166), r = 76 (n=1, CDF=0.305), r = 78 (n=1, CDF=0.333)</text>
                    <text x="0" y="156" class="doc-text" font-style="italic">  r = 96 (n=2, CDF=0.472), r = 136 (n=1, CDF=0.750), r = 150 (n=1, CDF=0.888)</text>

                    <rect x="0" y="170" width="455" height="34" rx="3" fill="#DCFCE7" stroke="#86EFAC" stroke-width="0.8" />
                    <text x="8" y="190" font-family="Consolas" font-size="9px" font-weight="700" fill="#166534">Derivation Formula: s_k = round[255 × (Cumulative Frequency n_k / 36)]</text>
                </g>

                <text x="243" y="246" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif" font-size="9px" font-weight="700" fill="#15803D">▼ [Q1 Histogram Derivation Continues to Page 2 — Continuous Segment] ▼</text>
            </g>

            <!-- Page 1 Footer -->
            <text x="257" y="416" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif" font-size="9px" font-weight="600" fill="#94A3B8">Page 1 of 4 (IntelliGrade Normalized Matrix: 2480 × 3508 px @ 300 DPI)</text>
        </g>

        <!-- MULTI-PAGE CONTINUOUS LINKAGE RIBBON -->
        <g transform="translate(25, 488)">
            <rect width="515" height="34" rx="5" fill="#EDE9FE" stroke="#C4B5FD" stroke-width="1.2" />
            <path d="M 20 17 L 55 17" fill="none" stroke="#7C3AED" stroke-width="2" />
            <text x="257" y="22" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif" font-size="10.5px" font-weight="800" fill="#6D28D9">CONTINUOUS ANSWER LINK: Q1 Segment Chained Across Page 1 &amp; Page 2</text>
            <path d="M 460 17 L 495 17" fill="none" stroke="#7C3AED" stroke-width="2" marker-end="url(#arrPurple)" />
        </g>

        <!-- SCRIPT PAGE 2 -->
        <g transform="translate(25, 530)">
            <!-- Page Sheet Background -->
            <rect width="515" height="475" rx="6" fill="#FFFFFF" stroke="#94A3B8" stroke-width="1.5" />
            <!-- Paper Header -->
            <rect width="515" height="28" rx="6" fill="#F1F5F9" />
            <rect y="22" width="515" height="6" fill="#F1F5F9" />
            <text x="14" y="18" class="doc-title" fill="#475569">STUDENT ANSWER SCRIPT — PAGE 2 OF 4</text>
            <text x="500" y="18" text-anchor="end" font-family="'Segoe UI', Arial, sans-serif" font-size="9.5px" font-weight="700" fill="#64748B">300 DPI Working Copy</text>

            <!-- ANSWER 1 CONTINUED (PAGE 2 TOP SEGMENT) -->
            <g transform="translate(14, 36)">
                <rect width="487" height="150" rx="4" fill="#F0FDF4" stroke="#86EFAC" stroke-width="1.2" />
                <rect x="0" y="0" width="240" height="18" rx="2" fill="#16A34A" />
                <text x="8" y="13" class="badge-text" fill="#FFFFFF">Q1 SLICE PART 2 (PAGE 2 / y: 0.00 - 0.40)</text>

                <g transform="translate(16, 26)">
                    <text x="0" y="14" class="doc-text" font-weight="700">Resulting Transformed Pixel Values for 3rd Row [CO2, C3, PO1]:</text>
                    <text x="0" y="30" class="doc-text" font-style="italic">• s(54)  = round[255 × 6/36]  = round[42.5]  = 43 (transformed value)</text>
                    <text x="0" y="46" class="doc-text" font-style="italic">• s(76)  = round[255 × 11/36] = round[77.9]  = 78 (transformed value)</text>
                    <text x="0" y="62" class="doc-text" font-style="italic">• s(78)  = round[255 × 12/36] = round[85.0]  = 85 (transformed value)</text>
                    <text x="0" y="78" class="doc-text" font-style="italic">• s(96)  = round[255 × 17/36] = round[120.4] = 120 (transformed value)</text>
                    <text x="0" y="94" class="doc-text" font-style="italic">• s(136) = round[255 × 27/36] = round[191.2] = 191 | s(150) = round[255 × 32/36] = 227</text>
                    
                    <rect x="0" y="104" width="455" height="26" rx="3" fill="#DCFCE7" stroke="#86EFAC" stroke-width="0.8" />
                    <text x="8" y="121" font-family="Consolas" font-size="9px" font-weight="700" fill="#166534">Final 3rd Row Matrix: [43, 85, 191, 120, 227, 78] (Full 25 Marks Derivation)</text>
                </g>
            </g>

            <!-- BOUNDARY CUT LINE: SPATIAL SEPARATOR -->
            <g transform="translate(14, 194)">
                <line x1="0" y1="12" x2="487" y2="12" stroke="#DC2626" stroke-width="2" stroke-dasharray="6 3" />
                <!-- Scissor / Boundary Cut Pill -->
                <rect x="150" y="0" width="187" height="24" rx="4" fill="#FEE2E2" stroke="#DC2626" stroke-width="1.2" />
                <text x="243" y="16" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif" font-size="9.5px" font-weight="800" fill="#B91C1C">✂ BOUNDARY CUT: y = 0.42 (Q1 Ends)</text>
            </g>

            <!-- DETECTED HEADER 2 OVERLAY (BLUE BOUNDING BOX) -->
            <g transform="translate(14, 226)">
                <rect width="487" height="36" rx="4" fill="#EFF6FF" stroke="#2563EB" stroke-width="2" stroke-dasharray="4 2" />
                <text x="12" y="22" font-family="'Courier New', monospace" font-size="14px" font-weight="800" fill="#1E40AF">Ans to Question No. 2</text>
                <rect x="375" y="8" width="102" height="20" rx="3" fill="#2563EB" />
                <text x="426" y="22" text-anchor="middle" class="badge-text" fill="#FFFFFF">HEADER: Q2</text>
                <text x="12" y="32" font-family="Consolas" font-size="8px" font-weight="600" fill="#1D4ED8">Spatial Box: [ymin: 0.44, xmin: 0.05, ymax: 0.50, xmax: 0.95] | Conf: 97%</text>
            </g>

            <!-- ANSWER 2 BODY (PAGE 2 SEGMENT) -->
            <g transform="translate(14, 270)">
                <rect width="487" height="180" rx="4" fill="#F0F9FF" stroke="#7DD3FC" stroke-width="1.2" />
                <rect x="0" y="0" width="220" height="18" rx="2" fill="#0284C7" />
                <text x="8" y="13" class="badge-text" fill="#FFFFFF">Q2 SLICE (PAGE 2 / y: 0.51 - 0.95)</text>

                <g transform="translate(16, 26)">
                    <text x="0" y="14" class="doc-text" font-weight="700">RGB to HSI &amp; CMY Conversion for First Pixel: (R=120, G=150, B=180)</text>
                    <text x="0" y="32" class="doc-text" font-style="italic">• <tspan font-weight="700">Intensity (I):</tspan> I = (R + G + B) / 3 = (120 + 150 + 180) / 3 = 450 / 3 = 150 (Normalized: 0.588)</text>
                    <text x="0" y="50" class="doc-text" font-style="italic">• <tspan font-weight="700">Saturation (S):</tspan> S = 1 - [3 / (R + G + B)] × min(R, G, B) = 1 - (3 × 120) / 450 = 0.20</text>
                    <text x="0" y="68" class="doc-text" font-style="italic">• <tspan font-weight="700">Hue (H):</tspan> θ = 210° | Since B &gt; G: Hue Angle H = 360° - θ = 150° (Cyan-Blue)</text>
                    <text x="0" y="86" class="doc-text" font-style="italic">• <tspan font-weight="700">CMY Representation:</tspan> [C, M, Y]^T = [1 - R/255, 1 - G/255, 1 - B/255]^T</text>
                    
                    <rect x="0" y="102" width="455" height="34" rx="3" fill="#E0F2FE" stroke="#BAE6FD" stroke-width="0.8" />
                    <text x="8" y="122" font-family="Consolas" font-size="9px" font-weight="700" fill="#0369A1">Derived CMY: C = 1 - 120/255 = 0.53, M = 1 - 150/255 = 0.41, Y = 1 - 180/255 = 0.29</text>
                </g>
            </g>

            <!-- Page 2 Footer -->
            <text x="257" y="466" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif" font-size="9px" font-weight="600" fill="#94A3B8">Page 2 of 4 (Continuous Spatial Polygon: Q1 mapped to P1+P2, Q2 mapped to P2)</text>
        </g>
    </g>

    <!-- ============================================================== -->
    <!-- PANEL 3 (RIGHT): TEACHER VISUAL CROP CONFIRMATION MODAL UI     -->
    <!-- Coordinates: x: 1180, y: 75, w: 575, h: 1025                    -->
    <!-- ============================================================== -->
    <g transform="translate(1180, 75)">
        <rect width="575" height="1025" rx="8" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1.3" />
        
        <!-- Header Bar -->
        <rect width="575" height="38" rx="8" fill="#047857" />
        <rect y="30" width="575" height="8" fill="#047857" />
        <text x="16" y="24" class="panel-header-title">3. Visual Crop &amp; Mapping Confirmation Modal</text>
        <text x="560" y="24" text-anchor="end" class="panel-header-sub">evaluation_wizard.html (Step 2.5)</text>

        <!-- MODAL WINDOW SHELL -->
        <g transform="translate(20, 50)">
            <rect width="535" height="955" rx="8" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.5" />
            
            <!-- Modal Title Bar -->
            <rect width="535" height="42" rx="8" fill="#0F172A" />
            <rect y="34" width="535" height="8" fill="#0F172A" />
            <circle cx="20" cy="21" r="5" fill="#EF4444" />
            <circle cx="36" cy="21" r="5" fill="#F59E0B" />
            <circle cx="52" cy="21" r="5" fill="#10B981" />
            <text x="72" y="25" font-family="'Segoe UI', Arial, sans-serif" font-size="12px" font-weight="800" fill="#F8FAFC">Step 2.5: Question Mapping Review &amp; Teacher Confirmation</text>
            
            <rect x="420" y="10" width="105" height="22" rx="4" fill="#065F46" />
            <text x="472" y="25" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif" font-size="9.5px" font-weight="700" fill="#A7F3D0">Ready for AI (98%)</text>

            <!-- PREVIEW VALIDATION BREAKDOWN CARD -->
            <g transform="translate(14, 52)">
                <rect width="507" height="48" rx="6" fill="#0F172A" stroke="#334155" stroke-width="1" />
                <text x="12" y="18" font-family="Consolas" font-size="10px" font-weight="800" fill="#34D399">--- PREVIEW VALIDATION BREAKDOWN ---</text>
                
                <g transform="translate(12, 36)">
                    <text x="0" y="0" font-family="Consolas" font-size="9.5px" fill="#94A3B8">Pages: <tspan font-weight="700" fill="#FFFFFF">4</tspan></text>
                    <text x="80" y="0" font-family="Consolas" font-size="9.5px" fill="#94A3B8">Orientation: <tspan font-weight="700" fill="#34D399">0° (OK)</tspan></text>
                    <text x="210" y="0" font-family="Consolas" font-size="9.5px" fill="#94A3B8">Blank Pages: <tspan font-weight="700" fill="#FFFFFF">0</tspan></text>
                    <text x="330" y="0" font-family="Consolas" font-size="9.5px" fill="#94A3B8">OCR Confidence: <tspan font-weight="700" fill="#34D399">98.2%</tspan></text>
                </g>
            </g>

            <!-- STUDENT INFO VERIFICATION CARD -->
            <g transform="translate(14, 110)">
                <rect width="507" height="64" rx="6" fill="#F8FAFC" stroke="#E2E8F0" stroke-width="1" />
                <text x="12" y="18" font-family="'Segoe UI', Arial, sans-serif" font-size="10.5px" font-weight="700" fill="#334155">Verified Student &amp; Course (IUBAT CSE 4385 — Summer 2026)</text>
                
                <g transform="translate(12, 28)">
                    <!-- Input 1: Student Name -->
                    <rect x="0" y="4" width="235" height="24" rx="4" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1" />
                    <text x="8" y="20" font-family="'Segoe UI', Arial, sans-serif" font-size="10px" font-weight="700" fill="#0F172A">Tanvir Hasan (Sec: E)</text>
                    
                    <!-- Input 2: Student Roll -->
                    <rect x="248" y="4" width="235" height="24" rx="4" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1" />
                    <text x="256" y="20" font-family="'Segoe UI', Arial, sans-serif" font-size="10px" font-weight="700" fill="#0F172A">ID: 22103045 (BCSE)</text>
                </g>
            </g>

            <!-- INTERACTIVE QUESTION CARDS CONTAINER -->
            <g transform="translate(14, 184)">
                
                <!-- CARD 1: QUESTION 1 (MULTI-PAGE LINKED) -->
                <g transform="translate(0, 0)">
                    <rect width="507" height="215" rx="6" fill="#FFFFFF" stroke="#16A34A" stroke-width="1.5" />
                    
                    <!-- Card Top Strip -->
                    <rect width="507" height="28" rx="6" fill="#DCFCE7" />
                    <rect y="22" width="507" height="6" fill="#DCFCE7" />
                    <text x="12" y="19" font-family="'Segoe UI', Arial, sans-serif" font-size="11.5px" font-weight="800" fill="#166534">Question 1: Histogram Equalization &amp; 3rd Row Matrix Shifting</text>
                    
                    <rect x="355" y="5" width="142" height="18" rx="3" fill="#16A34A" />
                    <text x="426" y="17" text-anchor="middle" class="badge-text" fill="#FFFFFF">MULTI-PAGE: PAGES 1, 2</text>

                    <!-- Content Layout: Thumbnail Crop on Left, Controls on Right -->
                    <g transform="translate(12, 38)">
                        <!-- Thumbnail Script Crop Image Box -->
                        <rect width="195" height="125" rx="4" fill="#F0FDF4" stroke="#86EFAC" stroke-width="1" />
                        <text x="10" y="18" font-family="'Courier New', monospace" font-size="10px" font-weight="700" fill="#15803D">Answer to Question No. 1</text>
                        <text x="10" y="34" font-family="'Segoe UI', Arial, sans-serif" font-size="8.5px" font-style="italic" fill="#334155">• N = 36, L = 256, Gray levels r_k</text>
                        <text x="10" y="48" font-family="'Segoe UI', Arial, sans-serif" font-size="8.5px" font-style="italic" fill="#334155">• s_k = round[255 × CDF(r_k)]</text>
                        <text x="10" y="62" font-family="'Segoe UI', Arial, sans-serif" font-size="8.5px" font-style="italic" fill="#334155">• 3rd Row Original: [54,78,136,96,150,76]</text>
                        <text x="10" y="76" font-family="'Segoe UI', Arial, sans-serif" font-size="8.5px" font-style="italic" fill="#334155">• Result: [43, 85, 191, 120, 227, 78]</text>
                        <rect x="8" y="88" width="179" height="24" rx="3" fill="#DCFCE7" stroke="#BBF7D0" stroke-width="0.8" />
                        <text x="97" y="104" text-anchor="middle" font-family="Consolas" font-size="8px" font-weight="700" fill="#166534">Chained Payload: 1200px Cropped Matrix</text>

                        <!-- Controls on Right -->
                        <g transform="translate(210, 0)">
                            <text x="0" y="12" class="label-text">Detection Confidence: <tspan font-weight="800" fill="#16A34A">99% (High)</tspan></text>
                            <text x="0" y="28" class="label-text">Page Assignment: <tspan font-weight="700" fill="#2563EB">Page 1, Page 2</tspan></text>
                            
                            <!-- Boundary Adjustment Slider -->
                            <text x="0" y="48" font-family="'Segoe UI', Arial, sans-serif" font-size="9.5px" font-weight="700" fill="#475569">Interactive Boundary Sliders:</text>
                            <rect x="0" y="56" width="270" height="14" rx="3" fill="#F1F5F9" />
                            <rect x="35" y="58" width="180" height="10" rx="2" fill="#86EFAC" />
                            <circle cx="35" cy="63" r="5" fill="#16A34A" />
                            <circle cx="215" cy="63" r="5" fill="#16A34A" />
                            <text x="0" y="82" font-family="Consolas" font-size="8.5px" fill="#64748B">ymin: 0.15</text>
                            <text x="220" y="82" font-family="Consolas" font-size="8.5px" fill="#64748B">ymax: 0.42</text>

                            <!-- Checkbox / Toggle Status -->
                            <rect x="0" y="92" width="270" height="24" rx="4" fill="#F0FDF4" stroke="#86EFAC" stroke-width="0.8" />
                            <text x="10" y="108" font-family="'Segoe UI', Arial, sans-serif" font-size="10px" font-weight="700" fill="#15803D">✓ Examiner Verified &amp; Boundary Locked</text>
                        </g>
                    </g>
                    
                    <!-- Card Footer Bar -->
                    <g transform="translate(12, 172)">
                        <rect width="483" height="32" rx="4" fill="#F8FAFC" stroke="#E2E8F0" stroke-width="0.8" />
                        <text x="10" y="20" font-family="Consolas" font-size="9.5px" font-weight="600" fill="#334155">Extracted Tokens: 385 words | Rubric Max: 25 Marks | Target: CO2, C3, PO1</text>
                        <text x="473" y="20" text-anchor="end" font-family="'Segoe UI', Arial, sans-serif" font-size="9.5px" font-weight="700" fill="#16A34A">Ready for Evaluator</text>
                    </g>
                </g>

                <!-- CARD 2: QUESTION 2 (SINGLE PAGE) -->
                <g transform="translate(0, 228)">
                    <rect width="507" height="205" rx="6" fill="#FFFFFF" stroke="#2563EB" stroke-width="1.5" />
                    
                    <!-- Card Top Strip -->
                    <rect width="507" height="28" rx="6" fill="#DBEAFE" />
                    <rect y="22" width="507" height="6" fill="#DBEAFE" />
                    <text x="12" y="19" font-family="'Segoe UI', Arial, sans-serif" font-size="11.5px" font-weight="800" fill="#1E40AF">Question 2: First Pixel (120, 150, 180) to HSI &amp; CMY</text>
                    
                    <rect x="355" y="5" width="142" height="18" rx="3" fill="#2563EB" />
                    <text x="426" y="17" text-anchor="middle" class="badge-text" fill="#FFFFFF">SINGLE PAGE: PAGE 2</text>

                    <!-- Content Layout -->
                    <g transform="translate(12, 38)">
                        <!-- Thumbnail Crop -->
                        <rect width="195" height="118" rx="4" fill="#EFF6FF" stroke="#93C5FD" stroke-width="1" />
                        <text x="10" y="18" font-family="'Courier New', monospace" font-size="10px" font-weight="700" fill="#1D4ED8">Ans to Question No. 2</text>
                        <text x="10" y="34" font-family="'Segoe UI', Arial, sans-serif" font-size="8.5px" font-style="italic" fill="#334155">• Pixel: (R=120, G=150, B=180)</text>
                        <text x="10" y="48" font-family="'Segoe UI', Arial, sans-serif" font-size="8.5px" font-style="italic" fill="#334155">• Intensity: I = (120+150+180)/3 = 150</text>
                        <text x="10" y="62" font-family="'Segoe UI', Arial, sans-serif" font-size="8.5px" font-style="italic" fill="#334155">• Saturation: S = 1 - 3(120)/450 = 0.20</text>
                        <text x="10" y="76" font-family="'Segoe UI', Arial, sans-serif" font-size="8.5px" font-style="italic" fill="#334155">• CMY: [0.53, 0.41, 0.29]^T</text>
                        <rect x="8" y="84" width="179" height="22" rx="3" fill="#DBEAFE" stroke="#BFDBFE" stroke-width="0.8" />
                        <text x="97" y="99" text-anchor="middle" font-family="Consolas" font-size="8px" font-weight="700" fill="#1E40AF">1200px Visual Crop Attached</text>

                        <!-- Controls on Right -->
                        <g transform="translate(210, 0)">
                            <text x="0" y="12" class="label-text">Detection Confidence: <tspan font-weight="800" fill="#2563EB">97% (High)</tspan></text>
                            <text x="0" y="28" class="label-text">Page Assignment: <tspan font-weight="700" fill="#2563EB">Page 2 [y: 0.44 - 0.95]</tspan></text>
                            
                            <text x="0" y="48" font-family="'Segoe UI', Arial, sans-serif" font-size="9.5px" font-weight="700" fill="#475569">Interactive Boundary Sliders:</text>
                            <rect x="0" y="56" width="270" height="14" rx="3" fill="#F1F5F9" />
                            <rect x="90" y="58" width="165" height="10" rx="2" fill="#93C5FD" />
                            <circle cx="90" cy="63" r="5" fill="#2563EB" />
                            <circle cx="255" cy="63" r="5" fill="#2563EB" />
                            <text x="55" y="82" font-family="Consolas" font-size="8.5px" fill="#64748B">ymin: 0.44</text>
                            <text x="225" y="82" font-family="Consolas" font-size="8.5px" fill="#64748B">ymax: 0.95</text>

                            <rect x="0" y="88" width="270" height="24" rx="4" fill="#EFF6FF" stroke="#BFDBFE" stroke-width="0.8" />
                            <text x="10" y="104" font-family="'Segoe UI', Arial, sans-serif" font-size="10px" font-weight="700" fill="#1D4ED8">✓ Examiner Verified &amp; Boundary Locked</text>
                        </g>
                    </g>
                    
                    <g transform="translate(12, 164)">
                        <rect width="483" height="30" rx="4" fill="#F8FAFC" stroke="#E2E8F0" stroke-width="0.8" />
                        <text x="10" y="19" font-family="Consolas" font-size="9.5px" font-weight="600" fill="#334155">Extracted Tokens: 290 words | Rubric Max: 25 Marks (15+10) | CO2, C3, PO1</text>
                        <text x="473" y="19" text-anchor="end" font-family="'Segoe UI', Arial, sans-serif" font-size="9.5px" font-weight="700" fill="#2563EB">Ready for Evaluator</text>
                    </g>
                </g>

                <!-- CARD 3: QUESTIONS 3 & 4 (DETECTED ON PAGES 3 & 4) -->
                <g transform="translate(0, 445)">
                    <rect width="507" height="130" rx="6" fill="#FFFFFF" stroke="#7C3AED" stroke-width="1.2" />
                    <rect width="507" height="26" rx="6" fill="#EDE9FE" />
                    <rect y="20" width="507" height="6" fill="#EDE9FE" />
                    <text x="12" y="18" font-family="'Segoe UI', Arial, sans-serif" font-size="11px" font-weight="800" fill="#6D28D9">Questions 3 &amp; 4: Image Types &amp; DIP Steps</text>
                    
                    <rect x="365" y="4" width="132" height="18" rx="3" fill="#7C3AED" />
                    <text x="431" y="16" text-anchor="middle" class="badge-text" fill="#FFFFFF">DETECTED: PAGES 3 &amp; 4</text>

                    <g transform="translate(12, 34)">
                        <text x="0" y="12" class="doc-text">• Q3 (25 Marks): <tspan font-family="Consolas" font-weight="700">"Ans to Q-3: B&amp;W Attendance, Color Photo, ID Scan Formats"</tspan> (Conf: 95%)</text>
                        <text x="0" y="28" class="doc-text">• Q4 (25 Marks): <tspan font-family="Consolas" font-weight="700">"Q4. Solution: 5 Fundamental Steps of DIP"</tspan> [ymin: 0.12, Conf: 98%]</text>
                        <text x="0" y="44" class="doc-text">• Course Total: 100 Marks (4 Questions × 25) | All 4 Student Answers Discovered &amp; Mapped</text>
                        <rect x="0" y="54" width="483" height="28" rx="4" fill="#F5F3FF" stroke="#DDD6FE" stroke-width="0.8" />
                        <text x="10" y="72" font-family="'Segoe UI', Arial, sans-serif" font-size="10px" font-weight="700" fill="#6D28D9">✓ Pages 3 &amp; 4 Assignments Confirmed | High-Res Script Payloads Ready</text>
                    </g>
                </g>
            </g>

            <!-- MODAL BOTTOM ACTION BUTTONS -->
            <g transform="translate(14, 785)">
                <rect width="507" height="150" rx="6" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1.2" />
                
                <text x="16" y="24" font-family="'Segoe UI', Arial, sans-serif" font-size="11.5px" font-weight="800" fill="#0F172A">Examiner Override &amp; Single-Click Confirmation:</text>
                <text x="16" y="42" class="state-desc">• Teachers can drag sliders, adjust page assignments, or fine-tune boundaries.</text>
                <text x="16" y="58" class="state-desc">• Guarantees zero unmapped student questions before AI token expenditure.</text>

                <!-- Action Button 1: View Full Script -->
                <g transform="translate(16, 75)">
                    <rect width="175" height="38" rx="6" fill="#7C3AED" />
                    <text x="87" y="24" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif" font-size="11px" font-weight="700" fill="#FFFFFF">View Full Answer Script</text>
                </g>

                <!-- Action Button 2: Confirm Mapping & Start Evaluation -->
                <g transform="translate(198, 75)">
                    <rect width="293" height="38" rx="6" fill="#059669" />
                    <text x="146" y="24" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif" font-size="11px" font-weight="800" fill="#FFFFFF">Confirm Mapping &amp; Start AI Evaluation →</text>
                </g>

                <text x="253" y="132" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif" font-size="9.5px" font-weight="600" fill="#64748B">Locks boundaries into StudentAnswerSubmission &amp; launches TaskRouter Dual AI Wizard</text>
            </g>
        </g>
    </g>

    <!-- Bottom Metadata Bar -->
    <g transform="translate(45, 1118)">
        <text x="0" y="0" class="footer-info">IntelliGrade AI Engine Core — Figure 3.6: Question Boundary Discovery State Machine &amp; Spatial Mapping (CSE 4385 Concept)</text>
        <text x="1710" y="0" text-anchor="end" class="footer-info">Target Dimensions: 6.0" × 3.8" (300 DPI, 1800 × 1140 px) | Pure Light Mode | Publication-Ready</text>
    </g>
</svg>
"""
    return svg

def main():
    output_dir = r"F:\Hijbullah\IntelliGrade\materials"
    os.makedirs(output_dir, exist_ok=True)
    
    svg_content = generate_svg()
    
    # Save single image file: Figure-3.6.png
    doc = fitz.open(stream=svg_content.encode("utf-8"), filetype="svg")
    page = doc[0]
    pix = page.get_pixmap(matrix=fitz.Matrix(1, 1), alpha=False)
    
    png_filename = "Figure-3.6.png"
    png_path = os.path.join(output_dir, png_filename)
    
    temp_path = os.path.join(output_dir, "temp_36.png")
    pix.save(temp_path)
    
    img = Image.open(temp_path)
    if img.size != (1800, 1140):
        img = img.resize((1800, 1140), Image.Resampling.LANCZOS)
    
    img.save(png_path, dpi=(300, 300), format="PNG")
    img.close()
    
    if os.path.exists(temp_path):
        os.remove(temp_path)
        
    print(f"Successfully generated single 300 DPI PNG at: {png_path}")

if __name__ == "__main__":
    main()
