
from src.convert_mmd_to_md import convert_mmd_to_md

def test_mermaid_conversion_preserves_structure_and_content(tmp_path):
    # Prepare a realistic Mermaid diagram (as in lineage.mmd)
    mmd_content = (
        "graph BT\n"
        "    %% Node styles\n"
        "    classDef table fill:#f96,stroke:#333,stroke-width:2px,color:#000;\n"
        "    classDef stored_proc fill:#9cf,stroke:#333,stroke-width:2px ,color:#000;\n"
        "    AcmeERP.usp_ProcessFullPayrollCycle --> AcmeERP.PayrollLogs\n"
        "    AcmeERP.usp_ProcessFullPayrollCycle --> AcmeERP.ExchangeRates\n"
        "    AcmeERP.usp_ProcessFullPayrollCycle --> #PayrollCalc\n"
        "    AcmeERP.usp_ProcessFullPayrollCycle --> AcmeERP.Employees\n"
        "    class AcmeERP.ExchangeRates,AcmeERP.PayrollLogs,#PayrollCalc,AcmeERP.Employees table;\n"
        "    class AcmeERP.usp_ProcessFullPayrollCycle stored_proc;\n"
    )
    mmd_file = tmp_path / "lineage.mmd"
    md_file = tmp_path / "lineage.md"
    mmd_file.write_text(mmd_content)

    # Run conversion
    convert_mmd_to_md(str(mmd_file), str(md_file))

    # Read and validate the output
    md_content = md_file.read_text()
    lines = md_content.splitlines()

    # Check code block markers
    assert lines[0] == "```mermaid"
    assert lines[-1] == "```"

    # Check that all key lines from the mmd are present in the md
    for expected_line in mmd_content.splitlines():
        assert expected_line in md_content, f"Missing line: {expected_line}"

    # Check that the output file exists and is not empty
    assert md_file.exists()
    assert len(md_content) > 0

    # Check that there are no extra blank lines at the start or end
    assert md_content.startswith("```mermaid\n")
    assert md_content.rstrip().endswith("```")

    # Check that the diagram direction and node styles are preserved
    assert "graph BT" in md_content
    assert "classDef table" in md_content
    assert "classDef stored_proc" in md_content

    # Check that all expected nodes and edges are present
    assert "AcmeERP.usp_ProcessFullPayrollCycle --> AcmeERP.PayrollLogs" in md_content
    assert "AcmeERP.usp_ProcessFullPayrollCycle --> AcmeERP.ExchangeRates" in md_content
    assert "AcmeERP.usp_ProcessFullPayrollCycle --> #PayrollCalc" in md_content
    assert "AcmeERP.usp_ProcessFullPayrollCycle --> AcmeERP.Employees" in md_content


# import json
# from src.generate_mermaid import generate_mermaid

# def test_generate_mermaid_diagram_matches_expected(tmp_path):
#     # Prepare lineage.json input
#     lineage = {
#         "AcmeERP.usp_ProcessFullPayrollCycle": {
#             "type": "procedure",
#             "calls": []
#         },
#         "AcmeERP.PayrollLogs": {
#             "type": "table",
#             "calls": ["AcmeERP.usp_ProcessFullPayrollCycle"],
#             "usage": {"AcmeERP.usp_ProcessFullPayrollCycle": ["write"]}
#         },
#         "AcmeERP.ExchangeRates": {
#             "type": "table",
#             "calls": ["AcmeERP.usp_ProcessFullPayrollCycle"],
#             "usage": {"AcmeERP.usp_ProcessFullPayrollCycle": ["read"]}
#         },
#         "#PayrollCalc": {
#             "type": "table",
#             "calls": ["AcmeERP.usp_ProcessFullPayrollCycle"],
#             "usage": {"AcmeERP.usp_ProcessFullPayrollCycle": ["read", "write"]}
#         },
#         "AcmeERP.Employees": {
#             "type": "table",
#             "calls": ["AcmeERP.usp_ProcessFullPayrollCycle"],
#             "usage": {"AcmeERP.usp_ProcessFullPayrollCycle": ["read"]}
#         }
#     }
#     lineage_file = tmp_path / "lineage.json"
#     mmd_file = tmp_path / "lineage.mmd"
#     lineage_file.write_text(json.dumps(lineage, indent=2))

#     # Run the generator
#     generate_mermaid(str(lineage_file), str(mmd_file))

#     # Read and validate the output
#     mmd_content = mmd_file.read_text()

#     # 1. Check code block structure and diagram direction
#     assert "graph BT" in mmd_content
#     assert "classDef table" in mmd_content
#     assert "classDef stored_proc" in mmd_content

#     # 2. Check all expected edges are present
#     assert "AcmeERP.usp_ProcessFullPayrollCycle --> AcmeERP.PayrollLogs" in mmd_content
#     assert "AcmeERP.usp_ProcessFullPayrollCycle --> AcmeERP.ExchangeRates" in mmd_content
#     assert "AcmeERP.usp_ProcessFullPayrollCycle --> #PayrollCalc" in mmd_content
#     assert "AcmeERP.usp_ProcessFullPayrollCycle --> AcmeERP.Employees" in mmd_content


#     # 4. Check that the output file exists and is not empty
#     assert mmd_file.exists()
#     assert len(mmd_content) > 0

#     # 5. Check that no unexpected nodes or edges are present
#     unexpected_nodes = ["UnknownTable", "UnknownProc"]
#     for node in unexpected_nodes:
#         assert node not in mmd_content

#     # 6. Check that usage info is not directly present (Mermaid doesn't show usage, but lineage.json does)
#     assert "write" not in mmd_content
#     assert "read" not in mmd_content

#     # 7. Check that the diagram is reproducible and deterministic
#     # (Re-run and compare output)
#     mmd_file2 = tmp_path / "lineage2.mmd"
#     generate_mermaid(str(lineage_file), str(mmd_file2))
#     assert mmd_file.read_text() == mmd_file2.read_text()   


# this is because the mermaid function signature has changed it is now generate mermaid diagrams with columnns