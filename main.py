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
            'name': 'MaiBot-模型配置文件',
            'path': get_absolute_path('modules/MaiBot/config/model_config.toml'),
            'template': get_absolute_path('modules/MaiBot/template/model_config_template.toml'),
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
            'template': get_absolute_path('modules/MaiBot-Napcat-Adapter/template/template_config.toml'),
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
    """检查是否是首次运行
    
    通过检查 runtime/.initialized 或 runtime/.gitkeep 文件是否存在来判断
    如果文件不存在则为首次运行,创建标记文件并返回 True
    """
    runtime_dir = Path(__file__) / "runtime"
    new_marker = runtime_dir / ".initialized"
    legacy_marker = runtime_dir / ".gitkeep"  # 兼容旧版本
    
    # 如果任一标记文件存在，则不是首次运行
    if new_marker.exists() or legacy_marker.exists():
        logger.info("检测到非首次运行 (标记文件存在)")
        return False
    
    # 首次运行:创建标记文件
    logger.info("首次运行检测: 未找到初始化标记文件,正在创建...")
    try:
        runtime_dir.mkdir(parents=True, exist_ok=True)
        new_marker.write_text('initialized', encoding='utf-8')
        logger.info("已创建初始化标记文件: .initialized")
    except Exception as e:
        logger.warning(f"创建初始化标记文件失败: {e}")
    
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
    """(弃用) 保留占位以兼容旧代码调用，直接返回 True"""
    logger.info("setup_webui_dependencies 已弃用，直接跳过。")
    return True

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
            
            # (已移除) 旧版 WebUI 依赖安装步骤已废弃
            
            print("======================")
            print("正在执行NapCat初始化脚本...")
            print("======================")
            
            if not run_python_script("init_napcat.py"):
                logger.error("NapCat初始化失败")
                return
            
            print("======================")
            print("正在配置QQ适配器...")
            print("======================")
            
            if not run_python_script("config_qq_adapter.py"):
                logger.error("QQ适配器配置失败")
                return
            
            print("3秒后启动MaiBot Client...")
            safe_system_command("timeout /t 3 /nobreak > nul")
            safe_system_command("cls")
            
            # 首次初始化后直接进入 start.py（主菜单/主逻辑）
            if not run_python_script("start.py"):
                logger.error("首次运行后启动主程序失败")
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