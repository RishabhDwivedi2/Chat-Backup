// src/utils/XAxisWrapper.tsx

import React from 'react';
import { XAxis as RechartsXAxis } from 'recharts';

const XAxisWrapper = ({ dataKey = "name", ...props }) => {
    return <RechartsXAxis dataKey={dataKey} {...props} />;
};

export default XAxisWrapper;
