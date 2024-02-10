import unittest
import random

from faker import Faker

from tests.cases import Case, CaseGenerator


class TestCaseGeneration(unittest.TestCase):
    def setUp(self):
        self.seed = "example_seed"
        fake = Faker()
        fake.seed_instance(self.seed)
        random.seed(self.seed)
        self.generator = CaseGenerator(faker=fake)

    def test_repr_overload(self):
        case = self.generator.generate_git()
        self.assertIsNotNone(repr(case))
        self.assertNotEqual(repr(case), "")
        case = self.generator.generate_gpg()
        self.assertIsNotNone(repr(case))
        self.assertNotEqual(repr(case), "")
        case = self.generator.generate_ssh()
        self.assertIsNotNone(repr(case))
        self.assertNotEqual(repr(case), "")
        # Assert repr works with combining case parts together
        case = self.generator.generate_git(override_from_output=True)
        self.assertIsNotNone(repr(case))
        self.assertNotEqual(repr(case), "")
        case = self.generator.generate_gpg(case, True)
        self.assertIsNotNone(repr(case))
        self.assertNotEqual(repr(case), "")
        case = self.generator.generate_ssh(case, True)
        self.assertIsNotNone(repr(case))
        self.assertNotEqual(repr(case), "")

    def test_cases_consistent_for_same_seed(self):
        # Set the state to the initial state, so we can restore to it
        # Avoids issues if tests are ran out of order
        reset_fake = Faker()
        reset_fake.seed_instance(self.seed)
        reset_generator = CaseGenerator(faker=reset_fake)
        case = reset_generator.generate_git(override_from_output=True)
        case = reset_generator.generate_gpg(case, True)
        case = reset_generator.generate_ssh(case, True)
        first_output = repr(case)

        reset_fake = Faker()
        reset_fake.seed_instance(self.seed)
        reset_generator = CaseGenerator(faker=reset_fake)
        case = reset_generator.generate_git(override_from_output=True)
        case = reset_generator.generate_gpg(case, True)
        case = reset_generator.generate_ssh(case, True)
        # Should return same result
        self.assertEqual(first_output, repr(case))

    def test_cases_inconsistent_for_different_seed(self):
        case = self.generator.generate_git(override_from_output=True)
        case = self.generator.generate_gpg(case, True)
        case = self.generator.generate_ssh(case, True)
        first_output = repr(case)

        case = self.generator.generate_git(override_from_output=True)
        case = self.generator.generate_gpg(case, True)
        case = self.generator.generate_ssh(case, True)
        # Should return different result
        self.assertNotEqual(first_output, repr(case))

    def test_generation_with_overrides(self):
        initial_email = self.generator.email
        case = self.generator.generate_git(override_from_output=True)
        current_email = self.generator.email
        # Should change the value of the email property on the first call
        self.assertNotEqual(initial_email, current_email)
        # Result case part should match the generator's email property
        self.assertEqual(case.git_data[0].email, current_email)

        case = self.generator.generate_gpg(case, True)
        current_email = self.generator.email
        # Should not change the value of the email property any more
        self.assertEqual(current_email, self.generator.email)
        # Result case part should match the generator's email property
        self.assertEqual(case.gpg_data[0].email, current_email)

        case = self.generator.generate_ssh(case, True)
        current_email = self.generator.email
        # Should not change the value of the email property any more
        self.assertEqual(current_email, self.generator.email)
        # Result case part should match the generator's email property
        self.assertEqual(case.ssh_data[0].email, current_email)

    def test_generation_without_overrides(self):
        initial_email = self.generator.email
        case = self.generator.generate_git(override_from_output=False)
        current_email = self.generator.email
        # Should never change the value of the email property
        self.assertEqual(initial_email, current_email)

        case = self.generator.generate_gpg(case, False)
        current_email = self.generator.email
        # Should never change the value of the email property
        self.assertEqual(current_email, self.generator.email)

        case = self.generator.generate_ssh(case, False)
        current_email = self.generator.email
        # Should never change the value of the email property
        self.assertEqual(current_email, self.generator.email)

        # Each case part's email should be distinct from that of other case parts
        self.assertNotEqual(
            case.git_data[0].email, case.gpg_data[0].email, "git vs. gpg"
        )
        self.assertNotEqual(
            case.git_data[0].email, case.ssh_data[0].email, "git vs. ssh"
        )
        self.assertNotEqual(
            case.gpg_data[0].email, case.ssh_data[0].email, "gpg vs. ssh"
        )

    def test_generation_with_combination(self):
        case = self.generator.generate_git()

        def count(case: Case):
            return len(case.git_data) + len(case.gpg_data) + len(case.ssh_data)

        # Check that combining cases increases the "case part" count each time
        self.assertEqual(count(case), 1)
        case = self.generator.generate_gpg(case)
        self.assertEqual(count(case), 2)
        case = self.generator.generate_ssh(case)
        self.assertEqual(count(case), 3)
        case = self.generator.generate_ssh(case)
        case = self.generator.generate_git(case)
        case = self.generator.generate_ssh(case)
        self.assertEqual(count(case), 6)
        # Check that not combining cases does not increase the "case part" count
        case = self.generator.generate_gpg()
        self.assertNotEqual(count(case), 7)
        # It should be a new Case object, with only one "case part"
        self.assertEqual(count(case), 1)

        # Combining two different cases together
        case2 = self.generator.generate_git()
        for _ in range(5):
            case2 = self.generator.generate_git(case2)
            case2 = self.generator.generate_git(case2)
            case2 = self.generator.generate_git(case2)
            self.assertNotEqual(count(case), count(case2))
            case = self.generator.generate_git(case2)
            # Should result in a copy, not a reference
            self.assertNotEqual(count(case), count(case2))
            self.assertEqual(count(case), count(case2) + 1)


if __name__ == "__main__":
    unittest.main()
