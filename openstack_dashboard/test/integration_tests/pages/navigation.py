# coding:utf-8
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

import importlib
import types


class Navigation(object):
    """Provide basic navigation among pages.

    * allows navigation among pages without need to import pageobjects
    * shortest path possible should be always used for navigation to
      specific page as user would navigate in the same manner
    * go_to_*some_page* method respects following pattern:
      * go_to_{sub_menu}_{pagename}page
    * go_to_*some_page* methods are generated at runtime at module import
    * go_to_*some_page* method returns pageobject
    * pages must be located in the correct directories for the navigation
      to work correctly
    * pages modules and class names must respect following pattern
      to work correctly with navigation module:
      * module name consist of menu item in lower case without spaces and '&'
      * page class begins with capital letter and ends with 'Page'

    Examples:
        In order to go to Project/Compute/Overview page, one would have to call
        method go_to_compute_overviewpage()

        In order to go to Admin/System/Overview page, one would have to call
        method go_to_system_overviewpage()

    """
    # constants
    MAX_SUB_LEVEL = 4
    MIN_SUB_LEVEL = 2
    SIDE_MENU_MAX_LEVEL = 3
    PAGES_IMPORT_PATH = "openstack_dashboard.test.integration_tests.pages.%s"
    ITEMS = "__items__"

    PAGE_STRUCTURE = \
        {
            "Project":
                {
                    "Compute":
                        {
                            "Access & Security":
                                {
                                    ITEMS:
                                        (
                                            "Security Groups",
                                            "Key Pairs",
                                            "Floating IPs",
                                            "API Access"
                                        ),
                                },
                            "Volumes":
                                {
                                    ITEMS:
                                        (
                                            "Volumes",
                                            "Volume Snapshots"
                                        )
                                },
                            ITEMS:
                                (
                                    "Overview",
                                    "Instances",
                                    "Images",
                                )
                        },
                    "Network":
                        {
                            ITEMS:
                                (
                                    "Network Topology",
                                    "Networks",
                                    "Routers"
                                )
                        },
                    "Object Store":
                        {
                            ITEMS:
                                (
                                    "Containers",
                                )
                        },
                    "Data Processing":
                        {
                            ITEMS:
                                (
                                    "Clusters",
                                    "Cluster Templates",
                                    "Node Group Templates",
                                    "Job Executions",
                                    "Jobs",
                                    "Job Binaries",
                                    "Data Sources",
                                    "Image Registry",
                                    "Plugins"
                                ),
                        },
                    "Orchestration":
                        {
                            ITEMS:
                                (
                                    "Stacks",
                                )
                        }
                },
            "Admin":
                {
                    "System":
                        {
                            "Resource Usage":
                                {
                                    ITEMS:
                                        (
                                            "Daily Report",
                                            "Stats"
                                        )
                                },
                            "System info":
                                {
                                    ITEMS:
                                        (
                                            "Services",
                                            "Compute Services",
                                            "Block Storage Services",
                                            "Network Agents",
                                            "Default Quotas"
                                        )
                                },
                            "Volumes":
                                {
                                    ITEMS:
                                        (
                                            "Volumes",
                                            "Volume Types",
                                            "Volume Snapshots"
                                        )
                                },
                            ITEMS:
                                (
                                    "Overview",
                                    "Hypervisors",
                                    "Host Aggregates",
                                    "Instances",
                                    "Flavors",
                                    "Images",
                                    "Networks",
                                    "Routers"
                                )
                        },
                },
            "Settings":
                {
                    ITEMS:
                        (
                            "User Settings",
                            "Change Password"
                        )
                },
            "Identity":
                {
                    ITEMS:
                        (
                            "Projects",
                            "Users",
                            "Groups",
                            "Domains",
                            "Roles"
                        )
                }
        }

    TRANSLATE_DICT = {"Project": u'项目',
                      "Compute": u'Compute',
                      "Access & Security": u'访问 & 安全',
                      "Security Groups": u'',
                      "Key Pairs": u'',
                      "Floating IPs": u'',
                      "API Access": u'',
                      "Volumes": u'',
                      "Volume Snapshots": u'',
                      "Overview": u'',
                      "Instances": u'',
                      "Images": u'镜像',
                      "Network": u'网络',
                      "Network Topology": u'',
                      "Networks": u'网络',
                      "Routers": u'',
                      "Object Store": u'',
                      "Containers": u'',
                      "Data Processing": u'',
                      "Clusters": u'',
                      "Cluster Templates": u'',
                      "Node Group Templates": u'',
                      "Job Executions": u'',
                      "Jobs": u'',
                      "Job Binaries": u'',
                      "Data Sources": u'',
                      "Image Registry": u'',
                      "Plugins": u'',
                      "Orchestration": u'',
                      "Stacks": u'',
                      "Admin": u'',
                      "System": u'',
                      "Resource Usage": u'',
                      "Daily Report": u'',
                      "Stats": u'',
                      "System info": u'',
                      "Services": u'',
                      "Compute Services": u'',
                      "Block Storage Services": u'',
                      "Network Agents": u'',
                      "Default Quotas": u'',
                      "Volume Types": u'',
                      "Hypervisors": u'',
                      "Host Aggregates": u'',
                      "Flavors": u'',
                      "Settings": u'',
                      "User Settings": u'',
                      "Change Password": u'',
                      "Identity": u'',
                      "Projects": u'',
                      "Users": u'',
                      "Groups": u'',
                      "Domains": u'',
                      "Roles": u'',}

    # 将英语翻译成中文
    @classmethod
    def _eng_to_chs(cls, word):
        return cls.TRANSLATE_DICT[word]

    # protected methods
    def _go_to_page(self, path, page_class=None):
        """Go to page specified via path parameter.

         * page_class parameter overrides basic process for receiving
           pageobject
        """
        path_len = len(path)
        if path_len < self.MIN_SUB_LEVEL or path_len > self.MAX_SUB_LEVEL:
            raise ValueError("Navigation path length should be in the interval"
                             " between %s and %s, but its length is %s" %
                             (self.MIN_SUB_LEVEL, self.MAX_SUB_LEVEL,
                              path_len))

        if path_len == self.MIN_SUB_LEVEL:
            # menu items that do not contain second layer of menu
            if path[0] == "Settings":
                self._go_to_settings_page(path[1])
            else:
                self._go_to_side_menu_page([path[0], None, path[1]])
        else:
            # side menu contains only three sub-levels
            # 英语使用这个
            # self._go_to_side_menu_page(path[:self.SIDE_MENU_MAX_LEVEL])
            # 中文使用这个
            menu_items = []
            for i in path[:self.SIDE_MENU_MAX_LEVEL]:
                menu_items.append(Navigation._eng_to_chs(i))
            self._go_to_side_menu_page(menu_items)

        if path_len == self.MAX_SUB_LEVEL:
            # apparently there is tabbed menu,
            #  because another extra sub level is present
            self._go_to_tab_menu_page(path[self.MAX_SUB_LEVEL - 1])

        # if there is some nonstandard pattern in page object naming
        return self._get_page_class(path, page_class)(self.driver, self.conf)

    def _go_to_tab_menu_page(self, item_text):
        self.driver.find_element_by_link_text(item_text).click()

    def _go_to_settings_page(self, item_text):
        """Go to page that is located under the settings tab."""
        self.topbar.user_dropdown_menu.click_on_settings()
        self.navaccordion.click_on_menu_items(third_level=item_text)

    def _go_to_side_menu_page(self, menu_items):
        """Go to page that is located in the side menu (navaccordion)."""
        self.navaccordion.click_on_menu_items(*menu_items)

    def _get_page_cls_name(self, filename):
        """Gather page class name from path.

         * take last item from path (should be python filename
           without extension)
         * make the first letter capital
         * append 'Page'
         """
        cls_name = "".join((filename.capitalize(), "Page"))
        return cls_name

    def _get_page_class(self, path, page_cls_name):

        # last module name does not contain '_'
        final_module = self.unify_page_path(path[-1],
                                            preserve_spaces=False)
        page_cls_path = ".".join(path[:-1] + (final_module,))
        page_cls_path = self.unify_page_path(page_cls_path)
        # append 'page' as every page module ends with this keyword
        page_cls_path += "page"

        page_cls_name = page_cls_name or self._get_page_cls_name(final_module)

        # return imported class
        module = importlib.import_module(self.PAGES_IMPORT_PATH %
                                         page_cls_path)
        return getattr(module, page_cls_name)

    class GoToMethodFactory(object):
        """Represent the go_to_some_page method."""

        METHOD_NAME_PREFIX = "go_to_"
        METHOD_NAME_SUFFIX = "page"
        METHOD_NAME_DELIMITER = "_"

        # private methods
        def __init__(self, path, page_class=None):
            self.path = path
            self.page_class = page_class
            self._name = self._create_name()

        def __call__(self, *args, **kwargs):
            return Navigation._go_to_page(args[0], self.path, self.page_class)

        # protected methods
        def _create_name(self):
            """Create method name.

            * consist of 'go_to_subsubmenu_menuitem_page'
            """
            submenu, menu_item = self.path[-2:]

            name = "".join((self.METHOD_NAME_PREFIX, submenu,
                            self.METHOD_NAME_DELIMITER, menu_item,
                            self.METHOD_NAME_SUFFIX))
            name = Navigation.unify_page_path(name, preserve_spaces=False)
            return name

        # properties
        @property
        def name(self):
            return self._name

    # classmethods
    @classmethod
    def _initialize_go_to_methods(cls):
        """Create all navigation methods based on the PAGE_STRUCTURE."""

        def rec(items, sub_menus):
            if isinstance(items, dict):
                for sub_menu, sub_item in items.iteritems():
                    rec(sub_item, sub_menus + (sub_menu,))
            elif isinstance(items, tuple):
                # exclude ITEMS element from sub_menus
                paths = (sub_menus[:-1] + (menu_item,) for menu_item in items)
                for path in paths:
                    cls._create_go_to_method(path)

        rec(cls.PAGE_STRUCTURE, ())

    @classmethod
    def _create_go_to_method(cls, path, class_name=None):
        go_to_method = Navigation.GoToMethodFactory(path, class_name)
        inst_method = types.MethodType(go_to_method, None, Navigation)
        setattr(Navigation, inst_method.name, inst_method)

    @classmethod
    def unify_page_path(cls, path, preserve_spaces=True):
        """Unify path to page.

        Replace '&' in path with 'and', remove spaces (if not specified
        otherwise) and convert path to lower case.
        """
        path = path.replace("&", "and")
        path = path.lower()
        if preserve_spaces:
            path = path.replace(" ", "_")
        else:
            path = path.replace(" ", "")
        return path


Navigation._initialize_go_to_methods()
