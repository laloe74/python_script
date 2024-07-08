# macOS桌面创建「from」文件夹，待转换视频拖进去。
# pip install ffmpeg-python
# python ffmpeg.py

import os
import shutil
import subprocess
import time
from datetime import datetime

####################
#参数设置

# 编码方式
# 「1」：默认全自动，较快，体积x2                                           [对比时间：1M    测试大小/原大小：87MB/41.3MB] 
# 「2」：重新解码编码[轻微压缩]，较慢，体积x3 [libx264 acc -crf 18]           [对比时间：1M16s 测试大小/原大小：145.7MB/41.3MB]
# 「3」：重新解码编码[无损]，超慢，体积x30   [libx264 flac -crf 0]            [对比时间：1M25s 测试大小/原大小：1.53G/41.3MB]
# 「4」：流复制[无损]，超快，体积x1         [但某些平台不支持，打开视频是黑的]     [对比时间：1s    测试大小/原大小：41.4MB/41.3MB]
# 修改后 command+s 手动保存再执行。
FFmpeg = 1

# 目标视频格式
target_ext = ".mp4"

# FFmpeg支持的原视频格式
source_ext = [
    '.3g2', '.3gp', '.amv', '.asf', '.avi', '.drc', '.f4a', '.f4b', '.f4p', '.f4v',
    '.flv', '.gif', '.gifv', '.m2v', '.m3u8', '.m4p', '.m4v', '.mkv', '.mng', '.mov',
    '.mp2', '.mp4', '.mpe', '.mpeg', '.mpg', '.mpv', '.mxf', '.nsv', '.ogg', '.ogv',
    '.qt', '.rm', '.rmvb', '.roq', '.svi', '.ts', '.vob', '.webm', '.wmv', '.yuv'
]

# Mac 桌面文件夹「from」和「to」路径
desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
from_folder = os.path.join(desktop, 'from')
start_time = time.time()
current_time = datetime.now().strftime("%H:%M:%S")
to_folder = os.path.join(desktop, f'to--{current_time}')

####################

if not os.path.exists(to_folder):
    os.makedirs(to_folder)

def create_log():
    log_path = os.path.join(desktop, f'log--{current_time}.txt')
    with open(log_path, 'w') as log_file:
        log_file.write('## 本次运行信息\n成功：0\n失败：0\n跳过：0\n总数：0\n总时间：00H:00M:00S\n\n')
        log_file.write('## 成功转换的视频名称\n')
        log_file.write('## 失败转换的视频名称\n')
        log_file.write('## 跳过转换的视频名称\n')
    return log_path

def log_update(log_path, success_count, failure_count, skip_count, total_files, elapsed_time):
    with open(log_path, 'r+') as log_file:
        content = log_file.readlines()
        content[1] = f'成功：{success_count}\n'
        content[2] = f'失败：{failure_count}\n'
        content[3] = f'跳过：{skip_count}\n'
        content[4] = f'总数：{total_files}\n'
        content[5] = f'总时间：{elapsed_time}\n'
        log_file.seek(0)
        log_file.writelines(content)

def log_append_section(log_path, section, message):
    with open(log_path, 'r+') as log_file:
        content = log_file.readlines()
        index = content.index(f'## {section}\n') + 1
        while index < len(content) and not content[index].startswith('## '):
            index += 1
        content.insert(index, f'{message}\n')
        log_file.seek(0)
        log_file.writelines(content)

log_path = create_log()
total_files = sum([len([file for file in files if file.endswith(tuple(source_ext))]) for _, _, files in os.walk(from_folder)])
success_count = 0
failure_count = 0
skip_count = 0

def convert_video(input_path, output_path):
    try:
        if FFmpeg == 1:
            command = ['ffmpeg', '-i', input_path, output_path]
        elif FFmpeg == 2:
            command = ['ffmpeg', '-i', input_path, '-c:v', 'libx264', '-crf', '18', '-c:a', 'aac', output_path]
        elif FFmpeg == 3:
            command = ['ffmpeg', '-i', input_path, '-c:v', 'libx264', '-crf', '0', '-c:a', 'flac', output_path]
        elif FFmpeg == 4:
             command = ['ffmpeg', '-i', input_path, '-c', 'copy', output_path]

        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        duration = None
        for line in process.stderr:
            if 'Duration' in line:
                duration_str = line.split('Duration: ')[1].split(', ')[0]
                h, m, s = duration_str.split(':')
                duration = int(h) * 3600 + int(m) * 60 + float(s)
            if 'time=' in line and duration:
                time_str = line.split('time=')[1].split(' ')[0]
                time_parts = time_str.split(':')
                if len(time_parts) == 3:
                    h, m, s = time_parts
                    current_time = int(h) * 3600 + int(m) * 60 + float(s)
                    progress = int(current_time / duration * 100)
                    bar = f"[{'█' * int(progress // 5)}{' ' * (20 - int(progress // 5))}]"
                    elapsed_time = format_time(time.time() - start_time)
                    filename = os.path.basename(input_path)
                    display_name = f'{filename[:20]}...{os.path.splitext(filename)[1]}'
                    print(f"\r运行中[{elapsed_time}]: {success_count}/{failure_count}/{skip_count}/{total_files} {progress}% {bar} -- {display_name}", end='', flush=True)
        process.wait()
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, command)
        return True
    except subprocess.CalledProcessError:
        return False

def format_time(seconds):
    time_struct = time.gmtime(seconds)
    return time.strftime("%H", time_struct) + "H:" + time.strftime("%M", time_struct) + "M:" + time.strftime("%S", time_struct) + "S"

def process_videos():
    global success_count, failure_count, skip_count
    processed_files = 0
    for root, _, files in os.walk(from_folder):
        for file in files:
            if not file.endswith(tuple(source_ext)):
                continue
            input_path = os.path.join(root, file)
            relative_path = os.path.relpath(root, from_folder)
            output_dir = os.path.join(to_folder, relative_path)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            output_path = os.path.join(output_dir, os.path.splitext(file)[0] + target_ext)
            processed_files += 1

            if os.path.splitext(file)[-1] == target_ext:
                shutil.copy(input_path, output_path)
                skip_count += 1
                log_append_section(log_path, '跳过转换的视频名称', file)
                print(f"\r跳过[{format_time(time.time() - start_time)}]: {success_count}/{failure_count}/{skip_count}/{total_files} 0% |        | -- {file[:20]}...{os.path.splitext(file)[1]}", end='', flush=True)
                continue
            
            result = convert_video(input_path, output_path)
            if result:
                success_count += 1
                log_append_section(log_path, '成功转换的视频名称', file)
            else:
                failure_count += 1
                log_append_section(log_path, '失败转换的视频名称', f'{file} -- 转换失败')
                print(f"\n[失败] 转换失败 -- {file}", flush=True)
                continue
            
            progress = processed_files / total_files * 100
            bar = f"[{'█' * int(progress // 5)}{' ' * (20 - int(progress // 5))}]"
            print(f"\r运行中[{format_time(time.time() - start_time)}]: {success_count}/{failure_count}/{skip_count}/{total_files} {int(progress)}% {bar} -- {file[:20]}...{os.path.splitext(file)[1]}", end='', flush=True)

            # 实时更新日志
            log_update(log_path, success_count, failure_count, skip_count, total_files, format_time(time.time() - start_time))

process_videos()

total_time = time.time() - start_time
log_update(log_path, success_count, failure_count, skip_count, total_files, format_time(total_time))

# 读取并显示日志中 "## 本次运行信息" 内的内容
with open(log_path, 'r') as log_file:
    content = log_file.readlines()
    basic_info = content[1:6]  # 获取本次运行信息部分的内容
    print("\n\n" + "".join(basic_info))

print("处理完成，详情请在桌面查看日志。")