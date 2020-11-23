# !/usr/bin/python
# -*- coding: UTF-8 -*-
"""
Created on 2020-11-23
@author: aibingbing

通过命令adb shell getprop | grep abi 可以查看推荐的ABI类型
"""
import os
import zipfile
import shutil
import argparse

source_path = None
result_path = None

arg_parser = argparse.ArgumentParser(description='从Apk中提取so文件脚本')
arg_parser.add_argument('--src', '-s', help='Apk文件所在文件夹，必填项', required=True)
arg_parser.add_argument('--dist', '-d', help='so文件输出文件夹，非必要参数', required=False)
args = arg_parser.parse_args()


def extract_apks():
    apk_source_dir = os.listdir(source_path)
    apk_file_names = []
    for file_name in apk_source_dir:
        if file_name.endswith(".apk"):
            apk_file_names.append(file_name)

    if len(apk_file_names) <= 0:
        print("[{0}] has none apk file.".format(source_path))
        exit()
        return

    for apk in apk_file_names:
        print("[{0}] Start extract".format(apk))
        # apk name
        apk_name = os.path.splitext(apk)[0]
        # apk absolute path
        apk_absolute_path = os.path.join(source_path, apk)
        # apk extract temp path
        temp_apk_path = os.path.join(get_temp_extract_path(), apk_name)
        # extract apk to temp path
        extract_apk(apk_absolute_path, temp_apk_path)

        if has_lib_dir(temp_apk_path):
            # abi types in current apk
            so_platform_dirs = get_lib_children(temp_apk_path)
            print("[{0}] abi types: {1}".format(apk, ','.join(so_platform_dirs)))
            for so_type in so_platform_dirs:
                copy_so_files(so_type, apk_name)
            print("[{0}] extract success".format(apk))
        else:
            print("[{0}] abi types: None".format(apk))
            print("[{0}] passed because do not has lib dir".format(apk))
        shutil.rmtree(temp_apk_path)
    shutil.rmtree(get_temp_extract_path())


def has_lib_dir(temp_apk_path):
    return "lib" in [f for f in os.listdir(temp_apk_path) if not f.startswith('.')]


def get_lib_children(temp_apk_path):
    return [f for f in os.listdir(os.path.join(temp_apk_path, "lib")) if not f.startswith('.')]


def get_temp_extract_path():
    return os.path.join(source_path, "temp")


def get_temp_extract_lib_path(temp_extract_apk_path):
    return os.path.join(temp_extract_apk_path, "lib")


def extract_apk(apk_path, extract_dest_path):
    with zipfile.ZipFile(apk_path, mode="r") as zf:
        if not os.path.exists(extract_dest_path):
            os.makedirs(extract_dest_path)
        zf.extractall(path=extract_dest_path)


def copy_so_files(so_type, apk_name):
    so_source_file_path = os.path.join(get_temp_extract_lib_path(os.path.join(get_temp_extract_path(), apk_name)),
                                       so_type)
    so_dist_file_path = os.path.join(os.path.join(result_path, so_type), apk_name)
    shutil.copytree(src=so_source_file_path, dst=so_dist_file_path, ignore=shutil.ignore_patterns('.DS_Store'))


if __name__ == '__main__':
    if not os.path.isdir(args.src) or not os.path.exists(args.src):
        print("'[{0}]' is not a dir or not exists".format(args.src))
        exit()
    source_path = args.src

    if args.dist is None:
        result_path = os.path.join(source_path, "result")
    elif not os.path.isdir(args.dist) or not os.path.exists(args.dist):
        print("'[{0}]' is not a dir or not exists".format(args.dist))
        exit()
    else:
        result_path = args.dist

    print("Use Source Dir: [{0}]".format(source_path))
    print("Use Dist Dir: [{0}]".format(result_path))

    print("*******[Extract Start]********")
    extract_apks()
    print("*******[Extract End]*******")
