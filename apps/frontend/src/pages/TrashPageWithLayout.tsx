import React from 'react';
import Layout from '@/components/Layout';
import { TrashPage } from './TrashPage';

export function TrashPageWithLayout() {
  return (
    <Layout currentPage="trash">
      <TrashPage />
    </Layout>
  );
}

export default TrashPageWithLayout;