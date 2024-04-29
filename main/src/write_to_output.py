# 写入output
import os
OUTPUT_DIR = "main\\output\\"
# 程序开始时清空文件
def clear_output_file(filename):
    """ Clears the content of the specified output file. """
    output_file_path = os.path.join(OUTPUT_DIR, filename)
    open(output_file_path, 'w').close()

def write_to_file(message, filename):
    """
    将给定的消息写入到指定的文件中。
    
    :param message: 要写入文件的消息。
    :param file_path: 输出文件的路径，默认为当前目录下的output.txt。
    """
    # Ensure the output directory exists
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # Define the full path for the output file
    output_file_path = os.path.join(OUTPUT_DIR, filename)

    with open(output_file_path, "a") as file:  # 使用追加模式打开文件
        file.write(message + "\n")  # 写入消息并追加换行符