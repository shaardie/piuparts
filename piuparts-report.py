#!/usr/bin/python
#
# Copyright 2005 Lars Wirzenius (liw@iki.fi)
# Copyright 2009 Holger Levsen (holger@layer-acht.org)
# 
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.
# 
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details.
# 
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA


"""Create HTML reports of piuparts log files

Lars Wirzenius <liw@iki.fi>
"""


import os
import sys
import time
import logging
import ConfigParser
import urllib
import shutil
import string
import re

# if python-rpy ain't installed, we don't draw fancy graphs
try:
  from rpy import *
except:
  pass

import piupartslib


CONFIG_FILE = "/etc/piuparts/piuparts.conf"


HTML_HEADER = """
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
 <html><head><meta http-equiv="Content-Type" content="text/html; charset=utf-8">
  <title>piuparts.debian.org / piuparts.cs.helsinki.fi</title>
  <link type="text/css" rel="stylesheet" href="/style.css">
  <link rel="shortcut icon" href="/favicon.ico">
 </head>

 <body>
 <div id="header">
   <h1 class="header">
    <a href="http://www.debian.org/">
     <img src="http://piuparts.debian.org/images/openlogo-nd-50.png" border="0" hspace="0" vspace="0" alt=""></a>
    <a href="http://www.debian.org/">
     <img src="http://piuparts.debian.org/images/debian.png" border="0" hspace="0" vspace="0" alt="Debian Project"></a>
    Quality Assurance
   </h1>
   <div id="obeytoyourfriend">Policy is your friend. Trust the Policy. Love the Policy. Obey the Policy.</div>
 </div>
 <hr>
<div id="main">
<table class="containertable">
 <tr class="containerrow" valign="top">
  <td class="containercell">
   <table class="lefttable">
    <tr class="titlerow">
     <td class="titlecell">
      General information
     </td>
    </tr>
    <tr class="normalrow">
     <td class="contentcell">
      <a href="/">Overview</a>
     </td>
    </tr>
      <td class="contentcell">
      <a href="http://wiki.debian.org/piuparts" target="_blank">About</a>
     </td>
    </tr>
    <tr class="normalrow">
     <td class="contentcell">
      <a href="http://wiki.debian.org/piuparts/FAQ" target="_blank">FAQ</a> 
     </td>
     </tr>     
    <tr class="normalrow">
     <td class="contentcell">
      <a href="http://bugs.debian.org/piuparts" target="_blank">Bugs</a> / <a href="http://svn.debian.org/viewsvn/piuparts/trunk/TODO" target="_blank">ToDo</a>
     </td>
    </tr>     
    <tr class="titlerow">
     <td class="titlecell">
      Documentation
     </td>
    </tr>
    <tr class="normalrow">
     <td class="contentcell">
      <a href="/doc/README.html" target="_blank">piuparts README</a>
     </td>
    </tr>
    <tr class="titlerow">
    <tr class="normalrow">
     <td class="contentcell">
      <a href="/doc/piuparts.1.html" target="_blank">piuparts manpage</a>
     </td>
    </tr>
    <tr class="normalrow">
     <td class="contentcell">
      <a href="http://www.debian.org/doc/debian-policy/" target="_blank">Debian policy</a>
     </td>
    </tr>
    <tr class="titlerow">
     <td class="alerttitlecell">
      Available reports
     </td>
    </tr>
    <tr>
     <td class="contentcell">
      <a href="http://bugs.debian.org/cgi-bin/pkgreport.cgi?tag=piuparts;users=debian-qa@lists.debian.org&archive=both" target="_blank">Bugs filed</a> 
     </td>
    </tr>     
    $section_navigation
    <tr class="titlerow">
     <td class="titlecell">
      Other Debian QA efforts
     </td>
    </tr>
    <tr class="normalrow">
     <td class="contentcell">
      <a href="http://edos.debian.net" target="_blank">EDOS tools</a>
     </td>
    </tr>
    <tr class="normalrow">
     <td class="contentcell">
      <a href="http://lintian.debian.org" target="_blank">Lintian</a>
     </td>
    </tr>
    <tr class="normalrow">
     <td class="contentcell">
      <a href="http://packages.qa.debian.org" target="_blank">Package Tracking System</a>
     </td>
    <tr class="normalrow">
     <td class="contentcell">
      <a href="http://udd.debian.org" target="_blank">Ultimate Debian Database</a>
     </td>
    </tr>
    <tr class="titlerow">
     <td class="titlecell">
      Last update
     </td>
    </tr>
    <tr class="normalrow">
     <td class="lastcell">
      $time
     </td>
    </tr>
   </table>
  </td>
  <td class="containercell">
"""


HTML_FOOTER = """
  </td>
 </tr>
</table> 
</div>
 <hr>
 <div id="footer">
  <div>
   piuparts was written by <a href="mailto:liw@iki.fi">Lars Wirzenius</a> and is now maintained by 
   <a href="mailto:holger@debian.org">Holger Levsen</a>,  
   <a href="mailto:luk@debian.org">Luk Claes</a> and <a href="http://qa.debian.org/" target="_blank">others</a>. 
   GPL2 <a href="http://packages.debian.org/changelogs/pool/main/p/piuparts/current/copyright" target="_blank">licenced</a>.
   Weather icons are from the <a href="http://tango.freedesktop.org/Tango_Icon_Library" target="_blank">Tango Icon Library</a>.
   <a href="http://validator.w3.org/check?uri=referer">
    <img border="0" src="/images/valid-html401.png" alt="Valid HTML 4.01!" height="15" width="80" valign="middle">
   </a>
   <a href="http://jigsaw.w3.org/css-validator/check/referer">
    <img border="0" src="/images/w3c-valid-css.png" alt="Valid CSS!"  height="15" width="80" valign="middle">
   </a>
  </div>
 </div>
</body>
</html>
"""


LOG_LIST_BODY_TEMPLATE = """
   <table class="righttable">
    <tr class="titlerow">
     <td class="$title_style" colspan="2">
      $title in $section
     </td>
    </tr>
    <tr class="normalrow">
     <td class="contentcell2" colspan="2">
      $preface
      The list has $count packages, with $versioncount total versions.
     </td>
    </tr>
    $logrows
   </table>
"""


STATE_BODY_TEMPLATE = """
   <table class="righttable">
    <tr class="titlerow">
     <td class="alerttitlecell">
      Packages in state "$state" in $section
     </td>
    </tr>
    <tr class="normalrow">
     <td class="contentcell2">
      <ul>
       $list
      </ul>
     </td>
    </tr>
   </table>
"""


SECTION_INDEX_BODY_TEMPLATE = """
   <table class="righttable">
    <tr class="titlerow">
     <td class="titlecell" colspan="3">
      $section statistics
     </td>
    </tr>
    <tr class="normalrow">
     <td class="contentcell2" colspan="3">
      $description
     </td>
    </tr>
    <tr class="titlerow">
     <td class="alerttitlecell" colspan="3">
      Packages per state
     </td>
    </tr>
    $tablerows
    <tr class="titlerow">
     <td class="titlecell" colspan="3">
      URL to packages file(s)
     </td>
    </tr>
     <tr class="normalrow">
     <td class="contentcell2" colspan="3">
      <code>$packagesurl</code>
     </td>
    </tr>
   </table>
"""

SOURCE_PACKAGE_BODY_TEMPLATE = """
   <table class="righttable">
    $rows
   </table>
"""

ANALYSIS_BODY_TEMPLATE = """
   <table class="righttable">
    $rows
   </table>
"""

# this template is normally replaced with from $htdocs
INDEX_BODY_TEMPLATE = """
   <table class="righttable">
    <tr class="titlerow">
     <td class="titlecell">
      piuparts
     </td>
    </tr>
    <tr class="normalrow">
     <td class="contentcell2">
      piuparts is a tool for testing that .deb packages can be installed, upgraded, and removed without problems. The
      name, a variant of something suggested by Tollef Fog Heen, is short for "<em>p</em>ackage <em>i</em>nstallation, 
      <em>up</em>grading <em>a</em>nd <em>r</em>emoval <em>t</em>esting <em>s</em>uite". 
     </td>
    </tr>
    <tr class="normalrow">
     <td class="contentcell2">
      It does this by  creating a minimal Debian installation in a chroot, and installing,
      upgrading, and removing packages in that environment, and comparing the state of the directory tree before and after. 
      piuparts reports any files that have been added, removed, or modified during this process.
     </td>
    </tr>
    <tr class="normalrow">
     <td class="contentcell2">
      piuparts is meant as a quality assurance tool for people who create .deb packages to test them before they upload them to the Debian package archive. See the <a href="/doc/README.html" target="_blank">piuparts README</a> for a quick intro and then read the <a href="/doc/piuparts.1.html" target="_blank">piuparts manpage</a> to learn about all the fancy options!
     </td>
    </tr>
    </table>
"""


title_by_dir = {
    "pass": "PASSED piuparts logs",
    "fail": "Failed UNREPORTED piuparts logs",
    "bugged": "Failed REPORTED piuparts logs",
    "fixed": "Failed and FIXED packages",
    "reserved": "RESERVED packages",
    "untestable": "UNTESTABLE packages",
}


desc_by_dir = {
    "pass": "Log files for packages that have PASSED testing.",
    "fail": "Log files for packages that have FAILED testing. " +
            "Bugs have not yet been reported.",
    "bugged": "Log files for packages that have FAILED testing. " +
              "Bugs have been reported, but not yet fixed.",
    "fixed": "Log files for packages that have FAILED testing, but for " +
             "which a fix has been made.",
    "reserved": "Packages that are RESERVED for testing on a node in a " +
                "distributed piuparts network.",
    "untestable": "Log files for packages that have are UNTESTABLE with " +
                  "piuparts at the current time.",
}

state_by_dir = {
    "pass": "successfully-tested",
    "fail": "failed-testing",
    "bugged": "failed-testing",
    "fixed": "fix-not-yet-tested",
    "reserved": "waiting-to-be-tested",
    "untestable": "dependency-cannot-be-tested",
}

linktarget_by_template = {
    "command_not_found_error.tpl": "due to a 'command not found' error",
    "files_in_usr_local_error.tpl": "due to files in /usr/local",
    "overwrite_other_packages_files_error.tpl": "due to overwriting other packages files",
    "owned_files_after_purge_error.tpl": "due to owned files existing after purge",
    "owned_files_by_many_packages_error.tpl": "due to owned files by many packages",
    "processes_running_error.tpl": "due to leaving processes running behind",
    "unowned_files_after_purge_error.tpl": "due to unowned files after purge",
    "unknown_failures.tpl": "unclassified failures",
    "command_not_found_issue.tpl": "but logfile contains 'command not found'",
}


class Config(piupartslib.conf.Config):

    def __init__(self, section="report"):
        self.section = section
        piupartslib.conf.Config.__init__(self, section,
            {
                "sections": "report",
                "output-directory": "html",
                "packages-url": None,
                "sources-url": None,
                "master-directory": ".",
                "description": "",
            }, "")


def setup_logging(log_level, log_file_name):
    logger = logging.getLogger()
    logger.setLevel(log_level)

    formatter = logging.Formatter(fmt="%(asctime)s %(message)s",
                                  datefmt="%H:%M")

    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    if log_file_name:
        handler = logging.FileHandler(log_file_name)
        logger.addHandler(handler)


def html_protect(str):
    str = "&amp;".join(str.split("&"))
    str = "&lt;".join(str.split("<"))
    str = "&gt;".join(str.split(">"))
    str = "&#34;".join(str.split('"'))
    str = "&#39;".join(str.split("'"))
    return str


def emphasize_reason(reason):
    if reason in ("unknown", "failed-testing", "circular-dependency", "dependency-failed-testing", "dependency-does-not-exist", "cannot-be-tested"):
      reason = "<em>"+reason+"</em>"
    return reason


def source_subdir(source):
    if source[:3] == "lib":
      return source[:4]
    else:
      return source[:1]


def maintainer_subdir(maintainer):
    return maintainer.lower()[:1]


def find_files_with_suffix(dir,suffix):
    files=[name for name in os.listdir(dir) if name.endswith(suffix)]
    subdirs=os.listdir(dir)
    for subdir in subdirs:
      if os.path.isdir(os.path.join(dir,subdir)):
        for name_in_subdir in os.listdir(os.path.join(dir,subdir)):
          if name_in_subdir.endswith(suffix):
            files += [os.path.join(dir,subdir, name_in_subdir)]
    # sort by age
    content = {}
    for file in files:
      content[file] = os.path.getmtime(os.path.join(dir,file))
    # Sort keys, based on time stamps
    files = content.keys()
    files.sort(lambda x,y: cmp(content[x],content[y]))
    return files

def update_file(source, target):
    if os.path.exists(target):
        aa = os.stat(source)
        bb = os.stat(target)
        if aa.st_size == bb.st_size and aa.st_mtime < bb.st_mtime:
            return
    shutil.copyfile(source, target)


def copy_logs(logs_by_dir, output_dir):
    for dir in logs_by_dir:
        fulldir = os.path.join(output_dir, dir)
        if not os.path.exists(fulldir):
            os.makedirs(fulldir)
        for basename in logs_by_dir[dir]:
            source = os.path.join(dir, basename)
            target = os.path.join(fulldir, basename)
            update_file(source, target)

def remove_old_logs(logs_by_dir, output_dir):
    for dir in logs_by_dir:
        fulldir = os.path.join(output_dir, dir)
        if os.path.exists(fulldir):
            for basename in os.listdir(fulldir):
                if basename not in logs_by_dir[dir]:
                    os.remove(os.path.join(fulldir, basename))


def write_file(filename, contents):
    f = file(filename, "w")
    f.write(contents)
    f.close()


def append_file(filename, contents):
    f = file(filename, "a")
    f.write(contents)
    f.close()

def read_file(filename):
    f = file(filename, "r")
    l = f.readlines()
    f.close()
    return l

def create_section_navigation(section_names,current_section="sid"):
    tablerows = ""
    for section in section_names:
        tablerows += ("<tr class=\"normalrow\"><td class=\"contentcell\"><a href='/%s'>%s</a></td></tr>\n") % \
                          (html_protect(section), html_protect(section))
    tablerows += "<tr><td class=\"contentcell\"><a href=\"/%s/source/\">by source package</a></td></tr>" % current_section
    tablerows += "<tr><td class=\"contentcell\"><a href=\"/%s/maintainer/\">by maintainer / uploader</a></td></tr>" % current_section
    return tablerows;

def get_email_address(maintainer):
    email = "INVALID maintainer address: %s" % (maintainer)
    try:
      m = re.match(r"(.+)(<)(.+@.+)(>)", maintainer)
      email = m.group(3)
    except:
      pass
    return email


class Section:

    def __init__(self, section):
        self._config = Config(section=section)
        self._config.read(CONFIG_FILE)
        logging.debug("-------------------------------------------")
        logging.debug("Running section " + self._config.section)
        logging.debug("Loading and parsing Packages file")

        logging.info("Fetching %s" % self._config["packages-url"])
        packages_file = piupartslib.open_packages_url(self._config["packages-url"])
        self._binary_db = piupartslib.packagesdb.PackagesDB()
        self._binary_db.read_packages_file(packages_file)
        packages_file.close()

        if self._config["sources-url"]:
          logging.info("Fetching %s" % self._config["sources-url"])
          sources_file = piupartslib.open_packages_url(self._config["sources-url"])
          self._source_db = piupartslib.packagesdb.PackagesDB()
          self._source_db.read_packages_file(sources_file)
          sources_file.close()

    def write_log_list_page(self, filename, title, preface, logs):
        packages = {}
        for pathname, package, version in logs:
            packages[package] = packages.get(package, []) + [(pathname, version)]

        names = packages.keys()
        names.sort()
        lines = []
        version_count = 0
        for package in names:
            versions = []
            for pathname, version in packages[package]:
                version_count += 1
                versions.append("<a href=\"%s\">%s</a>" % 
                                (html_protect(pathname), 
                                 html_protect(version)))
            line = "<tr class=\"normalrow\"><td class=\"contentcell2\">%s</td><td class=\"contentcell2\">%s</td></tr>" % \
                                (html_protect(package), 
                                 ", ".join(versions))
            lines.append(line)

        if "FAIL" in preface:
          title_style="alerttitlecell"
        else:
          title_style="titlecell"

        htmlpage = string.Template(HTML_HEADER + LOG_LIST_BODY_TEMPLATE + HTML_FOOTER)
        f = file(filename, "w")
        f.write(htmlpage.safe_substitute( {
                    "section_navigation": create_section_navigation(self._section_names,self._config.section),
                    "time": time.strftime("%Y-%m-%d %H:%M %Z"),
                    "title": html_protect(title),
                    "section": html_protect(self._config.section),
                    "title_style": title_style,
                    "preface": preface,
                    "count": len(packages),
                    "versioncount": version_count,
                    "logrows": "".join(lines)
                }))
        f.close()


    def print_by_dir(self, output_directory, logs_by_dir):
        for dir in logs_by_dir:
            list = []
            for basename in logs_by_dir[dir]:
                assert basename.endswith(".log")
                assert "_" in basename
                package, version = basename[:-len(".log")].split("_")
                list.append((os.path.join(dir, basename), package, version))
            self.write_log_list_page(os.path.join(output_directory, dir + ".html"),
                                title_by_dir[dir], 
                                desc_by_dir[dir], list)

    def find_links_to_logs(self, package_name, dirs, logs_by_dir):
        links = []
        for dir in dirs:
          for basename in logs_by_dir[dir]:
            if basename.startswith(package_name+"_") and basename.endswith(".log"):
              package, version = basename[:-len(".log")].split("_")
              links.append("<a href=\"/%s\">%s</a>" % (os.path.join(self._config.section, dir, basename),html_protect(version)))
        return links

    def link_to_maintainer_summary(self, maintainer):
	email = get_email_address(maintainer)
        return "<a href=\"/%s/maintainer/%s/%s.html\">%s</a>" % (self._config.section,maintainer_subdir(email),email,html_protect(maintainer))

    def link_to_uploaders(self, uploaders):
        link = ""
        for uploader in uploaders.split(", "):
          link += self.link_to_maintainer_summary(uploader)+", "
        return link[:-2]

    def link_to_source_summary(self, package_name):
        source_name = self._binary_db.get_control_header(package_name, "Source")
        link = "<a href=\"/%s/source/%s\">%s</a>" % (
                self._config.section,
                source_subdir(source_name)+"/"+source_name+".html",
                html_protect(package_name))
        return link

    def link_to_state_page(self, section, package_name, link_target):
        state = self._binary_db.state_by_name(package_name)
        if state != "unknown":
            link = "<a href=\"/%s/%s\">%s</a>" % (
                section,
                "state-"+state+".html"+"#"+package_name,
                link_target)
        else:
          if link_target == package_name:
            link = html_protect(package_name)
          else:
            link = "unknown-package-or-udeb"

        return link

    def links_to_logs(self, package_name, state, logs_by_dir):
        link = "N/A"
        dirs = ""

        if state == "successfully-tested":
          dirs = ["pass", "fixed"]
        elif state == "failed-testing":
          dirs = ["fail", "bugged", "untestable"]

        if dirs != "":
          links = self.find_links_to_logs (package_name, dirs, logs_by_dir)
          link = ", ".join(links)

        if "/bugged/" in link:
          link += " - <a href=\"http://bugs.debian.org/cgi-bin/pkgreport.cgi?package="+package_name+"\" target=\"_blank\" class=\"bugged\">&nbsp;bug filed&nbsp;</a>"

        return link

    def write_counts_summary(self):
        logging.debug("Writing counts.txt")    
        header = "date"
        current_day = "%s" % time.strftime("%Y%m%d")
        counts = current_day
        total = 0
        for state in self._binary_db.get_states():
            count = len(self._binary_db.get_packages_in_state(state))
            header += ", %s" % state
            counts += ", %s" % count
            logging.debug("%s: %s" % (state, count))
            total += count
        header += "\n"       
        counts += "\n"       

        countsfile = os.path.join(self._output_directory, "counts.txt") 
        if not os.path.isfile(countsfile):
          logging.debug("writing new file: %s" % countsfile) 
          write_file(countsfile, header)
        else:
          last_line = read_file(countsfile)[-1]
        if not current_day in last_line:
          append_file(countsfile, counts)
          logging.debug("appending line: %s" % counts) 
        return total


    def merge_maintainer_templates(self, templates):
        for maint_tpl in templates:
            tpl = os.path.join(self._output_directory,"maintainer",maintainer_subdir(maint_tpl),maint_tpl)
            lines = read_file(tpl)
            rows = ""
            for line in lines:
              state, count, packages = line.split(",")
              if packages == "none\n":
                links = "&nbsp;"
              else:
                links = ""
                for package in packages.split(" "):
                  links += "<a href=\"#%s\">%s</a> " % (package,package)
              rows += "<tr class=\"normalrow\"><td class=\"labelcell\">%s:</td><td class=\"contentcell2\">%s</td><td class=\"contentcell2\" colspan=\"4\">%s</td></tr>" % \
                       (state, count, links)
            os.unlink(tpl)
            template_path = tpl[:-len("_tpl")]

            for state in ("fail","unkn","pass"):
                filename = template_path+"_"+state
                if os.path.isfile(filename):
                     f = file(filename, "r")
                     rows += file.read(f)
                     f.close()
                     os.unlink(filename)
     
            htmlpage = string.Template(HTML_HEADER + SOURCE_PACKAGE_BODY_TEMPLATE + HTML_FOOTER)
            filename = template_path+".html"
            f = file(filename, "w")
            f.write(htmlpage.safe_substitute( {
               "section_navigation": create_section_navigation(self._section_names,self._config.section),
               "time": time.strftime("%Y-%m-%d %H:%M %Z"),
               "rows": rows,
             }))
            f.close()

    def create_source_summary (self, source, logs_by_dir):
        source_version = self._source_db.get_control_header(source, "Version")
        binaries = self._source_db.get_control_header(source, "Binary")
        maintainer = self._source_db.get_control_header(source, "Maintainer")
        uploaders = self._source_db.get_control_header(source, "Uploaders")

        success = True
        failed = False
        binaryrows = ""
        for binary in binaries.split(", "):
          state = self._binary_db.state_by_name(binary)
          current_version = self._source_db.get_control_header(source, "Version")
          if state != "circular-dependency" and not "waiting" in state and "dependency" in state:
            state_style="lightalertlabelcell"
          elif state == "failed-testing":
            state_style="lightlabelcell"
          else:
            state_style="labelcell"
          binaryrows += "<tr class=\"normalrow\"><td class=\"labelcell\">Binary:</td><td class=\"contentcell2\">%s</td><td class=\"%s\">piuparts-result:</td><td class=\"contentcell2\">%s %s</td><td class=\"labelcell\">Version:</td><td class=\"contentcell2\">%s</td></tr>" %  (binary, state_style, self.link_to_state_page(self._config.section,binary,state), self.links_to_logs(binary, state, logs_by_dir), html_protect(current_version))
          if state not in ("successfully-tested", "essential-required"):
            success = False
          if state in ("failed-testing", "dependency-does-not-exist", "cannot-be-tested"):
            failed = True

        source_state="unknown"
        if success: source_state="<img src=\"/images/sunny.png\">"
        if failed:  source_state="<img src=\"/images/weather-severe-alert.png\">"

        sourcerows = "<tr class=\"titlerow\"><td class=\"titlecell\" colspan=\"6\" id=\"%s\">%s in %s</td></tr>" % (source, source, self._config.section)
        sourcerows += "<tr class=\"normalrow\"><td class=\"labelcell\">Source:</td><td class=\"contentcell2\"><a href=\"http://packages.qa.debian.org/%s\" target=\"_blank\">%s</a></td><td class=\"labelcell\">piuparts summary:</td><td class=\"contentcell2\">%s</td><td class=\"labelcell\">Version:</td><td class=\"contentcell2\">%s</td></tr>" % (source, html_protect(source), source_state, html_protect(source_version))
        sourcerows += "<tr class=\"normalrow\"><td class=\"labelcell\">Maintainer:</td><td class=\"contentcell2\" colspan=\"5\">%s</td></tr>" % (self.link_to_maintainer_summary(maintainer))
        if uploaders:
          sourcerows += "<tr class=\"normalrow\"><td class=\"labelcell\">Uploaders:</td><td class=\"contentcell2\" colspan=\"5\">%s</td></tr>" % (self.link_to_uploaders(uploaders))
        
        source_summary_page_path = os.path.join(self._output_directory, "source", source_subdir(source))
        if not os.path.exists(source_summary_page_path):
           os.makedirs(source_summary_page_path)
        filename = os.path.join(source_summary_page_path, (source + ".html"))
        htmlpage = string.Template(HTML_HEADER + SOURCE_PACKAGE_BODY_TEMPLATE + HTML_FOOTER)
        f = file(filename, "w")
        f.write(htmlpage.safe_substitute( {
           "section_navigation": create_section_navigation(self._section_names,self._config.section),
           "time": time.strftime("%Y-%m-%d %H:%M %Z"),
           "rows": sourcerows+binaryrows,
        }))
        f.close()

        # return parsable values
        if success: source_state = "pass"
        if failed:  source_state = "fail"

        return sourcerows, binaryrows, source_state, maintainer, uploaders

    def create_maintainer_templates_for_source(self,source, source_state, sourcerows, binaryrows, maintainer, uploaders):
        maintainer_pages = [] 
        maintainer_pages.append(get_email_address(maintainer))
        for uploader in uploaders.split(", "):
          if uploader:
            maintainer_pages.append(get_email_address(uploader))
        for maintainer_page in maintainer_pages:
          maintainer_summary_page_path = os.path.join(self._output_directory, "maintainer", maintainer_subdir(maintainer_page))

          if not os.path.exists(maintainer_summary_page_path):
            os.makedirs(maintainer_summary_page_path)
          filename = os.path.join(maintainer_summary_page_path, (maintainer_page + "_tpl"))
          maintainer_package_count = {}
          maintainer_packages = {}
          if os.path.isfile(filename):
            lines = read_file(filename)
            for line in lines:
              state, count, packages = line.split(",")
              maintainer_package_count[state]=int(count)
              maintainer_packages[state]=packages[:-1]
            if maintainer_packages[source_state] == "none":
              maintainer_packages[source_state] = source
            else:
              maintainer_packages[source_state] = "%s %s" % (maintainer_packages[source_state],source)
          else:
            maintainer_package_count["fail"] = 0
            maintainer_package_count["unknown"] = 0
            maintainer_package_count["pass"] = 0
            for state in "fail", "unknown", "pass":
              maintainer_packages[state] = "none"
            maintainer_packages[source_state] = source
          if source_state == "fail":
            maintainer_package_count["fail"]+=1
          elif source_state == "unknown":
            maintainer_package_count["unknown"]+=1
          else:
            maintainer_package_count["pass"]+=1
          lines = ""
          for state in "fail", "unknown", "pass":
            lines +=  "%s,%s,%s\n" % (state,maintainer_package_count[state],maintainer_packages[state])
          write_file(filename,lines)
          append_file(filename[:-4]+"_"+source_state[:4],sourcerows+binaryrows)

    def create_package_summaries(self, logs_by_dir):
        logging.debug("Writing package templates in %s" % self._config.section)    

        sources = ""
        for source in self._source_db.get_all_packages():
            (sourcerows, binaryrows, source_state, maintainer, uploaders) = self.create_source_summary(source, logs_by_dir)
            sources += "%s: %s\n" % (source, source_state)
            self.create_maintainer_templates_for_source(source, source_state, sourcerows, binaryrows, maintainer, uploaders)
 
        write_file(os.path.join(self._output_directory, "sources.txt"), sources)


    def make_stats_graph(self):
        countsfile = os.path.join(self._output_directory, "counts.txt")
        pngfile = os.path.join(self._output_directory, "bimonthly-states.png")
        r('t <- (read.table("'+countsfile+'",sep=",",header=1,row.names=1))')
        r('cname <- c("date",rep(colnames(t)))')
        r('v <- t[(nrow(t)-60):nrow(t),0:12]')
        # thanks to http://tango.freedesktop.org/Generic_Icon_Theme_Guidelines for those nice colors
        r('palette(c("#4e9a06", "#ef2929", "#73d216", "#d3d7cf", "#5c3566", "#c4a000", "#fce94f", "#a40000", "#888a85", "#2e3436", "#8ae234",  "#729fcf","#204a87"))')
        r('bitmap(file="'+pngfile+'",type="png16m",width=16,height=9,pointsize=10,res=100)')
        r('barplot(t(v),col = 1:13, main="Packages per state in '+self._config.section+' (past 2 months)", xlab="", ylab="Number of packages",space=0.1,border=0)')
        r('legend(x="bottom",legend=colnames(t), ncol=2,fill=1:13,xjust=0.5,yjust=0,bty="n")')
        return "<tr class=\"normalrow\"> <td class=\"contentcell2\" colspan=\"3\"><a href=\"%s\"><img src=\"/%s/%s\" height=\"450\" width=\"800\" alt=\"Package states in the last 2 months\"></a></td></tr>\n" % ("bimonthly-states.png", self._config.section, "bimonthly-states.png")

    def create_and_link_to_analysises(self,state):
        link="<ul>"
        print self._output_directory
        templates = find_files_with_suffix(self._output_directory,".tpl")
        print state
        for template in templates:
          if (state == "failed-testing" and template[-9:] != "issue.tpl") or (state == "successfully-tested" and template[-9:] == "issue.pl"):
            print template

            tpl = os.path.join(self._output_directory, template)
            f = file(tpl, "r")
            analysis = file.read(f)
            f.close()
            os.unlink(tpl)

            htmlpage = string.Template(HTML_HEADER + ANALYSIS_BODY_TEMPLATE + HTML_FOOTER)
            filename = os.path.join(self._output_directory, template[:-len(".tpl")]+".html")
            f = file(filename, "w")
            f.write(htmlpage.safe_substitute( {
               "section_navigation": create_section_navigation(self._section_names,self._config.section),
               "time": time.strftime("%Y-%m-%d %H:%M %Z"),
               "rows": analysis,
             }))
            f.close()

            link += "<li><a href=%s>%s</a></li>" % (template[:-len(".tpl")]+".html", linktarget_by_template[template])
        link += "</ul>"
        return link

    def write_section_index_page(self,dirs,total_packages):
        tablerows = ""
        for state in self._binary_db.get_states():
            dir_link = ""
            analysis = ""
            for dir in dirs:
              if dir in ("pass","fail","bugged") and state_by_dir[dir] == state:
                dir_link += "<a href='%s.html'>%s</a> logs<br>" % (dir, html_protect(dir))
            if state in ("successfully-tested", "failed-testing"):
              analysis = self.create_and_link_to_analysises(state)
            tablerows += ("<tr class=\"normalrow\"><td class=\"contentcell2\"><a href='state-%s.html'>%s</a>%s</td>" +
                          "<td class=\"contentcell2\">%d</td><td class=\"contentcell2\">%s</td></tr>\n") % \
                          (html_protect(state), html_protect(state), analysis, len(self._binary_db.get_packages_in_state(state)),
                          dir_link)
        try:
          tablerows += self.make_stats_graph();
        except:
          logging.debug("python-rpy not installed, disabled graphs.")

        tablerows += "<tr class=\"normalrow\"> <td class=\"labelcell2\">Total</td> <td class=\"labelcell2\" colspan=\"2\">%d</td></tr>\n" % total_packages
        htmlpage = string.Template(HTML_HEADER + SECTION_INDEX_BODY_TEMPLATE + HTML_FOOTER)
        write_file(os.path.join(self._output_directory, "index.html"), htmlpage.safe_substitute( {
            "section_navigation": create_section_navigation(self._section_names,self._config.section),
            "time": time.strftime("%Y-%m-%d %H:%M %Z"),
            "section": html_protect(self._config.section),
            "description": html_protect(self._config["description"]),
            "tablerows": tablerows,
            "packagesurl": html_protect(self._config["packages-url"]), 
           }))

    def write_state_pages(self):
        for state in self._binary_db.get_states():
            logging.debug("Writing page for %s" % state)
            list = "<ul>\n"
            for package in self._binary_db.get_packages_in_state(state):
                list += "<li id=\"%s\">%s (%s)" % (
                                         package["Package"],
                                         self.link_to_source_summary(package["Package"]),
                                         html_protect(package["Maintainer"]))
                if package.dependencies():
                    list += "\n<ul>\n"
                    for dep in package.dependencies():
                        list += "<li>dependency %s is %s</li>\n" % \
                                  (self.link_to_state_page(self._config.section,dep,dep), 
                                  emphasize_reason(html_protect(self._binary_db.state_by_name(dep))))
                    list += "</ul>\n"
                list += "</li>\n"
            list += "</ul>\n"
            htmlpage = string.Template(HTML_HEADER + STATE_BODY_TEMPLATE + HTML_FOOTER)
            write_file(os.path.join(self._output_directory, "state-%s.html" % state), htmlpage.safe_substitute( {
                                        "section_navigation": create_section_navigation(self._section_names,self._config.section),
                                        "time": time.strftime("%Y-%m-%d %H:%M %Z"),
                                        "state": html_protect(state),
                                        "section": html_protect(self._config.section),
                                        "list": list
                                       }))

    def generate_html(self):
        logging.debug("Finding log files")
        dirs = ["pass", "fail", "bugged", "fixed", "reserved", "untestable"]
        logs_by_dir = {}
        for dir in dirs:
            logs_by_dir[dir] = find_files_with_suffix(dir, ".log")

        logging.debug("Copying log files")
        copy_logs(logs_by_dir, self._output_directory)

        logging.debug("Removing old log files")
        remove_old_logs(logs_by_dir, self._output_directory)

        logging.debug("Writing per-dir HTML pages")
        self.print_by_dir(self._output_directory, logs_by_dir)

        total_packages = self.write_counts_summary()

        if self._config["sources-url"]:
            self.create_package_summaries(logs_by_dir)

            logging.debug("Merging maintainer summaries in %s" % self._output_directory)    
            self.merge_maintainer_templates(find_files_with_suffix(self._output_directory+"/maintainer/", "_tpl"))

        logging.debug("Writing section index page")    
        self.write_section_index_page(dirs, total_packages)

        logging.debug("Writing stats pages for %s" % self._config.section)
        self.write_state_pages()


    def generate_output(self, master_directory, output_directory, section_names):
        self._section_names = section_names
        self._master_directory = os.path.abspath(os.path.join(master_directory, self._config.section))
        if not os.path.exists(self._master_directory):
            logging.debug("Warning: %s does not exist. Did you ever let the slave work?" % (self._master_directory, self._config.section))
            os.mkdir(self._master_directory)

        self._output_directory = os.path.abspath(os.path.join(output_directory, self._config.section))
        if not os.path.exists(self._output_directory):
            os.mkdir(self._output_directory)

        oldcwd = os.getcwd()
        os.chdir(self._master_directory)
        self.generate_html()
        os.chdir(oldcwd)

def main():
    setup_logging(logging.DEBUG, None)

    # For supporting multiple architectures and suites, we take a command-line
    # argument referring to a section in configuration file.  
    # If no argument is given, the "global" section is assumed.
    section_names = []
    if len(sys.argv) > 1:
        section = sys.argv[1]
    else:
        global_config = Config(section="global")
        global_config.read(CONFIG_FILE)
        section_names = global_config["sections"].split()
        master_directory = global_config["master-directory"]
        output_directory = global_config["output-directory"]


    if os.path.exists(master_directory):
        sections = []
        for section_name in section_names:
            section = Section(section_name)
            section.generate_output(master_directory=master_directory,output_directory=output_directory,section_names=section_names)
            sections.append(section)


        logging.debug("Writing index page")
        # FIXME: I'm sure the next 3 lines can be written more elegant..
        INDEX_BODY = INDEX_BODY_TEMPLATE
        if os.path.isfile(os.path.join(output_directory,"index.tpl")):
          INDEX_BODY = "".join(read_file(os.path.join(output_directory,"index.tpl")))
        htmlpage = string.Template(HTML_HEADER + INDEX_BODY + HTML_FOOTER)
        write_file(os.path.join(output_directory,"index.html"), htmlpage.safe_substitute( {
                                 "section_navigation": create_section_navigation(section_names),
                                 "time": time.strftime("%Y-%m-%d %H:%M %Z"),
                              }))
    else:
        logging.debug("Warning: %s does not exist!?! Creating it for you now." % master_directory)
        os.mkdir(master_directory)


if __name__ == "__main__":
    main()