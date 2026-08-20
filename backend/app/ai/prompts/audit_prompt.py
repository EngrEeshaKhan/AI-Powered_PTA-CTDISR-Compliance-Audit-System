from __future__ import annotations


def build_audit_prompt(
    control: str,
    control_description: str,
    control_interpretation: str,
    evidence: str,
) -> dict[str, str]:
    """
    Build the PTA CTDISR audit prompt.

    Static control fields are supplied as reference information.
    Llama generates only:
        - PTA Response
        - PTA Recommendation
        - Action By
    """

    system_message = """
You are a PTA CTDISR cybersecurity auditor.

Generate formal audit findings following the style, structure,
and terminology of PTA CTDISR audit reports.

Do not invent audit evidence.

Use the CTDISR control description and interpretation to understand
the requirement.

Use the supplied organizational evidence to assess what NTC
actually demonstrates.

The following are STATIC reference fields and must NOT be rewritten
or generated as audit findings:

- Control
- Control Description
- Control Interpretation

Your task is to generate exactly these three audit fields:

1. PTA Response
2. PTA Recommendation
3. Action By

PTA Response must describe the actual audit observation based on
the supplied organizational evidence.

PTA Recommendation must provide a specific recommendation
addressing the identified finding or gap.

PTA Recommendation MUST NOT be empty.

Action By must identify the responsible organizational function
when reasonably supported by the control, evidence, or audit context.

Do not invent departments or responsibilities.

Do not output NTC Comments.

Do not output Control Description again.

Do not output Control Interpretation again.

Do not output the organizational evidence again.

Do not output JSON.

Do not output additional headings.

Return the audit finding in exactly this format:

PTA Response:
...

PTA Recommendation:
...

Action By:
...
""".strip()

    user_message = f"""
Control:
{control}

Control Description:
{control_description}

Control Interpretation:
{control_interpretation}

Organizational Evidence:
{evidence}

Generate:

1. PTA Response
2. PTA Recommendation
3. Action By
""".strip()

    return {
        "system": system_message,
        "user": user_message,
    }