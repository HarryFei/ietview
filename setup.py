# This file is part of IETView
# Copyright (C) 2008,2009 Jeffrey Panczyk <jpanczyk@gmail.com>
#
# IETView is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IETView is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with IETView.  If not, see <http://www.gnu.org/licenses/>.

from distutils.core import setup
setup(name='IETView',
      version='1.0b3',
      description='GUI tool that manages iSCSI Enterprise Target software',
      long_description='GUI tool that manages iSCSI Enterprise Target software.  It enables you to add, edit, and delete iSCSI targets on your server.',
      author='Jeffrey Panczyk',
      author_email='jpanczyk@gmail.com',
      url='http://code.google.com/p/ietview/',
      license='GPLv3orLater',
      platforms='Linux',
      packages=['IETView'],
      package_dir={'IETView': 'src'},
      scripts=['ietview'],
      data_files=[('share/IETView', ['src/IETView.glade'])],
     )

