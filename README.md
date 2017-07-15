# ansible-gvm-module

[![Build Status](https://travis-ci.org/suzuki-shunsuke/ansible-gvm-module.svg?branch=master)](https://travis-ci.org/suzuki-shunsuke/ansible-gvm-module)

ansible module to run gvm command.

https://galaxy.ansible.com/suzuki-shunsuke/gvm-module/

## Notice

* This module doesn't support the [check mode](http://docs.ansible.com/ansible/dev_guide/developing_modules_general.html#supporting-check-mode)
* gvm is the abbreviation for [Go Version Manager](https://github.com/moovweb/gvm), and this module has nothing to do with [Groovy enVironment Manager](http://sdkman.io/).

## Supported platform

* GenericLinux
* MacOSX

We test this module in

* Ubuntu 16.04 (Vagrant, Virtualbox)
* CentOS 7.3 (Vagrant, Virtualbox)
* MaxOS Sierra 10.12.5

## Requirements

* [gvm](https://github.com/moovweb/gvm)
* [golang build dependencies](https://github.com/moovweb/gvm#mac-os-x-requirements)

If you want to install gvm and golang build dependencies with ansible role, we recommend the [suzuki-shunsuke.gvm](https://galaxy.ansible.com/suzuki-shunsuke/gvm/).

## Supported gvm subcommands and options

```
$ gvm install <version> [--binary] [--prefer-binary] [--with-build-tools] [--with-protobuf]
$ gvm uninstall <version>
$ gvm list
$ gvm listall
$ gvm alias list
$ gvm alias create <alias> <version>
$ gvm alias delete <alias>
```

## Install

```
$ ansible-galaxy install suzuki-shunsuke.gvm-module
```

```yaml
# playbook.yml

- hosts: default
  roles:
  # After you call this role, you can use this module.
  - suzuki-shunsuke.gvm-module
```

## Options

### Common Options

name | type | required | default | choices / example | description
--- | --- | --- | --- | --- | ---
subcommand | str | no | install | [install, uninstall, list, listall, alias list, alias create, alias delete] |
gvm_root | str | no | | ~/.gvm | If the environment variable "GVM_ROOT" is not set, this option is required
expanduser | bool | no | yes | | By default the environment variable GVM_ROOT and "gvm_root" option are filtered by [os.path.expanduser](https://docs.python.org/2.7/library/os.path.html#os.path.expanduser)

### Options of the "install" subcommand

parameter | type | required | default | choices / example | description
--- | --- | --- | --- | --- | ---
version | str | yes | | go1.4 |
binary | bool | no | no | | If you want to avoid compile errors, we recommend to set this option to "yes"
prefer_binary | bool | no | no | |
with_build_tools | bool | no | no | |
with_protobuf | bool | no | no | |

### Options of the "uninstall" subcommand

parameter | type | required | default | choices / example | description
--- | --- | --- | --- | --- | ---
version | str | yes | | go1.4 |

### Options of the "list" subcommand

Nothing.

The return value of the "list" subcommand has "versions" field.

### Options of the "listall" subcommand

Nothing.

The return value of the "listall" subcommand has "versions" field.

### Options of the "alias list" subcommand

Nothing.

The return value of the "alias list" subcommand has "aliases" field.

### Options of the "alias create" subcommand

parameter | type | required | default | choices / example | description
--- | --- | --- | --- | --- | ---
version | str | yes | | go1.4 |
alias | str | yes | | foo |

### Options of the "alias delete" subcommand

parameter | type | required | default | choices / example | description
--- | --- | --- | --- | --- | ---
alias | str | yes | | foo |

## Example

```yaml
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
```

## Change Log

See [CHANGELOG.md](CHANGELOG.md).

## See also

* [suzuki-shunsuke.gvm](https://github.com/suzuki-shunsuke/ansible-gvm): ansible role to install gvm

## Licence

[MIT](LICENSE)

## Develop

### Requirements

* Vagrant
* Ansible
* Node.js
* yarn

### Setup

```
$ yarn install
$ cd tests
$ ansible-galaxy install -r roles.yml
```

### Test

```
$ cd tests
$ vagrant up --provision
```
