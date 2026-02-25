import type { Device, Script, Report } from '../types'

export const mockDevices: Device[] = [
  {
    id: '1',
    serialNumber: 'ABC123456789',
    model: 'Xiaomi 12 Pro',
    androidVersion: '13',
    resolution: '1440x3200',
    battery: 85,
    status: 'online',
  },
  {
    id: '2',
    serialNumber: 'DEF987654321',
    model: 'Samsung Galaxy S23',
    androidVersion: '14',
    resolution: '1080x2400',
    battery: 62,
    status: 'online',
  },
  {
    id: '3',
    serialNumber: 'GHI456789123',
    model: 'OPPO Find X6',
    androidVersion: '13',
    resolution: '1440x3216',
    battery: 45,
    status: 'busy',
  },
  {
    id: '4',
    serialNumber: 'JKL789123456',
    model: 'Vivo X90 Pro',
    androidVersion: '13',
    resolution: '1260x2800',
    battery: 0,
    status: 'offline',
  },
]

export const mockScripts: Script[] = [
  {
    id: '1',
    name: '登录测试',
    type: 'visual',
    category: 'login',
    description: '自动化登录测试脚本',
    steps: [
      {
        id: 's1',
        type: 'click',
        name: '点击登录按钮',
        config: { x: 100, y: 200 },
      },
      {
        id: 's2',
        type: 'input',
        name: '输入用户名',
        config: { text: 'testuser', x: 150, y: 300 },
      },
      {
        id: 's3',
        type: 'input',
        name: '输入密码',
        config: { text: '******', x: 150, y: 400 },
      },
      {
        id: 's4',
        type: 'click',
        name: '点击提交',
        config: { x: 200, y: 500 },
      },
    ],
    createdAt: '2024-01-15 10:30:00',
    updatedAt: '2024-01-15 14:20:00',
  },
  {
    id: '2',
    name: '商品浏览',
    type: 'visual',
    category: 'test',
    description: '商品列表浏览测试',
    steps: [
      {
        id: 's5',
        type: 'click',
        name: '打开商品列表',
        config: { x: 100, y: 150 },
      },
      {
        id: 's6',
        type: 'swipe',
        name: '向上滑动',
        config: { x1: 200, y1: 800, x2: 200, y2: 200, duration: 500 },
      },
      {
        id: 's7',
        type: 'wait',
        name: '等待加载',
        config: { duration: 2000 },
      },
    ],
    createdAt: '2024-01-14 09:15:00',
    updatedAt: '2024-01-14 16:45:00',
  },
  {
    id: '3',
    name: 'ADB设备检测',
    type: 'python',
    category: 'automation',
    description: 'Python脚本：检测连接的ADB设备',
    filePath: 'scripts/check_devices.py',
    fileContent: `import subprocess

def check_adb_devices():
    result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
    print(result.stdout)

if __name__ == '__main__':
    check_adb_devices()`,
    steps: [],
    createdAt: '2024-01-13 15:20:00',
    updatedAt: '2024-01-13 15:20:00',
  },
  {
    id: '4',
    name: '清理临时文件',
    type: 'batch',
    category: 'automation',
    description: '批处理脚本：清理设备临时文件',
    filePath: 'scripts/clean_temp.bat',
    fileContent: `@echo off
echo 正在清理临时文件...
adb shell rm -rf /sdcard/temp/*
echo 清理完成！
pause`,
    steps: [],
    createdAt: '2024-01-12 11:30:00',
    updatedAt: '2024-01-12 11:30:00',
  },
]

export const mockReports: Report[] = [
  {
    id: '1',
    taskName: '登录测试',
    deviceId: '1',
    scriptId: '1',
    status: 'success',
    startTime: '2024-01-15 14:30:00',
    duration: 5.2,
  },
  {
    id: '2',
    taskName: '商品浏览',
    deviceId: '2',
    scriptId: '2',
    status: 'failed',
    startTime: '2024-01-15 14:35:00',
    duration: 12.8,
  },
  {
    id: '3',
    taskName: '支付流程',
    deviceId: '1',
    scriptId: '1',
    status: 'success',
    startTime: '2024-01-15 14:40:00',
    duration: 25.3,
  },
]
