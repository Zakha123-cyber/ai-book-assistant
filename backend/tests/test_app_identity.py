import unittest

from models import SystemProfile
from services.qa.app_identity import (
    AppIdentityMode,
    build_app_identity_context,
    detect_app_identity_question,
)


class AppIdentityTest(unittest.TestCase):
    def test_detects_assistant_role_question(self) -> None:
        route = detect_app_identity_question("tugas anda apa?")

        self.assertIsNotNone(route)
        self.assertEqual(route.mode, AppIdentityMode.ROLE)

    def test_detects_creator_question(self) -> None:
        route = detect_app_identity_question("siapakah yang menciptakan anda?")

        self.assertIsNotNone(route)
        self.assertEqual(route.mode, AppIdentityMode.CREATOR)

    def test_detects_combined_role_and_creator_question(self) -> None:
        route = detect_app_identity_question(
            "apa tugas anda, dan siapakah yang menciptakan anda?"
        )

        self.assertIsNotNone(route)
        self.assertEqual(route.mode, AppIdentityMode.PROFILE)

    def test_ignores_book_question(self) -> None:
        route = detect_app_identity_question("siapa pak wira?")

        self.assertIsNone(route)

    def test_detects_creator_name_question_from_profile(self) -> None:
        profile = SystemProfile(
            profile_key="default",
            assistant_name="AI Book Assistant",
            assistant_description="Assistant description.",
            creator_name="Zakha Aditya Hadiansyah, Abdurrahman Qoim Haqqi Muhammad",
            creator_description="Creator description.",
        )

        route = detect_app_identity_question("siapakah zakha?", profile=profile)

        self.assertIsNotNone(route)
        self.assertEqual(route.mode, AppIdentityMode.CREATOR)

    def test_does_not_match_unrelated_person_question_from_profile(self) -> None:
        profile = SystemProfile(
            profile_key="default",
            assistant_name="AI Book Assistant",
            assistant_description="Assistant description.",
            creator_name="Zakha Aditya Hadiansyah",
            creator_description="Creator description.",
        )

        route = detect_app_identity_question("siapa pak wira?", profile=profile)

        self.assertIsNone(route)

    def test_builds_creator_context_from_profile(self) -> None:
        profile = SystemProfile(
            profile_key="default",
            assistant_name="AI Book Assistant",
            assistant_description="Assistant description.",
            creator_name="Creator Name",
            creator_description="Creator description.",
        )

        context = build_app_identity_context(
            profile,
            detect_app_identity_question("who created you?"),
        )

        self.assertNotIn("System Creator Profile", context)
        self.assertIn("Creator Name", context)
        self.assertIn("Creator description.", context)
        self.assertIn("Jangan menyebut profile", context)

    def test_builds_combined_profile_context(self) -> None:
        profile = SystemProfile(
            profile_key="default",
            assistant_name="AI Book Assistant",
            assistant_description="Assistant description.",
            creator_name="Creator Name",
            creator_description="Creator description.",
        )

        context = build_app_identity_context(
            profile,
            detect_app_identity_question(
                "apa tugas anda, dan siapakah yang menciptakan anda?"
            ),
        )

        self.assertIn("AI Book Assistant", context)
        self.assertIn("Assistant description.", context)
        self.assertIn("Creator Name", context)
        self.assertIn("Creator description.", context)


if __name__ == "__main__":
    unittest.main()
