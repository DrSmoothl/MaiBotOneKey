# -*- coding: utf-8 -*-
"""
模块更新脚本
功能：更新所有模块的git仓库并安装依赖包
支持参数：
- --only-onekey: 仅更新一键包仓库
- 无参数: 更新所有模块

特性：
- 支持多个备用远程仓库，当一个仓库无法访问时自动尝试下一个
- 在拉取前强制设置远程仓库为指定的仓库地址
- 自动安装requirements.txt中的依赖包
"""

import os
import subprocess
import sys
from pathlib import Path

def get_git_command():
    """获取可用的git命令路径"""
    # 获取脚本所在目录（项目根目录）
    script_dir = Path(__file__).parent.absolute()
    
    # 检查内置git
    portable_git = script_dir / 'runtime' / 'PortableGit' / 'bin' / 'git.exe'
    
    if portable_git.exists():
        print(f"✅ 找到内置Git: {portable_git}")
        return str(portable_git)
    
    # 检查系统git
    try:
        result = subprocess.run(
            ['git', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"✅ 找到系统Git: git")
            return 'git'
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass
    
    # 都没找到
    print("❌ 错误: 未找到Git命令！")
    print("请确保满足以下条件之一：")
    print(f"  1. 内置Git存在: {portable_git}")
    print("  2. 系统已安装Git并添加到PATH环境变量")
    return None

# 全局变量存储git命令
GIT_COMMAND = None

def run_command(command, cwd=None, description="", realtime_output=False):
    """执行命令"""
    try:
        if description:
            print(f"正在执行: {description}")
        print(f"命令: {command} (目录: {cwd if cwd else '当前目录'})")
        
        # 设置环境变量以确保正确的编码
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        env['LANG'] = 'zh_CN.UTF-8'
        
        if realtime_output:
            # 实时输出模式
            process = subprocess.Popen(
                command,
                cwd=cwd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='ignore',
                env=env,
                bufsize=1,  # 行缓冲
                universal_newlines=True
            )
            
            # 实时读取并输出
            output_lines = []
            while True:
                line = process.stdout.readline()
                if line:
                    line = line.rstrip('\n\r')
                    print(line)
                    output_lines.append(line)
                elif process.poll() is not None:
                    break
            
            # 等待进程完成
            return_code = process.wait()
            
            if return_code == 0:
                print("✅ 执行完成")
                return True
            else:
                print(f"❌ 执行失败，返回码: {return_code}")
                return False
        else:
            # 原有的缓冲输出模式
            result = subprocess.run(
                command,
                cwd=cwd,
                shell=True,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',  # 忽略编码错误
                env=env
            )
            
            if result.returncode == 0:
                if result.stdout and result.stdout.strip():
                    print(f"✅ 成功: {result.stdout.strip()}")
                else:
                    print("✅ 成功")
                return True
            else:
                error_msg = result.stderr.strip() if result.stderr else "未知错误"
                print(f"❌ 错误: {error_msg}")
                return False
    except Exception as e:
        print(f"❌ 执行命令时发生异常: {e}")
        return False

def run_git_command(repo_path, command):
    """在指定目录执行git命令"""
    global GIT_COMMAND
    
    # 如果还没有检测git命令，先检测
    if GIT_COMMAND is None:
        GIT_COMMAND = get_git_command()
        if GIT_COMMAND is None:
            return False
    
    # 替换命令中的git为具体的git路径
    if command.startswith('git '):
        git_command = command.replace('git ', f'"{GIT_COMMAND}" ', 1)
    else:
        git_command = command
    
    # 为Git命令添加SSL和网络配置，解决证书验证问题
    # 这些配置只对网络相关的Git操作有效
    if any(cmd in command for cmd in ['fetch', 'pull', 'push', 'clone', 'remote']):
        # 设置Git配置以解决SSL证书问题
        git_config_commands = [
            f'"{GIT_COMMAND}" config http.sslverify false',
            f'"{GIT_COMMAND}" config http.sslbackend schannel',
            f'"{GIT_COMMAND}" config http.schannelCheckRevoke false',
            f'"{GIT_COMMAND}" config http.schannelUseSSLCAInfo false'
        ]
        
        # 先设置Git配置
        for config_cmd in git_config_commands:
            run_command(config_cmd, repo_path)
    
    return run_command(git_command, repo_path)

def install_requirements(repo_path, repo_name):
    """安装requirements.txt中的依赖"""
    requirements_file = os.path.join(repo_path, 'requirements.txt')
    
    if not os.path.exists(requirements_file):
        print(f"📋 {repo_name} 没有requirements.txt文件，跳过依赖安装")
        return True
    
    print(f"\n{'='*40}")
    print(f"正在安装 {repo_name} 的依赖")
    print(f"{'='*40}")
    
    # 获取Python可执行文件路径
    python_cmd = sys.executable
    # 安装依赖（使用阿里云镜像源，禁用进度条避免编码问题）
    install_cmd = f'"{python_cmd}" -m pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com --upgrade --no-color --disable-pip-version-check --progress-bar off'
    success = run_command(install_cmd, repo_path, f"安装 {repo_name} 依赖", realtime_output=True)
    
    if success:
        print(f"✅ {repo_name} 依赖安装完成")
    else:
        print(f"❌ {repo_name} 依赖安装失败")
    
    return success

def update_repository(repo_path, repo_name, remote_urls=None, force_reset=False):
    """更新单个仓库，支持多个备用远程仓库，支持强制覆盖本地更改"""
    print(f"\n{'='*50}")
    print(f"正在更新 {repo_name}")
    print(f"路径: {repo_path}")
    print(f"{'='*50}")
    
    if not os.path.exists(repo_path):
        print(f"❌ 错误: 仓库路径不存在: {repo_path}")
        return False
    
    if not os.path.exists(os.path.join(repo_path, '.git')):
        print(f"❌ 错误: 不是git仓库: {repo_path}")
        return False

    # 如果需要强制覆盖本地更改，先执行 reset --hard 和 clean -fd
    if force_reset:
        print("⚠️  一键包将强制覆盖所有本地更改（包括未提交和已暂存的修改，配置文件和数据文件夹不在这个范围），此操作不可逆！")
        print("⚠️  如果你是第一次启动,请忽略此提示。")
        confirm = input("是否继续？输入 y 确认，其他键取消: ").strip().lower()
        if confirm != 'y':
            print("用户取消强制更新操作。")
            return False
        print("\n正在放弃所有本地更改并强制拉取最新代码...")
        if not run_git_command(repo_path, 'git reset --hard'):
            print("❌ git reset --hard 失败")
            return False
        if not run_git_command(repo_path, 'git clean -fd'):
            print("❌ git clean -fd 失败")
            return False
        # 跳过 fetch --all，因为后面会设置新的远程仓库并拉取

    # 如果提供了远程URL列表，尝试每个URL直到成功
    pull_success = False
    if remote_urls:
        # 确保remote_urls是列表
        if isinstance(remote_urls, str):
            remote_urls = [remote_urls]
        
        for i, remote_url in enumerate(remote_urls):
            print(f"尝试远程仓库 {i+1}/{len(remote_urls)}: {remote_url}")
            
            # 设置远程仓库
            if run_git_command(repo_path, f"git remote set-url origin {remote_url}"):
                print(f"✅ 成功设置远程仓库: {remote_url}")
                
                # 尝试拉取
                print("正在拉取最新代码...")
                if force_reset:
                    # 强制拉取远程最新代码并覆盖本地
                    # 先fetch获取最新的远程引用
                    if run_git_command(repo_path, 'git fetch origin'):
                        print("✅ 成功获取远程更新")
                        # 然后强制重置到远程分支
                        if (run_git_command(repo_path, 'git reset --hard origin/main') or 
                            run_git_command(repo_path, 'git reset --hard origin/master') or
                            run_git_command(repo_path, 'git pull --rebase') or 
                            run_git_command(repo_path, 'git pull')):
                            print(f"✅ {repo_name} 强制更新完成")
                            pull_success = True
                            break
                        else:
                            print("❌ 强制重置失败，尝试下一个仓库")
                    else:
                        print("❌ 获取远程更新失败，尝试下一个仓库")
                else:
                    if run_git_command(repo_path, "git pull"):
                        print(f"✅ {repo_name} 更新完成")
                        pull_success = True
                        break
                    else:
                        print(f"❌ 从 {remote_url} 拉取失败，尝试下一个仓库")            
            else:
                print(f"❌ 设置远程仓库失败: {remote_url}")
        
        if not pull_success:
            print(f"❌ 所有远程仓库都无法访问，{repo_name} 更新失败")
            return False
    else:
        # 没有提供远程URL，直接使用现有的远程仓库
        print("使用现有远程仓库进行更新")
        print("正在拉取最新代码...")
        if not run_git_command(repo_path, "git pull"):
            print(f"❌ {repo_name} 更新失败")
            return False
        else:
            print(f"✅ {repo_name} 更新完成")
            pull_success = True
    
    # 检查git状态
    print("检查仓库状态...")
    if not run_git_command(repo_path, "git status --porcelain"):
        return False
    
    # 获取当前分支
    print("获取当前分支...")
    result = subprocess.run(
        "git branch --show-current",
        cwd=repo_path,
        shell=True,
        capture_output=True,
        text=True,
        encoding='utf-8'
    )
    
    if result.returncode == 0:
        current_branch = result.stdout.strip()
        print(f"当前分支: {current_branch}")
    else:
        print("无法获取当前分支")
        current_branch = "main"
    
    return pull_success

def main():
    """主函数"""
    # 检查命令行参数
    only_onekey = len(sys.argv) > 1 and sys.argv[1] == "--only-onekey"
    
    if only_onekey:
        print("开始更新一键包仓库...")
    else:
        print("开始更新所有模块...")
    
    print(f"当前工作目录: {os.getcwd()}")
    
    # 初始化Git检测
    global GIT_COMMAND
    print("\n正在检测Git环境...")
    GIT_COMMAND = get_git_command()
    if GIT_COMMAND is None:
        print("❌ Git环境检测失败，无法继续")
        return 1
    
    # 获取脚本所在目录（项目根目录）
    script_dir = Path(__file__).parent.absolute()
    
    # 硬编码的远程仓库URL（支持多个备用仓库）
    REMOTE_URLS = {
        'onekey': [
            'https://gh.llkk.cc/https://github.com/DrSmoothl/MaiBotOneKey.git',
            'https://github.moeyy.xyz/https://github.com/DrSmoothl/MaiBotOneKey.git',
            'https://gitproxy.click/https://github.com/DrSmoothl/MaiBotOneKey.git',
            'https://gitproxy.net/https://github.com/DrSmoothl/MaiBotOneKey.git',
            'https://github.com/DrSmoothl/MaiBotOneKey.git'
        ],
        'maibot': [
            'https://gh.llkk.cc/https://github.com/MaiM-with-u/MaiBot.git',
            'https://github.moeyy.xyz/https://github.com/MaiM-with-u/MaiBot.git',
            'https://gitproxy.click/https://github.com/MaiM-with-u/MaiBot.git',
            'https://gitproxy.net/https://github.com/MaiM-with-u/MaiBot.git',
            'https://github.com/MaiM-with-u/MaiBot.git',
        ],
        'adapter': [
            'https://gh.llkk.cc/https://github.com/UnCLAS-Prommer/MaiBot-Napcat-Adapter.git',
            'https://github.moeyy.xyz/https://github.com/UnCLAS-Prommer/MaiBot-Napcat-Adapter.git',
            'https://gitproxy.click/https://github.com/UnCLAS-Prommer/MaiBot-Napcat-Adapter.git',
            'https://gitproxy.net/https://github.com/UnCLAS-Prommer/MaiBot-Napcat-Adapter.git',
            'https://github.com/UnCLAS-Prommer/MaiBot-Napcat-Adapter.git'
        ]
    }
      # 定义要更新的仓库
    if only_onekey:
        repositories = [
            {
                'name': '一键包主仓库',
                'path': script_dir,
                'remote_urls': REMOTE_URLS['onekey'],
                'force_reset': True
            }
        ]
    else:
        repositories = [
            {
                'name': '一键包主仓库',
                'path': script_dir,
                'remote_urls': REMOTE_URLS['onekey'],
                'force_reset': True
            },
            {
                'name': 'MaiBot主仓库',
                'path': script_dir / 'modules' / 'MaiBot',
                'remote_urls': REMOTE_URLS['maibot'],
                'force_reset': True
            },
            {
                'name': 'MaiBot-Napcat-Adapter适配器仓库',
                'path': script_dir / 'modules' / 'MaiBot-Napcat-Adapter',
                'remote_urls': REMOTE_URLS['adapter'],
                'force_reset': True
            }
        ]
    
    total_count = len(repositories)
    update_success_count = 0
    install_success_count = 0
      # 第一阶段：逐个更新仓库
    print(f"\n{'='*60}")
    print("第一阶段：更新Git仓库")
    print(f"{'='*60}")
    
    for repo in repositories:
        if update_repository(str(repo['path']), repo['name'], repo['remote_urls'], repo['force_reset']):
            update_success_count += 1
    
    # 第二阶段：安装依赖
    print(f"\n{'='*60}")
    print("第二阶段：安装依赖包")
    print(f"{'='*60}")
    
    for repo in repositories:
        if install_requirements(str(repo['path']), repo['name']):
            install_success_count += 1
    
    # 输出总结
    print(f"\n{'='*60}")
    if only_onekey:
        print(f"一键包仓库更新完成！Git更新: {update_success_count}/{total_count}")
    else:
        print(f"更新完成！Git更新: {update_success_count}/{total_count}")
    print(f"依赖安装: {install_success_count}/{total_count}")
    print(f"{'='*60}")
    
    if update_success_count == total_count and install_success_count == total_count:
        if only_onekey:
            print("🎉 一键包仓库更新和依赖安装成功！")
        else:
            print("🎉 所有模块更新和依赖安装成功！")
        return 0
    elif update_success_count == total_count:
        print("✅ 所有模块更新成功，但部分依赖安装失败")
        return 1
    else:
        print("⚠️  部分模块更新失败，请检查错误信息")
        return 1

def update_onekey_only():
    """仅更新一键包仓库的便捷函数"""
    sys.argv = [sys.argv[0], "--only-onekey"]  # 设置参数
    return main()

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n用户取消操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n程序执行过程中发生未知错误: {e}")
        sys.exit(1)
