#!/bin/bash
echo "=== Тест: минимальная VFS ==="
mkdir -p logs
python3 main.py --vfs ./vfs_minimal --log ./logs/vfs_min.log --script ./scripts/commands_minimal.txt
