import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def build_prompt_from_files(files, payload):
    pr_title = payload["pull_request"]["title"]
    pr_author = payload["pull_request"]["user"]["login"]

    content = f"PR Title: {pr_title}\nAuthor: {pr_author}\n\n"

    for f in files:
        filename = f.get("filename", "unknown")
        patch = f.get("patch", "")

        content += f"\n### File: {filename}\n"
        content += patch + "\n"

    return (
        "You are an expert senior engineer.\n"
        "Review the following PR and return STRICT JSON ONLY.\n\n"
        "JSON FORMAT:\n"
        "{\n"
        '   "summary": "overall summary",\n'
        '   "suggestions": [\n'
        "       {\n"
        '           "file": "filename",\n'
        '           "severity": "MINOR|MAJOR|CRITICAL",\n'
        '           "comment": "explanation",\n'
        '           "fix": "suggested code fix if any"\n'
        "       }\n"
        "   ]\n"
        "}\n\n"
        "-------- PR CONTENT BELOW --------\n"
        f"{content}"
    )


def run_llm_review(prompt):
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You MUST return valid JSON ONLY. No markdown."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content
