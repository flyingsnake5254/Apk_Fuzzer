import json
import random
import string
import re
import os

def random_string(length):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))

def random_integer_array(l, a, b):
    return [random_integer(a, b) for _ in range(l)]

def random_float_array(l, a, b):
    return [random_float(a, b) for _ in range(l)]

def random_bool():
    return random.choice([True, False])

def random_integer(a, b):
    return random.randint(a, b)

def random_float(a, b):
    return random.uniform(a, b)

# 讀取 JSON 檔案
def read_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

component_type = ['activity', 'service', 'receiver', 'provider']
# 主函數
commands = ['#!/bin/bash']
count = 0

def get_key(component_path, command_base):
    p = component_path.replace('.', '/')
    file_path = 'decompile/sources/' + p + '.java'

    # 檢查檔案是否存在
    if not os.path.exists(file_path):
        return []

    result = []

    with open(file_path, 'r', encoding='utf-8') as file:
        # 讀取文件內容並存儲到字符串中
        file_content = file.read()
    matches = re.findall(r'\"(.*?)\"', file_content)
    filtered_matches = [match for match in matches if match.isalnum() or match.replace('_', '').isalnum()]

    for i in filtered_matches:
        result.append(command_base + ' --ez ' + i + ' ' + str(random_bool()))
        result.append(command_base + ' --ef ' + i + ' ' + str(random_float(0, 100000)))
        result.append(command_base + ' --ei ' + i + ' ' + str(random_integer(0, 10000)))
        result.append(command_base + ' --es ' + i + ' ' + random_string(random_integer(2, 10)))
        result.append(command_base + ' --el ' + i + ' ' + str(random_integer(10000, 10000000)))

    return result

def main():
    global count
    json_data = read_json_file('exported_true_tags.json')
    package = json_data['manifest']['@package']
    print('now----------------------------------', package)
    with open('package_name.txt', 'w') as file:
        file.write(package)
    # manifest -> application

    # activity
    # any('mes' in item for item in a)
    for data in json_data['manifest']['application']:
        command_boot = 'start'
        if data == 'activity':
            command_boot = 'start'
        elif data == 'service':
            command_boot = 'startservice'
        elif data == 'provider':
            command_boot = 'broadcast'
        elif data == 'receiver':
            command_boot = 'broadcast'
        if data in component_type:
            for d in json_data['manifest']['application'][data]:
                if 'attr' in d.keys() and '@http://schemas.android.com/apk/res/android:exported' in d['attr'].keys() and d['attr']['@http://schemas.android.com/apk/res/android:exported'] == 'true' and '@http://schemas.android.com/apk/res/android:name' in d['attr']:
                    count = count + 1
                    # <activity />
                    component_path = d['attr']['@http://schemas.android.com/apk/res/android:name']
                    if 'MainActivity' in component_path:
                        continue
                    # null intent
                    command = 'adb shell am ' + command_boot + ' -n ' + package + '/' + component_path
                    commands.append(command)

                    # focus key
                    for c in get_key(component_path, command):
                        commands.append(c)

                    # 帶有隨機數據的 intent
                    command = ('adb shell am ' + command_boot + ' -n ' + package + '/' + component_path +
                               ' --es ' + random_string(random_integer(2, 7)) + ' ' + random_string(
                                random_integer(2, 10)) +
                               ' --ez ' + random_string(random_integer(2, 7)) + ' ' + str(random_bool()) +
                               ' --ei ' + random_string(random_integer(2, 7)) + ' ' + str(random_integer(0, 10000)) +
                               ' --el ' + random_string(random_integer(2, 7)) + ' ' + str(random_integer(10000, 10000000)) +
                               ' --ef ' + random_string(random_integer(2, 7)) + ' ' + str(random_float(0, 100000)))
                    commands.append(command)




                elif 'intent-filter' not in d.keys() and '@http://schemas.android.com/apk/res/android:exported' in d.keys() and d['@http://schemas.android.com/apk/res/android:exported'] == 'true' and '@http://schemas.android.com/apk/res/android:name' in d.keys():
                    count = count + 1
                    # <activity />
                    component_path = d['@http://schemas.android.com/apk/res/android:name']
                    if 'MainActivity' in component_path:
                        continue
                    # null intent
                    command = 'adb shell am ' + command_boot + ' -n ' + package + '/' + component_path
                    commands.append(command)

                    for c in get_key(component_path, command):
                        commands.append(c)

                    # 帶有隨機數據的 intent
                    command = ('adb shell am ' + command_boot + ' -n ' + package + '/' + component_path +
                               ' --es ' + random_string(random_integer(2, 7)) + ' ' + random_string(
                                random_integer(2, 10)) +
                               ' --ez ' + random_string(random_integer(2, 7)) + ' ' + str(random_bool()) +
                               ' --ei ' + random_string(random_integer(2, 7)) + ' ' + str(random_integer(0, 10000)) +
                               ' --el ' + random_string(random_integer(2, 7)) + ' ' + str(
                                random_integer(10000, 10000000)) +
                               ' --ef ' + random_string(random_integer(2, 7)) + ' ' + str(random_float(0, 100000)))
                    commands.append(command)

                elif 'intent-filter' in d.keys():
                    # <activity> <activity/>
                    if '@http://schemas.android.com/apk/res/android:name' in d.keys() and '@http://schemas.android.com/apk/res/android:exported' in d.keys() and d['@http://schemas.android.com/apk/res/android:exported'] == 'true':
                        count = count + 1
                        component_path = d['@http://schemas.android.com/apk/res/android:name']
                        if 'MainActivity' in component_path:
                            continue
                        command = 'adb shell am ' + command_boot + ' -n ' + package + '/' + component_path
                        if isinstance(d['intent-filter'], list):
                            for dd in d['intent-filter']:
                                # add category
                                if 'category' in dd.keys():
                                    if isinstance(dd['category'], list):
                                        is_first = True
                                        for ddd in dd['category']:
                                            if is_first:
                                                command = command + ' -c ' + ddd['attr']['@http://schemas.android.com/apk/res/android:name']
                                                is_first = False
                                            else:
                                                command = command + ', ' + ddd['attr']['@http://schemas.android.com/apk/res/android:name']
                                    elif isinstance(dd['category'], dict):
                                        command = command + ' -c ' + dd['category']['attr']['@http://schemas.android.com/apk/res/android:name']
                                if isinstance(dd['action'], list):
                                    for ddd in dd['action']:
                                        command = command + ' -a ' + ddd['attr']['@http://schemas.android.com/apk/res/android:name']
                                        for c in get_key(component_path, command):
                                            commands.append(c)
                                        # null intent
                                        temp = command
                                        temp= (temp +
                                         ' --es ' + random_string(random_integer(2, 7)) + ' ' + random_string(
                                                    random_integer(2, 10)) +
                                         ' --ez ' + random_string(random_integer(2, 7)) + ' ' + str(random_bool()) +
                                         ' --ei ' + random_string(random_integer(2, 7)) + ' ' + str(
                                                    random_integer(0, 10000)) +
                                         ' --el ' + random_string(random_integer(2, 7)) + ' ' + str(
                                                    random_integer(10000, 10000000)) +
                                         ' --ef ' + random_string(random_integer(2, 7)) + ' ' + str(
                                                    random_float(0, 100000)))
                                        commands.append(temp)


                                elif isinstance(dd['action'], dict):
                                    command = command + ' -a ' + dd['action']['attr']['@http://schemas.android.com/apk/res/android:name']
                                    for c in get_key(component_path, command):
                                        commands.append(c)
                                    # null intent
                                    temp = command
                                    temp = (temp +
                                            ' --es ' + random_string(random_integer(2, 7)) + ' ' + random_string(
                                                random_integer(2, 10)) +
                                            ' --ez ' + random_string(random_integer(2, 7)) + ' ' + str(random_bool()) +
                                            ' --ei ' + random_string(random_integer(2, 7)) + ' ' + str(
                                                random_integer(0, 10000)) +
                                            ' --el ' + random_string(random_integer(2, 7)) + ' ' + str(
                                                random_integer(10000, 10000000)) +
                                            ' --ef ' + random_string(random_integer(2, 7)) + ' ' + str(
                                                random_float(0, 100000)))
                                    commands.append(temp)
                        elif isinstance(d['intent-filter'], dict):
                            # add category
                            if 'category' in d['intent-filter'].keys():
                                if isinstance(d['intent-filter']['category'], list):
                                    is_first = True
                                    for dd in d['intent-filter']['category']:
                                        if is_first:
                                            command = command + ' -c ' + dd['attr'][ '@http://schemas.android.com/apk/res/android:name']
                                            is_first = False
                                        else:
                                            command = command + ', ' + dd['attr']['@http://schemas.android.com/apk/res/android:name']
                                elif isinstance(d['intent-filter']['category'], dict):
                                    command = command + ' -c ' + d['intent-filter']['category']['attr']['@http://schemas.android.com/apk/res/android:name']
                            if isinstance(d['intent-filter']['action'], list):
                                for dd in d['intent-filter']['action']:
                                    command = command + ' -a ' + dd['attr']['@http://schemas.android.com/apk/res/android:name']
                                    for c in get_key(component_path, command):
                                        commands.append(c)
                                    # null intent
                                    temp = command
                                    temp = (temp +
                                            ' --es ' + random_string(random_integer(2, 7)) + ' ' + random_string(
                                                random_integer(2, 10)) +
                                            ' --ez ' + random_string(random_integer(2, 7)) + ' ' + str(random_bool()) +
                                            ' --ei ' + random_string(random_integer(2, 7)) + ' ' + str(
                                                random_integer(0, 10000)) +
                                            ' --el ' + random_string(random_integer(2, 7)) + ' ' + str(
                                                random_integer(10000, 10000000)) +
                                            ' --ef ' + random_string(random_integer(2, 7)) + ' ' + str(
                                                random_float(0, 100000)))
                                    commands.append(temp)
                            elif isinstance(d['intent-filter']['action'], dict):
                                command = command + ' -a ' + d['intent-filter']['action']['attr']['@http://schemas.android.com/apk/res/android:name']
                                for c in get_key(component_path, command):
                                    commands.append(c)
                                # null intent
                                temp = command
                                temp = (temp +
                                        ' --es ' + random_string(random_integer(2, 7)) + ' ' + random_string(
                                            random_integer(2, 10)) +
                                        ' --ez ' + random_string(random_integer(2, 7)) + ' ' + str(random_bool()) +
                                        ' --ei ' + random_string(random_integer(2, 7)) + ' ' + str(
                                            random_integer(0, 10000)) +
                                        ' --el ' + random_string(random_integer(2, 7)) + ' ' + str(
                                            random_integer(10000, 10000000)) +
                                        ' --ef ' + random_string(random_integer(2, 7)) + ' ' + str(
                                            random_float(0, 100000)))
                                commands.append(temp)

    file_name = 'commands.sh'

    # 使用 with 語句打開文件進行寫入
    with open(file_name, 'w') as file:
        for item in commands:
            # 寫入每個元素，並在每個元素後添加換行符
            file.write(item + '\n')
    print('total intent :', len(commands))



# 執行主函數
if __name__ == "__main__":
    main()


