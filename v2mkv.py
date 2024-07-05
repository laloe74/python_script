import os
import subprocess
import re
import shutil
import time

# FFmpeg支持的视频格式
supported_formats = [
    '.3g2', '.3gp', '.amv', '.asf', '.avi', '.drc', '.f4a', '.f4b', '.f4p', '.f4v', 
    '.flv', '.gif', '.gifv', '.m2v', '.m3u8', '.m4p', '.m4v', '.mkv', '.mng', '.mov', 
    '.mp2', '.mp4', '.mpe', '.mpeg', '.mpg', '.mpv', '.mxf', '.nsv', '.ogg', '.ogv', 
    '.qt', '.rm', '.rmvb', '.roq', '.svi', '.ts', '.vob', '.webm', '.wmv', '.yuv'
]

log_file_path = os.path.expanduser('~/Desktop/conversion_log.txt')

def create_log_file():
    with open(log_file_path, 'w') as log_file:
        log_file.write("")

def count_supported_videos(folder):
    count = 0
    for root, dirs, files in os.walk(folder):
        for file in files:
            if os.path.splitext(file)[1].lower() in supported_formats and file != '.DS_Store':
                count += 1
    return count

def parse_ffmpeg_output(line):
    result = {}
    parts = line.split()
    for part in parts:
        if '=' in part:
            key, value = part.split('=')
            result[key] = value
    return result

def read_log():
    processed_files = set()
    if os.path.exists(log_file_path):
        with open(log_file_path, 'r') as log_file:
            for line in log_file:
                processed_files.add(line.strip())
    return processed_files

def write_log_section(title, content_list):
    with open(log_file_path, 'a') as log_file:
        log_file.write(f"\n## {title}\n")
        for content in content_list:
            log_file.write(f"{content}\n")

def write_summary(expected_count, success_count, fail_count, skip_count, total_time, unsupported_files, failed_files, success_files, no_processing_files):
    with open(log_file_path, 'a') as log_file:
        log_file.write("\n## 基本信息\n")
        log_file.write(f"本次运行预计处理数：{expected_count}\n")
        log_file.write(f"本次运行成功次数：{success_count}\n")
        log_file.write(f"本次运行失败次数：{fail_count}\n")
        log_file.write(f"本次运行跳过次数：{skip_count}\n")
        log_file.write(f"本次运行总时间：{total_time:.2f}秒\n")
    write_log_section("失败信息", failed_files)
    write_log_section("跳过信息", no_processing_files)
    write_log_section("成功信息", success_files)

def convert_videos(from_folder, to_folder):
    create_log_file()

    if not os.path.exists(to_folder):
        os.makedirs(to_folder)

    total_files = count_supported_videos(from_folder)
    processed_files = 0
    error_files = 0
    unsupported_files = []
    failed_files_list = []
    no_processing_files = []
    processed_set = read_log()
    success_files = list(processed_set)
    success_count = 0
    fail_count = 0
    skip_count = 0

    time_pattern = re.compile(r'^\d+:\d+:\d+\.\d+$')

    start_time = time.time()

    for root, dirs, files in os.walk(from_folder):
        for file in files:
            processed_files += 1
            file_extension = os.path.splitext(file)[1].lower()
            
            if file == '.DS_Store':
                continue
            
            input_path = os.path.join(root, file)
            relative_path = os.path.relpath(root, from_folder)
            output_dir = os.path.join(to_folder, relative_path)
            os.makedirs(output_dir, exist_ok=True)
            
            output_file = os.path.splitext(file)[0] + '.mp4'
            output_path = os.path.join(output_dir, output_file)
            
            if file_extension == '.mp4':
                shutil.copy2(input_path, output_path)
                no_processing_files.append(file)
                skip_count += 1
                print(f"\r正在处理: {processed_files}/{total_files}/{error_files} -- 跳过MP4文件: {file}")
                continue
            
            if file_extension in supported_formats:
                if file in processed_set:
                    no_processing_files.append(file)
                    skip_count += 1
                    print(f"\r正在处理: {processed_files}/{total_files}/{error_files} -- 跳过已处理文件: {file}")
                    continue
                
                try:
                    process = subprocess.Popen(
                        ['ffmpeg', '-i', input_path, '-c:v', 'copy', '-c:a', 'copy', output_path],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        universal_newlines=True
                    )
                    
                    duration = None
                    for line in process.stdout:
                        if "Duration" in line:
                            duration_str = line.split("Duration:")[1].split(",")[0].strip()
                            h, m, s = map(float, duration_str.split(':'))
                            duration = h * 3600 + m * 60 + s
                        
                        if "time=" in line:
                            ffmpeg_output = parse_ffmpeg_output(line)
                            time_str = ffmpeg_output.get('time', '0:00:00.00')
                            if time_pattern.match(time_str):
                                h, m, s = map(float, time_str.split(':'))
                                time_in_seconds = h * 3600 + m * 60 + s
                                
                                if duration:
                                    progress = (time_in_seconds / duration) * 100
                                    progress_bar = '|' + '█' * int(progress // 2) + ' ' * (50 - int(progress // 2)) + '|'
                                    elapsed_time = time.time() - start_time
                                    elapsed_hours = int(elapsed_time // 3600)
                                    elapsed_minutes = int((elapsed_time % 3600) // 60)
                                    elapsed_seconds = int(elapsed_time % 60)
                                    elapsed_str = f"{elapsed_hours}H/{elapsed_minutes}M/{elapsed_seconds}S"
                                    print(f"\r正在处理: {processed_files}/{total_files}/{error_files} {int(progress)}% {progress_bar} -- {file} ({elapsed_str})", end='')
                    
                    process.wait()
                    if process.returncode == 0:
                        success_files.append(file)
                        success_count += 1
                    else:
                        failed_files_list.append(file)
                        fail_count += 1
                        print(f"\n转换失败: {input_path}")
                    
                except subprocess.CalledProcessError as e:
                    failed_files_list.append(file)
                    fail_count += 1
                    print(f"\n转换失败: {input_path}")
                    print(e.stderr.decode())
                
                print()  # 换行以显示下一个文件的进度
            else:
                unsupported_files.append(file)
                error_files += 1
                print(f"\r正在处理: {processed_files}/{total_files}/{error_files} -- 文件格式不受支持: {file_extension} 文件: {file}")

    end_time = time.time()
    total_time = end_time - start_time
    write_summary(total_files, success_count, fail_count, skip_count, total_time, unsupported_files, failed_files_list, success_files, no_processing_files)

    print("\n## 基本信息")
    print(f"本次运行预计处理数：{total_files}")
    print(f"本次运行成功次数：{success_count}")
    print(f"本次运行失败次数：{fail_count}")
    print(f"本次运行跳过次数：{skip_count}")
    print(f"本次运行总时间：{total_time:.2f}秒")

from_folder = os.path.expanduser('~/Desktop/from')
to_folder = os.path.expanduser('~/Desktop/to')

convert_videos(from_folder, to_folder)

print("\n视频转换完成！")