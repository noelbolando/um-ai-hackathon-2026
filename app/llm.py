"""
llm.py
------
Handles all communication with Mistral via Ollama.

Responsibilities:
  1. extract_search_query()       — distill user message into a search query
  2. explain_course_match()       — why does this course help meet the goal?
  3. explain_faculty_match()      — why is this faculty relevant to the goal?
  4. generate_goal_response()     — unified response covering both courses + faculty
"""

import ollama

LLM_MODEL = "mistral"


def extract_search_query(user_message: str, history: list[dict]) -> str:
    """
    Extract a concise search query from the student's learning goal,
    using conversation history for context.
    """
    history_text = ""
    if history:
        lines = []
        for msg in history[-6:]:
            role = "Student" if msg["role"] == "user" else "Advisor"
            lines.append(f"{role}: {msg['content']}")
        history_text = "\n".join(lines) + "\n"

    prompt = f"""You are extracting a search query from a student's learning goal.

Previous conversation:
{history_text}
Student's goal: "{user_message}"

Extract the core academic topic(s) that would help this student meet their goal. Return ONLY a short search query (2-6 keywords, no explanation, no punctuation). Examples: "negotiations conflict resolution", "machine learning neural networks", "consulting strategy frameworks".

Search query:"""

    response = ollama.chat(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return response["message"]["content"].strip()


def explain_course_match(course: dict, user_goal: str, history: list[dict]) -> str:
    """
    1-2 sentence explanation of why this course helps the student meet their goal.
    """
    history_text = ""
    if history:
        lines = []
        for msg in history[-4:]:
            role = "Student" if msg["role"] == "user" else "Advisor"
            lines.append(f"{role}: {msg['content']}")
        history_text = "Conversation so far:\n" + "\n".join(lines) + "\n\n"

    prompt = f"""{history_text}A student's learning goal: "{user_goal}"

Course being considered:
- Code: {course['course code']}
- Description: {course['course description']}
- Semester: {course['semester taught']}
- Instructor: {course['taught by']}

In 1-2 sentences, explain specifically how this course helps the student achieve their goal. Be concrete — reference the student's goal and the course content. Do not start with "This course".

Explanation:"""

    response = ollama.chat(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return response["message"]["content"].strip()


def explain_faculty_match(faculty: dict, user_goal: str, history: list[dict]) -> str:
    """
    1-2 sentence explanation of why this faculty member is relevant to the student's goal.
    """
    history_text = ""
    if history:
        lines = []
        for msg in history[-4:]:
            role = "Student" if msg["role"] == "user" else "Advisor"
            lines.append(f"{role}: {msg['content']}")
        history_text = "Conversation so far:\n" + "\n".join(lines) + "\n\n"

    bio_snippet = faculty.get("bio", "")
    if len(bio_snippet) > 500:
        bio_snippet = bio_snippet[:500] + "..."

    prompt = f"""{history_text}A student's learning goal: "{user_goal}"

Faculty member being considered:
- Name: {faculty['name']}
- Title: {faculty['titles']}
- Bio: {bio_snippet}

In 1-2 sentences, explain specifically why connecting with this faculty member would help the student achieve their goal. Reference both the student's goal and the faculty member's specific expertise. Do not start with "This professor" or "This faculty member".

Explanation:"""

    response = ollama.chat(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return response["message"]["content"].strip()


def generate_goal_response(
    user_goal: str,
    courses: list[dict],
    faculty: list[dict],
    history: list[dict],
) -> str:
    """
    Generate a unified conversational response that addresses the student's
    learning goal by referencing both the matched courses and faculty.
    """
    # Format courses
    if courses:
        course_lines = []
        for i, c in enumerate(courses, 1):
            course_lines.append(
                f"{i}. [{c['course code']}] {c['course description']}\n"
                f"   Why it helps: {c.get('explanation', '')}"
            )
        courses_text = "\n\n".join(course_lines)
    else:
        courses_text = "No matching courses found."

    # Format faculty
    if faculty:
        faculty_lines = []
        for i, f in enumerate(faculty, 1):
            faculty_lines.append(
                f"{i}. {f['name']} — {f['titles']}\n"
                f"   Why connect: {f.get('explanation', '')}"
            )
        faculty_text = "\n\n".join(faculty_lines)
    else:
        faculty_text = "No matching faculty found."

    ollama_messages = [
        {
            "role": "system",
            "content": (
                "You are a warm, knowledgeable academic advisor. A student has shared "
                "a learning goal with you, and you have found relevant courses and faculty "
                "to help them achieve it. Write a concise, encouraging response that: "
                "acknowledges their goal, briefly introduces the courses as a learning path, "
                "and introduces the faculty as people worth connecting with. "
                "Keep it conversational — no long bullet lists. End with an invitation to refine."
            ),
        }
    ]

    for msg in history:
        ollama_messages.append({"role": msg["role"], "content": msg["content"]})

    ollama_messages.append({
        "role": "user",
        "content": (
            f"My learning goal: {user_goal}\n\n"
            f"[Matched courses:]\n{courses_text}\n\n"
            f"[Matched faculty:]\n{faculty_text}"
        ),
    })

    response = ollama.chat(model=LLM_MODEL, messages=ollama_messages)
    return response["message"]["content"].strip()
