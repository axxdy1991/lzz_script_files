import json
import os
import re
from pathlib import Path

# 1. 工程根目录 = 脚本所在目录
workspace_root = os.path.dirname(os.path.abspath(__file__))

# 2. 自动查找 compile_commands.json（优先使用 Projects 下 Debug/Release 目录中最新的）
def find_compile_commands():
    wr = Path(workspace_root)
    candidates = (
        list(wr.glob("Projects/**/STM32CubeIDE/Debug/compile_commands.json"))
        + list(wr.glob("Projects/**/STM32CubeIDE/Release/compile_commands.json"))
    )
    if candidates:
        # 按修改时间排序，使用最新的（最近编译的项目）
        candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        return str(candidates[0])
    # 若未找到，尝试根目录下的（可能是之前脚本的输出）
    root_json = os.path.join(workspace_root, "compile_commands.json")
    if os.path.exists(root_json):
        return root_json
    return None

json_path = find_compile_commands()
if not json_path:
    print("[ERROR] 未找到 compile_commands.json，请先在 STM32CubeIDE 中编译任意工程。")
    exit(1)

# 读取原始 JSON
with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 3. 相对路径的基准目录 = compile_commands.json 所在目录（Debug 或 Release）
#    即 directory 字段下的 Debug/Release 文件夹，而非 directory 本身
debug_dir = os.path.dirname(os.path.abspath(json_path))
debug_dir = os.path.normpath(debug_dir)

# 替换函数：将 -I 后面的相对路径计算为绝对路径
def resolve_include(match):
    prefix = match.group(1)   # 匹配到 "-I" 或 "-I "
    rel_path = match.group(2) # 匹配到 "../../..."
    
    # 以 directory 为基准，计算出真实的绝对路径
    abs_path = os.path.normpath(os.path.join(debug_dir, rel_path))
    
    # 统一替换为正斜杠，符合 gcc/clang 的格式规范
    abs_path = abs_path.replace('\\', '/')
    return f"{prefix}{abs_path}"

# 遍历修改
for entry in data:
    command = entry.get('command', '')
    
    # 使用正则匹配 command 中的所有 "-I../../xxx" 并全部替换为绝对路径
    command = re.sub(r'(-I\s*)(\.\.[\w\./\\]+)', resolve_include, command)
    entry['command'] = command
    
    # 强制将目录设为根目录，这样 clangd 就不必再做额外的路径转换
    entry['directory'] = workspace_root.replace('\\', '/')

# 保存处理后的文件到根目录
out_path = os.path.join(workspace_root, "compile_commands.json")
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4)

print("[OK] 头文件依赖修正成功！")
# 删除当前根目录下的 .cache 文件夹（如果存在）
cache_dir = os.path.join(workspace_root, ".cache")
if os.path.isdir(cache_dir):
    import shutil
    try:
        shutil.rmtree(cache_dir)
        print(f"[OK] 已删除 {cache_dir}")
    except Exception as e:
        print(f"[WARN] 删除 {cache_dir} 失败: {e}")

print(f"   源文件: {json_path}")
print(f"   输出到: {out_path}")