#!/usr/bin/python
# -*- coding: utf-8 -*-

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: gvm
short_description: Run gvm command
options:
  alias:
    description:
    - A golang alias name
    type: str
    required: false
    default: null
  binary:
    description:
    - the "--binary" option of gvm install
    required: false
    type: bool
    default: false
  expanduser:
    description:
    - whether the environment variable GVM_ROOT and "gvm_root" option are filtered by os.path.expanduser
    required: false
    type: bool
    default: true
  gvm_root:
    description:
    - GVM_ROOT
    required: false
    type: str
    default: null
  prefer_binary:
    description:
    - the "--prefer-binary" option of gvm install
    required: false
    type: bool
    default: false
  subcommand:
    description:
    - gvm subcommand
    choices: ["install", "list", "listall", "uninstall", "alias list", "alias create", "alias delete"]
    required: false
    default: install
  version:
    description:
    - A golang version name
    type: str
    required: false
    default: null
  with_build_tools:
    description:
    - the "--with-build-tools" option of gvm install
    required: false
    type: bool
    default: false
  with_protobuf:
    description:
    - the "--with-protobuf" option of gvm install
    required: false
    type: bool
    default: false
requirements:
- gvm
author: "Suzuki Shunsuke"
'''

EXAMPLES = '''
- name: gvm install go1.4
  gvm:
    version: go1.4
    gvm_root: "~/.gvm"

- name: gvm install go1.5 --binary
  gvm:
    version: go1.5
    gvm_root: "~/.gvm"
    binary: yes

- name: gvm uninstall go1.5
  gvm:
    subcommand: uninstall
    version: go1.5
    gvm_root: "~/.gvm"

- name: gvm list
  gvm:
    subcommand: list
    gvm_root: "~/.gvm"
  register: result
- debug:
    var: result.versions

- name: gvm listall
  gvm:
    subcommand: listall
    gvm_root: "~/.gvm"
  register: result
- debug:
    var: result.versions

- name: gvm alias create foo go1.4
  gvm:
    subcommand: alias create
    version: go1.4
    alias: foo
    gvm_root: "~/.gvm"

- name: gvm alias list
  gvm:
    subcommand: alias list
    gvm_root: "~/.gvm"
  register: result
- debug:
    var: result.aliases

- name: gvm alias delete foo
  gvm:
    subcommand: alias delete
    alias: foo
    gvm_root: "~/.gvm"
'''

RETURNS = '''
versions:
  description: the return value of `gvm list` or `gvm listall`
  returned: success
  type: list
  sample:
  - go1.4
aliases:
  description: the return value of `gvm alias list`
  returned: success
  type: dict
  sample:
    foo: go1.4
'''

import os  # noqa E402
import re  # noqa E402

from ansible.module_utils.basic import AnsibleModule  # noqa E402


def wrap_get_func(func):
    def wrap(module, *args, **kwargs):
        result, data = func(module, *args, **kwargs)
        if result:
            module.exit_json(**data)
        else:
            module.fail_json(**data)

    return wrap


ALIAS_LIST_LINE_PATTERN = re.compile(r"(\S+) +\((\S+)\)")


def parse_alias(value):
    """
    "./alias (version)" -> (alias, version)
    """
    m = ALIAS_LIST_LINE_PATTERN.match(value)
    # remove "./" from alias
    return (m.group(1)[2:], m.group(2)) if m else None


def get_alias_list(module, cmd_path, **kwargs):
    """ gvm alias list
    """
    cmd = [cmd_path, "alias", "list"]
    rc, out, err = module.run_command(cmd, **kwargs)
    if rc:
        return (False, dict(msg=err, stdout=out))
    else:
        # slice: remove last newline
        failed_lines = []
        aliases = {}
        for line in out.split("\n"):
            line = line.strip()
            if not line or line == "gvm go aliases":
                continue
            m = parse_alias(line)
            if m is None:
                failed_lines.append(line)
                continue
            aliases[m[0]] = m[1]
        if failed_lines:
            err = "{}\n{}".format(err, "\n".join(failed_lines)).strip()
        return (True, dict(
            changed=False, failed=False, stdout=out, stderr=err,
            aliases=aliases))


cmd_alias_list = wrap_get_func(get_alias_list)


def get_list(module, cmd_path, **kwargs):
    """ gvm list
    """
    cmd = [cmd_path, "list"]
    rc, out, err = module.run_command(cmd, **kwargs)
    if rc:
        return (False, dict(msg=err, stdout=out))
    else:
        # slice: remove last newline
        versions = [line.strip() for line in out.split("\n")
                    if line.strip() and line.strip() != "gvm gos (installed)"]
        return (True, dict(
            changed=False, failed=False, stdout=out, stderr=err,
            versions=versions))


cmd_list = wrap_get_func(get_list)


def get_listall(module, cmd_path, **kwargs):
    """ gvm listall
    """
    cmd = [cmd_path, "listall"]
    rc, out, err = module.run_command(cmd, **kwargs)
    if rc:
        return (False, dict(msg=err, stdout=out))
    else:
        # slice: remove last newline
        versions = [line.strip() for line in out.split("\n") if line.strip()]
        return (True, dict(
            changed=False, failed=False, stdout=out, stderr=err,
            versions=versions))


cmd_listall = wrap_get_func(get_listall)


def cmd_alias_delete(module, cmd_path, alias, **kwargs):
    """ gvm alias delete <alias>
    """
    result, data = get_alias_list(module, cmd_path, **kwargs)
    if not result:
        module.fail_json(**data)
    if alias not in data["aliases"]:
        return module.exit_json(
            changed=False, failed=False, stdout="", stderr="")

    cmd = [cmd_path, "alias", "delete", alias]
    rc, out, err = module.run_command(cmd, **kwargs)
    if rc:
        return module.fail_json(msg=err, stdout=out)
    else:
        return module.exit_json(
            changed=True, failed=False, stdout=out, stderr=err)


def cmd_uninstall(module, cmd_path, version, **kwargs):
    """ gvm uninstall <version>
    """
    result, data = get_list(module, cmd_path, **kwargs)
    if not result:
        module.fail_json(**data)
    if version not in data["versions"]:
        return module.exit_json(
            changed=False, failed=False, stdout="", stderr="")

    cmd = [cmd_path, "uninstall", version]
    rc, out, err = module.run_command(cmd, **kwargs)
    if rc:
        return module.fail_json(msg=err, stdout=out)
    else:
        return module.exit_json(
            changed=True, failed=False, stdout=out, stderr=err)


def cmd_install(module, cmd_path, version, params, **kwargs):
    """ gvm install <version> [--binary] [--prefer-binary] [--with-build-tools]
                              [--with-protobuf]
    """
    result, data = get_list(module, cmd_path, **kwargs)
    if not result:
        module.fail_json(**data)
    if version in data["versions"]:
        return module.exit_json(
            changed=False, failed=False,
            stdout="Already installed!", stderr="")

    cmd = [cmd_path, "install", version]
    for key in [
            "binary", "prefer_binary", "with_build_tools", "with_protobuf"]:
        if params[key]:
            cmd.append("--{}".format(key.replace("_", "-")))

    rc, out, err = module.run_command(cmd, **kwargs)
    if rc:
        return module.fail_json(msg=err, stdout=out)
    else:
        return module.exit_json(
            changed=True, failed=False, stdout=out, stderr=err)


def cmd_alias_create(module, cmd_path, alias, version, **kwargs):
    """ gvm alias create <alias> <version>
    """
    result, data = get_alias_list(module, cmd_path, **kwargs)
    if not result:
        module.fail_json(**data)
    if alias in data["aliases"]:
        if version == data["aliases"][alias]:
            return module.exit_json(
                changed=False, failed=False,
                stdout="Alias already exists!", stderr="")
        else:
            return module.fail_json(
                msg="{} already exists but version differs".format(alias))

    cmd = [cmd_path, "alias", "create", alias, version]

    rc, out, err = module.run_command(cmd, **kwargs)
    if rc:
        return module.fail_json(msg=err, stdout=out)
    else:
        return module.exit_json(
            changed=True, failed=False, stdout=out, stderr=err)


MSGS = {
    "required_gvm_root": (
        "Either the environment variable 'GVM_ROOT' "
        "or 'gvm_root' option is required"),
    "required_version": "version option is required",
    "required_alias": "alias option is required",
}


def get_gvm_root(params):
    if params["gvm_root"]:
        if params["expanduser"]:
            return os.path.expanduser(params["gvm_root"])
        else:
            return params["gvm_root"]
    else:
        if "GVM_ROOT" not in os.environ:
            return None
        if params["expanduser"]:
            return os.path.expanduser(os.environ["GVM_ROOT"])
        else:
            return os.environ["GVM_ROOT"]


def main():
    module = AnsibleModule(argument_spec={
        "alias": {"required": False, "type": "str", "default": None},
        "binary": {"required": False, "type": "bool", "default": False},
        "expanduser": {"required": False, "type": "bool", "default": True},
        "gvm_root": {"required": False, "default": None},
        "prefer_binary": {"required": False, "type": "bool", "default": False},
        "subcommand": {
            "required": False, "default": "install",
            "choices": [
                "install", "list", "listall", "uninstall",
                "alias list", "alias create", "alias delete"]
        },
        "version": {"required": False, "type": "str", "default": None},
        "with_build_tools": {
            "required": False, "type": "bool", "default": False},
        "with_protobuf": {"required": False, "type": "bool", "default": False},
    })
    params = module.params
    environ_update = {}
    gvm_root = get_gvm_root(params)
    if gvm_root is None:
        return module.fail_json(
            msg=MSGS["required_gvm_root"])
    environ_update["GVM_ROOT"] = gvm_root
    cmd_path = os.path.join(gvm_root, "bin", "gvm")

    if params["subcommand"] == "install":
        version = params["version"]
        if not version:
            return module.fail_json(msg=MSGS["required_version"])
        return cmd_install(
            module, cmd_path, version, params, environ_update=environ_update)
    elif params["subcommand"] == "uninstall":
        version = params["version"]
        if not version:
            return module.fail_json(msg=MSGS["required_version"])
        return cmd_uninstall(
            module, cmd_path, version, environ_update=environ_update)
    elif params["subcommand"] == "list":
        return cmd_list(
            module, cmd_path, environ_update=environ_update)
    elif params["subcommand"] == "listall":
        return cmd_listall(
            module, cmd_path, environ_update=environ_update)
    elif params["subcommand"] == "alias list":
        return cmd_alias_list(
            module, cmd_path, environ_update=environ_update)
    elif params["subcommand"] == "alias create":
        version = params["version"]
        if not version:
            return module.fail_json(msg=MSGS["required_version"])
        alias = params["alias"]
        if not alias:
            return module.fail_json(msg=MSGS["required_alias"])
        return cmd_alias_create(
            module, cmd_path, alias, version, environ_update=environ_update)
    elif params["subcommand"] == "alias delete":
        alias = params["alias"]
        if not alias:
            return module.fail_json(msg=MSGS["required_alias"])
        return cmd_alias_delete(
            module, cmd_path, alias, environ_update=environ_update)


if __name__ == '__main__':
    main()
