import unittest
from unittest.mock import patch

from faker import Faker
from gitidtool.__init__ import write
from tests.cases import CaseGenerator


class TestWriteCmd(unittest.TestCase):
    def test_write_cmd_produces_correct_output(self):
        fake = Faker()
        generator = CaseGenerator(fake)
        case = generator.generate_git(override_from_output=True)
        case = generator.generate_gpg(case, True)
        case = generator.generate_ssh(case, True)

        with patch(
            "gitidtool.__init__._read_config",
            return_value=(case.git_data, case.gpg_data, case.ssh_data),
        ):
            write.callback("dummy", True)
