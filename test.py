import os

# def current_path(*args):
#     """用于创建确切格式的目录"""
#     current_script_path = os.path.abspath(__file__)
#     ntqqbots_index = current_script_path.rfind('NTQQBots')
#     if ntqqbots_index != -1:
#         truncated_path = current_script_path[:ntqqbots_index + len('NTQQBots')]
#         data_file_path = os.path.join(truncated_path, *args)
#         return data_file_path
#     else:
#         raise ValueError('没有找到NTQQBots目录！')
#
# print(current_path('data'))


def current_path(*args):
    """用于获取准确的目录"""
    current_script_path = os.path.dirname(os.path.abspath(__file__))
    data_file_path = os.path.join(current_script_path, *args)
    return data_file_path

print(current_path('data'))