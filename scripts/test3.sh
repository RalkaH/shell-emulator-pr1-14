#!/bin/bash
echo "=== Тест 3: Успешный скрипт ==="
mkdir -p ./logs
cat > good_script.txt <<EOF
ls
cd /tmp
ls -l
exit
EOF

python3 main.py --vfs ./vfs_root --log ./logs/good.log --script good_script.txt

