/**
 * 骨架屏组件 - 加载状态优化
 */
import React from 'react';
import { Skeleton, Card } from 'antd';

interface LoadingSkeletonProps {
  type?: 'card' | 'list' | 'table' | 'form';
  rows?: number;
}

export const LoadingSkeleton: React.FC<LoadingSkeletonProps> = ({ 
  type = 'card', 
  rows = 3 
}) => {
  if (type === 'card') {
    return (
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: 16 }}>
        {Array.from({ length: rows }).map((_, index) => (
          <Card key={index} style={{ marginBottom: 16 }}>
            <Skeleton active avatar paragraph={{ rows: 3 }} />
          </Card>
        ))}
      </div>
    );
  }

  if (type === 'list') {
    return (
      <div>
        {Array.from({ length: rows }).map((_, index) => (
          <div key={index} style={{ marginBottom: 16, padding: 16, background: '#fff', borderRadius: 8 }}>
            <Skeleton active paragraph={{ rows: 2 }} />
          </div>
        ))}
      </div>
    );
  }

  if (type === 'table') {
    return (
      <Card>
        <Skeleton active paragraph={{ rows: 8 }} />
      </Card>
    );
  }

  if (type === 'form') {
    return (
      <Card>
        <Skeleton active paragraph={{ rows: 6 }} />
      </Card>
    );
  }

  return <Skeleton active />;
};

export default LoadingSkeleton;
