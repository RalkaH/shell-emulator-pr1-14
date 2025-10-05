#!/bin/bash
echo "=== Тест: глубокая VFS ==="
mkdir -p logs
python3 main.py --vfs ./vfs_deep --log ./logs/vfs_deep.log --script ./scripts/commands_deep.txt
