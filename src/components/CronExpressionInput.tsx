/**
 * Cron 表达式输入组件
 */
import { useState, useEffect } from 'react'
import { Input, Select, Space, Tag, Tooltip } from 'antd'
import { ClockCircleOutlined, QuestionCircleOutlined } from '@ant-design/icons'

interface CronExpressionInputProps {
  value?: string
  onChange?: (value: string) => void
  disabled?: boolean
}

// 常用 Cron 表达式模板
const CRON_TEMPLATES = [
  { label: '每分钟', value: '* * * * *', desc: '每分钟执行一次' },
  { label: '每5分钟', value: '*/5 * * * *', desc: '每5分钟执行一次' },
  { label: '每15分钟', value: '*/15 * * * *', desc: '每15分钟执行一次' },
  { label: '每30分钟', value: '*/30 * * * *', desc: '每30分钟执行一次' },
  { label: '每小时', value: '0 * * * *', desc: '每小时整点执行' },
  { label: '每2小时', value: '0 */2 * * *', desc: '每2小时执行一次' },
  { label: '每天上午9点', value: '0 9 * * *', desc: '每天上午9:00执行' },
  { label: '每天中午12点', value: '0 12 * * *', desc: '每天中午12:00执行' },
  { label: '每天下午6点', value: '0 18 * * *', desc: '每天下午18:00执行' },
  { label: '每天凌晨0点', value: '0 0 * * *', desc: '每天凌晨0:00执行' },
  { label: '工作日上午9点', value: '0 9 * * 1-5', desc: '周一到周五上午9:00' },
  { label: '工作日下午6点', value: '0 18 * * 1-5', desc: '周一到周五下午18:00' },
  { label: '每周一上午9点', value: '0 9 * * 1', desc: '每周一上午9:00' },
  { label: '每月1号凌晨', value: '0 0 1 * *', desc: '每月1号凌晨0:00' },
]

const CronExpressionInput = ({ value, onChange, disabled }: CronExpressionInputProps) => {
  const [cronValue, setCronValue] = useState(value || '')
  const [useTemplate, setUseTemplate] = useState(true)

  useEffect(() => {
    setCronValue(value || '')
  }, [value])

  const handleTemplateChange = (templateValue: string) => {
    setCronValue(templateValue)
    onChange?.(templateValue)
  }

  const handleCustomChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value
    setCronValue(newValue)
    onChange?.(newValue)
  }

  // 解析 Cron 表达式
  const parseCron = (cron: string) => {
    if (!cron) return null
    
    const parts = cron.trim().split(/\s+/)
    if (parts.length !== 5) return null

    const [minute, hour, day, month, weekday] = parts
    
    try {
      let description = ''
      
      // 分钟
      if (minute === '*') {
        description += '每分钟'
      } else if (minute.startsWith('*/')) {
        description += `每${minute.slice(2)}分钟`
      } else {
        description += `第${minute}分钟`
      }
      
      // 小时
      if (hour === '*') {
        description += ', 每小时'
      } else if (hour.startsWith('*/')) {
        description += `, 每${hour.slice(2)}小时`
      } else {
        description += `, ${hour}点`
      }
      
      // 日期
      if (day !== '*') {
        description += `, ${day}号`
      }
      
      // 月份
      if (month !== '*') {
        description += `, ${month}月`
      }
      
      // 星期
      if (weekday !== '*') {
        const weekMap: Record<string, string> = {
          '0': '周日', '1': '周一', '2': '周二', '3': '周三',
          '4': '周四', '5': '周五', '6': '周六'
        }
        if (weekday.includes('-')) {
          const [start, end] = weekday.split('-')
          description += `, ${weekMap[start]}到${weekMap[end]}`
        } else {
          description += `, ${weekMap[weekday]}`
        }
      }
      
      return description
    } catch {
      return null
    }
  }

  const cronDescription = parseCron(cronValue)
  const matchedTemplate = CRON_TEMPLATES.find(t => t.value === cronValue)

  return (
    <Space direction="vertical" style={{ width: '100%' }}>
      <Space>
        <Select
          value={useTemplate ? 'template' : 'custom'}
          onChange={(v) => setUseTemplate(v === 'template')}
          disabled={disabled}
          style={{ width: 120 }}
          options={[
            { label: '使用模板', value: 'template' },
            { label: '自定义', value: 'custom' }
          ]}
        />
        
        <Tooltip title="Cron 表达式格式: 分钟 小时 日期 月份 星期">
          <QuestionCircleOutlined style={{ color: '#8c8c8c' }} />
        </Tooltip>
      </Space>

      {useTemplate ? (
        <Select
          style={{ width: '100%' }}
          placeholder="选择执行时间模板"
          value={cronValue}
          onChange={handleTemplateChange}
          disabled={disabled}
          showSearch
          filterOption={(input, option) =>
            (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
          }
          options={CRON_TEMPLATES.map(t => ({
            label: t.label,
            value: t.value,
            desc: t.desc
          }))}
          optionRender={(option) => (
            <div>
              <div>{option.label}</div>
              <div style={{ fontSize: 12, color: '#8c8c8c' }}>
                {option.data.desc} ({option.value})
              </div>
            </div>
          )}
        />
      ) : (
        <Input
          placeholder="输入 Cron 表达式，如: 0 9 * * *"
          value={cronValue}
          onChange={handleCustomChange}
          disabled={disabled}
          prefix={<ClockCircleOutlined />}
        />
      )}

      {cronValue && (
        <div style={{ 
          padding: 8, 
          background: '#f5f5f5', 
          borderRadius: 4,
          fontSize: 12
        }}>
          <Space direction="vertical" size={4} style={{ width: '100%' }}>
            <div>
              <span style={{ color: '#8c8c8c' }}>表达式：</span>
              <Tag color="blue">{cronValue}</Tag>
            </div>
            {matchedTemplate && (
              <div>
                <span style={{ color: '#8c8c8c' }}>说明：</span>
                {matchedTemplate.desc}
              </div>
            )}
            {cronDescription && !matchedTemplate && (
              <div>
                <span style={{ color: '#8c8c8c' }}>解析：</span>
                {cronDescription}
              </div>
            )}
          </Space>
        </div>
      )}

      <div style={{ fontSize: 12, color: '#8c8c8c' }}>
        💡 Cron 格式说明：分钟(0-59) 小时(0-23) 日期(1-31) 月份(1-12) 星期(0-6)
      </div>
    </Space>
  )
}

export default CronExpressionInput
