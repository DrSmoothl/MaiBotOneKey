# -*- coding: utf-8 -*-
"""
QQ适配器配置脚本
用于首次运行时配置QQ适配器相关设置
"""
import sys
from pathlib import Path
import toml

try:
    from modules.MaiBot.src.common.logger import get_logger
    logger = get_logger("qq_adapter_config")
except ImportError:
    import logging as logger
    logger.basicConfig(level=logger.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logger.getLogger("qq_adapter_config")


def get_config_path() -> Path:
    """获取配置文件路径"""
    script_dir = Path(__file__).parent
    config_path = script_dir / "modules" / "MaiBot-Napcat-Adapter" / "config.toml"
    return config_path


def read_config_with_comments(file_path: Path) -> tuple[dict, list[str]]:
    """读取配置文件,保留注释
    
    Returns:
        tuple: (配置字典, 原始文件行列表)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        config = toml.load(file_path)
        return config, lines
        
    except Exception as e:
        logger.error(f"读取配置文件失败: {e}")
        raise


def update_config_preserve_comments(file_path: Path, config: dict, original_lines: list[str]) -> bool:
    """更新配置文件,保留注释
    
    Args:
        file_path: 配置文件路径
        config: 更新后的配置字典
        original_lines: 原始文件行列表
        
    Returns:
        bool: 是否成功
    """
    try:
        new_lines = []
        in_section = None
        
        for line in original_lines:
            stripped = line.strip()
            
            # 检测section
            if stripped.startswith('[') and stripped.endswith(']'):
                section_name = stripped[1:-1].strip()
                in_section = section_name
                new_lines.append(line)
                continue
            
            # 保留注释和空行
            if stripped.startswith('#') or not stripped:
                new_lines.append(line)
                continue
            
            # 处理配置项
            if '=' in line and in_section:
                key = line.split('=')[0].strip()
                
                # 更新特定的配置项
                if in_section == 'chat':
                    if key == 'group_list':
                        indent = len(line) - len(line.lstrip())
                        group_list = config.get('chat', {}).get('group_list', [])
                        new_lines.append(' ' * indent + f'group_list = {group_list}\n')
                        continue
                    elif key == 'private_list':
                        indent = len(line) - len(line.lstrip())
                        private_list = config.get('chat', {}).get('private_list', [])
                        new_lines.append(' ' * indent + f'private_list = {private_list}\n')
                        continue
            
            # 保留其他行
            new_lines.append(line)
        
        # 写入文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        
        logger.info("配置文件已更新,注释已保留")
        return True
        
    except Exception as e:
        logger.error(f"更新配置文件失败: {e}")
        return False


def input_qq_list(prompt: str) -> list[int]:
    """交互式输入QQ号列表
    
    Args:
        prompt: 提示信息
        
    Returns:
        list: QQ号列表
    """
    print(f"\n{prompt}")
    print("请输入QQ号,多个号码用逗号或空格分隔")
    print("直接按回车跳过此项配置")
    print("-" * 50)
    
    user_input = input(">>> ").strip()
    
    if not user_input:
        logger.info("用户跳过此项配置")
        return []
    
    # 支持逗号和空格分隔
    qq_list = []
    separators = [',', '，', ' ', '\t']
    
    # 替换所有分隔符为空格
    for sep in separators:
        user_input = user_input.replace(sep, ' ')
    
    # 分割并转换为整数
    parts = user_input.split()
    for part in parts:
        try:
            qq_num = int(part.strip())
            if qq_num > 0:
                qq_list.append(qq_num)
            else:
                print(f"警告: 忽略无效的QQ号 '{part}'")
        except ValueError:
            print(f"警告: 忽略无效的输入 '{part}'")
    
    if qq_list:
        logger.info(f"已添加 {len(qq_list)} 个QQ号: {qq_list}")
        print(f"✓ 已添加 {len(qq_list)} 个号码")
    
    return qq_list


def configure_qq_adapter() -> bool:
    """配置QQ适配器
    
    Returns:
        bool: 配置是否成功
    """
    try:
        logger.info("开始配置QQ适配器")
        print("=" * 50)
        print("QQ适配器配置向导")
        print("=" * 50)
        print("\n本向导将帮助您配置群聊和私聊白名单")
        print("白名单模式: 只有在名单中的群组/用户可以与机器人聊天")
        
        # 获取配置文件路径
        config_path = get_config_path()
        
        if not config_path.exists():
            logger.error(f"配置文件不存在: {config_path}")
            print(f"\n错误: 配置文件不存在")
            return False
        
        # 读取配置文件
        config, original_lines = read_config_with_comments(config_path)
        
        # 确保chat section存在
        if 'chat' not in config:
            config['chat'] = {}
        
        # 配置群聊白名单
        group_list = input_qq_list("【群聊白名单配置】")
        config['chat']['group_list'] = group_list
        
        # 配置私聊白名单
        private_list = input_qq_list("【私聊白名单配置】")
        config['chat']['private_list'] = private_list
        
        # 保存配置
        print("\n正在保存配置...")
        if update_config_preserve_comments(config_path, config, original_lines):
            print("✓ 配置已保存")
            print(f"\n配置文件位置: {config_path}")
            print(f"群聊白名单: {len(group_list)} 个群组")
            print(f"私聊白名单: {len(private_list)} 个用户")
            logger.info("QQ适配器配置完成")
            return True
        else:
            print("✗ 保存配置失败")
            return False
        
    except Exception as e:
        logger.error(f"配置QQ适配器时发生错误: {e}")
        print(f"\n错误: {e}")
        return False


def main() -> None:
    """主函数"""
    try:
        if configure_qq_adapter():
            logger.info("QQ适配器配置成功")
            print("\nQQ适配器配置成功!")
        else:
            logger.error("QQ适配器配置失败")
            print("\nQQ适配器配置失败,请检查日志")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("用户中断配置过程")
        print("\n配置已被用户中断")
        sys.exit(1)
    except Exception as e:
        logger.error(f"配置过程中出现未知错误: {e}")
        print(f"\n配置失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
