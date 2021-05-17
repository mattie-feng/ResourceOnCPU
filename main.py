import subprocess
import time
import argparse
import os


def get_hexadecimal_number(number):
    binary_number = '1' + number * '0'
    hexadecimal_number = hex(int(binary_number, 2))
    hexadecimal_number = hexadecimal_number[2:]
    return hexadecimal_number


class SetInputParser(object):
    def __init__(self):
        self.parser = argparse.ArgumentParser(prog="Create resource and set it run on CPU")
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
                                 '--Size',
                                 dest='size',
                                 help='The size of resource that you want to create',
                                 action='store')
        self.parser.add_argument('-dfl',
                                 '--diskful',
                                 dest='diskful',
                                 help='Node name.Create the diskful resource on this node',
                                 action='store')
        self.parser.add_argument('-sp',
                                 '--storagepool',
                                 dest='storagepool',
                                 help='Storagepool name.Create the diskful resource on this storagepool',
                                 action='store')
        self.parser.add_argument('-dl',
                                 '--diskless',
                                 dest='diskless',
                                 help='Node name.Create the diskless resource on this node',
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
        if args.name and args.number and args.size and args.diskful and args.storagepool and args.diskless:
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
                self.exec_cmd(f'linstor resource create {self.dfl} {self.name} --storage-pool {self.sp}')
                self.exec_cmd(f'linstor resource create {self.dl} {self.name} --diskless')

    def set_resource_run_on_cpu(self):
        if self.exec_cmd(f'linstor rd drbd-options --cpu-mask {self.hexadecimal_number} {self.name}'):
            self.exec_cmd(f'drbdadm disconnect {self.name}')
            time.sleep(1)
            self.exec_cmd(f'drbdadm connect {self.name}')

    def set_primary(self):
        self.exec_cmd(f'drbdadm primary --force {self.name}')


if __name__ == '__main__':
    run_program = SetInputParser()
    run_program.parse()
