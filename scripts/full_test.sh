#!/bin/bash
echo "=== Полный тест: все команды и ошибки ==="
python3 main.py --vfs ./vfs_deep --log ./logs/full_test.log --script <<EOF
ls
cd /nonexistent
cd /home/user/docs
ls
cd ../../..
ls
cd /etc/config
ls
xyz
exit
EOF

