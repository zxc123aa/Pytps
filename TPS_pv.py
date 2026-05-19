# epics_server.py
from pcaspy import Driver, SimpleServer

# 定义 PV 数据库（这里只定义一个 PV 用于控制按钮/灯状态）
pvDB = {
    'TPS_cutoff_energy:pv': {
        'prec': 1,
        'unit': '',
        'type': 'float',
        'value': 0,  # 初始状态为 False（灯关闭）
    },
}

# 自定义 Driver 类
class MyDriver(Driver):
    def __init__(self):
        super().__init__()

    def write(self, reason, value):
        """当写入 PV 时更新按钮状态"""
        if reason in self.pvDB:
            self.setParam(reason, value)
            print(f"PV {reason} 更新为: {value}")
            return True
        return False

# 初始化 pcaspy 服务器
server = SimpleServer()
server.createPV('TPS_pv:', pvDB)  # 创建 PV，完整 PV 名称为 "mypv:button:pv"
driver = MyDriver()



print("EPICS PV 服务器正在运行...")

# 持续处理事件，使服务器响应请求
while True:
    server.process(0.1)