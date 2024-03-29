from cases import Case, CaseGenerator
from faker import Faker
from unittest.mock import mock_open, patch
import logging
import unittest

from gitidtool.tool_config import (
    ToolConfigEntry,
    ToolConfigEntryFactory,
    ToolConfigJsonContextManager,
    ToolConfigJsonFileContextManager,
    config_to_json_str,
    json_str_to_config,
)


class TestConversion(unittest.TestCase):
    def test_config_conversion_roundtrip_single_entry(self):
        fake = Faker()
        generator = CaseGenerator(fake)
        factory = ToolConfigEntryFactory()
        for i in range(100):
            fake.seed_instance(i)
            case = generator.generate_git(override_from_output=True)

            config: set[ToolConfigEntry] = set()
            config.add(factory.create_from_git_data_entry(case.git_data[0]))

            json_str = config_to_json_str(config)
            config2 = json_str_to_config(json_str)
            self.assertEqual(config, config2)

            json_str2 = config_to_json_str(config)
            self.assertEqual(json_str, json_str2)

            # When we change the first config, the second config does not
            # change (they aren't linked by ref)
            entry = config.pop()
            entry.name = "something totally different"
            config.add(entry)
            self.assertNotEqual(config, config2)

            # Same for the new json str relative to the second config's json
            # str
            json_str = config_to_json_str(config)
            self.assertNotEqual(json_str, json_str2)

    def test_config_conversion_roundtrip_multiple_entries(self):
        fake = Faker()
        generator = CaseGenerator(fake)
        factory = ToolConfigEntryFactory()
        for i in range(10):
            fake.seed_instance(i)

            config: set[ToolConfigEntry] = set()
            case: Case = None
            # Generate multiple git data entries and add them to the same
            # config
            for j in range(5):
                case = generator.generate_git(case, True)
                case = generator.generate_gpg(case, True)
                case = generator.generate_ssh(case, True)
                config.add(factory.create_from_git_data_entry(case.git_data[j]))

            json_str = config_to_json_str(config)
            config2 = json_str_to_config(json_str)
            self.assertEqual(config, config2)

            json_str2 = config_to_json_str(config)
            self.assertEqual(json_str, json_str2)

            # When we change the first config, the second config does not
            # change (they aren't linked by ref)
            entry = config.pop()
            entry.name = "something totally different"
            config.add(entry)
            self.assertNotEqual(config, config2)

            # Same for the new json str relative to the second config's json
            # str
            json_str = config_to_json_str(config)
            self.assertNotEqual(json_str, json_str2)


class TestJsonContextManager(unittest.TestCase):
    def setUp(self) -> None:
        fake = Faker()
        fake.seed_instance("seed")
        generator = CaseGenerator(fake)
        factory = ToolConfigEntryFactory()

        # Config 1: a single git data entry
        self.config_example: set[ToolConfigEntry] = set()
        case = generator.generate_git(override_from_output=True)
        case = generator.generate_gpg(case, True)
        case = generator.generate_ssh(case, True)
        self.config_example.add(factory.create_from_git_data_entry(case.git_data[0]))

        # Config 2: multiple git data entries
        self.config_example2: set[ToolConfigEntry] = set()
        case = None
        # Generate multiple git data entries and add them to the same
        # config
        for i in range(5):
            case = generator.generate_git(case, True)
            case = generator.generate_gpg(case, True)
            case = generator.generate_ssh(case, True)
            self.config_example2.add(
                factory.create_from_git_data_entry(case.git_data[i])
            )

    def test_config_is_empty_on_entry(self):
        context_manager: ToolConfigJsonContextManager = ToolConfigJsonContextManager()
        config: set(ToolConfigEntry) = context_manager.__enter__()
        self.assertEqual(len(config), 0)
        # Assert the same when using the context via "with"
        with context_manager as config:
            self.assertEqual(len(config), 0)

    def test_config_is_modifiable_during_with(self):
        context_manager: ToolConfigJsonContextManager = ToolConfigJsonContextManager()

        with context_manager as config:
            # set the config to the first example
            config.update(self.config_example)
            self.assertEqual(context_manager._entries, config)
            self.assertNotEqual(len(config), 0)
            self.assertEqual(config, self.config_example)

        with context_manager as config2:
            # should still equal what it was set to in the first context
            self.assertEqual(config, self.config_example)
            # clear the config and set it to the second example
            config2.clear()
            config2.update(self.config_example2)
            self.assertEqual(context_manager._entries, config2)
            self.assertNotEqual(len(config2), 0)
            self.assertEqual(config2, self.config_example2)

    def test_config_prints_correctly_on_exit(self):
        logger = logging.getLogger(__name__)
        # should log the first config example as json to DEBUG
        with self.assertLogs(logger, level=logging.DEBUG) as cm:
            context_manager: ToolConfigJsonContextManager = (
                ToolConfigJsonContextManager(logger)
            )
            with context_manager as config:
                config.update(self.config_example)
            self.assertEqual(
                cm.output[0],
                f"DEBUG:test_tool_config:{config_to_json_str(self.config_example)}",
            )
        # can't add second config example case due to click echo length limits


class TestJsonFileContextManager(unittest.TestCase):
    def setUp(self):
        fake = Faker()
        fake.seed_instance("seed2")
        generator = CaseGenerator(fake)
        factory = ToolConfigEntryFactory()

        # Config 1: a single git data entry
        self.config_example: set[ToolConfigEntry] = set()
        case = generator.generate_git(override_from_output=True)
        case = generator.generate_gpg(case, True)
        case = generator.generate_ssh(case, True)
        self.config_example.add(factory.create_from_git_data_entry(case.git_data[0]))

        # Config 2: multiple git data entries
        self.config_example2: set[ToolConfigEntry] = set()
        case = None
        # Generate multiple git data entries and add them to the same
        # config
        for i in range(5):
            case = generator.generate_git(case, True)
            case = generator.generate_gpg(case, True)
            case = generator.generate_ssh(case, True)
            self.config_example2.add(
                factory.create_from_git_data_entry(case.git_data[i])
            )

        # Create mocks
        # Path.exists mock
        path_exists_patcher = patch("pathlib.Path.exists", return_value=True)
        path_exists_patcher.start()
        # "open" context manager mocks
        self.mock_open1 = mock_open(read_data=config_to_json_str(self.config_example))
        self.patcher1 = patch(
            "gitidtool.tool_config.open",
            self.mock_open1,
        )

        self.addCleanup(self.patcher1.stop)
        self.addCleanup(path_exists_patcher.stop)

    def test_config_is_not_empty_on_entry(self):
        context_manager: ToolConfigJsonFileContextManager = None
        config: set(ToolConfigEntry) = None
        with self.patcher1:
            context_manager = ToolConfigJsonFileContextManager("dummy")
            config = context_manager.__enter__()
            self.assertNotEqual(len(config), 0)
            self.assertEqual(config, self.config_example)
            # Assert the same when using the context via "with"
            with context_manager as config:
                self.assertNotEqual(len(config), 0)
                self.assertEqual(config, self.config_example)

    def test_config_is_modifiable_during_with(self):
        context_manager: ToolConfigJsonFileContextManager = (
            ToolConfigJsonFileContextManager("dummy")
        )

        with self.patcher1:
            with context_manager as config:
                # set the config to the second example instead
                config.clear()
                config.update(self.config_example2)
                self.assertEqual(context_manager._entries, config)
                self.assertNotEqual(config, self.config_example)
                self.assertEqual(config, self.config_example2)

            with context_manager as config2:
                # should still equal what it was set to in the first context
                self.assertEqual(config, self.config_example2)
                # clear the config and set it to the first example
                config2.clear()
                config2.update(self.config_example)
                self.assertEqual(context_manager._entries, config2)
                self.assertNotEqual(config2, self.config_example2)
                self.assertEqual(config2, self.config_example)

    def test_config_written_correctly_on_exit(self):
        # should call f.write(config_to_json_str(<config example>))
        context_manager: ToolConfigJsonFileContextManager = (
            ToolConfigJsonFileContextManager("dummy")
        )
        with self.patcher1 as m:
            with context_manager:
                pass
            handle = m()
            handle.write.assert_called_once_with(config_to_json_str(self.config_example))
            # try again, this time clearing the config prior to writing
            # note: tried to use a second example, and while the contents
            # matched, the order that they appeared in the json str did not,
            # resulting in false negative
            with context_manager as config:
                config.clear()
            handle.write.assert_called_with("[]")


if __name__ == "__main__":
    unittest.main()
