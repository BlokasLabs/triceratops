#!/usr/bin/env python
import os
import sys 
import shutil
from waflib import Logs
from waflib.extras import autowaf as autowaf

# Variables for 'waf dist'
APPNAME = 'triceratops.lv2'
VERSION = '0.2.1'

# Mandatory variables
top = '.'
out = 'build'

def options(opt):
    opt.load('compiler_c')
    opt.load('compiler_cxx')
    autowaf.set_options(opt)

def configure(conf):	
    conf.load('compiler_c')
    conf.load('compiler_cxx')
    autowaf.configure(conf)
    autowaf.display_header('triceratops Configuration')
   
    if conf.env['MSVC_COMPILER']:
        conf.env.append_unique('CXXFLAGS', ['-TP', '-MD'])
    else:
        conf.env.append_unique('CXXFLAGS', ['-O2','-funroll-loops','-std=c++0x'])

    if not autowaf.is_child():
        autowaf.check_pkg(conf, 'lv2core', uselib_store='LV2CORE')

    # Set env['pluginlib_PATTERN']
    pat = conf.env['cshlib_PATTERN']
    if pat.startswith('lib'):
        pat = pat[3:]
    conf.env['pluginlib_PATTERN'] = pat
    conf.env['pluginlib_EXT'] = pat[pat.rfind('.'):]

    autowaf.display_msg(conf, "LV2 bundle directory", conf.env['LV2DIR'])
    print('')

def build(bld):
    bundle = APPNAME

    # Build manifest.ttl by substitution (for portable lib extension)
    bld(features     = 'subst',
        source       = 'manifest.ttl.in',
        target       = '%s/%s' % (bundle, 'manifest.ttl'),
        install_path = '${LV2DIR}/%s' % bundle,
        LIB_EXT      = bld.env['pluginlib_EXT'])

    # Copy other data files to build bundle (build/triceratops.lv2)
    for i in [ 'triceratops.ttl' ]:
        bld(features     = 'subst',
            source       = i,
            target       = '%s/%s' % (bundle, i),
            install_path = '${LV2DIR}/%s' % bundle,
            LIB_EXT      = bld.env['pluginlib_EXT'])

    # Create a build environment that builds module-style library names
    # e.g. triceratops.so instead of libtriceratops.so
    # Note for C++ you must set cxxshlib_PATTERN instead
    penv                   = bld.env.derive()
    penv['cshlib_PATTERN'] = bld.env['pluginlib_PATTERN']
    penv['cxxshlib_PATTERN'] = bld.env['pluginlib_PATTERN']

    includes = None
    if autowaf.is_child:
        includes = '../..'

    # Build plugin library
    obj = bld(features     = 'cxx cshlib ',
              env          = penv,
              source       = 'triceratops.cpp filter.cpp lfo.cpp fastmaths.cpp synth.cpp nix-echo.cpp dsp/eq.cpp dsp/Object.cpp dsp/Reverb.cpp dsp/DLineN.cpp dsp/JCRev.cpp dsp/Filter.cpp',
              name         = 'triceratops',
              target       = '%s/triceratops' % bundle,
              install_path = '${LV2DIR}/%s' % bundle,
              uselib       = 'LV2CORE',
              includes     = includes)

    bld.install_files('${LV2DIR}/triceratops.lv2/', 'minblep.mat')
    bld.install_files('${LV2DIR}/triceratops.lv2/', 'logo.png')
    bld.install_files('${LV2DIR}/triceratops.lv2/', 'triceratops.conf')
    bld.install_files('${LV2DIR}/triceratops.lv2/', 'triceratops_categories.txt')
    bld.install_files('${LV2DIR}/triceratops.lv2', bld.path.ant_glob('presets.lv2/*.*'))




