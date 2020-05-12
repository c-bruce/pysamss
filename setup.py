#!/usr/bin/env python

from distutils.core import setup

setup(name='pysamss',
      version='0.0.1',
      description='Python Space Asset Management and Simulation System',
      author='Callum Bruce',
      author_email='callum.bruce1@gmail.com',
      url='https://github.com/c-bruce/pysamss',
      license='MIT License',
      packages=['pysamss',
                'pysamss.resources',
                'pysamss.main',
                'pysamss.gui',
                'pysamss.helpermath',
                'pysamss.control',
                'pysamss.plotting',
                'pysamss.forcetorque'],
      package_data={'pysamss' : ['LICENSE.txt'],
                    'pysamss.resources' : ['*.jpg']},
      install_requires=['h5py>=2.10.0',
                        'jplephem>=2.14',
                        'julian>=0.14',
                        'mayavi>=4.7.1',
                        'numpy>=1.18.1',
                        'PyQt5>=5.14.2',
                        'pyquaternion>=0.9.5',
                        'sgp4>=2.7',
                        'vtk>=8.1.2']
     )