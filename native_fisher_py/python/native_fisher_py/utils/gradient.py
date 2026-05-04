import re
from typing import List, Tuple

def parse_vanquish_neo_gradient(method_text: str) -> dict:
    """
    Parses Vanquish Neo style pump lines from instrument method text.
    Supports both standard text summary and XML-like structured data.
    Returns a dictionary with 'solvents' and 'gradient'.
    """
    results = {
        "solvents": {"A": None, "B": None},
        "gradient": []
    }
    
    # 1. Try standard text format
    # Extract Solvents
    a_match = re.search(r'Pump\.%A_Solvent:\s+(.*)', method_text)
    if a_match:
        results["solvents"]["A"] = a_match.group(1).strip()
        
    b_match = re.search(r'Pump\.%B_Solvent:\s+(.*)', method_text)
    if b_match:
        results["solvents"]["B"] = b_match.group(1).strip()

    # Split by time points like "71.800 [min]"
    segments = re.split(r'(\d+\.\d+)\s+\[min\]', method_text)
    current_time = None
    for part in segments:
        if re.match(r'^\d+\.\d+$', part):
            current_time = float(part)
        elif current_time is not None:
            match = re.search(r'Pump\.%B\.Value:\s+(\d+\.\d+)\s+\[%\]', part)
            if match:
                percent_b = float(match.group(1))
                results["gradient"].append((current_time, percent_b))

    if results["gradient"]:
        return results

    # 2. Try XML-like format (found in some Astral files)
    # <Time type="MethodTime"><InternalValue value="0.00000000000000000E+000" /></Time>
    # <SymbolPath value="Neo.PumpModule.Pump.%B.Value" /><Value value="6.0 [%]" />
    
    parts = re.split(r'<Item type="TimeStepNode">', method_text)
    for part in parts:
        time_match = re.search(r'<Time type="MethodTime"><InternalValue value="([\d\.E\+-]+)" />', part)
        b_match = re.search(r'Pump\.%B\.Value" /><Value value="(\d+\.\d+)\s+\[%\]"', part)
        if time_match and b_match:
            time = float(time_match.group(1))
            percent_b = float(b_match.group(1))
            results["gradient"].append((time, percent_b))

    return results
