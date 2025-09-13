# -*- coding: utf-8 -*-
import os
import re
import sys
import subprocess
import shutil
try:
    from modules.MaiBot.src.common.logger import get_logger
    logger = get_logger("init")
except ImportError:
    import logging as logger
    logger.basicConfig(level=logger.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logger.getLogger("init")

from pathlib import Path
from typing import Optional

def get_absolute_path(relative_path: str) -> str:
    """获取绝对路径
    
    Args:
        relative_path: 相对路径
        
    Returns:
        str: 绝对路径
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, relative_path)
def check_and_create_config_files() -> bool:
    """检测并创建所有必要的配置文件
    
    Returns:
        bool: 所有配置文件检测和创建是否成功
    """
    config_checks = [
        {
            'name': 'MaiBot配置目录',
            'path': get_absolute_path('modules/MaiBot/config'),
            'is_directory': True
        },
        {
            'name': 'MaiBot主配置文件',
            'path': get_absolute_path('modules/MaiBot/config/bot_config.toml'),  
            'template': get_absolute_path('modules/MaiBot/template/bot_config_template.toml'),
            'is_directory': False
        },
        {
            'name': 'MaiBot-LPMM配置文件',
            'path': get_absolute_path('modules/MaiBot/config/lpmm_config.toml'),
            'template': get_absolute_path('modules/MaiBot/template/lpmm_config_template.toml'),
            'is_directory': False
        },
        {
            'name': 'MaiBot环境文件',
            'path': get_absolute_path('modules/MaiBot/.env'),
            'template': get_absolute_path('modules/MaiBot/template/template.env'),
            'is_directory': False
        },
        {
            'name': 'NapCat适配器配置文件',
            'path': get_absolute_path('modules/MaiBot-Napcat-Adapter/config.toml'),
            'template': get_absolute_path('modules/MaiBot-Napcat-Adapter/template.toml'),
            'is_directory': False
        }
    ]
    
    all_success = True
    
    for config in config_checks:
        try:
            if config['is_directory']:
                # 检测目录
                if not os.path.exists(config['path']):
                    os.makedirs(config['path'], exist_ok=True)
                    logger.info(f"已创建目录: {config['name']}")
                else:
                    logger.info(f"目录已存在: {config['name']}")
            else:
                # 检测配置文件
                if not os.path.exists(config['path']):
                    if 'template' in config and os.path.exists(config['template']):
                        # 确保目标目录存在
                        target_dir = os.path.dirname(config['path'])
                        if not os.path.exists(target_dir):
                            os.makedirs(target_dir, exist_ok=True)
                        
                        # 复制模板文件
                        shutil.copy2(config['template'], config['path'])
                        logger.info(f"已从模板创建配置文件: {config['name']}")
                    else:
                        logger.warning(f"模板文件不存在，无法创建: {config['name']}")
                        logger.warning(f"模板路径: {config.get('template', '未指定')}")
                        all_success = False
                else:
                    logger.info(f"配置文件已存在: {config['name']}")
                    
        except Exception as e:
            logger.error(f"处理配置文件时出错 {config['name']}: {str(e)}")
            all_success = False
    
    if all_success:
        logger.info("所有配置文件检测完成！")
    else:
        logger.warning("部分配置文件处理失败，请检查上述错误信息")
    
    return all_success
# 配置日志

def get_python_interpreter() -> Optional[Path]:
    """获取Python解释器路径"""
    try:
        # 尝试多个可能的路径
        possible_paths = [
            Path(__file__).parent / "runtime" / "python31211" / "bin" / "python.exe",
            Path(__file__).parent / "runtime" / "python31211" / "python.exe",
            Path(sys.executable),  # 当前Python解释器
        ]
        
        for python_path in possible_paths:
            if python_path.exists() and python_path.is_file():
                logger.info(f"找到Python解释器: {python_path}")
                return python_path
        
        logger.error("未找到可用的Python解释器")
        return None
        
    except Exception as e:
        logger.error(f"获取Python解释器路径时出错: {e}")
        return None

def is_first_run() -> bool:
    """检查是否是首次运行"""
    try:
        # 标记文件路径: 主程序目录/runtime/.gitkeep
        marker = Path(__file__).parent / "runtime" / ".gitkeep"
        
        if not marker.exists():
            # 首次运行：创建runtime目录和标记文件
            marker.parent.mkdir(parents=True, exist_ok=True)
            marker.touch()  # 创建空文件
            logger.info("检测到首次运行，已创建标记文件")
            return True
        
        logger.info("检测到非首次运行")
        return False
        
    except Exception as e:
        logger.error(f"检查首次运行状态时出错: {e}")
        # 出错时默认为首次运行，确保初始化能正常进行
        return True

def run_python_script(script_name: str) -> bool:
    """运行同一目录下的Python脚本"""
    try:
        # 获取当前脚本目录
        current_dir = Path(__file__).parent
        
        # 构建目标脚本路径
        target_script = current_dir / script_name
        
        # 检查目标脚本是否存在
        if not target_script.exists():
            logger.error(f"目标脚本不存在: {target_script}")
            return False
        
        # 获取Python解释器路径
        python_path = get_python_interpreter()
        if python_path is None:
            logger.error("无法找到Python解释器")
            return False
        
        logger.info(f"开始执行脚本: {script_name}")
        
        # 执行目标脚本
        result = subprocess.run(
            [str(python_path), str(target_script)],
            capture_output=False,  # 保持输出到控制台
            text=True,
            timeout=30000,  # 5分钟超时
            cwd=str(current_dir)  # 设置工作目录
        )
        
        if result.returncode == 0:
            logger.info(f"脚本执行成功: {script_name}")
            return True
        else:
            logger.error(f"脚本执行失败: {script_name}, 返回码: {result.returncode}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error(f"脚本执行超时: {script_name}")
        return False
    except FileNotFoundError as e:
        logger.error(f"文件未找到: {e}")
        return False
    except Exception as e:
        logger.error(f"执行脚本时出错: {script_name}, 错误: {e}")
        return False

def safe_system_command(command: str, timeout: int = 30) -> bool:
    """安全地执行系统命令
    
    Args:
        command: 要执行的命令
        timeout: 超时时间（秒）
        
    Returns:
        bool: 命令执行是否成功
    """
    try:
        logger.info(f"执行系统命令: {command}")
        result = subprocess.run(
            command,
            shell=True,
            timeout=timeout,
            capture_output=False,
            text=True
        )
        
        if result.returncode == 0:
            logger.info(f"系统命令执行成功: {command}")
            return True
        else:
            logger.warning(f"系统命令执行失败: {command}, 返回码: {result.returncode}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error(f"系统命令执行超时: {command}")
        return False
    except Exception as e:
        logger.error(f"执行系统命令时出错: {command}, 错误: {e}")
        return False

def setup_webui_dependencies() -> bool:
    """设置WebUI的默认运行路径和安装依赖
    
    Returns:
        bool: 安装是否成功
    """
    try:
        # 获取路径
        current_dir = Path(__file__).parent
        nodejs_dir = current_dir / "runtime" / "nodejs"
        pnpm_path = nodejs_dir / "pnpm.cmd"
        hmml_demon_dir = current_dir / "modules" / "HMMLDemon"
        
        # 检查必要路径是否存在
        if not nodejs_dir.exists():
            logger.error(f"Node.js 路径不存在: {nodejs_dir}")
            return False
            
        if not pnpm_path.exists():
            logger.error(f"pnpm 可执行文件不存在: {pnpm_path}")
            return False
            
        if not hmml_demon_dir.exists():
            logger.error(f"HMMLDemon 模块路径不存在: {hmml_demon_dir}")
            return False
        
        logger.info("开始设置 WebUI 依赖...")
        print("======================")
        print("正在设置 WebUI 依赖...")
        print("======================")
        
        # 设置环境变量，将 Node.js 路径添加到 PATH
        env = os.environ.copy()
        env['PATH'] = str(nodejs_dir) + os.pathsep + env.get('PATH', '')
        
        # 定义可用的 npm 源
        npm_registries = [
            {"name": "淘宝源", "url": "https://registry.npmmirror.com"},
            {"name": "腾讯源", "url": "https://mirrors.cloud.tencent.com/npm/"},
            {"name": "华为源", "url": "https://repo.huaweicloud.com/repository/npm/"},
            {"name": "官方源", "url": "https://registry.npmjs.org"}
        ]
        
        # 最大重试次数
        max_retries = len(npm_registries)
        
        for attempt in range(max_retries):
            registry = npm_registries[attempt]
            logger.info(f"尝试使用 {registry['name']}: {registry['url']} (第 {attempt + 1}/{max_retries} 次)")
            print(f"尝试使用 {registry['name']}: {registry['url']} (第 {attempt + 1}/{max_retries} 次)")
            
            try:
                # 设置 npm 源
                set_registry_cmd = f'"{pnpm_path}" config set registry {registry["url"]}'
                logger.info(f"设置 npm 源: {set_registry_cmd}")
                
                result = subprocess.run(
                    set_registry_cmd,
                    shell=True,
                    timeout=30,
                    capture_output=True,
                    text=True,
                    cwd=str(hmml_demon_dir),
                    env=env
                )
                
                if result.returncode != 0:
                    logger.warning(f"设置 npm 源失败: {result.stderr}")
                    continue
                
                logger.info(f"成功设置 npm 源为: {registry['name']}")
                
                # 执行 pnpm install
                install_cmd = f'"{pnpm_path}" install'
                logger.info(f"执行 pnpm install: {install_cmd}")
                print(f"正在使用 {registry['name']} 安装依赖...")
                
                result = subprocess.run(
                    install_cmd,
                    shell=True,
                    timeout=600,  # 10分钟超时
                    capture_output=False,  # 保持输出到控制台
                    text=True,
                    cwd=str(hmml_demon_dir),
                    env=env
                )
                
                if result.returncode == 0:
                    logger.info(f"使用 {registry['name']} 成功安装 WebUI 依赖")
                    print(f"✓ 使用 {registry['name']} 成功安装 WebUI 依赖")
                    return True
                else:
                    logger.warning(f"使用 {registry['name']} 安装依赖失败，返回码: {result.returncode}")
                    print(f"✗ 使用 {registry['name']} 安装依赖失败，尝试下一个源...")
                    
            except subprocess.TimeoutExpired:
                logger.error(f"使用 {registry['name']} 安装依赖超时")
                print(f"✗ 使用 {registry['name']} 安装依赖超时，尝试下一个源...")
                continue
            except Exception as e:
                logger.error(f"使用 {registry['name']} 安装依赖时出错: {e}")
                print(f"✗ 使用 {registry['name']} 安装依赖时出错: {e}")
                continue
        
        # 所有源都失败了
        logger.error("所有 npm 源都尝试失败，WebUI 依赖安装失败")
        print("✗ 所有 npm 源都尝试失败，WebUI 依赖安装失败")
        print("请检查网络连接或手动安装依赖")
        return False
        
    except Exception as e:
        logger.error(f"设置 WebUI 依赖时出现未知错误: {e}")
        print(f"✗ 设置 WebUI 依赖时出现未知错误: {e}")
        return False

def check_dir_legal() -> bool:
    """检查当前目录是否包含中文等特殊字符
    
    Returns:
        bool: True表示目录包含非法字符，False表示目录合法
    """
    try:
        # 获取当前工作目录
        current_path = os.getcwd()
        
        # 检查路径是否包含中文字符（Unicode范围）
        has_chinese = bool(re.search(r'[\u3000-\u303f\u4e00-\u9fff\uff00-\uffef]', current_path))
        
        if has_chinese:
            error_msg = f"警告：当前路径包含中文等特殊字符: {current_path}"
            print(error_msg)
            print("禁止启动，已自动退出，请将一键包移动到非中文目录再启动！")
            logger.error(error_msg)
            logger.error("程序因路径包含特殊字符而退出")
            return True
        else:
            logger.info(f"路径检查通过: {current_path}")
            return False
            
    except Exception as e:
        error_msg = f"检查目录路径时出错: {e}"
        print(error_msg)
        logger.error(error_msg)
        # 出错时为安全起见，认为路径不合法
        return True

def main() -> None:
    """主函数"""
    try:
        logger.info("MaiBot 一键包启动")
        check_and_create_config_files()
        
        # 检查目录路径合法性
        if check_dir_legal():
            logger.error("目录路径不合法，程序退出")
            sys.exit(1)
        
        # 检查是否首次运行
        if is_first_run():
            # 初始化一键包
            logger.info("首次运行一键包，执行初始化操作")
            print("首次运行一键包，执行初始化操作……")
            
            if not run_python_script("update_modules.py"):
                logger.error("模块更新失败")
                return
            
            # 设置 WebUI 依赖
            if not setup_webui_dependencies():
                logger.warning("WebUI 依赖安装失败，但程序将继续运行")
                print("警告：WebUI 依赖安装失败，WebUI 功能可能不可用")
            
            print("======================")
            print("正在执行NapCat初始化脚本...")
            print("======================")
            
            if not run_python_script("init_napcat.py"):
                logger.error("NapCat初始化失败")
                return
            
            # 直接启动 HMML WebUI 让用户进行交互配置
            print("======================")
            print("首次运行：即将启动 HMML WebUI 进行配置，请在浏览器中完成操作。")
            print("如未自动打开，可手动访问: http://localhost:7998")
            print("======================")

            # 内联一个最小化的 HMML WebUI 启动逻辑（避免循环导入）
            def _first_launch_hmml_webui():
                import subprocess
                from pathlib import Path
                base_dir = Path(__file__).parent

                # 新版结构
                new_frontend = base_dir / 'modules' / 'HMML2Panel'
                new_backend = base_dir / 'modules' / 'HMML2Backend'
                new_node = new_frontend / 'node.exe'
                new_server = new_frontend / 'server.cjs'
                new_backend_entry = new_backend / 'start.py'

                # 旧版结构
                old_frontend = base_dir / 'modules' / 'HMMLPanel'
                old_backend = base_dir / 'modules' / 'HMMLDemon'
                old_node = base_dir / 'runtime' / 'nodejs' / 'node.exe'
                old_server = old_frontend / 'server.cjs'
                old_backend_js = old_backend / 'start.js'

                # Python 解释器候选
                py_candidates = [
                    base_dir / 'runtime' / 'python31211' / 'python.exe',
                    base_dir / 'runtime' / 'python31211' / 'bin' / 'python.exe'
                ]
                python_path = next((str(p) for p in py_candidates if p.exists()), None)

                def _create_cmd_window(cwd: Path, command: str) -> bool:
                    try:
                        subprocess.Popen(command, cwd=str(cwd), shell=True)
                        return True
                    except Exception as _e:
                        logger.error(f"创建命令窗口失败: {command} 错误: {_e}")
                        return False

                # 优先新版
                if new_frontend.is_dir() and new_backend.is_dir():
                    if not new_node.exists() or not new_server.exists() or not new_backend_entry.exists():
                        logger.error("HMML2 目录存在但缺少必要文件 (node.exe/server.cjs/start.py)")
                        return False
                    if not python_path:
                        logger.error("未找到 Python 解释器，无法启动 HMML2 后端")
                        return False
                    front_cmd = f'start http://localhost:7998 && "{new_node}" "{new_server}"'
                    back_cmd = f'"{python_path}" "{new_backend_entry}"'
                    ok1 = _create_cmd_window(new_frontend, front_cmd)
                    ok2 = _create_cmd_window(new_backend, back_cmd) if ok1 else False
                    if ok1 and ok2:
                        logger.info("HMML2 WebUI 已启动 (前端+后端)")
                        return True
                    logger.error("HMML2 WebUI 启动失败")
                    return False
                # 回退旧版
                if old_frontend.is_dir() and old_backend.is_dir():
                    if not old_node.exists() or not old_server.exists() or not old_backend_js.exists():
                        logger.error("旧版 HMML 目录缺少必要文件 (node.exe/server.cjs/start.js)")
                        return False
                    front_cmd = f'start http://localhost:7998 && "{old_node}" server.cjs'
                    back_cmd = f'"{old_node}" start.js'
                    ok1 = _create_cmd_window(old_frontend, front_cmd)
                    ok2 = _create_cmd_window(old_backend, back_cmd) if ok1 else False
                    if ok1 and ok2:
                        logger.info("旧版 HMML WebUI 已启动")
                        return True
                    logger.error("旧版 HMML WebUI 启动失败")
                    return False
                logger.error("未找到任何可用的 HMML WebUI 结构 (HMML2 或 旧版)")
                return False

            if not _first_launch_hmml_webui():
                print("启动 HMML WebUI 失败，可稍后从菜单手动启动。")
                logger.error("首次运行时启动 HMML WebUI 失败")
                
            print("3秒后启动MaiBot Client...")
            safe_system_command("timeout /t 3 /nobreak > nul")
            safe_system_command("cls")
            
            if not run_python_script("main.py"):
                logger.error("MaiBot启动失败")
                return
        else:
            # 非首次运行
            logger.info("检测到不是首次运行，正在跳过向导启动 MaiBot Core")
            print("检测到不是首次运行，正在跳过向导启动 MaiBot Core...")
            
            if not run_python_script("start.py"):
                logger.error("启动主程序失败")
                return
                
        logger.info("程序执行完成")
        
    except KeyboardInterrupt:
        logger.info("用户中断程序执行")
        print("\n程序已被用户中断")
    except Exception as e:
        logger.error(f"程序执行过程中出现未知错误: {e}")
        print(f"程序执行失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()