import re


def parse_vanquish_neo_gradient(method_text: str) -> dict:
    """
    Parses Vanquish Neo style pump lines from instrument method text.
    Returns a dictionary with 'solvents' and 'gradient'.
    """
    results = {
        "solvents": {"A": None, "B": None},
        "gradient": []
    }

    # Extract Solvents
    # Format: Neo.PumpModule.Pump.%A_Solvent: H2O
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

    return results

def parse_agilent_gradient(method_text: str) -> dict:
    """
    Parses Agilent style pump lines from instrument method text.
    Returns a dictionary with 'solvents' and 'gradient'.
    """
    results = {
        "solvents": {"A": None, "B": None},
        "gradient": []
    }

    # Extract Solvents
    # Format: Solvent A: 0.1%FA
    a_match = re.search(r'Solvent A:\s+(.*)', method_text)
    if a_match:
        results["solvents"]["A"] = a_match.group(1).strip()

    b_match = re.search(r'Solvent B:\s+(.*)', method_text)
    if b_match:
        results["solvents"]["B"] = b_match.group(1).strip()

    # Find the Gradient program section
    # Format:
    #       0.00(min)    0.050(ml/min)      A=100.0% B=0.0%
    gradient_section = re.search(r'Gradient program:.*?(?=\n\s*\n|\Z)', method_text, re.DOTALL)
    if gradient_section:
        lines = gradient_section.group(0).split('\n')
        for line in lines:
            # Match lines with time, flow rate, and composition
            match = re.search(r'^\s*(\d+\.\d+)\(min\).*?B=(\d+\.\d+)%', line)
            if match:
                time = float(match.group(1))
                percent_b = float(match.group(2))
                results["gradient"].append((time, percent_b))

    return results
