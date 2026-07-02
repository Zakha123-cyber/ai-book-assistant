import re
from dataclasses import dataclass
from enum import StrEnum

from models import SystemProfile

CREATOR_PATTERNS = (
    re.compile(r"\bsiapa(?:kah)?\s+(?:yang\s+)?(?:membuat|menciptakan|mengembangkan)\b", re.IGNORECASE),
    re.compile(r"\bsiapa(?:kah)?\s+(?:pembuat|pencipta|developer)\b", re.IGNORECASE),
    re.compile(r"\bwho\s+(?:created|made|developed)\s+you\b", re.IGNORECASE),
    re.compile(r"\bwho\s+is\s+your\s+(?:creator|developer)\b", re.IGNORECASE),
)
ROLE_PATTERNS = (
    re.compile(r"\b(?:apa|apakah)\s+(?:tugas|fungsi)\s+(?:anda|kamu|mu)\b", re.IGNORECASE),
    re.compile(r"\b(?:tugas|fungsi)\s+(?:anda|kamu|mu)\s+(?:apa|apa\?)?\b", re.IGNORECASE),
    re.compile(r"\b(?:anda|kamu)\s+bisa\s+apa\b", re.IGNORECASE),
    re.compile(r"\bwho\s+are\s+you\b", re.IGNORECASE),
    re.compile(r"\bwhat\s+(?:do\s+you\s+do|is\s+your\s+(?:task|role|function))\b", re.IGNORECASE),
)
PERSON_LOOKUP_PATTERNS = (
    re.compile(r"\bsiapa(?:kah)?\b", re.IGNORECASE),
    re.compile(r"\bwho\s+is\b", re.IGNORECASE),
)
WORD_PATTERN = re.compile(r"[a-zA-Z0-9]+")
NAME_STOPWORDS = {
    "dan",
    "the",
    "who",
    "siapa",
    "siapakah",
    "yang",
}


class AppIdentityMode(StrEnum):
    CREATOR = "creator_identity"
    ROLE = "system_identity"
    PROFILE = "application_profile"


@dataclass(frozen=True)
class AppIdentityRoute:
    mode: AppIdentityMode


def detect_app_identity_question(
    question: str,
    profile: SystemProfile | None = None,
) -> AppIdentityRoute | None:
    normalized_question = question.strip()
    if not normalized_question:
        return None

    creator_match = _matches_any(CREATOR_PATTERNS, normalized_question)
    role_match = _matches_any(ROLE_PATTERNS, normalized_question)

    if profile is not None and _matches_creator_name_question(
        normalized_question,
        profile,
    ):
        creator_match = True

    if creator_match and role_match:
        return AppIdentityRoute(mode=AppIdentityMode.PROFILE)

    if creator_match:
        return AppIdentityRoute(mode=AppIdentityMode.CREATOR)

    if role_match:
        return AppIdentityRoute(mode=AppIdentityMode.ROLE)

    return None


def build_app_identity_context(
    profile: SystemProfile,
    route: AppIdentityRoute,
) -> str:
    base_instruction = (
        "Informasi internal aplikasi untuk menjawab pertanyaan pengguna.\n"
        "Jawab secara langsung dan natural.\n"
        "Jangan menyebut profile, context, metadata, atau label sumber internal.\n"
        "Jika pengguna bertanya tugas/fungsi assistant, jelaskan memakai "
        "Assistant name dan Assistant description.\n"
        "Jika pengguna bertanya pembuat/creator, jelaskan memakai Creator name "
        "dan Creator description.\n"
    )

    if route.mode == AppIdentityMode.PROFILE:
        return (
            base_instruction
            + (
            f"Assistant name: {profile.assistant_name}\n"
            f"Assistant description: {profile.assistant_description}\n"
            f"Creator name: {profile.creator_name}\n"
            f"Creator description: {profile.creator_description}\n"
            "Answer only using this application profile information."
            )
        )

    if route.mode == AppIdentityMode.CREATOR:
        return (
            base_instruction
            + (
            f"Assistant name: {profile.assistant_name}\n"
            f"Creator name: {profile.creator_name}\n"
            f"Creator description: {profile.creator_description}\n"
            "Answer only using this creator information."
            )
        )

    return (
        base_instruction
        + (
        f"Assistant name: {profile.assistant_name}\n"
        f"Assistant description: {profile.assistant_description}\n"
        "Answer only using this assistant information."
        )
    )


def _matches_any(patterns: tuple[re.Pattern[str], ...], value: str) -> bool:
    return any(pattern.search(value) for pattern in patterns)


def _matches_creator_name_question(question: str, profile: SystemProfile) -> bool:
    if not _matches_any(PERSON_LOOKUP_PATTERNS, question):
        return False

    question_tokens = _tokens(question)
    creator_tokens = _tokens(profile.creator_name)
    if not creator_tokens:
        return False

    return bool(question_tokens & creator_tokens)


def _tokens(value: str) -> set[str]:
    return {
        token
        for token in WORD_PATTERN.findall(value.casefold())
        if len(token) > 2 and token not in NAME_STOPWORDS
    }
