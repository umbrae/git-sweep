from mock import patch
from nose.plugins.attrib import attr

from gitsweep.tests.testcases import CommandTestCase


class TestHelpMenu(CommandTestCase):

    """
    Command-line tool can show the help menu.

    """
    def test_help(self):
        """
        If no arguments are given the help menu is displayed.
        """
        (retcode, stdout, stderr) = self.gscommand('git-sweep -h')

        self.assertResults('''
            usage: git-sweep [-h] {preview,cleanup} ...

            Clean up your Git repository remote branches

            optional arguments:
              -h, --help         show this help message and exit

            action:
              Preview changes or perform clean up

              {preview,cleanup}
                preview          Preview the branches that will be deleted
                cleanup          Delete merged branches from the remote
            ''', stdout)

    def test_fetch(self):
        """
        Will fetch if told not to.
        """
        (retcode, stdout, stderr) = self.gscommand('git-sweep preview')

        self.assertResults('''
            Fetching from the remote
            No remote branches are available for cleaning up
            ''', stdout)

    def test_no_fetch(self):
        """
        Will not fetch if told not to.
        """
        (retcode, stdout, stderr) = self.gscommand(
            'git-sweep preview --nofetch')

        self.assertResults('''
            No remote branches are available for cleaning up
            ''', stdout)

    def test_will_preview(self):
        """
        Will preview the proposed deletes.
        """
        for i in range(1, 6):
            self.command('git checkout -b branch{0}'.format(i))
            self.make_commit()
            self.command('git checkout master')
            self.make_commit()
            self.command('git merge branch{0}'.format(i))

        (retcode, stdout, stderr) = self.gscommand('git-sweep preview')

        self.assertResults('''
            Fetching from the remote
            These branches have been merged into master:

              branch1
              branch2
              branch3
              branch4
              branch5

            To delete them, run again with `git-sweep cleanup`
            ''', stdout)

    def test_will_preview_none_found(self):
        """
        Will preview the proposed deletes.
        """
        for i in range(1, 6):
            self.command('git checkout -b branch{0}'.format(i))
            self.make_commit()
            self.command('git checkout master')

        (retcode, stdout, stderr) = self.gscommand('git-sweep preview')

        self.assertResults('''
            Fetching from the remote
            No remote branches are available for cleaning up
            ''', stdout)

    def test_will_cleanup(self):
        """
        Will preview the proposed deletes.
        """
        for i in range(1, 6):
            self.command('git checkout -b branch{0}'.format(i))
            self.make_commit()
            self.command('git checkout master')
            self.make_commit()
            self.command('git merge branch{0}'.format(i))

        with patch('gitsweep.cli.raw_input', create=True) as ri:
            ri.return_value = 'y'
            (retcode, stdout, stderr) = self.gscommand('git-sweep cleanup')

        self.assertResults('''
            Fetching from the remote
            These branches have been merged into master:

              branch1
              branch2
              branch3
              branch4
              branch5

            Delete these branches? (y/n) 
              deleting branch1 (done)
              deleting branch2 (done)
              deleting branch3 (done)
              deleting branch4 (done)
              deleting branch5 (done)

            All done!

            Tell everyone to run `git fetch --prune` to sync with this remote.
            (you don't have to, your's is synced)
            ''', stdout)

    def test_will_abort_cleanup(self):
        """
        Will preview the proposed deletes.
        """
        for i in range(1, 6):
            self.command('git checkout -b branch{0}'.format(i))
            self.make_commit()
            self.command('git checkout master')
            self.make_commit()
            self.command('git merge branch{0}'.format(i))

        with patch('gitsweep.cli.raw_input', create=True) as ri:
            ri.return_value = 'n'
            (retcode, stdout, stderr) = self.gscommand('git-sweep cleanup')

        self.assertResults('''
            Fetching from the remote
            These branches have been merged into master:

              branch1
              branch2
              branch3
              branch4
              branch5

            Delete these branches? (y/n) 
            OK, aborting.
            ''', stdout)

    @attr('focus')
    def test_will_skip_certain_branches(self):
        """
        Can be forced to skip certain branches.
        """
        for i in range(1, 6):
            self.command('git checkout -b branch{0}'.format(i))
            self.make_commit()
            self.command('git checkout master')
            self.make_commit()
            self.command('git merge branch{0}'.format(i))

        (retcode, stdout, stderr) = self.gscommand(
            'git-sweep preview --skip=branch1,branch2')

        self.assertResults('''
            Fetching from the remote
            These branches have been merged into master:

              branch3
              branch4
              branch5

            To delete them, run again with `git-sweep cleanup`
            ''', stdout)
