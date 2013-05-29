# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2011 OpenStack LLC.
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

"""
Utilities with minimum-depends for use in setup.py
"""

import os
import re
import subprocess

from setuptools.command import sdist


def parse_mailmap(mailmap='.mailmap'):
    mapping = {}
    if os.path.exists(mailmap):
        fp = open(mailmap, 'r')
        for l in fp:
            l = l.strip()
            if not l.startswith('#') and ' ' in l:
                canonical_email, alias = [x for x in l.split(' ')
                                          if x.startswith('<')]
                mapping[alias] = canonical_email
    return mapping


def canonicalize_emails(changelog, mapping):
    """Takes in a string and an email alias mapping and replaces all
       instances of the aliases in the string with their real email.
    """
    for alias, email in mapping.iteritems():
        changelog = changelog.replace(alias, email)
    return changelog


# Get requirements from the first file that exists
def get_reqs_from_files(requirements_files):
    for requirements_file in requirements_files:
        if os.path.exists(requirements_file):
            return open(requirements_file, 'r').read().split('\n')
    return []


def parse_requirements(requirements_files=['requirements.txt',
                                           'tools/pip-requires']):
    requirements = []
    for line in get_reqs_from_files(requirements_files):
        # For the requirements list, we need to inject only the portion
        # after egg= so that distutils knows the package it's looking for
        # such as:
        # -e git://github.com/openstack/nova/master#egg=nova
        if re.match(r'\s*-e\s+', line):
            requirements.append(re.sub(r'\s*-e\s+.*#egg=(.*)$', r'\1',
                                line))
        # such as:
        # http://github.com/openstack/nova/zipball/master#egg=nova
        elif re.match(r'\s*https?:', line):
            requirements.append(re.sub(r'\s*https?:.*#egg=(.*)$', r'\1',
                                line))
        # -f lines are for index locations, and don't get used here
        elif re.match(r'\s*-f\s+', line):
            pass
        else:
            requirements.append(line)

    return requirements


def parse_dependency_links(requirements_files=['requirements.txt',
                                               'tools/pip-requires']):
    dependency_links = []
    # dependency_links inject alternate locations to find packages listed
    # in requirements
    for line in get_reqs_from_files(requirements_files):
        # skip comments and blank lines
        if re.match(r'(\s*#)|(\s*$)', line):
            continue
        # lines with -e or -f need the whole line, minus the flag
        if re.match(r'\s*-[ef]\s+', line):
            dependency_links.append(re.sub(r'\s*-[ef]\s+', '', line))
        # lines that are only urls can go in unmolested
        elif re.match(r'\s*https?:', line):
            dependency_links.append(line)
    return dependency_links


def write_requirements():
    venv = os.environ.get('VIRTUAL_ENV', None)
    if venv is not None:
        with open("requirements.txt", "w") as req_file:
            output = subprocess.Popen(["pip", "-E", venv, "freeze", "-l"],
                                      stdout=subprocess.PIPE)
            requirements = output.communicate()[0].strip()
            req_file.write(requirements)


def _run_shell_command(cmd):
    output = subprocess.Popen(["/bin/sh", "-c", cmd],
                              stdout=subprocess.PIPE)
    return output.communicate()[0].strip()


def write_vcsversion(location):
    """Produce a vcsversion dict that mimics the old one produced by bzr.
    """
    if os.path.isdir('.git'):
        branch_nick_cmd = 'git branch | grep -Ei "\* (.*)" | cut -f2 -d" "'
        branch_nick = _run_shell_command(branch_nick_cmd)
        revid_cmd = "git rev-parse HEAD"
        revid = _run_shell_command(revid_cmd).split()[0]
        revno_cmd = "git log --oneline | wc -l"
        revno = _run_shell_command(revno_cmd)
        with open(location, 'w') as version_file:
            version_file.write("""
# This file is automatically generated by setup.py, So don't edit it. :)
version_info = {
    'branch_nick': '%s',
    'revision_id': '%s',
    'revno': %s
}
""" % (branch_nick, revid, revno))


def write_git_changelog():
    """Write a changelog based on the git changelog."""
    if os.path.isdir('.git'):
        git_log_cmd = 'git log --stat'
        changelog = _run_shell_command(git_log_cmd)
        mailmap = parse_mailmap()
        with open("ChangeLog", "w") as changelog_file:
            changelog_file.write(canonicalize_emails(changelog, mailmap))


def generate_authors():
    """Create AUTHORS file using git commits."""
    jenkins_email = 'jenkins@review.openstack.org'
    old_authors = 'AUTHORS.in'
    new_authors = 'AUTHORS'
    if os.path.isdir('.git'):
        # don't include jenkins email address in AUTHORS file
        git_log_cmd = ("git log --format='%aN <%aE>' | sort -u | "
                       "grep -v " + jenkins_email)
        changelog = _run_shell_command(git_log_cmd)
        mailmap = parse_mailmap()
        with open(new_authors, 'w') as new_authors_fh:
            new_authors_fh.write(canonicalize_emails(changelog, mailmap))
            if os.path.exists(old_authors):
                with open(old_authors, "r") as old_authors_fh:
                    new_authors_fh.write('\n' + old_authors_fh.read())


def get_cmdclass():
    """Return dict of commands to run from setup.py."""

    cmdclass = dict()

    class LocalSDist(sdist.sdist):
        """Builds the ChangeLog and Authors files from VC first."""

        def run(self):
            write_git_changelog()
            generate_authors()
            # sdist.sdist is an old style class, can't use super()
            sdist.sdist.run(self)

    cmdclass['sdist'] = LocalSDist

    # If Sphinx is installed on the box running setup.py,
    # enable setup.py to build the documentation, otherwise,
    # just ignore it
    try:
        from sphinx.setup_command import BuildDoc

        class LocalBuildDoc(BuildDoc):
            def run(self):
                for builder in ['html', 'man']:
                    self.builder = builder
                    self.finalize_options()
                    BuildDoc.run(self)
        cmdclass['build_sphinx'] = LocalBuildDoc
    except ImportError:
        pass

    return cmdclass