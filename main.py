import os
from output_log_string import OutputLogString


def main():
    base_path = r'E:\tmp\xoyologs\xoyologs.tar\xoyologs'
    output_class = OutputLogString(base_path, 'output', 'input.txt')
    output_class.work()
    output_class.output_struct()

if __name__ == '__main__':
    main()
