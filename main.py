import subprocess
import time


class CreateResource():

    def __init__(self, name, number, size, dfl, sp, dl, primary):
        self.name = name
        self.number = number
        self.size = size
        self.dfl = dfl
        self.sp = sp
        self.dl = dl
        self.primary = primary

    def get_binary_number(self):
        binary_number = '1' + (self.number - 1) * '0'
        return binary_number

    def get_hexadecimal_number(self):
        binary_number = self.get_binary_number()
        hexadecimal_number = hex(int(binary_number, 2))
        hexadecimal_number = hexadecimal_number[2:]
        return hexadecimal_number

    def exec_cmd(self, cmd):
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        if p.returncode == 0:
            return True
        else:
            print(f'Failed to ececute cmd:{cmd}')

    def create_resource(self, resource):
        if self.exec_cmd(f"linstor resource-definition create {resource}"):
            if self.exec_cmd(f'linstor volume-definition create {resource} {self.size}'):
                self.exec_cmd(f'linstor resource create {self.dfl} {resource} --storage-pool {self.sp}')
                self.exec_cmd(f'linstor resource create {self.dl} {resource} --diskless')

    def set_resource_run_on_cpu(self, resource):
        hexadecimal_number = self.get_hexadecimal_number()
        if self.exec_cmd(f'linstor rd drbd-options --cpu-mask {hexadecimal_number} {resource}'):
            self.exec_cmd(f'drbdadm disconnect {resource}')
            time.sleep(1)
            self.exec_cmd(f'drbdadm connect {resource}')

    def set_primary(self, resource):
        self.exec_cmd(f'drbdadm primary --force {resource}')


def run():
    r = CreateResource(0, 3, 2, 2, 2, 2, 2)
    print(r.get_binary_number())
    print(r.get_hexadecimal_number())
    print(r.create_resource("a"))
    print(r.set_resource_run_on_cpu("a"))


if __name__ == '__main__':
    run()
