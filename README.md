sudo apt-get install can-utils
pip3 install canopen
sudo vi /boot/config.txt
	dtparam=spi=on
	dtoverlay=mcp2515-can0,oscillator=12000000,interrupt=25,spimaxfrequency=2000000

sudo ip link set can0 up type can bitrate 125000

linux下python解释器的sys.path路径如何添加
　1. 使用命令行的形式添加, 虽然方便, 但是只对本次对话生效, 下次还的处理
　　    export PYTHONPATH=/home/目录/项目根目录/            # 等号后为项目的根目录路径
　2. 编辑配置文件
　　    vim /etc/profile
 在最后一行完整添加如下命令, 保存退出后重新登陆即可生效
			export PYTHONPATH=/home/目录/项目根目录/ 


ls /sys/class/tty/ttyUSB* -l

udevadm info /dev/ttyUSB*

sudo nano /etc/udev/rules.d/99-com.rules UBSYSTEM=="tty", ENV{ID_PATH}=="platform-fd500000.pcie-pci-0000:01:00.0-usb-0:1.3:1.0", SYMLINK+="USB0"	
