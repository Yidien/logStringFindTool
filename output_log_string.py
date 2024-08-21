import os
import json
from jsonpath import JSONPath
from enum import Flag, Enum, auto


# 搜索模式
class EnumFindMethod(Enum):
    BASE_PATH = auto()
    SUB_PATH = auto()


# 输出模式
class EnumOutputMethod(Flag):
    PATH_METHOD = auto()
    PREFIX_METHOD = auto()


# 单条记录类
class OutputString:
    def __init__(self, string_content, file_name, file_prefix=''):
        self.string_content = string_content
        self.file_name = file_name
        self.file_prefix = file_prefix if file_prefix else file_name.split('_')[0]
        tmp_json = json.loads(string_content)
        self.log_time = JSONPath("$.event_detail._log_time").parse(tmp_json)
        self.ip = JSONPath("$.client_ip").parse(tmp_json)
        self.url = JSONPath("$.msg_context.url").parse(tmp_json)
        self.event = JSONPath("$.event").parse(tmp_json)
        return


# 搜索类
class FindStruct:
    def __init__(self, find_string, base_path, output_file_name):
        self.find_string = find_string
        self.base_path = base_path
        self.output_file_name = output_file_name
        self.output_string_list = []
        self.dict_file_path = {}
        self.dict_file_prefix = {}
        return

    def init_output_info(self):
        self.output_string_list.clear()
        self.dict_file_path.clear()
        self.dict_file_prefix.clear()
        return

    def output_txt(self, method: EnumOutputMethod = EnumOutputMethod.PATH_METHOD | EnumOutputMethod.PREFIX_METHOD):
        if not self.output_string_list: return
        with (open(os.path.join(self.base_path, self.output_file_name)+'-'+self.find_string,
                   'w', encoding='utf-8') as f):
            f.write(self.find_string + '\n')
            if method & EnumOutputMethod.PATH_METHOD:
                f.write('path method\n\n')
                for key, value in self.dict_file_path.items():
                    f.write('file name: ' + key + '\n\n')
                    for output_string in sorted(value, key=lambda k: k.log_time):
                        f.write(output_string.string_content)
                    f.write('\n\n')

            if method & EnumOutputMethod.PREFIX_METHOD:
                f.write('prefix method\n\n')
                for key, value in self.dict_file_prefix.items():
                    f.write('prefix name: ' + key + '\n\n')
                    for output_string in sorted(value, key=lambda k: k.log_time):
                        f.write(output_string.string_content)
                    f.write('\n\n')
        return

    def output_struct(self):
        if not self.output_string_list: return
        with (open(os.path.join(self.base_path, self.output_file_name) + '-item-' + self.find_string,
                   'w', encoding='utf-8') as f):
            f.write('find_string,file_name,file_prefix,log_time,ip,url,event\n')
            for struct in self.output_string_list:
                f.write(','.join([str(self.find_string),
                                 str(struct.file_name),
                                 str(struct.file_prefix),
                                 str(struct.log_time),
                                 str(struct.ip),
                                 str(struct.url),
                                 str(struct.event)])+'\n')
        return


class OutputLogString:
    def __init__(self, base_path, output_file_name, input_path, find_string='',
                 method: EnumFindMethod = EnumFindMethod.BASE_PATH):
        self.base_path = base_path
        self.output_file_name = output_file_name
        self.method = method
        self.file_path_list = []
        self.find_struct_list = self.init_find_struct(input_path, find_string)
        return

    def init_find_struct(self, input_path, find_string):
        ret_tup = ()
        if find_string: ret_tup += (find_string,)
        with open(os.path.join(self.base_path, input_path), 'r') as f:
            for postfix in f:
                ret_tup += (postfix.strip(),)
        ret_list = []
        for item in ret_tup:
            ret_list.append(FindStruct(item, self.base_path, self.output_file_name))
        return ret_list

    def init_output_info(self):
        self.file_path_list.clear()
        for struct in self.find_struct_list:
            struct.init_output_info()
        return

    def find_log_file_path_list(self):
        match self.method:
            case EnumFindMethod.BASE_PATH:
                self.file_path_list = [os.path.join(self.base_path, file_name)
                                       for file_name in os.listdir(self.base_path) if file_name.endswith('.log')]
            case EnumFindMethod.SUB_PATH:
                for dir_path, dir_name, file_name_list in os.walk(self.base_path):
                    self.file_path_list = [os.path.join(dir_path, file_name)
                                           for file_name in file_name_list if file_name.endswith('.log')]
            case _: self.file_path_list.clear()
        return

    def find_log_string(self, file_full_path):
        # ret_string_dict = {}
        prefix = file_full_path.split('\\')[-1].split('_')[0]
        with open(file_full_path, 'r', encoding='utf-8') as f:
            for line in f:
                for struct in self.find_struct_list:
                    if struct.find_string in line:
                        tmp_item = OutputString(line, file_full_path, prefix)
                        struct.output_string_list.append(tmp_item)
                        struct.dict_file_path[file_full_path] = struct.dict_file_path.get(file_full_path,[]) + [tmp_item]
                        struct.dict_file_prefix[prefix] = struct.dict_file_prefix.get(prefix, []) + [tmp_item]
        return

    def work(self):
        self.init_output_info()
        self.find_log_file_path_list()
        for file_full_path in self.file_path_list:
            self.find_log_string(file_full_path)
        return

    def output(self, method: EnumOutputMethod = EnumOutputMethod.PATH_METHOD | EnumOutputMethod.PREFIX_METHOD):
        for struct in self.find_struct_list:
            struct.output_txt(method)
        return

    def output_struct(self):
        for struct in self.find_struct_list:
            struct.output_struct()
        return
