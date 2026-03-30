# app/docx_bridge.py
import subprocess
from pathlib import Path


def render_docx_with_node(
    tender_id: str,
    template_path: str = "templates/fujitsu_response_template.docx",
    payload_path: str | None = None,
    output_path: str | None = None
) -> str:
    if payload_path is None:
        payload_path = f"tenders/{tender_id}/output/docx_payload.json"

    if output_path is None:
        output_path = f"tenders/{tender_id}/output/proposal_overview.docx"

    cmd = [
        "node",
        "docx_renderer/render_docx.js",
        template_path,
        payload_path,
        output_path,
    ]

    import subprocess

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"DOCX render failed.\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )

    if not Path(output_path).exists():
        raise RuntimeError("DOCX render completed but output file was not created.")

    return output_path