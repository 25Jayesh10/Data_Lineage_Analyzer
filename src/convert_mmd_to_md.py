def convert_mmd_to_md(mmd_file, md_file):
    """
    Converts a Mermaid .mmd file to a .md file with a Mermaid code block.

    Args:
        mmd_file (str): Path to the input .mmd file.
        md_file (str): Path to the output .md file.
    """
    with open(mmd_file, "r") as mmd:
        mmd_content = mmd.read()

    with open(md_file, "w") as md:
        md.write("```mermaid\n")
        md.write(mmd_content)
        md.write("```")

    print(f"Converted {mmd_file} ➜ {md_file} (Markdown format)")
