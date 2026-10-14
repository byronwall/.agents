#!/usr/bin/env python3
"""Generate a Finder Quick Action Automator workflow around a zsh script."""

from __future__ import annotations

import argparse
import plistlib
import re
import sys
import uuid
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", required=True, help="Finder menu item and bundle name")
    parser.add_argument("--script-file", required=True, type=Path, help="Self-contained zsh script; Finder paths arrive in $@")
    parser.add_argument("--output", required=True, type=Path, help="Destination ending in .workflow")
    parser.add_argument(
        "--send-file-type",
        action="append",
        dest="send_file_types",
        required=True,
        help="Accepted input UTI; repeat for multiple types",
    )
    parser.add_argument("--bundle-id", help="Bundle identifier; defaults to com.local.services.<slug>")
    return parser.parse_args()


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "finder-quick-action"


def build_info(name: str, bundle_id: str, send_file_types: list[str]) -> dict:
    return {
        "CFBundleDevelopmentRegion": "en_US",
        "CFBundleIdentifier": bundle_id,
        "CFBundleName": name,
        "CFBundleShortVersionString": "1.0",
        "NSServices": [
            {
                "NSMenuItem": {"default": name},
                "NSMessage": "runWorkflowAsService",
                "NSSendFileTypes": send_file_types,
            }
        ],
    }


def build_document(script: str) -> dict:
    action_uuid = str(uuid.uuid4()).upper()
    input_uuid = str(uuid.uuid4()).upper()
    output_uuid = str(uuid.uuid4()).upper()
    return {
        "actions": [
            {
                "action": {
                    "ActionBundlePath": "/System/Library/Automator/Run Shell Script.action",
                    "ActionName": "Run Shell Script",
                    "ActionParameters": {
                        "CheckedForUserDefaultShell": True,
                        "COMMAND_STRING": script,
                        "inputMethod": 1,
                        "shell": "/bin/zsh",
                        "source": "",
                    },
                    "AMAccepts": {
                        "Container": "List",
                        "Optional": False,
                        "Types": ["com.apple.cocoa.string"],
                    },
                    "AMActionVersion": "2.0.3",
                    "AMApplication": ["Automator"],
                    "AMProvides": {
                        "Container": "List",
                        "Types": ["com.apple.cocoa.string"],
                    },
                    "BundleIdentifier": "com.apple.RunShellScript",
                    "CanShowSelectedItemsWhenRun": False,
                    "CanShowWhenRun": True,
                    "Category": ["AMCategoryUtilities"],
                    "CFBundleVersion": "2.0.3",
                    "Class Name": "RunShellScriptAction",
                    "InputUUID": input_uuid,
                    "OutputUUID": output_uuid,
                    "UUID": action_uuid,
                },
                "isViewVisible": True,
            }
        ],
        "AMApplicationBuild": "346",
        "AMApplicationVersion": "2.3",
        "AMDocumentVersion": "2",
        "connectors": {},
        "workflowMetaData": {
            "serviceApplicationBundleID": "com.apple.finder",
            "serviceApplicationPath": "",
            "serviceInputTypeIdentifier": "com.apple.Automator.fileSystemObject",
            "serviceOutputTypeIdentifier": "com.apple.Automator.nothing",
            "serviceProcessesInput": 0,
            "workflowTypeIdentifier": "com.apple.Automator.servicesMenu",
        },
    }


def main() -> int:
    args = parse_args()
    output = args.output.expanduser().resolve()
    script_file = args.script_file.expanduser().resolve()

    if output.suffix != ".workflow":
        print("error: --output must end in .workflow", file=sys.stderr)
        return 2
    if output.exists():
        print(f"error: refusing to overwrite existing path: {output}", file=sys.stderr)
        return 2
    if not script_file.is_file():
        print(f"error: script file does not exist: {script_file}", file=sys.stderr)
        return 2

    script = script_file.read_text(encoding="utf-8")
    if not script.strip():
        print("error: script file is empty", file=sys.stderr)
        return 2

    bundle_id = args.bundle_id or f"com.local.services.{slugify(args.name)}"
    resources = output / "Contents" / "Resources"
    resources.mkdir(parents=True)

    with (output / "Contents" / "Info.plist").open("wb") as handle:
        plistlib.dump(build_info(args.name, bundle_id, args.send_file_types), handle, sort_keys=False)
    with (resources / "document.wflow").open("wb") as handle:
        plistlib.dump(build_document(script), handle, sort_keys=False)

    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
