import re
import json
import tomlkit  # 替换 tomli
from pathlib import Path

def is_valid_qq(qq_str):
    # 检查是否为纯数字
    return bool(re.match(r'^\d+$', qq_str))

def get_available_versions():
    """获取可用的QQ版本列表"""
    versions = []
    
    # 检查napcat目录中的版本
    napcat_versions_dir = Path('./modules/napcat/versions')
    if napcat_versions_dir.exists():
        versions.extend([
            version_dir.name for version_dir in napcat_versions_dir.iterdir()
            if version_dir.is_dir() and version_dir.name != 'config.json'
        ])
    
    # 检查napcatframework目录中的版本（合并去重）
    napcatframework_versions_dir = Path('./modules/napcatframework/versions')
    if napcatframework_versions_dir.exists():
        framework_versions = [
            version_dir.name for version_dir in napcatframework_versions_dir.iterdir()
            if version_dir.is_dir() and version_dir.name != 'config.json' and version_dir.name not in versions
        ]
        versions.extend(framework_versions)
    
    return sorted(versions)

def create_napcat_config(qq_number):
    # 创建napcat配置文件
    config = {
        "fileLog": False,
        "consoleLog": True,
        "fileLogLevel": "debug",
        "consoleLogLevel": "info",
        "packetBackend": "auto",
        "packetServer": "",
        "o3HookMode": 1
    }
    
    # 获取所有可用版本
    available_versions = get_available_versions()
    
    if not available_versions:
        print("警告：未找到任何QQ版本，使用默认版本")
        available_versions = ["9.9.19-34740"]
    
    print(f"找到 {len(available_versions)} 个QQ版本：{', '.join(available_versions)}")
    
    # 为每个版本创建配置文件
    for version in available_versions:
        # napcat路径
        config_dir_1 = Path(f'./modules/napcat/versions/{version}/resources/app/napcat/config')
        config_dir_1.mkdir(parents=True, exist_ok=True)
        
        config_path_1 = config_dir_1 / f'napcat_{qq_number}.json'
        with open(config_path_1, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print(f"已创建napcat配置文件：{config_path_1}")

        # napcatframework路径
        config_dir_2 = Path(f'./modules/napcatframework/versions/{version}/resources/app/LiteLoader/plugins/NapCat/config')
        config_dir_2.mkdir(parents=True, exist_ok=True)

        config_path_2 = config_dir_2 / f'napcat_{qq_number}.json'
        with open(config_path_2, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print(f"已创建napcatframework配置文件：{config_path_2}")

def create_onebot_config(qq_number):
    # 创建OneBot11配置文件
    config = {
    "network": {
        "httpServers": [],
        "httpSseServers": [],
        "httpClients": [],
        "websocketServers": [],
        "websocketClients": [
            {
                "enable": True,
                "name": "MaiBot Main",
                "url": "ws://localhost:8095",
                "reportSelfMessage": False,
                "messagePostFormat": "array",
                "token": "",
                "debug": False,
                "heartInterval": 30000,
                "reconnectInterval": 30000
            }
        ],
        "plugins": []
    },
    "musicSignUrl": "",
    "enableLocalFile2Url": False,
    "parseMultMsg": False
    }
    
    # 获取所有可用版本
    available_versions = get_available_versions()
    
    if not available_versions:
        print("警告：未找到任何QQ版本，使用默认版本")
        available_versions = ["9.9.19-34740"]
    
    print(f"为 {len(available_versions)} 个版本创建OneBot11配置")
    
    # 为每个版本创建配置文件
    for version in available_versions:
        # napcat路径
        config_dir_1 = Path(f'./modules/napcat/versions/{version}/resources/app/napcat/config')
        config_dir_1.mkdir(parents=True, exist_ok=True)
        
        config_path_1 = config_dir_1 / f'onebot11_{qq_number}.json'
        with open(config_path_1, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print(f"已创建OneBot11配置文件：{config_path_1}")

        # napcatframework路径
        config_dir_2 = Path(f'./modules/napcatframework/versions/{version}/resources/app/LiteLoader/plugins/NapCat/config')
        config_dir_2.mkdir(parents=True, exist_ok=True)

        config_path_2 = config_dir_2 / f'onebot11_{qq_number}.json'
        with open(config_path_2, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print(f"已创建OneBot11配置文件：{config_path_2}")

def update_qq_in_config(path: str, qq_number: int):  # 确保 qq_number 是整数
    config_path = Path(path)
    
    # 如果配置文件不存在，尝试从模板创建
    if not config_path.exists() and 'config' in str(config_path):
        template_path = config_path.parent.parent / 'template' / config_path.name.replace('bot_config.toml', 'bot_config_template.toml')
        if template_path.exists():
            # 确保配置目录存在
            config_path.parent.mkdir(parents=True, exist_ok=True)
            # 从模板复制配置文件
            import shutil
            shutil.copy2(template_path, config_path)
            print(f"已从模板创建配置文件: {config_path}")
    
    try:
        # 读取原始文件内容
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 解析 TOML 内容
        doc = tomlkit.parse(content)
        
        # 更新 qq 值
        if 'bot' not in doc:
            doc['bot'] = tomlkit.table()  # 如果 bot 表不存在则创建
        doc['bot']['qq_account'] = qq_number  # qq_number 已经是整数
        
        # 写入更新后的内容
        with open(config_path, 'w', encoding='utf-8') as f:
            tomlkit.dump(doc, f)
            
    except FileNotFoundError:
        print(f"错误：配置文件 {config_path} 未找到。")
        raise
    except tomlkit.exceptions.TOMLKitError as e:
        print(f"错误：解析配置文件 {config_path} 失败：{e}")
        raise
    except Exception as e:
        print(f"错误：更新配置文件 {config_path} 时发生未知错误：{e}")
        raise

def main():
    while True:
        qq_input = input('请输入QQ号：')
        if not is_valid_qq(qq_input):
            print('错误：请输入有效的QQ号（纯数字）')
            continue
        
        qq_number_int = int(qq_input)  # 转换为整数        
        try:
            update_qq_in_config('./modules/MaiBot/config/bot_config.toml', qq_number_int)
            update_qq_in_config('./modules/MaiBot/template/bot_config_template.toml', qq_number_int)
            create_onebot_config(qq_input)  # create_onebot_config 和 create_napcat_config 需要字符串类型的 qq
            create_napcat_config(qq_input)
            print(f'成功更新QQ号为：{qq_input}并创建所有必要的配置文件')
            break
        except Exception as e:
            print(f'更新配置文件时出错：{str(e)}')
            continue

if __name__ == '__main__':
    main()