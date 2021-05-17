# -*- coding:utf-8 -*-
import subprocess
import time
import argparse


def get_hexadecimal_number(number):
    binary_number = '1' + number * '0'
    hexadecimal_number = hex(int(binary_number, 2))
    hexadecimal_number = hexadecimal_number[2:]
    return hexadecimal_number


class SetInputParser(object):
    def __init__(self):
        self.parser = argparse.ArgumentParser(prog="Create resources and set resource run on CPU core")
        self.set_parser()

    def set_parser(self):

        self.parser.add_argument('name',
                                 help='Marks the resource created by the program')
        self.parser.add_argument('-n',
                                 '--number',
                                 dest='number',
                                 type=int,
                                 help='The number of resource that you want to create',
                                 action='store')
        self.parser.add_argument('-s',
                                 '--size',
                                 dest='size',
                                 help='The size of resource that you want to create',
                                 action='store')
        self.parser.add_argument('-dfl',
                                 '--diskful',
                                 metavar='NodeName',
                                 nargs='+',
                                 dest='diskful',
                                 help='Create the diskful resource on one or more nodes',
                                 action='store')
        self.parser.add_argument('-sp',
                                 '--storagepool',
                                 nargs='+',
                                 dest='storagepool',
                                 help='One to one correspondence with nodes which uesd to created diskful resource',
                                 action='store')
        self.parser.add_argument('-dl',
                                 '--diskless',
                                 metavar='NodeName',
                                 nargs='*',
                                 dest='diskless',
                                 help='Create the diskless resource on one or more nodes',
                                 action='store')
        self.parser.add_argument('-p',
                                 '--primary',
                                 dest='primary',
                                 help='Set to be primary resource',
                                 action='store_true')

        self.parser.set_defaults(func=self.run_func)

        # self.parser.add_argument('-v',
        #                          '--version',
        #                          dest='version',
        #                          help='Show current version',
        #                          action='store_true')

    def parse(self):  # 调用入口
        args = self.parser.parse_args()
        args.func(args)

    def run_func(self, args):
        if args.name and args.number and args.size and args.diskful and args.storagepool:
            if len(args.diskful) != len(args.storagepool):
                print("Check the Diskful Node and Storagepool that you input.")
            for i in range(args.number):
                hexadecimal_number = get_hexadecimal_number(i)
                resource_name = f'{args.name}_{i}'
                r = CreateResource(resource_name, hexadecimal_number, args.size, args.diskful, args.storagepool,
                                   args.diskless)
                print("Start to create resource:", resource_name)
                r.create_resource()
                r.set_resource_run_on_cpu()
                if args.primary:
                    r.set_primary()
        else:
            self.parser.print_help()


class CreateResource(object):

    def __init__(self, name, number, size, dfl, sp, dl):
        self.name = name
        self.hexadecimal_number = number
        self.size = size
        self.dfl = dfl
        self.sp = sp
        self.dl = dl

    def exec_cmd(self, cmd):
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        if p.returncode == 0:
            return True
        else:
            print(f'  Failed to execute command:{cmd}')

    def create_resource(self):
        if self.exec_cmd(f"linstor resource-definition create {self.name}"):
            if self.exec_cmd(f'linstor volume-definition create {self.name} {self.size}'):
                # self.exec_cmd(f'linstor resource create {self.dfl} {self.name} --storage-pool {self.sp}')
                # self.exec_cmd(f'linstor resource create {self.dl} {self.name} --diskless')
                self.create_diskful_resource()
                if self.dl is not None:
                    self.create_diskless_resource()

    def create_diskful_resource(self):
        for dfl, sp in zip(self.dfl, self.sp):
            self.exec_cmd(f'linstor resource create {dfl} {self.name} --storage-pool {sp}')
        return True

    def create_diskless_resource(self):
        for dl in self.dl:
            self.exec_cmd(f'linstor resource create {dl} {self.name} --diskless')
        return True

    def set_resource_run_on_cpu(self):
        if self.exec_cmd(f'linstor rd drbd-options --cpu-mask {self.hexadecimal_number} {self.name}'):
            self.exec_cmd(f'drbdadm disconnect {self.name}')
            time.sleep(1)
            self.exec_cmd(f'drbdadm connect {self.name}')
            time.sleep(1)
        return True

    def set_primary(self):
        self.exec_cmd(f'drbdadm primary --force {self.name}')
        return True


if __name__ == '__main__':
    run_program = SetInputParser()
    run_program.parse()
