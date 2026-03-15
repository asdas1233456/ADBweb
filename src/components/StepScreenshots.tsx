import React, { useState, useEffect } from 'react'
import { Card, Empty, Image, Timeline, Badge, Space, Button } from 'antd'
import { CameraOutlined, FullscreenOutlined, DownloadOutlined } from '@ant-design/icons'

interface Screenshot {
  stepName: string
  filename: string
  imageData: string
  timestamp: string
}

interface StepScreenshotsProps {
  screenshots: Screenshot[]
}

const StepScreenshots: React.FC<StepScreenshotsProps> = ({ screenshots }) => {
  const [currentIndex, setCurrentIndex] = useState(0)
  const [isFullscreen, setIsFullscreen] = useState(false)

  // 自动切换到最新截图
  useEffect(() => {
    if (screenshots.length > 0) {
      setCurrentIndex(screenshots.length - 1)
    }
  }, [screenshots.length])

  if (screenshots.length === 0) {
    return (
      <Card 
        title={
          <Space>
            <CameraOutlined />
            步骤截图
          </Space>
        }
        style={{ height: '100%' }}
      >
        <Empty 
          description="暂无截图" 
          image={Empty.PRESENTED_IMAGE_SIMPLE}
        />
      </Card>
    )
  }

  const currentScreenshot = screenshots[currentIndex]

  const handleDownload = () => {
    const link = document.createElement('a')
    link.href = `data:image/jpeg;base64,${currentScreenshot.imageData}`
    link.download = currentScreenshot.filename
    link.click()
  }

  return (
    <Card
      title={
        <Space>
          <CameraOutlined />
          步骤截图
          <Badge count={screenshots.length} style={{ backgroundColor: '#52c41a' }} />
        </Space>
      }
      extra={
        <Space>
          <Button 
            size="small" 
            icon={<DownloadOutlined />}
            onClick={handleDownload}
          >
            下载
          </Button>
          <Button 
            size="small" 
            icon={<FullscreenOutlined />}
            onClick={() => setIsFullscreen(true)}
          >
            全屏
          </Button>
        </Space>
      }
      style={{ height: '100%', display: 'flex', flexDirection: 'column' }}
      bodyStyle={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}
    >
      {/* 当前截图显示 */}
      <div style={{ 
        flex: 1, 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        marginBottom: 16,
        overflow: 'hidden',
        background: '#f5f5f5',
        borderRadius: 4
      }}>
        <Image
          src={`data:image/jpeg;base64,${currentScreenshot.imageData}`}
          alt={currentScreenshot.stepName}
          style={{ 
            maxWidth: '100%', 
            maxHeight: '100%',
            objectFit: 'contain'
          }}
          preview={{
            visible: isFullscreen,
            onVisibleChange: setIsFullscreen,
            mask: null
          }}
        />
      </div>

      {/* 步骤名称 */}
      <div style={{ 
        textAlign: 'center', 
        marginBottom: 12,
        fontSize: 14,
        fontWeight: 500,
        color: '#1890ff'
      }}>
        {currentScreenshot.stepName.replace(/_/g, ' ')}
      </div>

      {/* 步骤时间线 */}
      <div style={{ 
        maxHeight: 200, 
        overflowY: 'auto',
        borderTop: '1px solid #f0f0f0',
        paddingTop: 12
      }}>
        <Timeline
          items={screenshots.map((shot, index) => ({
            color: index === currentIndex ? 'blue' : 'gray',
            children: (
              <div
                onClick={() => setCurrentIndex(index)}
                style={{
                  cursor: 'pointer',
                  padding: '4px 8px',
                  borderRadius: 4,
                  background: index === currentIndex ? '#e6f7ff' : 'transparent',
                  transition: 'all 0.3s'
                }}
              >
                <div style={{ 
                  display: 'flex', 
                  alignItems: 'center',
                  gap: 8
                }}>
                  <img
                    src={`data:image/jpeg;base64,${shot.imageData}`}
                    alt={shot.stepName}
                    style={{
                      width: 40,
                      height: 40,
                      objectFit: 'cover',
                      borderRadius: 4,
                      border: index === currentIndex ? '2px solid #1890ff' : '1px solid #d9d9d9'
                    }}
                  />
                  <div style={{ flex: 1 }}>
                    <div style={{ 
                      fontSize: 12, 
                      fontWeight: index === currentIndex ? 500 : 400,
                      color: index === currentIndex ? '#1890ff' : '#666'
                    }}>
                      {shot.stepName.replace(/_/g, ' ')}
                    </div>
                    <div style={{ fontSize: 11, color: '#999' }}>
                      {new Date(shot.timestamp).toLocaleTimeString()}
                    </div>
                  </div>
                </div>
              </div>
            )
          }))}
        />
      </div>
    </Card>
  )
}

export default StepScreenshots
