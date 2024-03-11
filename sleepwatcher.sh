#!/bin/zsh

if brew ls --versions sleepwatcher <= /dev/null; then
    brew install sleepwatcher
    brew services start sleepwatcher
else
    brew services restart sleepwatcher
fi
cd ~
echo '#!/bin/zsh' > ~/.wakeup
echo '~/Desktop/side_project/face_id/.venv/bin/python ~/Desktop/side_project/face_id/main.py detection' > ~/.wakeup
sudo chmod +x .wakeup