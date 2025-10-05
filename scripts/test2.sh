#!/bin/bash
echo "=== Тест 2: Скрипт-режим ==="
cat > test_commands.txt <<EOF
ls
cd /home
xyz
EOF

python3 main.py --vfs /tmp/vfs --log ./logs/script.log --script test_commands.txt
