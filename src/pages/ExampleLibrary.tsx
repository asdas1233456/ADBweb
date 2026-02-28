/**
 * 示例库页面
 */
import React, { useState, useEffect } from 'react';
import {
  Card,
  Tabs,
  Input,
  Select,
  Tag,
  Button,
  Modal,
  message,
  Row,
  Col,
  Pagination,
  Space,
  Typography,
  Tooltip,
  Statistic,
} from 'antd';
import {
  CodeOutlined,
  DownloadOutlined,
  EyeOutlined,
  StarOutlined,
  SearchOutlined,
  LikeOutlined,
  CopyOutlined,
  BookOutlined,
} from '@ant-design/icons';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

const { Search } = Input;
const { Option } = Select;
const { Title, Text, Paragraph } = Typography;
const { TabPane } = Tabs;

// 类型定义
interface Example {
  id: number;
  title: string;
  description: string;
  category: string;
  difficulty: string;
  script_type: string;
  code: string;
  tags: string;
  use_case: string;
  prerequisites: string;
  expected_result: string;
  author: string;
  rating: number;
  download_count: number;
  view_count: number;
  is_featured: boolean;
  created_at: string;
  updated_at: string;
}

interface BestPractice {
  id: number;
  title: string;
  category: string;
  content: string;
  difficulty: string;
  tags: string;
  author: string;
  view_count: number;
  like_count: number;
  created_at: string;
}

interface Snippet {
  id: number;
  title: string;
  description: string;
  language: string;
  code: string;
  category: string;
  tags: string;
  usage_count: number;
  shortcut: string;
  author: string;
  created_at: string;
}

const ExampleLibrary: React.FC = () => {
  const [activeTab, setActiveTab] = useState('examples');
  
  // 示例脚本状态
  const [examples, setExamples] = useState<Example[]>([]);
  const [examplesTotal, setExamplesTotal] = useState(0);
  const [examplesPage, setExamplesPage] = useState(1);
  const [examplesPageSize] = useState(9);
  const [examplesLoading, setExamplesLoading] = useState(false);
  const [exampleFilters, setExampleFilters] = useState({
    category: '',
    difficulty: '',
    keyword: '',
  });
  
  // 最佳实践状态
  const [practices, setPractices] = useState<BestPractice[]>([]);
  const [practicesTotal, setPracticesTotal] = useState(0);
  const [practicesPage, setPracticesPage] = useState(1);
  const [practicesPageSize] = useState(9);
  const [practicesLoading, setPracticesLoading] = useState(false);
  
  // 代码片段状态
  const [snippets, setSnippets] = useState<Snippet[]>([]);
  const [snippetsTotal, setSnippetsTotal] = useState(0);
  const [snippetsPage, setSnippetsPage] = useState(1);
  const [snippetsPageSize] = useState(12);
  const [snippetsLoading, setSnippetsLoading] = useState(false);
  
  // 详情模态框
  const [detailModalVisible, setDetailModalVisible] = useState(false);
  const [selectedItem, setSelectedItem] = useState<any>(null);

  // 加载示例脚本
  const loadExamples = async () => {
    setExamplesLoading(true);
    try {
      const params = new URLSearchParams({
        page: examplesPage.toString(),
        page_size: examplesPageSize.toString(),
        ...(exampleFilters.category && { category: exampleFilters.category }),
        ...(exampleFilters.difficulty && { difficulty: exampleFilters.difficulty }),
        ...(exampleFilters.keyword && { keyword: exampleFilters.keyword }),
      });

      const response = await fetch(`http://localhost:8000/api/v1/examples?${params}`);
      const result = await response.json();
      
      if (result.code === 200) {
        setExamples(result.data.items);
        setExamplesTotal(result.data.total);
      }
    } catch (error) {
      message.error('加载示例失败');
      console.error(error);
    } finally {
      setExamplesLoading(false);
    }
  };

  // 加载最佳实践
  const loadPractices = async () => {
    setPracticesLoading(true);
    try {
      const params = new URLSearchParams({
        page: practicesPage.toString(),
        page_size: practicesPageSize.toString(),
      });

      const response = await fetch(`http://localhost:8000/api/v1/examples/practices/list?${params}`);
      const result = await response.json();
      
      if (result.code === 200) {
        setPractices(result.data.items);
        setPracticesTotal(result.data.total);
      }
    } catch (error) {
      message.error('加载最佳实践失败');
      console.error(error);
    } finally {
      setPracticesLoading(false);
    }
  };

  // 加载代码片段
  const loadSnippets = async () => {
    setSnippetsLoading(true);
    try {
      const params = new URLSearchParams({
        page: snippetsPage.toString(),
        page_size: snippetsPageSize.toString(),
      });

      const response = await fetch(`http://localhost:8000/api/v1/examples/snippets/list?${params}`);
      const result = await response.json();
      
      if (result.code === 200) {
        setSnippets(result.data.items);
        setSnippetsTotal(result.data.total);
      }
    } catch (error) {
      message.error('加载代码片段失败');
      console.error(error);
    } finally {
      setSnippetsLoading(false);
    }
  };

  // 下载示例
  const handleDownloadExample = async (id: number) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/examples/${id}/download`, {
        method: 'POST',
      });
      const result = await response.json();
      
      if (result.code === 200) {
        message.success('下载成功');
        loadExamples();
      }
    } catch (error) {
      message.error('下载失败');
    }
  };

  // 点赞最佳实践
  const handleLikePractice = async (id: number) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/examples/practices/${id}/like`, {
        method: 'POST',
      });
      const result = await response.json();
      
      if (result.code === 200) {
        message.success('点赞成功');
        loadPractices();
      }
    } catch (error) {
      message.error('点赞失败');
    }
  };

  // 使用代码片段
  const handleUseSnippet = async (id: number, code: string) => {
    try {
      await navigator.clipboard.writeText(code);
      
      await fetch(`http://localhost:8000/api/v1/examples/snippets/${id}/use`, {
        method: 'POST',
      });
      
      message.success('代码已复制到剪贴板');
      loadSnippets();
    } catch (error) {
      message.error('复制失败');
    }
  };

  // 查看详情
  const handleViewDetail = async (type: string, id: number) => {
    try {
      let url = '';
      if (type === 'example') {
        url = `http://localhost:8000/api/v1/examples/${id}`;
      } else if (type === 'practice') {
        url = `http://localhost:8000/api/v1/examples/practices/${id}`;
      } else if (type === 'snippet') {
        url = `http://localhost:8000/api/v1/examples/snippets/${id}`;
      }

      const response = await fetch(url);
      const result = await response.json();
      
      if (result.code === 200) {
        setSelectedItem({ ...result.data, type });
        setDetailModalVisible(true);
      }
    } catch (error) {
      message.error('加载详情失败');
    }
  };

  useEffect(() => {
    if (activeTab === 'examples') {
      loadExamples();
    } else if (activeTab === 'practices') {
      loadPractices();
    } else if (activeTab === 'snippets') {
      loadSnippets();
    }
  }, [activeTab, examplesPage, practicesPage, snippetsPage, exampleFilters]);

  // 难度颜色映射
  const getDifficultyColor = (difficulty: string) => {
    const colors: Record<string, string> = {
      beginner: 'green',
      intermediate: 'orange',
      advanced: 'red',
    };
    return colors[difficulty] || 'default';
  };

  // 难度文本映射
  const getDifficultyText = (difficulty: string) => {
    const texts: Record<string, string> = {
      beginner: '初级',
      intermediate: '中级',
      advanced: '高级',
    };
    return texts[difficulty] || difficulty;
  };

  return (
    <div style={{ padding: '24px', background: '#f0f2f5', minHeight: '100vh' }}>
      <Card bordered={false}>
        <Title level={2}>
          <BookOutlined /> 示例库
        </Title>
        <Paragraph type="secondary">
          提供常用场景的示例脚本、最佳实践和代码片段，帮助您快速上手
        </Paragraph>

        <Tabs activeKey={activeTab} onChange={setActiveTab}>
          {/* 示例脚本 */}
          <TabPane tab={<span><CodeOutlined /> 示例脚本</span>} key="examples">
            <Space direction="vertical" style={{ width: '100%' }} size="large">
              {/* 筛选栏 */}
              <Row gutter={16}>
                <Col span={8}>
                  <Search
                    placeholder="搜索示例..."
                    allowClear
                    onSearch={(value) => {
                      setExampleFilters({ ...exampleFilters, keyword: value });
                      setExamplesPage(1);
                    }}
                    prefix={<SearchOutlined />}
                  />
                </Col>
                <Col span={4}>
                  <Select
                    style={{ width: '100%' }}
                    placeholder="选择分类"
                    allowClear
                    onChange={(value) => {
                      setExampleFilters({ ...exampleFilters, category: value || '' });
                      setExamplesPage(1);
                    }}
                  >
                    <Option value="UI自动化">UI自动化</Option>
                    <Option value="应用管理">应用管理</Option>
                    <Option value="性能测试">性能测试</Option>
                    <Option value="功能测试">功能测试</Option>
                  </Select>
                </Col>
                <Col span={4}>
                  <Select
                    style={{ width: '100%' }}
                    placeholder="选择难度"
                    allowClear
                    onChange={(value) => {
                      setExampleFilters({ ...exampleFilters, difficulty: value || '' });
                      setExamplesPage(1);
                    }}
                  >
                    <Option value="beginner">初级</Option>
                    <Option value="intermediate">中级</Option>
                    <Option value="advanced">高级</Option>
                  </Select>
                </Col>
              </Row>

              {/* 示例列表 */}
              <Row gutter={[16, 16]}>
                {examples.map((example) => (
                  <Col span={8} key={example.id}>
                    <Card
                      hoverable
                      style={{ height: '100%' }}
                      actions={[
                        <Tooltip title="查看详情">
                          <EyeOutlined onClick={() => handleViewDetail('example', example.id)} />
                        </Tooltip>,
                        <Tooltip title="下载示例">
                          <DownloadOutlined onClick={() => handleDownloadExample(example.id)} />
                        </Tooltip>,
                        <Tooltip title="复制代码">
                          <CopyOutlined onClick={() => {
                            navigator.clipboard.writeText(example.code);
                            message.success('代码已复制');
                          }} />
                        </Tooltip>,
                      ]}
                    >
                      <Space direction="vertical" style={{ width: '100%' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <Title level={5} style={{ margin: 0 }}>
                            {example.is_featured && <StarOutlined style={{ color: '#faad14', marginRight: 8 }} />}
                            {example.title}
                          </Title>
                          <Tag color={getDifficultyColor(example.difficulty)}>
                            {getDifficultyText(example.difficulty)}
                          </Tag>
                        </div>
                        
                        <Text type="secondary" ellipsis={{ rows: 2 }}>
                          {example.description}
                        </Text>
                        
                        <div>
                          <Tag color="blue">{example.category}</Tag>
                          <Tag>{example.script_type}</Tag>
                        </div>
                        
                        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', color: '#999' }}>
                          <span><EyeOutlined /> {example.view_count}</span>
                          <span><DownloadOutlined /> {example.download_count}</span>
                          <span>作者: {example.author}</span>
                        </div>
                      </Space>
                    </Card>
                  </Col>
                ))}
              </Row>

              {/* 分页 */}
              <div style={{ textAlign: 'center', marginTop: 24 }}>
                <Pagination
                  current={examplesPage}
                  pageSize={examplesPageSize}
                  total={examplesTotal}
                  onChange={(page) => setExamplesPage(page)}
                  showSizeChanger={false}
                  showTotal={(total) => `共 ${total} 个示例`}
                />
              </div>
            </Space>
          </TabPane>

          {/* 最佳实践 */}
          <TabPane tab={<span><BookOutlined /> 最佳实践</span>} key="practices">
            <Row gutter={[16, 16]}>
              {practices.map((practice) => (
                <Col span={8} key={practice.id}>
                  <Card
                    hoverable
                    style={{ height: '100%' }}
                    actions={[
                      <Tooltip title="查看详情">
                        <EyeOutlined onClick={() => handleViewDetail('practice', practice.id)} />
                      </Tooltip>,
                      <Tooltip title="点赞">
                        <LikeOutlined onClick={() => handleLikePractice(practice.id)} />
                      </Tooltip>,
                    ]}
                  >
                    <Space direction="vertical" style={{ width: '100%' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Title level={5} style={{ margin: 0 }}>{practice.title}</Title>
                        <Tag color={getDifficultyColor(practice.difficulty)}>
                          {getDifficultyText(practice.difficulty)}
                        </Tag>
                      </div>
                      
                      <Tag color="purple">{practice.category}</Tag>
                      
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', color: '#999' }}>
                        <span><EyeOutlined /> {practice.view_count}</span>
                        <span><LikeOutlined /> {practice.like_count}</span>
                        <span>作者: {practice.author}</span>
                      </div>
                    </Space>
                  </Card>
                </Col>
              ))}
            </Row>

            <div style={{ textAlign: 'center', marginTop: 24 }}>
              <Pagination
                current={practicesPage}
                pageSize={practicesPageSize}
                total={practicesTotal}
                onChange={(page) => setPracticesPage(page)}
                showSizeChanger={false}
                showTotal={(total) => `共 ${total} 个最佳实践`}
              />
            </div>
          </TabPane>

          {/* 代码片段 */}
          <TabPane tab={<span><CodeOutlined /> 代码片段</span>} key="snippets">
            <Row gutter={[16, 16]}>
              {snippets.map((snippet) => (
                <Col span={6} key={snippet.id}>
                  <Card
                    hoverable
                    size="small"
                    style={{ height: '100%' }}
                    actions={[
                      <Tooltip title="查看详情">
                        <EyeOutlined onClick={() => handleViewDetail('snippet', snippet.id)} />
                      </Tooltip>,
                      <Tooltip title="复制代码">
                        <CopyOutlined onClick={() => handleUseSnippet(snippet.id, snippet.code)} />
                      </Tooltip>,
                    ]}
                  >
                    <Space direction="vertical" style={{ width: '100%' }} size="small">
                      <Title level={5} style={{ margin: 0 }}>{snippet.title}</Title>
                      <Text type="secondary" style={{ fontSize: '12px' }} ellipsis>
                        {snippet.description}
                      </Text>
                      <div>
                        <Tag color="cyan" style={{ fontSize: '11px' }}>{snippet.category}</Tag>
                        {snippet.shortcut && (
                          <Tag color="orange" style={{ fontSize: '11px' }}>
                            {snippet.shortcut}
                          </Tag>
                        )}
                      </div>
                      <div style={{ fontSize: '11px', color: '#999' }}>
                        使用 {snippet.usage_count} 次
                      </div>
                    </Space>
                  </Card>
                </Col>
              ))}
            </Row>

            <div style={{ textAlign: 'center', marginTop: 24 }}>
              <Pagination
                current={snippetsPage}
                pageSize={snippetsPageSize}
                total={snippetsTotal}
                onChange={(page) => setSnippetsPage(page)}
                showSizeChanger={false}
                showTotal={(total) => `共 ${total} 个代码片段`}
              />
            </div>
          </TabPane>
        </Tabs>
      </Card>

      {/* 详情模态框 */}
      <Modal
        title={selectedItem?.title}
        open={detailModalVisible}
        onCancel={() => setDetailModalVisible(false)}
        width={800}
        footer={[
          <Button key="close" onClick={() => setDetailModalVisible(false)}>
            关闭
          </Button>,
          selectedItem?.type === 'example' && (
            <Button
              key="download"
              type="primary"
              icon={<DownloadOutlined />}
              onClick={() => {
                handleDownloadExample(selectedItem.id);
                setDetailModalVisible(false);
              }}
            >
              下载示例
            </Button>
          ),
          <Button
            key="copy"
            icon={<CopyOutlined />}
            onClick={() => {
              navigator.clipboard.writeText(selectedItem?.code || selectedItem?.content);
              message.success('内容已复制');
            }}
          >
            复制代码
          </Button>,
        ]}
      >
        {selectedItem && (
          <Space direction="vertical" style={{ width: '100%' }} size="large">
            {/* 基本信息 */}
            {selectedItem.type === 'example' && (
              <>
                <div>
                  <Text strong>描述：</Text>
                  <Paragraph>{selectedItem.description}</Paragraph>
                </div>
                
                {selectedItem.use_case && (
                  <div>
                    <Text strong>使用场景：</Text>
                    <Paragraph>{selectedItem.use_case}</Paragraph>
                  </div>
                )}
                
                {selectedItem.prerequisites && (
                  <div>
                    <Text strong>前置条件：</Text>
                    <Paragraph>{selectedItem.prerequisites}</Paragraph>
                  </div>
                )}
                
                {selectedItem.expected_result && (
                  <div>
                    <Text strong>预期结果：</Text>
                    <Paragraph>{selectedItem.expected_result}</Paragraph>
                  </div>
                )}
              </>
            )}

            {selectedItem.type === 'practice' && (
              <div>
                <Paragraph>{selectedItem.content}</Paragraph>
              </div>
            )}

            {selectedItem.type === 'snippet' && (
              <div>
                <Text strong>描述：</Text>
                <Paragraph>{selectedItem.description}</Paragraph>
              </div>
            )}

            {/* 代码展示 */}
            {(selectedItem.code || selectedItem.content) && (
              <div>
                <Text strong>代码：</Text>
                <div style={{ marginTop: 8 }}>
                  <SyntaxHighlighter
                    language="python"
                    style={vscDarkPlus}
                    customStyle={{
                      borderRadius: '4px',
                      fontSize: '13px',
                    }}
                  >
                    {selectedItem.code || selectedItem.content}
                  </SyntaxHighlighter>
                </div>
              </div>
            )}

            {/* 统计信息 */}
            <Row gutter={16}>
              {selectedItem.view_count !== undefined && (
                <Col span={8}>
                  <Statistic title="浏览次数" value={selectedItem.view_count} prefix={<EyeOutlined />} />
                </Col>
              )}
              {selectedItem.download_count !== undefined && (
                <Col span={8}>
                  <Statistic title="下载次数" value={selectedItem.download_count} prefix={<DownloadOutlined />} />
                </Col>
              )}
              {selectedItem.like_count !== undefined && (
                <Col span={8}>
                  <Statistic title="点赞数" value={selectedItem.like_count} prefix={<LikeOutlined />} />
                </Col>
              )}
              {selectedItem.usage_count !== undefined && (
                <Col span={8}>
                  <Statistic title="使用次数" value={selectedItem.usage_count} prefix={<CopyOutlined />} />
                </Col>
              )}
            </Row>
          </Space>
        )}
      </Modal>
    </div>
  );
};

export default ExampleLibrary;
