# 写入output

# 程序开始时清空文件
open("output.txt", "w").close()
def write_to_file(message, file_path="output.txt"):
    """
    将给定的消息写入到指定的文件中。
    
    :param message: 要写入文件的消息。
    :param file_path: 输出文件的路径，默认为当前目录下的output.txt。
    """
    with open(file_path, "a") as file:  # 使用追加模式打开文件
        file.write(message + "\n")  # 写入消息并追加换行符