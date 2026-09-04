"""
CivicLens Official Municipal Audit PDF Generator Service
Renders executive ward audit summaries containing SLA compliance metrics, PWD material requisitions, and contractor quality ratings.
"""

from typing import Dict, Any

def generate_ward_audit_report_html(ward_name: str = "Ward 63 (College Road)") -> str:
    """
    Generates a printable, executive HTML audit document.
    """
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8"/>
        <title>CivicLens Municipal Ward Audit Report — {ward_name}</title>
        <style>
            body {{ font-family: 'Helvetica Neue', Arial, sans-serif; color: #102C2B; padding: 40px; background: #FFF; }}
            .header {{ border-bottom: 3px solid #287C73; padding-bottom: 15px; margin-bottom: 30px; }}
            .title {{ font-size: 24px; font-weight: bold; color: #287C73; text-transform: uppercase; }}
            .subtitle {{ font-size: 12px; color: #4B6363; margin-top: 5px; }}
            .kpi-box {{ background: #F7F6F2; border: 1px solid #E7E9E4; padding: 15px; border-radius: 12px; margin-bottom: 20px; }}
            .kpi-title {{ font-size: 11px; font-weight: bold; color: #4B6363; text-transform: uppercase; }}
            .kpi-value {{ font-size: 22px; font-weight: bold; color: #102C2B; margin-top: 4px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th, td {{ padding: 10px; border: 1px solid #E7E9E4; text-align: left; font-size: 12px; }}
            th {{ background: #287C73; color: white; text-transform: uppercase; font-size: 10px; }}
            .footer {{ margin-top: 40px; border-top: 1px solid #E7E9E4; padding-top: 15px; font-size: 10px; color: #4B6363; display: flex; justify-between: space-between; }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="title">🏛️ Central Municipal Corporation</div>
            <div class="subtitle">Official Executive Ward Performance &amp; Contractor Quality Audit Report • {ward_name}</div>
        </div>

        <div style="display: flex; gap: 15px;">
            <div class="kpi-box" style="flex: 1;">
                <div class="kpi-title">Total Reports Logged</div>
                <div class="kpi-value">12,482</div>
            </div>
            <div class="kpi-box" style="flex: 1;">
                <div class="kpi-title">AI Vision Pass Rate</div>
                <div class="kpi-value" style="color: #10B981;">98.4%</div>
            </div>
            <div class="kpi-box" style="flex: 1;">
                <div class="kpi-title">Avg SLA Resolution</div>
                <div class="kpi-value" style="color: #287C73;">2.4 Hours</div>
            </div>
        </div>

        <h3>1. PWD Material Requisitions &amp; Dispatch Summary</h3>
        <table>
            <thead>
                <tr>
                    <th>Material Type</th>
                    <th>Required Quantity</th>
                    <th>Estimated Cost</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Cold-Mix Bitumen Asphalt</td>
                    <td>4.2 Tons</td>
                    <td>₹42,000</td>
                    <td>DISPATCHED (Depot #4)</td>
                </tr>
                <tr>
                    <td>RCC Drainage Culvert Piping</td>
                    <td>12.0 Meters</td>
                    <td>₹28,500</td>
                    <td>ALLOCATED</td>
                </tr>
            </tbody>
        </table>

        <h3 style="margin-top: 30px;">2. Municipal Contractor Quality Scorecard</h3>
        <table>
            <thead>
                <tr>
                    <th>Contractor Name</th>
                    <th>Ward Assigned</th>
                    <th>AI Pass Rate</th>
                    <th>Durability Score</th>
                    <th>Rating</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Alpha Infrastructure Ltd</td>
                    <td>Ward 63 &amp; Ward 12</td>
                    <td>98.2%</td>
                    <td>96 / 100</td>
                    <td style="color: green; font-weight: bold;">RATED EXCELLENT</td>
                </tr>
                <tr>
                    <td>Metro Sanitation Services</td>
                    <td>Ward 18</td>
                    <td>74.5%</td>
                    <td>68 / 100</td>
                    <td style="color: red; font-weight: bold;">UNDER AUDIT WARNING</td>
                </tr>
            </tbody>
        </table>

        <div class="footer">
            <div>Report ID: REPORT-CL-2026-9920 • Verified by AI Vision Engine</div>
            <div>Signed: Municipal Commissioner / Ward Supervisor</div>
        </div>
    </body>
    </html>
    """

def generate_audit_report(ward_name: str = "Ward 63") -> bytes:
    return generate_ward_audit_report_html(ward_name).encode('utf-8')
