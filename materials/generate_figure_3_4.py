"""
Generates Figure 3.4: 300 DPI Document Preprocessing, Deskewing and Normalization Pipeline
Dimensions: Width: 6.0 in, Height: 3.2 in @ 300 DPI (1800 x 960 px)
Light-mode, clean, visually engaging, publication-ready computer vision pipeline diagram.
Outputs ONLY a single image: materials/Figure-3.4.png
"""
import os
import fitz  # PyMuPDF
from PIL import Image

def generate_svg():
    width = 1800
    height = 960

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
    <defs>
        <marker id="arrStage" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <polygon points="0,1 10,5 0,9" fill="#2563EB" />
        </marker>
        <marker id="arrPurple" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <polygon points="0,1 10,5 0,9" fill="#7C3AED" />
        </marker>
        <marker id="arrEmerald" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <polygon points="0,1 10,5 0,9" fill="#059669" />
        </marker>
        <marker id="arrSky" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <polygon points="0,1 10,5 0,9" fill="#0284C7" />
        </marker>

        <style>
            .main-title {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 21px; font-weight: 800; fill: #0F172A; }}
            .main-subtitle {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 12.5px; font-weight: 600; fill: #475569; }}
            
            .stage-badge {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 10px; font-weight: 800; letter-spacing: 0.8px; text-transform: uppercase; fill: #FFFFFF; }}
            .stage-title {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 14.5px; font-weight: 700; fill: #0F172A; }}
            .stage-subtitle {{ font-family: 'Consolas', monospace; font-size: 10px; font-weight: 600; }}
            
            .param-bold {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 11px; font-weight: 700; fill: #1E293B; }}
            .param-desc {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 10.5px; font-weight: 500; fill: #475569; }}
            .param-code {{ font-family: 'Consolas', monospace; font-size: 9.5px; font-weight: 700; }}
            
            .canvas-label {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 9.5px; font-weight: 700; }}
            .code-tag {{ font-family: 'Consolas', monospace; font-size: 9px; font-weight: 700; }}
            
            .flow-tag {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 9px; font-weight: 700; fill: #1E40AF; text-anchor: middle; }}
            .footer-text {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 10.5px; font-weight: 500; fill: #64748B; }}
        </style>
    </defs>

    <!-- Background Canvas -->
    <rect width="{width}" height="{height}" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.5" />

    <!-- Top Diagram Header Block -->
    <g transform="translate(42, 18)">
        <rect x="0" y="0" width="5" height="42" rx="2" fill="#059669" />
        <text x="16" y="21" class="main-title">Figure 3.4: 300 DPI Document Preprocessing, Deskewing and Normalization Pipeline</text>
        <text x="16" y="39" class="main-subtitle">Computer Vision Normalization: Raw Capture Ingestion, PyMuPDF 300 DPI Rasterization, Hough Deskew, Otsu Binarization &amp; Unit Coordinates</text>
    </g>

    <!-- ============================================================== -->
    <!-- 5 HORIZONTAL STAGE CARDS                                       -->
    <!-- Card Width: 315px, Gap: 35px. Total: 5*315 + 4*35 = 1715px     -->
    <!-- Start X: 42.5px, Height: 815px                                  -->
    <!-- ============================================================== -->

    <!-- ============================================================== -->
    <!-- STAGE 1: RAW SCRIPT CAPTURE / UPLOAD                           -->
    <!-- ============================================================== -->
    <g transform="translate(43, 75)">
        <rect width="315" height="835" rx="8" fill="#F8FAFC" stroke="#94A3B8" stroke-width="1.3" />
        
        <!-- Header Strip -->
        <rect width="315" height="44" rx="8" fill="#475569" />
        <rect y="36" width="315" height="8" fill="#475569" />
        <rect x="14" y="12" width="60" height="20" rx="4" fill="#334155" />
        <text x="21" y="26" class="stage-badge">STAGE 1</text>
        <text x="84" y="26" font-family="'Segoe UI', Arial, sans-serif" font-size="12.5px" font-weight="700" fill="#FFFFFF">Raw Script Upload</text>

        <!-- Title & Subtitle inside card -->
        <g transform="translate(14, 58)">
            <text x="0" y="14" class="stage-title">Heterogeneous Capture</text>
            <text x="0" y="30" class="stage-subtitle" fill="#475569">Mobile Photos &amp; Scanned PDFs</text>
        </g>

        <!-- Visual Canvas Preview (Skewed & Shadowed Document) -->
        <g transform="translate(16, 105)">
            <rect width="283" height="340" rx="6" fill="#F1F5F9" stroke="#CBD5E1" stroke-width="1" />
            
            <!-- Simulated phone camera shadow gradient / uneven lighting -->
            <path d="M 0 0 L 283 0 L 283 200 L 0 340 Z" fill="#E2E8F0" opacity="0.6" />

            <!-- Skewed document representation (tilted by -8.5 degrees) -->
            <g transform="translate(141, 165) rotate(-8.5) translate(-95, -125)">
                <rect width="190" height="250" rx="3" fill="#FFFFFF" stroke="#94A3B8" stroke-width="1.2" />
                
                <!-- Document Lines (Simulated handwritten script with tilt) -->
                <!-- Heading -->
                <rect x="18" y="20" width="100" height="8" rx="2" fill="#64748B" />
                <rect x="18" y="34" width="70" height="6" rx="1.5" fill="#94A3B8" />

                <!-- Question Answer Section -->
                <rect x="18" y="55" width="28" height="7" rx="1.5" fill="#475569" />
                <line x1="18" y1="75" x2="160" y2="75" stroke="#64748B" stroke-width="2" stroke-linecap="round" />
                <line x1="18" y1="90" x2="140" y2="90" stroke="#64748B" stroke-width="2" stroke-linecap="round" />
                <line x1="18" y1="105" x2="170" y2="105" stroke="#64748B" stroke-width="2" stroke-linecap="round" />
                
                <!-- Formula sketch -->
                <text x="20" y="132" font-family="'Consolas', monospace" font-size="10px" font-weight="700" fill="#334155">y = Wx + b</text>
                
                <!-- More script lines -->
                <line x1="18" y1="150" x2="165" y2="150" stroke="#64748B" stroke-width="2" stroke-linecap="round" />
                <line x1="18" y1="165" x2="130" y2="165" stroke="#64748B" stroke-width="2" stroke-linecap="round" />
                <line x1="18" y1="180" x2="150" y2="180" stroke="#64748B" stroke-width="2" stroke-linecap="round" />
                <line x1="18" y1="195" x2="110" y2="195" stroke="#64748B" stroke-width="2" stroke-linecap="round" />

                <!-- Simulated shadow gradient across page -->
                <path d="M 0 100 L 190 20 L 190 250 L 0 250 Z" fill="#94A3B8" opacity="0.18" />
            </g>

            <!-- Metadata Pills Overlay -->
            <rect x="12" y="12" width="135" height="20" rx="4" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="0.8" />
            <text x="18" y="26" class="canvas-label" fill="#475569">📷 Mobile / Flatbed Scan</text>

            <rect x="12" y="306" width="115" height="20" rx="4" fill="#FEF2F2" stroke="#FECACA" stroke-width="0.8" />
            <text x="18" y="320" class="canvas-label" fill="#B91C1C">⚠ Tilt: ~ -8.50° Skew</text>

            <rect x="135" y="306" width="135" height="20" rx="4" fill="#FEF2F2" stroke="#FECACA" stroke-width="0.8" />
            <text x="142" y="320" class="canvas-label" fill="#B91C1C">⚠ Variable DPI (72-150)</text>
        </g>

        <!-- Technical Description & Parameters -->
        <g transform="translate(16, 465)">
            <text x="0" y="14" class="param-bold">• Input Ingestion:</text>
            <text x="0" y="30" class="param-desc">Direct PDF upload or multi-image photos</text>
            <text x="0" y="46" class="param-code" fill="#475569">Formats: PDF, JPEG, PNG, WebP</text>

            <text x="0" y="74" class="param-bold">• Common Document Flaws:</text>
            <text x="0" y="90" class="param-desc">• Non-uniform mobile perspective tilt</text>
            <text x="0" y="106" class="param-desc">• Uneven lighting &amp; harsh paper shadows</text>
            <text x="0" y="122" class="param-desc">• Inconsistent DPI &amp; low stroke contrast</text>

            <text x="0" y="150" class="param-bold">• Integrity Trace:</text>
            <text x="0" y="166" class="param-desc">SHA-256 fingerprinting on submission</text>
            <text x="0" y="182" class="param-code" fill="#334155">WorkingCopyManager initialization</text>

            <!-- Bottom Tag -->
            <rect x="0" y="320" width="283" height="26" rx="4" fill="#F1F5F9" stroke="#CBD5E1" stroke-width="1" />
            <text x="14" y="337" class="code-tag" fill="#334155">Output: Raw Byte Stream Array</text>
        </g>
    </g>

    <!-- Transition Arrow 1 -> 2 -->
    <g transform="translate(360, 480)">
        <line x1="0" y1="0" x2="33" y2="0" stroke="#2563EB" stroke-width="2.5" marker-end="url(#arrStage)" />
        <rect x="-10" y="-22" width="53" height="15" rx="3" fill="#EFF6FF" stroke="#BFDBFE" stroke-width="0.8" />
        <text x="16" y="-11" class="flow-tag">fitz</text>
    </g>

    <!-- ============================================================== -->
    <!-- STAGE 2: 300 DPI PYMUPDF RASTERIZATION                         -->
    <!-- ============================================================== -->
    <g transform="translate(398, 75)">
        <rect width="315" height="835" rx="8" fill="#F8FAFC" stroke="#93C5FD" stroke-width="1.3" />
        
        <rect width="315" height="44" rx="8" fill="#1D4ED8" />
        <rect y="36" width="315" height="8" fill="#1D4ED8" />
        <rect x="14" y="12" width="60" height="20" rx="4" fill="#1E3A8A" />
        <text x="21" y="26" class="stage-badge">STAGE 2</text>
        <text x="84" y="26" font-family="'Segoe UI', Arial, sans-serif" font-size="12.5px" font-weight="700" fill="#FFFFFF">300 DPI Rasterization</text>

        <g transform="translate(14, 58)">
            <text x="0" y="14" class="stage-title">Resolution Standardization</text>
            <text x="0" y="30" class="stage-subtitle" fill="#1D4ED8">PyMuPDF High-Res Matrix</text>
        </g>

        <!-- Visual Canvas Preview (High-Res 300 DPI Grid) -->
        <g transform="translate(16, 105)">
            <rect width="283" height="340" rx="6" fill="#F8FAFC" stroke="#BFDBFE" stroke-width="1" />
            
            <!-- High-Res Pixel Grid Simulation -->
            <g stroke="#DBEAFE" stroke-width="0.8" opacity="0.7">
                <line x1="30" y1="0" x2="30" y2="340" />
                <line x1="60" y1="0" x2="60" y2="340" />
                <line x1="90" y1="0" x2="90" y2="340" />
                <line x1="120" y1="0" x2="120" y2="340" />
                <line x1="150" y1="0" x2="150" y2="340" />
                <line x1="180" y1="0" x2="180" y2="340" />
                <line x1="210" y1="0" x2="210" y2="340" />
                <line x1="240" y1="0" x2="240" y2="340" />
                <line x1="0" y1="50" x2="283" y2="50" />
                <line x1="0" y1="100" x2="283" y2="100" />
                <line x1="0" y1="150" x2="283" y2="150" />
                <line x1="0" y1="200" x2="283" y2="200" />
                <line x1="0" y1="250" x2="283" y2="250" />
                <line x1="0" y1="300" x2="283" y2="300" />
            </g>

            <!-- Document centered, still with tilt, but ultra sharp edges -->
            <g transform="translate(141, 165) rotate(-8.5) translate(-95, -125)">
                <rect width="190" height="250" rx="3" fill="#FFFFFF" stroke="#1D4ED8" stroke-width="1.5" />
                
                <rect x="18" y="20" width="100" height="8" rx="2" fill="#1E3A8A" />
                <rect x="18" y="34" width="70" height="6" rx="1.5" fill="#3B82F6" />

                <rect x="18" y="55" width="28" height="7" rx="1.5" fill="#1D4ED8" />
                <line x1="18" y1="75" x2="160" y2="75" stroke="#1E293B" stroke-width="2.5" stroke-linecap="round" />
                <line x1="18" y1="90" x2="140" y2="90" stroke="#1E293B" stroke-width="2.5" stroke-linecap="round" />
                <line x1="18" y1="105" x2="170" y2="105" stroke="#1E293B" stroke-width="2.5" stroke-linecap="round" />
                
                <text x="20" y="132" font-family="'Consolas', monospace" font-size="11px" font-weight="700" fill="#0F172A">y = Wx + b</text>
                
                <line x1="18" y1="150" x2="165" y2="150" stroke="#1E293B" stroke-width="2.5" stroke-linecap="round" />
                <line x1="18" y1="165" x2="130" y2="165" stroke="#1E293B" stroke-width="2.5" stroke-linecap="round" />
                <line x1="18" y1="180" x2="150" y2="180" stroke="#1E293B" stroke-width="2.5" stroke-linecap="round" />
            </g>

            <rect x="12" y="12" width="145" height="20" rx="4" fill="#EFF6FF" stroke="#BFDBFE" stroke-width="0.8" />
            <text x="18" y="26" class="canvas-label" fill="#1D4ED8">🔍 Scale Factor: 4.166x</text>

            <rect x="12" y="306" width="140" height="20" rx="4" fill="#EFF6FF" stroke="#BFDBFE" stroke-width="0.8" />
            <text x="18" y="320" class="canvas-label" fill="#1D4ED8">✓ 300 DPI Standardized</text>

            <rect x="158" y="306" width="112" height="20" rx="4" fill="#EFF6FF" stroke="#BFDBFE" stroke-width="0.8" />
            <text x="164" y="320" class="canvas-label" fill="#1D4ED8">2480 × 3508 px</text>
        </g>

        <!-- Technical Description & Parameters -->
        <g transform="translate(16, 465)">
            <text x="0" y="14" class="param-bold">• PyMuPDF (fitz) Matrix:</text>
            <text x="0" y="30" class="param-desc">Scales default 72 DPI PDF to 300 DPI</text>
            <text x="0" y="46" class="param-code" fill="#1D4ED8">zoom = 300 / 72 = 4.166667</text>

            <text x="0" y="74" class="param-bold">• Resolution Calibration:</text>
            <text x="0" y="90" class="param-desc">• Matrix size: 2480 x 3508 px (A4)</text>
            <text x="0" y="106" class="param-desc">• Sub-pixel character edge definition</text>
            <text x="0" y="122" class="param-desc">• Anti-aliasing preserves ink strokes</text>

            <text x="0" y="150" class="param-bold">• Pre-OCR Preparation:</text>
            <text x="0" y="166" class="param-desc">Optimal density for CRNN &amp; Tesseract</text>
            <text x="0" y="182" class="param-code" fill="#1E40AF">page.get_pixmap(matrix=mat, alpha=False)</text>

            <rect x="0" y="320" width="283" height="26" rx="4" fill="#EFF6FF" stroke="#BFDBFE" stroke-width="1" />
            <text x="14" y="337" class="code-tag" fill="#1E40AF">Output: 300 DPI BGR Image Matrix</text>
        </g>
    </g>

    <!-- Transition Arrow 2 -> 3 -->
    <g transform="translate(715, 480)">
        <line x1="0" y1="0" x2="33" y2="0" stroke="#7C3AED" stroke-width="2.5" marker-end="url(#arrPurple)" />
        <rect x="-12" y="-22" width="57" height="15" rx="3" fill="#F5F3FF" stroke="#DDD6FE" stroke-width="0.8" />
        <text x="16" y="-11" class="flow-tag" fill="#6D28D9">Hough</text>
    </g>

    <!-- ============================================================== -->
    <!-- STAGE 3: OPENCV HOUGH TRANSFORM DESKEWING                      -->
    <!-- ============================================================== -->
    <g transform="translate(753, 75)">
        <rect width="315" height="835" rx="8" fill="#F8FAFC" stroke="#C4B5FD" stroke-width="1.3" />
        
        <rect width="315" height="44" rx="8" fill="#7C3AED" />
        <rect y="36" width="315" height="8" fill="#7C3AED" />
        <rect x="14" y="12" width="60" height="20" rx="4" fill="#5B21B6" />
        <text x="21" y="26" class="stage-badge">STAGE 3</text>
        <text x="84" y="26" font-family="'Segoe UI', Arial, sans-serif" font-size="12.5px" font-weight="700" fill="#FFFFFF">OpenCV Hough Deskew</text>

        <g transform="translate(14, 58)">
            <text x="0" y="14" class="stage-title">Geometric Tilt Correction</text>
            <text x="0" y="30" class="stage-subtitle" fill="#7C3AED">Canny Edges &amp; Rotation Matrix</text>
        </g>

        <!-- Visual Canvas Preview (Hough Lines & Rotation Vector) -->
        <g transform="translate(16, 105)">
            <rect width="283" height="340" rx="6" fill="#FBFDFF" stroke="#DDD6FE" stroke-width="1" />

            <!-- Document rotated to PERFECT horizontal 0.0° -->
            <g transform="translate(141, 165) translate(-95, -125)">
                <rect width="190" height="250" rx="3" fill="#FFFFFF" stroke="#7C3AED" stroke-width="1.5" />
                
                <rect x="18" y="20" width="100" height="8" rx="2" fill="#5B21B6" />
                <rect x="18" y="34" width="70" height="6" rx="1.5" fill="#8B5CF6" />

                <!-- Question Answer Section with Detected Hough Guide Lines -->
                <rect x="18" y="55" width="28" height="7" rx="1.5" fill="#7C3AED" />
                <line x1="18" y1="75" x2="160" y2="75" stroke="#1E293B" stroke-width="2.2" stroke-linecap="round" />
                <line x1="18" y1="90" x2="140" y2="90" stroke="#1E293B" stroke-width="2.2" stroke-linecap="round" />
                <line x1="18" y1="105" x2="170" y2="105" stroke="#1E293B" stroke-width="2.2" stroke-linecap="round" />
                
                <text x="20" y="132" font-family="'Consolas', monospace" font-size="11px" font-weight="700" fill="#0F172A">y = Wx + b</text>
                
                <line x1="18" y1="150" x2="165" y2="150" stroke="#1E293B" stroke-width="2.2" stroke-linecap="round" />
                <line x1="18" y1="165" x2="130" y2="165" stroke="#1E293B" stroke-width="2.2" stroke-linecap="round" />
                <line x1="18" y1="180" x2="150" y2="180" stroke="#1E293B" stroke-width="2.2" stroke-linecap="round" />

                <!-- Red & Cyan Hough Line detection overlay -->
                <line x1="10" y1="75" x2="180" y2="75" stroke="#EF4444" stroke-width="1" stroke-dasharray="4 2" />
                <line x1="10" y1="105" x2="180" y2="105" stroke="#EF4444" stroke-width="1" stroke-dasharray="4 2" />
                <line x1="10" y1="150" x2="180" y2="150" stroke="#EF4444" stroke-width="1" stroke-dasharray="4 2" />
            </g>

            <!-- Rotation indicator circle & arc -->
            <circle cx="230" cy="50" r="18" fill="#F5F3FF" stroke="#7C3AED" stroke-width="1.2" />
            <path d="M 220 50 A 10 10 0 0 1 240 50" fill="none" stroke="#7C3AED" stroke-width="2" marker-end="url(#arrPurple)" />
            <text x="216" y="30" font-family="'Segoe UI', Arial, sans-serif" font-size="9px" font-weight="700" fill="#7C3AED">Δθ: +8.5°</text>

            <rect x="12" y="12" width="135" height="20" rx="4" fill="#F5F3FF" stroke="#DDD6FE" stroke-width="0.8" />
            <text x="18" y="26" class="canvas-label" fill="#7C3AED">📐 Hough Line Vector</text>

            <rect x="12" y="306" width="125" height="20" rx="4" fill="#F0FDF4" stroke="#BBF7D0" stroke-width="0.8" />
            <text x="18" y="320" class="canvas-label" fill="#15803D">✓ Aligned: ± 0.05°</text>

            <rect x="145" y="306" width="125" height="20" rx="4" fill="#F5F3FF" stroke="#DDD6FE" stroke-width="0.8" />
            <text x="151" y="320" class="canvas-label" fill="#7C3AED">warpAffine INTER_CUBIC</text>
        </g>

        <!-- Technical Description & Parameters -->
        <g transform="translate(16, 465)">
            <text x="0" y="14" class="param-bold">• Canny Edge Gradient:</text>
            <text x="0" y="30" class="param-desc">Detects high-contrast line boundaries</text>
            <text x="0" y="46" class="param-code" fill="#7C3AED">cv2.Canny(gray, 50, 150, apertureSize=3)</text>

            <text x="0" y="74" class="param-bold">• HoughLines Detection:</text>
            <text x="0" y="90" class="param-desc">• Identifies dominant horizontal text lines</text>
            <text x="0" y="106" class="param-desc">• Median angle computes global skew</text>
            <text x="0" y="122" class="param-desc">• Rotates around image centroid</text>

            <text x="0" y="150" class="param-bold">• Affine Transformation:</text>
            <text x="0" y="166" class="param-desc">cv2.getRotationMatrix2D + warpAffine</text>
            <text x="0" y="182" class="param-code" fill="#5B21B6">flags=cv2.INTER_CUBIC, BORDER_REPLICATE</text>

            <rect x="0" y="320" width="283" height="26" rx="4" fill="#F5F3FF" stroke="#DDD6FE" stroke-width="1" />
            <text x="14" y="337" class="code-tag" fill="#6D28D9">Output: Deskewed Horizontal Array</text>
        </g>
    </g>

    <!-- Transition Arrow 3 -> 4 -->
    <g transform="translate(1070, 480)">
        <line x1="0" y1="0" x2="33" y2="0" stroke="#059669" stroke-width="2.5" marker-end="url(#arrEmerald)" />
        <rect x="-10" y="-22" width="53" height="15" rx="3" fill="#ECFDF5" stroke="#A7F3D0" stroke-width="0.8" />
        <text x="16" y="-11" class="flow-tag" fill="#065F46">Otsu</text>
    </g>

    <!-- ============================================================== -->
    <!-- STAGE 4: ADAPTIVE OTSU BINARIZATION & SHADOW REMOVAL           -->
    <!-- ============================================================== -->
    <g transform="translate(1108, 75)">
        <rect width="315" height="835" rx="8" fill="#F8FAFC" stroke="#A7F3D0" stroke-width="1.3" />
        
        <rect width="315" height="44" rx="8" fill="#059669" />
        <rect y="36" width="315" height="8" fill="#059669" />
        <rect x="14" y="12" width="60" height="20" rx="4" fill="#064E3B" />
        <text x="21" y="26" class="stage-badge">STAGE 4</text>
        <text x="84" y="26" font-family="'Segoe UI', Arial, sans-serif" font-size="12.5px" font-weight="700" fill="#FFFFFF">Adaptive Binarization</text>

        <g transform="translate(14, 58)">
            <text x="0" y="14" class="stage-title">Shadow Removal &amp; Contrast</text>
            <text x="0" y="30" class="stage-subtitle" fill="#059669">Otsu Threshold &amp; Morphological Whitening</text>
        </g>

        <!-- Visual Canvas Preview (Pure White Background + Deep Black Ink) -->
        <g transform="translate(16, 105)">
            <rect width="283" height="340" rx="6" fill="#F0FDF4" stroke="#A7F3D0" stroke-width="1" />

            <!-- Document with pristine white background and high contrast black ink -->
            <g transform="translate(141, 165) translate(-95, -125)">
                <rect width="190" height="250" rx="3" fill="#FFFFFF" stroke="#059669" stroke-width="1.5" />
                
                <rect x="18" y="20" width="100" height="8" rx="2" fill="#064E3B" />
                <rect x="18" y="34" width="70" height="6" rx="1.5" fill="#059669" />

                <rect x="18" y="55" width="28" height="7" rx="1.5" fill="#047857" />
                <line x1="18" y1="75" x2="160" y2="75" stroke="#000000" stroke-width="2.5" stroke-linecap="round" />
                <line x1="18" y1="90" x2="140" y2="90" stroke="#000000" stroke-width="2.5" stroke-linecap="round" />
                <line x1="18" y1="105" x2="170" y2="105" stroke="#000000" stroke-width="2.5" stroke-linecap="round" />
                
                <text x="20" y="132" font-family="'Consolas', monospace" font-size="11px" font-weight="800" fill="#000000">y = Wx + b</text>
                
                <line x1="18" y1="150" x2="165" y2="150" stroke="#000000" stroke-width="2.5" stroke-linecap="round" />
                <line x1="18" y1="165" x2="130" y2="165" stroke="#000000" stroke-width="2.5" stroke-linecap="round" />
                <line x1="18" y1="180" x2="150" y2="180" stroke="#000000" stroke-width="2.5" stroke-linecap="round" />
            </g>

            <rect x="12" y="12" width="145" height="20" rx="4" fill="#ECFDF5" stroke="#A7F3D0" stroke-width="0.8" />
            <text x="18" y="26" class="canvas-label" fill="#065F46">✨ Shadows Eliminated</text>

            <rect x="12" y="306" width="130" height="20" rx="4" fill="#ECFDF5" stroke="#A7F3D0" stroke-width="0.8" />
            <text x="18" y="320" class="canvas-label" fill="#065F46">✓ Pristine #FFFFFF Paper</text>

            <rect x="150" y="306" width="120" height="20" rx="4" fill="#ECFDF5" stroke="#A7F3D0" stroke-width="0.8" />
            <text x="156" y="320" class="canvas-label" fill="#065F46">Max Ink Contrast</text>
        </g>

        <!-- Technical Description & Parameters -->
        <g transform="translate(16, 465)">
            <text x="0" y="14" class="param-bold">• Morphological Shadow Removal:</text>
            <text x="0" y="30" class="param-desc">Dilates RGB planes &amp; estimates background</text>
            <text x="0" y="46" class="param-code" fill="#059669">bg = medianBlur(dilate(plane, 7x7), 21)</text>

            <text x="0" y="74" class="param-bold">• Otsu Thresholding:</text>
            <text x="0" y="90" class="param-desc">• Minimizes intra-class intensity variance</text>
            <text x="0" y="106" class="param-desc">• Bimodal distribution splits ink vs paper</text>
            <text x="0" y="122" class="param-desc">• CLAHE contrast enhancement in LAB space</text>

            <text x="0" y="150" class="param-bold">• Teacher Ink Filter (Optional):</text>
            <text x="0" y="166" class="param-desc">HSV mask isolates red/green pens</text>
            <text x="0" y="182" class="param-code" fill="#064E3B">Student blue/black ink strictly preserved</text>

            <rect x="0" y="320" width="283" height="26" rx="4" fill="#ECFDF5" stroke="#A7F3D0" stroke-width="1" />
            <text x="14" y="337" class="code-tag" fill="#065F46">Output: High-Contrast Binary Matrix</text>
        </g>
    </g>

    <!-- Transition Arrow 4 -> 5 -->
    <g transform="translate(1425, 480)">
        <line x1="0" y1="0" x2="33" y2="0" stroke="#0284C7" stroke-width="2.5" marker-end="url(#arrSky)" />
        <rect x="-12" y="-22" width="57" height="15" rx="3" fill="#F0F9FF" stroke="#BAE6FD" stroke-width="0.8" />
        <text x="16" y="-11" class="flow-tag" fill="#0369A1">Normalize</text>
    </g>

    <!-- ============================================================== -->
    <!-- STAGE 5: DYNAMIC COORDINATE NORMALIZATION                      -->
    <!-- ============================================================== -->
    <g transform="translate(1463, 75)">
        <rect width="315" height="835" rx="8" fill="#F8FAFC" stroke="#7DD3FC" stroke-width="1.3" />
        
        <rect width="315" height="44" rx="8" fill="#0284C7" />
        <rect y="36" width="315" height="8" fill="#0284C7" />
        <rect x="14" y="12" width="60" height="20" rx="4" fill="#075985" />
        <text x="21" y="26" class="stage-badge">STAGE 5</text>
        <text x="84" y="26" font-family="'Segoe UI', Arial, sans-serif" font-size="12.5px" font-weight="700" fill="#FFFFFF">Coordinate Normalization</text>

        <g transform="translate(14, 58)">
            <text x="0" y="14" class="stage-title">Spatial Unit Mapping</text>
            <text x="0" y="30" class="stage-subtitle" fill="#0284C7">[ymin, xmin, ymax, xmax] ∈ [0.0, 1.0]</text>
        </g>

        <!-- Visual Canvas Preview (Bounding Box Coordinates on Screen) -->
        <g transform="translate(16, 105)">
            <rect width="283" height="340" rx="6" fill="#F0F9FF" stroke="#BAE6FD" stroke-width="1" />

            <!-- Document with Normalized Bounding Box Overlays -->
            <g transform="translate(141, 165) translate(-95, -125)">
                <rect width="190" height="250" rx="3" fill="#FFFFFF" stroke="#0284C7" stroke-width="1.5" />
                
                <rect x="18" y="20" width="100" height="8" rx="2" fill="#075985" />
                <rect x="18" y="34" width="70" height="6" rx="1.5" fill="#0284C7" />

                <!-- Bounding Box 1: Question Header [0.22, 0.09, 0.30, 0.35] -->
                <rect x="14" y="50" width="162" height="68" rx="3" fill="#0284C7" fill-opacity="0.08" stroke="#0284C7" stroke-width="1.2" stroke-dasharray="3 2" />
                <text x="18" y="62" font-family="'Consolas', monospace" font-size="8px" font-weight="700" fill="#0284C7">[0.20, 0.08, 0.47, 0.92]</text>

                <rect x="18" y="70" width="28" height="7" rx="1.5" fill="#0284C7" />
                <line x1="18" y1="85" x2="160" y2="85" stroke="#0F172A" stroke-width="2" stroke-linecap="round" />
                <line x1="18" y1="100" x2="140" y2="100" stroke="#0F172A" stroke-width="2" stroke-linecap="round" />
                
                <!-- Bounding Box 2: Formula & Answer Region -->
                <rect x="14" y="125" width="162" height="110" rx="3" fill="#10B981" fill-opacity="0.08" stroke="#10B981" stroke-width="1.2" stroke-dasharray="3 2" />
                <text x="18" y="137" font-family="'Consolas', monospace" font-size="8px" font-weight="700" fill="#059669">[0.50, 0.08, 0.94, 0.92]</text>

                <text x="20" y="152" font-family="'Consolas', monospace" font-size="10px" font-weight="700" fill="#0F172A">y = Wx + b</text>
                
                <line x1="18" y1="168" x2="165" y2="168" stroke="#0F172A" stroke-width="2" stroke-linecap="round" />
                <line x1="18" y1="184" x2="130" y2="184" stroke="#0F172A" stroke-width="2" stroke-linecap="round" />
                <line x1="18" y1="200" x2="150" y2="200" stroke="#0F172A" stroke-width="2" stroke-linecap="round" />
            </g>

            <rect x="12" y="12" width="150" height="20" rx="4" fill="#F0F9FF" stroke="#BAE6FD" stroke-width="0.8" />
            <text x="18" y="26" class="canvas-label" fill="#0369A1">🎯 Normalized Unit Coords</text>

            <rect x="12" y="306" width="135" height="20" rx="4" fill="#F0F9FF" stroke="#BAE6FD" stroke-width="0.8" />
            <text x="18" y="320" class="canvas-label" fill="#0369A1">✓ Device-Independent</text>

            <rect x="154" y="306" width="116" height="20" rx="4" fill="#F0F9FF" stroke="#BAE6FD" stroke-width="0.8" />
            <text x="160" y="320" class="canvas-label" fill="#0369A1">Split-Screen Ready</text>
        </g>

        <!-- Technical Description & Parameters -->
        <g transform="translate(16, 465)">
            <text x="0" y="14" class="param-bold">• Normalization Formula:</text>
            <text x="0" y="30" class="param-desc">Relative coordinate transformation</text>
            <text x="0" y="46" class="param-code" fill="#0284C7">ymin_norm = ymin_px / page_height</text>
            <text x="0" y="60" class="param-code" fill="#0284C7">xmin_norm = xmin_px / page_width</text>

            <text x="0" y="86" class="param-bold">• Device-Independent Rendering:</text>
            <text x="0" y="102" class="param-desc">• Scales perfectly on 4K, laptop &amp; tablet</text>
            <text x="0" y="118" class="param-desc">• Resolution-agnostic bounding boxes</text>
            <text x="0" y="134" class="param-desc">• Split-screen canvas overlay alignment</text>

            <text x="0" y="160" class="param-bold">• Database Model Storage:</text>
            <text x="0" y="176" class="param-desc">Stored in SubmissionPage.answer_regions</text>
            <text x="0" y="192" class="param-code" fill="#075985">SubmissionAnswer.bounding_box_json</text>

            <rect x="0" y="320" width="283" height="26" rx="4" fill="#F0F9FF" stroke="#BAE6FD" stroke-width="1" />
            <text x="14" y="337" class="code-tag" fill="#0369A1">Ready for OCR &amp; Dual Workbenches</text>
        </g>
    </g>

    <!-- Bottom Metadata Bar -->
    <g transform="translate(43, 938)">
        <text x="0" y="0" class="footer-text">IntelliGrade Computer Vision Core — Figure 3.4: 300 DPI Document Preprocessing, Deskewing &amp; Normalization Pipeline</text>
        <text x="1714" y="0" class="footer-text" text-anchor="end">Target Dimensions: 6.0" × 3.2" (300 DPI, 1800 × 960 px) | Pure Light Mode | Publication-Ready</text>
    </g>
</svg>
"""
    return svg

def main():
    output_dir = r"F:\Hijbullah\IntelliGrade\materials"
    os.makedirs(output_dir, exist_ok=True)
    
    svg_content = generate_svg()
    
    # Save single image file: Figure-3.4.png
    doc = fitz.open(stream=svg_content.encode("utf-8"), filetype="svg")
    page = doc[0]
    pix = page.get_pixmap(matrix=fitz.Matrix(1, 1), alpha=False)
    
    png_filename = "Figure-3.4.png"
    png_path = os.path.join(output_dir, png_filename)
    
    temp_path = os.path.join(output_dir, "temp_34.png")
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
