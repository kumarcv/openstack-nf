# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright (c) 2012 Openstack, LLC.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


import os
import re


class CommandFilter(object):
    """Command filter only checking that the 1st argument matches exec_path"""

    def __init__(self, exec_path, run_as, *args):
        self.exec_path = exec_path
        self.run_as = run_as
        self.args = args

    def match(self, userargs):
        """Only check that the first argument (command) matches exec_path"""
        return os.path.basename(self.exec_path) == userargs[0]

    def get_command(self, userargs):
        """Returns command to execute (with sudo -u if run_as != root)."""
        if (self.run_as != 'root'):
            # Used to run commands at lesser privileges
            return ['sudo', '-u', self.run_as, self.exec_path] + userargs[1:]
        return [self.exec_path] + userargs[1:]

    def get_environment(self, userargs):
        """Returns specific environment to set, None if none"""
        return None


class ExecCommandFilter(CommandFilter):
    def exec_args(self, userargs):
        return []


class RegExpFilter(CommandFilter):
    """Command filter doing regexp matching for every argument"""

    def match(self, userargs):
        # Early skip if command or number of args don't match
        if (len(self.args) != len(userargs)):
            # DENY: argument numbers don't match
            return False
        # Compare each arg (anchoring pattern explicitly at end of string)
        for (pattern, arg) in zip(self.args, userargs):
            try:
                if not re.match(pattern + '$', arg):
                    break
            except re.error:
                # DENY: Badly-formed filter
                return False
        else:
            # ALLOW: All arguments matched
            return True

        # DENY: Some arguments did not match
        return False


class DnsmasqFilter(CommandFilter):
    """Specific filter for the dnsmasq call (which includes env)"""

    def is_dnsmasq_cmd(self, argv):
        if (argv[0] == "dnsmasq"):
            return True
        return False

    def is_dnsmasq_env_vars(self, argv):
        if (argv[0].startswith("QUANTUM_RELAY_SOCKET_PATH=") and
            argv[1].startswith("QUANTUM_NETWORK_ID=")):
            return True
        return False

    def match(self, userargs):
        """This matches the combination of the leading env
        vars plus "dnsmasq" """
        if (self.is_dnsmasq_env_vars(userargs) and
            self.is_dnsmasq_cmd(userargs[2:])):
            return True
        return False

    def get_command(self, userargs):
        return [self.exec_path] + userargs[3:]

    def get_environment(self, userargs):
        env = os.environ.copy()
        env['QUANTUM_RELAY_SOCKET_PATH'] = userargs[0].split('=')[-1]
        env['QUANTUM_NETWORK_ID'] = userargs[1].split('=')[-1]
        return env


class DnsmasqNetnsFilter(DnsmasqFilter):
    """Specific filter for the dnsmasq call (which includes env)"""

    def is_ip_netns_cmd(self, argv):
        if ((argv[0] == "ip") and
            (argv[1] == "netns") and
            (argv[2] == "exec")):
            return True
        return False

    def match(self, userargs):
        """This matches the combination of the leading env
        vars plus "ip" "netns" "exec" <foo> "dnsmasq" """
        if (self.is_dnsmasq_env_vars(userargs) and
            self.is_ip_netns_cmd(userargs[2:]) and
            self.is_dnsmasq_cmd(userargs[6:])):
            return True
        return False


class KillFilter(CommandFilter):
    """Specific filter for the kill calls.
       1st argument is the user to run /bin/kill under
       2nd argument is the location of the affected executable
       Subsequent arguments list the accepted signals (if any)

       This filter relies on /proc to accurately determine affected
       executable, so it will only work on procfs-capable systems (not OSX).
    """

    def __init__(self, *args):
        super(KillFilter, self).__init__("/bin/kill", *args)

    def match(self, userargs):
        if userargs[0] != "kill":
            return False
        args = list(userargs)
        if len(args) == 3:
            # this means we're asking for a specific signal
            signal = args.pop(1)
            if signal not in self.args[1:]:
                # Requested signal not in accepted list
                return False
        else:
            if len(args) != 2:
                # Incorrect number of arguments
                return False
            if len(self.args) > 1:
                # No signal requested, but filter requires specific signal
                return False

        try:
            command = os.readlink("/proc/%d/exe" % int(args[1]))
            # NOTE(dprince): /proc/PID/exe may have ' (deleted)' on
            # the end if an executable is updated or deleted
            if command.endswith(" (deleted)"):
                command = command[:command.rindex(" ")]
            if command != self.args[0]:
                # Affected executable doesn't match
                return False
        except (ValueError, OSError):
            # Incorrect PID
            return False
        return True


class ReadFileFilter(CommandFilter):
    """Specific filter for the utils.read_file_as_root call"""

    def __init__(self, file_path, *args):
        self.file_path = file_path
        super(ReadFileFilter, self).__init__("/bin/cat", "root", *args)

    def match(self, userargs):
        if userargs[0] != 'cat':
            return False
        if userargs[1] != self.file_path:
            return False
        if len(userargs) != 2:
            return False
        return True


class IpFilter(CommandFilter):
    """Specific filter for the ip utility to that does not match exec."""

    def match(self, userargs):
        if userargs[0] == 'ip':
            if userargs[1] == 'netns':
                if userargs[2] in ('list', 'add', 'delete'):
                    return True
                else:
                    return False
            else:
                return True


class IpNetnsExecFilter(ExecCommandFilter):
    """Specific filter for the ip utility to that does match exec."""
    def match(self, userargs):
        if userargs[:3] == ['ip', 'netns', 'exec']:
            return True
        else:
            return False

    def exec_args(self, userargs):
        args = userargs[4:]
        if args:
            args[0] = os.path.basename(args[0])
        return args
