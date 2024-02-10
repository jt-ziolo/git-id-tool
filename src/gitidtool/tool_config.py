from dataclasses import dataclass
import json
import logging
from pathlib import Path
from typing import Any
from gitidtool.click_echo_wrapper import ClickEchoWrapper
from gitidtool.git_data import GitDataEntry


@dataclass
class ToolConfigEntry:
    name: str
    email: str
    signing_key: str
    remotes: dict[str, str]

    def __key(self):
        dict_json = json.dumps(self.remotes, separators=(",", ":"), sort_keys=True)
        return (self.name, self.email, self.signing_key, dict_json)

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if isinstance(other, ToolConfigEntry):
            return self.__key() == other.__key()
        return NotImplemented


@dataclass
class ToolConfigEntryFactory:
    def create_from_git_data_entry(self, entry: GitDataEntry):
        remotes_dict: dict[str, str] = {}
        for remote in entry.remotes:
            remotes_dict[remote.remote_name] = remote.hostname
        output = ToolConfigEntry(
            entry.name, entry.email, entry.signing_key, remotes_dict
        )
        return output


class ToolConfigContextManager:
    def __init__(self, logger: logging.Logger = None):
        self._entries: set[ToolConfigEntry] = set()
        self._logger = logger

    def __enter__(self):
        return self._entries

    def __exit__(self, exc_type, exc_value, exc_traceback):
        pass


def config_to_json_str(entries: set[ToolConfigEntry]):
    records: list[dict[str, Any]] = []
    for entry in entries:
        dict_repr = {
            "name": entry.name,
            "email": entry.email,
            "signing_key": entry.signing_key,
            "remotes": entry.remotes,
        }
        records.append(dict_repr)
    return json.dumps(records, separators=(",", ":"), sort_keys=True)


def json_str_to_config(json_str: str):
    records: list[dict[str, Any]] = json.loads(json_str)
    entries: set[ToolConfigEntry] = set()
    for record in records:
        next_entry = ToolConfigEntry(
            record["name"], record["email"], record["signing_key"], record["remotes"]
        )
        entries.add(next_entry)
    return entries


class ToolConfigJsonContextManager(ToolConfigContextManager):
    def __init__(self, logger: logging.Logger = None):
        super().__init__(logger)
        self._click_echo_wrapper = ClickEchoWrapper()

    def __exit__(self, exc_type, exc_value, exc_traceback):
        msg = config_to_json_str(self._entries)
        # echo the json representation to the command line
        self._click_echo_wrapper.clear()
        self._click_echo_wrapper.add_line(msg)
        self._click_echo_wrapper.echo_all()

        if self._logger:
            self._logger.log(level=logging.DEBUG, msg=msg)


class ToolConfigJsonFileContextManager(ToolConfigContextManager):
    def __init__(self, path, logger: logging.Logger = None):
        super().__init__(logger)
        self._path = path

    def _read_to_memory_from_file(self):
        json_str = ""
        with open(self._path, "r", encoding="utf-8") as f:
            json_str = f.read()
        self._entries = json_str_to_config(json_str)

    def __enter__(self):
        if Path(self._path).exists():
            # read and convert json file data first
            self._read_to_memory_from_file()
        return self._entries

    def __exit__(self, exc_type, exc_value, exc_traceback):
        # write the json representation to the file
        with open(self._path, "w", encoding="utf-8") as f:
            f.write(config_to_json_str(self._entries))
