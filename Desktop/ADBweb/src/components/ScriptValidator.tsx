/**
 * 脚本验证组件
 * 显示脚本验证结果
 */
import { Alert, Card, Progress, Space, Tag, List, Divider, Button } from 'antd'
import {
  CheckCircleOutlined,
  WarningOutlined,
  CloseCircleOutlined,
  ReloadOutlined,
} from '@ant-design/icons'

interface ValidationItem {
  name: string
  level: 'success' | 'warning' | 'error'
  message: string
  details: string
}

interface ValidationResult {
  passed: boolean
  score: number
  items: ValidationItem[]
  suggestions: string[]
}

interface ScriptValidatorProps {
  result: ValidationResult | null
  loading?: boolean
  onRevalidate?: () => void
}

const ScriptValidator = ({ result, loading = false, onRevalidate }: ScriptValidatorProps) => {
  if (!result && !loading) {
    return null
  }

  if (loading) {
    return (
      <Card
        title="📝 脚本验证中..."
        size="small"
        style={{
          marginTop: 16,
          background: '#1a1a2e',
          border: '1px solid #2a2a4e',
        }}
      >
        <Space direction="vertical" style={{ width: '100%' }}>
          <Progress percent={50} status="active" showInfo={false} />
          <div style={{ textAlign: 'center', color: '#888' }}>
            正在检查脚本语法、安全性和代码质量...
          </div>
        </Space>
      </Card>
    )
  }

  if (!result) {
    return null
  }

  const getScoreColor = (score: number) => {
    if (score >= 90) return '#52c41a'
    if (score >= 70) return '#faad14'
    return '#ff4d4f'
  }

  const getScoreStatus = (score: number) => {
    if (score >= 90) return '优秀'
    if (score >= 70) return '良好'
    if (score >= 60) return '及格'
    return '需改进'
  }

  const getLevelIcon = (level: string) => {
    switch (level) {
      case 'success':
        return <CheckCircleOutlined style={{ color: '#52c41a' }} />
      case 'warning':
        return <WarningOutlined style={{ color: '#faad14' }} />
      case 'error':
        return <CloseCircleOutlined style={{ color: '#ff4d4f' }} />
      default:
        return null
    }
  }

  const getLevelColor = (level: string) => {
    switch (level) {
      case 'success':
        return 'success'
      case 'warning':
        return 'warning'
      case 'error':
        return 'error'
      default:
        return 'default'
    }
  }

  return (
    <Card
      title={
        <Space>
          <span style={{ color: '#fff' }}>📝 验证结果</span>
          {onRevalidate && (
            <Button
              type="text"
              size="small"
              icon={<ReloadOutlined />}
              onClick={onRevalidate}
              style={{ color: '#fff' }}
            >
              重新验证
            </Button>
          )}
        </Space>
      }
      size="small"
      style={{
        marginTop: 16,
        background: '#1a1a2e',
        border: `1px solid ${result.passed ? '#52c41a' : '#ff4d4f'}`,
        color: '#fff',
      }}
      headStyle={{ color: '#fff', borderBottom: '1px solid #2a2a4e' }}
      bodyStyle={{ color: '#fff' }}
    >
      {/* 总体状态 */}
      <Alert
        message={
          <Space>
            <span style={{ fontWeight: 600 }}>
              {result.passed ? '✅ 验证通过' : '❌ 验证失败'}
            </span>
            <Tag color={getScoreColor(result.score)}>
              {result.score}分 - {getScoreStatus(result.score)}
            </Tag>
          </Space>
        }
        description={
          result.passed
            ? '脚本通过所有检查，可以安全保存'
            : '脚本存在错误，请修复后重新上传'
        }
        type={result.passed ? 'success' : 'error'}
        showIcon
        style={{ marginBottom: 16 }}
      />

      {/* 质量评分 */}
      <div style={{ marginBottom: 16 }}>
        <div style={{ marginBottom: 8 }}>
          <Space>
            <span style={{ color: '#fff' }}>代码质量评分:</span>
            <span style={{ fontWeight: 600, color: getScoreColor(result.score) }}>
              {result.score}/100
            </span>
          </Space>
        </div>
        <Progress
          percent={result.score}
          strokeColor={getScoreColor(result.score)}
          status={result.score >= 60 ? 'success' : 'exception'}
        />
      </div>

      <Divider style={{ margin: '12px 0', borderColor: '#2a2a4e' }} />

      {/* 检查项列表 */}
      <List
        size="small"
        dataSource={result.items}
        renderItem={(item) => (
          <List.Item style={{ padding: '8px 0', border: 'none' }}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <Space>
                {getLevelIcon(item.level)}
                <span style={{ fontWeight: 500, color: '#fff' }}>{item.name}:</span>
                <Tag color={getLevelColor(item.level)}>{item.message}</Tag>
              </Space>
              {item.details && (
                <div
                  style={{
                    fontSize: '12px',
                    color: '#aaa',
                    paddingLeft: 24,
                  }}
                >
                  {item.details}
                </div>
              )}
            </Space>
          </List.Item>
        )}
      />

      {/* 建议 */}
      {result.suggestions && result.suggestions.length > 0 && (
        <>
          <Divider style={{ margin: '12px 0', borderColor: '#2a2a4e' }} />
          <div>
            <div style={{ marginBottom: 8, fontWeight: 500, color: '#fff' }}>💡 优化建议:</div>
            <List
              size="small"
              dataSource={result.suggestions}
              renderItem={(suggestion, index) => (
                <List.Item style={{ padding: '4px 0', border: 'none' }}>
                  <div style={{ fontSize: '12px', color: '#aaa' }}>
                    {index + 1}. {suggestion}
                  </div>
                </List.Item>
              )}
            />
          </div>
        </>
      )}
    </Card>
  )
}

export default ScriptValidator
