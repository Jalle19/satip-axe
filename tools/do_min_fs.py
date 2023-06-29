#!/usr/bin/env python3

import sys, os, re, getopt
import subprocess
from subprocess import Popen, PIPE, STDOUT

#-----------------------------------------------------
def run_cmd(cmd):
    """ runs the os.system(). run a command into the shell and return
        the stdout on a list. Each element terminates whith '\n'
        It doesn't catch errors
        You can use the builtin 'command' module.
        Like: command.getoutput()
    """
    # print cmd
    try:
      cmd = str(cmd) + '  > output.txt'
      # print 'command: ' + cmd
      os.system(cmd)
      f=open('output.txt','r')
      cmd_output = f.readlines()
      f.close()
      os.system('rm output.txt')
      # print 'cmd_output: ' + str(cmd_output[0][:-1])
      # print 'cmd_output: ' + str(cmd_output)
    except Exception as e:
         print('-> Error run_cmd ' + cmd + ':', e)
    else:
        return cmd_output

#-----------------------------------------------------------------

def get_cmd_output(cmd):
    """ run a command on the shell and return
        stdout and stderr on the same list.
        Each element isn't '/n' terminated
        os.popen* is obsolete! it's replaced by the new subprocess module (2.6)
        FIXME
    """
    #p = Popen(cmd, shell=True, bufsize=bufsize, stdin=PIPE, stdout=PIPE, stderr=SDTOUT,
    #close_fds=True)
    #(dummy, stdout_and_stderr) = (p.stdin, p.stdout)
    p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
    (dummy, stdout_and_stderr) = (p.stdin, p.stdout)
    result = stdout_and_stderr.read()
    return  result.splitlines()

#---------------------------------------

def setup_busybox():
    run_cmd('cp ' + target_prefix + '/bin/busybox fs/bin')

    run_cmd(' ln -s  /bin/busybox  fs/sbin/init')
    run_cmd(' ln -s  /bin/busybox  fs/bin/sh')

    run_cmd('mknod fs/dev/console c 5 1')
    run_cmd('mknod fs/dev/null c 1 3')
    run_cmd('mknod fs/dev/zero c 1 5')

#------------------------------------------------

def gen_fs(init_type):
    """ 1) generate a minimal FS skeleton;
        2) get paths from lib_list.
        Copy all files into the fs. Setup busybox or sh shell
    """
    print('\t coping libraries  and binary files \n')
    run_cmd('rm -rf fs fs.cpio')
    for i in ['sbin', 'bin', 'dev', 'sys', 'etc', 'lib/modules', 'tmp', 'proc', 'usr/lib', 'usr/libexec', 'var', 'root']:
      run_cmd('mkdir -p fs/' + i)
    for i in ['sbin', 'bin']:
      run_cmd('mkdir -p fs/usr/' + i)

    run_cmd('cp  -d ' + target_prefix + '/lib/*' + ' fs/lib/')

    run_cmd(' chmod a+x fs/lib/lib* ')
    run_cmd(' chmod a+x fs/etc/* ')
    run_cmd(' chmod 0600 fs/root ')

    if init_type == 'busybox':
       setup_busybox()

#------------------------------------------------

def do_cpio(path):
    """
    """
    print('doing fs.cpio \n')
    cmd = 'cd ' + str(path) + ' ; find . | cpio -ovB -H newc >  ../fs.cpio  '
    print(cmd)
    get_cmd_output(cmd)

#------------------------------------------------

def usage():
    print('\n\nDESCRIPTION:\nStarting from the installed binary RPM (for SH4), it discover ')
    print('the minimal set of shared library object needed from a dinamically linked application.')
    print('It also returns, a filesystem skeleton, including a small set of selected binaries')
    print('\n  -h,  --help   Usage information.')
    print('\n  -b,  --binary <file> executable file; use " " to specify more than one bin ')
    print('         (example: -b "gzip ls pwd") ')
    print('\n  -t,  --target_prefix <path> the target path location ')
    print('         (default: /usr/sh4-linux-gnu/)')
    print('\n  -e,  --extra <file>:<dst> to be added to the filesystem')
    print('\n  -r,  --version <ver>')
    print('\n  -i   --init_type : ')
    print('\t\t\t  busybox ')
    print('\t\t\t  sysv ')
    print('\t\t\t  no (no init files) ')
    print('example: ./do_min_fs.py -i busybox -t /usr/sh4-linux-gnu -b "file more"')
    print('\n\n\n')
    sys.exit()

#--------------------------------------------------

def get_menu_opt(argv):
    """ print a menu and return a list with selected options
    """
    try:
#      opts = ''
#      args = ''
       opts , args = getopt.gnu_getopt(argv, 'h:e:d:t:i:r:',
           ['--init_type', '--extra', '--extradir',
            '--target_prefix=', '--version', '--help'])
    except getopt.GetoptError:
           usage()
    target_prefix = ''
    console = ''
    extra_list=[]
    extradir_list=[]
    version = ''
    for o, v  in opts:
       if o == '-e' or o == '--extra':
          v = v.split(' ')
          for i in v:
            if i != '':
               extra_list.append(i)
       elif o == '-d' or o == '--extradir':
          v = v.split(' ')
          for i in v:
            if i != '':
               extradir_list.append(i)
       elif o == '-t' or o == '--target_prefix':
            target_prefix = v
       elif o == '-i' or o == '--init_type':
            console = v
       elif o == '-r' or o == '--version':
            version = v
       elif o == '-h' or o == '--help':
          usage()
    params = []
    params.append(console)
    params.append(target_prefix)
    params.append(extra_list)
    params.append(extradir_list)
    params.append(version)
    return params

## ================================================================
## 		       		Main
## =================================================================

#os.environ['LDD_ROOT_SHOW'] = '0'

global target_prefix
target_prefix = '/usr/sh4-linux-gnu'
boot_type = 'busybox' # default
user_param = ['', '', '']
user_param = get_menu_opt(sys.argv[1:])
extra_list = user_param[2]
extradir_list = user_param[3]
version = user_param[4]

if user_param[0] != '':
   boot_type = user_param[1] # default busybox
if user_param[1] != '':
   target_prefix =  user_param[2]

print(30*'=')
print('  boot_type: ' + str(boot_type))
print('  target_prefix:  ' + str(target_prefix))
print(30*'=')

gen_fs(boot_type)

for d in extradir_list:
  run_cmd('cp -Rv ' + d + '/* fs')
f = open("fs/etc/motd")
b = f.read(1024*1024)
f.close()
f = open("fs/etc/motd", "w+")
f.write(b.replace('@VERSION@', version))
f.close()
files = run_cmd('find fs -name "*~"')
for f in files:
  run_cmd('rm ' + f.strip())
for r in ['usr/bin/bashbug', 'usr/lib/pkgconfig']:
  if os.path.exists('fs/' + r):
    run_cmd('rm -rf fs/' + r)
for e in extra_list:
  src, dst = e.split(':')
  dir = os.path.dirname(dst)
  if not os.path.exists('fs/' + dir):
    run_cmd('mkdir -p fs/' + dir)
  run_cmd('cp -P ' + src + ' fs/' + dst)
do_cpio('fs')
