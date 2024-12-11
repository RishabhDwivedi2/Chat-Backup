// src/utils/YAxisWrapper.tsx

import React from 'react';
import { YAxis as RechartsYAxis } from 'recharts';

const YAxisWrapper = ({ tickFormatter = (value: any) => value, ...props }) => {
    return <RechartsYAxis tickFormatter={tickFormatter} {...props} />;
};

export default YAxisWrapper;
