'''
COPYRIGHT Ericsson 2019
The copyright to the computer program(s) herein is the property of
Ericsson Inc. The programs may be used and/or copied only with written
permission from Ericsson Inc. or in accordance with the terms and
conditions stipulated in the agreement/contract under which the
program(s) have been supplied.

@since:     February 2014
@author:    Maria Varley, Maurizio Senno
@summary:   STORY LITPCDS-1708
                As an Administrator/Installer I want to be able to
                configure yum repositories,
                so I can install new software or upgrade existing packages

            BUG LITPCDS-9745
                Yum plugin will no longer attempt to remove any yum repo
                configuration file

            Code re-factored on June 2015 to remove test dependencies
            from Package plugin
'''

from litp_generic_test import GenericTest, attr
from redhat_cmd_utils import RHCmdUtils
from litp_cli_utils import CLIUtils
import test_constants
import os
import time


class Story1708(GenericTest):
    '''
    As an Administrator/Installer I want to be able to
    configure yum repositories,
    so I can install new software or upgrade existing packages
    '''

    def setUp(self):
        """
        Description:
            Runs before every single test
        Actions:
            1. Call the super class setup method
            2. Set up variables used in the tests
        Results:
            The super class prints out diagnostics and variables
            common to all tests are available.
        """
        # 1. Call super class setup
        super(Story1708, self).setUp()
        self.rhcmd = RHCmdUtils()
        self.cli = CLIUtils()
        self.ms1 = self.get_management_node_filename()
        self.mn1, self.mn2 = self.get_managed_node_filenames()[:2]

        # test attributes
        self.sys_repo1 = {}
        self.sys_repo2 = {}
        self.sys_repos = []

        self.sw_repo1 = {}
        self.sw_repo2 = {}
        self.sw_repos = []

        self.ms_repo1 = {}
        self.ms_repo2 = {}
        self.ms_repos = []

        self.mn1_repo1 = {}
        self.mn1_repo2 = {}
        self.mn1_repos = []

        self.step = ''

    def tearDown(self):
        """
        Description:
            Runs after every single test
        Actions:
            1. Perform Test Cleanup
            2. Call superclass tear down
        Results:
            Items used in the test are cleaned up and the
        """
        super(Story1708, self).tearDown()

    def _log_step(self, msg):
        """
        Description:
            Log step description and update step count variable
        Args:
            msg (str): Test to be logged
        """
        self.step = msg
        self.log('info', msg)

    def _initialize_litp_items_definition(self,
                                          test_id,
                                          sw_collection_sw_item_path=None,
                                          ms_collection_sw_item_path=None,
                                          mn1_collection_sw_item_path=None,
                                          wait_for_puppet=False):
        """
        Description:
            Initialize dictionaries that represent litp items to be used
            during test
        Args:
            test_id (str): Test identifier as story<number>_tc<number>
        """
        self.sys_repo1.clear()
        self.sys_repo1['container'] = self.sys_repos
        self.sys_repo1['name'] = 'sys-repo-1'
        self.sys_repo1['path'] = ('{0}{1}-{2}'
                                  .format(test_constants.PARENT_PKG_REPO_DIR,
                                          test_id, self.sys_repo1['name']))
        self.sys_repo1['rpm'] = 'ms_pkg_story17081-1.0-1.noarch.rpm'
        self.sys_repo1['rpm_upgrade'] = 'ms_pkg_story17081-5.0-5.noarch.rpm'
        self.sys_repo1['rpm_src'] = self.sys_repo1['rpm']
        self.sys_repo1['rpm_src_upgrade'] = self.sys_repo1['rpm_upgrade']
        self.sys_repo1['pkg'] = (self.sys_repo1['rpm'].split('-')[0])
        self.sys_repo1['pkg_rel_ver'] = (self.sys_repo1['rpm']
                                         .replace('.noarch', '')
                                         .replace('.rpm', ''))
        self.del_file_after_run(self.ms1,
                                self.sys_repo1['path'],
                                wait_for_puppet=wait_for_puppet)

        self.sys_repo2.clear()
        self.sys_repo2['container'] = self.sys_repos
        self.sys_repo2['name'] = 'sys-repo-2'
        self.sys_repo2['path'] = ('{0}{1}-{2}'
                                  .format(test_constants.PARENT_PKG_REPO_DIR,
                                          test_id, self.sys_repo2['name']))
        self.sys_repo2['rpm'] = 'ms_pkg_story17082-1.0-1.noarch.rpm'
        self.sys_repo2['rpm_upgrade'] = 'ms_pkg_story17082-5.0-5.noarch.rpm'
        self.sys_repo2['rpm_src'] = self.sys_repo2['rpm']
        self.sys_repo2['rpm_src_upgrade'] = self.sys_repo1['rpm_upgrade']
        self.sys_repo2['pkg'] = (self.sys_repo2['rpm'].split('-')[0])
        self.sys_repo2['pkg_rel_ver'] = (self.sys_repo2['rpm']
                                         .replace('.noarch', '')
                                         .replace('.rpm', ''))
        self.del_file_after_run(self.ms1,
                                self.sys_repo2['path'],
                                wait_for_puppet=wait_for_puppet)

        self.sw_repo1.clear()
        self.sw_repo1['container'] = self.sw_repos
        self.sw_repo1['name'] = '{0}-litp-repoA'.format(test_id)
        self.sw_repo1['name_update'] = '{0}_new_base_repo_1'.format(test_id)
        self.sw_repo1['path'] = ('{0}/{1}-sw-repo-1'
                               .format(sw_collection_sw_item_path, test_id))
        self.sw_repo1['node'] = self.ms1
        self.sw_repo1['item_type'] = 'yum-repository'
        self.sw_repo1['sys_repo'] = self.sys_repo1
        self.sw_repo1['ms_url_path'] = ('/{0}'
            .format(self.sw_repo1['sys_repo']['path'].split('/')[-1]))
        self.sw_repo1['ms_url_path_update'] = ('/{0}-new'
            .format(self.sw_repo1['sys_repo']['path'].split('/')[-1]))
        self.sw_repo1['base_url'] = 'http://example.com/yum-repo1'
        self.sw_repo1['config_file'] = ('{0}/{1}.repo'
                    .format(test_constants.YUM_CONFIG_FILES_DIR,
                            self.sw_repo1['name']))

        self.sw_repo2.clear()
        self.sw_repo2['container'] = self.sw_repos
        self.sw_repo2['name'] = '{0}-litp-repoB'.format(test_id)
        self.sw_repo2['name_update'] = '{0}_new_base_repo_2'.format(test_id)
        self.sw_repo2['path'] = ('{0}/{1}-sw-repo-2'
                               .format(sw_collection_sw_item_path, test_id))
        self.sw_repo2['node'] = self.ms1
        self.sw_repo2['item_type'] = 'yum-repository'
        self.sw_repo2['sys_repo'] = self.sys_repo2
        self.sw_repo2['ms_url_path'] = ('/{0}'
            .format(self.sw_repo2['sys_repo']['path'].split('/')[-1]))
        self.sw_repo2['ms_url_path_update'] = ('/{0}-new'
            .format(self.sw_repo2['sys_repo']['path'].split('/')[-1]))
        self.sw_repo2['base_url'] = 'http://example.com/yum-repo2'
        self.sw_repo2['config_file'] = ('{0}/{1}.repo'
                    .format(test_constants.YUM_CONFIG_FILES_DIR,
                            self.sw_repo2['name']))

        self.ms_repo1.clear()
        self.ms_repo1['container'] = self.ms_repos
        self.ms_repo1['node'] = self.ms1
        self.ms_repo1['path'] = ('{0}/{1}-ms-repo-1'
                        .format(ms_collection_sw_item_path, test_id))
        self.ms_repo1['item_type'] = 'reference-to-yum-repository'

        self.ms_repo2.clear()
        self.ms_repo2['container'] = self.ms_repos
        self.ms_repo2['node'] = self.ms1
        self.ms_repo2['path'] = ('{0}/{1}-ms-repo-2'
                        .format(ms_collection_sw_item_path, test_id))
        self.ms_repo2['item_type'] = 'reference-to-yum-repository'

        self.mn1_repo1.clear()
        self.mn1_repo1['container'] = self.mn1_repos
        self.mn1_repo1['node'] = self.mn1
        self.mn1_repo1['path'] = ('{0}/{1}-mn1-repo-1'
                        .format(mn1_collection_sw_item_path, test_id))
        self.mn1_repo1['item_type'] = 'reference-to-yum-repository'

        self.mn1_repo2.clear()
        self.mn1_repo2['container'] = self.mn1_repos
        self.mn1_repo2['node'] = self.mn1
        self.mn1_repo2['path'] = ('{0}/{1}-mn1-repo-2'
                        .format(mn1_collection_sw_item_path, test_id))
        self.mn1_repo2['item_type'] = 'reference-to-yum-repository'

    def _clone_repo(self, repo, parent=None, wait_for_puppet=False):
        """
        Description:
            Obtain a copy of the required repo type and add reference
            to appropriate list
        Args:
            repo (dict): repo to clone
            parent (dict): The yum repo dict from which to inherit
            wait_for_puppet (bool): Whether to wait for puppet cycle during
                                    clean up at end of test
        """
        clone = repo.copy()
        if parent != None:
            clone['parent'] = parent
            self.del_file_after_run(clone['node'],
                                    clone['parent']['config_file'],
                                    wait_for_puppet=wait_for_puppet)
        repo['container'].append(clone)
        return clone

    def _run_cmd_and_assert_success(self,
                                    node,
                                    cmd,
                                    expected_rc=0,
                                    su_root=False,
                                    execute_timeout=0.25):
        """
        Description:
            Run given linux command and check it completes successfully
        Args:
            node (str) : the node to run the command
            cmd (str) : Command string
            su_root (bool) : Set to True to run command as root
        """
        out, err, rc = self.run_command(node, cmd, su_root=su_root,
                                            execute_timeout=execute_timeout)
        self.assertEqual([], err,
            'Command "{0}" on node "{1}" failed with error: \n{2}'
            .format(cmd, node, '\n'.join(err)))
        self.assertEqual(rc, expected_rc,
            'Command "{0}" on node "{1}" exited with return code "{2}"'
            .format(cmd, node, rc))
        return out

    def _assert_yum_repo_config_file_content(self,
                                    node, config_file, expected_contents):
        """
        Description:
            Verify that yum configuration file content is correct
        Args:
            node (str) : The node where the config file resides
            config_file (str): Yum repo config file path
            expected_contents (dict): dictionary of expected values
        """
        self.assertTrue(
            self.remote_path_exists(node, config_file),
            'Yum repo configuration file {0} NOT found on node {1}'
            .format(config_file, node))

        file_contents = self.get_file_contents(node,
                                               config_file,
                                               su_root=True)[1:]
        error = False
        summary = []

        if len(file_contents) > len(expected_contents['ensure_found']):
            error = True

        for key, val in expected_contents['ensure_found'].iteritems():
            expected_line = '{0}={1}'.format(key, val)
            if self.is_text_in_list(key, file_contents) == False:
                result = 'ERROR - Missing field'
                error = True
            elif self.is_text_in_list(expected_line, file_contents) == False:
                result = 'ERROR - Incorrect value'
                error = True
            else:
                result = 'OK'
            msg = '{0:<70} [{1}]'.format(expected_line, result)
            self.log('info', msg)
            summary.append(msg)

        for key, val in expected_contents['ensure_not_found'].iteritems():
            if val == None:
                expected_line = '{0}'.format(key)
            else:
                expected_line = '{0}={1}'.format(key, val)
            for each_line in file_contents:
                if expected_line in each_line:
                    msg = '{0:<70} [{1}]'.format(each_line, 'EXTRA')
                    self.log('info', msg)
                    summary.append(msg)
                    error = True

        self.log('info', '\n' * 3)

        err_msg = ''
        if error:
            err_msg = 'STEP: {0}\nConfiguration file "{1}" on "{2}" ' \
                      'has invalid content:\n {3}'

        self.assertFalse(error,
                         err_msg.format(self.step,
                                        config_file,
                                        node,
                                        '\n '.join(summary)))

    def _install_package(self, node, pkg):
        """
        Description:
            Install given package using linux "yum" utility
        Args:
            node (str) : the node where the package is installed
            pkg (str): the name of the package to install
        """
        self.assertFalse(self.check_pkgs_installed(node, [pkg]),
            'Package "{0}" already installed on {1}'.format(pkg, node))

        cmd = self.rhc.get_yum_install_cmd([pkg])
        _, err, _ = self.run_command(node, cmd, su_root=True)
        self.assertEqual([], err,
                'Command "{0}" failed with error \n{1}'
                .format(cmd, '\n'.join(err)))

        self.assertTrue(self.check_pkgs_installed(node, [pkg]),
            'Package "{0}" failed to install on node "{1}"'
            .format(pkg, node))

    def _uninstall_package(self, node, pkg):
        """
        Description:
            Remove package using linux "yum" utility
        Args:
            node (str) : the node where the package is installed
            sys_repo (str): dictionary of sys repo data
        """
        if self.check_pkgs_installed(node, [pkg]) == True:
            cmd = self.rhc.get_yum_remove_cmd([pkg])
            _, err, _ = self.run_command(node, cmd, su_root=True)
            self.assertEqual([], err,
                'Command "{0}" on node "{1}" failed with error \n{2}'
                .format(cmd, node, '\n'.join(err)))
            self.assertFalse(self.check_pkgs_installed(node, [pkg]),
                'Failed to remove package "{0}" on node {1}'
                .format(pkg, node))

    def _create_system_repo(self, repo_dir):
        """
        Description:
            Creates a test repo to be used for these tests using "create_repo"
            utility
        Args:
            repo_dir (str): folder where yum repo is to be created
        """
        cmd = self.rhcmd.get_createrepo_cmd(repo_dir, update=False)
        self.run_command(self.ms1, cmd, su_root=True, default_asserts=True)
        self._check_yum_repo_is_present(repo_dir)

    def _copy_rpm_to_ms(self, dst_path, dst_rpm, src_rpm):
        """
        Description:
            Copy package to yum repository directory on MS
            Using md5 checksum to verify that rpm was successfully copied
        Args:
            dst_path (str): path to folder where rpm is to be copied to
            dst_rpm (str): name of the destination rpm file
            src_path (str): the location where the RPM is to be copied from
        """
        local_path = ('{0}/story1708_rpms/{1}'
                     .format(os.path.dirname(os.path.abspath(__file__)),
                                             src_rpm))
        ms_path = '{0}/{1}'.format(dst_path, dst_rpm)

        local_md5 = self.run_command_local('/usr/bin/md5sum {0}'
                                           .format(local_path))[0]

        expected_md5 = '{0}  {1}'.format(local_md5[0].split()[0], ms_path)

        self.assertTrue(self.copy_file_to(self.ms1,
                                          local_path,
                                          ms_path,
                                          root_copy=True))

        self.assertTrue(self.wait_for_cmd(self.ms1,
                                          'md5sum {0}'.format(ms_path),
                                          expected_rc=0,
                                          expected_stdout=expected_md5,
                                          timeout_mins=1))

        self.assertTrue(self.remote_path_exists(self.ms1, ms_path),
            ' rpm package <{0}> not found'.format(ms_path))

    def _check_yum_repo_is_present(self, repo_path):
        """
        Description:
            Check that file /repodata/repomd.xml file exist under repo
            folder on MS
        Args:
            repo_path (str): folder where the yum repo resides
        """
        repmod_path = repo_path + '/repodata/repomd.xml'
        self.assertTrue(self.remote_path_exists(self.ms1, repmod_path),
            '<{0}> not found'.format(repmod_path))

    def _execute_create_cmd_and_verify_msg(self,
            node, path, item_type, rule_set, args=''):
        """
        Description:
            Function that executes "cli_create_cmd" and
            verifies the error messages.
        Args:
            rule_set:   (dict) Dictionary containing rule sets
                          necessary for verifying error messages
            path: (str) The path to create on LITP model
            item_type : (str) The type of the item to create
        """
        fails = []
        error = False
        self.log("info", "Negative Validation test at 'create': {0}"
                         .format(rule_set['description']))

        cmd = self.cli.get_create_cmd(path,
                                      item_type,
                                      rule_set['param'],
                                      args=args)
        _, stderr, _ = self.run_command(node, cmd)

        if stderr == []:
            fails.append('{0}'.format(rule_set['description']))
            fails.append('Create cmd did NOT fail')
            error = True
        else:
            for result in rule_set['results']:
                msg_found = self._is_cli_error_message_found(stderr,
                                                             result)
                if msg_found == False:
                    fails.append('{0}'.format(rule_set['description']))
                    error = True
                    break

        out = self.find(node, path, item_type, assert_not_empty=False)
        if len(out) == 1:
            self.execute_cli_remove_cmd(node, path)
            if error == True:
                fails.append('Item was created despite of validation error')
            else:
                fails.append('Create cmd was successful and item was created')

        if len(fails) != 0:
            fails.append('EXPECTED msg:')
            for result in rule_set['results']:
                path = result.get('path')
                if path != None:
                    fails.append(' {0}'.format(path))
                fails.append(' {0}'.format(result['msg']))
            fails.append('ACTUAL msg :')
            for line in stderr:
                fails.append(' {0}'.format(line))

        return fails

    def _execute_update_cmd_and_verify_error_msg(self, node, path, rule_set):
        """
        Description:
            Function that executes "update" command and
            verifies results.
        Args:
            node: (str) The node to run the litp update command on
            rule_set:   (dict) Dictionary containing rule sets
                          necessary for verifying error messages
            path: (str) The path to create on LITP model
            expect_pass: (bool) Vhether the command should fail or pass
        """
        fails = []
        error = False
        self.log("info", "Negative Validation test at 'update': {0}"
                         .format(rule_set['description']))

        before_update = self.get_props_from_url(self.ms1, path)

        action_delete = rule_set.get('action_delete', False)
        args = rule_set.get('args', '')

        cmd = self.cli.get_update_cmd(path,
                                      rule_set['param'],
                                      args,
                                      action_delete=action_delete)
        _, stderr, _ = self.run_command(node, cmd)

        after_update = self.get_props_from_url(self.ms1, path)

        if stderr == []:
            fails.append('{0}'.format(rule_set['description']))
            fails.append('"update" cmd did NOT fail')
        else:
            for result in rule_set['results']:
                msg_found = self._is_cli_error_message_found(stderr,
                                                             result)
                if msg_found == False:
                    fails.append('{0}'.format(rule_set['description']))
                    error = True
                    break

        if before_update != after_update:
            if error == True:
                fails.append('Item was updated despite of validation error')
            else:
                fails.append('Updates were made to the litp items')

        if len(fails) != 0:
            fails.append('EXPECTED msg:')
            for result in rule_set['results']:
                path = result.get('path')
                if path != None:
                    fails.append(' {0}'.format(path))
                fails.append(' {0}'.format(result['msg']))
            fails.append('ACTUAL msg :')
            for line in stderr:
                fails.append(' {0}'.format(line))
            fails.append(' ')

        return fails

    def _execute_createplan_cmd_and_verify_msg(self, node, rule_set):
        """
        Description:
            Function that executes the "createplan_cmd"
            and verifies the error messages
        Args:
            node (str): the node where litp command is to be run
            rule_set (dict): Dictionary containing rule set
                             necessary for verifying error messages
        """
        fails = []
        self.log("info", "Negative validation test at 'create_plan' : {0}"
                         .format(rule_set['description']))

        cmd = self.cli.get_create_plan_cmd()
        _, stderr, _ = self.run_command(node, cmd)

        if stderr == []:
            fails.append(format(rule_set['description']))
            fails.append('"create_plan" did NOT fail')
        else:
            for result in rule_set['results']:
                msg_found = self._is_cli_error_message_found(stderr,
                                                             result)
                if msg_found == False:
                    fails.append(rule_set['description'])
                    break

        if len(fails) != 0:
            fails.append('EXPECTED msg:')
            for result in rule_set['results']:
                path = result.get('path')
                if path != None:
                    fails.append(' {0}'.format(path))
                fails.append(' {0}'.format(result['msg']))
            fails.append('ACTUAL msg :')
            for line in stderr:
                fails.append(' {0}'.format(line))

        return fails

    @staticmethod
    def _is_cli_error_message_found(err_list, result):
        """
        Description:
            Check that give path and message pair is found in error messages
        Args:
            err_list (list): list of error messages and paths
            result (dict):  dictionary of error data
        """
        found = False
        if result.get('path') != None:
            for i in xrange(len(err_list) - 1):
                if err_list[i] == result.get('path') and \
                    err_list[i + 1] == result['msg']:
                    found = True
                    break
        else:
            for line in err_list:
                if line == result['msg']:
                    found = True
                    break
        return found

    def _assert_cli_error_message_not_found(self, err_list, result):
        """
        Description:
            Check that give path and message pair is not found in
            error messages
        Args:
            err_list (list): list of error messages and paths
            result (dict):  dictionary of error data
        """
        self.assertTrue('msg' in result,
            'Required expected error message missing in "result"')

        if result.get('ensure_not_found') == True:
            if result.get('path') != None:
                path_assert_msg = '\n{0}'.format(result['path'])
                for i in xrange(len(err_list) - 1):
                    if err_list[i] == result.get('path') and \
                       err_list[i + 1] == result['msg']:
                        found = True
                        break

            else:
                path_assert_msg = ''
                for line in err_list:
                    if line == result['msg']:
                        found = True
                        break

            assert_msg = (
            '\nExtra error message:{0}\n{1}\nfound in:\n{2}'
            .format(path_assert_msg, result['msg'], '\n'.join(err_list)))
            self.assertFalse(found, assert_msg)

    def _create_run_and_wait_for_plan(self,
                                      state,
                                      msg,
                                      timeout=20,
                                      create_plan=True):
        """
        Description:
            Create and run plan and wait for specified plan state
        Args:
            msg (str): Message to be posted in case expected state is not
                       reached
            state (int): The expected state of the plan
            timeout (int): Max allowed time for given plan state to be reached
            create_plan: if False does not execute create_plan,
                         if True executes create_plan (default)
        """
        if create_plan:
            self.execute_cli_createplan_cmd(self.ms1)
        self.execute_cli_runplan_cmd(self.ms1)
        result = self.wait_for_plan_state(self.ms1,
                                          state,
                                          timeout_mins=timeout)
        if self.step != '':
            msg = '{0}\n{1}'.format(self.step, msg)
        self.assertTrue(result, msg)

    def _remove_installed_packages_and_all_yum_repo_items(self):
        """
        Description:
            Performs cleanup after test with the appropriate step sequence
            to ensure system is reverted back to initial state
        """
        self._log_step(
        'FINALLY 1. Remove all installed packages')

        ms1_pkgs = set(
            [x['parent']['sys_repo']['pkg'] for x in self.ms_repos])
        mn1_pkgs = set(
            [x['parent']['sys_repo']['pkg'] for x in self.mn1_repos])

        self.log('info',
                 'Pakages found on {0}: {1}'
                 .format(self.ms1, ', '.join(ms1_pkgs)))
        self.log('info',
                 'Pakages found on {0}: {1}'
                 .format(self.mn1, ', '.join(mn1_pkgs)))

        for each_pkg in ms1_pkgs:
            if self.check_pkgs_installed(self.ms1, [each_pkg]) == True:
                cmd = self.rhc.get_yum_remove_cmd([each_pkg])
                self.run_command(self.ms1, cmd, su_root=True)

        for each_pkg in mn1_pkgs:
            if self.check_pkgs_installed(self.mn1, [each_pkg]) == True:
                cmd = self.rhc.get_yum_remove_cmd([each_pkg])
                self.run_command(self.mn1, cmd, su_root=True)

    def _assert_yum_repos_dir_does_not_contain_story_files(self, nodes):
        """
        Description:
            Check that yum configuration files folder does not contain
            files generated during the testcase execution
        Args:
            nodes (list): List of nodes to check
        """
        contents = []
        found = False
        for each_node in nodes:
            contents.append('Node: {0}'.format(each_node))
            content = self.list_dir_contents(
                each_node,
                test_constants.YUM_CONFIG_FILES_DIR,
                su_root=True,
                grep_args='story')
            if content == []:
                contents.append(' - No story config files found')
            else:
                contents.extend(content)
                found = True

        self.assertFalse(found,
            '\nStory yum config files found\n{0}'
            .format('\n'.join(contents)))

    def _verify_clean_metadata_task(self, node, repo, expect_task=True):
        """
        Description:
            If expect_positive verifies that the cleanup task comes after the
            update task and is in the next phase,
            if not expect_positive verifies that there is no cleanup task after
            the update task
        Args:
            node (str): node to check the update/clean tasks
            repo (str): modeled repo where to check the update/clean tasks
            expect_task (boolean): whether the clean metadata tasks should
                                   be found or not
        """

        plan_output, _, _ = self.execute_cli_showplan_cmd(self.ms1)
        plan_dict = self.cli.parse_plan_output(plan_output)

        # find update task for node
        update_phase = -1
        expected_desc = 'Update yum repository "{0}" on node "{1}"'.format(
                repo, node)
        for phase in plan_dict.keys():
            for task in plan_dict[phase].keys():
                desc = " ".join(plan_dict[phase][task]['DESC'][1:])
                if desc == expected_desc:
                    update_phase = phase
                    break
            else:
                continue
            break

        #ensure update task has been found
        self.assertTrue(update_phase > 0)

        #look for cleanup task
        clean_metadata_found = False

        expected_desc = 'Clean metadata for yum repository "{0}"'\
                ' on node "{1}"'.format(repo, node)

        for phase in plan_dict.keys():
            for task in plan_dict[phase].keys():
                desc = "".join(plan_dict[phase][task]['DESC'][1:])

                if desc == expected_desc:
                    clean_metadata_found = True
                    self.assertTrue(update_phase < phase)
                    break
            if clean_metadata_found:
                break

        self.assertEqual(expect_task, clean_metadata_found)

    @attr('all', 'revert', 'story1708', 'story1708_tc01', 'cdb_priority1')
    def test_01_p_install_new_software(self):
        """
        @tms_id: litpcds_1708_tc01
        @tms_requirements_id: LITPCDS-1708
        @tms_title: Install SW from new yum-repository
        @tms_description: Verify that yum-repository can be created, inherited
            and package installed using linux "yum" utility. Also verify that
            yum-repository items can be removed from LITP model.
        @tms_test_steps:
            @step: 1. Find collection of software items on LITP model
            @result:  Collection of software items located
            @step: 2. Create yum-repository items to be used during test
            @result:  yum-repository items created
            @step: 3.1. Create directories that will become the system yum repo
            @result:  Directories created on MS and node1
            @step: 3.2. Copy an RPMs to the created system repo folder
            @result:  RPMs coppied to system repo folder on MS and node1
            @step: 3.3. Enable system repo using "create_repo" utility
            @result:  Repo is created on on MS and node1
            @step: 4. Create LITP source yum-repository items
            @result:  Yum-repository source items created
            @step: 5. Inherit LITP yum repository items into MS
            @result:  Yum-repository source items Inherit into MS
            @step: 6. Inherit LITP yum repository items into node1
            @result:  Yum-repository source items Inherit into node1
            @step: 7. Create and run plan and verify it completes successfully
            @result:  Create plan and run_plan completes successfully
            @step: 8. Check that yum repo config files are created successfully
            @result:  Yum repo config files are created successfully
            @step: 9. Install packages using linux "yum" utility on MS & node1
            @result:  Packages installed on MS and node1
            @step:10. Revert system to its initial state
            @result:  System to in pre test initial state
        @tms_test_precondition:NA
        @tms_execution_type: Automated
        """
        test_id = 'story1708-tc01'

        try:
            self._log_step(
            '1. Find collection of software items on LITP model')
            sw_collection_sw_item_path = self.find(
                node=self.ms1,
                path="/software",
                resource="collection-of-software-item")[0]

            ms_collection_sw_item_path = self.find(
                node=self.ms1,
                path="/ms",
                resource="ref-collection-of-software-item")[0]

            mn1_collection_sw_item_path = self.find(
                node=self.ms1,
                path=self.find(self.ms1, '/deployments', 'node')[0],
                resource="ref-collection-of-software-item")[0]

            self._log_step(
            '2. Define yum-repository items to be used during test')
            self._initialize_litp_items_definition(test_id,
                                                   sw_collection_sw_item_path,
                                                   ms_collection_sw_item_path,
                                                   mn1_collection_sw_item_path,
                                                   wait_for_puppet=False)

            self._clone_repo(self.sys_repo1)
            self._clone_repo(self.sys_repo2)

            sw_repo1 = self._clone_repo(self.sw_repo1)
            sw_repo2 = self._clone_repo(self.sw_repo2)

            self._clone_repo(self.ms_repo1, parent=sw_repo1)
            self._clone_repo(self.ms_repo2, parent=sw_repo2)

            self._clone_repo(self.mn1_repo1, parent=sw_repo1)
            self._clone_repo(self.mn1_repo2, parent=sw_repo2)

            self._log_step(
            '3. Enable system repositories on MS and node1')
            for i, each_repo in enumerate(self.sys_repos, 1):
                self._log_step(
                '3.0.-{0} Processing repo "{0}"'
                .format(i, each_repo['path']))
                msg = (
                '3.1.-{0} Create directories that will become the system '
                          'yum repo'.format(i))
                self._log_step(msg)
                cmd = "/bin/mkdir {0}".format(each_repo['path'])
                self._run_cmd_and_assert_success(self.ms1, cmd, su_root=True)

                self._log_step(
                '3.2.-{0} Copy an RPMs to the created system repo folder'
                .format(i))
                self._copy_rpm_to_ms(each_repo['path'],
                                     each_repo['rpm'],
                                     each_repo['rpm_src'])

                self._log_step(
                '3.3.-{0} Enable system repo using "create_repo" utility'
                .format(i))
                self._create_system_repo(each_repo['path'])

            self._log_step(
            '4. Create LITP source yum-repository items')
            for each_repo in self.sw_repos:
                props = ("name='{0}' ms_url_path='{1}'"
                         .format(each_repo['name'], each_repo['ms_url_path']))
                self.execute_cli_create_cmd(
                    self.ms1, each_repo['path'], each_repo['item_type'], props)

            self._log_step(
            '5. Inherit LITP yum-repository item into MS')
            for each_repo in self.ms_repos:
                self.execute_cli_inherit_cmd(
                    self.ms1, each_repo['path'], each_repo['parent']['path'])

            self._log_step(
            '6. Inherit LITP yum-repository item into node1')
            for each_repo in self.mn1_repos:
                self.execute_cli_inherit_cmd(
                    self.ms1, each_repo['path'], each_repo['parent']['path'])

            self._log_step(
            '7. Create and run plan and verify it completes successfully')
            self._create_run_and_wait_for_plan(test_constants.PLAN_COMPLETE,
                'Plan to install packages failed')

            self._log_step(
            '8. Check that yum repo config files are created successfully')
            for each_repo in self.ms_repos + self.mn1_repos:
                expected_contents = {}
                expected_contents['ensure_found'] = {
                    'name': each_repo['parent']['name'],
                    'baseurl': 'http://ms1{0}'
                               .format(each_repo['parent']['ms_url_path']),
                    'enabled': '1',
                    'gpgcheck': '0',
                    'metadata_expire': '0',
                    'skip_if_unavailable': '1'
                }
                expected_contents['ensure_not_found'] = {}
                self._assert_yum_repo_config_file_content(
                                            each_repo['node'],
                                            each_repo['parent']['config_file'],
                                            expected_contents)

            self._log_step(
            '9. Install packages using linux "yum" utility on MS and node1')
            for each_repo in self.ms_repos + self.mn1_repos:
                self._log_step(
                'Install package "{0}" on  "{1}"'
                .format(each_repo['parent']['sys_repo']['pkg'],
                        each_repo['node']))
                self._install_package(each_repo['node'],
                                      each_repo['parent']['sys_repo']['pkg'])
        finally:
            self._log_step(
            '10. Revert system to its initial state')
            self._remove_installed_packages_and_all_yum_repo_items()

    @attr('all', 'revert', 'story1708', 'story1708_tc02')
    def test_02_n_install_upgrade_pkg_failure(self):
        """
        @tms_id: litpcds_1708_tc02
        @tms_requirements_id: LITPCDS-1708
        @tms_title: install upgrade pkg failure
        @tms_description: Verify that LITP yum-repository items cannot be
            created if the system repository they point to does not exist and
            that packages can be installed after updating yum repo item to
            point to a running yum repository server.
        @tms_test_steps:
            @step: 1. Find collection of software items on LITP model
            @result:  Collection of software items and stored
            @step: 2. Define yum-repository items to be used during test
            @result:  yum-repository items Create
            @step: 3. Create a directory for system yum repository
            @result:  dir created
            @step: 4. Copy an RPM to the created system repo folder
            @result:  RPMs are in the created system repo folder
            @step: 5. Create system repo using "createrepo" utility
            @result:  repo created on node
            @step: 6. Create LITP source yum-repository item that points
                to a non existent system repo
            @result:  Yum-repository source items created
            @step: 7. Inherit LITP yum-repo item to MS
            @result:  Yum-repository source items Inherit into MS
            @step: 8. Create plan
            @result:  plan creation fails
            @step:10. Update yum-repository source "ms_url_path" so that it
                points to a valid sys repo LITP item
            @result:  ms_url_path updated
            @step:11. Create and run plan and verify it completes successfully
            @result:  Create and run plan completes successfully
            @step:12. Check that yum repo config file  has valid baseurl value
            @result:  Yum repo config file now has valid baseurl value
            @step:13. Install packages using linux "yum" utility on MS
            @result:  packages are installed
            @step:14. Revert system to its initial state
            @result:  System is returned to a pre test state
        @tms_test_precondition:NA
        @tms_execution_type: Automated
        """
        test_id = 'story1708-tc02'

        try:
            self._log_step(
            '1. Find collection of software items on LITP model')
            sw_collection_sw_item_path = self.find(
                node=self.ms1,
                path="/software",
                resource="collection-of-software-item")[0]

            ms_collection_sw_item_path = self.find(
                node=self.ms1,
                path="/ms",
                resource="ref-collection-of-software-item")[0]

            self._log_step(
            '2. Define yum-repository items to be used during test')
            self._initialize_litp_items_definition(test_id,
                                                   sw_collection_sw_item_path,
                                                   ms_collection_sw_item_path,
                                                   None,
                                                   wait_for_puppet=False)

            s_repo1 = self._clone_repo(self.sys_repo1)
            sw_repo1 = self._clone_repo(self.sw_repo1)
            ms_repo1 = self._clone_repo(self.ms_repo1, parent=sw_repo1)

            self._log_step(
            '3. Create a directory that will become the system yum repo')
            cmd = "/bin/mkdir {0}".format(s_repo1['path'])
            self._run_cmd_and_assert_success(self.ms1, cmd, su_root=True)

            self._log_step(
            '4. Copy an RPMs to the created system repo folder')
            self._copy_rpm_to_ms(s_repo1['path'],
                                 s_repo1['rpm'],
                                 s_repo1['rpm_src'])

            self._log_step(
            '5. Enable system repo using "create_repo" utility')
            self._create_system_repo(s_repo1['path'])

            msg = (
            '6. Create LITP source yum-repository items that points '
            'to a non existent system repo')
            self._log_step(msg)
            sw_repo1['ms_url_path'] = '/non_existent-sys-repo'
            props = ("name='{0}' ms_url_path='{1}'"
                     .format(sw_repo1['name'], sw_repo1['ms_url_path']))
            self.execute_cli_create_cmd(self.ms1,
                                        sw_repo1['path'],
                                        sw_repo1['item_type'],
                                        props)

            self._log_step(
            '7. Inherit LITP yum-repository items into MS')
            self.execute_cli_inherit_cmd(
                    self.ms1, ms_repo1['path'], ms_repo1['parent']['path'])

            self._log_step(
            '8. Create plan verify it fails')

            _, err, _ = self.execute_cli_createplan_cmd(self.ms1,
                    expect_positive=False)

            self.assertTrue(self.is_text_in_list('ValidationError    Create '\
                    'plan failed: The yum repository referenced by property '\
                    'ms_url_path "{0}" is not accessible. '\
                    'It is not possible to determine if the repository has '\
                    'been updated.'.format(sw_repo1['ms_url_path']), err))

            msg = (
            '10. Update yum-repository source "ms_url_path" so that it points '
            'to a valid sys repo LITP item')
            self._log_step(msg)
            sw_repo1 = self._clone_repo(self.sw_repo1)
            ms_repo1 = self._clone_repo(self.ms_repo1, parent=sw_repo1)

            props = 'ms_url_path="{0}"'.format(sw_repo1['ms_url_path'])
            self.execute_cli_update_cmd(self.ms1,
                                        sw_repo1['path'],
                                        props)

            self._log_step(
            '11. Create and run plan and verify it completes successfully')
            self._create_run_and_wait_for_plan(test_constants.PLAN_COMPLETE,
                'Plan to create yum-repository items failed')

            self._log_step(
            '12. Check that yum repo config file now has valid baseurl value')
            expected_contents = {}
            expected_contents['ensure_found'] = {
                'name': ms_repo1['parent']['name'],
                'baseurl': 'http://ms1{0}'
                           .format(ms_repo1['parent']['ms_url_path']),
                'enabled': '1',
                'gpgcheck': '0',
                'metadata_expire': '0',
                'skip_if_unavailable': '1'
            }
            expected_contents['ensure_not_found'] = {}
            self._assert_yum_repo_config_file_content(
                                            ms_repo1['node'],
                                            ms_repo1['parent']['config_file'],
                                            expected_contents)

            self._log_step(
            '13. Install packages using linux "yum" utility on MS and node1')
            self._log_step(
            'Install package "{0}" on  "{1}"'
            .format(ms_repo1['parent']['sys_repo']['pkg'], ms_repo1['node']))
            self._install_package(ms_repo1['node'],
                                      ms_repo1['parent']['sys_repo']['pkg'])
        finally:
            self._log_step(
            '14. Revert system to its initial state')
            self._remove_installed_packages_and_all_yum_repo_items()

    @attr('all', 'revert', 'story1708', 'story1708_tc03')
    def test_03_n_rename_yum_repo(self):
        """
        @tms_id: litpcds_1708_tc03
        @tms_requirements_id: LITPCDS-1708
        @tms_title: rename yum repo
        @tms_description: Verify that any attempt to update read-only
            properties of litp yum-repository items throws an error.
            This test is carried out on both source and child yum-repository
            items and after having installed a package using the created
            sys repository.
        @tms_test_steps:
            @step: 1. Find collection of software items on LITP model
            @result:  Collection of software items and stored
            @step: 2. Define yum-repository items to be used during test
            @result:  yum-repository items Create
            @step: 3. Create a directory for system yum repository
            @result:  dir created
            @step: 4. Copy an RPM to the created system repo folder
            @result:  RPMs are in the created system repo folder
            @step: 5. Create system repo using "createrepo" utility
            @result:  repo created on node
            @step: 6. Create LITP source yum-repository item
            @result:  Yum-repository source items created
            @step: 7. Inherit LITP yum-repo item to MS
            @result:  Yum-repository source items Inherit into MS
            @step: 8. Attempt to update yum repo read-only properties with
                yum-repo Item in "Initial" state and check for errors
            @result:  update successful
            @step: 9. Create and run the plan
            @result:  Plan run successfully
            @step:10. Check that yum repo config file was created successfully
            @result:  yum repo config file was created successfully
            @step:11. Install package using linux "yum" utility
            @result:  package installed
            @step:12. Attempt to update yum repo read-only properties with
                yum-repo Items in Applied state and check for errors
            @result:  update fails with correct error message
            @step:13. Revert system to its initial state
            @result:  system is returned to pre test state
        @tms_test_precondition:NA
        @tms_execution_type: Automated
        """
        test_id = 'story1708-tc03'
        fails = []

        try:
            self._log_step(
            '1. Find collection of software items on LITP model')
            sw_collection_sw_item_path = self.find(
                self.ms1, "/software", "collection-of-software-item")[0]

            ms_collection_sw_item_path = self.find(
                self.ms1, "/ms", "ref-collection-of-software-item")[0]

            self._log_step(
            '2. Define yum-repository items to be used during test')
            self._initialize_litp_items_definition(test_id,
                                                   sw_collection_sw_item_path,
                                                   ms_collection_sw_item_path,
                                                   None,
                                                   wait_for_puppet=False)

            s_repo = self._clone_repo(self.sys_repo1)
            sw_repo = self._clone_repo(self.sw_repo1)
            ms_repo = self._clone_repo(self.ms_repo1, parent=sw_repo)

            self._log_step(
            '3. Create a directory that will become the system yum repository')
            self.run_command(self.ms1,
                "mkdir {0}".format(s_repo['path']), su_root=True)

            self._log_step(
            '4. Copy an RPM to the created system repo folder')
            self._copy_rpm_to_ms(s_repo['path'],
                                 s_repo['rpm'],
                                 s_repo['rpm_src'])

            self._log_step(
            '5. Create system repo using "createrepo" utility')
            self._create_system_repo(s_repo['path'])

            self._log_step(
            '6. Create LITP source yum-repository item')
            props = ("name='{0}' ms_url_path='{1}'"
                     .format(sw_repo['name'], sw_repo['ms_url_path']))
            self.execute_cli_create_cmd(
                self.ms1, sw_repo['path'], sw_repo['item_type'], props)

            self._log_step(
            '7. Inherit LITP yum-repo item to MS')
            self.execute_cli_inherit_cmd(
                self.ms1, ms_repo['path'], ms_repo['parent']['path'])

            self._log_step(
            '8. Create and run the plan')
            self._create_run_and_wait_for_plan(test_constants.PLAN_COMPLETE,
                msg="YUM Repo Create Plan not completed successfully")

            self._log_step(
            '9. Check that yum repo config file was created successfully')
            expected_contents = {}
            expected_contents['ensure_found'] = {
                'name': ms_repo['parent']['name'],
                'baseurl': 'http://ms1{0}'
                           .format(ms_repo['parent']['ms_url_path']),
                'enabled': '1',
                'gpgcheck': '0',
                'metadata_expire': '0',
                'skip_if_unavailable': '1'
            }
            expected_contents['ensure_not_found'] = {}
            self._assert_yum_repo_config_file_content(
                                            ms_repo['node'],
                                            ms_repo['parent']['config_file'],
                                            expected_contents)

            self._log_step(
            '10. Install package using linux "yum" utility')
            self._install_package(self.ms1, s_repo['pkg'])

            info_msg = (
            '11. Attempt to update yum repo read-only properties '
               'with yum-repo items in Applied state')
            self._log_step(info_msg)

            rule_sets = []
            rule_set = {
             'path': sw_repo['path'],
             'description':
             '11.1. Attempt to update property "name" on LITP source yum-repo '
             'item',
             'param': "name='{0}_new_value' ms_url_path='{1}'"
                      .format(sw_repo['name'], sw_repo['ms_url_path_update']),
             'results':
             [
              {
                'path': sw_repo['path'],
                'msg': 'InvalidRequestError in property: "name"    '
                       'Unable to modify readonly property: name'
              },
             ]
            }
            rule_sets.append(rule_set.copy())

            for rule_set in rule_sets:
                fails.extend(self._execute_update_cmd_and_verify_error_msg(
                                                            self.ms1,
                                                            sw_repo['path'],
                                                            rule_set))

            rule_sets = []
            rule_set = {
             'path': ms_repo['path'],
             'description':
                '11.2. Attempt to update property "name" of LITP repo on MS ',
             'param': "name='{0}_new_value' ms_url_path='{1}'"
                      .format(ms_repo['parent']['name'],
                              ms_repo['parent']['ms_url_path_update']),
             'results':
             [
              {
              'path': ms_repo['path'],
              'msg': 'InvalidRequestError in property: "name"    '
                     'Unable to modify readonly property: name'
              },
             ]
            }
            rule_sets.append(rule_set.copy())

            for rule_set in rule_sets:
                fails.extend(self._execute_update_cmd_and_verify_error_msg(
                                                            self.ms1,
                                                            ms_repo['path'],
                                                            rule_set))
            self.assertEquals(fails, [],
                '\nThe following negative validation tests failed:\n {0}'
                .format('\n '.join(fails)))
        finally:
            self._log_step(
            '12. Revert system to its initial state')
            self._remove_installed_packages_and_all_yum_repo_items()

    @attr('all', 'revert', 'story1708', 'story1708_tc04')
    def test_04_n_yum_repo_create_validation(self):
        """
        @tms_id: litpcds_1708_tc04
        @tms_requirements_id: LITPCDS-1708
        @tms_title: Test 'create' validation  with invalid inputs
        @tms_description: Test 'create' validation  with invalid input
        @tms_test_steps:
            @step: 1. Find collection of software items on LITP model
            @result:  Collection of software items and stored
            @step: 2. Define yum-repository items to be used during test
            @result:  yum-repository items Create
            @step:3.1. Test create yum-repository command with invalid
                options/values
            @result:   Command fails with expected error message
            @step:3.2. Create a yum repository item-type with "ms_url_path"
                property only
            @result:   Command fails with expected error message
            @step:3.3. Create a yum repository item-type with "base_url"
                property only
            @result:   Command fails with expected error message
            @step:3.4. Create a yum repository item-type with "cache_metadata"
                property only
            @result:   Command fails with expected error message
            @step:3.5. Create a yum repository item-type with invalid
                "cache_metadata" property value
            @result:   Command fails with expected error message
            @step:3.6. Create a yum repository item-type with invalid "name"
                property value
            @result:   Command fails with expected error message
            @step:3.7. Create a yum repository item-type with a "name"
                property value that is not permitted
            @result:   Command fails with expected error message
            @step:3.8. Create a yum repository item-type with a "name"
                property value that is not permitted
            @result:   Command fails with expected error message
            @step:3.9. Create a yum repository item-type with invalid
                "ms_url_path" property value
            @result:   Command fails with expected error message
            @step:3.10.Create a yum repository item-type with invalid
                "base_url" property'
            @result:   Command fails with expected error message
            @step:3.11.Create a yum repository item-type with both "base_url"
                and "ms_url_path" properties
            @result:  Command fails with expected error message
        @tms_test_precondition:NA
        @tms_execution_type: Automated
        """
        test_id = 'story1708-tc04'
        fails = []

        self._log_step(
        '1. Find paths needed during test')
        sw_collection_sw_item_path = self.find(
            self.ms1, "/software", "collection-of-software-item")[0]

        ms_collection_sw_item_path = self.find(
            self.ms1, "/ms", "ref-collection-of-software-item")[0]

        mn1_collection_sw_item_path = self.find(
            node=self.ms1,
            path=self.find(self.ms1, "/deployments", 'node', True)[0],
            resource='ref-collection-of-software-item')[0]

        self._log_step(
        '2. Define yum-repository items to be used during test')
        self._initialize_litp_items_definition(test_id,
                                               sw_collection_sw_item_path,
                                               ms_collection_sw_item_path,
                                               mn1_collection_sw_item_path,
                                               wait_for_puppet=False)

        sw_repo = self.sw_repo1.copy()

        msg = (
        '3. Test create yum-repository command with invalid '
            'options/values')
        self._log_step(msg)
        rule_sets = []
        rule_set = {
         'description': '3.2. Create a yum repository item-type with '
                         '"ms_url_path" property only',
         'param': "ms_url_path='/{0}-repo'".format(test_id),
         'results':
         [
          {
           'msg': 'MissingRequiredPropertyError in property: "name"    '
            'ItemType "yum-repository" is required to have a property '
            'with name "name"'
           }
         ]
        }
        rule_sets.append(rule_set.copy())
        rule_set = {
         'description': '3.3. Create a yum repository item-type with '
                        '"base_url" property only',
         'param': "base_url='http://example.com/yum-repo'",
         'results':
         [
          {
           'msg': 'MissingRequiredPropertyError in property: "name"    '
                  'ItemType "yum-repository" is required to have a '
                  'property with name "name"',
           }
         ]
        }
        rule_sets.append(rule_set.copy())
        rule_set = {
        'description': '3.4. Create a yum repository item-type '
                       'with "cache_metadata" property only',
        'param': "cache_metadata='false'",
        'results':
         [
          {
           'msg': 'MissingRequiredPropertyError in property: "name"    '
             'ItemType "yum-repository" is required to have a property '
             'with name "name"'
           },
         ]
        }
        rule_sets.append(rule_set.copy())
        rule_set = {
        'description':
          '3.5. Create a yum repository item-type with invalid '
          '"cache_metadata" property value',
        'param':
            'name="{0}_repo" ms_url_path="/{0}-repo" cache_metadata="/yum"'
            .format(test_id),

        'results':
        [
         {
          'msg': 'ValidationError in property: "cache_metadata"    '
                 'Invalid value \'/yum\'.'
          }
         ]
        }
        rule_sets.append(rule_set.copy())
        rule_set = {
        'description':
          '3.6. Create a yum repository item-type with invalid '
          '"name" property value',
        'param': "name='' ms_url_path='/{0}-repo'".format(test_id),
        'results':
        [
         {
          'msg':
            'ValidationError in property: "name"    Invalid value \'\'.'
          }
         ]
        }
        rule_sets.append(rule_set.copy())
        rule_set = {
        'description': '3.7. Create a yum repository item-type with a '
                       '"name" property value that is not permitted',
        'param': "name='3PP' ms_url_path='/{0}-repo'".format(test_id),
        'results':
        [
         {
          'msg': 'ValidationError in property: "name"    '
                '3PP is not allowed as value for this property.'
          }
         ]
        }
        rule_sets.append(rule_set.copy())
        rule_set = {
        'description': '3.8. Create a yum repository item-type with a '
                       'name property that is not permitted',
        'param': "name='LITP' ms_url_path='/{0}-repo'".format(test_id),
        'results':
        [
         {
          'msg': 'ValidationError in property: "name"    '
                 'LITP is not allowed as value for this property.'
          }
         ]
        }
        rule_sets.append(rule_set.copy())
        rule_set = {
        'description': '3.9. Create a yum repository item-type with '
                       'invalid "ms_url_path" property value',
        'param': 'name="{0}_repo" ms_url_path="http://example.com/yum-repo"'
                 .format(test_id),
        'results':
        [
         {
          'msg': 'ValidationError in property: "ms_url_path"    '
                 'Invalid value \'http://example.com/yum-repo\'.'
          }
         ]
        }
        rule_sets.append(rule_set.copy())
        rule_set = {
        'description': '3.10. Create a yum repository item-type with '
                       '"invalid base_url" property',
        'param': "name='{0}_repo' base_url='/{0}-repo'".format(test_id),
        'results':
        [
         {
          'msg': 'ValidationError in property: "base_url"    '
                 'Invalid value \'/{0}-repo\'.'.format(test_id)
          }
         ]
        }
        rule_sets.append(rule_set.copy())
        rule_set = {
        'description': '3.11. Create a yum repository item-type with both '
                       '"base_url" and "ms_url_path" properties',
        'param': 'name="{0}_repo" '
                 'base_url="http://example.com/yum_repo" '
                 'ms_url_path="/{0}-repo"'.format(test_id),
        'results':
        [
         {
          'msg': 'ValidationError    Only one of "ms_url_path" or '
                 '"base_url" property must be set.'
          }
         ]
        }
        rule_sets.append(rule_set.copy())

        for rule_set in rule_sets:
            fails.extend(
                self._execute_create_cmd_and_verify_msg(
                                                self.ms1,
                                                sw_repo['path'],
                                                sw_repo['item_type'],
                                                rule_set))

        self.assertEquals(fails, [],
            '\nThe following NEGATIVE validation tests failed:\n {0}'
            .format('\n '.join(fails)))

    @attr('all', 'revert', 'story1708', 'story1708_tc05')
    def test_05_p_yum_repo_cache_metadata(self):
        """
        @tms_id: litpcds_1708_tc05
        @tms_requirements_id: LITPCDS-1708
        @tms_title: yum plugin "cache_metadata" property
        @tms_description: Test yum plugin "cache_metadata" property
        @tms_test_steps:
            @step: 1. Find paths needed during test
            @result:  paths needed during test stored
            @step: 2. Create yum-repository items to be used during test
            @result:  yum-repository items created
            @step: 3. Create directories that will become the system yum repo
            @result:  Directories created on MS and node1
            @step: 4. Copy an RPMs to the created system repo folder
            @result:  RPMs copied to system repo folder on MS and node1
            @step: 5. Enable system repo using "create_repo" utility
            @result:  Repo is created on on MS and node1
            @step: 6. Create LITP source yum-repository items
            @result:  Yum-repository source items created
            @step: 7. Inherit LITP yum repository items into MS
            @result:  Yum-repository source items Inherit into MS
            @step: 8. Create and run the plan
            @result:  plan completes successfully
            @step: 9. Check that yum repo config file was created successfully
            @result:  yum repo config file was created successfully
            @step:10. Update 'cache_metadata' property of LITP source
                yum-repository item
            @result:  'cache_metadata' property updated
            @step:11. Create plan
            @result:  plan created successfully
            @step:12. Verify metadata cleanup task is not generated
            @result:  metadata cleanup task is not generated
            @step:13. Run the plan
            @result:  Plan completes successfully
            @step:14. Check that yum repo config file does not contain
                "metadata_expire" field
            @result:  yum repo config file does not contain "metadata_expire"
            @step:15. Revert system to its initial state
            @result:  System is restored to pre test state
        @tms_test_precondition:NA
        @tms_execution_type: Automated
        """
        test_id = 'story1708-tc05'

        try:
            self._log_step(
            '1. Find paths needed during test')
            sw_collection_sw_item_path = self.find(
                self.ms1, "/software", "collection-of-software-item")[0]

            ms_collection_sw_item_path = self.find(
                self.ms1, "/ms", "ref-collection-of-software-item")[0]

            self._log_step(
            '2. Define yum-repository items to be used during test')
            self._initialize_litp_items_definition(test_id,
                                                   sw_collection_sw_item_path,
                                                   ms_collection_sw_item_path,
                                                   None,
                                                   wait_for_puppet=False)

            s_repo1 = self._clone_repo(self.sys_repo1)
            sw_repo1 = self._clone_repo(self.sw_repo1)
            ms_repo1 = self._clone_repo(self.ms_repo1, parent=sw_repo1)

            self._log_step(
            '3. Create a directory that will become the system yum repo')
            cmd = "/bin/mkdir {0}".format(s_repo1['path'])
            self._run_cmd_and_assert_success(self.ms1, cmd, su_root=True)

            self._log_step(
            '4. Copy an RPMs to the created system repo folder')
            self._copy_rpm_to_ms(s_repo1['path'],
                                 s_repo1['rpm'],
                                 s_repo1['rpm_src'])

            self._log_step(
            '5. Enable system repo using "create_repo" utility')
            self._create_system_repo(s_repo1['path'])

            self._log_step(
            '6. Create LITP source yum-repository')
            props = ("name='{0}' ms_url_path='{1}'"
                     .format(sw_repo1['name'], sw_repo1['ms_url_path']))
            self.execute_cli_create_cmd(
                self.ms1, sw_repo1['path'], sw_repo1['item_type'], props)

            self._log_step(
            '7. Inherit LITP yum-repository into MS')
            self.execute_cli_inherit_cmd(
                self.ms1, ms_repo1['path'], ms_repo1['parent']['path'])

            self._log_step(
            '8. Create and run the plan')
            self._create_run_and_wait_for_plan(test_constants.PLAN_COMPLETE,
                msg="YUM Repo Create Plan not completed successfully")

            self._log_step(
            '9. Check that yum repo config file content is correct')
            expected_contents = {}
            expected_contents['ensure_found'] = {
                'name': ms_repo1['parent']['name'],
                'baseurl': 'http://ms1{0}'
                           .format(ms_repo1['parent']['ms_url_path']),
                'enabled': '1',
                'gpgcheck': '0',
                'metadata_expire': '0',
                'skip_if_unavailable': '1'
            }
            expected_contents['ensure_not_found'] = {}
            self._assert_yum_repo_config_file_content(
                                            ms_repo1['node'],
                                            ms_repo1['parent']['config_file'],
                                            expected_contents)

            msg = (
            '10. Update "cache_metadata" property of LITP source '
                 'yum-repository')
            self._log_step(msg)
            props = "cache_metadata='true'"
            self.execute_cli_update_cmd(self.ms1, sw_repo1['path'], props)

            self._log_step('11. Create plan')
            self.execute_cli_createplan_cmd(self.ms1)

            self._log_step("12. Verify metadata cleanup task is not generated")
            self._verify_clean_metadata_task(self.ms1, self.sw_repo1['name'],
                    expect_task=False)

            self._log_step('13. Run the plan')
            self._create_run_and_wait_for_plan(test_constants.PLAN_COMPLETE,
                msg="YUM Repo Create Plan not completed successfully",
                create_plan=False)

            msg = (
            '14. Check that yum repo config file does not contain '
            '"metadata_expire" field')
            self._log_step(msg)
            expected_contents = {}
            expected_contents['ensure_found'] = {
                'name': ms_repo1['parent']['name'],
                'baseurl': 'http://ms1{0}'
                           .format(ms_repo1['parent']['ms_url_path']),
                'enabled': '1',
                'gpgcheck': '0',
                'skip_if_unavailable': '1'
            }
            expected_contents['ensure_not_found'] = {'metadata_expire': None}
            self._assert_yum_repo_config_file_content(
                                            ms_repo1['node'],
                                            ms_repo1['parent']['config_file'],
                                            expected_contents)
        finally:
            self._log_step(
            '15. Revert system to its initial state')
            self._remove_installed_packages_and_all_yum_repo_items()

    @attr('all', 'revert', 'story1708', 'story1708_tc06')
    def test_06_p_yum_repo_update_path(self):
        """
        @tms_id: litpcds_1708_tc06
        @tms_requirements_id: LITPCDS-1708
        @tms_title: yum repo update path
        @tms_description: Test update of yum plugin "ms_url_path" and
            "base_url" properties
        @tms_test_steps:
           @step: 1. Find paths needed during test
            @result:  paths needed during test stored
            @step: 2. Create yum-repository items to be used during test
            @result:  yum-repository items created
            @step: 3. Create directories that will become the system yum repo
            @result:  Directories created on MS and node1
            @step: 4. Copy an RPMs to the created system repo folder
            @result:  RPMs copied to system repo folder on MS and node1
            @step: 5. Enable system repo using "create_repo" utility
            @result:  Repo is created on on MS and node1
            @step:6.1 Create LITP source yum-repository items
            @result: Source yum-repository items created
            @step:6.2 Inherit LITP yum-repository into MS
            @result:   Item inherited onto the MS
            @step:6.3 Inherit LITP yum-repositories into node1
            @result:  Item inherited onto the node
            @step:6.4 Create and run plan to create litp yum-repository items
            @result:  Plan runs successfully and repos created
            @step:6.5 Check that yum repo config files were created ok
            @result:  Config files were created successfully
            @step:6.6 Update property "ms_url_path" on MS and node1
            @result:  "ms_url_path" on MS and node1 Updated
            @step:6.7 Create plan
            @result:  Plan creates successfully
            @step:6.8 Verify metadata cleanup task is in correct phase
            @result:  Metadata cleanup task is generated in correct phase
            @step:6.9 Run the plan to update property "ms_url_path"
            @result:  Plan runs successfully
            @step:6.10.Check that yum repo config files have updated "baseurl"
            @result:  yum repo config files have updated "baseurl" value
            @step:7.1 Replace property "ms_url_path" with "base_url"
                on LITP source yum-repository item
            @result:  Property "ms_url_path" replaced with "base_url"
                on LITP source yum-repository item
            @step:7.2 Create plan
            @result:  Plan creates successfully
            @step:7.3 Verify metadata cleanup task is in correct phase
            @result:  Metadata cleanup task is generated in correct phase
            @step:7.4 Run the plan to replace property "ms_url_path"
                with base_url
            @result:  Plan runs successfully
            @step:7.5 Check that yum repo config files have updated
                "baseurl" value
            @result:  Yum repo config files have updated "baseurl" value
            @step:8. Revert system to its initial state
            @result:  System is back to a pre test state
        @tms_test_precondition:NA
        @tms_execution_type: Automated
        """
        test_id = 'story1708-tc06'

        try:
            self._log_step(
            '1. Find paths needed during test')
            sw_collection_sw_item_path = self.find(
                self.ms1, "/software", "collection-of-software-item")[0]

            ms_collection_sw_item_path = self.find(
                self.ms1, "/ms", "ref-collection-of-software-item")[0]

            mn1_collection_sw_item_path = self.find(
                node=self.ms1,
                path=self.find(self.ms1, '/deployments', 'node')[0],
                resource="ref-collection-of-software-item")[0]

            self._log_step(
            '2. Define yum-repository items to be used during test')
            self._initialize_litp_items_definition(test_id,
                                                   sw_collection_sw_item_path,
                                                   ms_collection_sw_item_path,
                                                   mn1_collection_sw_item_path,
                                                   wait_for_puppet=False)

            s_repo1 = self._clone_repo(self.sys_repo1)
            sw_repo1 = self._clone_repo(self.sw_repo1)
            ms_repo1 = self._clone_repo(self.ms_repo1, parent=sw_repo1)
            mn1_repo1 = self._clone_repo(self.mn1_repo1, parent=sw_repo1)

            self._log_step(
            '3. Create a directory that will become the system yum repository')
            self.run_command(self.ms1,
                "mkdir {0}".format(s_repo1['path']), su_root=True)

            self._log_step(
            '4. Copy an RPM to the created system repo folder')
            self._copy_rpm_to_ms(s_repo1['path'],
                                 s_repo1['rpm'],
                                 s_repo1['rpm_src'])

            self._log_step(
            '5. Create system repo using "createrepo" utility')
            self._create_system_repo(s_repo1['path'])

            self._log_step(
            '6. Testing update of "ms_url_path" property')

            self._log_step(
            '6.1 Create LITP source yum-repository items')
            props = ("name='{0}' ms_url_path='{1}'"
                     .format(sw_repo1['name'], sw_repo1['ms_url_path']))
            self.execute_cli_create_cmd(self.ms1,
                                        sw_repo1['path'],
                                        sw_repo1['item_type'],
                                        props)

            self._log_step(
            '6.2. Inherit LITP yum-repository into MS')
            self.execute_cli_inherit_cmd(
                    self.ms1, ms_repo1['path'], ms_repo1['parent']['path'])

            self._log_step(
            '6.3. Inherit LITP yum-repositories into node1')
            self.execute_cli_inherit_cmd(
                    self.ms1, mn1_repo1['path'], mn1_repo1['parent']['path'])

            self._log_step(
            '6.4. Create and run plan to create litp yum-repository items')
            self._create_run_and_wait_for_plan(test_constants.PLAN_COMPLETE,
                msg="YUM Repo Create Plan not completed successfully")

            self._log_step(
            '6.5. Check that yum repo config files were created successfully')
            for each_repo in [ms_repo1, mn1_repo1]:
                expected_contents = {}
                expected_contents['ensure_found'] = {
                    'name': each_repo['parent']['name'],
                    'baseurl': 'http://ms1{0}'
                               .format(each_repo['parent']['ms_url_path']),
                    'enabled': '1',
                    'gpgcheck': '0',
                    'metadata_expire': '0',
                    'skip_if_unavailable': '1'
                }
                expected_contents['ensure_not_found'] = {}
                self._assert_yum_repo_config_file_content(
                                            each_repo['node'],
                                            each_repo['parent']['config_file'],
                                            expected_contents)

            self._log_step(
            '6.6. Update property "ms_url_path" on MS and node1')
            ms_repo1['ms_url_path'] = '/{0}-updated-repo'.format(test_id)
            mn1_repo1['ms_url_path'] = '/{0}-updated-repo'.format(test_id)

            # Create a directory that will become the system yum repository
            repo_dir = '{0}{1}'.format(test_constants.PARENT_PKG_REPO_DIR,
                                        ms_repo1['ms_url_path'])
            self.assertTrue(self.create_dir_on_node(self.ms1,
                                                    repo_dir,
                                                    su_root=True))

            # Create system repo using "createrepo" utility
            self._create_system_repo(repo_dir)

            props = 'ms_url_path="{0}"'.format(ms_repo1['ms_url_path'])
            self.execute_cli_update_cmd(self.ms1, ms_repo1['path'], props)

            props = 'ms_url_path="{0}"'.format(mn1_repo1['ms_url_path'])
            self.execute_cli_update_cmd(self.ms1, mn1_repo1['path'], props)

            self._log_step('6.7 Create plan')
            self.execute_cli_createplan_cmd(self.ms1)
            self._log_step(
            '6.8. Verify metadata cleanup task is generated in correct phase')
            self._verify_clean_metadata_task(self.ms1, self.sw_repo1['name'])
            self._verify_clean_metadata_task(self.mn1, self.sw_repo1['name'])

            self._log_step(
            '6.9. Run the plan to update property "ms_url_path"')
            self._create_run_and_wait_for_plan(test_constants.PLAN_COMPLETE,
                msg="YUM Repo Update Plan not completed successfully",
                create_plan=False)

            msg = (
            '6.10. Check that yum repo config files have updated "baseurl" '
                 'value')
            self._log_step(msg)
            for each_repo in [ms_repo1, mn1_repo1]:
                expected_contents = {}
                expected_contents['ensure_found'] = {
                    'name': each_repo['parent']['name'],
                    'baseurl': 'http://ms1{0}'
                               .format(each_repo['ms_url_path']),
                    'enabled': '1',
                    'gpgcheck': '0',
                    'metadata_expire': '0',
                    'skip_if_unavailable': '1'
                }
                expected_contents['ensure_not_found'] = {}
                self._assert_yum_repo_config_file_content(
                                            each_repo['node'],
                                            each_repo['parent']['config_file'],
                                            expected_contents)

            self._log_step('7. Testing update of "base_url" property')

            self._log_step(
                    '7.1. Replace property "ms_url_path" with "base_url" on '
                    'LITP source yum-repository item')
            sw_repo1['base_url'] = ('http://{0}-updated-base-url-repo'
                                    .format(test_id))

            props = ('base_url="{0}" -d ms_url_path'
                    .format(sw_repo1['base_url']))
            self.execute_cli_update_cmd(self.ms1, ms_repo1['path'],
            "ms_url_path", action_del=True)
            self.execute_cli_update_cmd(self.ms1, mn1_repo1['path'],
            "ms_url_path", action_del=True)
            self.execute_cli_update_cmd(self.ms1, sw_repo1['path'], props)

            self._log_step('7.2 Create plan')
            self.execute_cli_createplan_cmd(self.ms1)
            self._log_step(
            '7.3. Verify metadata cleanup task is generated in correct phase')

            self._verify_clean_metadata_task(self.ms1, self.sw_repo1['name'])
            self._verify_clean_metadata_task(self.mn1, self.sw_repo1['name'])

            msg = (
            '7.4. Run the plan to replace property ms_url_path with base_url')
            self._log_step(msg)
            self._create_run_and_wait_for_plan(test_constants.PLAN_COMPLETE,
                msg="Replace ms_url_path plan not completed successfully",
                create_plan=False)

            msg = (
            '7.5. Check that yum repo config files have updated "baseurl" '
                  'value')
            self._log_step(msg)
            for each_repo in [ms_repo1, mn1_repo1]:
                expected_contents = {}
                expected_contents['ensure_found'] = {
                    'name': each_repo['parent']['name'],
                    'baseurl': '{0}'.format(each_repo['parent']['base_url']),
                    'enabled': '1',
                    'gpgcheck': '0',
                    'metadata_expire': '0',
                    'skip_if_unavailable': '1'
                }
                expected_contents['ensure_not_found'] = {}
                self._assert_yum_repo_config_file_content(
                                            each_repo['node'],
                                            each_repo['parent']['config_file'],
                                            expected_contents)
        finally:
            self._log_step(
            '8. Revert system to its initial state')
            self._remove_installed_packages_and_all_yum_repo_items()

    @attr('manual-test', 'revert', 'story1708', 'story1708_tc08')
    def test_08_n_puppet_yum_race_condition(self):
        """
        @tms_id: litpcds_1708_tc08
        @tms_requirements_id: LITPCDS-1708
        @tms_title: Test puppet yum race condition
        @tms_description: Verify that a plan to remove yum repository items
            completes only after any pending puppet task is completed.
            This is to ensure puppet does not restore yum configuration files
            manually removed after removing LITP yum-repository items from
            model.
        @tms_test_steps:
            @step: 1. Find paths needed during test
            @result:  Paths needed during test stored
            @step: 2. Create yum-repository items to be used during test
            @result:  Yum-repository items created
            @step: 3. Create directories that will become the system yum repo
            @result:  Directories created on MS and node1
            @step: 4. Copy an RPMs to the created system repo folder
            @result:  RPMs copied to system repo folder on MS and node1
            @step: 5. Enable system repo using "create_repo" utility
            @result:  Repo is created on on MS and node1
            @step: 6. Create LITP source yum-repository items
            @result:  Source yum-repository items created
            @step: 7. Inherit LITP source yum-repository item into MS and nodes
            @result:  Item inherited onto the MS and node
            @step: 8. Create and run the plan
            @result:  Plan is run successfully
            @step: 9. Check if yum config file is present
            @result:  yum config file are present
            @step:10. Remove LITP yum-repository items from model
            @result:  Yum-repository items from model
            @step:11. Wait for puppet idle and then kick off new puppet job
            @result:  Puppet job is run
            @step:12. Sleep Xs then create and run the plan
            @result:  Plan fails with expected
            @step:13. Remove LITP yum-repository config files
            @result:  LITP yum-repository config files removed
            @step:14. Sleep for 1 puppet cycle time
            @result:  Wait one puppet cycle before continuing
            @step:15. Check if yum config file are still present
            @result:  Yum config file are still present
        @tms_test_precondition:NA
        @tms_execution_type: Automated
        """
        test_id = 'story1708-tc08'

        self._log_step(
        '1. Find collection of software items on LITP model')
        sw_collection_sw_item_path = self.find(
            self.ms1, "/software", "collection-of-software-item")[0]

        ms_collection_sw_item_path = self.find(
            self.ms1, "/ms", "ref-collection-of-software-item")[0]

        mn1_collection_sw_item_path = self.find(
            node=self.ms1,
            path=self.find(self.ms1, '/deployments', 'node')[0],
            resource="ref-collection-of-software-item")[0]

        mn2_collection_sw_item_path = self.find(
            node=self.ms1,
            path=self.find(self.ms1, '/deployments', 'node')[1],
            resource="ref-collection-of-software-item")[0]

        self._log_step(
        '2. Define yum-repository items to be used during test')
        self._initialize_litp_items_definition(test_id,
                                               sw_collection_sw_item_path,
                                               ms_collection_sw_item_path,
                                               mn1_collection_sw_item_path)

        s_repo1 = self._clone_repo(self.sys_repo1)

        self._log_step(
        '3. Create a directory that will become the system yum repo')
        cmd = "/bin/mkdir {0}".format(s_repo1['path'])
        self._run_cmd_and_assert_success(self.ms1, cmd, su_root=True)

        self._log_step(
        '4. Copy an RPMs to the created system repo folder')
        self._copy_rpm_to_ms(s_repo1['path'],
                             s_repo1['rpm'],
                             s_repo1['rpm_src'])

        self._log_step(
        '5. Enable system repo using "create_repo" utility')
        self._create_system_repo(s_repo1['path'])

        for i in range(30, 3, -3):
            sw_repo1 = self._clone_repo(self.sw_repo1)
            sw_repo1['name'] = '{0}__{1}s_'.format(sw_repo1['name'], i)
            sw_repo1['config_file'] = ('{0}/{1}.repo'
                .format(test_constants.YUM_CONFIG_FILES_DIR, sw_repo1['name']))
            ms_repo1 = self._clone_repo(self.ms_repo1, parent=sw_repo1)
            mn1_repo1 = self._clone_repo(self.mn1_repo1, parent=sw_repo1)
            mn2_repo1 = self._clone_repo(self.mn1_repo1, parent=sw_repo1)
            mn2_repo1['node'] = self.mn2
            mn2_repo1['path'] = ('{0}/{1}_mn2_repo_1'
                        .format(mn2_collection_sw_item_path, test_id))

            all_child_repos = [ms_repo1, mn1_repo1, mn2_repo1]

            self.log('info', '\n.' * 10)
            self.log('info', 'Iteration with sleep time of {0}s'.format(i))
            self.log('info', '\n.' * 10)
            msg = (
            '6. Create LITP source yum-repository items')
            self._log_step(msg)
            props = ("name='{0}' ms_url_path='{1}'"
                     .format(sw_repo1['name'], sw_repo1['ms_url_path']))
            self.execute_cli_create_cmd(self.ms1,
                                        sw_repo1['path'],
                                        sw_repo1['item_type'],
                                        props)

            self._log_step(
            '7. Inherit LITP source yum-repository item into MS and nodes')
            for each_repo in all_child_repos:
                self.execute_cli_inherit_cmd(self.ms1, each_repo['path'],
                                             each_repo['parent']['path'])

            self._log_step(
            '8. Create and run the plan')
            self._create_run_and_wait_for_plan(
                test_constants.PLAN_COMPLETE,
                msg="YUM Repo Install Plan not completed successfully")

            self._log_step(
            '9. Check if yum config files are present')
            err_msg_template = (
            'File "{0}" NOT found on system after plan completed')
            for each_repo in all_child_repos:
                self.assertTrue(
                    self.remote_path_exists(
                        each_repo['node'],
                        each_repo['parent']['config_file']),
                        err_msg_template
                        .format(each_repo['parent']['config_file']))

            self._log_step(
            '10. Remove LITP yum-repository items from model')
            for each_repo in all_child_repos + [sw_repo1]:
                self.execute_cli_remove_cmd(self.ms1, each_repo['path'])

            self._log_step(
            '11. Wait for puppet idle and then kick off new puppet job')
            self.wait_for_puppet_idle(self.ms1)
            cmd = 'mco puppet runonce'
            self.run_command(self.ms1, cmd, su_root=True)

            self._log_step(
            '12. Sleep {0}s then create and run the plan'.format(i))
            time.sleep(i)
            msg = (
            "YUM Repo and Packages Remove Plan not completed successfully")
            self._create_run_and_wait_for_plan(
                                    test_constants.PLAN_COMPLETE,
                                    msg=msg)

            self._log_step(
            '13. Remove yum configuration files')
            for each_node in [x['node'] for x in all_child_repos]:
                self.remove_item(
                    each_node,
                    '{0}/story*'.format(test_constants.YUM_CONFIG_FILES_DIR),
                    su_root=True)

            self._log_step(
            '14. Sleep for 1 puppet cycle time')
            time.sleep(self.get_puppet_interval(self.ms1))

            self._log_step(
            '15. Check if yum config file are still present')
            self._assert_yum_repos_dir_does_not_contain_story_files(
                                    [x['node'] for x in all_child_repos])

    @attr('all', 'revert', 'story1708', 'story1708_tc09')
    def test_09_n_yum_repo_create_plan_validation(self):
        """
        @tms_id: litpcds_1708_tc09
        @tms_requirements_id: LITPCDS-1708
        @tms_title: Yum repo create plan validation
        @tms_description: Test validation associated with yum plugin
        @tms_test_steps:
            @step: 1. Find paths needed during test
            @result: Paths needed during test stored
            @step: 2. Create yum-repository items to be used during test
            @result: Yum-repository items created
            @step:3.1. Create first LITP source yum repo item'
            @result: Source yum-repository items created
            @step:3.2. Create 2nd LITP source yum repo item with duplicate name
            @result: Second source yum-repository items created
            @step:3.3. Inherit both repos on the MS
            @result: items inherited to MS
            @step:3.4. Inherit both repos on node1
            @result: items inherited to node
            @step:3.5. Create_plan with duplicate repository name
            @result: Create plan fails with expcted error
            @step:3.6. Remove duplicate repo items
            @result: duplicate repo items removed
            @step:4.1. Create first LITP source yum repo item with ms_url_path
            @result: LITP source yum repo item with ms_url_path created
            @step:4.2. Create second LITP source yum repo item with
                duplicate ms_url_path
            @result: LITP yum repo item with duplicate ms_url_path created
            @step:4.3. Inherit both source repos on the MS
            @result: items inherited to MS
            @step:4.4. Inherit both source repos on node1
            @result: items inherited to node1
            @step:4.5. Create plan for Yum repository items with duplicate
                "ms_url_path"
            @result: Plan fails with expected error message
            @step:4.6. Remove LITP yum items
            @result: Item is in ForRemoval state
            @step:5.1. Create first LITP source yum repo item with base_url
            @result: item is created and is in Initial state
            @step:5.2. Create second LITP source yum repo item with
                duplicate base_url
            @result: item is created and is in Initial state
            @step:5.3. Inherit both source repos on the MS
            @result: items inherited to MS
            @step:5.4. Inherit both source repos on node1
            @result: items inherited to node1
            @step:5.5. Create plan for Yum repository items with
                duplicate "base_url"
            @result: Plan fails with expected error message
            @step:5.6. Remove LITP yum items
            @result: Item is Removed from model
            @step:6.1. Create LITP source yum repo item with "base_url"
            @result: Item is created and is in Initial state
            @step:6.2. Update the yum repository item-type with an invalid
                base_url property
            @result: Item is updated as expected
            @step:6.3. Update the yum repository item-type with an invalid
                name property
            @result: Item is updated as expected
            @step:6.4. Update the yum repository item-type with an invalid
                "cache_metadata" property
            @result: Item is updated as expected
            @step:6.5. Update yum repository item to use "ms_url_path"
                instead of the "base_url" property
            @result: Item is updated as expected
            @step:6.6. Remove LITP yum items
            @result: Item is Removed from model
            @step:7.1. Create plan with LITP yum repo item with "base_url"
            @result: Plan fails with expected error message
            @step:7.2. Inherit source repo on the MS
            @result: Items inherited to MS
            @step:7.3  "update -o -d" to switch from "base_url" 2 "ms_url_base"
            @result: Item is updated as expected
            @step:7.4  "update -d -o" to switch from "base_url" 2 "ms_url_base"
            @result: Item is updated as expected
            @step:7.5. Create and run plan
            @result: Plan is created and run
            @step:7.6. Testing validation errors with "update" command on
                inherited yum repository items in Applied state
            @result: Plan fails with expected error message
            @step:8. Revert system to its initial state
            @result: system is returned to pre test state
        @tms_test_precondition:NA
        @tms_execution_type: Automated
        """
        test_id = 'story1708-tc09'
        fails = []

        try:
            self._log_step(
            '1. Find paths needed during test')
            sw_collection_sw_item_path = self.find(
                self.ms1, "/software", "collection-of-software-item")[0]

            ms_collection_sw_item_path = self.find(
                self.ms1, "/ms", "ref-collection-of-software-item")[0]

            mn1_collection_sw_item_path = self.find(
                node=self.ms1,
                path=self.find(self.ms1, "/deployments", 'node', True)[0],
                resource='ref-collection-of-software-item')[0]

            self._log_step(
            '2. Define yum-repository items to be used during test')
            self._initialize_litp_items_definition(test_id,
                                                   sw_collection_sw_item_path,
                                                   ms_collection_sw_item_path,
                                                   mn1_collection_sw_item_path,
                                                   wait_for_puppet=False)

            self._log_step(
            '3. Testing create_plan with duplicate repository name')
            sw_repo1 = self._clone_repo(self.sw_repo1)
            sw_repo2 = self._clone_repo(self.sw_repo2)
            sw_repo2['name'] = sw_repo1['name']

            ms_repo1 = self._clone_repo(self.ms_repo1, parent=sw_repo1)
            ms_repo2 = self._clone_repo(self.ms_repo2, parent=sw_repo2)

            mn_repo1 = self._clone_repo(self.mn1_repo1, parent=sw_repo1)
            mn_repo2 = self._clone_repo(self.mn1_repo2, parent=sw_repo2)

            self._log_step(
            '3.1. Create first LITP source yum repo item')
            props = ('name="{0}" ms_url_path="{1}"'
                     .format(sw_repo1['name'], sw_repo1['ms_url_path']))
            self.execute_cli_create_cmd(self.ms1,
                                        sw_repo1['path'],
                                        sw_repo1['item_type'],
                                        props)

            self._log_step(
            '3.2. Create second LITP source yum repo item with duplicate name')
            props = ('name="{0}" base_url="{1}"'
                     .format(sw_repo2['name'], sw_repo2['base_url']))
            self.execute_cli_create_cmd(self.ms1,
                                        sw_repo2['path'],
                                        sw_repo2['item_type'],
                                        props)

            self._log_step(
            '3.3. Inherit both source repos on the MS')
            self.execute_cli_inherit_cmd(self.ms1,
                                         ms_repo1['path'],
                                         ms_repo1['parent']['path'])

            self.execute_cli_inherit_cmd(self.ms1,
                                         ms_repo2['path'],
                                         ms_repo2['parent']['path'])

            self._log_step(
            '3.4. Inherit both source repos on node1')
            self.execute_cli_inherit_cmd(self.ms1,
                                         mn_repo1['path'],
                                         mn_repo1['parent']['path'])

            self.execute_cli_inherit_cmd(self.ms1,
                                         mn_repo2['path'],
                                         mn_repo2['parent']['path'])

            rule_set = {
            'description': '3.5. Create_plan with duplicate repository name',
            'param': None,
            'results': list()}

            for repo in [ms_repo1, ms_repo2, mn_repo1, mn_repo2]:
                rule_set['results'].append(
                 {
                  'path': '{0}'.format(repo['path']),
                  'msg': 'ValidationError    Create plan failed: '
                      'The property "name" with value "{0}" '
                      'must be unique per node'
                         .format(repo['parent']['name'])
                  })
            fails.extend(
                self._execute_createplan_cmd_and_verify_msg(self.ms1,
                                                            rule_set))

            self._log_step(
            '3.6. Remove LITP yum items')
            self.execute_cli_remove_cmd(self.ms1, mn_repo2['path'])
            self.execute_cli_remove_cmd(self.ms1, mn_repo1['path'])
            self.execute_cli_remove_cmd(self.ms1, ms_repo2['path'])
            self.execute_cli_remove_cmd(self.ms1, ms_repo1['path'])
            self.execute_cli_remove_cmd(self.ms1, sw_repo2['path'])
            self.execute_cli_remove_cmd(self.ms1, sw_repo1['path'])

            self._log_step(
            '4. Testing create_plan with duplicate ms_url_path value')

            sw_repo1 = self._clone_repo(self.sw_repo1)
            sw_repo2 = self._clone_repo(self.sw_repo2)
            sw_repo2['ms_url_path'] = sw_repo1['ms_url_path']

            ms_repo1 = self._clone_repo(self.ms_repo1, parent=sw_repo1)
            ms_repo2 = self._clone_repo(self.ms_repo2, parent=sw_repo2)

            mn_repo1 = self._clone_repo(self.mn1_repo1, parent=sw_repo1)
            mn_repo2 = self._clone_repo(self.mn1_repo2, parent=sw_repo2)

            self._log_step(
            '4.1. Create first LITP source yum repo item with ms_url_path')
            props = ('name="{0}" ms_url_path="{1}"'
                     .format(sw_repo1['name'], sw_repo1['ms_url_path']))
            self.execute_cli_create_cmd(self.ms1,
                                        sw_repo1['path'],
                                        sw_repo1['item_type'],
                                        props)

            msg = (
            '4.2. Create second LITP source yum repo item with '
                 'duplicate ms_url_path')
            self._log_step(msg)
            props = ('name="{0}" ms_url_path="{1}"'
                     .format(sw_repo2['name'], sw_repo2['ms_url_path']))
            self.execute_cli_create_cmd(self.ms1,
                                        sw_repo2['path'],
                                        sw_repo2['item_type'],
                                        props)

            self._log_step(
            '4.3. Inherit both source repos on the MS')
            self.execute_cli_inherit_cmd(self.ms1,
                                         ms_repo1['path'],
                                         ms_repo1['parent']['path'])

            self.execute_cli_inherit_cmd(self.ms1,
                                         ms_repo2['path'],
                                         ms_repo2['parent']['path'])

            self._log_step(
            '4.4. Inherit both source repos on node1')
            self.execute_cli_inherit_cmd(self.ms1,
                                         mn_repo1['path'],
                                         mn_repo1['parent']['path'])

            self.execute_cli_inherit_cmd(self.ms1,
                                         mn_repo2['path'],
                                         mn_repo2['parent']['path'])

            rule_sets = []
            rule_set = {
            'description':
               '4.5. Yum repository items with duplicate "ms_url_path"',
            'param': None,
            'results': list()}

            for repo in [ms_repo1, ms_repo2, mn_repo1, mn_repo2]:
                rule_set['results'].append(
                 {
                  'path': '{0}'.format(repo['path']),
                  'msg': 'ValidationError    Create plan failed: '
                  'The property "ms_url_path" with value "{0}" must be '
                  'unique per node'.format(repo['parent']['ms_url_path'])
                  })

            fails.extend(
                self._execute_createplan_cmd_and_verify_msg(self.ms1,
                                                            rule_set))

            self._log_step(
            '4.6. Remove LITP yum items')
            self.execute_cli_remove_cmd(self.ms1, mn_repo2['path'])
            self.execute_cli_remove_cmd(self.ms1, mn_repo1['path'])
            self.execute_cli_remove_cmd(self.ms1, ms_repo2['path'])
            self.execute_cli_remove_cmd(self.ms1, ms_repo1['path'])
            self.execute_cli_remove_cmd(self.ms1, sw_repo2['path'])
            self.execute_cli_remove_cmd(self.ms1, sw_repo1['path'])

            self._log_step(
            '5. Testing create_plan with duplicate base_url_path value')

            sw_repo1 = self._clone_repo(self.sw_repo1)
            sw_repo2 = self._clone_repo(self.sw_repo2)
            sw_repo2['base_url'] = sw_repo1['base_url']

            ms_repo1 = self._clone_repo(self.ms_repo1, parent=sw_repo1)
            ms_repo2 = self._clone_repo(self.ms_repo2, parent=sw_repo2)

            mn_repo1 = self._clone_repo(self.mn1_repo1, parent=sw_repo1)
            mn_repo2 = self._clone_repo(self.mn1_repo2, parent=sw_repo2)

            self._log_step(
            '5.1. Create first LITP source yum repo item with base_url')
            props = ('name="{0}" base_url="{1}"'
                     .format(sw_repo1['name'], sw_repo1['base_url']))
            self.execute_cli_create_cmd(self.ms1,
                                        sw_repo1['path'],
                                        sw_repo1['item_type'],
                                        props)

            msg = (
            '5.2. Create second LITP source yum repo item with '
                 'duplicate base_url')
            self._log_step(msg)
            props = ('name="{0}" base_url="{1}"'
                     .format(sw_repo2['name'], sw_repo2['base_url']))
            self.execute_cli_create_cmd(self.ms1,
                                        sw_repo2['path'],
                                        sw_repo2['item_type'],
                                        props)

            self._log_step(
            '5.3. Inherit both source repos on the MS')
            self.execute_cli_inherit_cmd(self.ms1,
                                         ms_repo1['path'],
                                         ms_repo1['parent']['path'])

            self.execute_cli_inherit_cmd(self.ms1,
                                         ms_repo2['path'],
                                         ms_repo2['parent']['path'])

            self._log_step(
            '5.4. Inherit both source repos on node1')
            self.execute_cli_inherit_cmd(self.ms1,
                                         mn_repo1['path'],
                                         mn_repo1['parent']['path'])

            self.execute_cli_inherit_cmd(self.ms1,
                                         mn_repo2['path'],
                                         mn_repo2['parent']['path'])

            rule_sets = []
            rule_set = {
            'description':
               '5.5. Yum repository items with duplicate "base_url"',
            'param': None,
            'results': list()}

            for repo in [ms_repo1, ms_repo2, mn_repo1, mn_repo2]:
                rule_set['results'].append(
                 {
                  'path': '{0}'.format(repo['path']),
                  'msg': 'ValidationError    Create plan failed: '
                  'The property "base_url" with value "{0}" must be '
                  'unique per node'.format(repo['parent']['base_url'])
                  })

            fails.extend(
                self._execute_createplan_cmd_and_verify_msg(self.ms1,
                                                            rule_set))

            self._log_step(
            '5.6. Remove LITP yum items')
            self.execute_cli_remove_cmd(self.ms1, mn_repo2['path'])
            self.execute_cli_remove_cmd(self.ms1, mn_repo1['path'])
            self.execute_cli_remove_cmd(self.ms1, ms_repo2['path'])
            self.execute_cli_remove_cmd(self.ms1, ms_repo1['path'])
            self.execute_cli_remove_cmd(self.ms1, sw_repo2['path'])
            self.execute_cli_remove_cmd(self.ms1, sw_repo1['path'])

            msg = (
            '6. Testing validation errors with "update" command on source '
                'yum repository items')
            self._log_step(msg)
            sw_repo1 = self._clone_repo(self.sw_repo1)

            self._log_step(
            '6.1. Create LITP source yum repo item with "base_url"')
            props = ('name="{0}" base_url="{1}"'
                     .format(sw_repo1['name'], sw_repo1['base_url']))
            self.execute_cli_create_cmd(self.ms1,
                                        sw_repo1['path'],
                                        sw_repo1['item_type'],
                                        props)

            rule_sets = []
            rule_set = {
            'description': '6.2. Update the yum repository item-type with '
                           'an invalid base_url property',
            'param': "base_url='/example.com/yum-repo'",
            'results':
            [
             {
              'msg': 'ValidationError in property: "base_url"    '
                     'Invalid value \'/example.com/yum-repo\'.'
              }
             ]
            }
            rule_sets.append(rule_set.copy())
            rule_set = {
            'description': '6.3. Update the yum repository item-type with an '
                           'invalid name property',
            'param': "name='/example.com/yum_repo'",
            'results':
            [
             {
              'msg': 'ValidationError in property: "name"    '
                     'Invalid value \'/example.com/yum_repo\'.'
              }
             ]
            }
            rule_sets.append(rule_set.copy())
            rule_set = {
            'description': '6.4. Update the yum repository item-type with an '
                           'invalid cache_metadata property',
            'param': "cache_metadata=TRUE",
            'results':
            [
             {
              'msg': 'ValidationError in property: "cache_metadata"    '
                     'Invalid value \'TRUE\'.'
              }
             ]
            }
            rule_sets.append(rule_set.copy())
            rule_set = {
            'description': '6.5. Update yum repository item to use '
                           'ms_url_path instead of the base_url property',
            'param': "ms_url_path='/{0}-repo-a'".format(test_id),
            'results':
            [
             {
              'msg': 'ValidationError    Only one of "ms_url_path" or '
                     '"base_url" property must be set.'
              }
             ]
            }
            rule_sets.append(rule_set.copy())

            for rule_set in rule_sets:
                fails.extend(
                    self._execute_update_cmd_and_verify_error_msg(
                                                            self.ms1,
                                                            sw_repo1['path'],
                                                            rule_set))

            self._log_step(
            '6.6. Remove LITP yum items')
            self.execute_cli_remove_cmd(self.ms1, sw_repo1['path'])

            msg = (
            '7. Testing validation errors with "update" command on inherited '
                'yum repository items in Initial state')
            self._log_step(msg)

            sw_repo1 = self._clone_repo(self.sw_repo1)
            ms_repo1 = self._clone_repo(self.ms_repo1, parent=sw_repo1)

            self._log_step(
            '7.1. Create LITP source yum repo item with "base_url"')
            props = ('name="{0}" base_url="{1}"'
                     .format(sw_repo1['name'], sw_repo1['base_url']))
            self.execute_cli_create_cmd(self.ms1,
                                        sw_repo1['path'],
                                        sw_repo1['item_type'],
                                        props)

            self._log_step(
            '7.2.. Inherit source repo on the MS')
            self.execute_cli_inherit_cmd(self.ms1,
                                         ms_repo1['path'],
                                         ms_repo1['parent']['path'])

            rule_sets = []
            rule_set = {
            'description': '7.3 "update -o -d" to switch from "base_url" to '
                           '"ms_url_base"',
            'param': 'ms_url_path="/{0}-updated-repo"'.format(test_id),
            'args': '-d base_url',
            'action_delete': False,
            'results':
            [
             {
              'msg': 'ValidationError    Only one of "ms_url_path" or '
                     '"base_url" property must be set.'
              }
             ]
            }
            rule_sets.append(rule_set.copy())
            rule_set = {
            'description': '7.4 "update -d -o" to switch from "base_url" to '
                           '"ms_url_base"',
            'param': 'base_url',
            'args': ('-o ms_url_path="/{0}-updated_repo"'
                    .format(ms_repo1['parent']['base_url'])),
            'action_delete': True,
            'results':
            [
             {
              'msg': 'ValidationError    Only one of "ms_url_path" or '
                     '"base_url" property must be set.'
              }
             ]
            }
            rule_sets.append(rule_set.copy())

            for rule_set in rule_sets:
                fails.extend(
                    self._execute_update_cmd_and_verify_error_msg(
                                                            self.ms1,
                                                            ms_repo1['path'],
                                                            rule_set))

            self._log_step(
            '7.5. Create and run plan')
            self._create_run_and_wait_for_plan(test_constants.PLAN_COMPLETE,
                'Plan to create yum repositories failed')

            msg = (
            '7.6. Testing validation errors with "update" command on '
                 'inherited yum repository items in Applied')
            self._log_step(msg)
            for rule_set in rule_sets:
                fails.extend(
                    self._execute_update_cmd_and_verify_error_msg(
                                                            self.ms1,
                                                            ms_repo1['path'],
                                                            rule_set))

            # Finally check results
            self.assertEquals(fails, [],
                '\nThe following negative validation tests failed:\n {0}'
                .format('\n '.join(fails)))

        finally:
            self._log_step(
            '8. Revert system to its initial state')
            self._remove_installed_packages_and_all_yum_repo_items()
