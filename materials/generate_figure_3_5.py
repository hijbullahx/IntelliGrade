"""
Generates Figure 3.5: Hybrid Multi-Engine Optical Character Recognition (OCR) Cascade
Dimensions: Width: 6.0 in, Height: 3.2 in @ 300 DPI (1800 x 960 px)
Light-mode, clean, publication-ready decision tree flowchart:
- Left: Document Ingestion & 2-Stage Decision Gates + Benchmark Comparison Matrix
- Center: 3-Tier Engines (PyMuPDF -> PyTesseract -> EasyOCR) with Fallback Gate
- Right: Noise Filtering & PostScript Sanitizer -> Standardized OCR Result & Spatial Cache
Outputs ONLY a single image: materials/Figure-3.5.png
"""
import os
import fitz  # PyMuPDF
from PIL import Image

def generate_svg():
    width = 1800
    height = 960

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
    <defs>
        <!-- Arrowhead Markers -->
        <marker id="arrSlate" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <polygon points="0,1 10,5 0,9" fill="#475569" />
        </marker>
        <marker id="arrGreen" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <polygon points="0,1 10,5 0,9" fill="#15803D" />
        </marker>
        <marker id="arrBlue" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <polygon points="0,1 10,5 0,9" fill="#2563EB" />
        </marker>
        <marker id="arrOrange" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <polygon points="0,1 10,5 0,9" fill="#D97706" />
        </marker>
        <marker id="arrPurple" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <polygon points="0,1 10,5 0,9" fill="#7C3AED" />
        </marker>

        <style>
            .main-title {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 20px; font-weight: 800; fill: #0F172A; }}
            .main-subtitle {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 12px; font-weight: 600; fill: #475569; }}
            
            .card-title {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 13.5px; font-weight: 700; fill: #FFFFFF; }}
            .gate-title {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 13px; font-weight: 800; }}
            
            .node-title {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 12.5px; font-weight: 700; fill: #0F172A; }}
            .node-desc {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 11px; font-weight: 500; fill: #475569; }}
            .node-code {{ font-family: 'Consolas', monospace; font-size: 10px; font-weight: 700; }}
            
            .branch-label {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 10.5px; font-weight: 700; }}
            .metric-pill-text {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 9.5px; font-weight: 700; }}
            
            .tbl-th {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 10.5px; font-weight: 700; fill: #1E293B; }}
            .tbl-td {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 10px; font-weight: 500; fill: #334155; }}
            
            .footer-info {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 10px; font-weight: 500; fill: #64748B; }}
        </style>
    </defs>

    <!-- Canvas Background -->
    <rect width="{width}" height="{height}" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.5" />

    <!-- Top Diagram Header Block -->
    <g transform="translate(45, 18)">
        <rect x="0" y="0" width="5" height="42" rx="2" fill="#2563EB" />
        <text x="16" y="21" class="main-title">Figure 3.5: Hybrid Multi-Engine Optical Character Recognition (OCR) Cascade</text>
        <text x="16" y="39" class="main-subtitle">Decision Logic &amp; Fallback Cascade: PyMuPDF Native Extraction → PyTesseract Printed OCR → EasyOCR Deep Learning (CRAFT + BiLSTM)</text>
    </g>

    <!-- ============================================================== -->
    <!-- FLOW CONNECTORS & ROUTING WIRES (Segmented around pills)       -->
    <!-- ============================================================== -->

    <!-- 1. Document Ingestion -> Decision Gate 1 -->
    <path d="M 265 195 L 318 195" fill="none" stroke="#64748B" stroke-width="2" marker-end="url(#arrSlate)" />

    <!-- 2. Decision Gate 1 [YES] -> Tier 1 PyMuPDF -->
    <!-- Segment 1: Gate 1 to Pill -->
    <path d="M 520 180 L 610 180" fill="none" stroke="#15803D" stroke-width="2.5" />
    <!-- Branch Pill [YES] -->
    <g transform="translate(610, 168)">
        <rect width="115" height="24" rx="5" fill="#DCFCE7" stroke="#86EFAC" stroke-width="1.2" />
        <text x="57.5" y="16" text-anchor="middle" class="branch-label" fill="#15803D">YES (Glyphs)</text>
    </g>
    <!-- Segment 2: Pill to Tier 1 -->
    <path d="M 725 180 L 838 180" fill="none" stroke="#15803D" stroke-width="2.5" marker-end="url(#arrGreen)" />

    <!-- 3. Decision Gate 1 [NO / Scanned] -> Decision Gate 2 -->
    <!-- Segment 1: Gate 1 bottom to Pill -->
    <path d="M 420 280 L 420 318" fill="none" stroke="#475569" stroke-width="2.5" />
    <!-- Branch Pill [NO] -->
    <g transform="translate(340, 318)">
        <rect width="160" height="24" rx="5" fill="#F1F5F9" stroke="#CBD5E1" stroke-width="1.2" />
        <text x="80" y="16" text-anchor="middle" class="branch-label" fill="#475569">NO / Scanned Image</text>
    </g>
    <!-- Segment 2: Pill to Gate 2 top -->
    <path d="M 420 342 L 420 373" fill="none" stroke="#475569" stroke-width="2.5" marker-end="url(#arrSlate)" />

    <!-- 4. Decision Gate 2 [YES (Printed)] -> Tier 2 PyTesseract -->
    <!-- Segment 1: Gate 2 right to Pill -->
    <path d="M 520 445 L 595 445" fill="none" stroke="#2563EB" stroke-width="2.5" />
    <!-- Branch Pill [YES Printed] -->
    <g transform="translate(595, 433)">
        <rect width="140" height="24" rx="5" fill="#EFF6FF" stroke="#93C5FD" stroke-width="1.2" />
        <text x="70" y="16" text-anchor="middle" class="branch-label" fill="#1D4ED8">YES (Printed Text)</text>
    </g>
    <!-- Segment 2: Pill to Tier 2 -->
    <path d="M 735 445 L 785 445 L 785 425 L 838 425" fill="none" stroke="#2563EB" stroke-width="2.5" marker-end="url(#arrBlue)" />

    <!-- 5. Decision Gate 2 [NO (Handwritten)] -> Tier 3 EasyOCR (Circumnavigating table) -->
    <!-- Segment 1: Gate 2 bottom to Pill at y=555 -->
    <path d="M 420 535 L 420 555 L 525 555" fill="none" stroke="#7C3AED" stroke-width="2.5" />
    <!-- Branch Pill [NO Handwritten] -->
    <g transform="translate(525, 543)">
        <rect width="180" height="24" rx="5" fill="#F5F3FF" stroke="#C4B5FD" stroke-width="1.2" />
        <text x="90" y="16" text-anchor="middle" class="branch-label" fill="#6D28D9">NO (Handwritten Script)</text>
    </g>
    <!-- Segment 2: Pill around table edge to Tier 3 -->
    <path d="M 705 555 L 805 555 L 805 700 L 838 700" fill="none" stroke="#7C3AED" stroke-width="2.5" marker-end="url(#arrPurple)" />

    <!-- 6. Fallback from Tier 2 to Tier 3 if Confidence < 0.75 -->
    <!-- Segment 1: Tier 2 bottom to Fallback Pill -->
    <path d="M 1060 515 L 1060 540" fill="none" stroke="#D97706" stroke-width="2" stroke-dasharray="5 3" />
    <g transform="translate(980, 540)">
        <rect width="160" height="22" rx="4" fill="#FFFBEB" stroke="#FDE68A" stroke-width="1" />
        <text x="80" y="15" text-anchor="middle" class="branch-label" fill="#B45309">Fallback: Conf &lt; 0.75</text>
    </g>
    <!-- Segment 2: Fallback Pill to Tier 3 top -->
    <path d="M 1060 562 L 1060 588" fill="none" stroke="#D97706" stroke-width="2" stroke-dasharray="5 3" marker-end="url(#arrOrange)" />

    <!-- 7. Engine Outputs into Noise Filtering & PostScript Sanitizer -->
    <!-- Tier 1 -> Sanitizer -->
    <path d="M 1280 195 L 1315 195 L 1315 285 L 1348 285" fill="none" stroke="#15803D" stroke-width="2" marker-end="url(#arrGreen)" />
    <!-- Tier 2 -> Sanitizer -->
    <path d="M 1280 425 L 1315 425 L 1315 330 L 1348 330" fill="none" stroke="#2563EB" stroke-width="2" marker-end="url(#arrBlue)" />
    <!-- Tier 3 -> Sanitizer -->
    <path d="M 1280 700 L 1315 700 L 1315 375 L 1348 375" fill="none" stroke="#7C3AED" stroke-width="2" marker-end="url(#arrPurple)" />

    <!-- 8. Sanitizer -> Standardized OCR Result & Storage -->
    <path d="M 1552 435 L 1552 518" fill="none" stroke="#0284C7" stroke-width="2.5" marker-end="url(#arrBlue)" />

    <!-- ============================================================== -->
    <!-- COLUMN 1: DOCUMENT INGESTION (x: 45, y: 105, w: 220)           -->
    <!-- ============================================================== -->
    <g transform="translate(45, 105)">
        <rect width="220" height="185" rx="8" fill="#F8FAFC" stroke="#94A3B8" stroke-width="1.3" />
        <rect width="220" height="34" rx="8" fill="#475569" />
        <rect y="26" width="220" height="8" fill="#475569" />
        <text x="14" y="23" class="card-title">Document Ingestion</text>

        <g transform="translate(14, 50)">
            <text x="0" y="0" class="node-title">300 DPI Preprocessed Input</text>
            <text x="0" y="19" class="node-desc">• Normalized working copy</text>
            <text x="0" y="36" class="node-desc">• Deskewed to ± 0.05°</text>
            <text x="0" y="53" class="node-desc">• Otsu shadow-free matrix</text>
            <text x="0" y="70" class="node-desc">• Byte stream or PDF file</text>
        </g>
        
        <rect x="14" y="146" width="192" height="24" rx="4" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1" />
        <text x="20" y="162" class="node-code" fill="#334155">media/submission_working/</text>
    </g>

    <!-- ============================================================== -->
    <!-- DECISION 1: Embedded Digital Font Glyphs? (x: 320, y: 115)     -->
    <!-- ============================================================== -->
    <g transform="translate(320, 115)">
        <rect width="200" height="165" rx="8" fill="#F0FDF4" stroke="#86EFAC" stroke-width="1.5" />
        <rect width="200" height="34" rx="8" fill="#16A34A" />
        <rect y="26" width="200" height="8" fill="#16A34A" />
        <text x="12" y="22" font-family="'Segoe UI', Arial, sans-serif" font-size="12px" font-weight="700" fill="#FFFFFF">Decision Gate 1</text>

        <g transform="translate(14, 48)">
            <text x="0" y="12" class="gate-title" fill="#14532D">Embedded Digital</text>
            <text x="0" y="30" class="gate-title" fill="#14532D">Font Glyphs?</text>

            <text x="0" y="52" class="node-desc">Checks if PDF contains</text>
            <text x="0" y="68" class="node-desc">direct text streams</text>
            <text x="0" y="84" class="node-desc">(len &gt; 30 chars &amp; non-scan)</text>
        </g>

        <rect x="14" y="136" width="172" height="18" rx="3" fill="#DCFCE7" stroke="#BBF7D0" stroke-width="0.8" />
        <text x="20" y="149" class="node-code" fill="#15803D">page.get_text("text")</text>
    </g>

    <!-- ============================================================== -->
    <!-- DECISION 2: Printed Typography vs Handwriting? (x: 320, y: 375) -->
    <!-- ============================================================== -->
    <g transform="translate(320, 375)">
        <rect width="200" height="160" rx="8" fill="#EFF6FF" stroke="#93C5FD" stroke-width="1.5" />
        <rect width="200" height="34" rx="8" fill="#2563EB" />
        <rect y="26" width="200" height="8" fill="#2563EB" />
        <text x="12" y="22" font-family="'Segoe UI', Arial, sans-serif" font-size="12px" font-weight="700" fill="#FFFFFF">Decision Gate 2</text>

        <g transform="translate(14, 48)">
            <text x="0" y="12" class="gate-title" fill="#1E3A8A">Printed Layout</text>
            <text x="0" y="30" class="gate-title" fill="#1E3A8A">vs. Handwriting?</text>

            <text x="0" y="52" class="node-desc">Document classification:</text>
            <text x="0" y="68" class="node-desc">Question Paper / Routine vs.</text>
            <text x="0" y="84" class="node-desc">Student Answer Script</text>
        </g>

        <rect x="14" y="132" width="172" height="18" rx="3" fill="#DBEAFE" stroke="#BFDBFE" stroke-width="0.8" />
        <text x="18" y="145" class="node-code" fill="#1D4ED8">AIConfiguration.OCREngine</text>
    </g>

    <!-- ============================================================== -->
    <!-- CENTER COLUMN: 3-TIER OCR ENGINES (x: 840 to 1280, w: 440)     -->
    <!-- ============================================================== -->

    <!-- TIER 1: PyMuPDF Native Glyph Extraction (y: 105, h: 180) -->
    <g transform="translate(840, 105)">
        <rect width="440" height="180" rx="8" fill="#FFFFFF" stroke="#16A34A" stroke-width="1.5" />
        <rect width="440" height="36" rx="8" fill="#16A34A" />
        <rect y="28" width="440" height="8" fill="#16A34A" />
        <text x="16" y="24" class="card-title">Tier 1: PyMuPDF Native Extractor</text>

        <!-- Metric Badges -->
        <g transform="translate(285, 8)">
            <rect width="68" height="20" rx="4" fill="#DCFCE7" />
            <text x="34" y="14" text-anchor="middle" class="metric-pill-text" fill="#15803D">&lt; 5 ms</text>
        </g>
        <g transform="translate(360, 8)">
            <rect width="68" height="20" rx="4" fill="#DCFCE7" />
            <text x="34" y="14" text-anchor="middle" class="metric-pill-text" fill="#15803D">100% Glyph</text>
        </g>

        <g transform="translate(16, 50)">
            <text x="0" y="10" class="node-title">Native PDF Vector Font Stream Parser</text>
            <text x="0" y="30" class="node-desc">• Instant extraction from embedded TrueType / Type 3 glyphs</text>
            <text x="0" y="48" class="node-desc">• Extracts exact font metrics, line positions &amp; embedded images</text>
            <text x="0" y="66" class="node-desc">• Zero CPU OCR overhead — direct memory byte-stream decode</text>
            <text x="0" y="86" class="node-code" fill="#16A34A">fitz.open(stream=pdf_bytes) → page.get_text("text")</text>
        </g>
    </g>

    <!-- TIER 2: PyTesseract Printed OCR (y: 335, h: 180) -->
    <g transform="translate(840, 335)">
        <rect width="440" height="180" rx="8" fill="#FFFFFF" stroke="#2563EB" stroke-width="1.5" />
        <rect width="440" height="36" rx="8" fill="#2563EB" />
        <rect y="28" width="440" height="8" fill="#2563EB" />
        <text x="16" y="24" class="card-title">Tier 2: PyTesseract v5.3 OCR</text>

        <g transform="translate(285, 8)">
            <rect width="68" height="20" rx="4" fill="#EFF6FF" />
            <text x="34" y="14" text-anchor="middle" class="metric-pill-text" fill="#1D4ED8">0.8s / Page</text>
        </g>
        <g transform="translate(360, 8)">
            <rect width="68" height="20" rx="4" fill="#EFF6FF" />
            <text x="34" y="14" text-anchor="middle" class="metric-pill-text" fill="#1D4ED8">&gt; 90% Conf</text>
        </g>

        <g transform="translate(16, 50)">
            <text x="0" y="10" class="node-title">Printed Layout &amp; Tabular Schedule Recognizer</text>
            <text x="0" y="30" class="node-desc">• Optimized for printed question papers, cover sheets &amp; routines</text>
            <text x="0" y="48" class="node-desc">• Page Segmentation Modes (PSM 3 fully automatic, PSM 6 block)</text>
            <text x="0" y="66" class="node-desc">• LSTM optical recognition engine with dictionary whitelisting</text>
            <text x="0" y="86" class="node-code" fill="#2563EB">pytesseract.image_to_string(img, config='--oem 1 --psm 3')</text>
        </g>
    </g>

    <!-- TIER 3: EasyOCR Deep Learning Sequence Recognition (y: 590, h: 220) -->
    <g transform="translate(840, 590)">
        <rect width="440" height="220" rx="8" fill="#FFFFFF" stroke="#7C3AED" stroke-width="1.5" />
        <rect width="440" height="36" rx="8" fill="#7C3AED" />
        <rect y="28" width="440" height="8" fill="#7C3AED" />
        <text x="16" y="24" class="card-title">Tier 3: EasyOCR Deep Learning</text>

        <g transform="translate(270, 8)">
            <rect width="76" height="20" rx="4" fill="#F5F3FF" />
            <text x="38" y="14" text-anchor="middle" class="metric-pill-text" fill="#6D28D9">PyTorch CPU</text>
        </g>
        <g transform="translate(352, 8)">
            <rect width="76" height="20" rx="4" fill="#F5F3FF" />
            <text x="38" y="14" text-anchor="middle" class="metric-pill-text" fill="#6D28D9">CRAFT+LSTM</text>
        </g>

        <g transform="translate(16, 50)">
            <text x="0" y="10" class="node-title">Cursive &amp; Student Handwriting Transcriber</text>
            <text x="0" y="30" class="node-desc">• CRAFT CNN detects individual character regions &amp; affinities</text>
            <text x="0" y="48" class="node-desc">• Deep Bidirectional LSTM recognizes sequential cursive strokes</text>
            <text x="0" y="66" class="node-desc">• Generates line &amp; word-level bounding boxes [ymin, xmin, ymax, xmax]</text>
            <text x="0" y="84" class="node-desc">• Multi-language support (English, Mathematical symbols, Bengali)</text>
            <text x="0" y="104" class="node-code" fill="#7C3AED">reader.readtext(working_image) → [bbox, text, conf]</text>
        </g>
    </g>

    <!-- ============================================================== -->
    <!-- RIGHT COLUMN: SANITIZER & FINAL OUTPUT (x: 1350 to 1755, w: 405) -->
    <!-- ============================================================== -->

    <!-- Noise Filtering & Skia PostScript Sanitizer (y: 235, h: 200) -->
    <g transform="translate(1350, 235)">
        <rect width="405" height="200" rx="8" fill="#FFF7ED" stroke="#FDBA74" stroke-width="1.5" />
        <rect width="405" height="36" rx="8" fill="#EA580C" />
        <rect y="28" width="405" height="8" fill="#EA580C" />
        <text x="16" y="24" class="card-title">Noise Filtering &amp; Skia Purge</text>

        <g transform="translate(305, 8)">
            <rect width="85" height="20" rx="4" fill="#FFEDD5" />
            <text x="42.5" y="14" text-anchor="middle" class="metric-pill-text" fill="#C2410C">Regex Filter</text>
        </g>

        <g transform="translate(16, 52)">
            <text x="0" y="10" class="node-title">Virtual Printer Artifact Purge Engine</text>
            <text x="0" y="30" class="node-desc">• Purges virtual PDF printer glyphs: <tspan font-family="monospace" font-weight="700">node000123</tspan></text>
            <text x="0" y="48" class="node-desc">• Strips raw PostScript font strings &amp; Skia driver metadata</text>
            <text x="0" y="66" class="node-desc">• Eliminates orphan PDF object references: <tspan font-family="monospace" font-weight="700">r'^\\d+\\s+\\d+\\s+R$'</tspan></text>
            <text x="0" y="84" class="node-desc">• Canonicalizes whitespace, line breaks &amp; hyphenation</text>
            <text x="0" y="104" class="node-code" fill="#EA580C">re.search(r'node\\d{{6,}}', s) | 'Skia/PDF'</text>
        </g>
    </g>

    <!-- Final Output & Bounding Box Cache (y: 520, h: 290) -->
    <g transform="translate(1350, 520)">
        <rect width="405" height="290" rx="8" fill="#F0F9FF" stroke="#7DD3FC" stroke-width="1.5" />
        <rect width="405" height="36" rx="8" fill="#0284C7" />
        <rect y="28" width="405" height="8" fill="#0284C7" />
        <text x="16" y="24" class="card-title">Standardized OCR Output &amp; Cache</text>

        <g transform="translate(288, 8)">
            <rect width="104" height="20" rx="4" fill="#E0F2FE" />
            <text x="52" y="14" text-anchor="middle" class="metric-pill-text" fill="#0369A1">Structured JSON</text>
        </g>

        <g transform="translate(16, 52)">
            <text x="0" y="10" class="node-title">Verified Text Stream &amp; Spatial Metadata</text>
            <text x="0" y="30" class="node-desc">• Clean raw text payload delivered to TaskRouter</text>
            <text x="0" y="48" class="node-desc">• Word &amp; line bounding boxes for split-screen canvas</text>
            <text x="0" y="66" class="node-desc">• Normalized coordinates [ymin, xmin, ymax, xmax] ∈ [0.0, 1.0]</text>
            <text x="0" y="84" class="node-desc">• Composite confidence rating attached to SubmissionPage</text>

            <rect x="0" y="105" width="373" height="52" rx="4" fill="#FFFFFF" stroke="#BAE6FD" stroke-width="1" />
            <text x="12" y="125" class="node-code" fill="#0369A1">OCRResult (engine_name, raw_text, page_conf)</text>
            <text x="12" y="143" class="node-code" fill="#0369A1">SubmissionPage.word_boxes_json &amp; line_boxes</text>

            <rect x="0" y="170" width="373" height="26" rx="4" fill="#E0F2FE" stroke="#7DD3FC" stroke-width="1" />
            <text x="12" y="187" class="node-code" fill="#0284C7">Ready for Question Detection &amp; Dual AI Wizard</text>
        </g>
    </g>

    <!-- ============================================================== -->
    <!-- LOWER-LEFT PANEL: BENCHMARK MATRIX (x: 45, y: 600, w: 745)     -->
    <!-- ============================================================== -->
    <g transform="translate(45, 600)">
        <rect width="745" height="205" rx="8" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1.3" />
        
        <rect width="745" height="30" rx="8" fill="#F1F5F9" />
        <rect y="22" width="745" height="8" fill="#F1F5F9" />
        <line x1="0" y1="30" x2="745" y2="30" stroke="#CBD5E1" stroke-width="1" />
        <text x="14" y="20" font-family="'Segoe UI', Arial, sans-serif" font-size="11.5px" font-weight="700" fill="#1E293B">OCR ENGINE PERFORMANCE &amp; SELECTION BENCHMARK MATRIX</text>

        <g transform="translate(14, 45)">
            <!-- Table Header -->
            <rect width="717" height="24" rx="4" fill="#E2E8F0" />
            <text x="12" y="16" class="tbl-th">OCR Engine Tier</text>
            <text x="165" y="16" class="tbl-th">Target Document Type</text>
            <text x="375" y="16" class="tbl-th">Latency / Speed</text>
            <text x="485" y="16" class="tbl-th">Accuracy Metric</text>
            <text x="610" y="16" class="tbl-th">Failover Trigger</text>

            <!-- Row 1: PyMuPDF -->
            <g transform="translate(0, 28)">
                <rect width="717" height="28" fill="#FFFFFF" />
                <line x1="0" y1="28" x2="717" y2="28" stroke="#F1F5F9" stroke-width="1" />
                <text x="12" y="18" class="tbl-td" font-weight="700" fill="#16A34A">Tier 1: PyMuPDF (fitz)</text>
                <text x="165" y="18" class="tbl-td">Digital Vector PDF (Embedded Fonts)</text>
                <text x="375" y="18" class="tbl-td" font-family="monospace">&lt; 5 ms / page</text>
                <text x="485" y="18" class="tbl-td" font-weight="700" fill="#16A34A">100% Glyph Precision</text>
                <text x="610" y="18" class="tbl-td">Scanned PDF / No Text</text>
            </g>

            <!-- Row 2: PyTesseract -->
            <g transform="translate(0, 58)">
                <rect width="717" height="28" fill="#F8FAFC" />
                <line x1="0" y1="28" x2="717" y2="28" stroke="#F1F5F9" stroke-width="1" />
                <text x="12" y="18" class="tbl-td" font-weight="700" fill="#2563EB">Tier 2: PyTesseract v5.3</text>
                <text x="165" y="18" class="tbl-td">Printed Question Papers &amp; Routines</text>
                <text x="375" y="18" class="tbl-td" font-family="monospace">0.8 s / page</text>
                <text x="485" y="18" class="tbl-td" font-weight="700" fill="#2563EB">&gt; 90% Confidence</text>
                <text x="610" y="18" class="tbl-td">Confidence &lt; 0.75</text>
            </g>

            <!-- Row 3: EasyOCR -->
            <g transform="translate(0, 88)">
                <rect width="717" height="28" fill="#FFFFFF" />
                <text x="12" y="18" class="tbl-td" font-weight="700" fill="#7C3AED">Tier 3: EasyOCR (PyTorch)</text>
                <text x="165" y="18" class="tbl-td">Handwritten Student Answer Scripts</text>
                <text x="375" y="18" class="tbl-td" font-family="monospace">2.1 s / page</text>
                <text x="485" y="18" class="tbl-td" font-weight="700" fill="#7C3AED">85–94% Cursive Match</text>
                <text x="610" y="18" class="tbl-td">Cloud Vision Fallback</text>
            </g>
        </g>
    </g>

    <!-- Bottom Metadata Bar -->
    <g transform="translate(45, 938)">
        <text x="0" y="0" class="footer-info">IntelliGrade Computer Vision Core — Figure 3.5: Hybrid Multi-Engine OCR Cascade Architecture</text>
        <text x="1710" y="0" text-anchor="end" class="footer-info">Target Dimensions: 6.0" × 3.2" (300 DPI, 1800 × 960 px) | Pure Light Mode | Publication-Ready</text>
    </g>
</svg>
"""
    return svg

def main():
    output_dir = r"F:\Hijbullah\IntelliGrade\materials"
    os.makedirs(output_dir, exist_ok=True)
    
    svg_content = generate_svg()
    
    # Save single image file: Figure-3.5.png
    doc = fitz.open(stream=svg_content.encode("utf-8"), filetype="svg")
    page = doc[0]
    pix = page.get_pixmap(matrix=fitz.Matrix(1, 1), alpha=False)
    
    png_filename = "Figure-3.5.png"
    png_path = os.path.join(output_dir, png_filename)
    
    temp_path = os.path.join(output_dir, "temp_35.png")
    pix.save(temp_path)
    
    img = Image.open(temp_path)
    if img.size != (1800, 960):
        img = img.resize((1800, 960), Image.Resampling.LANCZOS)
    
    img.save(png_path, dpi=(300, 300), format="PNG")
    img.close()
    
    if os.path.exists(temp_path):
        os.remove(temp_path)
        
    print(f"Successfully generated single 300 DPI PNG at: {png_path}")

if __name__ == "__main__":
    main()
