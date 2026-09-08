"""
Generates Figure 3.3: AI Examination Routine Parsing & Fuzzy Course Matching Flow
Dimensions: Width: 6.0 in, Height: 3.5 in @ 300 DPI (1800 x 1050 px)
Light-mode, clean, publication-ready hybrid diagram:
- Left: 5-step operational pipeline workflow
- Right: High-fidelity UI screenshot mockup of AI Exam Routine Ingestion & Review
Outputs ONLY a single image: materials/Figure-3.3.png
"""
import os
import fitz  # PyMuPDF
from PIL import Image

def generate_svg():
    width = 1800
    height = 1050

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
    <defs>
        <marker id="arrPurple" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <polygon points="0,1 10,5 0,9" fill="#7C3AED" />
        </marker>
        <marker id="arrBlue" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <polygon points="0,1 10,5 0,9" fill="#2563EB" />
        </marker>
        <marker id="arrSlate" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <polygon points="0,1 10,5 0,9" fill="#64748B" />
        </marker>

        <style>
            .main-title {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 21px; font-weight: 800; fill: #0F172A; }}
            .main-subtitle {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 12.5px; font-weight: 600; fill: #475569; }}
            
            .section-header {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 12px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.8px; }}
            
            .step-num {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 14px; font-weight: 800; fill: #FFFFFF; text-anchor: middle; }}
            .step-title {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 13.5px; font-weight: 700; fill: #0F172A; }}
            .step-desc {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 11px; font-weight: 500; fill: #475569; }}
            .step-tech {{ font-family: 'Consolas', monospace; font-size: 9.5px; font-weight: 700; }}
            
            .ui-window-title {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 13px; font-weight: 700; fill: #1E293B; }}
            .ui-th {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 11px; font-weight: 700; fill: #475569; }}
            .ui-td-bold {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 11px; font-weight: 700; fill: #0F172A; }}
            .ui-td-regular {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 10.5px; font-weight: 500; fill: #334155; }}
            .ui-code {{ font-family: 'Consolas', monospace; font-size: 10px; font-weight: 700; }}
            .badge-text {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 9.5px; font-weight: 700; }}
            .footer-info {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 10.5px; font-weight: 500; fill: #64748B; }}
        </style>
    </defs>

    <!-- Canvas Background -->
    <rect width="{width}" height="{height}" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.5" />

    <!-- Top Title Block -->
    <g transform="translate(40, 18)">
        <rect x="0" y="0" width="5" height="42" rx="2" fill="#7C3AED" />
        <text x="16" y="21" class="main-title">Figure 3.3: AI Examination Routine Parsing &amp; Fuzzy Course Matching Flow</text>
        <text x="16" y="39" class="main-subtitle">Automated Ingestion Pipeline: 300 DPI Multi-Page Document OCR, Regex Metadata Extraction, 0ms Database Matching &amp; One-Click Creation</text>
    </g>

    <!-- ============================================================== -->
    <!-- LEFT PANEL: 5-STEP WORKFLOW PIPELINE (x: 40 to 760)             -->
    <!-- ============================================================== -->
    <g transform="translate(40, 72)">
        <!-- Container Box -->
        <rect width="715" height="935" rx="8" fill="#F8FAFC" stroke="#DDD6FE" stroke-width="1.5" />
        
        <!-- Header Strip -->
        <path d="M 0 8 Q 0 0 8 0 L 707 0 Q 715 0 715 8 L 715 34 L 0 34 Z" fill="#EDE9FE" />
        <line x1="0" y1="34" x2="715" y2="34" stroke="#DDD6FE" stroke-width="1" />
        <rect x="14" y="9" width="5" height="16" rx="2" fill="#7C3AED" />
        <text x="26" y="22" class="section-header" fill="#5B21B6">OPERATIONAL PARSING PIPELINE</text>
        <text x="240" y="21" font-family="'Segoe UI', Arial, sans-serif" font-size="11px" font-weight="600" fill="#6B21A8">— Sequential Processing &amp; Matching Engine</text>

        <!-- STEP 1: Multi-Page Document Ingestion -->
        <g transform="translate(20, 50)">
            <rect width="675" height="140" rx="6" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.2" />
            
            <!-- Step Circle Badge -->
            <circle cx="36" cy="40" r="18" fill="#7C3AED" />
            <text x="36" y="45" class="step-num">1</text>

            <g transform="translate(70, 26)">
                <text x="0" y="0" class="step-title">Multi-Page Schedule Ingestion &amp; Integrity Verification</text>
                <text x="0" y="22" class="step-desc">• Controller uploads semester routine schedule (Multi-page PDF or JPEG/PNG/WebP scan)</text>
                <text x="0" y="42" class="step-desc">• SHA-256 cryptographic payload fingerprinting &amp; request trace integrity verification</text>
            </g>

            <rect x="70" y="94" width="225" height="22" rx="4" fill="#F5F3FF" stroke="#DDD6FE" stroke-width="1" />
            <text x="78" y="109" class="step-tech" fill="#6D28D9">POST /controller/scan-routine-ai/</text>
            
            <rect x="305" y="94" width="165" height="22" rx="4" fill="#F8FAFC" stroke="#E2E8F0" stroke-width="1" />
            <text x="313" y="109" class="step-tech" fill="#475569">Multi-Page PDF / Scanned Image</text>
        </g>

        <!-- Down Arrow 1 -> 2 -->
        <path d="M 377 190 L 377 215" fill="none" stroke="#7C3AED" stroke-width="2.5" marker-end="url(#arrPurple)" />

        <!-- STEP 2: 300 DPI Normalization & Hybrid OCR -->
        <g transform="translate(20, 220)">
            <rect width="675" height="140" rx="6" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.2" />
            
            <circle cx="36" cy="40" r="18" fill="#7C3AED" />
            <text x="36" y="45" class="step-num">2</text>

            <g transform="translate(70, 26)">
                <text x="0" y="0" class="step-title">300 DPI Document Normalization &amp; Hybrid OCR</text>
                <text x="0" y="22" class="step-desc">• PyMuPDF renders pages at 300 DPI with anti-aliasing &amp; direct font-stream extraction</text>
                <text x="0" y="42" class="step-desc">• PyTesseract &amp; EasyOCR (PyTorch CPU) printed text line &amp; column OCR fallback</text>
            </g>

            <rect x="70" y="94" width="200" height="22" rx="4" fill="#F5F3FF" stroke="#DDD6FE" stroke-width="1" />
            <text x="78" y="109" class="step-tech" fill="#6D28D9">PyMuPDF 300 DPI + PyTesseract</text>

            <rect x="280" y="94" width="195" height="22" rx="4" fill="#F8FAFC" stroke="#E2E8F0" stroke-width="1" />
            <text x="288" y="109" class="step-tech" fill="#475569">Hough Deskewing + Otsu Threshold</text>
        </g>

        <!-- Down Arrow 2 -> 3 -->
        <path d="M 377 360 L 377 385" fill="none" stroke="#7C3AED" stroke-width="2.5" marker-end="url(#arrPurple)" />

        <!-- STEP 3: Regex State Machine & Schema Parsing -->
        <g transform="translate(20, 390)">
            <rect width="675" height="140" rx="6" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.2" />
            
            <circle cx="36" cy="40" r="18" fill="#7C3AED" />
            <text x="36" y="45" class="step-num">3</text>

            <g transform="translate(70, 26)">
                <text x="0" y="0" class="step-title">Regex State Machine &amp; Multi-Line Parser</text>
                <text x="0" y="22" class="step-desc">• Extracts structured schedule blocks: Date, Time Slot, Course Code, Section &amp; Room</text>
                <text x="0" y="42" class="step-desc">• clean_faculty_name() scrubs student headers, program metadata &amp; OCR artifact noise</text>
            </g>

            <rect x="70" y="94" width="220" height="22" rx="4" fill="#F5F3FF" stroke="#DDD6FE" stroke-width="1" />
            <text x="78" y="109" class="step-tech" fill="#6D28D9">Deterministic Regex State Machine</text>

            <rect x="300" y="94" width="170" height="22" rx="4" fill="#F8FAFC" stroke="#E2E8F0" stroke-width="1" />
            <text x="308" y="109" class="step-tech" fill="#475569">clean_faculty_name() Filter</text>
        </g>

        <!-- Down Arrow 3 -> 4 -->
        <path d="M 377 530 L 377 555" fill="none" stroke="#7C3AED" stroke-width="2.5" marker-end="url(#arrPurple)" />

        <!-- STEP 4: Local Fuzzy Course Code Matcher -->
        <g transform="translate(20, 560)">
            <rect width="675" height="140" rx="6" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.2" />
            
            <circle cx="36" cy="40" r="18" fill="#059669" />
            <text x="36" y="45" class="step-num">4</text>

            <g transform="translate(70, 26)">
                <text x="0" y="0" class="step-title">Local Fuzzy Course Matching (0ms Latency)</text>
                <text x="0" y="22" class="step-desc">• In-memory token-overlap matcher checks course codes against PostgreSQL Course DB</text>
                <text x="0" y="42" class="step-desc">• Fuzzy tolerance resolves spacing variations (e.g. "CSE 4383" vs "CSE4383") with 0ms delay</text>
            </g>

            <rect x="70" y="94" width="180" height="22" rx="4" fill="#ECFDF5" stroke="#A7F3D0" stroke-width="1" />
            <text x="78" y="109" class="step-tech" fill="#065F46">0ms In-Memory Token Matcher</text>

            <rect x="260" y="94" width="185" height="22" rx="4" fill="#F8FAFC" stroke="#E2E8F0" stroke-width="1" />
            <text x="268" y="109" class="step-tech" fill="#475569">Course.objects.filter(code__iregex)</text>
        </g>

        <!-- Down Arrow 4 -> 5 -->
        <path d="M 377 700 L 377 725" fill="none" stroke="#059669" stroke-width="2.5" marker-end="url(#arrEmerald)" />

        <!-- STEP 5: One-Click Examination Generation -->
        <g transform="translate(20, 730)">
            <rect width="675" height="140" rx="6" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.2" />
            
            <circle cx="36" cy="40" r="18" fill="#2563EB" />
            <text x="36" y="45" class="step-num">5</text>

            <g transform="translate(70, 26)">
                <text x="0" y="0" class="step-title">Interactive Review &amp; One-Click Bulk Creation</text>
                <text x="0" y="22" class="step-desc">• Controller verifies extracted rows, matched faculty examiners, dates, and time slots</text>
                <text x="0" y="42" class="step-desc">• Single-click creates all semester Examination database instances with assigned teachers</text>
            </g>

            <rect x="70" y="94" width="220" height="22" rx="4" fill="#EFF6FF" stroke="#BFDBFE" stroke-width="1" />
            <text x="78" y="109" class="step-tech" fill="#1E40AF">Bulk Examination Instance Factory</text>

            <rect x="300" y="94" width="165" height="22" rx="4" fill="#F8FAFC" stroke="#E2E8F0" stroke-width="1" />
            <text x="308" y="109" class="step-tech" fill="#475569">Atomic Transaction Commit</text>
        </g>
    </g>

    <!-- Transition Pipe from Pipeline to UI Screenshot -->
    <path d="M 755 540 L 785 540" fill="none" stroke="#7C3AED" stroke-width="3" stroke-dasharray="5 3" marker-end="url(#arrPurple)" />

    <!-- ============================================================== -->
    <!-- RIGHT PANEL: HIGH-FIDELITY UI SCREENSHOT MOCKUP (x: 785 to 1760) -->
    <!-- ============================================================== -->
    <g transform="translate(785, 72)">
        <!-- Browser / App Window Container -->
        <rect width="975" height="935" rx="10" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.5" />
        
        <!-- Window Title Bar -->
        <path d="M 0 10 Q 0 0 10 0 L 965 0 Q 975 0 975 10 L 975 42 L 0 42 Z" fill="#F1F5F9" />
        <line x1="0" y1="42" x2="975" y2="42" stroke="#CBD5E1" stroke-width="1" />
        
        <!-- Window Controls (Red, Yellow, Green dots) -->
        <circle cx="20" cy="21" r="5" fill="#EF4444" />
        <circle cx="36" cy="21" r="5" fill="#F59E0B" />
        <circle cx="52" cy="21" r="5" fill="#10B981" />

        <!-- Address Bar / App Header -->
        <rect x="75" y="10" width="480" height="22" rx="4" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="1" />
        <text x="88" y="25" font-family="'Consolas', monospace" font-size="10px" fill="#64748B">https://intelligrade.university.edu/dashboard/scan-routine-ai/</text>

        <!-- Active Status Badge -->
        <rect x="760" y="10" width="195" height="22" rx="11" fill="#ECFDF5" stroke="#A7F3D0" stroke-width="1" />
        <circle cx="774" cy="21" r="3.5" fill="#10B981" />
        <text x="784" y="25" class="badge-text" fill="#065F46">STATUS: COMPLETED (0ms)</text>

        <!-- UI Inner Canvas -->
        <!-- Banner Card -->
        <g transform="translate(24, 60)">
            <rect width="927" height="90" rx="8" fill="#F5F3FF" stroke="#DDD6FE" stroke-width="1.2" />
            
            <text x="20" y="32" font-family="'Segoe UI', Arial, sans-serif" font-size="16px" font-weight="800" fill="#5B21B6">AI Exam Routine Scanner &amp; Database Cross-Referencer</text>
            <text x="20" y="52" font-family="'Segoe UI', Arial, sans-serif" font-size="11.5px" font-weight="500" fill="#6B21A8">Upload complete semester PDF routine. PyMuPDF renders pages at 300 DPI, OCR parses schedules, and local matcher binds DB courses with zero latency.</text>
            
            <!-- Tags -->
            <rect x="20" y="62" width="165" height="18" rx="4" fill="#FFFFFF" stroke="#C4B5FD" stroke-width="0.8" />
            <text x="26" y="74" class="badge-text" fill="#6D28D9">✨ Active Provider: PyMuPDF + Gemini</text>

            <rect x="195" y="62" width="135" height="18" rx="4" fill="#FFFFFF" stroke="#C4B5FD" stroke-width="0.8" />
            <text x="201" y="74" class="badge-text" fill="#6D28D9">⚡ 0ms Fuzzy Token Match</text>

            <rect x="340" y="62" width="150" height="18" rx="4" fill="#FFFFFF" stroke="#C4B5FD" stroke-width="0.8" />
            <text x="346" y="74" class="badge-text" fill="#6D28D9">📄 Routine_Spring_2026.pdf</text>
        </g>

        <!-- Progress Banner -->
        <g transform="translate(24, 165)">
            <rect width="927" height="42" rx="6" fill="#F8FAFC" stroke="#E2E8F0" stroke-width="1" />
            <text x="16" y="25" font-family="'Segoe UI', Arial, sans-serif" font-size="11.5px" font-weight="700" fill="#0F172A">Parsing Progress: 100% Complete</text>
            <text x="230" y="25" font-family="'Segoe UI', Arial, sans-serif" font-size="11px" font-weight="500" fill="#059669">✅ Found 4 scheduled examination items. Cross-referencing institutional database records...</text>
            
            <!-- 100% Progress Bar -->
            <rect x="735" y="16" width="175" height="10" rx="5" fill="#E2E8F0" />
            <rect x="735" y="16" width="175" height="10" rx="5" fill="#10B981" />
        </g>

        <!-- Table Summary Header -->
        <g transform="translate(24, 225)">
            <text x="0" y="0" font-family="'Segoe UI', Arial, sans-serif" font-size="13px" font-weight="800" fill="#0F172A">Extracted Routine Courses, Assigned Examiners, Date &amp; Time Slot</text>
            <rect x="765" y="-12" width="162" height="20" rx="10" fill="#F5F3FF" stroke="#DDD6FE" stroke-width="1" />
            <text x="775" y="2" class="badge-text" fill="#6D28D9">4 Schedule Entries Found</text>
        </g>

        <!-- Interactive Schedule Table -->
        <g transform="translate(24, 250)">
            <!-- Table Box -->
            <rect width="927" height="570" rx="8" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="1.2" />
            
            <!-- Table Thead -->
            <path d="M 0 8 Q 0 0 8 0 L 919 0 Q 927 0 927 8 L 927 36 L 0 36 Z" fill="#F8FAFC" />
            <line x1="0" y1="36" x2="927" y2="36" stroke="#E2E8F0" stroke-width="1" />
            
            <text x="20" y="23" class="ui-th">Course Code &amp; Module Title</text>
            <text x="320" y="23" class="ui-th">Assigned Faculty Examiner</text>
            <text x="560" y="23" class="ui-th">Exam Date &amp; Time Slot</text>
            <text x="770" y="23" class="ui-th">Database Match Status</text>

            <!-- ROW 1: CSE 4383 -->
            <g transform="translate(0, 36)">
                <rect width="927" height="130" fill="#FFFFFF" />
                <line x1="0" y1="130" x2="927" y2="130" stroke="#F1F5F9" stroke-width="1" />

                <!-- Course -->
                <rect x="20" y="16" width="70" height="22" rx="4" fill="#F5F3FF" stroke="#DDD6FE" stroke-width="1" />
                <text x="26" y="31" class="ui-code" fill="#6D28D9">CSE 4383</text>
                <text x="100" y="31" class="ui-td-bold">Computer Graphics and Animation</text>
                <text x="20" y="58" font-family="'Segoe UI', Arial, sans-serif" font-size="10.5px" fill="#64748B">Department: Computer Science &amp; Engineering | Section: C</text>
                <text x="20" y="78" font-family="'Segoe UI', Arial, sans-serif" font-size="10px" fill="#059669">Total Marks: 100.00 | Room &amp; Seat: Room 402, Building A</text>

                <!-- Faculty -->
                <rect x="320" y="16" width="220" height="34" rx="6" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1" />
                <text x="332" y="32" class="ui-td-bold">Engr. Hijbullah Al Mahdi</text>
                <text x="332" y="45" font-family="'Segoe UI', Arial, sans-serif" font-size="9.5px" fill="#64748B">hijbullah (CSE Faculty) - Active</text>
                <text x="320" y="78" font-family="'Segoe UI', Arial, sans-serif" font-size="10px" fill="#7C3AED">Detected: "Engr. Hijbullah" ✓</text>

                <!-- Date & Time -->
                <text x="560" y="30" class="ui-td-bold">2026-05-17</text>
                <text x="560" y="48" class="ui-td-regular">09:00 AM - 12:00 PM</text>
                <text x="560" y="78" font-family="'Segoe UI', Arial, sans-serif" font-size="10px" fill="#64748B">Slot: Morning Session (3 hrs)</text>

                <!-- Match Badge -->
                <rect x="770" y="20" width="135" height="26" rx="13" fill="#ECFDF5" stroke="#A7F3D0" stroke-width="1" />
                <text x="782" y="37" class="badge-text" fill="#065F46">✓ 100% DB Matched</text>
                <text x="775" y="62" font-family="'Segoe UI', Arial, sans-serif" font-size="9.5px" fill="#059669">Course ID #104 linked</text>
            </g>

            <!-- ROW 2: CSE 4385 -->
            <g transform="translate(0, 166)">
                <rect width="927" height="130" fill="#FBFDFF" />
                <line x1="0" y1="130" x2="927" y2="130" stroke="#F1F5F9" stroke-width="1" />

                <rect x="20" y="16" width="70" height="22" rx="4" fill="#F5F3FF" stroke="#DDD6FE" stroke-width="1" />
                <text x="26" y="31" class="ui-code" fill="#6D28D9">CSE 4385</text>
                <text x="100" y="31" class="ui-td-bold">Artificial Intelligence &amp; Expert Systems</text>
                <text x="20" y="58" font-family="'Segoe UI', Arial, sans-serif" font-size="10.5px" fill="#64748B">Department: Computer Science &amp; Engineering | Section: A</text>
                <text x="20" y="78" font-family="'Segoe UI', Arial, sans-serif" font-size="10px" fill="#059669">Total Marks: 100.00 | Room &amp; Seat: Room 305, Building B</text>

                <rect x="320" y="16" width="220" height="34" rx="6" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1" />
                <text x="332" y="32" class="ui-td-bold">Dr. Tariq Ahmed</text>
                <text x="332" y="45" font-family="'Segoe UI', Arial, sans-serif" font-size="9.5px" fill="#64748B">tariq.ahmed (CSE Faculty)</text>
                <text x="320" y="78" font-family="'Segoe UI', Arial, sans-serif" font-size="10px" fill="#7C3AED">Detected: "Dr. Tariq" ✓</text>

                <text x="560" y="30" class="ui-td-bold">2026-05-19</text>
                <text x="560" y="48" class="ui-td-regular">01:30 PM - 04:30 PM</text>
                <text x="560" y="78" font-family="'Segoe UI', Arial, sans-serif" font-size="10px" fill="#64748B">Slot: Afternoon Session (3 hrs)</text>

                <rect x="770" y="20" width="135" height="26" rx="13" fill="#ECFDF5" stroke="#A7F3D0" stroke-width="1" />
                <text x="782" y="37" class="badge-text" fill="#065F46">✓ 100% DB Matched</text>
                <text x="775" y="62" font-family="'Segoe UI', Arial, sans-serif" font-size="9.5px" fill="#059669">Course ID #108 linked</text>
            </g>

            <!-- ROW 3: MAT 2101 -->
            <g transform="translate(0, 296)">
                <rect width="927" height="130" fill="#FFFFFF" />
                <line x1="0" y1="130" x2="927" y2="130" stroke="#F1F5F9" stroke-width="1" />

                <rect x="20" y="16" width="70" height="22" rx="4" fill="#F5F3FF" stroke="#DDD6FE" stroke-width="1" />
                <text x="26" y="31" class="ui-code" fill="#6D28D9">MAT 2101</text>
                <text x="100" y="31" class="ui-td-bold">Engineering Mathematics &amp; Calculus</text>
                <text x="20" y="58" font-family="'Segoe UI', Arial, sans-serif" font-size="10.5px" fill="#64748B">Department: Department of Mathematics | Section: B</text>
                <text x="20" y="78" font-family="'Segoe UI', Arial, sans-serif" font-size="10px" fill="#059669">Total Marks: 100.00 | Room &amp; Seat: Room 201, Building C</text>

                <rect x="320" y="16" width="220" height="34" rx="6" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1" />
                <text x="332" y="32" class="ui-td-bold">Prof. Shahriar Hossain</text>
                <text x="332" y="45" font-family="'Segoe UI', Arial, sans-serif" font-size="9.5px" fill="#64748B">shahriar.math (Faculty)</text>
                <text x="320" y="78" font-family="'Segoe UI', Arial, sans-serif" font-size="10px" fill="#7C3AED">Detected: "S. Hossain" ✓</text>

                <text x="560" y="30" class="ui-td-bold">2026-05-22</text>
                <text x="560" y="48" class="ui-td-regular">09:00 AM - 12:00 PM</text>
                <text x="560" y="78" font-family="'Segoe UI', Arial, sans-serif" font-size="10px" fill="#64748B">Slot: Morning Session (3 hrs)</text>

                <rect x="770" y="20" width="135" height="26" rx="13" fill="#F0FDFA" stroke="#99F6E4" stroke-width="1" />
                <text x="784" y="37" class="badge-text" fill="#0F766E">✓ Fuzzy Matched</text>
                <text x="775" y="62" font-family="'Segoe UI', Arial, sans-serif" font-size="9.5px" fill="#0D9488">Course ID #203 linked</text>
            </g>

            <!-- ROW 4: PHY 1101 -->
            <g transform="translate(0, 426)">
                <rect width="927" height="144" fill="#FBFDFF" />

                <rect x="20" y="16" width="70" height="22" rx="4" fill="#F5F3FF" stroke="#DDD6FE" stroke-width="1" />
                <text x="26" y="31" class="ui-code" fill="#6D28D9">PHY 1101</text>
                <text x="100" y="31" class="ui-td-bold">Physics for Engineers (Electromagnetism)</text>
                <text x="20" y="58" font-family="'Segoe UI', Arial, sans-serif" font-size="10.5px" fill="#64748B">Department: Department of Physics | Section: D</text>
                <text x="20" y="78" font-family="'Segoe UI', Arial, sans-serif" font-size="10px" fill="#059669">Total Marks: 100.00 | Room &amp; Seat: Room 102, Building A</text>

                <rect x="320" y="16" width="220" height="34" rx="6" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1" />
                <text x="332" y="32" class="ui-td-bold">Dr. K. Rahman</text>
                <text x="332" y="45" font-family="'Segoe UI', Arial, sans-serif" font-size="9.5px" fill="#64748B">k.rahman (Physics Faculty)</text>
                <text x="320" y="78" font-family="'Segoe UI', Arial, sans-serif" font-size="10px" fill="#7C3AED">Detected: "Dr. K. Rahman" ✓</text>

                <text x="560" y="30" class="ui-td-bold">2026-05-25</text>
                <text x="560" y="48" class="ui-td-regular">01:30 PM - 04:30 PM</text>
                <text x="560" y="78" font-family="'Segoe UI', Arial, sans-serif" font-size="10px" fill="#64748B">Slot: Afternoon Session (3 hrs)</text>

                <rect x="770" y="20" width="135" height="26" rx="13" fill="#ECFDF5" stroke="#A7F3D0" stroke-width="1" />
                <text x="782" y="37" class="badge-text" fill="#065F46">✓ 100% DB Matched</text>
                <text x="775" y="62" font-family="'Segoe UI', Arial, sans-serif" font-size="9.5px" fill="#059669">Course ID #305 linked</text>
            </g>
        </g>

        <!-- Bottom Action CTA Bar -->
        <g transform="translate(24, 835)">
            <rect width="927" height="60" rx="8" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1" />
            
            <text x="20" y="35" font-family="'Segoe UI', Arial, sans-serif" font-size="12px" font-weight="600" fill="#475569">Review complete. Ready to schedule 4 examinations in Spring 2026 academic semester.</text>

            <!-- Secondary Button -->
            <rect x="580" y="14" width="150" height="32" rx="6" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1" />
            <text x="600" y="34" font-family="'Segoe UI', Arial, sans-serif" font-size="11px" font-weight="700" fill="#475569">Scan Another Routine</text>

            <!-- Primary Glowing Button -->
            <rect x="740" y="14" width="172" height="32" rx="6" fill="#7C3AED" />
            <text x="752" y="34" font-family="'Segoe UI', Arial, sans-serif" font-size="11.5px" font-weight="800" fill="#FFFFFF">+ Create All 4 Exams</text>
        </g>
    </g>

    <!-- Bottom Metadata Bar -->
    <g transform="translate(40, 1030)">
        <text x="0" y="0" class="footer-info">IntelliGrade Examination Management Suite — Figure 3.3: AI Routine Parser &amp; 0ms Local Course Matcher</text>
        <text x="1720" y="0" class="footer-info" text-anchor="end">Target Dimensions: 6.0" × 3.5" (300 DPI, 1800 × 1050 px) | Pure Light Mode | Publication-Ready</text>
    </g>
</svg>
"""
    return svg

def main():
    output_dir = r"F:\Hijbullah\IntelliGrade\materials"
    os.makedirs(output_dir, exist_ok=True)
    
    svg_content = generate_svg()
    
    # Save single image file: Figure-3.3.png
    doc = fitz.open(stream=svg_content.encode("utf-8"), filetype="svg")
    page = doc[0]
    pix = page.get_pixmap(matrix=fitz.Matrix(1, 1), alpha=False)
    
    png_filename = "Figure-3.3.png"
    png_path = os.path.join(output_dir, png_filename)
    
    temp_path = os.path.join(output_dir, "temp_33.png")
    pix.save(temp_path)
    
    img = Image.open(temp_path)
    if img.size != (1800, 1050):
        img = img.resize((1800, 1050), Image.Resampling.LANCZOS)
    
    img.save(png_path, dpi=(300, 300), format="PNG")
    img.close()
    
    if os.path.exists(temp_path):
        os.remove(temp_path)
        
    print(f"Successfully generated single 300 DPI PNG at: {png_path}")

if __name__ == "__main__":
    main()
