/**
 * 右键菜单组件
 */
import React, { useState, useEffect, ReactNode } from 'react';
import { Dropdown, Menu } from 'antd';
import type { MenuProps } from 'antd';

interface ContextMenuProps {
  children: ReactNode;
  items: MenuProps['items'];
  onMenuClick?: (key: string) => void;
}

export const ContextMenu: React.FC<ContextMenuProps> = ({ children, items, onMenuClick }) => {
  const [visible, setVisible] = useState(false);
  const [position, setPosition] = useState({ x: 0, y: 0 });

  const handleContextMenu = (e: React.MouseEvent) => {
    e.preventDefault();
    setPosition({ x: e.clientX, y: e.clientY });
    setVisible(true);
  };

  const handleMenuClick: MenuProps['onClick'] = ({ key }) => {
    setVisible(false);
    onMenuClick?.(key);
  };

  useEffect(() => {
    const handleClick = () => setVisible(false);
    if (visible) {
      document.addEventListener('click', handleClick);
      return () => document.removeEventListener('click', handleClick);
    }
  }, [visible]);

  return (
    <>
      <div onContextMenu={handleContextMenu}>{children}</div>
      {visible && (
        <div
          style={{
            position: 'fixed',
            left: position.x,
            top: position.y,
            zIndex: 1000,
          }}
        >
          <Menu
            items={items}
            onClick={handleMenuClick}
            style={{
              boxShadow: '0 3px 6px -4px rgba(0,0,0,.12), 0 6px 16px 0 rgba(0,0,0,.08)',
              borderRadius: 8,
            }}
          />
        </div>
      )}
    </>
  );
};

export default ContextMenu;
