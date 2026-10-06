#!/usr/bin/env python3
"""Negative tests for the CI scripts: each bad fixture must make its check fail
with a clear error (never a traceback), and the real repo must pass.

Run: python3 tests/test_ci_checks.py
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "scripts")
STUDIO = os.path.join(ROOT, "plugins", "audiopod-studio")


def write(path, text):
    with open(path, "w") as fh:
        fh.write(text)


def load(path):
    with open(path) as fh:
        return json.load(fh)


def run(script, *args):
    proc = subprocess.run(
        [sys.executable, os.path.join(SCRIPTS, script), *args],
        capture_output=True, text=True,
    )
    return proc.returncode, proc.stdout + proc.stderr


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp)

    def assertFails(self, result, needle):
        code, out = result
        self.assertNotEqual(code, 0, out)
        self.assertIn(needle, out)
        self.assertNotIn("Traceback", out)

    def assertPasses(self, result):
        code, out = result
        self.assertEqual(code, 0, out)

    def plugin_copy(self):
        dst = os.path.join(self.tmp, "plugin")
        shutil.copytree(STUDIO, dst)
        return dst

    def edit_manifest(self, plugin, fn):
        path = os.path.join(plugin, ".codex-plugin", "plugin.json")
        m = load(path)
        fn(m)
        write(path, json.dumps(m, indent=2))


class RealRepoPasses(Base):
    def test_all_checks_pass(self):
        self.assertPasses(run("check_claude_manifests.py"))
        self.assertPasses(run("check_codex_manifest.py", "--offline"))
        self.assertPasses(run("lint_neutral_language.py"))
        out = os.path.join(self.tmp, "ok.zip")
        self.assertPasses(run("build_openai_zip.py", "--out", out))
        self.assertPasses(run("check_codex_manifest.py", "--offline", "--zip", out))
        unzipped = os.path.join(self.tmp, "unzipped")
        with zipfile.ZipFile(out) as zf:
            zf.extractall(unzipped)
        self.assertPasses(run("lint_neutral_language.py", unzipped))


class CodexManifest(Base):
    def check(self, mutate):
        plugin = self.plugin_copy()
        self.edit_manifest(plugin, mutate)
        return run("check_codex_manifest.py", "--offline", "--plugin", plugin)

    def test_d1_unknown_category(self):
        self.assertFails(self.check(lambda m: m["interface"].update(category="Music")), "interface.category")

    def test_d2_multiline_short_description(self):
        self.assertFails(self.check(lambda m: m["interface"].update(shortDescription="Stems\nand MIDI")),
                         "shortDescription: must be a single line")

    def test_d2_multiline_display_name(self):
        self.assertFails(self.check(lambda m: m["interface"].update(displayName="Audio\rPod")),
                         "displayName: must be a single line")

    def test_d6_non_string_default_prompt(self):
        self.assertFails(self.check(lambda m: m["interface"].update(defaultPrompt=["ok", 123])),
                         "interface.defaultPrompt[1]: must be a non-empty string")

    def test_path_outside_plugin(self):
        self.assertFails(self.check(lambda m: m["interface"].update(logo="./../outside.png")),
                         "points outside the plugin")


class BuiltZip(Base):
    def build(self, plugin=None):
        out = os.path.join(self.tmp, "a.zip")
        args = ["--out", out] + (["--plugin", plugin] if plugin else [])
        self.assertPasses(run("build_openai_zip.py", *args))
        return out

    def rezip(self, src, drop=(), replace=None):
        out = os.path.join(self.tmp, "b.zip")
        with zipfile.ZipFile(src) as zin, zipfile.ZipFile(out, "w") as zout:
            for info in zin.infolist():
                if info.filename in drop:
                    continue
                data = zin.read(info)
                if replace and info.filename in replace:
                    data = replace[info.filename](data)
                zout.writestr(info, data)
        return out

    def test_d3_logo_missing_from_zip(self):
        bad = self.rezip(self.build(), drop={"assets/icon.png"})
        self.assertFails(run("check_codex_manifest.py", "--offline", "--zip", bad),
                         "interface.logo: ./assets/icon.png does not exist")

    def test_d3_mcp_target_missing_from_zip(self):
        bad = self.rezip(self.build(), drop={".mcp.json"})
        self.assertFails(run("check_codex_manifest.py", "--offline", "--zip", bad),
                         "mcpServers: ./.mcp.json does not exist")

    def test_d3_screenshot_missing_from_zip(self):
        def add_shot(data):
            m = json.loads(data)
            m["interface"]["screenshots"] = ["./assets/shot.png"]
            return json.dumps(m).encode()
        bad = self.rezip(self.build(), replace={".codex-plugin/plugin.json": add_shot})
        self.assertFails(run("check_codex_manifest.py", "--offline", "--zip", bad),
                         "interface.screenshots[0]: ./assets/shot.png does not exist")

    def test_d3_zip_name_not_listing_name(self):
        def rename(data):
            m = json.loads(data)
            m["name"] = "audiopod-studio"
            return json.dumps(m).encode()
        bad = self.rezip(self.build(), replace={".codex-plugin/plugin.json": rename})
        self.assertFails(run("check_codex_manifest.py", "--offline", "--zip", bad), "expected 'audiopod'")


class BuildSafety(Base):
    def build(self, plugin):
        return run("build_openai_zip.py", "--plugin", plugin, "--out", os.path.join(self.tmp, "x.zip"))

    def test_d5_symlink_file(self):
        plugin = self.plugin_copy()
        os.symlink("icon.png", os.path.join(plugin, "assets", "link.png"))
        self.assertFails(self.build(plugin), "assets/link.png: symlinks are not allowed")

    def test_d5_symlink_outside_root(self):
        plugin = self.plugin_copy()
        outside = os.path.join(self.tmp, "outside-skill")
        os.makedirs(outside)
        write(os.path.join(outside, "SKILL.md"), "---\nname: x\ndescription: x\n---\n")
        os.symlink(outside, os.path.join(plugin, "skills", "escape"))
        self.assertFails(self.build(plugin), "skills/escape: symlinks are not allowed")

    def test_d5_symlink_in_excluded_dir(self):
        plugin = self.plugin_copy()
        os.symlink("/etc/passwd", os.path.join(plugin, "evals", "passwd"))
        self.assertFails(self.build(plugin), "evals/passwd: symlinks are not allowed")

    def test_d5_hidden_file_under_skills(self):
        plugin = self.plugin_copy()
        write(os.path.join(plugin, "skills", "audiopod-jobs", ".notes.md"), "x")
        self.assertFails(self.build(plugin), "hidden files and directories are not allowed under skills/")

    def test_d5_hidden_dir_under_skills(self):
        plugin = self.plugin_copy()
        os.makedirs(os.path.join(plugin, "skills", ".draft"))
        self.assertFails(self.build(plugin), "skills/.draft: hidden files and directories")


class NeutralLint(Base):
    def lint(self, name, text):
        path = os.path.join(self.tmp, name)
        write(path, text)
        return run("lint_neutral_language.py", path)

    def test_d4_flags_each_term(self):
        for name, text in [
            ("a.md", "Ask Claude to do it."),
            ("b.md", "Built by Anthropic."),
            ("c.md", "Open it in Cowork."),
            ("d.md", "Make an artifact."),
            ("e.md", "Run /mcp to reconnect."),
            ("f.md", "Run /plugin install audiopod."),
            ("g.md", "Use /audiopod:stems for this."),
            ("h.md", "Or /audiopod-studio:tts."),
        ]:
            with self.subTest(text=text):
                self.assertFails(self.lint(name, text), "Host-specific language")

    def test_d4_scans_yaml_and_other_text(self):
        self.assertFails(self.lint("case.yaml", "prompt: ask claude\n"), "case.yaml")
        self.assertFails(self.lint("notes", "made for Claude\n"), "notes")

    def test_urls_are_not_slash_commands(self):
        self.assertPasses(self.lint("ok.md", "See https://chatgpt.com/plugins and https://x.ai/plugin and https://y.ai/mcp\n"))


class ClaudeMarketplace(Base):
    def market(self, mutate):
        root = os.path.join(self.tmp, "repo")
        shutil.copytree(os.path.join(ROOT, ".claude-plugin"), os.path.join(root, ".claude-plugin"))
        shutil.copytree(os.path.join(ROOT, "plugins"), os.path.join(root, "plugins"))
        path = os.path.join(root, ".claude-plugin", "marketplace.json")
        m = load(path)
        mutate(m)
        write(path, json.dumps(m, indent=2))
        return run("check_claude_manifests.py", "--root", root)

    def test_d6_extra_entry_with_missing_source_dir(self):
        def add(m):
            m["plugins"].append({"name": "ghost", "source": "./plugins/ghost", "version": m["metadata"]["version"]})
        self.assertFails(self.market(add), "ghost: source directory ./plugins/ghost does not exist")

    def test_d6_entry_without_source(self):
        self.assertFails(self.market(lambda m: m["plugins"][0].pop("source")), "audiopod has no source")

    def test_d6_expected_plugin_missing(self):
        self.assertFails(self.market(lambda m: m["plugins"].pop(1)), "audiopod-studio is not listed")


if __name__ == "__main__":
    unittest.main(verbosity=2)
