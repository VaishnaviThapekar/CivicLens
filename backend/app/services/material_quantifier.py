"""
CivicLens Automated Repair Material & Cost Quantifier Engine
Calculates repair material requirements (asphalt, concrete, PVC piping, labor days, total cost in ₹ INR)
from defect bounding box dimensions, category, and severity.
"""

from typing import Dict, Any, Optional

def estimate_repair_materials(
    category: str = "Road Infrastructure",
    area_sqm: float = 1.8,
    severity: str = "P2 — High"
) -> Dict[str, Any]:
    """
    Quantifies repair material estimates and estimated municipal budget in INR.
    """
    area = max(0.5, float(area_sqm))
    cat_upper = str(category).upper()

    if "ROAD" in cat_upper or "TRAFFIC" in cat_upper:
        asphalt_tons = round(area * 0.12, 2)
        gravel_m3 = round(area * 0.08, 2)
        bitumen_liters = round(area * 4.5, 1)
        labor_days = max(1, int(area // 2.5) + 1)
        cost_inr = int(asphalt_tons * 4500 + gravel_m3 * 1200 + bitumen_liters * 85 + labor_days * 3500)
        
        materials = [
            {"material": "Bituminous Asphalt Mix", "quantity": f"{asphalt_tons} Tons", "unit_cost_inr": 4500},
            {"material": "Crushed Stone Gravel Aggregate", "quantity": f"{gravel_m3} m³", "unit_cost_inr": 1200},
            {"material": "Emulsified Bitumen Tack Coat", "quantity": f"{bitumen_liters} Liters", "unit_cost_inr": 85},
            {"material": "Road Repair Crew Labor", "quantity": f"{labor_days} Team Days", "unit_cost_inr": 3500}
        ]
    elif "DRAINAGE" in cat_upper or "WATER" in cat_upper:
        pipe_meters = round(area * 2.2, 1)
        concrete_m3 = round(area * 0.15, 2)
        sealant_kg = round(area * 1.5, 1)
        labor_days = max(1, int(area // 2.0) + 1)
        cost_inr = int(pipe_meters * 1800 + concrete_m3 * 4200 + sealant_kg * 350 + labor_days * 3800)

        materials = [
            {"material": "HDPE Reinforced Drainage Pipe", "quantity": f"{pipe_meters} Meters", "unit_cost_inr": 1800},
            {"material": "M25 Structural Concrete Mix", "quantity": f"{concrete_m3} m³", "unit_cost_inr": 4200},
            {"material": "Hydraulic Waterproof Sealant", "quantity": f"{sealant_kg} kg", "unit_cost_inr": 350},
            {"material": "Utilities & Drainage Crew Labor", "quantity": f"{labor_days} Team Days", "unit_cost_inr": 3800}
        ]
    elif "GARBAGE" in cat_upper or "SANITATION" in cat_upper:
        disinfectant_l = round(area * 8.0, 1)
        compactor_trips = max(1, int(area // 4.0) + 1)
        bin_replacements = 1 if area >= 5.0 else 0
        labor_days = 1
        cost_inr = int(disinfectant_l * 65 + compactor_trips * 2500 + bin_replacements * 12000 + labor_days * 2800)

        materials = [
            {"material": "Bio-Enzymatic Disinfectant Spray", "quantity": f"{disinfectant_l} Liters", "unit_cost_inr": 65},
            {"material": "Compactor Truck Transit & Haulage", "quantity": f"{compactor_trips} Trips", "unit_cost_inr": 2500},
            {"material": "Commercial Waste Bins (1100L)", "quantity": f"{bin_replacements} Units", "unit_cost_inr": 12000},
            {"material": "Sanitation Rapid Response Crew", "quantity": f"{labor_days} Team Days", "unit_cost_inr": 2800}
        ]
    else:
        materials = [
            {"material": "General Municipal Supplies", "quantity": f"{area} m² Area Equivalent", "unit_cost_inr": 1500},
            {"material": "Field Maintenance Crew", "quantity": "1 Team Day", "unit_cost_inr": 3000}
        ]
        cost_inr = int(area * 1500 + 3000)

    return {
        "defect_category": category,
        "estimated_area_sqm": area,
        "severity_level": severity,
        "estimated_total_cost_inr": cost_inr,
        "formatted_cost_inr": f"₹{cost_inr:,}",
        "material_breakdown": materials,
        "recommended_contractor_type": "Public Works Division (PWD)" if "ROAD" in cat_upper else "Water & Sanitation Cell"
    }
