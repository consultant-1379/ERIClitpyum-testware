# -*- coding: utf-8 -*-
# coding: utf-8

"""
COPYRIGHT Ericsson 2019
The copyright to the computer program(s) herein is the property of
Ericsson Inc. The programs may be used and/or copied only with written
permission from Ericsson Inc. or in accordance with the terms and
conditions stipulated in the agreement/contract under which the
program(s) have been supplied.

@since:     Sept 2015
@author:    Jose Martinez & Jenny Schulze
@summary:   Integration test for story 9743: Given a LITP deployment when a
            LITP deployed yum repo in updated then LITP will detect this and
            update the corresponding yum-repository Item's checksum property.
            Agile: STORY-9743
"""

from litp_generic_test import GenericTest, attr
from litp_cli_utils import CLIUtils
from redhat_cmd_utils import RHCmdUtils
import test_constants
import os


class Story9743(GenericTest):
    """
    Description:
        Given a LITP deployment when a LITP deployed yum repo in updated then
        LITP will detect this and update the corresponding yum-repository
        Item's checksum property.
    """

    def setUp(self):
        """ Setup variables for every test """
        super(Story9743, self).setUp()
        self.ms_node = self.get_management_node_filename()
        self.mn_nodes = self.get_managed_node_filenames()
        self.all_nodes = [self.ms_node] + self.mn_nodes
        self.cli = CLIUtils()
        self.rhcmd = RHCmdUtils()

    def tearDown(self):
        """ Called after every test"""
        super(Story9743, self).tearDown()

    def _create_my_repo(self, repos):
        """
        Function which creates a test repo to be used for these tests
        """
        for repo in repos:
            repo_dir = test_constants.PARENT_PKG_REPO_DIR + repo
            cmd = self.rhc.get_createrepo_cmd(repo_dir, update=False)
            self.assertTrue(
                self.create_dir_on_node(self.ms_node, repo_dir, su_root=True))
            self.run_command(self.ms_node, cmd, su_root=True)
            self._check_yum_repo_is_present(repo_dir)
            self.del_file_after_run(self.ms_node,
                    "/etc/yum.repos.d/{0}.repo".format(repo))

    def _check_yum_repo_is_present(self, repo_path):
        """
        Check that file /repodata/repomd.xml file exist under repo folder
        """
        repmod_path = repo_path + '/repodata/repomd.xml'
        self.assertTrue(self.remote_path_exists(self.ms_node, repmod_path),
            '<{0}> not found'.format(repmod_path))

    def _verify_checksum_update(self, url, repo, old_checksum=None,
            expect_none=False):
        """
        verifies that the checksum property of repo under the given url gets
        updated
        """
        checksum_repo_upd = self.get_props_from_url(self.ms_node,
            "{0}/{1}".format(url, repo),
            "checksum")
        if expect_none:
            self.assertEqual(None, checksum_repo_upd)
        else:
            self.assertTrue(old_checksum != checksum_repo_upd)
            self.assertNotEqual(None, checksum_repo_upd)

    def _verify_no_clean_metadata_task(self, node, repo):
        """
        Verifies that there is no cleanup task in the plan
        """

        plan_output, _, _ = self.execute_cli_showplan_cmd(self.ms_node)
        plan_dict = self.cli.parse_plan_output(plan_output)

        # find update task for node
        expected_desc = 'Clean metadata for yum repository "{0}"'\
                    ' on node "{1}"'.format(repo, node)

        for phase in  plan_dict.keys():
            for task in plan_dict[phase].keys():
                desc = " ".join(plan_dict[phase][task]['DESC'][1:])
                self.assertNotEqual(desc, expected_desc)

    @attr('all', 'revert', 'story9743', 'story9743_tc01')
    def test_01_p_checksum_property_gets_updated_in_local_repo(self):
        """
        @tms_id: litpcds_9743_tc01
        @tms_requirements_id: LITPCDS-9743
        @tms_title: Checksum property gets updated in local repo
        @tms_description: Verify that when the user creates a local repo that
            is inherited in some of the nodes and  and there were updates in
            that repo, the checksum property of the related repo gets updated
            with the md5 of repomd.xml. Also verifies that package updates are
            still possible although the inherited repo is in "updated" state
            (because of the checksum update).
        @tms_test_steps:
            @step: Install test rpm
            @result:test rpm gets installed on MN
            @step: Create a repo in the model
            @result:Repo is created in the mode
            @step: Get the 'checksum' property from the model
            @result:'checksum' property is stored
            @step: Add upgrade item
            @result:upgrade item added
            @step: Update the repo
            @result:repo gets updated
            @step: Create plan
            @result:Plan is created successfully
            @step: Verify that there is no clean metadata task in the plan
            @result:there is no clean metadata task in the plan
            @step: Run plan to update the nodes
            @result:Plan runs successfully
            @step: Verify inherited 'checksum' property was updated
            @result:deployment checksum was updated
            @step: Verify source 'checksum' property was not updated
            @result:source checksum was not updated
            @step:Update the repo
            @result:repo is updated
            @step:Verify no tasks are created if only the checksum is updated
            @result:tasks are created on create plan
        @tms_test_precondition:NA
        @tms_execution_type: Automated
        """

        try:

            self.log("info", "1. Install test rpms")
            install_package = "testpackage-1.0-1.el6.x86_64.rpm"
            update_package = "testpackage-1.1-1.el6.x86_64.rpm"
            update_node = self.mn_nodes[0]
            new_repo = "story9743_test01_1"
            rpm_local_dir = os.path.join(os.path.dirname(__file__),
                    "story9743_rpms")
            self.assertTrue(self.copy_and_install_rpms(update_node,
                [os.path.join(rpm_local_dir, install_package)], "/tmp"))

            # Nodes that will inherit the repo
            nodes = [update_node] + [self.ms_node]

            # Get path in model of software items.
            sw_items = self.find(self.ms_node,
                                 "/software",
                                 "collection-of-software-item")
            self.assertNotEqual([], sw_items)
            sw_items_path = sw_items[0]

            # Sofware items in ms
            ms_sw_items_url = "/ms/items"
            # Software items in nodes
            dep_sw_items = self.find(self.ms_node,
                                 "/deployments",
                                 "ref-collection-of-software-item")
            self.assertNotEqual([], sw_items)
            nodes_sw_items = [item for item in dep_sw_items if "nodes" in item]
            inherit_sw_paths = [ms_sw_items_url] + [nodes_sw_items[0]]

            self.log("info", "2. Create a repo in the model")
            # Create local repo
            self._create_my_repo([new_repo])
            # fill repo
            self.assertTrue(\
                    self.copy_file_to(self.ms_node,
                        os.path.join(rpm_local_dir, update_package),
                        os.path.join(test_constants.PARENT_PKG_REPO_DIR,
                            new_repo),
                        root_copy=True
                        )
                        )

            # Create repo in the model
            sw_items_url = sw_items_path + "/{0}".format(new_repo)
            props = "name='{0}' ms_url_path='/{1}'".format(
                    new_repo, new_repo)
            self.execute_cli_create_cmd(self.ms_node,
                                        sw_items_url,
                                        "yum-repository",
                                        props)
            # Inherit repos in ms and node1
            for path in inherit_sw_paths:
                self.execute_cli_inherit_cmd(self.ms_node,
                    "{0}/{1}".format(path, new_repo),
                    "{0}/{1}".format(sw_items_path, new_repo))

            # Make sure repo client files are removed at
            # the end of test
            for node in nodes:
                self.del_file_after_run(node,
                            "/etc/yum.repos.d/{0}.repo".format(new_repo))
            # Create and run plan
            self.execute_cli_createplan_cmd(self.ms_node)

            self.log("info", "3. Get the 'checksum' property from the model")
            checksum_repos = {}
            for path in inherit_sw_paths:
                checksum_repo = self.get_props_from_url(self.ms_node,
                                    "{0}/{1}".format(path, new_repo),
                                    "checksum")
                checksum_repos[path] = checksum_repo

                # item is in initial state checksum should be present
                self.assertNotEqual(None, checksum_repo)

            self.execute_cli_runplan_cmd(self.ms_node)
            self.assertTrue(self.wait_for_plan_state(self.ms_node,
                test_constants.PLAN_COMPLETE))

            deployment_url = self.find(self.ms_node,
                           "/deployments",
                           "deployment")[0]

            self.log("info", "4. Add upgrade item")
            self.execute_cli_upgrade_cmd(self.ms_node, deployment_url)

            self.log("info", "5. Update the repo")
            cmd = self.rhc.get_createrepo_cmd(
                    test_constants.PARENT_PKG_REPO_DIR + new_repo,
                    update=False)
            self.run_command(self.ms_node, cmd, su_root=True)

            self.log("info", "6. Create plan")
            self.execute_cli_createplan_cmd(self.ms_node)

            self.log("info",
            "7. Verify that there is no clean metadata task in the plan")
            for node in nodes:
                self._verify_no_clean_metadata_task(node, new_repo)

            self.log("info", "8. Run plan to update the nodes")
            self.execute_cli_runplan_cmd(self.ms_node)
            self.assertTrue(self.wait_for_plan_state(self.ms_node,
                test_constants.PLAN_COMPLETE))

            self.log("info", "9. Verify that 'checksum' property in the" +
                     " inherited items was updated")

            for path in inherit_sw_paths:
                self._verify_checksum_update(path, new_repo,
                        checksum_repos[path])

            self.log("info", "10. Verify that 'checksum' property in the" +
                     " source items was not updated")
            self._verify_checksum_update(sw_items_path, new_repo,
                    expect_none=True)

            self.log("info", "11. Update the repo")
            cmd = self.rhc.get_createrepo_cmd(
                    test_constants.PARENT_PKG_REPO_DIR + new_repo,
                    update=False)
            self.run_command(self.ms_node, cmd, su_root=True)

            self.log("info", "12. Verify no tasks are created if only the "\
                    "checksum is updated")
            # Bug 12023
            _, err, _ = self.execute_cli_createplan_cmd(self.ms_node,
                    expect_positive=False)
            self.assertTrue(self.is_text_in_list("DoNothingPlanError    "\
                    "Create plan failed: no tasks were generated", err))
        finally:
            self.remove_rpm_on_node(update_node, "testpackage")

    @attr('all', 'revert', 'story9743', 'story9743_tc03')
    def test_03_n_detect_update_in_repo_fails_detect_base_url_update(self):
        """
        @tms_id: litpcds_9743_tc03
        @tms_requirements_id: LITPCDS-9743
        @tms_title: Detect update in repo fails detect base url update
        @tms_description: Verify that when users run litp create_plan LITP
            fails when trying to calculate the checksum of a deployed repo
            server (whose ms_url_path is specified) that has been updated,
            a suitable exception will be raised and the create_plan will fail.
            Also verifies that when base_url is updated on the source item,
            then the checksum property is deleted on the inherited item.
        @tms_test_steps:
            @step:1. Create repos in the model
            @result: Repo created in the model
            @step:2. Get the 'checksum' properties from the model
            @result: Checksum values are stored
            @step:3. Update one source item to use base_url
            @result: Base_url property is updated on one node
            @step:4. Delete repodata/repomd.xml from one repo
            @result: repodata/repomd.xml is deleted
            @step:5. Verify create plan fails
            @result: Create plan fails with expected error message
            @step:6. Verify that 'checksum' properties in the model are updated
                except the failing one
            @result: 'checksum' properties in the model are updated as expected
            @step:7. Check error messages in logs
            @result: Error messages in logs are correct
        @tms_test_precondition:NA
        @tms_execution_type: Automated
        """

        new_repos = ["story9743-test03-1",
                     "story9743-test03-2",
                     "story9743-test03-3"]

        repo_xml_file = "/repodata/repomd.xml"
        repo_to_fail = new_repos[1]
        repo_to_change_to_base_path = new_repos[-1]

        log_path = test_constants.GEN_SYSTEM_LOG_PATH
        log_len = self.get_file_len(self.ms_node, log_path)

        # Get path in model of software items.
        sw_items = self.find(self.ms_node,
                             "/software",
                             "collection-of-software-item")
        self.assertNotEqual([], sw_items)
        sw_items_path = sw_items[0]

        ms_sw_items_url = "/ms/items"

        self.log("info", "1. Create repos in the model")
        # Create local repo
        self._create_my_repo(new_repos)
        # Create repo in the model
        for new_repo in new_repos:
            sw_items_url = sw_items_path + "/{0}".format(new_repo)
            props = "name='{0}' ms_url_path='/{1}'".format(
                    new_repo, new_repo)
            self.execute_cli_create_cmd(self.ms_node,
                                        sw_items_url,
                                        "yum-repository",
                                        props)
            # The ms inherits from yum repo item
            self.execute_cli_inherit_cmd(self.ms_node,
                    "{0}/{1}".format(ms_sw_items_url, new_repo),
                    "{0}/{1}".format(sw_items_path, new_repo))

            # Make sure repo client files are removed at
            # the end of test
            self.del_file_after_run(self.ms_node,
                    "/etc/yum.repos.d/{0}.repo".format(new_repo))

        # Create and run plan
        self.execute_cli_createplan_cmd(self.ms_node)
        self.execute_cli_runplan_cmd(self.ms_node)
        self.assertTrue(self.wait_for_plan_state(self.ms_node,
            test_constants.PLAN_COMPLETE))

        self.log("info", "2. Get the 'checksum' properties from the model")
        checksums_before = {}
        for new_repo in new_repos:
            checksum_repo = self.get_props_from_url(self.ms_node,
                                "{0}/{1}".format(ms_sw_items_url,
                                                 new_repo),
                                "checksum")
            checksums_before[new_repo] = checksum_repo
        try:
            self.log("info", "3. Update source item to use base_url")
            props = "base_url='http://{0}/{1}' -d ms_url_path".format(
                    self.ms_node, new_repo)
            self.execute_cli_update_cmd(self.ms_node,
                                        "{0}/{1}".format(sw_items_path,
                                            repo_to_change_to_base_path),
                                        props)

            self.log("info", "4. Delete repodata/repomd.xml from one repo")
            cmd_del = "/bin/rm -f {0}{1}{2}".format(
                                            test_constants.PARENT_PKG_REPO_DIR,
                                            repo_to_fail,
                                            repo_xml_file)
            out, err, rc = self.run_command(self.ms_node, cmd_del,
                                            su_root=True, default_asserts=True)
            self.assertEqual(out, [])

            self.log("info", "5. Verify create plan fails")
            _, err, rc = self.execute_cli_createplan_cmd(self.ms_node,
                                                         expect_positive=False)
            self.assertEqual(1, rc)

            expected_error = 'The yum repository referenced by property '\
                             'ms_url_path "/{0}" is not accessible. It is '\
                             'not possible to determine if the repository '\
                             'has been updated'.format(repo_to_fail)

            self.assertTrue(self.is_text_in_list(expected_error, err))
            self.log("info", "6. Verify that 'checksum' properties in the" +
                     " model are updated, except the failing one")
            # Get and verify checksums
            for new_repo in new_repos:
                url = "{0}/{1}".format(ms_sw_items_url, new_repo)
                checksum_repo_upd = self.get_props_from_url(self.ms_node,
                                    url,
                                    "checksum")
                state = self.get_item_state(self.ms_node, url)

                if new_repo == repo_to_fail:
                    self.assertEqual(None, checksum_repo_upd)
                    self.assertEqual("Updated", state)
                elif new_repo == repo_to_change_to_base_path:
                    self.assertEqual(None, checksum_repo_upd)
                    self.assertEqual("Updated", state)
                else:
                    self.assertTrue(
                        checksums_before[new_repo] == checksum_repo_upd)
                    self.assertEqual("Applied", state)

            self.log("info", "7. Check error messages in logs")

            log_msg = ['ERROR: Unable to checksum yum repository "{0}"'.format(
                repo_to_fail)]
            curr_log_pos = self.get_file_len(self.ms_node, log_path)
            test_logs_len = curr_log_pos - log_len

            cmd = self.rhcmd.get_grep_file_cmd(log_path, "ERROR",
                file_access_cmd="tail -n {0}".format(test_logs_len))
            out, _, _ = self.run_command(self.ms_node, cmd,
                    su_root=True, default_asserts=True)

            for log_entry in log_msg:
                self.assertTrue(self.is_text_in_list(log_entry, out))
        finally:
            # revert update from base_url
            self.execute_cli_restoremodel_cmd(self.ms_node)

    @attr('all', 'revert', 'story9743', 'story9743_tc04')
    def test_04_p_remote_repo_checksum_does_not_exist(self):
        """
        @tms_id: litpcds_9743_tc04
        @tms_requirements_id: LITPCDS-9743
        @tms_title: Detect update in repo fails detect base urlupdate
        @tms_description: Verify that when users run litp create_plan and there
            were updates in a remote repo ('base_url' property), the 'checksum'
            properties does not exist
        @tms_test_steps:
            @step: 1. Find Collection-of-software-item under '/software'
            @result:  Item found and stored
            @step: 2. Create a yum repo server
            @result:  yum repo server created
            @step: 3. Create a source LITP yum repo item
            @result:  source LITP yum repo item created
            @step: 4. Inherit the created LITP yum repo item into MS
            @result:  Item is interited on the MS
            @step: 5. Create the plan
            @result:  Plan is created successfully
            @step: 6. Verify that 'checksum' property does not exist on
                inherited LITP yum repo item
            @result:  Property does not exist on inherited item
            @step: 7. Run the plan
            @result:  Plan runs successfully
            @step: 8. Ensure inherited LITP yum repo item repo item is in
                "Applied" state
            @result:  Item is in "Applied" state
            @step: 9. Update the server repo
            @result:  Server repo is updated
            @step:10. Create plan
            @result:  Plan is created successfully
            @step:11. Verify that 'checksum' property does not exist on
                inherited LITP yum repo item
            @result:  Property does not exist on inherited item
        @tms_test_precondition:NA
        @tms_execution_type: Automated
        """

        new_remote_repo = "story9743-test04-remote"

        self.log("info",
        "1. Find Collection-of-software-item under '/software'")
        sw_items = self.find(self.ms_node,
                             "/software",
                             "collection-of-software-item")
        self.assertNotEqual([], sw_items)
        sw_items_path = sw_items[0]

        ms_sw_items_url = "/ms/items"

        self.log("info",
        "2. Create a yum repo server")
        self._create_my_repo([new_remote_repo])

        self.log("info",
        "3. Create a source LITP yum repo item")
        sw_items_url = sw_items_path + "/{0}".format(new_remote_repo)
        props = ("name='{0}' base_url='http://{1}/{2}'"
                 .format(new_remote_repo, self.ms_node, new_remote_repo))

        self.execute_cli_create_cmd(
            self.ms_node, sw_items_url, "yum-repository", props)

        self.log("info",
        "4. Inherit the created LITP yum repo item into MS")
        self.execute_cli_inherit_cmd(self.ms_node,
                "{0}/{1}".format(ms_sw_items_url, new_remote_repo),
                "{0}/{1}".format(sw_items_path, new_remote_repo))

        # Make sure repo client files are removed at the end of test
        self.del_file_after_run(self.ms_node,
                "/etc/yum.repos.d/{0}.repo".format(new_remote_repo))

        self.log("info",
        "5. Create the plan")
        self.execute_cli_createplan_cmd(self.ms_node)

        self.log("info",
        "6. Verify that 'checksum' property does not exist on inherited LITP "
            "yum repo item")
        checksum_repo = self.get_props_from_url(self.ms_node,
                            "{0}/{1}".format(ms_sw_items_url, new_remote_repo),
                            "checksum")
        self.assertTrue(checksum_repo is None)

        self.log("info",
        "7. Run the plan")
        self.execute_cli_runplan_cmd(self.ms_node)
        self.assertTrue(self.wait_for_plan_state(self.ms_node,
            test_constants.PLAN_COMPLETE))

        # ensure repo item is not in initial state
        self.log("info",
        '8. Ensure inherited LITP yum repo item repo item is in "Applied" '
            'state')
        state = self.get_item_state(self.ms_node,
                        "{0}/{1}".format(ms_sw_items_url, new_remote_repo))
        self.assertEqual("Applied", state)

        self.log("info",
        "9. Update the server repo")
        repo_dir = '{0}{1}'.format(test_constants.PARENT_PKG_REPO_DIR,
                                   new_remote_repo)
        cmd = self.rhcmd.get_createrepo_cmd(repo_dir, update=False)
        self.run_command(self.ms_node, cmd, su_root=True, default_asserts=True)

        self.log("info",
        "10. Create plan")
        self.execute_cli_createplan_cmd(self.ms_node, expect_positive=False)

        self.log("info",
        "11. Verify that 'checksum' property does not exist on inherited LITP "
            "yum repo item")
        checksum_repo_upd = self.get_props_from_url(
                        self.ms_node,
                        "{0}/{1}".format(ms_sw_items_url, new_remote_repo),
                        "checksum")
        self.assertTrue(checksum_repo_upd is None)

    @attr('all', 'revert', 'story9743', 'story9743_tc08')
    def test_08_n_no_checksum_property_when_repo_does_not_exist(self):
        """
        @tms_id: litpcds_9743_tc08
        @tms_requirements_id: LITPCDS-9743
        @tms_title: There is no checksum property when repo does not exist
        @tms_description: Verify that when users models a repo that does not in
            the source item nor in the inherited items
        @tms_test_steps:
            @step: 1. Find Collection-of-software-item under '/software'
            @result:  Collection-of-software-item stored
            @step: 2. Create a source LITP yum repo item
            @result:  source LITP yum repo item created
            @step: 3. Inherit the created LITP yum repo item into MS
            @result:  Item is inherited onto the MS
            @step: 4. Create the plan and verify error
            @result:  Create plan fail with expected error
            @step: 5. Check there is no 'checksum' property & state is initial
            @result:  item is as expected
        @tms_test_precondition:NA
        @tms_execution_type: Automated
        """
        new_remote_repo = "story9743-test08"

        self.log("info",
                 "1. Find Collection-of-software-item under '/software'")
        sw_items = self.find(self.ms_node,
                             "/software",
                             "collection-of-software-item")
        sw_items_path = sw_items[0]

        ms_sw_items_url = self.find(self.ms_node,
                             "/ms",
                             "ref-collection-of-software-item")[0]

        modeled_sw_items = [ms_sw_items_url] + [sw_items_path]

        self.log("info", "2. Create a source LITP yum repo item with"\
                 " checksum property set")
        sw_items_url = sw_items_path + "/{0}".format(new_remote_repo)
        props = ("name='{0}' ms_url_path='/{0}' " \
                 "checksum=671b45dc0e44f2864869b8c2fac052f0"
                 .format(new_remote_repo))

        self.execute_cli_create_cmd(
            self.ms_node, sw_items_url, "yum-repository", props)

        self.log("info", "3. Inherit the created LITP yum repo item into MS")
        self.execute_cli_inherit_cmd(self.ms_node,
                "{0}/{1}".format(ms_sw_items_url, new_remote_repo),
                "{0}/{1}".format(sw_items_path, new_remote_repo))

        # Make sure repo config file is removed at the end of test
        self.del_file_after_run(self.ms_node,
                "/etc/yum.repos.d/{0}.repo".format(new_remote_repo))

        self.log("info", "4. Create the plan and verify error")
        _, err, _ = self.execute_cli_createplan_cmd(self.ms_node,
                                                    expect_positive=False)

        expected_error = "ValidationError    Create plan failed: The yum "\
                         "repository referenced by property ms_url_path "\
                         "\"/{0}\" is not accessible. It is not possible "\
                         "to determine if the repository has been "\
                         "updated".format(new_remote_repo)

        self.assertTrue(self.is_text_in_list(expected_error, err))

        self.log("info", "5. Check there is no 'checksum' property and item "
                 "in 'initial' state")
        for sw_item in modeled_sw_items:
            checksum_repo = self.get_props_from_url(self.ms_node,
                                        "{0}/{1}".format(sw_item,
                                                         new_remote_repo),
                                        "checksum")

            self.assertEqual(None, checksum_repo)

            state = self.get_item_state(self.ms_node,
                                        "{0}/{1}".format(sw_item,
                                                         new_remote_repo))
            self.assertEqual("Initial", state)
