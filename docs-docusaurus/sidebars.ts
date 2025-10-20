import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.
 */
const sidebars: SidebarsConfig = {
  tutorialSidebar: [
    'intro',
    {
      type: 'category',
      label: '使用指南',
      items: [
        'usage/quick_start',
        'usage/workflow',
        'usage/config',
        'usage/plots',
      ],
    },
    {
      type: 'category',
      label: 'API 参考',
      items: [
        'api/model',
        'api/hunter',
        'api/farmer',
        'api/env',
      ],
    },
    {
      type: 'category',
      label: '技术文档',
      items: [
        'tech/changelog_v2',
        'tech/sequence_diagram',
        'tech/breakpoint',
      ],
    },
  ],
};

export default sidebars;
