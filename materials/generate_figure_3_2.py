"""
Generates Figure 3.2: High-Level Multi-Tier System Architecture of IntelliGrade
Dimensions: Width: 6.5 in, Height: 4.5 in @ 300 DPI (1950 x 1350 px)
Light-mode, clean, simple, highly legible, publication-ready architectural diagram.
Outputs ONLY a single image file: Figure-3.2.png
"""
import os
import fitz  # PyMuPDF
from PIL import Image

def generate_svg():
    width = 1950
    height = 1350

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
    <defs>
        <!-- Arrowhead Markers -->
        <marker id="arrSlate" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <polygon points="0,1 10,5 0,9" fill="#475569" />
        </marker>
        <marker id="arrBlue" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <polygon points="0,1 10,5 0,9" fill="#2563EB" />
        </marker>
        <marker id="arrIndigo" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <polygon points="0,1 10,5 0,9" fill="#4338CA" />
        </marker>
        <marker id="arrEmerald" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <polygon points="0,1 10,5 0,9" fill="#059669" />
        </marker>
        <marker id="arrAmber" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <polygon points="0,1 10,5 0,9" fill="#D97706" />
        </marker>
        <marker id="arrSky" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <polygon points="0,1 10,5 0,9" fill="#0284C7" />
        </marker>

        <style>
            .main-title {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 24px; font-weight: 800; fill: #0F172A; }}
            .main-subtitle {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 13.5px; font-weight: 600; fill: #475569; }}
            
            .tier-header-text {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 12px; font-weight: 800; letter-spacing: 0.8px; text-transform: uppercase; }}
            .tier-sub-text {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 11.5px; font-weight: 600; fill: #475569; }}
            
            .card-header-title {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 15px; font-weight: 700; fill: #FFFFFF; }}
            
            .bullet-title {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 12.5px; font-weight: 700; fill: #1E293B; }}
            .bullet-desc {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 12px; font-weight: 400; fill: #475569; }}
            
            .tech-pill-text {{ font-family: 'Consolas', monospace; font-size: 10px; font-weight: 700; }}
            .footer-info {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 11px; font-weight: 500; fill: #64748B; }}
        </style>
    </defs>

    <!-- Background Canvas -->
    <rect width="{width}" height="{height}" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.5" />

    <!-- Top Title Banner -->
    <g transform="translate(45, 20)">
        <rect x="0" y="0" width="5" height="46" rx="2" fill="#2563EB" />
        <text x="18" y="23" class="main-title">Figure 3.2: High-Level Multi-Tier System Architecture of IntelliGrade</text>
        <text x="18" y="42" class="main-subtitle">End-to-End Enterprise Architecture: Administrative Governance, Computer Vision Preprocessing, Multimodal AI &amp; Real-Time OBE Tabulation</text>
    </g>

    <!-- ============================================================== -->
    <!-- TIER 1: PRESENTATION & INTERACTION TIER                        -->
    <!-- ============================================================== -->
    <g transform="translate(45, 82)">
        <!-- Outer Tier Container -->
        <rect width="1860" height="215" rx="8" fill="#F8FAFC" stroke="#BFDBFE" stroke-width="1.5" />
        
        <!-- Header Strip -->
        <path d="M 0 8 Q 0 0 8 0 L 1852 0 Q 1860 0 1860 8 L 1860 32 L 0 32 Z" fill="#EFF6FF" />
        <line x1="0" y1="32" x2="1860" y2="32" stroke="#BFDBFE" stroke-width="1" />
        
        <rect x="14" y="8" width="6" height="16" rx="2" fill="#2563EB" />
        <text x="28" y="21" class="tier-header-text" fill="#1D4ED8">TIER 1: PRESENTATION &amp; USER INTERACTION</text>
        <text x="350" y="20" class="tier-sub-text">— Responsive Web UI, Dynamic Split-Screen Canvases, and Real-Time Portals (HTML5 / TailwindCSS / JavaScript)</text>

        <!-- 4 Clean Cards -->
        <!-- Card 1.1 -->
        <g transform="translate(18, 44)">
            <rect width="435" height="155" rx="6" fill="#FFFFFF" stroke="#2563EB" stroke-width="1.3" />
            <path d="M 0 6 Q 0 0 6 0 L 429 0 Q 435 0 435 6 L 435 34 L 0 34 Z" fill="#2563EB" />
            <text x="14" y="23" class="card-header-title">Administrative Governance</text>
            
            <g transform="translate(14, 54)">
                <text x="0" y="0" class="bullet-title">• Exam Routine AI Parser:</text>
                <text x="175" y="0" class="bullet-desc">0ms local timetable course match</text>

                <text x="0" y="26" class="bullet-title">• Institutional Tree:</text>
                <text x="135" y="26" class="bullet-desc">College → School → Department CRUD</text>

                <text x="0" y="52" class="bullet-title">• Controller Dashboard:</text>
                <text x="155" y="52" class="bullet-desc">Student approvals &amp; faculty assignments</text>
            </g>
            <rect x="14" y="122" width="180" height="20" rx="4" fill="#EFF6FF" stroke="#BFDBFE" stroke-width="1" />
            <text x="22" y="136" class="tech-pill-text" fill="#1E40AF">/dashboard/exam-controller/</text>
        </g>

        <!-- Card 1.2 -->
        <g transform="translate(473, 44)">
            <rect width="435" height="155" rx="6" fill="#FFFFFF" stroke="#2563EB" stroke-width="1.3" />
            <path d="M 0 6 Q 0 0 6 0 L 429 0 Q 435 0 435 6 L 435 34 L 0 34 Z" fill="#2563EB" />
            <text x="14" y="23" class="card-header-title">23-Taxonomy Question Studio</text>
            
            <g transform="translate(14, 54)">
                <text x="0" y="0" class="bullet-title">• OBE Accreditation:</text>
                <text x="145" y="0" class="bullet-desc">CO1–CO6, PO1–PO12, Bloom levels</text>

                <text x="0" y="26" class="bullet-title">• Engineering Profiles:</text>
                <text x="150" y="26" class="bullet-desc">KP1–KP8, CEP problems, CEA activities</text>

                <text x="0" y="52" class="bullet-title">• Rich Media &amp; Rubrics:</text>
                <text x="150" y="52" class="bullet-desc">LaTeX math, matrices, golden solutions</text>
            </g>
            <rect x="14" y="122" width="145" height="20" rx="4" fill="#EFF6FF" stroke="#BFDBFE" stroke-width="1" />
            <text x="22" y="136" class="tech-pill-text" fill="#1E40AF">/teacher/questions/</text>
        </g>

        <!-- Card 1.3 -->
        <g transform="translate(928, 44)">
            <rect width="455" height="155" rx="6" fill="#FFFFFF" stroke="#2563EB" stroke-width="1.3" />
            <path d="M 0 6 Q 0 0 6 0 L 449 0 Q 455 0 455 6 L 455 34 L 0 34 Z" fill="#2563EB" />
            <text x="14" y="23" class="card-header-title">Dual Evaluation Workbenches</text>
            
            <g transform="translate(14, 54)">
                <text x="0" y="0" class="bullet-title">• Split-Screen Canvas:</text>
                <text x="145" y="0" class="bullet-desc">High-res pan/zoom &amp; synchronized view</text>

                <text x="0" y="26" class="bullet-title">• Dual Pipeline Choice:</text>
                <text x="155" y="26" class="bullet-desc">AI Wizard v3.0 OR 100% Direct Manual</text>

                <text x="0" y="52" class="bullet-title">• Human-in-the-Loop:</text>
                <text x="150" y="52" class="bullet-desc">Score override, feedback tips &amp; finalize</text>
            </g>
            <rect x="14" y="122" width="165" height="20" rx="4" fill="#EFF6FF" stroke="#BFDBFE" stroke-width="1" />
            <text x="22" y="136" class="tech-pill-text" fill="#1E40AF">/evaluation/wizard/ (Dual)</text>
        </g>

        <!-- Card 1.4 -->
        <g transform="translate(1403, 44)">
            <rect width="435" height="155" rx="6" fill="#FFFFFF" stroke="#2563EB" stroke-width="1.3" />
            <path d="M 0 6 Q 0 0 6 0 L 429 0 Q 435 0 435 6 L 435 34 L 0 34 Z" fill="#2563EB" />
            <text x="14" y="23" class="card-header-title">Department &amp; Student Portals</text>
            
            <g transform="translate(14, 54)">
                <text x="0" y="0" class="bullet-title">• Dept Head Analytics:</text>
                <text x="145" y="0" class="bullet-desc">Faculty grading speed &amp; pass rates</text>

                <text x="0" y="26" class="bullet-title">• Student Grade Cards:</text>
                <text x="150" y="26" class="bullet-desc">Self-service marks, GPA &amp; mistake audit</text>

                <text x="0" y="52" class="bullet-title">• Certified Downloads:</text>
                <text x="145" y="52" class="bullet-desc">Watermarked, official stamped PDF scripts</text>
            </g>
            <rect x="14" y="122" width="165" height="20" rx="4" fill="#EFF6FF" stroke="#BFDBFE" stroke-width="1" />
            <text x="22" y="136" class="tech-pill-text" fill="#1E40AF">/dept-head/ &amp; /student/</text>
        </g>
    </g>

    <!-- Clean Connectors: Tier 1 to Tier 2 -->
    <path d="M 270 297 L 270 325" fill="none" stroke="#64748B" stroke-width="2" marker-end="url(#arrIndigo)" />
    <path d="M 700 297 L 700 325" fill="none" stroke="#64748B" stroke-width="2" marker-end="url(#arrIndigo)" />
    <path d="M 1160 297 L 1160 325" fill="none" stroke="#64748B" stroke-width="2" marker-end="url(#arrIndigo)" />
    <path d="M 1620 325 L 1620 297" fill="none" stroke="#0284C7" stroke-width="2" marker-end="url(#arrBlue)" />

    <!-- ============================================================== -->
    <!-- TIER 2: APPLICATION & BUSINESS LOGIC TIER                       -->
    <!-- ============================================================== -->
    <g transform="translate(45, 327)">
        <rect width="1860" height="215" rx="8" fill="#F8FAFC" stroke="#C7D2FE" stroke-width="1.5" />
        
        <path d="M 0 8 Q 0 0 8 0 L 1852 0 Q 1860 0 1860 8 L 1860 32 L 0 32 Z" fill="#EEF2FF" />
        <line x1="0" y1="32" x2="1860" y2="32" stroke="#C7D2FE" stroke-width="1" />
        
        <rect x="14" y="8" width="6" height="16" rx="2" fill="#4338CA" />
        <text x="28" y="21" class="tier-header-text" fill="#3730A3">TIER 2: APPLICATION &amp; BUSINESS LOGIC</text>
        <text x="320" y="20" class="tier-sub-text">— Core Domain Services, Exam Lifecycle State Machine, and RBAC Security (Django 5.2.x &amp; DRF)</text>

        <!-- Card 2.1 -->
        <g transform="translate(18, 44)">
            <rect width="435" height="155" rx="6" fill="#FFFFFF" stroke="#4338CA" stroke-width="1.3" />
            <path d="M 0 6 Q 0 0 6 0 L 429 0 Q 435 0 435 6 L 435 34 L 0 34 Z" fill="#4338CA" />
            <text x="14" y="23" class="card-header-title">Security &amp; RBAC Control</text>
            
            <g transform="translate(14, 54)">
                <text x="0" y="0" class="bullet-title">• Role-Based Access:</text>
                <text x="145" y="0" class="bullet-desc">@controller, @teacher, @dept_head</text>

                <text x="0" y="26" class="bullet-title">• Cryptographic Auth:</text>
                <text x="150" y="26" class="bullet-desc">Argon2 password hashing &amp; CSRF tokens</text>

                <text x="0" y="52" class="bullet-title">• Immutable Audits:</text>
                <text x="135" y="52" class="bullet-desc">EvaluationAuditLog &amp; TeacherReview</text>
            </g>
            <rect x="14" y="122" width="165" height="20" rx="4" fill="#EEF2FF" stroke="#C7D2FE" stroke-width="1" />
            <text x="22" y="136" class="tech-pill-text" fill="#312E81">core.middleware &amp; auth</text>
        </g>

        <!-- Card 2.2 -->
        <g transform="translate(473, 44)">
            <rect width="435" height="155" rx="6" fill="#FFFFFF" stroke="#4338CA" stroke-width="1.3" />
            <path d="M 0 6 Q 0 0 6 0 L 429 0 Q 435 0 435 6 L 435 34 L 0 34 Z" fill="#4338CA" />
            <text x="14" y="23" class="card-header-title">Exam Lifecycle Engine</text>
            
            <g transform="translate(14, 54)">
                <text x="0" y="0" class="bullet-title">• State Machine:</text>
                <text x="110" y="0" class="bullet-desc">Draft → Published → Evaluating → Final</text>

                <text x="0" y="26" class="bullet-title">• Paper Document DOM:</text>
                <text x="165" y="26" class="bullet-desc">Hierarchical question &amp; rubric tree</text>

                <text x="0" y="52" class="bullet-title">• Finalization Service:</text>
                <text x="145" y="52" class="bullet-desc">Score locking &amp; temp file cleanup hook</text>
            </g>
            <rect x="14" y="122" width="165" height="20" rx="4" fill="#EEF2FF" stroke="#C7D2FE" stroke-width="1" />
            <text x="22" y="136" class="tech-pill-text" fill="#312E81">core.models.Examination</text>
        </g>

        <!-- Card 2.3 -->
        <g transform="translate(928, 44)">
            <rect width="455" height="155" rx="6" fill="#FFFFFF" stroke="#4338CA" stroke-width="1.3" />
            <path d="M 0 6 Q 0 0 6 0 L 449 0 Q 455 0 455 6 L 455 34 L 0 34 Z" fill="#4338CA" />
            <text x="14" y="23" class="card-header-title">Grading &amp; Override Coordinator</text>
            
            <g transform="translate(14, 54)">
                <text x="0" y="0" class="bullet-title">• Dual Wizard Router:</text>
                <text x="145" y="0" class="bullet-desc">Dispatches to AI v3.0 or Manual pipeline</text>

                <text x="0" y="26" class="bullet-title">• Threshold Review:</text>
                <text x="135" y="26" class="bullet-desc">Flags confidence &lt; 0.75 for human check</text>

                <text x="0" y="52" class="bullet-title">• Scoring Algorithm:</text>
                <text x="140" y="52" class="bullet-desc">Rubric criteria step scoring &amp; deductions</text>
            </g>
            <rect x="14" y="122" width="175" height="20" rx="4" fill="#EEF2FF" stroke="#C7D2FE" stroke-width="1" />
            <text x="22" y="136" class="tech-pill-text" fill="#312E81">core.services.evaluation</text>
        </g>

        <!-- Card 2.4 -->
        <g transform="translate(1403, 44)">
            <rect width="435" height="155" rx="6" fill="#FFFFFF" stroke="#4338CA" stroke-width="1.3" />
            <path d="M 0 6 Q 0 0 6 0 L 429 0 Q 435 0 435 6 L 435 34 L 0 34 Z" fill="#4338CA" />
            <text x="14" y="23" class="card-header-title">Real-Time OBE Calculation</text>
            
            <g transform="translate(14, 54)">
                <text x="0" y="0" class="bullet-title">• 5-Metric Formula:</text>
                <text x="130" y="0" class="bullet-desc">CT 10% + Mid 25% + Final 50% + Ass 10% + Att 5%</text>

                <text x="0" y="26" class="bullet-title">• Live Tabulation Sync:</text>
                <text x="150" y="26" class="bullet-desc">Instant recalculation on score edits</text>

                <text x="0" y="52" class="bullet-title">• Attainment Matrix:</text>
                <text x="140" y="52" class="bullet-desc">Course Outcome (CO) &amp; PO percentages</text>
            </g>
            <rect x="14" y="122" width="165" height="20" rx="4" fill="#EEF2FF" stroke="#C7D2FE" stroke-width="1" />
            <text x="22" y="136" class="tech-pill-text" fill="#312E81">core.services.tabulation</text>
        </g>
    </g>

    <!-- Clean Connectors: Tier 2 to Tier 3 -->
    <path d="M 270 542 L 270 570" fill="none" stroke="#64748B" stroke-width="2" marker-end="url(#arrEmerald)" />
    <path d="M 700 542 L 700 570" fill="none" stroke="#64748B" stroke-width="2" marker-end="url(#arrEmerald)" />
    <path d="M 1160 570 L 1160 542" fill="none" stroke="#059669" stroke-width="2" marker-end="url(#arrIndigo)" />

    <!-- ============================================================== -->
    <!-- TIER 3: COMPUTER VISION & DOCUMENT PROCESSING TIER             -->
    <!-- ============================================================== -->
    <g transform="translate(45, 572)">
        <rect width="1860" height="215" rx="8" fill="#F8FAFC" stroke="#A7F3D0" stroke-width="1.5" />
        
        <path d="M 0 8 Q 0 0 8 0 L 1852 0 Q 1860 0 1860 8 L 1860 32 L 0 32 Z" fill="#ECFDF5" />
        <line x1="0" y1="32" x2="1860" y2="32" stroke="#A7F3D0" stroke-width="1" />
        
        <rect x="14" y="8" width="6" height="16" rx="2" fill="#059669" />
        <text x="28" y="21" class="tier-header-text" fill="#065F46">TIER 3: COMPUTER VISION &amp; SCRIPT PROCESSING</text>
        <text x="360" y="20" class="tier-sub-text">— 300 DPI Preprocessing, OpenCV Deskewing, Otsu Thresholding, and Hybrid OCR (PyMuPDF / OpenCV / EasyOCR)</text>

        <!-- Card 3.1 -->
        <g transform="translate(18, 44)">
            <rect width="435" height="155" rx="6" fill="#FFFFFF" stroke="#059669" stroke-width="1.3" />
            <path d="M 0 6 Q 0 0 6 0 L 429 0 Q 435 0 435 6 L 435 34 L 0 34 Z" fill="#059669" />
            <text x="14" y="23" class="card-header-title">300 DPI Image Normalization</text>
            
            <g transform="translate(14, 54)">
                <text x="0" y="0" class="bullet-title">• PyMuPDF Rasterizer:</text>
                <text x="155" y="0" class="bullet-desc">Universal 300 DPI high-res page render</text>

                <text x="0" y="26" class="bullet-title">• Hough Deskewing:</text>
                <text x="140" y="26" class="bullet-desc">Auto skew detection (-45° to +45° fix)</text>

                <text x="0" y="52" class="bullet-title">• Otsu Thresholding:</text>
                <text x="140" y="52" class="bullet-desc">Adaptive contrast &amp; shadow cleanup</text>
            </g>
            <rect x="14" y="122" width="165" height="20" rx="4" fill="#ECFDF5" stroke="#A7F3D0" stroke-width="1" />
            <text x="22" y="136" class="tech-pill-text" fill="#064E3B">OpenCV &amp; PyMuPDF fitz</text>
        </g>

        <!-- Card 3.2 -->
        <g transform="translate(473, 44)">
            <rect width="435" height="155" rx="6" fill="#FFFFFF" stroke="#059669" stroke-width="1.3" />
            <path d="M 0 6 Q 0 0 6 0 L 429 0 Q 435 0 435 6 L 435 34 L 0 34 Z" fill="#059669" />
            <text x="14" y="23" class="card-header-title">Working Copy Isolation</text>
            
            <g transform="translate(14, 54)">
                <text x="0" y="0" class="bullet-title">• Safe Image Copies:</text>
                <text x="140" y="0" class="bullet-desc">Working files in media/submission_working/</text>

                <text x="0" y="26" class="bullet-title">• Original Protected:</text>
                <text x="140" y="26" class="bullet-desc">Zero destructive changes to master PDF</text>

                <text x="0" y="52" class="bullet-title">• Versioned Edits:</text>
                <text x="120" y="52" class="bullet-desc">Tracks page rotations &amp; boundary crops</text>
            </g>
            <rect x="14" y="122" width="175" height="20" rx="4" fill="#ECFDF5" stroke="#A7F3D0" stroke-width="1" />
            <text x="22" y="136" class="tech-pill-text" fill="#064E3B">WorkingCopyManager</text>
        </g>

        <!-- Card 3.3 -->
        <g transform="translate(928, 44)">
            <rect width="455" height="155" rx="6" fill="#FFFFFF" stroke="#059669" stroke-width="1.3" />
            <path d="M 0 6 Q 0 0 6 0 L 449 0 Q 455 0 455 6 L 455 34 L 0 34 Z" fill="#059669" />
            <text x="14" y="23" class="card-header-title">Hybrid Multi-Engine OCR</text>
            
            <g transform="translate(14, 54)">
                <text x="0" y="0" class="bullet-title">• 3-Engine Ensemble:</text>
                <text x="145" y="0" class="bullet-desc">PyMuPDF Font + Tesseract + EasyOCR</text>

                <text x="0" y="26" class="bullet-title">• Handwriting Mode:</text>
                <text x="140" y="26" class="bullet-desc">PyTorch CPU CRAFT detector + CRNN</text>

                <text x="0" y="52" class="bullet-title">• Word &amp; Line Boxes:</text>
                <text x="145" y="52" class="bullet-desc">Cached JSON bbox coordinates per word</text>
            </g>
            <rect x="14" y="122" width="175" height="20" rx="4" fill="#ECFDF5" stroke="#A7F3D0" stroke-width="1" />
            <text x="22" y="136" class="tech-pill-text" fill="#064E3B">core.ai_engine.ocr</text>
        </g>

        <!-- Card 3.4 -->
        <g transform="translate(1403, 44)">
            <rect width="435" height="155" rx="6" fill="#FFFFFF" stroke="#059669" stroke-width="1.3" />
            <path d="M 0 6 Q 0 0 6 0 L 429 0 Q 435 0 435 6 L 435 34 L 0 34 Z" fill="#059669" />
            <text x="14" y="23" class="card-header-title">Question Detection &amp; Mapping</text>
            
            <g transform="translate(14, 54)">
                <text x="0" y="0" class="bullet-title">• Regex Pattern Matcher:</text>
                <text x="165" y="0" class="bullet-desc">Identifies Q1, Q.1, 1(a), Ans to Q, ১, ২</text>

                <text x="0" y="26" class="bullet-title">• Multi-Page Flow:</text>
                <text x="135" y="26" class="bullet-desc">Detects answer continuations across pages</text>

                <text x="0" y="52" class="bullet-title">• Visual Confirmation:</text>
                <text x="150" y="52" class="bullet-desc">Teacher modal for fast crop adjustment</text>
            </g>
            <rect x="14" y="122" width="165" height="20" rx="4" fill="#ECFDF5" stroke="#A7F3D0" stroke-width="1" />
            <text x="22" y="136" class="tech-pill-text" fill="#064E3B">mapping.orchestrator</text>
        </g>
    </g>

    <!-- Clean Connectors: Tier 3 to Tier 4 -->
    <path d="M 700 787 L 700 817" fill="none" stroke="#64748B" stroke-width="2" marker-end="url(#arrAmber)" />
    <path d="M 1160 787 L 1160 817" fill="none" stroke="#64748B" stroke-width="2" marker-end="url(#arrAmber)" />
    <path d="M 1620 817 L 1620 787" fill="none" stroke="#D97706" stroke-width="2" marker-end="url(#arrEmerald)" />

    <!-- ============================================================== -->
    <!-- TIER 4: MULTIMODAL AI ORCHESTRATION TIER                        -->
    <!-- ============================================================== -->
    <g transform="translate(45, 817)">
        <rect width="1860" height="215" rx="8" fill="#F8FAFC" stroke="#FED7AA" stroke-width="1.5" />
        
        <path d="M 0 8 Q 0 0 8 0 L 1852 0 Q 1860 0 1860 8 L 1860 32 L 0 32 Z" fill="#FFF7ED" />
        <line x1="0" y1="32" x2="1860" y2="32" stroke="#FED7AA" stroke-width="1" />
        
        <rect x="14" y="8" width="6" height="16" rx="2" fill="#D97706" />
        <text x="28" y="21" class="tier-header-text" fill="#B45309">TIER 4: MULTIMODAL AI INFERENCE &amp; ORCHESTRATION</text>
        <text x="380" y="20" class="tier-sub-text">— TaskRouter Failover Cascade, Rate-Limit Cooldown, Multi-LLM Providers, and JSON/LaTeX Repair</text>

        <!-- Card 4.1 -->
        <g transform="translate(18, 44)">
            <rect width="435" height="155" rx="6" fill="#FFFFFF" stroke="#D97706" stroke-width="1.3" />
            <path d="M 0 6 Q 0 0 6 0 L 429 0 Q 435 0 435 6 L 435 34 L 0 34 Z" fill="#D97706" />
            <text x="14" y="23" class="card-header-title">TaskRouter Failover Cascade</text>
            
            <g transform="translate(14, 54)">
                <text x="0" y="0" class="bullet-title">• Zero-Downtime Failover:</text>
                <text x="175" y="0" class="bullet-desc">Switches provider on 429 / error / quota</text>

                <text x="0" y="26" class="bullet-title">• Rate Limit Cooldown:</text>
                <text x="155" y="26" class="bullet-desc">Automatic 60s cooldown timer registry</text>

                <text x="0" y="52" class="bullet-title">• Health &amp; Latency Monitor:</text>
                <text x="180" y="52" class="bullet-desc">Real-time status tracking per model</text>
            </g>
            <rect x="14" y="122" width="165" height="20" rx="4" fill="#FFF7ED" stroke="#FED7AA" stroke-width="1" />
            <text x="22" y="136" class="tech-pill-text" fill="#9A3412">routing.task_router</text>
        </g>

        <!-- Card 4.2 -->
        <g transform="translate(473, 44)">
            <rect width="435" height="155" rx="6" fill="#FFFFFF" stroke="#D97706" stroke-width="1.3" />
            <path d="M 0 6 Q 0 0 6 0 L 429 0 Q 435 0 435 6 L 435 34 L 0 34 Z" fill="#D97706" />
            <text x="14" y="23" class="card-header-title">Multi-Provider Model Suite</text>
            
            <g transform="translate(14, 54)">
                <text x="0" y="0" class="bullet-title">• Local Offline Vision:</text>
                <text x="150" y="0" class="bullet-desc">Moondream2 / Ollama (800px LANCZOS)</text>

                <text x="0" y="26" class="bullet-title">• High-Speed Cloud:</text>
                <text x="145" y="26" class="bullet-desc">Groq Llama-3.3 70B (~500ms response)</text>

                <text x="0" y="52" class="bullet-title">• Deep Multimodal:</text>
                <text x="135" y="52" class="bullet-desc">Google Gemini 2.5 Flash / GPT-4o / OpenRouter</text>
            </g>
            <rect x="14" y="122" width="175" height="20" rx="4" fill="#FFF7ED" stroke="#FED7AA" stroke-width="1" />
            <text x="22" y="136" class="tech-pill-text" fill="#9A3412">ai_engine.providers.*</text>
        </g>

        <!-- Card 4.3 -->
        <g transform="translate(928, 44)">
            <rect width="455" height="155" rx="6" fill="#FFFFFF" stroke="#D97706" stroke-width="1.3" />
            <path d="M 0 6 Q 0 0 6 0 L 449 0 Q 455 0 455 6 L 455 34 L 0 34 Z" fill="#D97706" />
            <text x="14" y="23" class="card-header-title">JSON Sanitizer &amp; LaTeX Repair</text>
            
            <g transform="translate(14, 54)">
                <text x="0" y="0" class="bullet-title">• Pydantic Enforcement:</text>
                <text x="165" y="0" class="bullet-desc">Validates structured grading score schema</text>

                <text x="0" y="26" class="bullet-title">• Automated JSON Fix:</text>
                <text x="160" y="26" class="bullet-desc">Repairs trailing commas &amp; quotes</text>

                <text x="0" y="52" class="bullet-title">• Formula Standardization:</text>
                <text x="180" y="52" class="bullet-desc">Normalizes mathematical LaTeX equations</text>
            </g>
            <rect x="14" y="122" width="175" height="20" rx="4" fill="#FFF7ED" stroke="#FED7AA" stroke-width="1" />
            <text x="22" y="136" class="tech-pill-text" fill="#9A3412">core.ai_engine.services</text>
        </g>

        <!-- Card 4.4 -->
        <g transform="translate(1403, 44)">
            <rect width="435" height="155" rx="6" fill="#FFFFFF" stroke="#D97706" stroke-width="1.3" />
            <path d="M 0 6 Q 0 0 6 0 L 429 0 Q 435 0 435 6 L 435 34 L 0 34 Z" fill="#D97706" />
            <text x="14" y="23" class="card-header-title">Few-Shot RAG Memory</text>
            
            <g transform="translate(14, 54)">
                <text x="0" y="0" class="bullet-title">• Feedback Corrections:</text>
                <text x="160" y="0" class="bullet-desc">Learns from teacher score adjustments</text>

                <text x="0" y="26" class="bullet-title">• Semantic Exemplars:</text>
                <text x="145" y="26" class="bullet-desc">Embeddings retrieve similar past answers</text>

                <text x="0" y="52" class="bullet-title">• Continuous Adaptation:</text>
                <text x="165" y="52" class="bullet-desc">Aligns evaluation style with instructor rigor</text>
            </g>
            <rect x="14" y="122" width="165" height="20" rx="4" fill="#FFF7ED" stroke="#FED7AA" stroke-width="1" />
            <text x="22" y="136" class="tech-pill-text" fill="#9A3412">retrieval.rag_retriever</text>
        </g>
    </g>

    <!-- Clean Connectors: Tier 4 to Tier 5 -->
    <path d="M 270 1032 L 270 1062" fill="none" stroke="#64748B" stroke-width="2" marker-end="url(#arrSky)" />
    <path d="M 700 1032 L 700 1062" fill="none" stroke="#64748B" stroke-width="2" marker-end="url(#arrSky)" />
    <path d="M 1160 1032 L 1160 1062" fill="none" stroke="#64748B" stroke-width="2" marker-end="url(#arrSky)" />
    <path d="M 1620 1032 L 1620 1062" fill="none" stroke="#64748B" stroke-width="2" marker-end="url(#arrSky)" />

    <!-- ============================================================== -->
    <!-- TIER 5: PERSISTENCE, REPORTING & DISSEMINATION TIER            -->
    <!-- ============================================================== -->
    <g transform="translate(45, 1062)">
        <rect width="1860" height="225" rx="8" fill="#F8FAFC" stroke="#7DD3FC" stroke-width="1.5" />
        
        <path d="M 0 8 Q 0 0 8 0 L 1852 0 Q 1860 0 1860 8 L 1860 32 L 0 32 Z" fill="#E0F2FE" />
        <line x1="0" y1="32" x2="1860" y2="32" stroke="#7DD3FC" stroke-width="1" />
        
        <rect x="14" y="8" width="6" height="16" rx="2" fill="#0284C7" />
        <text x="28" y="21" class="tier-header-text" fill="#0369A1">TIER 5: PERSISTENCE, OBE TABULATION &amp; DISSEMINATION</text>
        <text x="400" y="20" class="tier-sub-text">— PostgreSQL Relational DB, Bi-Directional Tabulation, 8-Sheet Excel Builder, and Certified PDF Stamping</text>

        <!-- Card 5.1 -->
        <g transform="translate(18, 44)">
            <rect width="435" height="165" rx="6" fill="#FFFFFF" stroke="#0284C7" stroke-width="1.3" />
            <path d="M 0 6 Q 0 0 6 0 L 429 0 Q 435 0 435 6 L 435 34 L 0 34 Z" fill="#0284C7" />
            <text x="14" y="23" class="card-header-title">PostgreSQL Relational Storage</text>
            
            <g transform="translate(14, 54)">
                <text x="0" y="0" class="bullet-title">• Institutional &amp; Exam DB:</text>
                <text x="165" y="0" class="bullet-desc">ACID storage for courses, questions &amp; scripts</text>

                <text x="0" y="26" class="bullet-title">• Composite B-Tree Indexes:</text>
                <text x="175" y="26" class="bullet-desc">(exam, status), (tabulation, student_id)</text>

                <text x="0" y="52" class="bullet-title">• Query Optimization:</text>
                <text x="150" y="52" class="bullet-desc">Zero N+1 queries via select/prefetch_related</text>
            </g>
            <rect x="14" y="132" width="165" height="20" rx="4" fill="#E0F2FE" stroke="#7DD3FC" stroke-width="1" />
            <text x="22" y="146" class="tech-pill-text" fill="#075985">PostgreSQL 16+ &amp; Django ORM</text>
        </g>

        <!-- Card 5.2 -->
        <g transform="translate(473, 44)">
            <rect width="435" height="165" rx="6" fill="#FFFFFF" stroke="#0284C7" stroke-width="1.3" />
            <path d="M 0 6 Q 0 0 6 0 L 429 0 Q 435 0 435 6 L 435 34 L 0 34 Z" fill="#0284C7" />
            <text x="14" y="23" class="card-header-title">StudentGradeRecord Repository</text>
            
            <g transform="translate(14, 54)">
                <text x="0" y="0" class="bullet-title">• Synchronized Scores:</text>
                <text x="150" y="0" class="bullet-desc">Aggregated obtained marks &amp; letter grades</text>

                <text x="0" y="26" class="bullet-title">• Attendance Weighting:</text>
                <text x="160" y="26" class="bullet-desc">Fixed 5.0% institutional metric calculation</text>

                <text x="0" y="52" class="bullet-title">• Outcome JSON Stores:</text>
                <text x="160" y="52" class="bullet-desc">Class-wide CO and PO percentage breakdowns</text>
            </g>
            <rect x="14" y="132" width="175" height="20" rx="4" fill="#E0F2FE" stroke="#7DD3FC" stroke-width="1" />
            <text x="22" y="146" class="tech-pill-text" fill="#075985">StudentGradeRecord Store</text>
        </g>

        <!-- Card 5.3 -->
        <g transform="translate(928, 44)">
            <rect width="455" height="165" rx="6" fill="#FFFFFF" stroke="#0284C7" stroke-width="1.3" />
            <path d="M 0 6 Q 0 0 6 0 L 449 0 Q 455 0 455 6 L 455 34 L 0 34 Z" fill="#0284C7" />
            <text x="14" y="23" class="card-header-title">8-Sheet Excel &amp; Certified PDF</text>
            
            <g transform="translate(14, 54)">
                <text x="0" y="0" class="bullet-title">• openpyxl 8-Sheet Workbook:</text>
                <text x="195" y="0" class="bullet-desc">Course summary, marks, CO/PO attainments</text>

                <text x="0" y="26" class="bullet-title">• ReportLab Certified PDF:</text>
                <text x="175" y="26" class="bullet-desc">Official stamped script with score feedback</text>

                <text x="0" y="52" class="bullet-title">• Security Watermark:</text>
                <text x="150" y="52" class="bullet-desc">Institutional verification stamp on scripts</text>
            </g>
            <rect x="14" y="132" width="175" height="20" rx="4" fill="#E0F2FE" stroke="#7DD3FC" stroke-width="1" />
            <text x="22" y="146" class="tech-pill-text" fill="#075985">openpyxl &amp; ReportLab PDF</text>
        </g>

        <!-- Card 5.4 -->
        <g transform="translate(1403, 44)">
            <rect width="435" height="165" rx="6" fill="#FFFFFF" stroke="#0284C7" stroke-width="1.3" />
            <path d="M 0 6 Q 0 0 6 0 L 429 0 Q 435 0 435 6 L 435 34 L 0 34 Z" fill="#0284C7" />
            <text x="14" y="23" class="card-header-title">Async Email &amp; File Cleanup</text>
            
            <g transform="translate(14, 54)">
                <text x="0" y="0" class="bullet-title">• Threaded SMTP Mailer:</text>
                <text x="160" y="0" class="bullet-desc">Background grade release &amp; login alerts</text>

                <text x="0" y="26" class="bullet-title">• Automated Temp Purge:</text>
                <text x="160" y="26" class="bullet-desc">Cleans submission_working/ on PDF finalize</text>

                <text x="0" y="52" class="bullet-title">• Storage Optimization:</text>
                <text x="155" y="52" class="bullet-desc">Reclaims server disk from working images</text>
            </g>
            <rect x="14" y="132" width="165" height="20" rx="4" fill="#E0F2FE" stroke="#7DD3FC" stroke-width="1" />
            <text x="22" y="146" class="tech-pill-text" fill="#075985">core.services.email_service</text>
        </g>
    </g>

    <!-- Bottom Metadata Bar -->
    <g transform="translate(45, 1325)">
        <text x="0" y="0" class="footer-info">IntelliGrade Enterprise System Architecture — Figure 3.2: High-Level Multi-Tier Architecture Blueprint</text>
        <text x="1860" y="0" class="footer-info" text-anchor="end">Target Dimensions: 6.5" × 4.5" (300 DPI, 1950 × 1350 px) | Publication-Ready Light Mode</text>
    </g>
</svg>
"""
    return svg

def main():
    output_dir = r"F:\Hijbullah\IntelliGrade\materials"
    os.makedirs(output_dir, exist_ok=True)
    
    svg_content = generate_svg()
    
    # Save single image file: Figure-3.2.png
    doc = fitz.open(stream=svg_content.encode("utf-8"), filetype="svg")
    page = doc[0]
    pix = page.get_pixmap(matrix=fitz.Matrix(1, 1), alpha=False)
    
    png_filename = "Figure-3.2.png"
    png_path = os.path.join(output_dir, png_filename)
    
    temp_path = os.path.join(output_dir, "temp_32.png")
    pix.save(temp_path)
    
    img = Image.open(temp_path)
    if img.size != (1950, 1350):
        img = img.resize((1950, 1350), Image.Resampling.LANCZOS)
    
    img.save(png_path, dpi=(300, 300), format="PNG")
    img.close()
    
    if os.path.exists(temp_path):
        os.remove(temp_path)
        
    print(f"Successfully generated simplified 300 DPI PNG at: {png_path}")

if __name__ == "__main__":
    main()
