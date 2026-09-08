"""
Generates Figure 3.9: Resilient Multi-Provider AI Evaluation Failover Architecture
Dimensions: Width: 6.2 in, Height: 3.8 in @ 300 DPI (1860 x 1140 px)
Strict Light Mode, crisp high-contrast academic publication styling:
- Left: Request Ingestion, TaskRouter Core & Cooldown Registry
- Center: 4-Tier Provider Failover Cascade & HTTP 429 Cooldown Walkthrough
- Right: JSON Response Sanitizer, LaTeX Repair & Teacher Workbench Delivery
Outputs ONLY a single image: materials/Figure-3.9.png
"""
import os
import fitz  # PyMuPDF
from PIL import Image

def generate_svg():
    width = 1860
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
            
            .panel-header-title {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 13px; font-weight: 700; fill: #FFFFFF; }}
            .panel-header-sub {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 10px; font-weight: 500; fill: #E2E8F0; }}
            
            .card-title {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 11px; font-weight: 800; }}
            .card-desc {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 9.5px; font-weight: 500; fill: #334155; }}
            .code-text {{ font-family: 'Consolas', monospace; font-size: 8.5px; font-weight: 700; }}
            
            .badge-text {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 8.5px; font-weight: 700; }}
            .tier-title {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 11.5px; font-weight: 800; fill: #0F172A; }}
            .tier-sub {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 9.5px; font-weight: 600; }}
            
            .footer-info {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 10px; font-weight: 500; fill: #64748B; }}
        </style>
    </defs>

    <!-- Canvas Background -->
    <rect width="{width}" height="{height}" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.5" />

    <!-- Top Diagram Header Block -->
    <g transform="translate(45, 18)">
        <rect x="0" y="0" width="5" height="42" rx="2" fill="#2563EB" />
        <text x="16" y="21" class="main-title">Figure 3.9: Resilient Multi-Provider AI Evaluation Failover Architecture</text>
        <text x="16" y="39" class="main-subtitle">TaskRouter Orchestrator, 429 Quota Exhaustion Cooldown Registries, 4-Tier Evaluation Cascade, and Local Vision Downsampling</text>
    </g>

    <!-- ============================================================== -->
    <!-- PANEL 1 (LEFT): INGESTION, TASKROUTER & COOLDOWN REGISTRY      -->
    <!-- Coordinates: x: 45, y: 75, w: 450, h: 1025                     -->
    <!-- ============================================================== -->
    <g transform="translate(45, 75)">
        <rect width="450" height="1025" rx="8" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1.3" />
        
        <!-- Header Bar -->
        <rect width="450" height="38" rx="8" fill="#1E293B" />
        <rect y="30" width="450" height="8" fill="#1E293B" />
        <text x="16" y="24" class="panel-header-title">1. TaskRouter Core &amp; Cooldown Registry</text>
        <text x="434" y="24" text-anchor="end" class="panel-header-sub">task_router.py &amp; failover.py</text>

        <!-- CARD 1A: INCOMING EVALUATION REQUEST -->
        <g transform="translate(18, 52)">
            <rect width="414" height="130" rx="6" fill="#FFFFFF" stroke="#3B82F6" stroke-width="1.4" />
            <rect width="414" height="24" rx="6" fill="#DBEAFE" />
            <rect y="18" width="414" height="6" fill="#DBEAFE" />
            <text x="12" y="16" class="card-title" fill="#1E40AF">EVALUATION REQUEST DISPATCH (evaluate_answer)</text>
            
            <g transform="translate(12, 34)">
                <text x="0" y="12" class="card-desc">• <tspan font-weight="700">Question Text &amp; Academic Rubric:</tspan> 23-Taxonomy OBE Criteria, Max Marks</text>
                <text x="0" y="27" class="card-desc">• <tspan font-weight="700">Student Submission Payload:</tspan> OCR Extracted Text &amp; Visual Crop Payloads</text>
                <text x="0" y="42" class="card-desc">• <tspan font-weight="700">Task Classification:</tspan> <tspan font-family="Consolas" font-weight="700" fill="#2563EB">TaskType.ANSWER_VISUAL_READ</tspan> (has_images=True)</text>
                
                <g transform="translate(0, 52)">
                    <rect width="390" height="34" rx="4" fill="#EFF6FF" stroke="#BFDBFE" stroke-width="0.8" />
                    <text x="8" y="14" class="code-text" fill="#1E40AF">evaluate_answer(q_text, rubric, student_ans, max_marks=25,</text>
                    <text x="8" y="26" class="code-text" fill="#16A34A">                task_type=TaskType.ANSWER_VISUAL_READ, image_bytes=b'...'))</text>
                </g>
            </g>
        </g>

        <!-- DOWN ARROW 1A -> 1B -->
        <path d="M 225 182 L 225 204" fill="none" stroke="#64748B" stroke-width="2" marker-end="url(#arrSlate)" />

        <!-- CARD 1B: TASKROUTER ORCHESTRATION ENGINE -->
        <g transform="translate(18, 208)">
            <rect width="414" height="224" rx="6" fill="#FFFFFF" stroke="#6366F1" stroke-width="1.4" />
            <rect width="414" height="24" rx="6" fill="#E0E7FF" />
            <rect y="18" width="414" height="6" fill="#E0E7FF" />
            <text x="12" y="16" class="card-title" fill="#3730A3">TASKROUTER CAPABILITY &amp; BUDGET MANAGER</text>
            
            <g transform="translate(12, 34)">
                <text x="0" y="12" class="card-desc">• <tspan font-weight="700">Capability Matrix Match:</tspan> Filters providers by image &amp; JSON support</text>
                <text x="0" y="27" class="card-desc">• <tspan font-weight="700">Global Timeout Budget:</tspan> Strict 45.0s global ceiling across all failovers</text>
                <text x="0" y="42" class="card-desc">• <tspan font-weight="700">Deadline Tracking:</tspan> <tspan font-family="Consolas" font-weight="700">remaining = deadline - monotonic()</tspan> (&gt; 1.0s guard)</text>
                
                <!-- Downsampling Sub-Box -->
                <g transform="translate(0, 52)">
                    <rect width="390" height="70" rx="4" fill="#EEF2FF" stroke="#C7D2FE" stroke-width="1" />
                    <text x="10" y="16" font-family="'Segoe UI', Arial, sans-serif" font-size="10px" font-weight="700" fill="#4338CA">Image Preprocessing &amp; Downsampling Pipeline:</text>
                    <text x="10" y="32" class="card-desc">• <tspan font-weight="700">LANCZOS Downscale:</tspan> Max dimension clamped to <tspan font-weight="700" fill="#4338CA">800px</tspan> width/height</text>
                    <text x="10" y="47" class="card-desc">• <tspan font-weight="700">JPEG Compression:</tspan> Quality 75 optimize=True (reduces payload by 82%)</text>
                    <text x="10" y="62" class="card-desc">• <tspan font-weight="700">Crop Compaction:</tspan> Multi-page crops packed into composite grids</text>
                </g>

                <g transform="translate(0, 130)">
                    <rect width="390" height="38" rx="4" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="0.8" />
                    <text x="8" y="15" class="code-text" fill="#0F172A">img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)</text>
                    <text x="8" y="28" class="code-text" fill="#4338CA">img.save(out_buffer, format='JPEG', quality=75, optimize=True)</text>
                </g>
            </g>
        </g>

        <!-- DOWN ARROW 1B -> 1C -->
        <path d="M 225 432 L 225 452" fill="none" stroke="#64748B" stroke-width="2" marker-end="url(#arrSlate)" />

        <!-- CARD 1C: RATE-LIMIT COOLDOWN REGISTRY -->
        <g transform="translate(18, 456)">
            <rect width="414" height="268" rx="6" fill="#FFFBEB" stroke="#F59E0B" stroke-width="1.4" />
            <rect width="414" height="24" rx="6" fill="#FEF3C7" />
            <rect y="18" width="414" height="6" fill="#FEF3C7" />
            <text x="12" y="16" class="card-title" fill="#92400E">AI PROVIDER HEALTH &amp; COOLDOWN REGISTRY</text>
            
            <g transform="translate(12, 34)">
                <text x="0" y="12" class="card-desc">• <tspan font-weight="700">Error Classification:</tspan> Intercepts HTTP 429 Quota &amp; 401 Auth errors</text>
                <text x="0" y="27" class="card-desc">• <tspan font-weight="700">Transient Retry Policy:</tspan> 502/503/Timeout → Max 1 retry (0.5s backoff)</text>
                <text x="0" y="42" class="card-desc">• <tspan font-weight="700">Non-Transient Action:</tspan> HTTP 429 triggers <tspan font-weight="700" fill="#B45309">120s Immutable Cooldown</tspan></text>
                <text x="0" y="57" class="card-desc">• <tspan font-weight="700">Zero-Downtime Bypass:</tspan> Cooled providers skipped instantly (0ms delay)</text>

                <!-- Live Registry Table Mockup -->
                <g transform="translate(0, 68)">
                    <rect width="390" height="98" rx="4" fill="#FFFFFF" stroke="#FCD34D" stroke-width="1" />
                    <!-- Table Header -->
                    <rect width="390" height="22" rx="4" fill="#FEF3C7" />
                    <rect y="18" width="390" height="4" fill="#FEF3C7" />
                    <text x="10" y="15" font-family="'Segoe UI', Arial, sans-serif" font-size="9px" font-weight="700" fill="#78350F">PROVIDER</text>
                    <text x="140" y="15" font-family="'Segoe UI', Arial, sans-serif" font-size="9px" font-weight="700" fill="#78350F">STATUS</text>
                    <text x="240" y="15" font-family="'Segoe UI', Arial, sans-serif" font-size="9px" font-weight="700" fill="#78350F">COOLDOWN EXPIRY</text>
                    <text x="340" y="15" font-family="'Segoe UI', Arial, sans-serif" font-size="9px" font-weight="700" fill="#78350F">ACTION</text>

                    <!-- Row 1: Gemini (Rate Limited) -->
                    <g transform="translate(0, 25)">
                        <text x="10" y="14" font-family="Consolas" font-size="9px" font-weight="700" fill="#DC2626">GeminiProvider</text>
                        <rect x="135" y="3" width="76" height="15" rx="3" fill="#FEE2E2" />
                        <text x="173" y="14" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif" font-size="8px" font-weight="800" fill="#991B1B">429 LIMITED</text>
                        <text x="240" y="14" font-family="Consolas" font-size="8.5px" fill="#DC2626">t + 114.2s left</text>
                        <text x="340" y="14" font-family="'Segoe UI', Arial, sans-serif" font-size="8.5px" font-weight="700" fill="#DC2626">BYPASS</text>
                        <line x1="10" y1="20" x2="380" y2="20" stroke="#F1F5F9" stroke-width="1" />
                    </g>

                    <!-- Row 2: Groq (Healthy) -->
                    <g transform="translate(0, 47)">
                        <text x="10" y="14" font-family="Consolas" font-size="9px" font-weight="700" fill="#16A34A">GroqProvider</text>
                        <rect x="135" y="3" width="76" height="15" rx="3" fill="#DCFCE7" />
                        <text x="173" y="14" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif" font-size="8px" font-weight="800" fill="#166534">ACTIVE / 0.8s</text>
                        <text x="240" y="14" font-family="Consolas" font-size="8.5px" fill="#16A34A">0.0s (Cleared)</text>
                        <text x="340" y="14" font-family="'Segoe UI', Arial, sans-serif" font-size="8.5px" font-weight="700" fill="#16A34A">ROUTE</text>
                        <line x1="10" y1="20" x2="380" y2="20" stroke="#F1F5F9" stroke-width="1" />
                    </g>

                    <!-- Row 3: Moondream2 (Healthy Offline) -->
                    <g transform="translate(0, 69)">
                        <text x="10" y="14" font-family="Consolas" font-size="9px" font-weight="700" fill="#2563EB">LocalVision</text>
                        <rect x="135" y="3" width="76" height="15" rx="3" fill="#DBEAFE" />
                        <text x="173" y="14" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif" font-size="8px" font-weight="800" fill="#1E40AF">OFFLINE / $0</text>
                        <text x="240" y="14" font-family="Consolas" font-size="8.5px" fill="#2563EB">0.0s (Cleared)</text>
                        <text x="340" y="14" font-family="'Segoe UI', Arial, sans-serif" font-size="8.5px" font-weight="700" fill="#2563EB">STANDBY</text>
                    </g>
                </g>

                <g transform="translate(0, 174)">
                    <rect width="390" height="38" rx="4" fill="#FFFBEB" stroke="#FCD34D" stroke-width="0.8" />
                    <text x="8" y="14" class="code-text" fill="#92400E">ProviderHealthTracker.mark_cooldown(GeminiProvider,</text>
                    <text x="8" y="27" class="code-text" fill="#B45309">                                   duration_seconds=120.0)</text>
                </g>
            </g>
        </g>

        <!-- CARD 1D: SUMMARY KEY METRICS -->
        <g transform="translate(18, 738)">
            <rect width="414" height="264" rx="6" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="1.2" />
            <rect width="414" height="24" rx="6" fill="#F1F5F9" />
            <rect y="18" width="414" height="6" fill="#F1F5F9" />
            <text x="12" y="16" font-family="'Segoe UI', Arial, sans-serif" font-size="11px" font-weight="700" fill="#334155">ROUTING SPECIFICATION &amp; GUARANTEES</text>
            
            <g transform="translate(12, 34)">
                <text x="0" y="12" class="card-desc">• <tspan font-weight="700">Determinism First:</tspan> Questions &amp; routines strictly parsed locally</text>
                <text x="0" y="26" class="card-desc">• <tspan font-weight="700">Zero Score Fabrication:</tspan> Unreached providers never guess grades</text>
                <text x="0" y="40" class="card-desc">• <tspan font-weight="700">Graceful Degradation:</tspan> Multimodal → Text LLM → Offline Vision</text>
                <text x="0" y="54" class="card-desc">• <tspan font-weight="700">Failover Latency Overhead:</tspan> Under 5ms in-memory cache lookup</text>
                <text x="0" y="68" class="card-desc">• <tspan font-weight="700">Session Continuity:</tspan> Teacher evaluation session never terminates</text>
                
                <g transform="translate(0, 80)">
                    <rect width="390" height="126" rx="4" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="0.8" />
                    <text x="8" y="16" class="code-text" fill="#0F172A"># Dynamic Chain Selection in failover.py</text>
                    <text x="8" y="32" class="code-text" fill="#2563EB">for provider in chain_order:</text>
                    <text x="20" y="48" class="code-text" fill="#D97706">if ProviderHealthTracker.is_on_cooldown(provider):</text>
                    <text x="32" y="64" class="code-text" fill="#64748B">continue # Instant bypass (0ms overhead)</text>
                    <text x="20" y="80" class="code-text" fill="#16A34A">res = provider.evaluate_answer(...) # Attempt</text>
                    <text x="20" y="96" class="code-text" fill="#16A34A">if res: return res # Fast Exit on Success</text>
                    <text x="8" y="112" class="code-text" fill="#92400E"># Auto 120s cooldown trigger on HTTP 429 quota exception</text>
                </g>
            </g>
        </g>
    </g>

    <!-- ============================================================== -->
    <!-- PANEL 2 (CENTER): 4-TIER FAILOVER CASCADE & 429 WALKTHROUGH    -->
    <!-- Coordinates: x: 515, y: 75, w: 830, h: 1025                    -->
    <!-- ============================================================== -->
    <g transform="translate(515, 75)">
        <rect width="830" height="1025" rx="8" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1.3" />
        
        <!-- Header Bar -->
        <rect width="830" height="38" rx="8" fill="#1E40AF" />
        <rect y="30" width="830" height="8" fill="#1E40AF" />
        <text x="16" y="24" class="panel-header-title">2. Four-Tier Fault-Tolerant AI Provider Cascade</text>
        <text x="814" y="24" text-anchor="end" class="panel-header-sub">Dynamic Provider Routing &amp; Rate-Limit Cooldown Walkthrough</text>

        <!-- TIER 1: LOCAL OFFLINE VISION -->
        <g transform="translate(20, 52)">
            <rect width="790" height="120" rx="6" fill="#FFFFFF" stroke="#059669" stroke-width="1.5" />
            <!-- Top Status Strip -->
            <rect width="790" height="26" rx="6" fill="#D1FAE5" />
            <rect y="20" width="790" height="6" fill="#D1FAE5" />
            <text x="14" y="18" class="tier-title" fill="#065F46">TIER 1: LOCAL OFFLINE MULTIMODAL VISION (Moondream2 / Ollama)</text>
            
            <rect x="545" y="4" width="115" height="18" rx="3" fill="#059669" />
            <text x="602" y="16" text-anchor="middle" class="badge-text" fill="#FFFFFF">$0.00 TOKEN COST</text>
            
            <rect x="668" y="4" width="108" height="18" rx="3" fill="#047857" />
            <text x="722" y="16" text-anchor="middle" class="badge-text" fill="#FFFFFF">100% AIR-GAPPED</text>

            <g transform="translate(14, 34)">
                <text x="0" y="12" class="card-desc">• <tspan font-weight="700">Zero Cloud Dependency:</tspan> Self-hosted via Ollama daemon (`http://127.0.0.1:11434/api/generate`) on workstation CPU.</text>
                <text x="0" y="26" class="card-desc">• <tspan font-weight="700">Downsampling Optimization:</tspan> Input crops downscaled to <tspan font-weight="700" fill="#059669">800px width (LANCZOS)</tspan> and compressed to JPEG Q75.</text>
                <text x="0" y="40" class="card-desc">• <tspan font-weight="700">CPU Execution Metrics:</tspan> Evaluates full script in ~14.0 seconds with memory footprint capped under 1.8 GB RAM.</text>
                
                <g transform="translate(0, 50)">
                    <rect width="762" height="22" rx="3" fill="#ECFDF5" stroke="#A7F3D0" stroke-width="0.8" />
                    <text x="8" y="15" class="code-text" fill="#047857">LocalOfflineVisionProvider(model='moondream', endpoint='http://127.0.0.1:11434/api/generate')</text>
                </g>
            </g>
        </g>

        <!-- CONNECTOR 1 -> 2 -->
        <path d="M 415 172 L 415 198" fill="none" stroke="#64748B" stroke-width="2" marker-end="url(#arrSlate)" />

        <!-- TIER 2: HIGH-SPEED CLOUD LLM (GROQ) -->
        <g transform="translate(20, 202)">
            <rect width="790" height="120" rx="6" fill="#FFFFFF" stroke="#D97706" stroke-width="1.5" />
            <rect width="790" height="26" rx="6" fill="#FEF3C7" />
            <rect y="20" width="790" height="6" fill="#FEF3C7" />
            <text x="14" y="18" class="tier-title" fill="#92400E">TIER 2: HIGH-SPEED CLOUD LLM (Groq Llama-3.3 70B Versatile)</text>
            
            <rect x="545" y="4" width="115" height="18" rx="3" fill="#D97706" />
            <text x="602" y="16" text-anchor="middle" class="badge-text" fill="#FFFFFF">0.8s SUB-SECOND</text>
            
            <rect x="668" y="4" width="108" height="18" rx="3" fill="#B45309" />
            <text x="722" y="16" text-anchor="middle" class="badge-text" fill="#FFFFFF">LPU ACCELERATED</text>

            <g transform="translate(14, 34)">
                <text x="0" y="12" class="card-desc">• <tspan font-weight="700">Language Processing Unit (LPU):</tspan> Ultra-low latency tensor inference delivering sub-second reasoning execution.</text>
                <text x="0" y="26" class="card-desc">• <tspan font-weight="700">Text-Heavy Evaluation:</tspan> Ideal for transcribed OCR solutions, detailed rubric comparisons, and formula derivations.</text>
                <text x="0" y="40" class="card-desc">• <tspan font-weight="700">Structured JSON Output:</tspan> Enforces native JSON mode schema with deterministic confidence score calculation.</text>
                
                <g transform="translate(0, 50)">
                    <rect width="762" height="22" rx="3" fill="#FFFBEB" stroke="#FDE68A" stroke-width="0.8" />
                    <text x="8" y="15" class="code-text" fill="#92400E">GroqProvider(model='llama-3.3-70b-versatile', temperature=0.1, response_format={{'type': 'json_object'}})</text>
                </g>
            </g>
        </g>

        <!-- CONNECTOR 2 -> 3 -->
        <path d="M 415 322 L 415 348" fill="none" stroke="#64748B" stroke-width="2" marker-end="url(#arrSlate)" />

        <!-- TIER 3: CLOUD GATEWAY AGGREGATOR (OPENROUTER) -->
        <g transform="translate(20, 352)">
            <rect width="790" height="120" rx="6" fill="#FFFFFF" stroke="#7C3AED" stroke-width="1.5" />
            <rect width="790" height="26" rx="6" fill="#EDE9FE" />
            <rect y="20" width="790" height="6" fill="#EDE9FE" />
            <text x="14" y="18" class="tier-title" fill="#5B21B6">TIER 3: CLOUD GATEWAY AGGREGATOR (OpenRouter Multi-Model Router)</text>
            
            <rect x="545" y="4" width="115" height="18" rx="3" fill="#7C3AED" />
            <text x="602" y="16" text-anchor="middle" class="badge-text" fill="#FFFFFF">DYNAMIC ROUTING</text>
            
            <rect x="668" y="4" width="108" height="18" rx="3" fill="#6D28D9" />
            <text x="722" y="16" text-anchor="middle" class="badge-text" fill="#FFFFFF">MULTI-PROVIDER</text>

            <g transform="translate(14, 34)">
                <text x="0" y="12" class="card-desc">• <tspan font-weight="700">Dynamic Multi-Model Gateway:</tspan> Seamless access to Claude 3.5 Sonnet, Mistral Large, and DeepSeek V3.</text>
                <text x="0" y="26" class="card-desc">• <tspan font-weight="700">Unified Credit Pool:</tspan> Single institutional API key eliminates fragmented billing across disparate AI vendors.</text>
                <text x="0" y="40" class="card-desc">• <tspan font-weight="700">Global Failover Protection:</tspan> Automatically routes around regional cloud outages with zero code changes.</text>
                
                <g transform="translate(0, 50)">
                    <rect width="762" height="22" rx="3" fill="#F5F3FF" stroke="#DDD6FE" stroke-width="0.8" />
                    <text x="8" y="15" class="code-text" fill="#5B21B6">OpenRouterProvider(default_model='anthropic/claude-3.5-sonnet', fallback_model='deepseek/deepseek-chat')</text>
                </g>
            </g>
        </g>

        <!-- CONNECTOR 3 -> 4 -->
        <path d="M 415 472 L 415 498" fill="none" stroke="#64748B" stroke-width="2" marker-end="url(#arrSlate)" />

        <!-- TIER 4: ADVANCED MULTIMODAL VISION (GEMINI & OPENAI) -->
        <g transform="translate(20, 502)">
            <rect width="790" height="120" rx="6" fill="#FFFFFF" stroke="#2563EB" stroke-width="1.5" />
            <rect width="790" height="26" rx="6" fill="#DBEAFE" />
            <rect y="20" width="790" height="6" fill="#DBEAFE" />
            <text x="14" y="18" class="tier-title" fill="#1E40AF">TIER 4: ADVANCED MULTIMODAL FRONTIER VISION (Gemini 2.5 Flash / GPT-4o)</text>
            
            <rect x="545" y="4" width="115" height="18" rx="3" fill="#2563EB" />
            <text x="602" y="16" text-anchor="middle" class="badge-text" fill="#FFFFFF">DEEP VISUAL OBE</text>
            
            <rect x="668" y="4" width="108" height="18" rx="3" fill="#1D4ED8" />
            <text x="722" y="16" text-anchor="middle" class="badge-text" fill="#FFFFFF">DIAGRAM REASON</text>

            <g transform="translate(14, 34)">
                <text x="0" y="12" class="card-desc">• <tspan font-weight="700">Complex Multimodal Grounding:</tspan> Evaluates hand-drawn diagrams, circuit schematics, graphs, and spatial layouts.</text>
                <text x="0" y="26" class="card-desc">• <tspan font-weight="700">Native Multi-Image Ingestion:</tspan> Ingests multi-page answer script bounding crops directly via high-res visual tokens.</text>
                <text x="0" y="40" class="card-desc">• <tspan font-weight="700">Frontier Reasoning Quality:</tspan> Pinpoints step-by-step mathematical proofs with rigorous rubric step-marking.</text>
                
                <g transform="translate(0, 50)">
                    <rect width="762" height="22" rx="3" fill="#EFF6FF" stroke="#BFDBFE" stroke-width="0.8" />
                    <text x="8" y="15" class="code-text" fill="#1E40AF">GeminiProvider(model='gemini-2.5-flash') / OpenAIProvider(model='gpt-4o')</text>
                </g>
            </g>
        </g>

        <!-- ========================================================== -->
        <!-- FAILOVER SCENARIO SIMULATION CARD (THE HTTP 429 EVENT)     -->
        <!-- ========================================================== -->
        <g transform="translate(20, 642)">
            <rect width="790" height="360" rx="6" fill="#FFFFFF" stroke="#DC2626" stroke-width="1.6" />
            <!-- Header Strip -->
            <rect width="790" height="30" rx="6" fill="#FEE2E2" />
            <rect y="24" width="790" height="6" fill="#FEE2E2" />
            <text x="14" y="20" font-family="'Segoe UI', Arial, sans-serif" font-size="12px" font-weight="800" fill="#991B1B">LIVE FAILOVER EXECUTION WALKTHROUGH: CLOUD HTTP 429 RATE-LIMIT RECOVERY</text>
            <rect x="668" y="5" width="108" height="20" rx="3" fill="#DC2626" />
            <text x="722" y="19" text-anchor="middle" class="badge-text" fill="#FFFFFF">ACTIVE EVENT</text>

            <!-- 4-STEP TIMELINE -->
            <g transform="translate(18, 44)">
                
                <!-- STEP 1: INITIAL DISPATCH -->
                <g transform="translate(0, 0)">
                    <circle cx="16" cy="16" r="16" fill="#DBEAFE" stroke="#3B82F6" stroke-width="1.5" />
                    <text x="16" y="21" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif" font-size="12px" font-weight="800" fill="#1E40AF">1</text>
                    <g transform="translate(42, 2)">
                        <text x="0" y="12" font-family="'Segoe UI', Arial, sans-serif" font-size="10.5px" font-weight="700" fill="#0F172A">Primary Dispatch to Multimodal Frontier Provider (Gemini 2.5 Flash)</text>
                        <text x="0" y="26" class="card-desc">TaskRouter dispatches Question 1 script crop (CSE 4385 Histogram Equalization) with max_marks=25.</text>
                    </g>
                </g>

                <!-- STEP 2: HTTP 429 QUOTA EXHAUSTED -->
                <g transform="translate(0, 62)">
                    <circle cx="16" cy="16" r="16" fill="#FEE2E2" stroke="#DC2626" stroke-width="1.5" />
                    <text x="16" y="21" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif" font-size="12px" font-weight="800" fill="#991B1B">2</text>
                    <g transform="translate(42, 2)">
                        <text x="0" y="12" font-family="'Segoe UI', Arial, sans-serif" font-size="10.5px" font-weight="800" fill="#DC2626">Cloud Quota Exhaustion Encountered: HTTP 429 (Resource Exhausted)</text>
                        <text x="0" y="26" class="card-desc">Google Gemini returns: <tspan font-family="Consolas" font-weight="700" fill="#DC2626">"429: Resource has been exhausted (check quota)"</tspan>. Evaluator catches exception.</text>
                    </g>
                </g>

                <!-- STEP 3: COOLDOWN REGISTRY ENGAGEMENT -->
                <g transform="translate(0, 124)">
                    <circle cx="16" cy="16" r="16" fill="#FEF3C7" stroke="#F59E0B" stroke-width="1.5" />
                    <text x="16" y="21" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif" font-size="12px" font-weight="800" fill="#92400E">3</text>
                    <g transform="translate(42, 2)">
                        <text x="0" y="12" font-family="'Segoe UI', Arial, sans-serif" font-size="10.5px" font-weight="700" fill="#92400E">ProviderHealthTracker Engages 120-Second Immutable Cooldown</text>
                        <text x="0" y="26" class="card-desc">GeminiProvider flagged with <tspan font-family="Consolas" font-weight="700">expiry = monotonic() + 120s</tspan>. All subsequent student questions bypass Gemini instantly.</text>
                    </g>
                </g>

                <!-- STEP 4: ZERO-DELAY FAILOVER TO GROQ / MOONDREAM2 -->
                <g transform="translate(0, 186)">
                    <circle cx="16" cy="16" r="16" fill="#DCFCE7" stroke="#16A34A" stroke-width="1.5" />
                    <text x="16" y="21" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif" font-size="12px" font-weight="800" fill="#15803D">4</text>
                    <g transform="translate(42, 2)">
                        <text x="0" y="12" font-family="'Segoe UI', Arial, sans-serif" font-size="10.5px" font-weight="800" fill="#15803D">Instant Zero-Delay Failover to Groq Llama-3.3 70B (0.8s) &amp; Moondream2</text>
                        <text x="0" y="26" class="card-desc">Request seamlessly transferred. Groq generates complete rubric marks &amp; feedback in 0.8s without failing the teacher's session!</text>
                    </g>
                </g>

                <!-- Status Callout Strip -->
                <g transform="translate(0, 248)">
                    <rect width="754" height="38" rx="4" fill="#F0FDF4" stroke="#86EFAC" stroke-width="1" />
                    <text x="12" y="24" font-family="'Segoe UI', Arial, sans-serif" font-size="10.5px" font-weight="700" fill="#166534">✓ Result: Continuous 100% Evaluation Uptime | Zero Student Script Drop | 0ms Teacher Disruption</text>
                </g>
            </g>
        </g>
    </g>

    <!-- ============================================================== -->
    <!-- PANEL 3 (RIGHT): OUTPUT SANITIZER & WORKBENCH INTEGRATION      -->
    <!-- Coordinates: x: 1365, y: 75, w: 450, h: 1025                    -->
    <!-- ============================================================== -->
    <g transform="translate(1365, 75)">
        <rect width="450" height="1025" rx="8" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1.3" />
        
        <!-- Header Bar -->
        <rect width="450" height="38" rx="8" fill="#047857" />
        <rect y="30" width="450" height="8" fill="#047857" />
        <text x="16" y="24" class="panel-header-title">3. Sanitization &amp; Teacher Workbench</text>
        <text x="434" y="24" text-anchor="end" class="panel-header-sub">JSON Repair &amp; UI Delivery</text>

        <!-- CARD 3A: JSON REPAIR & LATEX SANITIZER -->
        <g transform="translate(18, 52)">
            <rect width="414" height="230" rx="6" fill="#FFFFFF" stroke="#059669" stroke-width="1.4" />
            <rect width="414" height="24" rx="6" fill="#D1FAE5" />
            <rect y="18" width="414" height="6" fill="#D1FAE5" />
            <text x="12" y="16" class="card-title" fill="#065F46">JSON SANITIZATION &amp; LATEX REPAIR PIPELINE</text>
            
            <g transform="translate(12, 34)">
                <text x="0" y="12" class="card-desc">• <tspan font-weight="700">Markdown Code Stripper:</tspan> Removes <tspan font-family="Consolas">```json ... ```</tspan> wraps</text>
                <text x="0" y="26" class="card-desc">• <tspan font-weight="700">LaTeX Escape Normalizer:</tspan> Repairs raw math backslashes</text>
                <text x="0" y="40" class="card-desc">  Converts <tspan font-family="Consolas" fill="#DC2626">\\frac, \\theta, \\sum</tspan> to escaped <tspan font-family="Consolas" fill="#16A34A">\\\\frac, \\\\theta, \\\\sum</tspan></text>
                <text x="0" y="54" class="card-desc">• <tspan font-weight="700">Syntax Repair Engine:</tspan> Resolves trailing commas and quotes</text>
                <text x="0" y="68" class="card-desc">• <tspan font-weight="700">Schema Validation:</tspan> Guarantees strictly valid JSON payload</text>

                <g transform="translate(0, 78)">
                    <rect width="390" height="102" rx="4" fill="#F0FDF4" stroke="#A7F3D0" stroke-width="0.8" />
                    <text x="8" y="16" class="code-text" fill="#047857">def sanitize_ai_response(raw_text: str) -&gt; dict:</text>
                    <text x="20" y="32" class="code-text" fill="#0F172A">cleaned = re.sub(r"^```[a-z]*\\s*", "", raw_text.strip())</text>
                    <text x="20" y="48" class="code-text" fill="#0F172A">cleaned = re.sub(r"\\s*```$", "", cleaned)</text>
                    <text x="20" y="64" class="code-text" fill="#2563EB">cleaned = re.sub(r'\\\\(?![/"\\\\bfnrtu])', r'\\\\\\\\', cleaned)</text>
                    <text x="20" y="80" class="code-text" fill="#16A34A">return json.loads(cleaned) # Validated Structured Dict</text>
                </g>
            </g>
        </g>

        <!-- DOWN ARROW 3A -> 3B -->
        <path d="M 225 282 L 225 304" fill="none" stroke="#64748B" stroke-width="2" marker-end="url(#arrSlate)" />

        <!-- CARD 3B: ACADEMIC SCORING GUARDRAILS -->
        <g transform="translate(18, 308)">
            <rect width="414" height="214" rx="6" fill="#FFFFFF" stroke="#0284C7" stroke-width="1.4" />
            <rect width="414" height="24" rx="6" fill="#E0F2FE" />
            <rect y="18" width="414" height="6" fill="#E0F2FE" />
            <text x="12" y="16" class="card-title" fill="#0369A1">SCORE VALIDATION &amp; BOUND ENFORCEMENT</text>
            
            <g transform="translate(12, 34)">
                <text x="0" y="12" class="card-desc">• <tspan font-weight="700">Hard Bound Clamping:</tspan> Strictly enforces <tspan font-family="Consolas" font-weight="700">0 &lt;= score &lt;= max_marks</tspan></text>
                <text x="0" y="26" class="card-desc">• <tspan font-weight="700">Criteria Sum Consistency:</tspan> Step marks sum to question total</text>
                <text x="0" y="40" class="card-desc">• <tspan font-weight="700">Zero Score Fabrication:</tspan> Non-evaluated answers receive 0 with alert</text>
                <text x="0" y="54" class="card-desc">• <tspan font-weight="700">Confidence Metric:</tspan> AI assigns confidence score (0.0 to 1.0)</text>

                <!-- Validated Response Card Preview -->
                <g transform="translate(0, 68)">
                    <rect width="390" height="92" rx="4" fill="#F8FAFC" stroke="#BAE6FD" stroke-width="0.8" />
                    <text x="8" y="15" class="code-text" fill="#0369A1">{{ "question_no": "1", "max_marks": 25.0, "awarded_marks": 23.5,</text>
                    <text x="8" y="30" class="code-text" fill="#0F172A">  "confidence": 0.96, "failover_provider": "GroqProvider",</text>
                    <text x="8" y="45" class="code-text" fill="#16A34A">  "feedback": "Correct CDF derivation and 3rd row matrix calculation.</text>
                    <text x="8" y="60" class="code-text" fill="#16A34A">               Minor rounding discrepancy on pixel s(76).",</text>
                    <text x="8" y="75" class="code-text" fill="#0369A1">  "rubric_breakdown": [{{ "co": "CO2", "po": "PO1", "marks": 23.5 }}] }}</text>
                </g>
            </g>
        </g>

        <!-- DOWN ARROW 3B -> 3C -->
        <path d="M 225 522 L 225 544" fill="none" stroke="#64748B" stroke-width="2" marker-end="url(#arrSlate)" />

        <!-- CARD 3C: SPLIT-SCREEN WORKBENCH INTEGRATION -->
        <g transform="translate(18, 548)">
            <rect width="414" height="454" rx="6" fill="#FFFFFF" stroke="#475569" stroke-width="1.4" />
            <rect width="414" height="24" rx="6" fill="#F1F5F9" />
            <rect y="18" width="414" height="6" fill="#F1F5F9" />
            <text x="12" y="16" class="card-title" fill="#1E293B">TEACHER EVALUATION WORKBENCH DELIVERY</text>
            
            <g transform="translate(12, 34)">
                <text x="0" y="12" class="card-desc">• Dispatched to <tspan font-weight="700">Split-Screen Teacher Workbench (Figure 3.10)</tspan></text>
                <text x="0" y="26" class="card-desc">• Real-time notification badge informs teacher of active failover</text>
                
                <!-- UI Notification Badge Card -->
                <g transform="translate(0, 36)">
                    <rect width="390" height="50" rx="4" fill="#FEF3C7" stroke="#F59E0B" stroke-width="1" />
                    <text x="10" y="16" font-family="'Segoe UI', Arial, sans-serif" font-size="10px" font-weight="800" fill="#92400E">⚡ AI Failover Alert: Evaluated via Tier 2 (Groq Llama-3.3)</text>
                    <text x="10" y="30" font-family="'Segoe UI', Arial, sans-serif" font-size="8.5px" font-weight="500" fill="#78350F">Primary Gemini tier on 120s cooldown (HTTP 429). Execution time: 0.82s.</text>
                    <text x="10" y="42" font-family="'Segoe UI', Arial, sans-serif" font-size="8.5px" font-weight="700" fill="#166534">✓ Student grading session completed seamlessly with zero data loss.</text>
                </g>

                <!-- UI Mockup of Split-Screen Studio Item -->
                <g transform="translate(0, 94)">
                    <rect width="390" height="186" rx="5" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1" />
                    <rect width="390" height="24" rx="5" fill="#0F172A" />
                    <rect y="18" width="390" height="6" fill="#0F172A" />
                    <circle cx="12" cy="12" r="4" fill="#EF4444" />
                    <circle cx="24" cy="12" r="4" fill="#F59E0B" />
                    <circle cx="36" cy="12" r="4" fill="#10B981" />
                    <text x="48" y="15" font-family="'Segoe UI', Arial, sans-serif" font-size="9.5px" font-weight="700" fill="#FFFFFF">Teacher Verification Modal — Question 1 (25 Marks)</text>

                    <g transform="translate(10, 34)">
                        <text x="0" y="12" class="card-desc">Course: <tspan font-weight="700">CSE 4385 (CV &amp; IP)</tspan> | Student: <tspan font-weight="700">Tanvir Hasan (22103045)</tspan></text>
                        
                        <!-- Score Slider / Input -->
                        <g transform="translate(0, 20)">
                            <rect width="220" height="24" rx="4" fill="#FFFFFF" stroke="#CBD5E1" />
                            <text x="8" y="16" font-family="'Segoe UI', Arial, sans-serif" font-size="9.5px" font-weight="700" fill="#0F172A">AI Suggested Score: 23.5 / 25.0</text>
                            
                            <rect x="230" y="0" width="140" height="24" rx="4" fill="#16A34A" />
                            <text x="300" y="16" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif" font-size="9.5px" font-weight="700" fill="#FFFFFF">Accept Score ✓</text>
                        </g>

                        <!-- Teacher Override Input -->
                        <g transform="translate(0, 52)">
                            <text x="0" y="12" class="card-desc">Manual Override / Teacher Notes:</text>
                            <rect y="18" width="370" height="34" rx="3" fill="#FFFFFF" stroke="#CBD5E1" />
                            <text x="6" y="34" font-family="'Segoe UI', Arial, sans-serif" font-size="8.5px" font-style="italic" fill="#64748B">"Excellent CDF calculations. Verified 3rd row transformation."</text>
                        </g>
                        
                        <!-- OBE Sync Pill -->
                        <g transform="translate(0, 114)">
                            <rect width="370" height="24" rx="3" fill="#ECFDF5" stroke="#A7F3D0" />
                            <text x="185" y="16" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif" font-size="9px" font-weight="700" fill="#065F46">Synchronized with Course OBE Tabulation (CT 10% + Mid 25%)</text>
                        </g>
                    </g>
                </g>

                <g transform="translate(0, 290)">
                    <rect width="390" height="42" rx="4" fill="#F1F5F9" stroke="#E2E8F0" stroke-width="0.8" />
                    <text x="195" y="18" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif" font-size="9.5px" font-weight="700" fill="#334155">Direct Database Persistence &amp; 8-Sheet Tabulation</text>
                    <text x="195" y="32" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif" font-size="8.5px" font-weight="500" fill="#64748B">Saves to StudentGradeRecord with bi-directional Excel sync</text>
                </g>
            </g>
        </g>
    </g>

    <!-- Bottom Metadata Bar -->
    <g transform="translate(45, 1118)">
        <text x="0" y="0" class="footer-info">IntelliGrade AI Engine Core — Figure 3.9: Resilient Multi-Provider AI Evaluation Failover Architecture</text>
        <text x="1815" y="0" text-anchor="end" class="footer-info">Target Dimensions: 6.2" × 3.8" (300 DPI, 1860 × 1140 px) | Pure Light Mode | Publication-Ready</text>
    </g>
</svg>
"""
    return svg

def main():
    output_dir = r"F:\Hijbullah\IntelliGrade\materials"
    os.makedirs(output_dir, exist_ok=True)
    
    svg_content = generate_svg()
    
    # Save single image file: Figure-3.9.png
    doc = fitz.open(stream=svg_content.encode("utf-8"), filetype="svg")
    page = doc[0]
    pix = page.get_pixmap(matrix=fitz.Matrix(1, 1), alpha=False)
    
    png_filename = "Figure-3.9.png"
    png_path = os.path.join(output_dir, png_filename)
    
    temp_path = os.path.join(output_dir, "temp_39.png")
    pix.save(temp_path)
    
    img = Image.open(temp_path)
    if img.size != (1860, 1140):
        img = img.resize((1860, 1140), Image.Resampling.LANCZOS)
    
    img.save(png_path, dpi=(300, 300), format="PNG")
    img.close()
    
    if os.path.exists(temp_path):
        os.remove(temp_path)
        
    print(f"Successfully generated single 300 DPI PNG at: {png_path}")

if __name__ == "__main__":
    main()
