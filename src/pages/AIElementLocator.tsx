
import React, { useState } from 'react';
import {
  Card,
  Upload,
  Button,
  Input,
  Select,
  Space,
  Image,
  Table,
  message,
  Tabs,
  Tag,
  Descriptions,
  Alert,
  Row,
  Col,
  Statistic,
  InputNumber,
  Switch,
  Divider,
} from 'antd';
import {
  UploadOutlined,
  SearchOutlined,
  AimOutlined,
  CodeOutlined,
  EyeOutlined,
  ThunderboltOutlined,
  CheckCircleOutlined,
  CompassOutlined,
  BorderOutlined,
  FilterOutlined,
} from '@ant-design/icons';

const { TextArea } = Input;

const AIElementLocator: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [uploadedImage, setUploadedImage] = useState<string>('');
  const [imagePath, setImagePath] = useState<string>('');
  const [analysisResult, setAnalysisResult] = useState<any>(null);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [searchMethod, setSearchMethod] = useState<string>('auto');
  const [foundElement, setFoundElement] = useState<any>(null);
  const [coordinates, setCoordinates] = useState<any>(null);
  const [adbCommand, setAdbCommand] = useState<string>('');
  const [annotatedImage, setAnnotatedImage] = useState<string>('');
  const [capabilities, setCapabilities] = useState<any>(null);
  
  // 新增状态
  const [elementTypes, setElementTypes] = useState<any[]>([]);
  const [elementStates, setElementStates] = useState<any[]>([]);
  const [showLabels, setShowLabels] = useState<boolean>(true);
  const [showCenter, setShowCenter] = useState<boolean>(false);
  const [minConfidence, setMinConfidence] = useState<number>(0.0);
  const [relativeResult, setRelativeResult] = useState<any>(null);
  const [regionResult, setRegionResult] = useState<any>(null);
  const [stateResult, setStateResult] = useState<any>(null);

  React.useEffect(() => {
    fetchCapabilities();
    fetchElementTypes();
    fetchElementStates();
  }, []);

  const fetchCapabilities = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/ai-element-locator/capabilities');
      const data = await response.json();
      if (data.code === 200) {
        setCapabilities(data.data);
      }
    } catch (error) {
      console.error('获取能力信息失败:', error);
    }
  };

  const fetchElementTypes = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/ai-element-locator/element-types');
      const data = await response.json();
      if (data.code === 200) {
        setElementTypes(data.data);
      }
    } catch (error) {
      console.error('获取元素类型失败:', error);
    }
  };

  const fetchElementStates = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/ai-element-locator/element-states');
      const data = await response.json();
      if (data.code === 200) {
        setElementStates(data.data);
      }
    } catch (error) {
      console.error('获取元素状态失败:', error);
    }
  };

  const handleUpload = async (file: any) => {
    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:8000/api/v1/ai-element-locator/upload-screenshot', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      
      if (response.ok && data.code === 200) {
        message.success('截图上传成功');
        // 使用file_path用于API调用，url_path用于显示
        setImagePath(data.data.file_path);
        setUploadedImage(`http://localhost:8000/${data.data.url_path || data.data.file_path.replace(/\\/g, '/')}`);
        analyzeScreenshot(data.data.file_path);
      } else {
        message.error(data.message || `上传失败: ${response.status}`);
        console.error('上传失败:', data);
      }
    } catch (error: any) {
      message.error(`上传失败: ${error.message || '网络错误'}`);
      console.error('上传错误:', error);
    } finally {
      setLoading(false);
    }
    return false;
  };

  const analyzeScreenshot = async (path?: string) => {
    const targetPath = path || imagePath;
    if (!targetPath) {
      message.warning('请先上传截图');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/v1/ai-element-locator/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image_path: targetPath }),
      });

      const data = await response.json();
      if (data.code === 200) {
        message.success(`识别到 ${data.data.total} 个UI元素`);
        setAnalysisResult(data.data);
      } else {
        message.error(data.message || '分析失败');
      }
    } catch (error) {
      message.error('分析失败');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!imagePath || !searchQuery) {
      message.warning('请先上传截图并输入查询条件');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/v1/ai-element-locator/find-element', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          image_path: imagePath,
          query: searchQuery,
          method: searchMethod,
        }),
      });

      const data = await response.json();
      if (data.code === 200) {
        message.success('找到匹配元素');
        setFoundElement(data.data);
        getCoordinates();
      } else {
        message.warning('未找到匹配元素');
        setFoundElement(null);
      }
    } catch (error) {
      message.error('查找失败');
    } finally {
      setLoading(false);
    }
  };

  const getCoordinates = async () => {
    if (!imagePath || !searchQuery) return;

    try {
      const response = await fetch('http://localhost:8000/api/v1/ai-element-locator/get-coordinates', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image_path: imagePath, query: searchQuery }),
      });

      const data = await response.json();
      if (data.code === 200) {
        setCoordinates(data.data);
        generateCommand();
      }
    } catch (error) {
      console.error('获取坐标失败');
    }
  };

  const generateCommand = async () => {
    if (!imagePath || !searchQuery) return;

    try {
      const response = await fetch('http://localhost:8000/api/v1/ai-element-locator/generate-command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image_path: imagePath, action: 'click', query: searchQuery }),
      });

      const data = await response.json();
      if (data.code === 200) {
        setAdbCommand(data.data.command);
      }
    } catch (error) {
      console.error('生成命令失败');
    }
  };

  const visualizeElements = async () => {
    if (!imagePath) {
      message.warning('请先上传截图');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/v1/ai-element-locator/visualize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          image_path: imagePath,
          show_labels: showLabels,
          show_center: showCenter,
          min_confidence: minConfidence,
        }),
      });

      const data = await response.json();
      if (data.code === 200) {
        message.success('可视化成功');
        const normalizedPath = data.data.output_path.replace(/\\/g, '/');
        setAnnotatedImage(`http://localhost:8000/${normalizedPath}?t=${Date.now()}`);
      } else {
        message.error(data.message || '可视化失败');
      }
    } catch (error) {
      message.error('可视化失败');
    } finally {
      setLoading(false);
    }
  };

  const findRelativeElement = async (anchorQuery: string, direction: string) => {
    if (!imagePath || !anchorQuery) {
      message.warning('请输入锚点元素查询条件');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/v1/ai-element-locator/find-relative', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          image_path: imagePath,
          anchor_query: anchorQuery,
          direction: direction,
          distance_threshold: 200,
        }),
      });

      const data = await response.json();
      if (data.code === 200) {
        message.success('找到相对元素');
        setRelativeResult(data.data);
      } else {
        message.warning(data.message || '未找到相对元素');
        setRelativeResult(null);
      }
    } catch (error) {
      message.error('查找失败');
    } finally {
      setLoading(false);
    }
  };

  const findInRegion = async (region: number[], elementType?: string) => {
    if (!imagePath || region.length !== 4) {
      message.warning('请输入有效的区域坐标');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/v1/ai-element-locator/find-in-region', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          image_path: imagePath,
          region: region,
          element_type: elementType,
        }),
      });

      const data = await response.json();
      if (data.code === 200) {
        message.success(`在区域内找到 ${data.data.count} 个元素`);
        setRegionResult(data.data);
      } else {
        message.warning(data.message || '未找到元素');
        setRegionResult(null);
      }
    } catch (error) {
      message.error('查找失败');
    } finally {
      setLoading(false);
    }
  };

  const filterByState = async (elementType: string, state: string) => {
    if (!imagePath || !elementType || !state) {
      message.warning('请选择元素类型和状态');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/v1/ai-element-locator/filter-by-state', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          image_path: imagePath,
          element_type: elementType,
          state: state,
        }),
      });

      const data = await response.json();
      if (data.code === 200) {
        message.success(`找到 ${data.data.count} 个${state}状态的${elementType}`);
        setStateResult(data.data);
      } else {
        message.warning(data.message || '未找到元素');
        setStateResult(null);
      }
    } catch (error) {
      message.error('查找失败');
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    { title: '序号', key: 'index', width: 60, render: (_: any, __: any, index: number) => index + 1 },
    {
      title: '类型',
      dataIndex: 'type',
      key: 'type',
      width: 100,
      render: (type: string) => <Tag color={type === 'button' ? 'red' : type === 'input' ? 'blue' : 'green'}>{type}</Tag>,
    },
    { title: '文本', dataIndex: 'text', key: 'text', ellipsis: true },
    {
      title: '置信度',
      dataIndex: 'confidence',
      key: 'confidence',
      width: 100,
      render: (confidence: number) => `${(confidence * 100).toFixed(1)}%`,
    },
    {
      title: '中心坐标',
      dataIndex: 'center',
      key: 'center',
      width: 120,
      render: (center: number[]) => `(${center[0]}, ${center[1]})`,
    },
    { title: '描述', dataIndex: 'description', key: 'description', ellipsis: true },
  ];

  return (
    <div style={{ padding: '24px' }}>
      <Card
        title={<Space><AimOutlined />AI智能元素定位器</Space>}
        extra={
          capabilities && (
            <Space>
              <Tag color={capabilities.ocr_available ? 'success' : 'default'}>
                OCR: {capabilities.ocr_available ? '已启用' : '未启用'}
              </Tag>
              <Tag color="success">视觉识别: 已启用</Tag>
            </Space>
          )
        }
      >
        <Alert
          message="功能说明"
          description="使用计算机视觉和OCR技术自动识别屏幕元素，无需手动指定坐标。支持文本匹配和自然语言描述查找元素。"
          type="info"
          showIcon
          style={{ marginBottom: 16 }}
        />

        <Tabs defaultActiveKey="1">
          <Tabs.TabPane tab="上传与分析" key="1">
            <Space direction="vertical" style={{ width: '100%' }} size="large">
              <Card title="1. 上传截图" size="small">
                <Upload beforeUpload={handleUpload} showUploadList={false} accept="image/*">
                  <Button icon={<UploadOutlined />} loading={loading}>选择截图文件</Button>
                </Upload>
              </Card>

              {uploadedImage && (
                <Card title="2. 截图预览" size="small">
                  <Row gutter={16}>
                    <Col span={annotatedImage ? 12 : 24}>
                      <Card title="原始截图" size="small">
                        <Image src={uploadedImage} alt="截图" style={{ maxWidth: '100%' }} />
                      </Card>
                    </Col>
                    {annotatedImage && (
                      <Col span={12}>
                        <Card title="标注结果" size="small">
                          <Image src={annotatedImage} alt="标注" style={{ maxWidth: '100%' }} />
                        </Card>
                      </Col>
                    )}
                  </Row>
                </Card>
              )}

              {analysisResult && (
                <Card
                  title="3. 分析结果"
                  size="small"
                  extra={
                    <Space>
                      <Space>
                        <span>显示标签:</span>
                        <Switch checked={showLabels} onChange={setShowLabels} size="small" />
                      </Space>
                      <Space>
                        <span>显示中心点:</span>
                        <Switch checked={showCenter} onChange={setShowCenter} size="small" />
                      </Space>
                      <Space>
                        <span>最小置信度:</span>
                        <InputNumber 
                          min={0} 
                          max={1} 
                          step={0.1} 
                          value={minConfidence} 
                          onChange={(val) => setMinConfidence(val || 0)} 
                          size="small"
                          style={{ width: 80 }}
                        />
                      </Space>
                      <Button icon={<EyeOutlined />} onClick={visualizeElements} loading={loading}>可视化元素</Button>
                    </Space>
                  }
                >
                  <Row gutter={16} style={{ marginBottom: 16 }}>
                    <Col span={8}>
                      <Statistic title="识别元素总数" value={analysisResult.total} prefix={<CheckCircleOutlined />} />
                    </Col>
                    <Col span={8}>
                      <Statistic title="按钮数量" value={analysisResult.elements.filter((e: any) => e.type === 'button').length} />
                    </Col>
                    <Col span={8}>
                      <Statistic title="输入框数量" value={analysisResult.elements.filter((e: any) => e.type === 'input').length} />
                    </Col>
                  </Row>
                  <Table columns={columns} dataSource={analysisResult.elements} rowKey={(_, index) => `${index}`} pagination={{ pageSize: 10 }} size="small" />
                </Card>
              )}
            </Space>
          </Tabs.TabPane>

          <Tabs.TabPane tab="元素查找" key="2">
            <Space direction="vertical" style={{ width: '100%' }} size="large">
              <Card title="查找元素" size="small">
                <Space direction="vertical" style={{ width: '100%' }}>
                  <Input
                    placeholder="输入查询条件（如：登录、蓝色的提交按钮）"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onPressEnter={handleSearch}
                    prefix={<SearchOutlined />}
                  />
                  <Space>
                    <Select value={searchMethod} onChange={setSearchMethod} style={{ width: 150 }}>
                      <Select.Option value="auto">自动模式</Select.Option>
                      <Select.Option value="text">文本匹配</Select.Option>
                      <Select.Option value="description">描述匹配</Select.Option>
                    </Select>
                    <Button type="primary" icon={<SearchOutlined />} onClick={handleSearch} loading={loading}>查找元素</Button>
                  </Space>
                </Space>
              </Card>

              {foundElement && (
                <Card title="查找结果" size="small">
                  <Descriptions bordered column={2} size="small">
                    <Descriptions.Item label="元素类型"><Tag color="blue">{foundElement.type}</Tag></Descriptions.Item>
                    <Descriptions.Item label="置信度">{(foundElement.confidence * 100).toFixed(1)}%</Descriptions.Item>
                    <Descriptions.Item label="文本内容">{foundElement.text || '-'}</Descriptions.Item>
                    <Descriptions.Item label="中心坐标">({foundElement.center[0]}, {foundElement.center[1]})</Descriptions.Item>
                    <Descriptions.Item label="边界框" span={2}>[{foundElement.bbox.join(', ')}]</Descriptions.Item>
                    <Descriptions.Item label="描述" span={2}>{foundElement.description}</Descriptions.Item>
                  </Descriptions>
                </Card>
              )}

              {coordinates && (
                <Card title="点击坐标" size="small">
                  <Alert message={`X: ${coordinates.x}, Y: ${coordinates.y}`} type="success" showIcon />
                </Card>
              )}

              {adbCommand && (
                <Card title="ADB命令" size="small">
                  <Space direction="vertical" style={{ width: '100%' }}>
                    <TextArea value={adbCommand} readOnly autoSize={{ minRows: 2, maxRows: 4 }} />
                    <Button
                      icon={<CodeOutlined />}
                      onClick={() => {
                        navigator.clipboard.writeText(adbCommand);
                        message.success('命令已复制到剪贴板');
                      }}
                    >
                      复制命令
                    </Button>
                  </Space>
                </Card>
              )}
            </Space>
          </Tabs.TabPane>

          <Tabs.TabPane tab={<Space><CompassOutlined />相对位置查找</Space>} key="3">
            <Space direction="vertical" style={{ width: '100%' }} size="large">
              <Card title="相对位置查找" size="small">
                <Alert
                  message="根据锚点元素查找其相对位置的元素"
                  description="例如：查找'登录'按钮右边的元素"
                  type="info"
                  showIcon
                  style={{ marginBottom: 16 }}
                />
                <Space direction="vertical" style={{ width: '100%' }}>
                  <Input
                    placeholder="输入锚点元素（如：登录）"
                    prefix={<AimOutlined />}
                    id="anchor-query"
                  />
                  <Select placeholder="选择方向" style={{ width: '100%' }} id="direction-select">
                    <Select.Option value="right">右边 (right)</Select.Option>
                    <Select.Option value="left">左边 (left)</Select.Option>
                    <Select.Option value="top">上方 (top)</Select.Option>
                    <Select.Option value="bottom">下方 (bottom)</Select.Option>
                  </Select>
                  <Button 
                    type="primary" 
                    icon={<SearchOutlined />} 
                    loading={loading}
                    onClick={() => {
                      const anchor = (document.getElementById('anchor-query') as HTMLInputElement)?.value;
                      const direction = (document.getElementById('direction-select') as any)?.value;
                      if (anchor && direction) {
                        findRelativeElement(anchor, direction);
                      } else {
                        message.warning('请输入锚点元素并选择方向');
                      }
                    }}
                  >
                    查找相对元素
                  </Button>
                </Space>
              </Card>

              {relativeResult && (
                <Card title="查找结果" size="small">
                  <Row gutter={16}>
                    <Col span={12}>
                      <Card title="锚点元素" size="small" type="inner">
                        <Descriptions bordered column={1} size="small">
                          <Descriptions.Item label="类型"><Tag color="blue">{relativeResult.anchor.type}</Tag></Descriptions.Item>
                          <Descriptions.Item label="文本">{relativeResult.anchor.text || '-'}</Descriptions.Item>
                          <Descriptions.Item label="坐标">({relativeResult.anchor.center[0]}, {relativeResult.anchor.center[1]})</Descriptions.Item>
                        </Descriptions>
                      </Card>
                    </Col>
                    <Col span={12}>
                      <Card title={`${relativeResult.direction}方向的元素`} size="small" type="inner">
                        <Descriptions bordered column={1} size="small">
                          <Descriptions.Item label="类型"><Tag color="green">{relativeResult.relative.type}</Tag></Descriptions.Item>
                          <Descriptions.Item label="文本">{relativeResult.relative.text || '-'}</Descriptions.Item>
                          <Descriptions.Item label="坐标">({relativeResult.relative.center[0]}, {relativeResult.relative.center[1]})</Descriptions.Item>
                        </Descriptions>
                      </Card>
                    </Col>
                  </Row>
                </Card>
              )}
            </Space>
          </Tabs.TabPane>

          <Tabs.TabPane tab={<Space><BorderOutlined />区域查找</Space>} key="4">
            <Space direction="vertical" style={{ width: '100%' }} size="large">
              <Card title="区域查找" size="small">
                <Alert
                  message="在指定矩形区域内查找元素"
                  description="输入区域坐标 [x1, y1, x2, y2]，例如：[0, 0, 800, 400] 表示顶部区域"
                  type="info"
                  showIcon
                  style={{ marginBottom: 16 }}
                />
                <Space direction="vertical" style={{ width: '100%' }}>
                  <Row gutter={8}>
                    <Col span={6}>
                      <InputNumber placeholder="X1" style={{ width: '100%' }} id="region-x1" />
                    </Col>
                    <Col span={6}>
                      <InputNumber placeholder="Y1" style={{ width: '100%' }} id="region-y1" />
                    </Col>
                    <Col span={6}>
                      <InputNumber placeholder="X2" style={{ width: '100%' }} id="region-x2" />
                    </Col>
                    <Col span={6}>
                      <InputNumber placeholder="Y2" style={{ width: '100%' }} id="region-y2" />
                    </Col>
                  </Row>
                  <Select placeholder="元素类型（可选）" style={{ width: '100%' }} allowClear id="region-type">
                    {elementTypes.map(type => (
                      <Select.Option key={type.value} value={type.value}>{type.description}</Select.Option>
                    ))}
                  </Select>
                  <Button 
                    type="primary" 
                    icon={<SearchOutlined />} 
                    loading={loading}
                    onClick={() => {
                      const x1 = (document.getElementById('region-x1') as any)?.value;
                      const y1 = (document.getElementById('region-y1') as any)?.value;
                      const x2 = (document.getElementById('region-x2') as any)?.value;
                      const y2 = (document.getElementById('region-y2') as any)?.value;
                      const type = (document.getElementById('region-type') as any)?.value;
                      if (x1 && y1 && x2 && y2) {
                        findInRegion([parseInt(x1), parseInt(y1), parseInt(x2), parseInt(y2)], type);
                      } else {
                        message.warning('请输入完整的区域坐标');
                      }
                    }}
                  >
                    在区域内查找
                  </Button>
                </Space>
              </Card>

              {regionResult && (
                <Card title={`找到 ${regionResult.count} 个元素`} size="small">
                  <Table 
                    columns={columns} 
                    dataSource={regionResult.elements} 
                    rowKey={(_, index) => `region-${index}`} 
                    pagination={{ pageSize: 10 }} 
                    size="small" 
                  />
                </Card>
              )}
            </Space>
          </Tabs.TabPane>

          <Tabs.TabPane tab={<Space><FilterOutlined />状态筛选</Space>} key="5">
            <Space direction="vertical" style={{ width: '100%' }} size="large">
              <Card title="按状态筛选元素" size="small">
                <Alert
                  message="筛选特定状态的元素"
                  description="例如：查找所有选中的复选框、开启的开关等"
                  type="info"
                  showIcon
                  style={{ marginBottom: 16 }}
                />
                <Space direction="vertical" style={{ width: '100%' }}>
                  <Select placeholder="选择元素类型" style={{ width: '100%' }} id="state-type">
                    <Select.Option value="checkbox">复选框 (checkbox)</Select.Option>
                    <Select.Option value="switch">开关 (switch)</Select.Option>
                    <Select.Option value="radio">单选按钮 (radio)</Select.Option>
                  </Select>
                  <Select placeholder="选择状态" style={{ width: '100%' }} id="state-value">
                    {elementStates.map(state => (
                      <Select.Option key={state.value} value={state.value}>{state.description}</Select.Option>
                    ))}
                  </Select>
                  <Button 
                    type="primary" 
                    icon={<FilterOutlined />} 
                    loading={loading}
                    onClick={() => {
                      const type = (document.getElementById('state-type') as any)?.value;
                      const state = (document.getElementById('state-value') as any)?.value;
                      if (type && state) {
                        filterByState(type, state);
                      } else {
                        message.warning('请选择元素类型和状态');
                      }
                    }}
                  >
                    筛选元素
                  </Button>
                </Space>
              </Card>

              {stateResult && (
                <Card title={`找到 ${stateResult.count} 个${stateResult.state}状态的${stateResult.element_type}`} size="small">
                  <Table 
                    columns={[
                      ...columns,
                      {
                        title: '状态',
                        dataIndex: 'state',
                        key: 'state',
                        width: 100,
                        render: (state: string) => (
                          <Tag color={state === 'checked' || state === 'selected' ? 'success' : 'default'}>
                            {state}
                          </Tag>
                        ),
                      },
                    ]} 
                    dataSource={stateResult.elements} 
                    rowKey={(_, index) => `state-${index}`} 
                    pagination={{ pageSize: 10 }} 
                    size="small" 
                  />
                </Card>
              )}
            </Space>
          </Tabs.TabPane>
        </Tabs>
      </Card>
    </div>
  );
};

export default AIElementLocator;
