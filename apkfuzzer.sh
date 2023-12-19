#!/bin/bash

# 檢查是否安裝的函數
check_installed() {
    local all_installed=true
    echo "-----確認所需套件是否安裝..."

    # 檢查 adb
    if command -v adb >/dev/null 2>&1; then
        echo "v 已安裝 adb"
    else
        echo "x 未安裝 adb"
        all_installed=false
    fi

    # 檢查 aapt
    if command -v aapt >/dev/null 2>&1; then
        echo "v 已安裝 aapt"
    else
        echo "x 未安裝 aapt"
        all_installed=false
    fi

    # 檢查 apktool
    if command -v apktool >/dev/null 2>&1; then
        echo "v 已安裝 apktool"
    else
        echo "x 未安裝 apktool"
        all_installed=false
    fi

    # 檢查 jadx
    if command -v jadx >/dev/null 2>&1; then
        echo "v 已安裝 jadx"
    else
        echo "x 未安裝 jadx"
        all_installed=false
    fi

    # 檢查 xmllint
    if command -v xmllint >/dev/null 2>&1; then
        echo "v 已安裝 xmllint"
    else
        echo "x 未安裝 xmllint"
        all_installed=false
    fi

    # 檢查 xmlstarlet
    if command -v xmlstarlet >/dev/null 2>&1; then
        echo "v 已安裝 xmlstarlet"
    else
        echo "x 未安裝 xmlstarlet"
        all_installed=false
    fi

    # 檢查 python
    if command -v python >/dev/null 2>&1; then
        echo "v 已安裝 python"
    else
        echo "x 未安裝 python"
        all_installed=false
    fi

    echo "-----確認完畢"
    # 返回安裝狀態
    if [ "$all_installed" = true ]; then
        echo "v 已具備所有所需套件"
        return 0
    else
        echo "x 有套件尚未安裝"
        return 1
    fi
}

# 確認設備是否連接到主機
check_device_connected() {
    local devices=$(adb devices | grep -v "List" | grep "device")

    if [[ -z "$devices" ]]; then
        echo "x 尚未連接設備"
        return 1
    else
        echo "v 已檢測到設備"
        return 0
    fi
}

# 從 APK 提取包名的函數
extract_package_name() {
    local apk_path=$1
    # 使用 aapt 工具提取包名，這裡假設 aapt 已經安裝並且在 PATH 中
    local package_name=$(aapt dump badging "$apk_path" | grep "package:" | awk -F"'" '/package: name=/{print $2}')
    echo "$package_name"
}

# 安裝 APK 的函數
install_apk() {
    local apk_path=$1
    local apk_name=$(basename "$apk_path")
    local install_result=$(adb install "$apk_path" 2>&1)

    if [[ $install_result == *"Success"* ]]; then
        echo "v 安裝 $apk_name 成功"
        return 0  # 返回 true
    else
        echo "x 安裝 $apk_name 失敗：$install_result"
        return 1  # 返回 false
    fi
}

# 解除安裝 APK 的函數
uninstall_apk() {
    local apk_path=$1
    local apk_name=$(basename "$apk_path")
    local package_name=$(extract_package_name "$apk_path")
    local uninstall_result=$(adb uninstall "$package_name" 2>&1)

    if [[ $uninstall_result == *"Success"* ]]; then
        echo "v 解除安裝 $apk_name 成功"
        return 0  # 返回 true
    else
        echo "x 解除安裝 $apk_name 失敗：$uninstall_result"
        return 1  # 返回 false
    fi
}

# 反編譯 APK 並提取 AndroidManifest.xml 的函數
decompile_apk() {
    local apk_path=$1
    local apk_name=$(basename "$apk_path")
    local decompile_dir="decompiled_$apk_name"

    # 使用 apktool 反編譯 APK
    apktool d "$apk_path" --frame-path ./apktool_framework -o "$decompile_dir" --force

    # 檢查是否成功提取 AndroidManifest.xml
    if [ -f "$decompile_dir/AndroidManifest.xml" ]; then
        echo "v 提取 $apk_name 的 AndroidManifest.xml 成功"
        # 將 AndroidManifest.xml 移動到當前目錄
        mv "$decompile_dir/AndroidManifest.xml" "AndroidManifest.xml"
    else
        echo "x 提取 $apk_name 的 AndroidManifest.xml 失敗"
    fi

    # 刪除反編譯的目錄
    rm -rf "$decompile_dir"
}

# 清理 AndroidManifest.xml 的函數
cleanup_manifest() {
    local apk_name=$1
    local manifest_file="AndroidManifest.xml"
    local package_name="package_name.txt"
    local json_file="exported_true_tags.json"
    local commands="commands.sh"
    local decompile_dir="decompile"

    if [ -f "$manifest_file" ]; then
        rm "$manifest_file"
    fi
    if [ -f "$package_name" ]; then
        rm "$package_name"
    fi
    if [ -f "$json_file" ]; then
        rm "$json_file"
    fi
    if [ -f "$commands" ]; then
        rm "$commands"
    fi
    if [ -d "$decompile_dir" ]; then
        rm -r "$decompile_dir"
    fi
}


# 遍歷 apks 目錄並安裝卸載 APK-----------------------------------
process_apks() {
    rm -r report/*
    local apk_dir="apks"

    for apk in "$apk_dir"/*.apk; do
        if [ -f "$apk" ]; then
            local apk_name=$(basename "$apk")
            local logcat_file="${apk_name}_logcat.csv"
            if install_apk "$apk"; then
                # 反編譯 APK 
                decompile_apk "$apk"
                jadx -d decompile "$apk"
                python xml_to_json.py
                python generate_test.py

                # 開始 logcat 並將輸出重定向到臨時文件
                chmod 777 package_name.txt
                package_name=$(<package_name.txt)
                adb logcat *:E | grep "$package_name" > "$logcat_file" &

                # 獲取 logcat 的 PID
                local logcat_pid=$!

                # 執行 commands.sh 腳本
                chmod 777 commands.sh
                ./commands.sh

                # 停止 logcat
                kill $logcat_pid

                # 將日誌文件移動到指定位置
                mv "$logcat_file" "./report"

                if uninstall_apk "$apk"; then
                    echo "已完成 $apk 的安裝和解除安裝"
                    # 清理 AndroidManifest.xml
                    cleanup_manifest "$apk_name"
                else
                    echo "解除安裝 $apk 失敗"
                fi
            else
                echo "安裝 $apk 失敗"
            fi
        fi
    done
    python lcs_report.py
}


# 檢查命令行參數
case "$1" in
    --auto)
        echo "now is auto mode"
        # 判斷是否安裝所有必要套件
        if check_installed && check_device_connected; then
            echo "start"
            process_apks
        else
            echo "stop"
        fi
        ;;
    --manual)
        echo "now is manual mode"
        ;;
    --help)
        echo "使用方式："
        echo "./apkfuzzer.sh [參數]"
        echo "說明："
        echo "--auto : 自動 fuzzing 模式，測資會自動生成"
        echo "--manual : 手動模式，"
        ;;
    *)
        echo "Usage: $0 [--auto|--manual|--help]"
        exit 1
        ;;

esac