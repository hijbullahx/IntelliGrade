"""
Figure 2.1 Generator: Organizational Structure of Al Hadi Enterprise and Software Development Team
Output Dimensions: Width: 6.0 in, Height: 3.5 in @ 300 DPI (1800 x 1050 px)
Pure light mode, academic publication aesthetic.
Embeds Al Hadi Enterprise logo (materials/Alhadi_logo_dark.png) in light mode.
Outputs ONLY: materials/Figure-2.1.png
"""

import os
import fitz  # PyMuPDF
from PIL import Image

OUTPUT_PNG = r"F:\Hijbullah\IntelliGrade\materials\Figure-2.1.png"
LOGO_PATH = r"F:\Hijbullah\IntelliGrade\materials\Alhadi_logo_dark.png"

def create_figure_2_1():
    width = 1800
    height = 1050

    svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
    <defs>
        <style>
            .fig-title {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 20px; font-weight: 800; fill: #0F172A; }}
            .fig-sub {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 12px; font-weight: 600; fill: #475569; }}
            
            .exec-title {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 14.5px; font-weight: 800; fill: #FFFFFF; text-anchor: middle; }}
            .exec-sub {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 10px; font-weight: 600; fill: #E2E8F0; text-anchor: middle; }}
            
            .dept-title {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 12px; font-weight: 800; fill: #FFFFFF; text-anchor: middle; }}
            
            .section-header-title {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 13.5px; font-weight: 800; fill: #FFFFFF; }}
            .section-header-sub {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 10.5px; font-weight: 600; fill: #E2E8F0; }}
            
            .card-title {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 11.5px; font-weight: 800; letter-spacing: 0.3px; }}
            .body-text {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 10px; fill: #1E293B; }}
            .body-text-bold {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 10px; font-weight: 700; fill: #0F172A; }}
            .code-text {{ font-family: 'Consolas', monospace; font-size: 9.5px; fill: #0F172A; }}
            .meta-tag {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 9px; font-weight: 700; }}
            .footer-text {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 10.5px; font-weight: 500; fill: #64748B; }}
        </style>

        <marker id="arrBlue" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <polygon points="0,1.5 8,5 0,8.5" fill="#2563EB" />
        </marker>
        <marker id="arrGreen" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <polygon points="0,1.5 8,5 0,8.5" fill="#059669" />
        </marker>

        <filter id="cardShadow" x="-2%" y="-1%" width="104%" height="104%">
            <feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#0F172A" flood-opacity="0.06" />
        </filter>
        <filter id="execShadow" x="-3%" y="-2%" width="106%" height="106%">
            <feDropShadow dx="0" dy="3" stdDeviation="4" flood-color="#1E3A8A" flood-opacity="0.12" />
        </filter>
        <filter id="traineeGlow" x="-3%" y="-2%" width="106%" height="106%">
            <feDropShadow dx="0" dy="3" stdDeviation="5" flood-color="#059669" flood-opacity="0.15" />
        </filter>
    </defs>

    <!-- Canvas Background -->
    <rect width="{width}" height="{height}" fill="#FFFFFF" />

    <!-- Top Figure Header -->
    <g transform="translate(35, 14)">
        <rect x="0" y="3" width="5" height="46" rx="2" fill="#2563EB" />
        <text x="16" y="22" class="fig-title">Figure 2.1: Organizational Structure of Al Hadi Enterprise and Software Development Team</text>
        <text x="16" y="42" class="fig-sub">Functional Governance Hierarchy, Operational Departments, Technical Engineering Sub-Tree, and Practicum Trainee Placement</text>
    </g>

    <!-- Corporate Brand Badge in Header (Right Side, logo will be composited here) -->
    <g transform="translate(1520, 10)">
        <rect width="245" height="56" rx="6" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.2" />
        <!-- Logo pasted at (1530, 14), text on the right: -->
        <text x="110" y="26" font-family="'Segoe UI', Arial, sans-serif" font-size="11px" font-weight="800" fill="#0F172A">Al Hadi Enterprise</text>
        <text x="110" y="42" font-family="'Segoe UI', Arial, sans-serif" font-size="9px" font-weight="700" fill="#2563EB">alhadiexpress.com.bd</text>
    </g>

    <!-- ============================================================== -->
    <!-- TIER 1: EXECUTIVE MANAGEMENT (MANAGING DIRECTOR / CEO)         -->
    <!-- Center: x: 900, y: 84, w: 480, h: 78                           -->
    <!-- ============================================================== -->
    <g transform="translate(660, 84)" filter="url(#execShadow)">
        <rect width="480" height="78" rx="8" fill="#1E3A8A" stroke="#1E40AF" stroke-width="1.4" />
        
        <!-- Symmetrical Center Top Badge -->
        <rect x="165" y="8" width="150" height="18" rx="3" fill="#2563EB" />
        <text x="240" y="20.5" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif" font-size="9px" font-weight="800" fill="#FFFFFF">EXECUTIVE GOVERNANCE</text>

        <text x="240" y="45" text-anchor="middle" class="exec-title">Managing Director / Chief Executive Officer (CEO)</text>
        <text x="240" y="63" text-anchor="middle" class="exec-sub">Strategic Leadership, Corporate Vision, Business Expansion &amp; Operational Governance</text>
    </g>

    <!-- Vertical Trunk line from CEO to Distribution Bus (x: 900, y: 162 to 205) -->
    <line x1="900" y1="162" x2="900" y2="205" stroke="#1E3A8A" stroke-width="2.5" />

    <!-- Horizontal Distribution Bus across 5 Functional Departments -->
    <!-- From x: 197 (center Dept 1) to x: 1603 (center Dept 5) -->
    <line x1="197" y1="205" x2="1603" y2="205" stroke="#1E3A8A" stroke-width="2" />

    <!-- Drops into 5 Departments -->
    <line x1="197" y1="205" x2="197" y2="225" stroke="#475569" stroke-width="1.8" />
    <line x1="546" y1="205" x2="546" y2="225" stroke="#0F766E" stroke-width="1.8" />
    <line x1="900" y1="205" x2="900" y2="225" stroke="#1D4ED8" stroke-width="2.5" />
    <line x1="1254" y1="205" x2="1254" y2="225" stroke="#B45309" stroke-width="1.8" />
    <line x1="1603" y1="205" x2="1603" y2="225" stroke="#047857" stroke-width="1.8" />

    <!-- ============================================================== -->
    <!-- TIER 2: FIVE FUNCTIONAL CORE DEPARTMENTS                       -->
    <!-- Total width: 1730 px, each card: w: 324 px, h: 142 px, y: 225  -->
    <!-- ============================================================== -->

    <!-- DEPT 1: Business Operations & Administration (x: 35) -->
    <g transform="translate(35, 225)" filter="url(#cardShadow)">
        <rect width="324" height="142" rx="6" fill="#F8FAFC" stroke="#94A3B8" stroke-width="1.2" />
        <rect width="324" height="34" rx="6" fill="#475569" />
        <rect y="26" width="324" height="8" fill="#475569" />
        <text x="162" y="22" text-anchor="middle" class="dept-title">Business Operations &amp; Admin</text>
        
        <g transform="translate(14, 46)">
            <text x="0" y="14" class="body-text-bold">• General Administration &amp; Corporate Affairs</text>
            <text x="0" y="30" class="body-text-bold">• Financial Accounting, Budgeting &amp; Payroll</text>
            <text x="0" y="46" class="body-text-bold">• Human Resources &amp; Talent Recruitment</text>
            <text x="0" y="62" class="body-text-bold">• Statutory Regulatory &amp; Legal Compliance</text>
            <text x="0" y="80" class="meta-tag" fill="#475569">Role: Institutional Infrastructure &amp; Finance</text>
        </g>
    </g>

    <!-- DEPT 2: E-Commerce & Digital Sales (x: 384) -->
    <g transform="translate(384, 225)" filter="url(#cardShadow)">
        <rect width="324" height="142" rx="6" fill="#F8FAFC" stroke="#14B8A6" stroke-width="1.2" />
        <rect width="324" height="34" rx="6" fill="#0F766E" />
        <rect y="26" width="324" height="8" fill="#0F766E" />
        <text x="162" y="22" text-anchor="middle" class="dept-title">E-Commerce &amp; Digital Sales</text>
        
        <g transform="translate(14, 46)">
            <text x="0" y="14" class="body-text-bold">• E-Commerce Storefront (alhadiexpress.com.bd)</text>
            <text x="0" y="30" class="body-text-bold">• Digital Marketing, SEO &amp; Brand Campaign</text>
            <text x="0" y="46" class="body-text-bold">• Merchant Onboarding &amp; Vendor Management</text>
            <text x="0" y="62" class="body-text-bold">• Promotional Strategy, Pricing &amp; Analytics</text>
            <text x="0" y="80" class="meta-tag" fill="#0F766E">Role: Commercial Revenue &amp; Customer Growth</text>
        </g>
    </g>

    <!-- DEPT 3: Technical & Software Development (CORE ANCHOR) (x: 733) -->
    <g transform="translate(733, 225)" filter="url(#cardShadow)">
        <rect width="334" height="142" rx="6" fill="#EFF6FF" stroke="#2563EB" stroke-width="1.8" />
        <rect width="334" height="34" rx="6" fill="#1D4ED8" />
        <rect y="26" width="334" height="8" fill="#1D4ED8" />
        <text x="167" y="22" text-anchor="middle" class="dept-title">Technical &amp; Software Development</text>
        
        <g transform="translate(14, 46)">
            <text x="0" y="13" class="body-text-bold" fill="#1E40AF">• Enterprise Web Systems &amp; E-Commerce Apps</text>
            <text x="0" y="28" class="body-text-bold" fill="#1E40AF">• Custom Business Software &amp; Internal ERP</text>
            <text x="0" y="43" class="body-text-bold" fill="#1E40AF">• Multimodal AI Systems (IntelliGrade R&amp;D)</text>
            <text x="0" y="58" class="body-text-bold" fill="#1E40AF">• Cloud Server Architecture &amp; Database Ops</text>
            
            <!-- Bottom Core Focus Pill -->
            <rect x="2" y="66" width="302" height="18" rx="3" fill="#FEF3C7" stroke="#F59E0B" stroke-width="1" />
            <text x="153" y="78.5" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif" font-size="8.5px" font-weight="800" fill="#92400E">★ CORE FOCUS: HOUSING PRACTICUM TRAINEE</text>
        </g>
    </g>

    <!-- DEPT 4: Customer Support & Service Operations (x: 1092) -->
    <g transform="translate(1092, 225)" filter="url(#cardShadow)">
        <rect width="324" height="142" rx="6" fill="#F8FAFC" stroke="#F59E0B" stroke-width="1.2" />
        <rect width="324" height="34" rx="6" fill="#B45309" />
        <rect y="26" width="324" height="8" fill="#B45309" />
        <text x="162" y="22" text-anchor="middle" class="dept-title">Customer Support &amp; CRM</text>
        
        <g transform="translate(14, 46)">
            <text x="0" y="14" class="body-text-bold">• Multi-Channel Helpdesk &amp; Inbound Inquiries</text>
            <text x="0" y="30" class="body-text-bold">• Order Verification &amp; Pre-Delivery Clearance</text>
            <text x="0" y="46" class="body-text-bold">• Post-Sales Customer Satisfaction &amp; Feedback</text>
            <text x="0" y="62" class="body-text-bold">• Escalation Resolution &amp; CRM Data Logging</text>
            <text x="0" y="80" class="meta-tag" fill="#B45309">Role: Client Experience &amp; Retention</text>
        </g>
    </g>

    <!-- DEPT 5: Logistics & Order Fulfillment (x: 1441) -->
    <g transform="translate(1441, 225)" filter="url(#cardShadow)">
        <rect width="324" height="142" rx="6" fill="#F8FAFC" stroke="#10B981" stroke-width="1.2" />
        <rect width="324" height="34" rx="6" fill="#047857" />
        <rect y="26" width="324" height="8" fill="#047857" />
        <text x="162" y="22" text-anchor="middle" class="dept-title">Logistics &amp; Fulfillment</text>
        
        <g transform="translate(14, 46)">
            <text x="0" y="14" class="body-text-bold">• Central Warehousing &amp; Inventory Management</text>
            <text x="0" y="30" class="body-text-bold">• Quality Inspection, Packaging &amp; Barcoding</text>
            <text x="0" y="46" class="body-text-bold">• Courier Service Integration &amp; Dispatch Routing</text>
            <text x="0" y="62" class="body-text-bold">• Last-Mile Delivery Tracking &amp; Returns Reverse</text>
            <text x="0" y="80" class="meta-tag" fill="#047857">Role: Supply Chain Physical Execution</text>
        </g>
    </g>

    <!-- Connecting Trunk from Dept 3 to Engineering Hierarchy -->
    <line x1="900" y1="367" x2="900" y2="400" stroke="#1D4ED8" stroke-width="3" marker-end="url(#arrBlue)" />

    <!-- ============================================================== -->
    <!-- TIER 3: TECHNICAL & SOFTWARE DEVELOPMENT DEEP-DIVE CONTAINER   -->
    <!-- Coordinates: x: 35, y: 400, w: 1730, h: 605                    -->
    <!-- ============================================================== -->
    <g transform="translate(35, 400)" filter="url(#cardShadow)">
        <!-- Container Box -->
        <rect width="1730" height="605" rx="8" fill="#FFFFFF" stroke="#3B82F6" stroke-width="1.6" />
        
        <!-- Header Bar -->
        <rect width="1730" height="36" rx="8" fill="#1E40AF" />
        <rect y="28" width="1730" height="8" fill="#1E40AF" />
        <text x="16" y="23" class="section-header-title">Technical &amp; Software Development Function: Engineering Hierarchy &amp; Practicum Trainee Role</text>
        <text x="1714" y="23" text-anchor="end" class="section-header-sub">Integration of Custom Web Development with Enterprise Operations</text>

        <!-- ========================================================== -->
        <!-- SUB-PANEL 1: CROSS-FUNCTIONAL ENTERPRISE INTEGRATION (LEFT) -->
        <!-- Coordinates: x: 16, y: 50, w: 420, h: 540                  -->
        <!-- ========================================================== -->
        <g transform="translate(16, 50)">
            <rect width="420" height="540" rx="6" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1.2" />
            <rect width="420" height="26" rx="6" fill="#EEF2FF" />
            <rect y="20" width="420" height="6" fill="#EEF2FF" />
            <text x="12" y="17" class="card-title" fill="#3730A3">CROSS-FUNCTIONAL ENTERPRISE INTEGRATION</text>

            <g transform="translate(12, 36)">
                <!-- Integration Block 1 -->
                <g transform="translate(0, 0)">
                    <rect width="396" height="90" rx="4" fill="#FFFFFF" stroke="#0D9488" stroke-width="1" />
                    <text x="10" y="18" font-family="'Segoe UI', Arial, sans-serif" font-size="10.5px" font-weight="700" fill="#0F766E">🛒 E-Commerce Platform Engineering</text>
                    <text x="10" y="34" class="body-text">• Powers <tspan font-family="'Consolas', monospace" font-weight="700">alhadiexpress.com.bd</tspan> storefront architecture</text>
                    <text x="10" y="48" class="body-text">• Product catalogs, dynamic filtering, real-time stock sync</text>
                    <text x="10" y="62" class="body-text">• Payment gateway integrations (bKash, Nagad, SSLCommerz)</text>
                    <text x="10" y="78" class="code-text" fill="#0D9488">Sync Link: Bi-directional product &amp; transaction feeds</text>
                </g>

                <!-- Integration Block 2 -->
                <g transform="translate(0, 102)">
                    <rect width="396" height="90" rx="4" fill="#FFFFFF" stroke="#059669" stroke-width="1" />
                    <text x="10" y="18" font-family="'Segoe UI', Arial, sans-serif" font-size="10.5px" font-weight="700" fill="#047857">🚚 Logistics &amp; Courier API Automated Dispatch</text>
                    <text x="10" y="34" class="body-text">• Automated shipment booking via third-party courier APIs</text>
                    <text x="10" y="48" class="body-text">• Barcode &amp; packing slip generation for warehouse staff</text>
                    <text x="10" y="62" class="body-text">• Automated webhook listeners for real-time delivery status</text>
                    <text x="10" y="78" class="code-text" fill="#059669">Sync Link: Automated parcel tracking updates to customers</text>
                </g>

                <!-- Integration Block 3 -->
                <g transform="translate(0, 204)">
                    <rect width="396" height="90" rx="4" fill="#FFFFFF" stroke="#475569" stroke-width="1" />
                    <text x="10" y="18" font-family="'Segoe UI', Arial, sans-serif" font-size="10.5px" font-weight="700" fill="#334155">📊 Internal Business ERP &amp; Tabulation Systems</text>
                    <text x="10" y="34" class="body-text">• Customized managerial reporting &amp; inventory dashboards</text>
                    <text x="10" y="48" class="body-text">• Automated invoice generation and vendor ledger sync</text>
                    <text x="10" y="62" class="body-text">• Academic &amp; institutional tabulation engines (IntelliGrade)</text>
                    <text x="10" y="78" class="code-text" fill="#334155">Sync Link: Relational PostgreSQL database &amp; audit logging</text>
                </g>

                <!-- Integration Block 4 -->
                <g transform="translate(0, 306)">
                    <rect width="396" height="90" rx="4" fill="#FFFFFF" stroke="#B45309" stroke-width="1" />
                    <text x="10" y="18" font-family="'Segoe UI', Arial, sans-serif" font-size="10.5px" font-weight="700" fill="#92400E">🎧 Customer Support &amp; CRM Telemetry</text>
                    <text x="10" y="34" class="body-text">• Integration of multi-threaded automated email pipelines</text>
                    <text x="10" y="48" class="body-text">• Customer ticket routing &amp; automated notification webhooks</text>
                    <text x="10" y="62" class="body-text">• OTP security authentication &amp; password recovery services</text>
                    <text x="10" y="78" class="code-text" fill="#B45309">Sync Link: SMTP gateway &amp; asynchronous thread dispatch</text>
                </g>

                <!-- Summary Callout -->
                <g transform="translate(0, 408)">
                    <rect width="396" height="82" rx="4" fill="#EFF6FF" stroke="#93C5FD" stroke-width="1" />
                    <text x="10" y="18" font-family="'Segoe UI', Arial, sans-serif" font-size="10px" font-weight="800" fill="#1E40AF">Collaboration Lifecycle Contract:</text>
                    <text x="10" y="34" class="body-text">Software engineers maintain continuous coordination with operational,</text>
                    <text x="10" y="48" class="body-text">e-commerce, and support teams to iteratively gather functional requirements,</text>
                    <text x="10" y="62" class="body-text">deploy customized updates, and resolve system anomalies.</text>
                    <text x="10" y="76" class="meta-tag" fill="#2563EB">✔ Agile Feedback Sprints &amp; Production Reliability</text>
                </g>
            </g>
        </g>

        <!-- ========================================================== -->
        <!-- SUB-PANEL 2: SOFTWARE ENGINEERING HIERARCHY (CENTER)       -->
        <!-- Coordinates: x: 452, y: 50, w: 860, h: 540                  -->
        <!-- ========================================================== -->
        <g transform="translate(452, 50)">
            <rect width="860" height="540" rx="6" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1.2" />
            <rect width="860" height="26" rx="6" fill="#E0E7FF" />
            <rect y="20" width="860" height="6" fill="#E0E7FF" />
            <text x="14" y="17" class="card-title" fill="#3730A3">SOFTWARE DEVELOPMENT TEAM HIERARCHY &amp; PRACTICUM PLACEMENT</text>

            <!-- LEVEL 1: Head of IT & Software Engineering (Center: x: 430, y: 38) -->
            <g transform="translate(205, 38)">
                <rect width="450" height="74" rx="6" fill="#1E40AF" stroke="#1D4ED8" stroke-width="1.4" />
                <rect x="172" y="8" width="105" height="16" rx="3" fill="#3B82F6" />
                <text x="225" y="19.5" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif" font-size="8.5px" font-weight="800" fill="#FFFFFF">SUPERVISORY HEAD</text>
                
                <text x="225" y="40" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif" font-size="13px" font-weight="800" fill="#FFFFFF">Head of IT &amp; Lead Technical Supervisor</text>
                <text x="225" y="55" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif" font-size="9.5px" fill="#DBEAFE">System Architecture, Agile Sprint Governance, Technical Standards &amp; Mentorship</text>
                <text x="225" y="67" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif" font-size="9px" font-weight="600" fill="#93C5FD">Supervises Development Lifecycle, Reviewing Senior Staff &amp; Practicum Trainee</text>
            </g>

            <!-- Trunk from Head to Tier 2 (y: 112 to 142) -->
            <line x1="430" y1="112" x2="430" y2="142" stroke="#1E40AF" stroke-width="2" />
            <line x1="220" y1="142" x2="640" y2="142" stroke="#1E40AF" stroke-width="1.8" />
            <line x1="220" y1="142" x2="220" y2="155" stroke="#1E40AF" stroke-width="1.8" />
            <line x1="640" y1="142" x2="640" y2="155" stroke="#1E40AF" stroke-width="1.8" />

            <!-- LEVEL 2: Senior Engineers & QA/DevOps (y: 155, height: 96 px) -->
            <!-- Box A: Senior Full-Stack Software Engineers (x: 25, w: 390) -->
            <g transform="translate(25, 155)">
                <rect width="390" height="96" rx="5" fill="#FFFFFF" stroke="#3B82F6" stroke-width="1.2" />
                <rect width="390" height="22" rx="5" fill="#EFF6FF" />
                <rect y="16" width="390" height="6" fill="#EFF6FF" />
                <text x="195" y="15" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif" font-size="10.5px" font-weight="800" fill="#1D4ED8">Senior Full-Stack Software Engineers</text>

                <g transform="translate(14, 30)">
                    <text x="0" y="12" class="body-text">• Backend architecture, Python/Django &amp; RESTful APIs</text>
                    <text x="0" y="26" class="body-text">• Relational PostgreSQL database schema &amp; query optimization</text>
                    <text x="0" y="40" class="body-text">• Responsive web UI design, HTML5, Vanilla JavaScript, CSS</text>
                    <text x="0" y="54" class="meta-tag" fill="#2563EB">Role: Core Engineering &amp; Daily Technical Mentorship</text>
                </g>
            </g>

            <!-- Box B: QA & Systems Deployment Engineer (DevOps) (x: 445, w: 390) -->
            <g transform="translate(445, 155)">
                <rect width="390" height="96" rx="5" fill="#FFFFFF" stroke="#0D9488" stroke-width="1.2" />
                <rect width="390" height="22" rx="5" fill="#F0FDFA" />
                <rect y="16" width="390" height="6" fill="#F0FDFA" />
                <text x="195" y="15" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif" font-size="10.5px" font-weight="800" fill="#0F766E">QA &amp; Systems Deployment Engineer (DevOps)</text>

                <g transform="translate(14, 30)">
                    <text x="0" y="12" class="body-text">• Automated test suites, regression testing &amp; API validation</text>
                    <text x="0" y="26" class="body-text">• CI/CD deployment pipelines, Ubuntu Server &amp; Nginx configuration</text>
                    <text x="0" y="40" class="body-text">• Production system monitoring, security audits &amp; SSL/TLS ops</text>
                    <text x="0" y="54" class="meta-tag" fill="#0D9488">Role: Quality Assurance &amp; Infrastructure Reliability</text>
                </g>
            </g>

            <!-- Supervisory & Mentorship Connector lines down to Practicum Trainee -->
            <!-- Direct line from Supervisor center (x: 430) -->
            <line x1="430" y1="251" x2="430" y2="280" stroke="#059669" stroke-width="2.2" stroke-dasharray="4,3" marker-end="url(#arrGreen)" />
            <text x="435" y="270" font-family="'Segoe UI', Arial, sans-serif" font-size="8.5px" font-weight="700" fill="#059669">Direct Mentorship &amp; Supervisory Reporting Line</text>

            <!-- Drop from Senior Engineers (x: 220) -->
            <line x1="220" y1="251" x2="220" y2="280" stroke="#2563EB" stroke-width="1.6" marker-end="url(#arrBlue)" />

            <!-- Drop from QA/DevOps (x: 640) -->
            <line x1="640" y1="251" x2="640" y2="280" stroke="#0D9488" stroke-width="1.6" marker-end="url(#arrGreen)" />

            <!-- ====================================================== -->
            <!-- LEVEL 3: PROMINENT PRACTICUM TRAINEE CARD (CORE FOCUS) -->
            <!-- Coordinates: x: 25, y: 280, w: 810, h: 245              -->
            <!-- ====================================================== -->
            <g transform="translate(25, 280)" filter="url(#traineeGlow)">
                <!-- Main Focus Card Box -->
                <rect width="810" height="245" rx="8" fill="#FFFFFF" stroke="#059669" stroke-width="2.4" />
                
                <!-- Double Inner Highlight Border -->
                <rect x="3" y="3" width="804" height="239" rx="6" fill="none" stroke="#A7F3D0" stroke-width="1.2" />

                <!-- Header Bar -->
                <rect width="810" height="38" rx="8" fill="#047857" />
                <rect y="30" width="810" height="8" fill="#047857" />

                <!-- Special Badges in Header -->
                <rect x="14" y="8" width="160" height="22" rx="4" fill="#F59E0B" />
                <text x="94" y="22.5" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif" font-size="10px" font-weight="900" fill="#0F172A">★ PRACTICUM POSITION</text>

                <text x="186" y="24" font-family="'Segoe UI', Arial, sans-serif" font-size="13.5px" font-weight="800" fill="#FFFFFF">Software Development Intern / Practicum Trainee</text>
                <text x="794" y="24" text-anchor="end" font-family="'Segoe UI', Arial, sans-serif" font-size="11px" font-weight="700" fill="#D1FAE5">Trainee: Hijbullah (ID: 22303142)</text>

                <!-- Inner Content: 3 Structured Columns of Scope & Contributions -->
                <g transform="translate(14, 48)">
                    <!-- Sub-Card 1: Core Practicum Responsibilities -->
                    <g transform="translate(0, 0)">
                        <rect width="250" height="182" rx="5" fill="#F0FDF4" stroke="#86EFAC" stroke-width="1" />
                        <rect width="250" height="22" rx="5" fill="#DCFCE7" />
                        <text x="125" y="15" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif" font-size="9.5px" font-weight="800" fill="#166534">1. WEB APPLICATION DEV</text>
                        
                        <g transform="translate(10, 30)">
                            <text x="0" y="12" class="body-text">• Developing frontend components</text>
                            <text x="0" y="26" class="body-text">  for <tspan font-weight="700" fill="#0F766E">alhadiexpress.com.bd</tspan></text>
                            <text x="0" y="42" class="body-text">• Designing responsive UI layouts</text>
                            <text x="0" y="56" class="body-text">  using modern HTML5/CSS/JS</text>
                            <text x="0" y="72" class="body-text">• Implementing RESTful API</text>
                            <text x="0" y="86" class="body-text">  endpoints in Django 5.2</text>
                            <text x="0" y="102" class="body-text">• Database query optimization</text>
                            <text x="0" y="116" class="body-text">  with composite PostgreSQL indexes</text>
                            <text x="0" y="134" class="meta-tag" fill="#15803D">✔ Active Feature Deployment</text>
                        </g>
                    </g>

                    <!-- Sub-Card 2: Specialized Practicum R&D (IntelliGrade) -->
                    <g transform="translate(262, 0)">
                        <rect width="258" height="182" rx="5" fill="#EFF6FF" stroke="#93C5FD" stroke-width="1" />
                        <rect width="258" height="22" rx="5" fill="#DBEAFE" />
                        <text x="129" y="15" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif" font-size="9.5px" font-weight="800" fill="#1E40AF">2. INTELLIGRADE AI R&amp;D PROJECT</text>
                        
                        <g transform="translate(10, 30)">
                            <text x="0" y="12" class="body-text">• Engineering multimodal automated</text>
                            <text x="0" y="26" class="body-text">  examination evaluation platform</text>
                            <text x="0" y="42" class="body-text">• Building 300 DPI computer vision</text>
                            <text x="0" y="56" class="body-text">  deskewing &amp; Otsu pipeline</text>
                            <text x="0" y="72" class="body-text">• Multi-engine OCR cascade</text>
                            <text x="0" y="86" class="body-text">  (PyMuPDF, PyTesseract, EasyOCR)</text>
                            <text x="0" y="102" class="body-text">• ReportLab certified watermarked</text>
                            <text x="0" y="116" class="body-text">  PDF stamping &amp; audit logging</text>
                            <text x="0" y="134" class="meta-tag" fill="#2563EB">✔ Flagship Applied Thesis Asset</text>
                        </g>
                    </g>

                    <!-- Sub-Card 3: Supervision & Team Collaboration -->
                    <g transform="translate(532, 0)">
                        <rect width="250" height="182" rx="5" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1" />
                        <rect width="250" height="22" rx="5" fill="#F1F5F9" />
                        <text x="125" y="15" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif" font-size="9.5px" font-weight="800" fill="#334155">3. SUPERVISION &amp; STANDARDS</text>
                        
                        <g transform="translate(10, 30)">
                            <text x="0" y="12" class="body-text">• Direct reporting to Lead</text>
                            <text x="0" y="26" class="body-text">  Technical Supervisor on milestones</text>
                            <text x="0" y="42" class="body-text">• Peer pairing with Senior Full-Stack</text>
                            <text x="0" y="56" class="body-text">  Engineers on complex tasks</text>
                            <text x="0" y="72" class="body-text">• Daily Agile standups &amp; Git</text>
                            <text x="0" y="86" class="body-text">  pull-request code reviews</text>
                            <text x="0" y="102" class="body-text">• Cross-functional coordination</text>
                            <text x="0" y="116" class="body-text">  with sales &amp; operations teams</text>
                            <text x="0" y="134" class="meta-tag" fill="#047857">✔ Professional Skill Governance</text>
                        </g>
                    </g>
                </g>
            </g>
        </g>

        <!-- ========================================================== -->
        <!-- SUB-PANEL 3: TECHNOLOGY STACK & METHODOLOGY (RIGHT)        -->
        <!-- Coordinates: x: 1326, y: 50, w: 388, h: 540                 -->
        <!-- ========================================================== -->
        <g transform="translate(1326, 50)">
            <rect width="388" height="540" rx="6" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1.2" />
            <rect width="388" height="26" rx="6" fill="#EEF2FF" />
            <rect y="20" width="388" height="6" fill="#EEF2FF" />
            <text x="12" y="17" class="card-title" fill="#3730A3">TECHNICAL GOVERNANCE &amp; METHODOLOGY</text>

            <g transform="translate(12, 36)">
                <!-- Method Card -->
                <g transform="translate(0, 0)">
                    <rect width="364" height="135" rx="5" fill="#FFFFFF" stroke="#818CF8" stroke-width="1" />
                    <text x="10" y="18" font-family="'Segoe UI', Arial, sans-serif" font-size="10.5px" font-weight="800" fill="#3730A3">Agile Development Methodology</text>
                    <g transform="translate(10, 26)">
                        <text x="0" y="12" class="body-text">• <tspan font-weight="700">Sprint Cycles:</tspan> 2-Week Agile Scrum Iterations</text>
                        <text x="0" y="28" class="body-text">• <tspan font-weight="700">Daily Sync:</tspan> 15-Minute Standup &amp; Blockers</text>
                        <text x="0" y="44" class="body-text">• <tspan font-weight="700">Version Control:</tspan> Git Feature-Branch Flow</text>
                        <text x="0" y="60" class="body-text">• <tspan font-weight="700">Code Reviews:</tspan> Strict PR Approval Policy</text>
                        <text x="0" y="76" class="body-text">• <tspan font-weight="700">Issue Tracking:</tspan> Jira / GitHub Project Boards</text>
                        <text x="0" y="94" class="meta-tag" fill="#4338CA">Standard: Clean Architecture &amp; SOLID Principles</text>
                    </g>
                </g>

                <!-- Production Stack Card -->
                <g transform="translate(0, 147)">
                    <rect width="364" height="185" rx="5" fill="#FFFFFF" stroke="#3B82F6" stroke-width="1" />
                    <text x="10" y="18" font-family="'Segoe UI', Arial, sans-serif" font-size="10.5px" font-weight="800" fill="#1D4ED8">Production Technology Stack</text>
                    <g transform="translate(10, 26)">
                        <text x="0" y="12" class="body-text">• <tspan font-weight="700">Backend Core:</tspan> Python 3.12, Django 5.2, DRF</text>
                        <text x="0" y="28" class="body-text">• <tspan font-weight="700">Database:</tspan> PostgreSQL 16 with B-Tree Indexes</text>
                        <text x="0" y="44" class="body-text">• <tspan font-weight="700">Async Workers:</tspan> threading.Thread, Celery, Redis</text>
                        <text x="0" y="60" class="body-text">• <tspan font-weight="700">Vision / OCR:</tspan> OpenCV 4.8, PyMuPDF, EasyOCR</text>
                        <text x="0" y="76" class="body-text">• <tspan font-weight="700">PDF Generator:</tspan> ReportLab Vector Certification</text>
                        <text x="0" y="92" class="body-text">• <tspan font-weight="700">Frontend Web:</tspan> HTML5, CSS3, Vanilla JS, Vite</text>
                        <text x="0" y="108" class="body-text">• <tspan font-weight="700">Web Gateway:</tspan> Nginx Reverse Proxy, Gunicorn</text>
                        <text x="0" y="124" class="body-text">• <tspan font-weight="700">Security Layer:</tspan> HTTPS / TLS 1.3, CSP, RBAC</text>
                        <text x="0" y="142" class="meta-tag" fill="#15803D">✔ High Reliability Enterprise Infrastructure</text>
                    </g>
                </g>

                <!-- Quality Standards Card -->
                <g transform="translate(0, 344)">
                    <rect width="364" height="142" rx="5" fill="#FFFFFF" stroke="#10B981" stroke-width="1" />
                    <text x="10" y="18" font-family="'Segoe UI', Arial, sans-serif" font-size="10.5px" font-weight="800" fill="#047857">Engineering Quality &amp; Governance</text>
                    <g transform="translate(10, 26)">
                        <text x="0" y="12" class="body-text">• <tspan font-weight="700">Standards:</tspan> ISO/IEC 25010 Quality Framework</text>
                        <text x="0" y="28" class="body-text">• <tspan font-weight="700">Testing:</tspan> PyTest Unit &amp; Integration Coverage</text>
                        <text x="0" y="44" class="body-text">• <tspan font-weight="700">Monitoring:</tspan> Error Logging &amp; Performance Telemetry</text>
                        <text x="0" y="60" class="body-text">• <tspan font-weight="700">Data Integrity:</tspan> Atomic Transactions &amp; Audit Logs</text>
                        <text x="0" y="76" class="body-text">• <tspan font-weight="700">Practicum Review:</tspan> Weekly Evaluator Milestones</text>
                        <text x="0" y="94" class="meta-tag" fill="#059669">Goal: Industry-Standard Software Engineering</text>
                    </g>
                </g>
            </g>
        </g>
    </g>

    <!-- Bottom Footer Meta Banner -->
    <g transform="translate(35, 1024)">
        <text x="0" y="14" class="footer-text">Al Hadi Enterprise Organogram — Figure 2.1: Organizational Structure &amp; Software Development Team</text>
        <text x="1730" y="14" text-anchor="end" class="footer-text">Dimensions: 6.0" × 3.5" (300 DPI, 1800 × 1050 px) | Pure Light Mode | Publication-Ready</text>
    </g>
</svg>
"""

    # 1. Render SVG background directly to PNG at 1:1 scale (1800 x 1050) using PyMuPDF
    doc_svg = fitz.open(stream=svg.encode('utf-8'), filetype='svg')
    pix = doc_svg[0].get_pixmap()
    doc_svg.close()

    base_img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    # 2. Composite the Al Hadi Enterprise Logo in the top-right header
    if os.path.exists(LOGO_PATH):
        logo = Image.open(LOGO_PATH).convert("RGBA")
        # Resize logo to fit inside the badge box: width ~85 px, height ~39 px
        target_logo_w = 85
        aspect = logo.height / logo.width
        target_logo_h = int(target_logo_w * aspect)
        logo_resized = logo.resize((target_logo_w, target_logo_h), Image.Resampling.LANCZOS)

        # Place inside the badge at x = 1520, y = 10 (badge width: 245, height: 56)
        # Position logo on the left of the badge: x = 1530, y = 10 + (56 - target_logo_h)//2 = 18
        paste_x = 1530
        paste_y = 10 + (56 - target_logo_h) // 2
        
        # Paste with alpha mask onto white background
        base_img.paste(logo_resized, (paste_x, paste_y), logo_resized)
        print(f"Composited Al Hadi logo at ({paste_x}, {paste_y}) size {logo_resized.size}")

    # 3. Save final Figure 2.1 PNG
    base_img.save(OUTPUT_PNG, format="PNG", dpi=(300, 300))
    print(f"Successfully generated Figure 2.1 at: {OUTPUT_PNG} ({base_img.width}x{base_img.height})")

if __name__ == "__main__":
    create_figure_2_1()
